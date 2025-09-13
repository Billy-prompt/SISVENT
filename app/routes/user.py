from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserOut, UserCreate
from app.config.db import get_db
from typing import List
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.config.db import get_db
from app import models, utils

templates = Jinja2Templates(directory="app/templates")


router = APIRouter()

# Listar usuarios

@router.get("/", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# Crear usuario

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

# Rutas para manejar usuarios desde una interfaz web

@router.get("/usuarios")
def listar_usuarios(request: Request, db: Session = Depends(get_db)):
    usuarios = db.query(models.User).all()
    return templates.TemplateResponse("usuarios.html", {"request": request, "usuarios": usuarios})

# Crear usuario desde formulario web

@router.post("/usuarios/crear")
def crear_usuario(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db)
):
    hashed_password = utils.hash_password(password)
    nuevo_usuario = models.User(username=username, password=hashed_password, role=models.RoleEnum(role))
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return RedirectResponse(url="/usuarios", status_code=303)

# Eliminar usuario desde formulario web

@router.post("/usuarios/eliminar/{user_id}")
def eliminar_usuario(user_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.User).filter(models.User.id == user_id).first()
    if usuario:
        db.delete(usuario)
        db.commit()
    return RedirectResponse(url="/usuarios", status_code=303)