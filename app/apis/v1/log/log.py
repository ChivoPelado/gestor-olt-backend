"""
APIs, para la gestión de Agentes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.schemas.log import ActionLogResponse, LoginLogResponse
from app.core.schemas.generic import IResponseBase
from app.database import get_db
from . import crud


router = APIRouter()


@router.get("/action/", response_model=IResponseBase[list[ActionLogResponse]])
async def action_log(ext_id: int = None, db_session: Session = Depends(get_db)):
    """API para la lectura de agente a partir del ID"""

    result = crud.get_action_log(db_session, ext_id)

    return IResponseBase[list[ActionLogResponse]](response=list(result))


@router.get("/login/", response_model=IResponseBase[LoginLogResponse])
async def login_log(agent_id: int, db_session: Session = Depends(get_db)):
    """API para la lectura de agente a partir del ID"""

    db_agent = crud.get_agent(db_session, agent_id=agent_id)
    if db_agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agente no encontrado")
    return IResponseBase[LoginLogResponse](response=db_agent)