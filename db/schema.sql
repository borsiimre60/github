CREATE TABLE IF NOT EXISTS tenant (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    timezone TEXT NOT NULL DEFAULT 'Europe/Budapest',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "user" (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    phone TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_tenant_email UNIQUE (tenant_id, email)
);

CREATE TABLE IF NOT EXISTS contact (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    notes TEXT,
    tags JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS location (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
    contact_id TEXT REFERENCES contact(id) ON DELETE SET NULL,
    address_line TEXT NOT NULL,
    zip TEXT,
    city TEXT,
    district TEXT,
    lat NUMERIC(10,7),
    lng NUMERIC(10,7),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS job (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
    job_no TEXT NOT NULL,
    title TEXT NOT NULL,
    category TEXT,
    service_type TEXT,
    priority TEXT,
    status TEXT NOT NULL DEFAULT 'NEW',
    contact_id TEXT REFERENCES contact(id) ON DELETE SET NULL,
    location_id TEXT REFERENCES location(id) ON DELETE SET NULL,
    description_raw TEXT,
    description_norm JSONB,
    created_by TEXT REFERENCES "user"(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_job_tenant_job_no UNIQUE (tenant_id, job_no),
    CONSTRAINT ck_job_status CHECK (
        status IN (
            'NEW','TRIAGE','READY','ASSIGNING','SCHEDULED',
            'IN_PROGRESS','DONE','INVOICED','PAID','BLOCKED','CANCELLED'
        )
    )
);

CREATE TABLE IF NOT EXISTS job_assignment (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL REFERENCES job(id) ON DELETE CASCADE,
    assignee_contact_id TEXT NOT NULL REFERENCES contact(id) ON DELETE CASCADE,
    channel TEXT NOT NULL,
    batch_id TEXT,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    state TEXT NOT NULL DEFAULT 'SENT',
    score NUMERIC(10,2),
    CONSTRAINT ck_job_assignment_state CHECK (state IN ('SENT','DELIVERED','RESPONDED','EXPIRED','FAILED'))
);

CREATE TABLE IF NOT EXISTS response (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
    job_assignment_id TEXT NOT NULL REFERENCES job_assignment(id) ON DELETE CASCADE,
    answer TEXT NOT NULL,
    comment TEXT,
    responded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meta JSONB,
    CONSTRAINT ck_response_answer CHECK (answer IN ('YES','NO','MAYBE'))
);

CREATE TABLE IF NOT EXISTS message (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
    job_id TEXT REFERENCES job(id) ON DELETE SET NULL,
    direction TEXT NOT NULL,
    type TEXT NOT NULL,
    to_contact_id TEXT REFERENCES contact(id) ON DELETE SET NULL,
    subject TEXT,
    body TEXT NOT NULL,
    provider TEXT,
    provider_msg_id TEXT,
    status TEXT NOT NULL,
    sent_at TIMESTAMPTZ,
    received_at TIMESTAMPTZ,
    meta JSONB
);

CREATE TABLE IF NOT EXISTS document (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL REFERENCES job(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    file_name TEXT NOT NULL,
    storage_uri TEXT NOT NULL,
    hash TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS worklog (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL REFERENCES job(id) ON DELETE CASCADE,
    user_id TEXT REFERENCES "user"(id) ON DELETE SET NULL,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ NOT NULL,
    minutes INTEGER NOT NULL,
    labor_note TEXT,
    materials JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payment (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL REFERENCES job(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    invoice_no TEXT,
    amount_gross NUMERIC(12,2) NOT NULL,
    currency TEXT NOT NULL DEFAULT 'HUF',
    status TEXT NOT NULL,
    due_date DATE,
    paid_at TIMESTAMPTZ,
    meta JSONB
);

CREATE TABLE IF NOT EXISTS event_log (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
    job_id TEXT REFERENCES job(id) ON DELETE SET NULL,
    scope TEXT NOT NULL,
    level TEXT NOT NULL,
    event_type TEXT NOT NULL,
    reason_code TEXT,
    message TEXT,
    data JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_event_log_scope CHECK (scope IN ('EMAIL','PUSH','WORKFLOW','IMPORT','SYSTEM')),
    CONSTRAINT ck_event_log_level CHECK (level IN ('INFO','WARN','ERROR')),
    CONSTRAINT ck_event_log_reason_code CHECK (
        reason_code IS NULL OR reason_code IN (
            'MISSING_EMAIL','MISSING_PHONE','MISSING_LOCATION','MISSING_TENANT','INVALID_CONTACT',
            'TIMEWINDOW_BLOCK','GRACE_BLOCK','DAILY_LIMIT_BLOCK','BATCH_LIMIT_BLOCK','STATUS_BLOCK',
            'UNSUBSCRIBED','OPTIN_REQUIRED','DO_NOT_CONTACT',
            'BOUNCE','PROVIDER_ERROR','NETWORK_ERROR','AUTH_ERROR','UNKNOWN_ERROR'
        )
    )
);
