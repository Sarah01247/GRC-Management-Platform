from pydantic import BaseModel


class UserCreate(BaseModel):

    username: str

    email: str

    password: str

    role: str = "Viewer"



class UserResponse(BaseModel):

    user_id: int

    username: str

    email: str

    role: str


    class Config:
        from_attributes = True