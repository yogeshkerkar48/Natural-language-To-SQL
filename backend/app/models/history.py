from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question = Column(String(1000), nullable=False)
    sql_generated = Column(String, nullable=True)
    database_type = Column(String(50), nullable=True)
    project_id = Column(Integer, ForeignKey("nl2sql_projects.id"), nullable=True)
    schema_hash = Column(String(64), index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", backref="query_history")
