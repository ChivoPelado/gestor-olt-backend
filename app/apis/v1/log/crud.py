"""
CRUD para la gestión de Agentes
"""
from sqlalchemy.orm import Session
from app.core.models.system import Olt, Onu
from app.core.models.agent import Agent
from app.core.models.log import ActionLog, LoginLog


def get_action_log(db_session: Session, onu_ext_id = None) -> ActionLog:
    """Retorna Agente desde la base de datos en base al ID

    Args:
        db_session (Session): Sesión de la base de datos
        agent_id (int): ID de agente

    Returns:
        Agent: Objeto Agente desde la base de datos
    """
    result = []
    response_log = {}

    if onu_ext_id:
        response = db_session.query(ActionLog).filter(ActionLog.onu_ext_id == onu_ext_id).all()

    else:
        response = db_session.query(ActionLog).all()
    """    if olt_id and not agent_id:
        response = db_session.query(ActionLog, Olt.name, Agent.email,Onu).join(Olt, Onu).filter(Olt.id == olt_id).all()

    elif agent_id and not olt_id:
        response =  db_session.query(ActionLog, Olt.name, Agent.email, Onu).join(Agent, Onu).filter(Agent.id == agent_id).all()

    elif olt_id and agent_id:
        response =  db_session.query(ActionLog, Olt.name, Agent.email, Onu).join(Olt, Agent, Onu).filter(Agent.id == agent_id, Olt.id == olt_id).all()

    elif not olt_id and not agent_id:
        response = db_session.query(ActionLog, Olt.name, Agent.email, Onu).join(Olt, Agent, Onu).all()
    """
    for log in response:
        response_log = log.__dict__.copy()
        response_log['olt_ext_id'] = log.onu.ext_id
        response_log['onu'] = log.onu.interface
        response_log['olt_name'] = log.olt.name
        response_log['agent_email'] = log.agent.email
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