from fastapi import (
    FastAPI,
    BackgroundTasks,
    UploadFile,
    File,
    Form,
    HTTPException,
    Depends,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List
from io import BytesIO
import pytesseract
from PIL import Image

from pypdf import PdfReader

from app.database import get_db, SessionLocal, Base, engine
from app.models.student import Student
from app.models.notice import Notice
from app.models.notification import Notification

from app.services.embedding_service import (
    create_embedding,
    create_preference_embedding,
)
from app.models.notification import Notification
from app.services.notice_workflow import process_notice_workflow
import os
import uuid
from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)

TESSERACT_PATH = os.getenv("TESSERACT_PATH")
POPPLER_PATH = os.getenv("POPPLER_PATH")

if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


app = FastAPI(
    title="Personalized Notice Intelligence System",
    description="AI-powered personalized college notice platform",
)

os.makedirs("uploads/notices", exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# SCHEMAS
# ============================================================


class StudentProfileCreate(BaseModel):
    id: str
    name: str
    year: int
    branch: str


class StudentLogin(BaseModel):
    student_id: str
    password: str


class StudentPreferencesUpdate(BaseModel):
    preferences: str


def process_notice_in_background(
    raw_text: str,
    pdf_url: str = None,
):
    db = SessionLocal()

    try:
        notice, notifications, routing_report = process_notice_workflow(
            db=db,
            raw_text=raw_text,
            pdf_url=pdf_url,
        )

        print(f"Notice processed: {notice.title}")
        print(f"Routing report: {routing_report}")

    except Exception as e:
        db.rollback()
        print(f"Background notice processing failed: {e}")

    finally:
        db.close()


# ============================================================
# HEALTH CHECK
# ============================================================
@app.get("/")
def read_root():

    return {
        "status": "online",
        "agent_framework": "Strands Agents SDK",
        "model_provider": "OpenAI",
        "database": "PostgreSQL",
    }


# ============================================================
# STUDENT LOGIN
# ============================================================


@app.post("/api/student/login")
def student_login(
    login_data: StudentLogin,
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == login_data.student_id).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    return {
        "message": "Login successful",
        "student": {
            "id": student.id,
            "name": student.name,
        },
    }


# ============================================================
# ADMIN — TEXT NOTICE
# ============================================================


@app.post("/api/admin/notice/text")
async def upload_text_notice(
    background_tasks: BackgroundTasks,
    text: str = Form(...),
):

    if not text.strip():
        raise HTTPException(status_code=400, detail="Notice text cannot be empty.")

    background_tasks.add_task(process_notice_in_background, text)

    return {"message": "Notice accepted for background processing."}


# ============================================================
# ADMIN — PDF NOTICE
# ============================================================


@app.post("/api/admin/notice/pdf")
async def upload_pdf_notice(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF file are supported.",
        )

    try:

        # ------------------------------------------
        # 1. Read PDF
        # ------------------------------------------

        pdf_bytes = await file.read()

        # ------------------------------------------
        # 1B. Save original PDF
        # ------------------------------------------

        upload_dir = "uploads/notices"
        os.makedirs(upload_dir, exist_ok=True)

        pdf_filename = f"{uuid.uuid4()}.pdf"
        pdf_path = os.path.join(upload_dir, pdf_filename)

        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        pdf_url = f"/uploads/notices/{pdf_filename}"

        # ------------------------------------------
        # 2. Extract text
        # ------------------------------------------

        reader = PdfReader(BytesIO(pdf_bytes))

        extracted_text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                extracted_text += page_text + "\n"

        # ------------------------------------------
        # 2B. OCR fallback for scanned PDFs
        # ------------------------------------------

        if not extracted_text.strip():

            try:
                from pdf2image import convert_from_bytes

                images = convert_from_bytes(
                    pdf_bytes,
                    poppler_path=POPPLER_PATH or None,
                )

                ocr_text = []

                for image in images:
                    text = pytesseract.image_to_string(image)

                    if text.strip():
                        ocr_text.append(text)

                extracted_text = "\n".join(ocr_text)

            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"PDF text extraction/OCR failed: {str(e)}",
                )

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the PDF.",
            )

        # ------------------------------------------
        # 3. AI processing
        # ------------------------------------------

        background_tasks.add_task(
            process_notice_in_background,
            extracted_text,
            pdf_url,
        )

        return {"message": "PDF accepted for background processing."}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF processing failed: {str(e)}",
        )


@app.post("/api/admin/notice/image")
async def upload_image_notice(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/jpg",
        "image/webp",
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG, JPEG and WEBP images are supported.",
        )

    try:
        # ------------------------------------------
        # 1. Read image
        # ------------------------------------------

        image_bytes = await file.read()

        upload_dir = "uploads/notices"
        os.makedirs(upload_dir, exist_ok=True)

        extension = file.filename.split(".")[-1].lower()
        image_filename = f"{uuid.uuid4()}.{extension}"
        image_path = os.path.join(upload_dir, image_filename)

        with open(image_path, "wb") as f:
            f.write(image_bytes)

        image_url = f"/uploads/notices/{image_filename}"

        image = Image.open(BytesIO(image_bytes))

        # ------------------------------------------
        # 2. OCR
        # ------------------------------------------

        extracted_text = pytesseract.image_to_string(image)

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the image.",
            )

        # ------------------------------------------
        # 3. AI processing
        # ------------------------------------------

        background_tasks.add_task(
            process_notice_in_background, extracted_text, image_url
        )

        return {"message": "Image accepted for background processing."}

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Image processing failed: {str(e)}",
        )


# ============================================================
# STUDENTS
# ============================================================


@app.post("/api/students")
def create_student(
    student_data: StudentProfileCreate,
    db: Session = Depends(get_db),
):
    existing_student = db.query(Student).filter(Student.id == student_data.id).first()

    if existing_student:
        raise HTTPException(
            status_code=409,
            detail="Student already exists.",
        )

    student = Student(
        id=student_data.id,
        name=student_data.name,
        year=student_data.year,
        branch=student_data.branch,
        # Student fills this later
        # from Student Portal.
        preferences="",
        preference_embedding=None,
        # Compatibility with existing DB schema
        interests=[],
        interest_embedding=None,
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return {
        "message": "Student created successfully.",
        "student": {
            "id": student.id,
            "name": student.name,
            "year": student.year,
            "branch": student.branch,
        },
    }


# ============================================================
# STUDENT PREFERENCES
# ============================================================


@app.get("/api/student/{student_id}/profile")
def get_student_profile(student_id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "id": student.id,
        "name": student.name,
        "year": student.year,
        "branch": student.branch,
        "preferences": student.preferences or "",
    }


@app.put("/api/student/{student_id}/profile")
def update_student_profile(
    student_id: str,
    profile: StudentPreferencesUpdate,
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    preferences = profile.preferences.strip()

    if not preferences:
        raise HTTPException(status_code=400, detail="Preferences cannot be empty.")

    # Save requirement
    student.preferences = preferences

    # Generate new embedding
    student.preference_embedding = create_preference_embedding(preferences)

    # Keep old fields synchronized
    student.interests = [preferences]
    student.interest_embedding = student.preference_embedding

    db.commit()
    db.refresh(student)

    # Recalculate this student's feed
    from app.services.notification_service import refresh_student_notifications

    refresh_student_notifications(db, student)

    return {
        "message": "Preferences saved and feed updated.",
        "student": {
            "id": student.id,
            "name": student.name,
            "year": student.year,
            "branch": student.branch,
            "preferences": student.preferences,
        },
    }


# ============================================================
# GET STUDENTS
# ============================================================


@app.get("/api/students")
def get_students(
    db: Session = Depends(get_db),
):
    students = db.query(Student).order_by(Student.name).all()

    if not students:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found.",
        )

    return students


@app.post("/api/admin/notices/batch")
async def upload_notice_batch(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    results = []

    for file in files:
        try:
            filename = file.filename.lower()
            file_bytes = await file.read()

            # ------------------------------------------
            # Save original file
            # ------------------------------------------

            upload_dir = "uploads/notices"
            os.makedirs(upload_dir, exist_ok=True)

            extension = file.filename.split(".")[-1].lower()
            saved_filename = f"{uuid.uuid4()}.{extension}"
            saved_path = os.path.join(upload_dir, saved_filename)

            with open(saved_path, "wb") as f:
                f.write(file_bytes)

            file_url = f"/uploads/notices/{saved_filename}"

            # PDF
            if filename.endswith(".pdf"):
                reader = PdfReader(BytesIO(file_bytes))

                extracted_text = ""

                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += page_text + "\n"

                # OCR fallback
                if not extracted_text.strip():
                    from pdf2image import convert_from_bytes

                    images = convert_from_bytes(
                        file_bytes,
                        poppler_path=POPPLER_PATH or None,
                    )

                    ocr_text = []

                    for image in images:
                        text = pytesseract.image_to_string(image)
                        if text.strip():
                            ocr_text.append(text)

                    extracted_text = "\n".join(ocr_text)

            # Image
            elif filename.endswith((".jpg", ".jpeg", ".png", ".webp")):
                image = Image.open(BytesIO(file_bytes))
                extracted_text = pytesseract.image_to_string(image)

            # Text file
            elif filename.endswith(".txt"):
                extracted_text = file_bytes.decode(
                    "utf-8",
                    errors="ignore",
                )

            else:
                results.append(
                    {
                        "filename": file.filename,
                        "status": "failed",
                        "error": "Unsupported file type",
                    }
                )
                continue

            if not extracted_text.strip():
                results.append(
                    {
                        "filename": file.filename,
                        "status": "failed",
                        "error": "Could not extract text",
                    }
                )
                continue

            notice, notifications, routing_report = process_notice_workflow(
                db=db, raw_text=extracted_text, pdf_url=file_url
            )

            results.append(
                {
                    "filename": file.filename,
                    "status": "success",
                    "notice_id": notice.id,
                    "title": notice.title,
                    "notifications_created": len(notifications),
                }
            )

        except Exception as e:
            db.rollback()

            results.append(
                {
                    "filename": file.filename,
                    "status": "failed",
                    "error": str(e),
                }
            )

    return {
        "message": "Batch processing completed",
        "total_files": len(files),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "results": results,
    }


# ============================================================
# ALL NOTICES
# ============================================================


@app.get("/api/notices")
def get_all_notices(
    db: Session = Depends(get_db),
):
    notices = db.query(Notice).order_by(Notice.created_at.desc()).all()

    return {
        "total": len(notices),
        "notices": [
            {
                "id": notice.id,
                "title": notice.title,
                "summary": notice.summary,
                "category": notice.category,
                "is_mandatory": notice.is_mandatory,
                "eligibility": notice.eligibility,
                "deadline": notice.deadline,
                "registration_link": notice.registration_link,
                "required_action": notice.required_action,
                "pdf_url": notice.pdf_url,
                "importance": notice.importance,
                "created_at": notice.created_at,
            }
            for notice in notices
        ],
    }


# ============================================================
# STUDENT PERSONALIZED FEED
# ============================================================


@app.get("/api/student/{student_id}/notifications")
def get_notifications(
    student_id: str,
    db: Session = Depends(get_db),
):
    notifications = (
        db.query(Notification)
        .filter(Notification.student_id == student_id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    result = []

    for notification in notifications:
        notice = db.query(Notice).filter(Notice.id == notification.notice_id).first()

        if not notice:
            continue

        result.append(
            {
                "notification_id": notification.id,
                "notice_id": notice.id,
                "title": notice.title,
                "summary": notice.summary,
                "pdf_url": notice.pdf_url,
                "category": notice.category,
                "deadline": notice.deadline,
                "registration_link": notice.registration_link,
                "required_action": notice.required_action,
                "priority": notification.priority,
                "urgency": notification.urgency,
                "days_left": notification.days_left,
                "relevance_score": notification.relevance_score,
                "reason": notification.reason,
                "status": notification.status,
                "created_at": notification.created_at,
            }
        )

    return {
        "student_id": student_id,
        "total": len(result),
        "notifications": result,
    }


@app.patch("/api/student/{student_id}/notifications/{notification_id}/read")
def mark_notification_read(
    student_id: str,
    notification_id: str,
    db: Session = Depends(get_db),
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.student_id == student_id,
        )
        .first()
    )

    if not notification:

        raise HTTPException(
            status_code=404,
            detail="Notification not found.",
        )

    notification.status = "READ"
    notification.read_at = datetime.utcnow()

    db.commit()

    return {"message": "Notification marked as read."}
