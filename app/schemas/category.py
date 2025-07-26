from pydantic import BaseModel

class CategoryCreate(BaseModel):
    category: str
    

class CategoryOut(BaseModel):
    id_category: int
    category: str


    class Config:
        from_attributes = True