from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DiagnosticEventOut(BaseModel):
    id: str
    event_type: str
    reason_code: str | None = None
    message: str | None = None
    data: dict[str, Any] | None = None
    created_at: datetime

    class Config:
        from_attributes = True
