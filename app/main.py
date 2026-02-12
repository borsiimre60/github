from fastapi import FastAPI

from app.core.config import settings
from app.routers.assignments import router as assignments_router
from app.routers.diagnostics import router as diagnostics_router
from app.routers.jobs import router as jobs_router

app = FastAPI(title=settings.app_name)

app.include_router(jobs_router)
app.include_router(assignments_router)
app.include_router(diagnostics_router)


@app.get("/health")
def health():
    return {"status": "ok"}
