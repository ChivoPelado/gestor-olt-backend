from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func


class Log(BaseModel):
    __tablename__ = "log"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, unique=True, index=True)
    olt_id = Column(Integer, ForeignKey("olt.id"))
    onu_id =Column(Integer, ForeignKey("onu.id"))
    agent_id = Column(Integer, ForeignKey("agent.id"))
    ip_address = Column(String)
    created_at = Column(DateTime, server_default=func.now())