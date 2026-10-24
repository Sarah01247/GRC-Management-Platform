from pydantic import BaseModel


class ControlAssessmentCreate(BaseModel):

    control_id: int

    status: str

    effectiveness: str

    evidence: str | None = None

    notes: str | None = None



class ControlAssessmentResponse(BaseModel):

    assessment_id: int

    control_id: int

    status: str

    effectiveness: str

    evidence: str | None = None

    notes: str | None = None


    class Config:
        from_attributes = True