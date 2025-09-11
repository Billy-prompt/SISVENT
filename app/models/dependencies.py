from fastapi import Depends, HTTPException
from app.models.user import User, RoleEnum

# Simulación de "usuario actual"
FAKE_USER = User(id=1, username="juan", role=RoleEnum.vendedor)

def get_current_user():
    if not FAKE_USER:
        raise HTTPException(status_code=401, detail="No autenticado")
    return FAKE_USER