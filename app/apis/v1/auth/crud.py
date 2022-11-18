from typing import Callable, Iterator, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.models.agent import Agent
from app.core.utils.security import login_manager


# Obtiene agente desde la db
@login_manager.user_loader(session_provider=get_db)
def get_agent(username: str, db: Optional[Session] = None, session_provider: Callable[[], Iterator[Session]] = None) -> Optional[Agent]:
    print("IN GET AGENT!!!!")
    if db is None and session_provider is None:
        print("DB ans SESSION IS NONE!!!!")
        raise ValueError("db and session none")

    if db is None:
        print("DB IS NONE!!!!")
        db = next(session_provider())

    agent_db = db.query(Agent).where(Agent.email == username).first()
    print(f"AGENT IS:::::::{agent_db}")
    return agent_db
