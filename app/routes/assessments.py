from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.audit import create_audit_log
from app.core.dependencies import require_role
from app.database.connection import get_db
from app.models.control_assessment import ControlAssessment
from app.schemas.assessment import AssessmentCreate, AssessmentResponse


router = APIRouter(
    prefix="/assessments",
    tags=["Assessments"]
)



@router.post("/", response_model=AssessmentResponse)
def create_assessment(
    assessment: AssessmentCreate,
    db: Session = Depends(get_db),
    user = Depends(
        require_role(["Admin", "Auditor"])
    )
):

    new_assessment = ControlAssessment(
    control_id=assessment.control_id,
    status=assessment.status,
    evidence=assessment.evidence
)


    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)


    create_audit_log(
        db,
        int(user["sub"]),
        "CREATE",
        "Assessment",
        f"Created assessment for control {new_assessment.control_id}"
    )


    return new_assessment




# Get All Assessments
@router.get("/", response_model=list[AssessmentResponse])
def get_assessments(
    db: Session = Depends(get_db)
):

    return db.query(ControlAssessment).all()