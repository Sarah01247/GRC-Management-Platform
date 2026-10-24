from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.risk_control import RiskControl
from app.schemas.risk_control import RiskControlCreate, RiskControlResponse

router = APIRouter(
    prefix="/risk-controls",
    tags=["Risk Controls"]
)




# Create Risk-Control Mapping
@router.post("/", response_model=RiskControlResponse)
def create_risk_control(
    data: RiskControlCreate,
    db: Session = Depends(get_db)
):

    # Check duplicate mapping
    existing_mapping = db.query(RiskControl).filter(
        RiskControl.risk_id == data.risk_id,
        RiskControl.control_id == data.control_id
    ).first()


    if existing_mapping:
        raise HTTPException(
            status_code=400,
            detail="Risk already linked to this Control"
        )


    new_mapping = RiskControl(
        risk_id=data.risk_id,
        control_id=data.control_id
    )


    db.add(new_mapping)
    db.commit()
    db.refresh(new_mapping)


    return new_mapping



# Get All Mappings
@router.get("/", response_model=list[RiskControlResponse])
def get_risk_controls(
    db: Session = Depends(get_db)
):

    return db.query(RiskControl).all()