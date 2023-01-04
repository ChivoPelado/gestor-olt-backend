
from typing import  Optional
from pydantic import BaseModel
from datetime import datetime


class ActionLogResponse(BaseModel):
    id: int
    olt_id: int
    olt_name: str
    agent_email: str
    onu: str
    agent_id: int
    action: str
    ip_address: str
    created_at: Optional[datetime]

    class Config:
        orm_mode = True
    
    
class LoginLogResponse(BaseModel):
    id: int
    agent_id: int
    action: str
    ip_address: str
    created_at: Optional[datetime]

    class Config:
        orm_mode = True