from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductOut
from app.config.db import get_db
from typing import List


router = APIRouter(prefix='/product', tags=["Product"])

# Crear un nuevo producto

@router.get("/{id_product}", response_model=ProductOut)
def get_product(id_product: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id_product == id_product).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no existe")
    return product

# Actualizar producto

@router.put("/{id_product}", response_model=ProductOut)
def update_product(id_product:int, product_data: ProductCreate, db:Session = Depends(get_db)):
    product_exist = db.query(Product).filter(Product.id_product == id_product).first()
    
    if not product_exist:
        raise HTTPException(status_code=400, detail="Producto no existe")
    
    product_exist.product = product_data.product
    product_exist.shopping_price = product_data.shopping_price
    product_exist.sale_price = product_data.sale_price
    product_exist.stock = product_data.stock
    product_exist.id_category = product_data.id_category

    db.commit()
    db.refresh(product_exist)
    return product_exist

# Eliminar un producto

@router.delete("/{id_product}")
def delete_product(id_product:int, db:Session = Depends(get_db)):
    product_exist = db.query(Product).filter(Product.id_product == id_product).first()
    
    if not product_exist:
        raise HTTPException(status_code=400, detail="Producto no existe")
    
    db.delete(product_exist)
    db.commit()
    return {"detail": "Producto eliminado"}
