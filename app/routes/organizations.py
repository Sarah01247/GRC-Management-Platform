from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.models.organization import Organization

from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse
)

from app.core.dependencies import require_role
from app.core.audit import create_audit_log


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)


# Create Organization
@router.post(
    "/",
    response_model=OrganizationResponse
)
def create_organization(
    organization_data: OrganizationCreate,
    db: Session = Depends(get_db),
    user=Depends(
        require_role(["Admin"])
    )
):

    organization = Organization(
        name=organization_data.name,
        industry=organization_data.industry,
        size=organization_data.size
    )

    db.add(organization)
    db.commit()
    db.refresh(organization)


    create_audit_log(
        db,
        int(user["sub"]),
        "CREATE",
        "Organization",
        f"Created organization {organization.name}"
    )


    return organization



# Get Organizations
@router.get(
    "/",
    response_model=list[OrganizationResponse]
)
def get_organizations(
    db: Session = Depends(get_db),
    user=Depends(
        require_role(["Admin", "Auditor", "Viewer"])
    )
):

    return db.query(Organization).all()



# Get Single Organization
@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse
)
def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    user=Depends(
        require_role(["Admin", "Auditor", "Viewer"])
    )
):

    organization = db.query(Organization).filter(
        Organization.organization_id == organization_id
    ).first()


    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )


    return organization



# Update Organization
@router.put(
    "/{organization_id}",
    response_model=OrganizationResponse
)
def update_organization(
    organization_id: int,
    organization_data: OrganizationCreate,
    db: Session = Depends(get_db),
    user=Depends(
        require_role(["Admin"])
    )
):

    organization = db.query(Organization).filter(
        Organization.organization_id == organization_id
    ).first()


    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )


    organization.name = organization_data.name
    organization.industry = organization_data.industry
    organization.size = organization_data.size


    db.commit()
    db.refresh(organization)


    create_audit_log(
        db,
        int(user["sub"]),
        "UPDATE",
        "Organization",
        f"Updated organization {organization.name}"
    )


    return organization



# Delete Organization
@router.delete(
    "/{organization_id}"
)
def delete_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    user=Depends(
        require_role(["Admin"])
    )
):

    organization = db.query(Organization).filter(
        Organization.organization_id == organization_id
    ).first()


    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )


    db.delete(organization)
    db.commit()


    create_audit_log(
        db,
        int(user["sub"]),
        "DELETE",
        "Organization",
        f"Deleted organization {organization.name}"
    )


    return {
        "message": "Organization deleted successfully"
    }