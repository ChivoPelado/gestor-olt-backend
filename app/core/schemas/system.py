from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel
from datetime import datetime

##############################
# Esquemas de OLT
##############################
class OltResponse(BaseModel):
    id: int
    name: str
    ip_address: str
    ssh_port: int
    ssh_user: str
    snmp_port: int
    hardware_ver: str 
    software_ver: str

    class Config:
        orm_mode = True

class OltCreate(BaseModel):
    name: str
    ip_address: str
    ssh_port: int
    ssh_user: str
    snmp_port: int
    hardware_ver: str 
    software_ver: str
    ssh_password: str
    snmp_read_com: str
    snmp_write_com: str

class Olt(OltResponse):
    pass


################################
# Esquemas de ONU
###############################

class Onu(BaseModel):
    id: int
    olt_id: int
    ext_id: int
    pon_type: str
    shelf: int
    slot: int
    port: int
    index: int
    serial_no: str
    vlan: int
    name: str
    comment: str
    onu_mode: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class OnuResponse(BaseModel):
    id: int
    olt_id: int
    ext_id: int
    pon_type: str
    shelf: int
    slot: int
    port: int
    index: int
    serial_no: str
    vlan: int
    name: str
    comment: str
    onu_mode: str
    created_at: Optional[datetime]
   
    class Config:
        orm_mode = True

class Onu(OnuResponse):
    updated_at: Optional[datetime]

class OnuCreate(BaseModel): 
    olt_id: int
    ext_id: int
    pon_type: str
    shelf: int
    slot: int
    port: int
    index: int
    serial_no: str
    vlan: int
    name: str
    comment: str
    onu_mode: str