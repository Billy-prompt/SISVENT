from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.config.db import Base

class SaleDetail(Base):
    __tablename__ = "saledetail"

    id_detail = Column(Integer, primary_key=True, index=True)
    id_sale = Column(Integer, ForeignKey('sale.id_sale'))
    id_product = Column(Integer, ForeignKey('product.id_product'))
    quantity = Column(Integer)
    subtotal = Column(Float)

    sale = relationship("Sale", back_populates="details")
    product = relationship("Product", back_populates="details")