from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.entities import Job
from app.schemas.jobs import JobCreate


def create_job(db: Session, payload: JobCreate) -> Job:
    job = Job(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        job_no=payload.job_no,
        title=payload.title,
        contact_id=payload.contact_id,
        location_id=payload.location_id,
        description_raw=payload.description_raw,
        status="NEW",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
