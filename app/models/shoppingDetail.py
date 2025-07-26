from sqlalchemy import Column, Integer, String, ForeignKey,Float
from sqlalchemy.orm import relationship
from app.config.db import Base

class ShoppingDetail(Base): 
    __tablename__ = "shoppingDetail"
    id_shopping_detail = Column(Integer, primary_key=True, index=True)
    id_shopping = Column(Integer, ForeignKey('shopping.id_shopping'))
    id_product = Column(Integer, ForeignKey('product.id_product'))
    quantity = Column(Integer)
    subtotal = Column(Float)

    shopping = relationship("Shopping", back_populates="details")
    product = relationship("Product", back_populates="shoppingDetail")
