from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Project(Base):
    __tablename__ = "nl2sql_projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    state = Column(JSON)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for backward compatibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to User
    user = relationship("User", backref="projects")
    
    # Relationship to QueryHistory with Cascade Delete
    # This ensures history is deleted when project is deleted
    history = relationship("QueryHistory", backref="project", cascade="all, delete-orphan")
