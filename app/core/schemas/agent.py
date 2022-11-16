from enum import Enum
from typing import List
from pydantic import BaseModel, EmailStr


class AgentRole(str, Enum):
    ADMIN = "Administrador"
    TECH_SUPPORT = "Soporte Técnico"
    ATC = "Call Center"
    INSTALLER = "Instalador"


class AgentCreate(BaseModel):
    name: str
    email: EmailStr
    hashed_password: str
    is_active: bool
    role: AgentRole
    scopes: List[str] = []
    
    
class AgentResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    role: AgentRole
    
    class Config:
        orm_mode = True
 
        
class PaginatedAgentListInfo(BaseModel):
    skip: int
    limit: int
    data: List[AgentResponse]
    

class AgentAuth(BaseModel):
    name: str
    email: EmailStr
    is_active: bool
    role: AgentRole
    
    class Config:
        orm_mode = True