from sqlalchemy import Boolean, Column, Integer, String, ARRAY
from app.database import Base

class Agent(Base):
    __tablename__ = "agent"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    scopes = Column(ARRAY(String))