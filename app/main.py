from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.core.config import settings

from app.apis.base import api_router

def include_router(app):
    app.include_router(api_router)


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

    # Invoca Rutas
    include_router(_app)
    # Invoca creación de tablas.
    create_tables()

    # Retorna instancia de la app
    return _app

# Inicialización de la app
app = get_application()


