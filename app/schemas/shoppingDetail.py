from pydantic import BaseModel
from typing import Optional

class ShoppingDetailCreate(BaseModel):
    id_shopping: Optional[int] = None
    id_product: Optional[int] = None
    quantity: Optional[int] = None
    subtotal: Optional[float] = None

class ShoppingDetailOut(BaseModel):
    id_shopping_detail: Optional[int] = None
    id_shopping: Optional[int] = None
    id_product: Optional[int] = None
    quantity: Optional[int] = None
    subtotal: Optional[float] = None