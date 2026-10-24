from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import require_role
from app.models.audit_log import AuditLog


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)


@router.get("/")
def get_audit_logs(
    db: Session = Depends(get_db),
    user=Depends(require_role(["Admin", "Auditor"]))
):

    logs = db.query(AuditLog).order_by(
        AuditLog.timestamp.desc()
    ).all()


    result = []

    for log in logs:

        result.append({
            "username": log.user.username if log.user else None,
            "action": log.action,
            "entity": log.entity,
            "description": log.description,
            "timestamp": log.timestamp
        })


    return result