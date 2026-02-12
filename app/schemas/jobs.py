from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.core.enums import JobStatus


class JobCreate(BaseModel):
    tenant_id: str
    job_no: str
    title: str
    contact_id: str | None = None
    location_id: str | None = None
    description_raw: str | None = None


class JobOut(BaseModel):
    id: str
    tenant_id: str
    job_no: str
    title: str
    status: JobStatus
    description_raw: str | None = None
    description_norm: dict[str, Any] | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class JobAssignIn(BaseModel):
    tenant_id: str
    assignee_contact_ids: list[str]
    channel: str = "PUSH"
    batch_id: str | None = None
    expires_at: datetime | None = None
