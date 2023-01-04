"""
CRUD para la gestión de Agentes
"""
from sqlalchemy.orm import Session
from app.core.models.system import Olt
from app.core.models.agent import Agent
from app.core.models.log import ActionLog, LoginLog


def get_action_log(db_session: Session, olt_id: int = None, agent_id: int = None) -> ActionLog:
    """Retorna Agente desde la base de datos en base al ID

    Args:
        db_session (Session): Sesión de la base de datos
        agent_id (int): ID de agente

    Returns:
        Agent: Objeto Agente desde la base de datos
    """
    result = []
    response_log = {}

    if olt_id and not agent_id:
        response = db_session.query(ActionLog, Olt.name, Agent.email).join(Olt).filter(Olt.id == olt_id).all()

    elif agent_id and not olt_id:
        response =  db_session.query(ActionLog, Olt.name, Agent.email).join(Agent).filter(Agent.id == agent_id).all()

    elif olt_id and agent_id:
        response =  db_session.query(ActionLog, Olt.name, Agent.email).join(Olt, Agent).filter(Agent.id == agent_id, Olt.id == olt_id).all()

    elif not olt_id and not agent_id:
        response = db_session.query(ActionLog, Olt.name, Agent.email).join(Olt, Agent).all()

    for log, olt, agent in response:
        response_log = log.__dict__.copy()
        response_log['olt_name'] = olt
        response_log['agent_email'] = agent
        result.append(response_log)

    return result



def get_login_log(db_session: Session, agent_id: int) -> Agent:
    """Retorna Agente desde la base de datos en base al ID

    Args:
        db_session (Session): Sesión de la base de datos
        agent_id (int): ID de agente

    Returns:
        Agent: Objeto Agente desde la base de datos
    """

    return db_session.query(Agent).filter(Agent.id == agent_id).first()