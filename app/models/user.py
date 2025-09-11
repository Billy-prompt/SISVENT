from sqlalchemy import Column, Integer, String, Enum
import enum
from app.config.db import Base

class RoleEnum(str, enum.Enum):
    admin = "admin"
    vendedor = "vendedor"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100))
    password = Column(String(100))
    role = Column(Enum(RoleEnum), default=RoleEnum.vendedor, nullable=False)