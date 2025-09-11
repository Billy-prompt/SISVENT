# app/utils.py

# Definimos los permisos de cada rol
ROLES_PERMISOS = {
    "admin": ["inventario", "ventas", "proveedores", "usuarios", "reportes", "salir"],
    "vendedor": ["ventas", "salir"]
}

def verificar_permiso(rol: str, modulo: str) -> bool:
    """
    Verifica si un rol tiene permiso para acceder a un módulo.
    """
    permisos = ROLES_PERMISOS.get(rol, [])
    return modulo in permisos

def obtener_permisos(rol: str):
    """
    Retorna la lista de módulos permitidos según el rol.
    """
    return ROLES_PERMISOS.get(rol, [])

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hashea una contraseña
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verifica una contraseña con el hash guardado en la BD
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)