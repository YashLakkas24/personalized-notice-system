from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from app.database import Base


class Notification(Base):

    __tablename__ = "notifications"

    id = Column(String, primary_key=True)

    student_id = Column(String, ForeignKey("students.id"), nullable=False, index=True)

    notice_id = Column(String, ForeignKey("notices.id"), nullable=False, index=True)

    relevance_score = Column(Float, nullable=False, default=0.0)

    priority = Column(String, nullable=False, default="NORMAL")

    urgency = Column(String, nullable=False, default="NORMAL")

    reason = Column(Text, nullable=True)

    days_left = Column(Integer, nullable=True)

    status = Column(String, nullable=False, default="UNREAD")

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    read_at = Column(DateTime, nullable=True)
