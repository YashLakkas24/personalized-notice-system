from fastapi import (
    FastAPI,
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
import uuid
import pytesseract
from PIL import Image

from pypdf import PdfReader

from app.database import get_db
from app.models.student import Student
from app.models.notice import Notice

from app.agents.notice_agent import process_new_notice
from app.services.embedding_service import create_embedding
from app.services.notification_service import route_notice_to_students
from app.models.notification import Notification

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Tesseract-OCR"
)

app = FastAPI(
    title="Personalized Notice Intelligence System",
    description="AI-powered personalized college notice platform",
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
    interests: List[str]


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
# ADMIN — TEXT NOTICE
# ============================================================


@app.post("/api/admin/notice/text")
async def upload_text_notice(text: str = Form(...), db: Session = Depends(get_db)):

    import traceback

    if not text.strip():
        raise HTTPException(status_code=400, detail="Notice text cannot be empty.")

    try:

        # AI extraction
        structured_data = process_new_notice(text)

        # Convert Pydantic model → dictionary
        notice_data = structured_data.model_dump()
        registration_link = notice_data.get("registration_link")

        if registration_link in ["None Provided", "None", "null", ""]:
            registration_link = None

        notice_embedding_text = f"""
        Title: {notice_data["title"]}
        Category: {notice_data["category"]}
        Summary: {notice_data["summary"]}
        Required action: {notice_data["required_action"]}
        Eligibility: {notice_data["eligibility"]}
        """

        notice_embedding = create_embedding(notice_embedding_text)

        # Add system fields
        notice = Notice(
            id=str(uuid.uuid4()),
            title=notice_data["title"],
            category=notice_data["category"],
            is_mandatory=notice_data["is_mandatory"],
            eligibility=notice_data["eligibility"],
            deadline=notice_data["deadline"],
            registration_link=registration_link,
            required_action=notice_data.get("required_action"),
            importance=notice_data.get("importance", "NORMAL"),
            summary=notice_data["summary"],
            raw_text=text,
            notice_embedding=notice_embedding,
        )

        # ------------------------------------------
        # 4. Save to PostgreSQL
        # ------------------------------------------

        db.add(notice)
        db.commit()
        db.refresh(notice)
        notifications = route_notice_to_students(db, notice)

        return {
            "message": "Notice processed and saved successfully.",
            "notifications_created": len(notifications),
            "notice": {
                "id": notice.id,
                "title": notice.title,
                "category": notice.category,
                "is_mandatory": notice.is_mandatory,
                "eligibility": notice.eligibility,
                "deadline": notice.deadline,
                "registration_link": notice.registration_link,
                "required_action": notice.required_action,
                "importance": notice.importance,
                "summary": notice.summary,
            },
        }
    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500, detail=f"Notice processing failed: {str(e)}"
        )


# ============================================================
# ADMIN — PDF NOTICE
# ============================================================


@app.post("/api/admin/notice/pdf")
async def upload_pdf_notice(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF file are supported.")

    try:

        # ------------------------------------------
        # 1. Read PDF
        # ------------------------------------------

        pdf_bytes = await file.read()

        reader = PdfReader(BytesIO(pdf_bytes))

        # ------------------------------------------
        # 2. Extract text
        # ------------------------------------------

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

                images = convert_from_bytes(pdf_bytes)

                ocr_text = []

                for image in images:
                    text = pytesseract.image_to_string(image)

                    if text.strip():
                        ocr_text.append(text)

                extracted_text = "\n".join(ocr_text)
            except:
                raise HTTPException(
                    status_code=400, detail=f"PDF text extraction/OCR failed: {str(e)}"
                )
        if not extracted_text.strip():
            raise HTTPException(
                status_code=400, detail="Could not extract text from the PDF."
            )

        # ------------------------------------------
        # 3. AI processing
        # ------------------------------------------

        structured_data = process_new_notice(extracted_text)

        notice_data = structured_data.model_dump()

        registration_link = notice_data.get("registration_link")

        if registration_link in ["None Provided", "None", "null", ""]:
            registration_link = None

        notice_embedding_text = f"""
            Title: {notice_data["title"]}
            Category: {notice_data["category"]}
            Summary: {notice_data["summary"]}
            Required action: {notice_data["required_action"]}
            Eligibility: {notice_data["eligibility"]}
        """

        notice_embedding = create_embedding(notice_embedding_text)

        # ------------------------------------------
        # 4. Save to PostgreSQL
        # ------------------------------------------

        notice = Notice(
            id=str(uuid.uuid4()),
            title=notice_data["title"],
            category=notice_data["category"],
            is_mandatory=notice_data["is_mandatory"],
            eligibility=notice_data["eligibility"],
            deadline=notice_data["deadline"],
            registration_link=registration_link,
            required_action=notice_data["required_action"],
            importance=notice_data["importance"],
            summary=notice_data["summary"],
            raw_text=extracted_text,
            notice_embedding=notice_embedding,
        )

        db.add(notice)
        db.commit()
        db.refresh(notice)
        notifications = route_notice_to_students(db, notice)

        return {
            "message": "PDF notice processed and saved successfully.",
            "notifications_created": len(notifications),
            "notice": {
                "id": notice.id,
                "title": notice.title,
                "category": notice.category,
                "is_mandatory": notice.is_mandatory,
                "eligibility": notice.eligibility,
                "deadline": notice.deadline,
                "registration_link": notice.registration_link,
                "required_action": notice.required_action,
                "importance": notice.importance,
                "summary": notice.summary,
            },
        }

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        raise HTTPException(status_code=500, detail=f"PDF Processing broken:{str(e)}")


@app.post("/api/admin/notice/image")
async def upload_image_notice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
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

        structured_data = process_new_notice(extracted_text)

        notice_data = structured_data.model_dump()

        registration_link = notice_data.get("registration_link")

        if registration_link in ["None Provided", "None", "null", ""]:
            registration_link = None

        # ------------------------------------------
        # 4. Embedding
        # ------------------------------------------

        notice_embedding_text = f"""
            Title: {notice_data["title"]}
            Category: {notice_data["category"]}
            Summary: {notice_data["summary"]}
            Required action: {notice_data["required_action"]}
            Eligibility: {notice_data["eligibility"]}
        """

        notice_embedding = create_embedding(notice_embedding_text)

        # ------------------------------------------
        # 5. Save
        # ------------------------------------------

        notice = Notice(
            id=str(uuid.uuid4()),
            title=notice_data["title"],
            category=notice_data["category"],
            is_mandatory=notice_data["is_mandatory"],
            eligibility=notice_data["eligibility"],
            deadline=notice_data["deadline"],
            registration_link=registration_link,
            required_action=notice_data["required_action"],
            importance=notice_data["importance"],
            summary=notice_data["summary"],
            raw_text=extracted_text,
            notice_embedding=notice_embedding,
        )

        db.add(notice)
        db.commit()
        db.refresh(notice)

        # ------------------------------------------
        # 6. Automatic routing
        # ------------------------------------------

        notifications = route_notice_to_students(db, notice)

        return {
            "message": "Image notice processed successfully.",
            "notifications_created": len(notifications),
            "notice": {
                "id": notice.id,
                "title": notice.title,
                "category": notice.category,
                "deadline": notice.deadline,
                "importance": notice.importance,
                "summary": notice.summary,
            },
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500, detail=f"Image processing failed: {str(e)}",
        )


# ============================================================
# STUDENTS
# ============================================================


@app.post("/api/students")
def create_student(
    student_data: StudentProfileCreate,
    db: Session = Depends(get_db),
):
    interest_text = ", ".join(student_data.interests)

    interest_embedding = create_embedding(f"Student interest:{interest_text}")

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
        interests=student_data.interests,
        interest_embedding=interest_embedding,
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return student


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

    return {"message": "Notificatio marked as read."}
