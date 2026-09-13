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

from app.database import get_db, SessionLocal
from app.models.student import Student
from app.models.notice import Notice

from app.services.embedding_service import create_embedding
from app.models.notification import Notification
from app.services.notice_workflow import process_notice_workflow

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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


def process_notice_in_background(raw_text: str):
    db = SessionLocal()

    try:
        notice, notifications, routing_report = process_notice_workflow(
            db=db,
            raw_text=raw_text,
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

                images = convert_from_bytes(
                    pdf_bytes,
                    poppler_path=r"C:\Program Files\poppler-26.07.0\Library\bin",
                )

                ocr_text = []

                for image in images:
                    text = pytesseract.image_to_string(image)

                    if text.strip():
                        ocr_text.append(text)

                extracted_text = "\n".join(ocr_text)
            except Exception as e:
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

        background_tasks.add_task(
            process_notice_in_background,
            extracted_text,
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
            process_notice_in_background,
            extracted_text,
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

    return {"message": "Notification marked as read."}
