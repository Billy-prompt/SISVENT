from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, File, UploadFile, Query
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from app.models import Supplier, Shopping, ShoppingDetail, Product
from app.models.category import Category
from app.schemas.suppliers import SupplierCreate, SupplierOut
from app.config.db import get_db
import os
import shutil
from uuid import uuid4
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from urllib.parse import unquote

UPLOAD_FOLDER = "app/uploaded_files"
app = FastAPI()
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")  # Ajusta si tu ruta real es diferente
app.mount("/supplier/files", StaticFiles(directory="app/uploaded_files"), name="supplier_files")
# router = APIRouter(prefix="/ingresos")

# =========================
# Obtener lista de proveedores
# =========================
# @router.get('/', response_model=List[SupplierOut])
# def get_suppliers(db: Session = Depends(get_db)):
#     return db.query(Supplier).all()

@router.get("/supplier/search")
def buscar_proveedor(name: str, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.supplier_name == name).first()
    if not supplier:
        return {"success": False, "message": "Proveedor no encontrado."}

    supplier_path = os.path.join(UPLOAD_FOLDER, name)
    files = []

    if os.path.exists(supplier_path):
        for filename in os.listdir(supplier_path):
            file_path = os.path.join(supplier_path, filename)
            if os.path.isfile(file_path):
                files.append({
                    "filename": filename,
                    "originalName": filename  # puedes usar otro nombre si lo guardas
                })

    return {
        "success": True,
        "supplier": {
            "name": supplier.supplier_name,
            "phone": supplier.telephone
        },
        "files": files
    }  
# Logica para mostrar factura PDF

@router.get("/supplier/files/{supplier}/{filename}")
def obtener_factura(supplier: str, filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, supplier, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(file_path, media_type="application/pdf", filename=filename)



# =========================
# Crear proveedor
# =========================

@router.post("/ingresos/supplier/create")
async def crear_supplier(
    supplierName: str = Form(...),
    supplierPhone: str = Form(...),
    supplierDocument: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    # Crear proveedor
    nuevo_proveedor = Supplier(supplier_name=supplierName, telephone=supplierPhone)
    db.add(nuevo_proveedor)
    db.commit()
    db.refresh(nuevo_proveedor)  # Ahora ya tiene id_supplier

    if supplierDocument and supplierDocument.filename:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        extension = os.path.splitext(supplierDocument.filename)[1] or ".pdf"
        nombre_archivo = f"{uuid4().hex}_{nuevo_proveedor.id_supplier}{extension}"
        ruta_archivo = os.path.join(UPLOAD_FOLDER, nombre_archivo)

        with open(ruta_archivo, "wb") as buffer:
            shutil.copyfileobj(supplierDocument.file, buffer)

        # Guardar nombre del archivo en el proveedor
        nuevo_proveedor.document_filename = nombre_archivo
        db.commit()


    return RedirectResponse(url="/category/proveedores", status_code=303)

# =========================
# Actualizar proveedor
# =========================
@router.put('/{supplier_id}', response_model=SupplierOut)
def update_supplier(supplier_id: int, supplier_data: SupplierCreate, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.id_supplier == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado")

    supplier.supplier_name = supplier_data.supplier_name
    supplier.telephone = supplier_data.telephone

    db.commit()
    db.refresh(supplier)
    return supplier

@router.put("/supplier/update")
def actualizar_proveedor(data: dict, db: Session = Depends(get_db)):
    original_name = data.get("original_name")
    new_name = data.get("new_name")
    new_phone = data.get("new_phone")

    proveedor = db.query(Supplier).filter(Supplier.supplier_name == original_name).first()
    if not proveedor:
        return {"success": False, "message": "Proveedor no encontrado"}

    proveedor.supplier_name = new_name
    proveedor.telephone = new_phone
    db.commit()
    return {"success": True}

# =========================
# Eliminar proveedor
# =========================
@router.delete('/{supplier_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.id_supplier == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado")

    db.delete(supplier)
    db.commit()
    return None

# =========================
# Mostrar formulario ingreso
# =========================
@router.get("/formulario")
def mostrar_formulario_ingreso(request: Request, db: Session = Depends(get_db)):
    proveedores = db.query(Supplier).all()
    categorias = db.query(Category).all()
    return templates.TemplateResponse("productos.html", {  # <- Aquí cambió el nombre
        "request": request,
        "proveedores": proveedores,
        "categorias": categorias
    })

@router.get("/categorias", response_model=list[str])
def obtener_categorias(db: Session = Depends(get_db)):
    categorias = db.query(Category).all()
    return [cat.category for cat in categorias]

# =========================
# Registrar ingreso POST
# =========================
@router.post("/registrar")
def registrar_ingreso(
    fecha_ingreso: str = Form(...),
    proveedor_nombre: str = Form(...),
    productos: list[str] = Form(...),
    cantidades: list[int] = Form(...),
    precios: list[float] = Form(...),
    precio_venta: list[float] = Form(...),
    categorias: list[str] = Form(...),
    db: Session = Depends(get_db)
):
    proveedor = db.query(Supplier).filter(Supplier.supplier_name == proveedor_nombre).first()
    if not proveedor:
        proveedor = Supplier(supplier_name=proveedor_nombre)
        db.add(proveedor)
        db.commit()
        db.refresh(proveedor)

    total_shopping = 0.0
    nuevo_ingreso = Shopping(
        shopping_date=fecha_ingreso,
        id_supplier=proveedor.id_supplier,
        total_shopping=0.0
    )
    db.add(nuevo_ingreso)
    db.commit()
    db.refresh(nuevo_ingreso)

    for nombre, cantidad, precio_compra, precio_venta_unitario, nombre_categoria in zip(productos, cantidades, precios, precio_venta, categorias):
        total_shopping += cantidad * precio_compra

        categoria = db.query(Category).filter(Category.category == nombre_categoria).first()
        if not categoria:
            categoria = Category(category=nombre_categoria)
            db.add(categoria)
            db.commit()
            db.refresh(categoria)

        producto = Product(
            product=nombre,
            stock=cantidad,
            shopping_price=precio_compra,
            sale_price=precio_venta_unitario,
            id_shopping=nuevo_ingreso.id_shopping,
            id_category=categoria.id_category
        )
        db.add(producto)
        db.commit()
        db.refresh(producto)

        detalle = ShoppingDetail(
            id_shopping=nuevo_ingreso.id_shopping,
            id_product=producto.id_product,
            quantity=cantidad,
            subtotal=precio_compra * cantidad
        )
        db.add(detalle)

    nuevo_ingreso.total_shopping = total_shopping
    db.commit()

    return RedirectResponse(url="/formulario", status_code=303)

# =========================


@router.post("/ingresos/supplier/upload/{supplier_name}")
def subir_factura(supplier_name: str, factura: UploadFile = File(...), db: Session = Depends(get_db)):
    # Validar tipo de archivo
    if factura.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")
    
    contents = factura.file.read()
    if len(contents) > 3 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="El archivo excede el tamaño máximo permitido (3 MB).")
    
    factura.file.seek(0)

    proveedor = db.query(Supplier).filter(Supplier.supplier_name == supplier_name).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado.")

    # Crear carpeta del proveedor si no existe
    proveedor_folder = os.path.join(UPLOAD_FOLDER, supplier_name)
    os.makedirs(proveedor_folder, exist_ok=True)

    # Guardar archivo dentro de la carpeta del proveedor
    safe_filename = f"{factura.filename}"  # puedes agregar timestamp si deseas
    filepath = os.path.join(proveedor_folder, safe_filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(factura.file, buffer)

    return JSONResponse(content={"success": True, "message": "Factura subida correctamente."})

# cargar lista de proveedores

@router.get("/supplier/list")
def listar_proveedores(db: Session = Depends(get_db)):
    proveedores = db.query(Supplier).all()
    return [{"name": p.supplier_name} for p in proveedores]

