from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import require_role
from app.database.connection import get_db
from app.models.control import Control
from app.schemas.control import ControlCreate, ControlResponse
from app.core.audit import create_audit_log

router = APIRouter(
    prefix="/controls",
    tags=["Controls"]
)


@router.post("/", response_model=ControlResponse)
def create_control(
    control: ControlCreate,
    db: Session = Depends(get_db),
    user = Depends(
        require_role(["Admin"])
    )
):

    new_control = Control(
        framework_id=control.framework_id,
        control_code=control.control_code,
        title=control.title,
        description=control.description,
        category=control.category
    )

    db.add(new_control)
    db.commit()
    db.refresh(new_control)
    

    create_audit_log(
        db,
        int(user["sub"]),
        "CREATE",
        "Control",
        f"Created control {new_control.title}"
    )

    return new_control



# Get All Controls
@router.get("/", response_model=list[ControlResponse])
def get_controls(
    db: Session = Depends(get_db)
):

    return db.query(Control).all()



# Get Controls By Framework
@router.get("/framework/{framework_id}", response_model=list[ControlResponse])
def get_controls_by_framework(
    framework_id: int,
    db: Session = Depends(get_db)
):

    controls = db.query(Control).filter(
        Control.framework_id == framework_id
    ).all()

    return controls