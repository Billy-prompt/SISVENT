from pydantic import BaseModel
from typing import Optional
from app.models.user import RoleEnum

class UserCreate(BaseModel):
    username: str
    password: str
    role: RoleEnum

class UserOut(BaseModel):
    id: int
    username: str
    role: RoleEnum

    class Config:
        from_attributes = True