from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.core.enums import ResponseAnswer


class AssignmentCreateResult(BaseModel):
    created_ids: list[str]


class AssignmentResponseIn(BaseModel):
    tenant_id: str
    answer: ResponseAnswer
    comment: str | None = None
    meta: dict[str, Any] | None = None


class AssignmentResponseOut(BaseModel):
    id: str
    job_assignment_id: str
    answer: ResponseAnswer
    responded_at: datetime

    class Config:
        from_attributes = True
