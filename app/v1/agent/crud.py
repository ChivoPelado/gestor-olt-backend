from typing import List
from sqlalchemy.orm import Session
from app.core.utils.hashing import Hasher
from app.core.models.agent import Agent


# Devuelve agente desde el id
def get_agent(db: Session, agent_id: int) -> Agent:
    return db.query(Agent).filter(Agent.id == agent_id).first()


# Devuelve agente desde el email
def get_agent_by_email(db: Session, email: str) -> Agent:
    return db.query(Agent).filter(Agent.email == email).first()


# Devuelve todos los agentes
def get_agents(db: Session, skip: int = 0, limit: int = 100) -> List[Agent]:
    return db.query(Agent).offset(skip).limit(limit).all()
    

# Crea un nuevo agente
def create_agent(db: Session, agent: Agent) -> Agent:
    hash_password = Hasher.get_password_hash(agent.hashed_password)    
    db_agent = Agent(
        name = agent.name, 
        email = agent.email,
        hashed_password = hash_password,
        is_active = agent.is_active,
        role = agent.role.value,
        scopes = agent.scopes  
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent) 
    return db_agent


# Elimina agente desde el id
def delete_agent(db: Session, agent: Agent):
    db_agent = get_agent(db, agent.id)
    db.delete(db_agent)
    db.commit()
    

# Actualiza agente dese el id
def update_agent(db: Session, currentAgent: Agent, newAgent: Agent) -> Agent:

    currentAgent.email = newAgent.email
    currentAgent.name = newAgent.name
    currentAgent.hashed_password = newAgent.hashed_password
    currentAgent.is_active = newAgent.is_active
    currentAgent.role = newAgent.role
    db.commit()
    db.refresh(currentAgent)
    return currentAgent


# Activa un agente
def activate_agent(db: Session, agent: Agent):
    db_agent = db_agent = get_agent(db, agent.id)
    db_agent.is_active = True
    db.commit()
    db.refresh(db_agent)
    
    
# Desactiva un agente   
def deactivate_agent(db: Session, agent: Agent):
    db_agent = db_agent = get_agent(db, agent.id)
    db_agent.is_active = False
    db.commit()
    db.refresh(db_agent)
