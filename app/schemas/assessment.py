from pydantic import BaseModel


class AssessmentCreate(BaseModel):
    control_id: int
    status: str
    evidence: str | None = None


class AssessmentResponse(BaseModel):

    assessment_id: int
    control_id: int
    status: str
    evidence: str | None = None


    class Config:
        from_attributes = True