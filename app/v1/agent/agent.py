from fastapi import APIRouter, Depends, Security, HTTPException, status
from sqlalchemy.orm import Session
from app.core.schemas.agent import AgentCreate, AgentResponse, PaginatedAgentListInfo, AgentAuth, AgentRole
from app.core.schemas.generic import IResponseBase
from app.database import get_db
from typing import List
from . import crud
from . import exceptions

router = APIRouter()
    
# Creación de Agente
@router.post("/agent/", response_model=IResponseBase[AgentResponse])
async def create_agent(self, agent: AgentCreate):  
    db_agent = crud.get_agent_by_email(self.db, agent.email)
    if db_agent:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Agente existe")
    new_agent = crud.create_agent(self.db, agent=agent)
    return IResponseBase[List[AgentResponse]](response=new_agent)


# Lectura de Agente por ID
@router.get("/agent/{id}", response_model=IResponseBase[List[AgentResponse]])
async def read_agent(self, id: int):
    db_agent = crud.get_agent(self.db, agent_id=id)
    if db_agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agente no encontrado")
    return IResponseBase[List[AgentResponse]](response=db_agent)


# Lista todos los Agentes
@router.get("/agents/", response_model=IResponseBase[List[PaginatedAgentListInfo]])
async def list_agents(self, skip: int = 0, limit: int = 100):
    db_agents = crud.get_agents(self.db, skip=skip, limit=limit)
    response = {"skip": skip, "limit": limit, "data": db_agents}
    return IResponseBase[List[AgentResponse]](response=response)


# Edita agente
@router.put("/agent/{id}", response_model=IResponseBase[AgentResponse])
async def edit_agent(self, id: int, newAgent: AgentCreate):
    agent_db = crud.get_agent(self.db, agent_id=id)
    if agent_db is None:
        raise exceptions.AgentNotFoundException
    updated_agent = crud.update_agent(self.db, currentAgent=agent_db, newAgent=newAgent)
    return IResponseBase[List[AgentResponse]](response=updated_agent)


# Elimina Agente
@router.delete("/agent/{id}", response_model=IResponseBase[str])
async def delete_agent(self, id: int):
    agent_db = crud.get_agent(self.db, agent_id=id)
    if agent_db is None:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    if self.current_agent.role != AgentRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acceso denegado por rol de usuario"
    ) 
    else:
        crud.delete_agent(self.db, agent_db)
    return  IResponseBase[str](response="Agente eliminado satisfactoriamente")


# Desabilita Agente (is_active = False)
@router.post("/agent/{id}/disable/", response_model=IResponseBase[str])
async def enable_agent(self, id: int):
    db_agent = crud.get_agent(self.db, agent_id=id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    if db_agent.is_active:
        crud.deactivate_agent(self.db, db_agent)
    else:
        raise HTTPException(status_code=422, detail="Agente se encuentra desactivado")
    return  IResponseBase[str](response="Agente desactivado satisfactoriamente")
    

# Habiliata Agente (is_active = True)
@router.post("/agent/{id}/enable/", response_model=IResponseBase[str])
async def disable_agent(self, id: int):
    db_agent = crud.get_agent(self.db, agent_id=id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    if not db_agent.is_active:
        crud.activate_agent(self.db, db_agent)
    else:
        raise HTTPException(status_code=422, detail="Agente se encuentra activado")
    return  IResponseBase[str](response="Agente activado satisfactoriamente")