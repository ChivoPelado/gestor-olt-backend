"""
CRUD para la gestión de Agentes
"""
from typing import List
from sqlalchemy.orm import Session
from app.core.utils.security import Hasher
from app.core.models.agent import Agent


def get_agent(db_session: Session, agent_id: int) -> Agent:
    """Retorna Agente desde la base de datos en base al ID

    Args:
        db_session (Session): Sesión de la base de datos
        agent_id (int): ID de agente

    Returns:
        Agent: Objeto Agente desde la base de datos
    """

    return db_session.query(Agent).filter(Agent.id == agent_id).first()


def get_agent_by_email(db_session: Session, email: str) -> Agent:
    """Retorna Agente desde la base de datos en base al email de agente

    Args:
        db_session (Session): Sesión de la base de datos
        email (str): Dirección email registrada de agente

    Returns:
        Agent: Objeto Agente desde la base de datos
    """

    return db_session.query(Agent).filter(Agent.email == email).first()


# Devuelve todos los agentes
def get_agents(db_session: Session, skip: int = 0, limit: int = 100) -> List[Agent]:
    """Retorna todos los agentes registrados desde la base de datos

    Args:
        db_session (Session): Sesión de la base de datos
        skip (int, optional): Saltos de páginas. Defaults to 0.
        limit (int, optional): Cantidad máxima de resultados a devolver. Defaults to 100.

    Returns:
        List[Agent]: Lista de Agentes registrados en la base de datos
    """

    return db_session.query(Agent).all()



def create_agent(db_session: Session, agent: Agent) -> Agent:
    """Gestión de creación de un nuevo agente en la base de datos

    Args:
        db_session (Session): Sesión de la base de datos
        agent (Agent): Objeto Agente

    Returns:
        Agent: Objeto Agente desde la base de datos
    """

    hash_password = Hasher.hash_password(agent.hashed_password)
    db_agent = Agent(
        name = agent.name,
        email = agent.email,
        hashed_password = hash_password,
        is_active = agent.is_active,
        role = agent.role.value,
        scopes = agent.scopes
    )
    db_session.add(db_agent)
    db_session.commit()
    db_session.refresh(db_agent)
    return db_agent


# Revisar proceso....
def delete_agent(db_session: Session, agent: Agent) -> None:
    """Elimina un agente desde un objeto Agente entregado

    Args:
        db_session (Session): Sesión de la base de datos
        agent (Agent): Objeto Agente
    """
    db_agent = get_agent(db_session, agent.id)
    db_session.delete(db_agent)
    db_session.commit()


def update_agent(db_session: Session, current_agent: Agent, new_agent: Agent) -> Agent:
    """Actualiza un Agente desde un Objeto agente provisto

    Args:
        db_session (Session): Sesión de la base de datos
        current_agent (Agent): Objeto Agente a editar
        new_agent (Agent): Objeto Agente con los acmbios a aplicar

    Returns:
        Agent: Agente editado
    """

    current_agent.email = new_agent.email
    current_agent.name = new_agent.name
    current_agent.hashed_password = Hasher.hash_password(new_agent.hashed_password)
    current_agent.is_active = new_agent.is_active
    current_agent.role = new_agent.role
    current_agent.scopes = new_agent.scopes
    db_session.commit()
    db_session.refresh(current_agent)
    return current_agent



def activate_agent(db_session: Session, agent: Agent) -> None:
    """Activa a un agente desactivado

    Args:
        db_session (Session): Sesión de la base de datos
        agent (Agent): Objeto Agente
    """

    db_agent = db_agent = get_agent(db_session, agent.id)
    db_agent.is_active = True
    db_session.commit()
    db_session.refresh(db_agent)


def deactivate_agent(db_session: Session, agent: Agent):
    """Desactiva a un agente activo

    Args:
        db_session (Session): Sesión de la base de datos
        agent (Agent): Objeto Agente
    """

    db_agent = db_agent = get_agent(db_session, agent.id)
    db_agent.is_active = False
    db_session.commit()
    db_session.refresh(db_agent)
