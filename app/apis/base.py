from app.apis.v1.agent import agent
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(agent.router, prefix="/api/v1", tags=["Agentes"])
