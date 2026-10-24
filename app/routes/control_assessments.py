from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.models.control_assessment import ControlAssessment

from app.schemas.control_assessment import (
    ControlAssessmentCreate,
    ControlAssessmentResponse
)


router = APIRouter(
    prefix="/control-assessments",
    tags=["Control Assessments"]
)



# Create Control Assessment
@router.post(
    "/",
    response_model=ControlAssessmentResponse
)
def create_control_assessment(
    assessment: ControlAssessmentCreate,
    db: Session = Depends(get_db)
):

    new_assessment = ControlAssessment(
        control_id=assessment.control_id,
        status=assessment.status,
        effectiveness=assessment.effectiveness,
        evidence=assessment.evidence,
        notes=assessment.notes
    )


    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)


    return new_assessment



# Get All Control Assessments
@router.get(
    "/",
    response_model=list[ControlAssessmentResponse]
)
def get_control_assessments(
    db: Session = Depends(get_db)
):

    return db.query(ControlAssessment).all()