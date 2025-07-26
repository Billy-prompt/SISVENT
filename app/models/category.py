from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config.db import Base

class Category(Base):
    __tablename__ = "category"

    id_category = Column(Integer, primary_key=True, index=True)
    category = Column(String(255), unique=True, index=True)


    products = relationship("Product", back_populates="category")
