from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.config.db import Base

class   Product(Base):
    __tablename__ = "product"

    id_product = Column(Integer, primary_key=True, index=True)
    product = Column(String(100))
    shopping_price = Column(Float)
    sale_price = Column(Float)
    stock = Column(Integer)
    id_category = Column(Integer, ForeignKey('category.id_category'))
    
    
    id_shopping = Column(Integer, ForeignKey("shopping.id_shopping"))

   
    shopping = relationship("Shopping", back_populates="products")


    details = relationship("SaleDetail", back_populates="product")
    shoppingDetail = relationship("ShoppingDetail", back_populates="product")
    category = relationship("Category", back_populates="products")
    



