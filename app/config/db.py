import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Si estás ejecutando localmente, carga el .env
if os.getenv("RENDER") != "true":
    from dotenv import load_dotenv
    load_dotenv()

# Intenta usar la DATABASE_URL completa (Render la define)
DATABASE_URL = os.getenv("DATABASE_URL")

# O si estás localmente, construye la URL desde partes
if not DATABASE_URL:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    if not all([DB_USER, DB_PASSWORD is not None, DB_HOST, DB_PORT, DB_NAME]):
        raise ValueError("Faltan variables de entorno necesarias.")

    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Verifica que la URL esté bien definida
if not DATABASE_URL:
    raise ValueError("No se pudo definir DATABASE_URL. Verifica tus variables de entorno.")

# Crear motor de conexión
engine = create_engine(DATABASE_URL)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Función para obtener la sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
