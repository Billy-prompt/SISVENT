from fastapi import FastAPI, Request, Form, APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from sqlalchemy.orm import Session
from .models.product import Product
from .models.sale import Sale
from .models.saledetail import SaleDetail
from .routes import user,product,category, sale, shopping, suppliers, ingresos, inventario, proveedor
from .routes.suppliers import router as suppliers_router
from .config.db import Base, engine, SessionLocal, get_db
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

# Montar carpeta static

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/supplier/files", StaticFiles(directory="app/uploaded_files"), name="supplier_files")

# Configuración de la ruta para la página de inicio

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "current_year": datetime.now().year, "title": "Home Page"})

# Configuración de la ruta para la página de ventas

@app.get("/ventas", response_class=HTMLResponse)
async def get_ventas(request: Request):
    return templates.TemplateResponse("ventas.html", {"request": request})

@app.get("/ventas/crear", response_class=HTMLResponse)
def create_venta(request: Request):
    db = SessionLocal()
    products = db.query(Product).all() 
    return templates.TemplateResponse("ventas.html", {"request": request, "products": products})

@app.get("/productos", response_class=HTMLResponse)
async def get_productos(request: Request):
    return templates.TemplateResponse("productos.html", {"request": request}) 


@app.get("/", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/", response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "1234":
        print("Inicio de sesión exitoso")
        return RedirectResponse(url="/home", status_code=303)
    else:
        print("Inicio de sesión fallido")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Credenciales incorrectas"
        })
    


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto a ["http://localhost"] si es necesario
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear las tablas
Base.metadata.create_all(bind=engine)

#registrar rutas

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

import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)






