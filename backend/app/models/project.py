from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from app.core.database import Base

class Project(Base):
    __tablename__ = "nl2sql_projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    state = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
