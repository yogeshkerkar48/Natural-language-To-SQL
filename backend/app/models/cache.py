"""
Semantic Query Cache Model

Database model for storing cached queries with semantic embeddings.
"""

from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class SemanticQueryCache(Base):
    """
    Stores cached NL2SQL queries with semantic embeddings for similarity matching.
    """
    __tablename__ = "semantic_query_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(500), nullable=False, index=True)
    question_embedding = Column(JSON, nullable=False)  # Stored as JSON array
    schema_hash = Column(String(64), nullable=False, index=True)
    sql_generated = Column(Text, nullable=False)
    database_type = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    hit_count = Column(Integer, default=0)  # Track how many times this cache was used
    last_hit_at = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationship
    user = relationship("User", backref="cached_queries")
    
    # Composite indexes for performance
    __table_args__ = (
        Index('idx_schema_created', 'schema_hash', 'created_at'),
        Index('idx_user_schema', 'user_id', 'schema_hash'),
    )
    
    def __repr__(self):
        return f"<SemanticQueryCache(id={self.id}, question='{self.question[:50]}...', hits={self.hit_count})>"
