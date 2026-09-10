from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
from pypdf import PdfReader # Used if processing uploaded pdf bytes
from io import BytesIO

from app.config import settings
from app.agents.notice_agent import process_new_notice,calculate_match_score

app=FastAPI(title="College Notice Intelligence System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

NOTICES_DB=[]
STUDENT_PROFILES_DB=[
    {
       "id": "student_1",
        "name": "Alex Kumar",
        "year": 3,
        "branch": "CS",
        "interests": ["Hackathons", "AI/ML", "Coding"],
    },
    {
        "id": "student_2",
        "name": "Pooja Sharma",
        "year": 2,
        "branch": "ME",
        "interests": ["Sports", "Cultural Events"],
    }
]

class StudentProfileUpdate(BaseModel):
    name:str
    year:int
    branch:str
    interests:List[str]

@app.get("/")
def read_root():
    return{"status":"online","agent_framework":"Strands Agents SDK"}

@app.get("/api/admin/notice/text")
def upload_text_notice(text:str=Form(...)):
    """Accepts pure text notice input from teh admin form and passes it to the agent."""
    if not text.strip():
        raise HTTPException(status_code=400,detail="Notice text cannot be empty.")

    structured_data=process_new_notice(text)
    structured_data["id"]=str(uuid.uuid4())
    structured_data["raw_text"]=text

    NOTICES_DB.insert(0,structured_data)
    return structured_data

@app.post("/api/admin/notice/pdf")
async def upload_pdf_notice(file:UploadFile=File(...)):
    """Accepts a file upload, parses structural text from the PDF, and matches via AI."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400,detail="Only PDF file extensions are supported.")

    try:
        from pypdf import PdfReader
        pdf_bytes=await file.read()
        reader=PdfReader(BytesIO(pdf_bytes))
        extracted_text=""
        for page in reader.pages():
            text=page.extrace_text()
            if text:
                extracted_text+=text+"\n"

        if not extracted_text.strip():
            raise HTTPException(status_code=400,detail="Could not extract text from this PDF file.")

        structured_data = process_new_notice(extracted_text)
        structured_data["id"] = str(uuid.uuid4())
        structured_data["raw_text"] = extracted_text

        NOTICES_DB.insert(0,structured_data)
        return structured_data
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"PDF Processing broken:{str(e)}")

        
@app.get("/api/students")
def get_students():
    """Returns available demo student profiles to easily switch perspectives in the video."""
    return STUDENT_PROFILES_DB

@app.get("/api/student/{student_id}/feed")
def get_personalized_feed(student_id:str):
    """Calculates live personalized visibility matrices for a specific student profile."""
    student=next((s for s in STUDENT_PROFILES_DB if s["id"]==student_id))
    if not student:
        raise HTTPException(status_code=404,detail="Student profile not found.")

    personalized_feed=[]

    for notice in NOTICES_DB:
        evaluation=calculate_match_score(student,notice)

        if evaluation["routing"]=="SUPPRESSED":
            continue

        feed_item={
            "id":notice["id"],
            "title":notice["title"],
            "category":notice["category"],
            "is_mandatory":notice["is_mandatory"],
            "summary":notice["summary"],
            "deadline":notice["deadline"],
            "registration_link": notice["registration_link"],
            "match_metrics": {
                "score": evaluation["relevance_score"],
                "routing": evaluation["routing"]
            }
        }
        personalized_feed.append(feed_item)
    personalized_feed.sort(key=lambda x:(x["is_mandatory"]==False,-x["match_metrics"]["score"]))
    return personalized_feed