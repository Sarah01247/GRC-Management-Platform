from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.framework import Framework
from app.schemas.framework import FrameworkCreate, FrameworkResponse
from app.core.audit import create_audit_log
from app.core.dependencies import require_role
router = APIRouter(
    prefix="/frameworks",
    tags=["Frameworks"]
)

@router.post("/", response_model=FrameworkResponse)
def create_framework(
    framework: FrameworkCreate,
    db: Session = Depends(get_db),
    user=Depends(
        require_role(["Admin"])
    )
):

    new_framework = Framework(
        name=framework.name,
        version=framework.version,
        description=framework.description
    )

    db.add(new_framework)
    db.commit()
    db.refresh(new_framework)

    create_audit_log(
        db,
        int(user["sub"]),
        "CREATE",
        "Framework",
        f"Created framework {new_framework.name}"
    )

    return new_framework


# Get All Frameworks
@router.get("/", response_model=list[FrameworkResponse])
def get_frameworks(
    db: Session = Depends(get_db)
):

    return db.query(Framework).all()