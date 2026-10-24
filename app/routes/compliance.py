from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.assessment import Assessment
from app.models.organization import Organization


router = APIRouter(
    prefix="/compliance",
    tags=["Compliance"]
)



@router.get("/{organization_id}")
def get_compliance_score(
    organization_id: int,
    db: Session = Depends(get_db)
):

    organization = db.query(Organization).filter(
        Organization.organization_id == organization_id
    ).first()


    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )


    assessments = db.query(Assessment).filter(
        Assessment.organization_id == organization_id
    ).all()


    if not assessments:
        return {
            "organization_id": organization_id,
            "total_controls": 0,
            "implemented_controls": 0,
            "compliance_score": 0,
            "status": "No assessments"
        }



    # عدد الـ Controls الفريدة
    unique_controls = set()

    implemented_controls = 0
    total_score = 0


    for assessment in assessments:

        unique_controls.add(
            assessment.control_id
        )


        total_score += assessment.score


        if assessment.status.lower() == "implemented":
            implemented_controls += 1



    total_controls = len(unique_controls)


    compliance_score = total_score / len(assessments)



    if compliance_score >= 90:
        status = "Excellent"

    elif compliance_score >= 75:
        status = "Good"

    elif compliance_score >= 50:
        status = "Needs Improvement"

    else:
        status = "Poor"



    return {

        "organization_id": organization_id,

        "total_controls": total_controls,

        "implemented_controls": implemented_controls,

        "compliance_score": round(
            compliance_score,
            2
        ),

        "status": status
    }