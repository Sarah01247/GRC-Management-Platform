from fastapi import FastAPI

from app.database.connection import Base, engine

# Routes
from app.routes import (
    audit_logs,
    organizations,
    frameworks,
    controls,
    assessments,
    risks,
    users,
    dashboard,
    risk_controls,
    compliance,
    auth,
    evidence as evidence_router
)

# Models (لتسجيل الجداول)
from app.models.audit_log import AuditLog
from app.models.framework import Framework
from app.models.organization import Organization
from app.models.control import Control
from app.models.assessment import Assessment
from app.models.risk import Risk
from app.models.risk_control import RiskControl
from app.models.user import User
from app.models.evidence import Evidence


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="GRC Management Platform",
    version="1.0"
)


# Include Routes
app.include_router(audit_logs.router)
app.include_router(evidence_router.router)
app.include_router(risk_controls.router)
app.include_router(organizations.router)
app.include_router(frameworks.router)
app.include_router(controls.router)
app.include_router(assessments.router)
app.include_router(risks.router)
app.include_router(dashboard.router)
app.include_router(users.router)
app.include_router(compliance.router)
app.include_router(auth.router)


@app.get("/")
def home():
    return {
        "message": "GRC Platform API is running"
    }