from pydantic import BaseModel


class ControlCreate(BaseModel):

    framework_id: int
    control_code: str
    title: str
    description: str
    category: str



class EvidenceInControl(BaseModel):

    evidence_id: int
    file_name: str
    file_path: str
    uploaded_by: str


    class Config:
        from_attributes = True



class ControlResponse(BaseModel):

    control_id: int
    framework_id: int
    control_code: str
    title: str
    description: str
    category: str

    evidences: list[EvidenceInControl] = []


    class Config:
        from_attributes = True