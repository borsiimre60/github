from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.entities import EventLog
from app.schemas.diagnostics import DiagnosticEventOut

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


@router.get("/sendability", response_model=list[DiagnosticEventOut])
def get_sendability(
    job_id: str = Query(...),
    db: Session = Depends(get_db),
):
    stmt = (
        select(EventLog)
        .where(
            EventLog.job_id == job_id,
            EventLog.event_type == "SEND_BLOCKED",
        )
        .order_by(EventLog.created_at.desc())
        .limit(20)
    )
    return list(db.scalars(stmt).all())
