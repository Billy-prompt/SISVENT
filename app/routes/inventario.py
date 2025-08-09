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
def actualizar_cantidad(product_id: int, data: dict, db: Session = Depends(get_db)):
    producto = db.query(Product).filter(Product.id_product == product_id).first()
    if not producto:
        return {"success": False, "error": "Producto no encontrado"}
    
    nueva_cantidad = data.get("quantity")
    if nueva_cantidad is not None:
        producto.stock = nueva_cantidad
        db.commit()
        return {"success": True}
    
    return {"success": False, "error": "Cantidad no válida"}

@router.delete("/inventory/delete/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id_product == product_id).first()
    if not product:
        return {"success": False, "message": "Producto no encontrado"}
    
    db.delete(product)
    db.commit()
    return {"success": True}

