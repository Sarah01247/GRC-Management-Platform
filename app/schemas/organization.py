from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    name: str
    industry: str | None = None
    size: str | None = None


class OrganizationResponse(BaseModel):
    organization_id: int
    name: str
    industry: str | None = None
    size: str | None = None

    class Config:
        from_attributes = True