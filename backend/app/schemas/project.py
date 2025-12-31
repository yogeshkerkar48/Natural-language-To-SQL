from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional

class ProjectBase(BaseModel):
    name: str

class ProjectCreate(ProjectBase):
    state: Any

class ProjectUpdate(ProjectBase):
    state: Optional[Any] = None

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProjectDetailResponse(ProjectResponse):
    state: Any
