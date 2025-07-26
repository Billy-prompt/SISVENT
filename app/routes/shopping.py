from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.models.shopping import Shopping
from app.schemas.shopping import ShoppingCreate, ShoppingOut, ShoppingFull
from app.models.shoppingDetail import ShoppingDetail
from app.models.product import Product
from app.models.suppliers import Supplier
from app.config.db import get_db
from typing import List

router = APIRouter(prefix='/shopping', tags=['shopping'])

# Llamar compras

# @router.get('/', response_model=List[ShoppingOut])
# def get_shoppings(db:Session = Depends(get_db)):
#     return db.query(Shopping).all()

# Crear compra

@router.post('/', response_model=ShoppingOut)
def create_shopping(shopping_data: ShoppingCreate, db: Session = Depends(get_db)):
    new_shopping = Shopping(
        id_supplier=shopping_data.id_supplier,
        shopping_date=shopping_data.shopping_date,
        total_shopping=shopping_data.total_shopping
    )

    db.add(new_shopping)
    db.commit()
    db.refresh(new_shopping)

    total = 0.0

    # Verificar si los productos existen y calcular el subtotal y el total de la compra

    for detail in shopping_data.details:
        product = db.query(Product).filter(Product.id_product == detail.id_product).first()

        if not product:
            raise HTTPException(status_code=404, detail=f"Producto con id {detail.id_product} no existe")
        
        subtotal = product.shopping_price * detail.quantity
        total += subtotal

        # Actualizar el stock del producto

        product.stock += detail.quantity
        db.commit()
        db.refresh(product)

        # Crear detalle de compra

        new_detail = ShoppingDetail(
            id_shopping=new_shopping.id_shopping,
            id_product=detail.id_product,
            quantity=detail.quantity,
            subtotal=subtotal
        )
        db.add(new_detail)

    new_shopping.total_shopping = total
    db.commit()
    db.refresh(new_shopping)

    return new_shopping

# Llamar compra por ID

@router.get('/{shopping_id}', response_model=ShoppingFull)
def get_shopping_by_id(shopping_id: int, db: Session = Depends(get_db)):
    shopping = db.query(Shopping).options(
        joinedload(Shopping.details).joinedload(ShoppingDetail.product),
        joinedload(Shopping.supplier)
    ).filter(Shopping.id_shopping == shopping_id).first()

    if not shopping:
        raise HTTPException(status_code=404, detail=f"Compra con id {shopping_id} no existe")

    return shopping

# Actualizar compra

@router.put('/{shopping_id}', response_model=ShoppingOut)
def update_shopping(shopping_id: int, shopping_data: ShoppingCreate, db: Session = Depends(get_db)):
    shopping = db.query(Shopping).filter(Shopping.id_shopping == shopping_id).first()

    if not shopping:
        raise HTTPException(status_code=404, detail=f"Compra con id {shopping_id} no existe")

    shopping.id_supplier = shopping_data.id_supplier
    shopping.shopping_date = shopping_data.shopping_date
    shopping.total_shopping = shopping_data.total_shopping

    db.commit()
    db.refresh(shopping)

    total = 0.0

    # Actualizar detalles de compra

    for detail in shopping_data.details:
        product = db.query(Product).filter(Product.id_product == detail.id_product).first()

        if not product:
            raise HTTPException(status_code=404, detail=f"Producto con id {detail.id_product} no existe")
        
        subtotal = product.shopping_price * detail.quantity
        total = subtotal

        # Actualizar stock del producto

        product.stock = detail.quantity
        db.commit()
        db.refresh(product)

        # Actualizar o crear detalle de compra

        existing_detail = db.query(ShoppingDetail).filter(
            ShoppingDetail.id_shopping == shopping_id,
            ShoppingDetail.id_product == detail.id_product
        ).first()

        if existing_detail:
            existing_detail.quantity = detail.quantity
            existing_detail.subtotal = subtotal
        else:
            new_detail = ShoppingDetail(
                id_shopping=shopping_id,
                id_product=detail.id_product,
                quantity=detail.quantity,
                subtotal=subtotal
            )
            db.add(new_detail)



    db.commit()
    db.refresh(shopping)

    return shopping