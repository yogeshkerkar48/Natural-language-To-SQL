from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class QueryHistoryBase(BaseModel):
    question: str
    sql_generated: Optional[str] = None
    database_type: Optional[str] = "MySQL"

class QueryHistoryCreate(QueryHistoryBase):
    pass

class QueryHistoryResponse(QueryHistoryBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True # For older pydantic versions if needed
