from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.risk import RiskUpdate
from app.core.dependencies import require_role
from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.schemas.risk import RiskCreate, RiskResponse, RiskUpdate
from app.models.risk import Risk
from app.models.risk_control import RiskControl
from app.models.control import Control
from app.models.framework import Framework
from app.core.audit import create_audit_log
from app.schemas.risk import RiskCreate, RiskResponse


router = APIRouter(
    prefix="/risks",
    tags=["Risks"]
)


# Create Risk
@router.post("/", response_model=RiskResponse)
def create_risk(
    risk: RiskCreate,
    db: Session = Depends(get_db),
    user=Depends(
        require_role(["Admin", "Auditor"])
    )
):

    new_risk = Risk(
        organization_id=risk.organization_id,
        title=risk.title,
        description=risk.description,
        likelihood=risk.likelihood,
        impact=risk.impact,
        status=risk.status,
        mitigation=risk.mitigation
    )

    db.add(new_risk)
    db.commit()
    db.refresh(new_risk)


    create_audit_log(
    db,
    int(user["sub"]),
    "CREATE",
    "Risk",
    f"Created risk {new_risk.title}"
)


    risk_score = new_risk.likelihood * new_risk.impact


    if risk_score <= 5:
        severity = "Low"
    elif risk_score <= 10:
        severity = "Medium"
    elif risk_score <= 15:
        severity = "High"
    else:
        severity = "Critical"


    return {
        "risk_id": new_risk.risk_id,
        "organization_id": new_risk.organization_id,
        "title": new_risk.title,
        "description": new_risk.description,
        "likelihood": new_risk.likelihood,
        "impact": new_risk.impact,
        "risk_score": risk_score,
        "severity": severity,
        "status": new_risk.status,
        "mitigation": new_risk.mitigation
    }



# Get All Risks
@router.get("/", response_model=list[RiskResponse])
def get_risks(
    db: Session = Depends(get_db)
):

    risks = db.query(Risk).all()

    result = []


    for risk in risks:

        risk_score = risk.likelihood * risk.impact


        if risk_score <= 5:
            severity = "Low"

        elif risk_score <= 10:
            severity = "Medium"

        elif risk_score <= 15:
            severity = "High"

        else:
            severity = "Critical"



        result.append({
            "risk_id": risk.risk_id,
            "organization_id": risk.organization_id,
            "title": risk.title,
            "description": risk.description,
            "likelihood": risk.likelihood,
            "impact": risk.impact,
            "risk_score": risk_score,
            "severity": severity,
            "status": risk.status,
            "mitigation": risk.mitigation,

            "controls": [
                {
                    "control_id": rc.control_id
                }
                for rc in risk.controls
            ]
        })


    return result



# Risk Matrix Summary
@router.get("/matrix")
def get_risk_matrix(
    db: Session = Depends(get_db)
):

    risks = db.query(Risk).all()


    matrix = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0
    }


    for risk in risks:

        score = risk.likelihood * risk.impact


        if score <= 5:
            severity = "Low"

        elif score <= 10:
            severity = "Medium"

        elif score <= 15:
            severity = "High"

        else:
            severity = "Critical"


        matrix[severity] += 1


    return matrix



# Get Risk Details With Controls
@router.get("/{risk_id}/controls")
def get_risk_controls(
    risk_id: int,
    db: Session = Depends(get_db)
):

    risk = db.query(Risk).filter(
        Risk.risk_id == risk_id
    ).first()


    if not risk:
        raise HTTPException(
            status_code=404,
            detail="Risk not found"
        )


    mappings = db.query(RiskControl).filter(
        RiskControl.risk_id == risk_id
    ).all()


    controls = []


    for mapping in mappings:

        control = db.query(Control).filter(
            Control.control_id == mapping.control_id
        ).first()


        if control:

            framework = db.query(Framework).filter(
                Framework.framework_id == control.framework_id
            ).first()


            controls.append({
                "control_id": control.control_id,
                "control_name": control.title,
                "framework": framework.name if framework else None
            })


    risk_score = risk.likelihood * risk.impact


    if risk_score <= 5:
        severity = "Low"

    elif risk_score <= 10:
        severity = "Medium"

    elif risk_score <= 15:
        severity = "High"

    else:
        severity = "Critical"



    return {
        "risk_id": risk.risk_id,
        "risk_title": risk.title,
        "description": risk.description,
        "severity": severity,
        "risk_score": risk_score,
        "controls": controls
    }
    # Update Risk
@router.put("/{risk_id}", response_model=RiskResponse)
def update_risk(
    risk_id: int,
    risk: RiskUpdate,
    db: Session = Depends(get_db),
    user=Depends(
        require_role(["Admin", "Auditor"])
    )
):

    db_risk = db.query(Risk).filter(
        Risk.risk_id == risk_id
    ).first()


    if not db_risk:
        raise HTTPException(
            status_code=404,
            detail="Risk not found"
        )


    db_risk.title = risk.title
    db_risk.description = risk.description
    db_risk.likelihood = risk.likelihood
    db_risk.impact = risk.impact
    db_risk.status = risk.status
    db_risk.mitigation = risk.mitigation


    db.commit()
    db.refresh(db_risk)


    create_audit_log(
    db,
    int(user["sub"]),
    "UPDATE",
    "Risk",
    f"Updated risk {db_risk.title}"
)


    db.add(audit)
    db.commit()


    risk_score = (
        db_risk.likelihood *
        db_risk.impact
    )


    if risk_score <= 5:
        severity = "Low"

    elif risk_score <= 10:
        severity = "Medium"

    elif risk_score <= 15:
        severity = "High"

    else:
        severity = "Critical"


    return {
        "risk_id": db_risk.risk_id,
        "organization_id": db_risk.organization_id,
        "title": db_risk.title,
        "description": db_risk.description,
        "likelihood": db_risk.likelihood,
        "impact": db_risk.impact,
        "risk_score": risk_score,
        "severity": severity,
        "status": db_risk.status,
        "mitigation": db_risk.mitigation,
        "controls": []
    }
    # Delete Risk
@router.delete("/{risk_id}")
def delete_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    user=Depends(
        require_role(["Admin"])
    )
):

    risk = db.query(Risk).filter(
        Risk.risk_id == risk_id
    ).first()


    if not risk:
        raise HTTPException(
            status_code=404,
            detail="Risk not found"
        )


    risk_title = risk.title


    db.delete(risk)
    db.commit()


    create_audit_log(
    db,
    int(user["sub"]),
    "DELETE",
    "Risk",
    f"Deleted risk {risk_title}"
)


    return {
        "message": "Risk deleted successfully",
        "deleted_risk": risk_title
    }
@router.patch("/{risk_id}/treatment")
def update_risk_treatment(
    risk_id: int,
    treatment_status: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    risk = db.query(Risk).filter(
        Risk.risk_id == risk_id
    ).first()


    if not risk:
        raise HTTPException(
            status_code=404,
            detail="Risk not found"
        )


    allowed_status = [
        "Open",
        "In Progress",
        "Closed"
    ]


    if treatment_status not in allowed_status:
        raise HTTPException(
            status_code=400,
            detail="Invalid treatment status"
        )


    risk.treatment_status = treatment_status


    db.commit()

    db.refresh(risk)


    return {
        "message": "Risk treatment updated successfully",
        "risk_id": risk.risk_id,
        "risk_title": risk.title,
        "treatment_status": risk.treatment_status
    }