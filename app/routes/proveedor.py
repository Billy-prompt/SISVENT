from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config.db import get_db
from app.models import Supplier 

router = APIRouter()

# autocomplete proveedores

@router.get("/supplier/autocomplete")
def autocomplete_suppliers(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
    ):
    results = db.query(Supplier).filter(Supplier.supplier_name.ilike(f"%{q}%")).limit(10).all()
    return [{"name": s.supplier_name} for s in results]