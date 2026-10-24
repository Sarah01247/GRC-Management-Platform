from pydantic import BaseModel


class RiskControlCreate(BaseModel):

    risk_id: int
    control_id: int



class RiskControlResponse(BaseModel):

    id: int
    risk_id: int
    control_id: int


    class Config:
        from_attributes = True