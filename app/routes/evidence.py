from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.database.connection import get_db
from app.models.evidence import Evidence
from app.core.audit import create_audit_log
from app.schemas.evidence import (
    EvidenceCreate,
    EvidenceUpdate,
    EvidenceResponse
)
from app.core.dependencies import require_role


router = APIRouter(
    prefix="/evidences",
    tags=["Evidences"]
)


# Create Evidence
@router.post("/", response_model=EvidenceResponse)
def create_evidence(
    evidence: EvidenceCreate,
    db: Session = Depends(get_db),
    user=Depends(
        require_role(["Admin", "Auditor"])
    )
):

    new_evidence = Evidence(
        control_id=evidence.control_id,
        file_name=evidence.file_name,
        file_path=evidence.file_path,
        uploaded_by=user["sub"]
    )


    db.add(new_evidence)
    db.commit()
    db.refresh(new_evidence)


    create_audit_log(
    db,
    int(user["sub"]),
    "CREATE",
    "Evidence",
    f"Uploaded evidence {new_evidence.file_name}"
)


    return new_evidence



# Get All Evidences
@router.get("/", response_model=list[EvidenceResponse])
def get_evidences(
    db: Session = Depends(get_db)
):

    return db.query(Evidence).all()
# Update Evidence
@router.put("/{evidence_id}", response_model=EvidenceResponse)
def update_evidence(
    evidence_id: int,
    evidence: EvidenceUpdate,
    db: Session = Depends(get_db),
    user=Depends(
        require_role(["Admin", "Auditor"])
    )
):

    db_evidence = db.query(Evidence).filter(
        Evidence.evidence_id == evidence_id
    ).first()


    if not db_evidence:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found"
        )


    db_evidence.file_name = evidence.file_name
    db_evidence.file_path = evidence.file_path


    db.commit()
    db.refresh(db_evidence)


    create_audit_log(
    db,
    int(user["sub"]),
    "UPDATE",
    "Evidence",
    f"Updated evidence {db_evidence.file_name}"
)


    return db_evidence
    # Delete Evidence
@router.delete("/{evidence_id}")
def delete_evidence(
    evidence_id: int,
    db: Session = Depends(get_db),
    user=Depends(
        require_role(["Admin"])
    )
):

    evidence = db.query(Evidence).filter(
        Evidence.evidence_id == evidence_id
    ).first()


    if not evidence:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found"
        )


    evidence_name = evidence.file_name


    db.delete(evidence)
    db.commit()


    create_audit_log(
    db,
    int(user["sub"]),
    "DELETE",
    "Evidence",
    f"Deleted evidence {evidence_name}"
)


    return {
        "message": "Evidence deleted successfully",
        "deleted_evidence": evidence_name
    }