from sqlalchemy import Column, Integer, String, JSON, Text

from app.database import Base


class Student(Base):

    __tablename__ = "students"

    id = Column(String, primary_key=True)

    name = Column(String, nullable=False)

    year = Column(Integer, nullable=False)

    branch = Column(String, nullable=False)

    preferences = Column(Text, nullable=False, default="")

    preference_embedding = Column(JSON, nullable=True)

    interests = Column(JSON, nullable=False, default=list)

    interest_embedding = Column(JSON, nullable=True)
