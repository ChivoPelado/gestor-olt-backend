from app.apis.v1.agent import agent
from app.apis.v1.auth import auth
from app.apis.v1.location import location
from app.apis.v1.system import olt, onu, general
from app.apis.v1.log import log
from fastapi import APIRouter

api_router = APIRouter()

# Rutas para módulo de gestión de OLTs
api_router.include_router(olt.router, prefix="/api/v1/system/olt", tags=["OLTs"])

# Rutas para módulo de gestión de ONUs
api_router.include_router(onu.router, prefix="/api/v1/system/onu", tags=["ONUs"])

# Rutas para módulo de Agente
api_router.include_router(agent.router, prefix="/api/v1/agent", tags=["Agentes"])

# Rutas para módulo de Autenticación
api_router.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticación"])

# Rutas para módulo de Parametrizaciones
api_router.include_router(general.router, prefix="/api/v1/system", tags=["Parametrizaciones"])

# Rutas para módulo de Localización
api_router.include_router(location.router, prefix="/api/v1/location", tags=["Localización"])

# Rutas para módulo de Localización
api_router.include_router(log.router, prefix="/api/v1/log", tags=["Registros"])

