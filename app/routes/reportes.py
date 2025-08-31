from fastapi import FastAPI, Request, Query, Depends
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date
from app.config.db import SessionLocal
from app.schemas import sale, saledetail, product
from app.models import Sale as SaleModel, SaleDetail as SaleDetailModel, Product as ProductModel
import calendar
from typing import Optional


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# --- Dependencia de DB ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Reportes ---
@router.get("/reportes", response_class=HTMLResponse)
def reportes_view(
    request: Request,
    tipo_reporte: str | None = Query(default=None),
    fecha: date | None = Query(default=None),
    db: Session = Depends(get_db)
):
    reporte = None

    if tipo_reporte == "dia" and fecha:
        # Total del día
        total = (
            db.query(func.sum(SaleModel.totalsale))
            .filter(SaleModel.datesale == fecha)
            .scalar()
        )

        # Detalle del día por producto
        detalles = (
            db.query(
                SaleModel.datesale.label("fecha"),
                ProductModel.product.label("producto"),
                SaleDetailModel.quantity.label("cantidad"),
                (SaleDetailModel.quantity * SaleDetailModel.subtotal).label("valor")
            )
            .join(SaleDetailModel, SaleModel.id_sale == SaleDetailModel.id_sale)
            .join(ProductModel, ProductModel.id_product == SaleDetailModel.id_product)
            .filter(SaleModel.datesale == fecha)
            .all()
        )

        reporte = {
            "titulo": f"📅 Ventas del día {fecha}",
            "contenido": f"Total vendido: ${total:,.0f}" if total else "Sin ventas registradas",
            "detalles": detalles
        }

    elif tipo_reporte == "mes" and fecha:
        mes = fecha.month
        anio = fecha.year
        ultimo_dia = calendar.monthrange(anio, mes)[1]

        # Total del mes
        total = (
            db.query(func.sum(SaleModel.totalsale))
            .filter(SaleModel.datesale.between(date(anio, mes, 1), date(anio, mes, ultimo_dia)))
            .scalar()
        )

        # Detalle del mes por producto
        detalles = (
            db.query(
                SaleModel.datesale.label("fecha"),
                ProductModel.product.label("producto"),
                SaleDetailModel.quantity.label("cantidad"),
                (SaleDetailModel.quantity * SaleDetailModel.subtotal).label("valor")
            )
            .join(SaleDetailModel, SaleModel.id_sale == SaleDetailModel.id_sale)
            .join(ProductModel, ProductModel.id_product == SaleDetailModel.id_product)
            .filter(SaleModel.datesale.between(date(anio, mes, 1), date(anio, mes, ultimo_dia)))
            .all()
        )

        reporte = {
            "titulo": f"📆 Ventas del mes {mes}/{anio}",
            "contenido": f"Total vendido: ${total:,.0f}" if total else "Sin ventas registradas",
            "detalles": detalles
        }

    elif tipo_reporte == "menos_vendido":
        productos = (
            db.query(ProductModel.product, func.sum(SaleDetailModel.quantity).label("cantidad"), ProductModel.stock)
            .join(SaleDetailModel, ProductModel.id_product == SaleDetailModel.id_product)
            .group_by(ProductModel.product, ProductModel.stock)
            .order_by("cantidad")
            .limit(5)
            .all()
        )
        if productos:
            reporte = {
                "titulo": "⬇️ Top 5 productos menos vendidos",
                "productos": productos  # 🔹 enviamos lista al template
            }
        else:
            reporte = {"titulo": "⬇️ Top 5 productos menos vendidos", "productos": []}

    elif tipo_reporte == "mas_vendido":
        productos = (
            db.query(ProductModel.product, func.sum(SaleDetailModel.quantity).label("cantidad"), ProductModel.stock)
            .join(SaleDetailModel, ProductModel.id_product == SaleDetailModel.id_product)
            .group_by(ProductModel.product, ProductModel.stock)
            .order_by(desc("cantidad"))
            .limit(5)
            .all()
        )
        if productos:
            reporte = {
                "titulo": "🔥 Top 5 productos más vendidos",
                "productos": productos  # 🔹 enviamos lista al template
            }
        else:
            reporte = {"titulo": "🔥 Top 5 productos más vendidos", "productos": []}

    return templates.TemplateResponse("reportes.html", {
        "request": request,
        "reporte": reporte
    })