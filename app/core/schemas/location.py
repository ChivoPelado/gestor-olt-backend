from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, EmailStr



class RegionCreate(BaseModel):
    name: str
    description: Optional[str]

    
class RegionResponse(RegionCreate):
    id: int

    class Config:
        orm_mode = True
 

class ZoneCreate(BaseModel):
    region_id: int
    name: str
    description: Optional[str]
    
    
class ZoneResponse(ZoneCreate):
    id: int

    class Config:
        orm_mode = True


class NapCreate(BaseModel):
    region_id: int
    zone_id: int
    name: str
    ports: int
    latitude: float
    longitude:float
    description: Optional[str]
    
    
class NapResponse(NapCreate):
    id: int

    class Config:
        orm_mode = True