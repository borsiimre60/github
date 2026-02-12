from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.entities import Job, JobAssignment
from app.schemas.assignments import AssignmentCreateResult
from app.schemas.jobs import JobAssignIn, JobCreate, JobOut
from app.services.jobs_service import create_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobOut)
def create_job_endpoint(payload: JobCreate, db: Session = Depends(get_db)):
    return create_job(db, payload)


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/assign", response_model=AssignmentCreateResult)
def assign_job(job_id: str, payload: JobAssignIn, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.tenant_id != payload.tenant_id:
        raise HTTPException(status_code=400, detail="Tenant mismatch")

    created_ids: list[str] = []
    for assignee_contact_id in payload.assignee_contact_ids:
        assignment = JobAssignment(
            id=str(uuid4()),
            tenant_id=payload.tenant_id,
            job_id=job_id,
            assignee_contact_id=assignee_contact_id,
            channel=payload.channel,
            batch_id=payload.batch_id,
            expires_at=payload.expires_at,
            state="SENT",
        )
        db.add(assignment)
        created_ids.append(assignment.id)

    db.commit()
    return AssignmentCreateResult(created_ids=created_ids)
