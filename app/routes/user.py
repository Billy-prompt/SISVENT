from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserOut, UserCreate
from app.config.db import get_db
from typing import List


router = APIRouter(prefix='/user', tags=["Users"])


@router.get("/", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.post("/", response_model=UserOut)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
   
    # Verificar si ya existe el email
    user_exist = db.query(User).filter(User.email == user_data.email).first()
    if user_exist:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    user = User(name=user_data.name, email=user_data.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user