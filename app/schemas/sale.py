from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from .saledetail import SaleDetailCreate, SaleDetailOut

class SaleCreate(BaseModel):
    datesale: Optional[date] = None
    totalsale: float
    details: List[SaleDetailCreate]

class SaleOut(BaseModel):
    id_sale: int
    datesale: Optional[date]
    totalsale: float

    class Config:
        from_attributes = True


class SaleFull(SaleOut):
    details: List[SaleDetailOut]