from pydantic import BaseModel


class EvidenceCreate(BaseModel):

    control_id: int

    file_name: str

    file_path: str



class EvidenceUpdate(BaseModel):

    file_name: str

    file_path: str



class EvidenceResponse(BaseModel):

    evidence_id: int

    control_id: int

    file_name: str

    file_path: str

    uploaded_by: str


    class Config:
        from_attributes = True