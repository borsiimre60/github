from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    func,
)

from app.models.base import Base


class Tenant(Base):
    __tablename__ = "tenant"

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    timezone = Column(Text, nullable=False, server_default="Europe/Budapest")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class User(Base):
    __tablename__ = "user"
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_user_tenant_email"),)

    id = Column(Text, primary_key=True)
    tenant_id = Column(Text, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)
    email = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    phone = Column(Text)
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Contact(Base):
    __tablename__ = "contact"

    id = Column(Text, primary_key=True)
    tenant_id = Column(Text, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)
    type = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    email = Column(Text)
    phone = Column(Text)
    notes = Column(Text)
    tags = Column(JSON)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Location(Base):
    __tablename__ = "location"

    id = Column(Text, primary_key=True)
    tenant_id = Column(Text, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)
    contact_id = Column(Text, ForeignKey("contact.id", ondelete="SET NULL"))
    address_line = Column(Text, nullable=False)
    zip = Column(Text)
    city = Column(Text)
    district = Column(Text)
    lat = Column(Numeric(10, 7))
    lng = Column(Numeric(10, 7))
    notes = Column(Text)


class Job(Base):
    __tablename__ = "job"
    __table_args__ = (
        UniqueConstraint("tenant_id", "job_no", name="uq_job_tenant_job_no"),
        CheckConstraint(
            "status IN ('NEW','TRIAGE','READY','ASSIGNING','SCHEDULED','IN_PROGRESS','DONE','INVOICED','PAID','BLOCKED','CANCELLED')",
            name="ck_job_status",
        ),
    )

    id = Column(Text, primary_key=True)
    tenant_id = Column(Text, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)
    job_no = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    category = Column(Text)
    service_type = Column(Text)
    priority = Column(Text)
    status = Column(Text, nullable=False, server_default="NEW")
    contact_id = Column(Text, ForeignKey("contact.id", ondelete="SET NULL"))
    location_id = Column(Text, ForeignKey("location.id", ondelete="SET NULL"))
    description_raw = Column(Text)
    description_norm = Column(JSON)
    created_by = Column(Text, ForeignKey("user.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class JobAssignment(Base):
    __tablename__ = "job_assignment"
    __table_args__ = (
        CheckConstraint(
            "state IN ('SENT','DELIVERED','RESPONDED','EXPIRED','FAILED')",
            name="ck_job_assignment_state",
        ),
    )

    id = Column(Text, primary_key=True)
    tenant_id = Column(Text, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Text, ForeignKey("job.id", ondelete="CASCADE"), nullable=False)
    assignee_contact_id = Column(Text, ForeignKey("contact.id", ondelete="CASCADE"), nullable=False)
    channel = Column(Text, nullable=False)
    batch_id = Column(Text)
    sent_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    state = Column(Text, nullable=False, server_default="SENT")
    score = Column(Numeric(10, 2))


class Response(Base):
    __tablename__ = "response"
    __table_args__ = (CheckConstraint("answer IN ('YES','NO','MAYBE')", name="ck_response_answer"),)

    id = Column(Text, primary_key=True)
    tenant_id = Column(Text, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)
    job_assignment_id = Column(
        Text, ForeignKey("job_assignment.id", ondelete="CASCADE"), nullable=False
    )
    answer = Column(Text, nullable=False)
    comment = Column(Text)
    responded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    meta = Column(JSON)


class Message(Base):
    __tablename__ = "message"

    id = Column(Text, primary_key=True)
    tenant_id = Column(Text, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Text, ForeignKey("job.id", ondelete="SET NULL"))
    direction = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    to_contact_id = Column(Text, ForeignKey("contact.id", ondelete="SET NULL"))
    subject = Column(Text)
    body = Column(Text, nullable=False)
    provider = Column(Text)
    provider_msg_id = Column(Text)
    status = Column(Text, nullable=False)
    sent_at = Column(DateTime(timezone=True))
    received_at = Column(DateTime(timezone=True))
    meta = Column(JSON)


class Document(Base):
    __tablename__ = "document"

    id = Column(Text, primary_key=True)
    tenant_id = Column(Text, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Text, ForeignKey("job.id", ondelete="CASCADE"), nullable=False)
    type = Column(Text, nullable=False)
    file_name = Column(Text, nullable=False)
    storage_uri = Column(Text, nullable=False)
    hash = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Worklog(Base):
    __tablename__ = "worklog"

    id = Column(Text, primary_key=True)
    tenant_id = Column(Text, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Text, ForeignKey("job.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Text, ForeignKey("user.id", ondelete="SET NULL"))
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=False)
    minutes = Column(Integer, nullable=False)
    labor_note = Column(Text)
    materials = Column(JSON)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Payment(Base):
    __tablename__ = "payment"

    id = Column(Text, primary_key=True)
    tenant_id = Column(Text, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Text, ForeignKey("job.id", ondelete="CASCADE"), nullable=False)
    type = Column(Text, nullable=False)
    invoice_no = Column(Text)
    amount_gross = Column(Numeric(12, 2), nullable=False)
    currency = Column(Text, nullable=False, server_default="HUF")
    status = Column(Text, nullable=False)
    due_date = Column(Date)
    paid_at = Column(DateTime(timezone=True))
    meta = Column(JSON)


class EventLog(Base):
    __tablename__ = "event_log"
    __table_args__ = (
        CheckConstraint(
            "scope IN ('EMAIL','PUSH','WORKFLOW','IMPORT','SYSTEM')",
            name="ck_event_log_scope",
        ),
        CheckConstraint("level IN ('INFO','WARN','ERROR')", name="ck_event_log_level"),
        CheckConstraint(
            "reason_code IS NULL OR reason_code IN ('MISSING_EMAIL','MISSING_PHONE','MISSING_LOCATION','MISSING_TENANT','INVALID_CONTACT','TIMEWINDOW_BLOCK','GRACE_BLOCK','DAILY_LIMIT_BLOCK','BATCH_LIMIT_BLOCK','STATUS_BLOCK','UNSUBSCRIBED','OPTIN_REQUIRED','DO_NOT_CONTACT','BOUNCE','PROVIDER_ERROR','NETWORK_ERROR','AUTH_ERROR','UNKNOWN_ERROR')",
            name="ck_event_log_reason_code",
        ),
    )

    id = Column(Text, primary_key=True)
    tenant_id = Column(Text, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Text, ForeignKey("job.id", ondelete="SET NULL"))
    scope = Column(Text, nullable=False)
    level = Column(Text, nullable=False)
    event_type = Column(Text, nullable=False)
    reason_code = Column(Text)
    message = Column(Text)
    data = Column(JSON)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
