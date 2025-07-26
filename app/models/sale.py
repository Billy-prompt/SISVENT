from sqlalchemy import Column, Integer,Float, Date
from sqlalchemy.orm import relationship
from app.config.db import Base

class Sale(Base):
    __tablename__ = "sale"

    id_sale = Column(Integer, primary_key=True, index=True)
    datesale = Column(Date)
    totalsale = Column(Float)


    details = relationship("SaleDetail", back_populates="sale")

