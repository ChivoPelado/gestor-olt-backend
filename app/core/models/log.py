from app.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func


class ActionLog(Base):
    __tablename__ = "action_log"

    id = Column(Integer, primary_key=True, index=True)
    olt_id = Column(Integer, ForeignKey("olt.id"))
    onu =Column(String)
    agent_id = Column(Integer, ForeignKey("agent.id"))
    action = Column(String)
    ip_address = Column(String)
    created_at = Column(DateTime, server_default=func.now())

class LoginLog(Base):
    __tablename__ = "login_log"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agent.id"))
    action = Column(String)
    ip_address = Column(String)
    created_at = Column(DateTime, server_default=func.now())