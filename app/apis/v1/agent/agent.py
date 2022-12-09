"""
APIs, para la gestión de Agentes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.schemas.agent import AgentCreate, AgentResponse, PaginatedAgentListInfo
from app.core.schemas.generic import IResponseBase
from app.database import get_db
from . import crud
# from . import exceptions

router = APIRouter()


@router.post("/",  response_model=IResponseBase[AgentResponse])
async def create_agent(agent: AgentCreate, db_session: Session = Depends(get_db)):
    """
    Agrega una Agente al sistema:

    - **name**: Nombres completos de Agente
    - **emails**: Dirección de correo electrónico (debe ser único)
    - **password**: Contraseña para la cuenta de Agente
    - **is_active**: Determinar si la cuenta está activa (Si por defecto)
    - **role**: Rol de agente
    - **scopes**: Los alcances (permisos) de Angente (Uso APIs.)
    \f
    :param agent: Objeto Agente.
    :param db_session: DataBase Session.
    """

    db_agent = crud.get_agent_by_email(db_session, agent.email)
    if db_agent:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Agente existe")
    new_agent = crud.create_agent(db_session, agent=agent)
    return IResponseBase[AgentResponse](response=new_agent)


@router.get("/{agent_id}", response_model=IResponseBase[AgentResponse])
async def read_agent(agent_id: int, db_session: Session = Depends(get_db)):
    """API para la lectura de agente a partir del ID"""

    db_agent = crud.get_agent(db_session, agent_id=agent_id)
    if db_agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agente no encontrado")
    return IResponseBase[AgentResponse](response=db_agent)


@router.get("/get_agents/", response_model=IResponseBase[PaginatedAgentListInfo])
async def list_agents(skip: int = 0, limit: int = 100, db_session: Session = Depends(get_db)):
    """API para la lectura de  todos los agentes"""

    db_agents = crud.get_agents(db_session, skip=skip, limit=limit)
    response = {"skip": skip, "limit": limit, "data": db_agents}
    return IResponseBase[PaginatedAgentListInfo](response=response)


@router.put("/{agent_id}", response_model=IResponseBase[AgentResponse])
async def edit_agent(agent_id: int, new_agent: AgentCreate, db_session: Session = Depends(get_db)):
    """API para la edición de  agente por ID"""

    agent_db = crud.get_agent(db_session, agent_id=agent_id)
    if agent_db is None:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    updated_agent = crud.update_agent(db_session, current_agent=agent_db, new_agent=new_agent)
    return IResponseBase[AgentResponse](response=updated_agent)


# Elimina Agente
@router.delete("/{agent_id}", response_model=IResponseBase[str])
async def delete_agent(agent_id: int, db_session: Session = Depends(get_db)):
    """API para la eliminación de agente por ID"""

    agent_db = crud.get_agent(db_session, agent_id=agent_id)
    if agent_db is None:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    # if self.current_agent.role != AgentRole.ADMIN.value:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Acceso denegado por rol de usuario"
    # )
    # else:
    crud.delete_agent(db_session, agent_db)
    return  IResponseBase[str](response="Agente eliminado satisfactoriamente")


# Desabilita Agente (is_active = False)
@router.post("/{agent_id}/disable/", response_model=IResponseBase[str])
async def enable_agent(agent_id: int, db: Session = Depends(get_db)):
    db_agent = crud.get_agent(db, agent_id=agent_id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    if db_agent.is_active:
        crud.deactivate_agent(db, db_agent)
    else:
        raise HTTPException(status_code=422, detail="Agente se encuentra desactivado")
    return  IResponseBase[str](response="Agente desactivado satisfactoriamente")
    

# Habiliata Agente (is_active = True)
@router.post("/{agent_id}/enable/", response_model=IResponseBase[str])
async def disable_agent(agent_id: int, db: Session = Depends(get_db)):
    db_agent = crud.get_agent(db, agent_id=agent_id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    if not db_agent.is_active:
        crud.activate_agent(db, db_agent)
    else:
        raise HTTPException(status_code=422, detail="Agente se encuentra activado")
    return  IResponseBase[str](response="Agente activado satisfactoriamente")
