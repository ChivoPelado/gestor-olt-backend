from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine

from app.core.config import settings

# Crear tablas en la db
def create_tables():           
	Base.metadata.create_all(bind=engine)

# Parametros de inicialización de la app
def get_application():
    
    # Parámetros base
    _app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.PROJECT_VER
    )

    # Configuración de midleware
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app

# Inicialización de la app
app = get_application()
