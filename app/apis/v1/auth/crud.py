from typing import Callable, Iterator, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.models.agent import Agent
from app.core.utils.security import login_manager


# Obtiene agente desde la db
@login_manager.user_loader(session_provider=get_db)
def get_agent(username: str, db: Optional[Session] = None, session_provider: Callable[[], Iterator[Session]] = None) -> Optional[Agent]:

    if db is None and session_provider is None:
        raise ValueError("No existe una sesión o conexión de base de datos activa")

    if db is None:
        db = next(session_provider())

    agent_db = db.query(Agent).where(Agent.email == username).first()
    return agent_db
