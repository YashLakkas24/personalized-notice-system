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
from sqlalchemy.orm import Session
from typing import List
from io import BytesIO
import uuid

from pypdf import PdfReader

from app.database import get_db
from app.models.student import Student
from app.models.notice import Notice

from app.agents.notice_agent import process_new_notice
from app.services.decision_engine import evaluate_student_for_notice
from app.services.embedding_service import create_embedding

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

    if not text.strip():
        raise HTTPException(status_code=400, detail="Notice text cannot be empty.")

    try:

        # AI extraction
        structured_data = process_new_notice(text)

        # Convert Pydantic model → dictionary
        notice_data = structured_data.model_dump()

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
            registration_link=notice_data["registration_link"],
            required_action=notice_data["required_action"],
            importance=notice_data["importance"],
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

        return {
            "message": "Notice processed and saved successfully.",
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
                "notice_embedding": notice.notice_embedding,
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

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400, detail="Could not extract text from the PDF."
            )

        # ------------------------------------------
        # 3. AI processing
        # ------------------------------------------

        structured_data = process_new_notice(extracted_text)

        notice_data = structured_data.model_dump()

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
            registration_link=notice_data["registration_link"],
            required_action=notice_data["required_action"],
            importance=notice_data["importance"],
            summary=notice_data["summary"],
            raw_text=extracted_text,
            notice_embedding=notice_embedding,
        )

        db.add(notice)
        db.commit()
        db.refresh(notice)

        return {
            "message": "PDF notice processed and saved successfully.",
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


@app.get("/api/student/{student_id}/feed")
def get_personalized_feed(
    student_id: str,
    db: Session = Depends(get_db),
):

    # Find student
    student_record = db.query(Student).filter(Student.id == student_id).first()
    if not student_record:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    personalized_feed = []

    # ------------------------------------------
    # 2. Convert DB model → dictionary
    # ------------------------------------------
    student = {
        "id": student_record.id,
        "name": student_record.name,
        "year": student_record.year,
        "branch": student_record.branch,
        "interests": student_record.interests or [],
        "interest_embedding": student_record.interest_embedding,
    }

    # ------------------------------------------
    # 3. Retrieve notices
    # ------------------------------------------

    notices = db.query(Notice).order_by(Notice.created_at.desc()).all()

    personalized_feed = []

    # ------------------------------------------
    # 4. Evaluate every notice
    # ------------------------------------------

    for notice_record in notices:

        notice = {
            "id": notice_record.id,
            "title": notice_record.title,
            "category": notice_record.category,
            "is_mandatory": notice_record.is_mandatory,
            "eligibility": notice_record.eligibility or {},
            "deadline": notice_record.deadline,
            "registration_link": notice_record.registration_link,
            "required_action": notice_record.required_action,
            "importance": notice_record.importance,
            "summary": notice_record.summary,
            "notice_embedding": notice_record.notice_embedding,
        }

        evaluation = evaluate_student_for_notice(
            student,
            notice,
        )

        # --------------------------------------
        # Suppressed notices aren't shown
        # --------------------------------------

        if evaluation["routing"] == "SUPPRESS":
            continue

        personalized_feed.append(
            {
                **notice,
                "match_metrics": {
                    "score": evaluation["relevance_score"],
                    "level": evaluation["relevance_level"],
                    "routing": evaluation["routing"],
                    "priority": evaluation["priority"],
                    "urgency": evaluation["urgency"],
                    "days_left": evaluation["days_left"],
                    "reason": evaluation["reason"],
                },
            }
        )

        # ------------------------------------------
        # 5. Sort personalized feed
        # ------------------------------------------

    personalized_feed.sort(
        key=lambda x: (
            not x["is_mandatory"],
            -x["match_metrics"]["score"],
        )
    )

    return {
        "student": {
            "id": student["id"],
            "name": student["name"],
        },
        "total_relevant_notices": len(personalized_feed),
        "notices": personalized_feed,
    }
