from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    password: EmailStr
    role: str

class UserOut(BaseModel):
    id: int
    username: str
    password: EmailStr
    role: str

    class Config:
        from_attributes = True