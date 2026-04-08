from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    template = Column(String, default="IEEE")
    title = Column(String, nullable=True)
    abstract = Column(Text, nullable=True)
    introduction = Column(Text, nullable=True)
    methodology = Column(Text, nullable=True)
    results = Column(Text, nullable=True)
    conclusion = Column(Text, nullable=True)
    acknowledgment = Column(Text, nullable=True)
    references = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())