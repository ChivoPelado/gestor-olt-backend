from app.apis.v1.agent import agent
from app.apis.v1.auth import auth
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(agent.router, prefix="/api/v1", tags=["Agentes"])
api_router.include_router(auth.router, prefix="/api/v1", tags=["Autenticación"])