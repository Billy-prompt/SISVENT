from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.config.db import get_db
from app.models.suppliers import Supplier
from app.models.category import Category

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")  # Asegúrate que esta ruta sea correcta

@router.get("/ingresos/productos")
def formulario_ingreso_productos(request: Request, db: Session = Depends(get_db)):
    proveedores = db.query(Supplier).all()
    categorias = db.query(Category).all()
    return templates.TemplateResponse("productos.html", {
        "request": request,
        "proveedores": proveedores,
        "categorias": categorias
    })