from pydantic import BaseModel
from datetime import date
from app.models.suppliers import Supplier

class SupplierCreate(BaseModel):
    supplier_name: str
    telephone: str

class SupplierOut(BaseModel):
    id_supplier: int
    supplier_name: str
    telephone: str

    class Config:
        from_attributes = True