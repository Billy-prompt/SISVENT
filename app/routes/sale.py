from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session, joinedload
from app.models.sale import Sale
from app.schemas.sale import SaleCreate, SaleOut, SaleFull
from app.models.saledetail import SaleDetail
from app.models.product import Product
from app.config.db import get_db
from typing import List

router = APIRouter(prefix='/sale', tags=['sale'])

# Llamar venta por ID

@router.get('/{id_sale}', response_model=SaleFull)
def get_sale(id_sale:int, db:Session = Depends(get_db)):
    sale = db.query(Sale).options(joinedload(Sale.details).joinedload(SaleDetail.product)).filter(Sale.id_sale == id_sale).first()   
    if not sale: 
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return sale

# Crear venta

@router.post('/ventas/registrar', response_model=SaleOut)
def create_sale(sale_data:SaleCreate ,db:Session = Depends(get_db)):
    new_sale = Sale(
        datesale = sale_data.datesale,
        totalsale = 0.0
    )

    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)

    total = 0.0

    # Verificar si los productos existen y calcular el subtotal y el total de la venta

    for detail in sale_data.details:
        product = db.query(Product).filter(Product.id_product == detail.id_product).first()

        if not product:
            raise ValueError(f"Producto con id {detail.id_product} no existe")
        
        subtotal = product.sale_price * detail.quantity
        total += subtotal

        # Actualizar el stock del producto

        if product.stock < detail.quantity:
            raise ValueError(f"Stock insuficiente para el producto {product.product}")
        product.stock -= detail.quantity
        db.commit()
        db.refresh(product)

        

        new_detail = SaleDetail(
            id_sale = new_sale.id_sale,
            id_product = detail.id_product,
            quantity = detail.quantity,
            subtotal = subtotal
        )

        db.add(new_detail)
    
    new_sale.totalsale = total
    db.commit()
    db.refresh(new_sale)

    return new_sale
            


