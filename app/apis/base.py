from app.apis.v1.agent import agent
from app.apis.v1.auth import auth
from app.apis.v1.system import olt, onu, general
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(agent.router, prefix="/api/v1/agent", tags=["Agentes"])
api_router.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticación"])
api_router.include_router(general.router, prefix="/api/v1/system", tags=["Parametrizaciones"])
api_router.include_router(olt.router, prefix="/api/v1/system/olt", tags=["OLTs"])
api_router.include_router(onu.router, prefix="/api/v1/system/onu", tags=["ONUs"])
