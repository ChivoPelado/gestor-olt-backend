"""
Modelado del módulo Sistema
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


##############################
# Esquemas de OLT
##############################
class OltResponse(BaseModel):
    id: int
    name: str
    host: str
    telnet_port: int
    telnet_user: str
    snmp_port: int
    hardware_ver: str 
    software_ver: str

    class Config:
        orm_mode = True

class OltCreate(BaseModel):
    name: str
    host: str
    telnet_port: int
    telnet_user: str
    telnet_password: str
    snmp_port: int
    hardware_ver: str 
    software_ver: str
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
    port_id: int
    ext_id: int
    pon_type: str
    shelf: int
    slot: int
    port_no: int
    index: int
    serial_no: str
    vlan: int
    name: str
    status: str
    signal: str
    comment: str
    onu_mode: str
    created_at: Optional[datetime]
   
    class Config:
        orm_mode = True

class Onu(OnuResponse):
    updated_at: Optional[datetime]

class OnuCreate(BaseModel): 
    olt_id: int
    port_id: int
    ext_id: int
    pon_type: str
    shelf: int
    slot: int
    port_no: int
    index: int
    serial_no: str
    vlan: int
    name: str
    status: str
    signal: str
    comment: str
    onu_mode: str

    class Config:
        orm_mode = True


class PortResponse(BaseModel):
    slot: int
    port: int
    pon_type: str
    admin_status: str 
    operation_status: str 
    description: str 
    tx_power: str 
    onu_count: int
    online_onu_count: int
    offline_onu_count: int
    average_onu_signal: int

    class Config:
        orm_mode = True


class CardResponse(BaseModel):
    slot: int
    type: str
    real_type: str
    port: int
    soft_ver: str
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True