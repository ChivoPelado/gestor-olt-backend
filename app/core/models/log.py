from app.database import Base
from app.core.models.system import Olt, Onu
from app.core.models.agent import Agent
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

class ActionLog(Base):
    __tablename__ = "action_log"

    id = Column(Integer, primary_key=True, index=True)
    olt_id = Column(Integer, ForeignKey("olt.id"))
    onu_ext_id = Column(Integer, ForeignKey("onu.ext_id"))
    agent_id = Column(Integer, ForeignKey("agent.id"))
    action = Column(String)
    ip_address = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    olt = relationship("Olt", backref="action_log") 
    onu = relationship("Onu", backref="action_log") 
    agent = relationship("Agent", backref="action_log") 

class LoginLog(Base):
    __tablename__ = "login_log"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agent.id"))
    action = Column(String)
    ip_address = Column(String)
    created_at = Column(DateTime, server_default=func.now())