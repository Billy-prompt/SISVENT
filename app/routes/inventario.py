from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.config.db import get_db
from app.models import Product
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Vista principal del inventario
@router.get("/inventario", response_class=HTMLResponse)
def ver_inventario(request: Request):
    return templates.TemplateResponse("inventario.html", {"request": request})

# API para obtener el listado del inventario
@router.get("/inventory/list")
def listar_inventario(db: Session = Depends(get_db)):
    productos = db.query(Product).all()
    return [
        {
            "id": p.id_product,
            "name": p.product,
            "category": p.category.category if p.category else "Sin categoría",
            "quantity": p.stock,
        }
        for p in productos
    ]

# API para actualizar cantidad de un producto
@router.put("/inventory/update/{product_id}")
def update_quantity(product_id: int, data: dict, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id_product == product_id).first()
    if not product:
        return {"success": False, "message": "Producto no encontrado"}

    add_qty = data.get("add_quantity", 0)
    if add_qty < 0:
        return {"success": False, "message": "Cantidad no válida"}

    # 👇 en vez de reemplazar, sumamos
    product.stock += add_qty  

    db.commit()
    db.refresh(product)

    return {"success": True, "new_quantity": product.stock}


@router.delete("/inventory/delete/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id_product == product_id).first()
    if not product:
        return {"success": False, "message": "Producto no encontrado"}
    
    db.delete(product)
    db.commit()
    return {"success": True}

