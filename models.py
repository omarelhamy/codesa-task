from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from database import Base

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True)
    description = Column(String)
    filename = Column(String)
    status = Column(String, default="PENDING")
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    report_path = Column(String)
