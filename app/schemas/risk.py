from pydantic import BaseModel, Field


class RiskCreate(BaseModel):

    organization_id: int

    title: str

    description: str | None = None

    likelihood: int = Field(
        ge=1,
        le=5,
        description="Likelihood must be between 1 and 5"
    )

    impact: int = Field(
        ge=1,
        le=5,
        description="Impact must be between 1 and 5"
    )

    status: str

    mitigation: str | None = None



class RiskUpdate(BaseModel):

    title: str

    description: str | None = None

    likelihood: int = Field(
        ge=1,
        le=5,
        description="Likelihood must be between 1 and 5"
    )

    impact: int = Field(
        ge=1,
        le=5,
        description="Impact must be between 1 and 5"
    )

    status: str

    mitigation: str | None = None



class ControlInRisk(BaseModel):

    control_id: int


    class Config:
        from_attributes = True



class RiskResponse(BaseModel):

    risk_id: int

    organization_id: int

    title: str

    description: str | None = None

    likelihood: int

    impact: int

    risk_score: int

    severity: str

    status: str

    mitigation: str | None = None

    controls: list[ControlInRisk] = []


    class Config:
        from_attributes = True