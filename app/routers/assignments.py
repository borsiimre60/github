from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.entities import JobAssignment, Response
from app.schemas.assignments import AssignmentResponseIn, AssignmentResponseOut

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("/{assignment_id}/response", response_model=AssignmentResponseOut)
def submit_response(
    assignment_id: str,
    payload: AssignmentResponseIn,
    db: Session = Depends(get_db),
):
    assignment = db.get(JobAssignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if assignment.tenant_id != payload.tenant_id:
        raise HTTPException(status_code=400, detail="Tenant mismatch")

    response = Response(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        job_assignment_id=assignment_id,
        answer=payload.answer.value,
        comment=payload.comment,
        meta=payload.meta,
    )
    assignment.state = "RESPONDED"

    db.add(response)
    db.commit()
    db.refresh(response)
    return response
