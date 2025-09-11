from fastapi import FastAPI, Request, Form, APIRouter, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from sqlalchemy.orm import Session
from .models.product import Product
from .models.sale import Sale
from .models.saledetail import SaleDetail
from . import models
from .models.user import RoleEnum
from app.routes import user, product, category, sale, shopping, suppliers, ingresos, inventario, proveedor, reportes
from .routes.suppliers import router as suppliers_router
from .config.db import Base, engine, get_db, SessionLocal
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import unquote
import os
from app import utils, models

# Import User model and get_current_user dependency
from app.models.user import User
from app.models.dependencies import get_current_user
from app.utils import hash_password
from starlette.middleware.sessions import SessionMiddleware


# nuevo_usuario.password = hash_password("12345")  
app = FastAPI()
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Montar carpeta static
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/supplier/files", StaticFiles(directory="app/uploaded_files"), name="supplier_files")

# Configuración de la ruta para la página de inicio
from fastapi import Request, Depends
from fastapi.responses import RedirectResponse

@app.get("/home")
def home(request: Request, db: Session = Depends(get_db)):
    # Verificar que haya sesión activa
    user_id = request.session.get("user_id")
    role = request.session.get("role")

    if not user_id:
        # Si no hay sesión, redirige al login
        return RedirectResponse("/", status_code=303)

    # Recuperar el usuario de la base de datos
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # Si el usuario ya no existe, limpiar sesión y volver al login
        request.session.clear()
        return RedirectResponse("/", status_code=303)

    # Pasar datos al template
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "user": user,  # tendrás disponible user.username
            "role": role,  # aquí ya llega como string: "admin" o "vendedor"
            "current_year": datetime.now().year,
            "title": "Home Page"
        }
    )


# Configuración de la ruta para la página de ventas
@app.get("/ventas", response_class=HTMLResponse)
async def get_ventas(request: Request):
    return templates.TemplateResponse("ventas.html", {"request": request})

@app.get("/ventas/crear", response_class=HTMLResponse)
def create_venta(request: Request, db: Session = Depends(get_db)):
    products = db.query(Product).all() 
    return templates.TemplateResponse("ventas.html", {"request": request, "products": products})

@app.get("/productos", response_class=HTMLResponse)
async def get_productos(request: Request):
    return templates.TemplateResponse("productos.html", {"request": request}) 

@app.get("/", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not utils.verify_password(password, user.password):
        return {"error": "Usuario o contraseña incorrectos"}

    # Guardar en la sesión como string
    request.session["user_id"] = user.id
    request.session["role"] = user.role.value

    # Redirigir al home
    return RedirectResponse("/home", status_code=303)

db = SessionLocal()
usuarios = db.query(models.User).all()

for u in usuarios:
    # Si la contraseña aún no está en formato hash
    if not u.password.startswith("$2b$"):  
        u.password = utils.hash_password(u.password)

db.commit()
db.close()

# Clave secreta para firmar las cookies de sesión
# (usa algo largo y aleatorio en producción)
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

# request.session["user_id"] = user.id   # Guardar en sesión
# user_id = request.session.get("user_id")  # Recuperar de sesión


@app.get("/home")
def admin_dashboard(current_user: User = Depends(get_current_user)):
    if current_user.role != RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    return {"msg": "Bienvenido al panel de administrador"}


@app.get("/home", response_class=HTMLResponse)
def dashboard(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": current_user,
            "role": current_user.role,
            "current_year": datetime.now().year
        }
    )


@app.post("/ventas/registrar/formulario")
def crear_venta_formulario(
    fecha: str = Form(...),
    products: list[int] = Form(...),
    quantity: list[int] = Form(...),
    total_general: float = Form(...),
    db: Session = Depends(get_db)
):
    nueva_venta = Sale(datesale=fecha, totalsale=0.0)
    db.add(nueva_venta)
    db.commit()
    db.refresh(nueva_venta)

    total = 0.0

    for id_producto, cantidad in zip(products, quantity):
        producto = db.query(Product).filter(Product.id_product == id_producto).first()
        if not producto:
            raise ValueError(f"Producto con ID {id_producto} no existe")
        if producto.stock < cantidad:
            raise ValueError(f"Stock insuficiente para el producto {producto.product}")

        subtotal = producto.sale_price * cantidad
        total += subtotal

        detalle = SaleDetail(
            id_sale=nueva_venta.id_sale,
            id_product=id_producto,
            quantity=cantidad,
            subtotal=subtotal
        )
        producto.stock -= cantidad
        db.add(detalle)
        db.commit()

    nueva_venta.totalsale = total
    db.commit()

    return RedirectResponse(url="/ventas/crear", status_code=303)

# Logica para eliminar factura PDF
UPLOAD_FOLDER = "app/uploaded_files"

@app.delete("/supplier/delete-file/{supplier}/{filename}")
def delete_supplier_file(supplier: str, filename: str):
    # Decodificar espacios y caracteres especiales (ej: %20 → espacio)
    filename = unquote(filename)

    # Ruta completa del archivo
    file_path = os.path.join(UPLOAD_FOLDER, supplier, filename)

    # Verificar si existe
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return JSONResponse(content={"success": True, "message": "Factura eliminada correctamente."})
        except Exception as e:
            return JSONResponse(content={"success": False, "message": f"Error al eliminar: {str(e)}"}, status_code=500)
    else:
        return JSONResponse(content={"success": False, "message": "Archivo no encontrado."}, status_code=404)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto a ["http://localhost"] si es necesario
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear las tablas
Base.metadata.create_all(bind=engine)

# Registrar rutas
app.include_router(user.router)
app.include_router(product.router)
app.include_router(category.router)
app.include_router(sale.router)
app.include_router(shopping.router)
app.include_router(suppliers.router)
app.include_router(ingresos.router)
app.include_router(suppliers_router)
app.include_router(inventario.router)
app.include_router(proveedor.router)
app.include_router(reportes.router)


import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)






