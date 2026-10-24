from pydantic import BaseModel


class FrameworkCreate(BaseModel):

    name: str
    version: str
    description: str


class FrameworkResponse(BaseModel):

    framework_id: int
    name: str
    version: str
    description: str

    class Config:
        from_attributes = True