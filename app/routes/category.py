from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.models.category import Category
from app.models import Supplier
from app.schemas.category import CategoryCreate, CategoryOut
from app.config.db import get_db
from typing import List

router = APIRouter(prefix='/category', tags=['category'])
templates = Jinja2Templates(directory="app/templates")  # Ajusta si tu ruta real es diferente

# listar todas las categorias
@router.get("/category_list", response_model=List[CategoryOut])
def get_categorys(db: Session = Depends(get_db)):
    return db.query(Category).all()

@router.get("/proveedores")
def mostrar_proveedores(request: Request, db: Session = Depends(get_db)):
    proveedores = db.query(Supplier).all()
    return templates.TemplateResponse("proveedores.html", {
        "request": request,
        "proveedores": proveedores
    })

# listar una categoria por parametro de url
@router.get("/{id_category}", response_model=CategoryOut)
def get_category(id_category:int,db: Session = Depends(get_db)):

    category_exist = db.query(Category).filter(Category.id_category == id_category).first()

    if not category_exist:
        raise HTTPException(status_code=400, detail="no existe la categoria")

    return db.query(Category).filter(Category.id_category == id_category).first()


# crear una categoria
@router.post("/", response_model=CategoryOut)
def create_category(category_data: CategoryCreate, db:Session = Depends(get_db)):

    category_exist = db.query(Category).filter(Category.category == category_data.category).first()

    if category_exist:
        db.rollback()
        raise HTTPException(status_code=400, detail="error al crear la categoria")
    
    new_category = Category(category=category_data.category)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


# actualizar una categoria 
@router.put('/{id_category}', response_model=CategoryOut)
def update_category(id_category:int, category_data: CategoryCreate, db:Session = Depends(get_db)):
    # buscar la categoria 
    category_exist = db.query(Category).filter(Category.id_category == id_category).first()

    if not category_exist:
        raise HTTPException(status_code=400, detail="no existe la categoria la categoria")
    
    category_exist.category = category_data.category

    db.commit()
    db.refresh(category_exist)
    return category_exist


# eliminar categoria
@router.delete('/{id_category}', status_code=status.HTTP_200_OK)
def delete_category(id_category: int, db: Session = Depends(get_db)):
     
     category_exist = db.query(Category).filter(Category.id_category == id_category).first()

     if not category_exist:
        raise HTTPException(status_code=400, detail="no existe la categoria")
     
     db.delete(category_exist)
     db.commit()
     return {
        "success": True,
        "message": f"Categoría con ID {id_category} eliminada exitosamente."
    }

# Vista HTML: Mostrar proveedores
# ========================

@router.get("/supplier/search")
def buscar_proveedor(name: str, db: Session = Depends(get_db)):
    proveedor = db.query(Supplier).filter(Supplier.supplier_name == name).first()
    
    if not proveedor:
        return JSONResponse(content={"success": False}, status_code=404)

    # Lógica ficticia para simular archivos adjuntos
    archivos = [
        {"filename": "factura1.pdf", "originalName": "Factura enero"},
        {"filename": "factura2.pdf", "originalName": "Factura febrero"},
    ]

    return {
        "success": True,
        "supplier": {
            "name": proveedor.supplier_name,
            "phone": proveedor.telephone
        },
        "files": archivos
    }