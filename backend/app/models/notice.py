from sqlalchemy import Column, String, Boolean, JSON, DateTime, Text
from datetime import datetime

from app.database import Base


class Notice(Base):

    __tablename__ = "notices"

    id = Column(String, primary_key=True)

    title = Column(String, nullable=False)

    category = Column(String, nullable=False)

    is_mandatory = Column(Boolean, default=False, nullable=False)

    eligibility = Column(JSON, nullable=False, default=dict)

    deadline = Column(String, nullable=True)

    registration_link = Column(String, nullable=True)

    required_action = Column(String, nullable=True)

    importance = Column(String, nullable=True)

    summary = Column(Text, nullable=True)

    raw_text = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    notice_embedding = Column(JSON, nullable=True)
