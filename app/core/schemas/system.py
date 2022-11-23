from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel


class OltCreate(BaseModel):
    name: str
    ip_address: str
    ssh_port: int
    ssh_user: str
    ssh_password: str
    snmp_port: int
    snmp_read_com: str
    snmp_write_com: str
    hardware_ver: str 
    software_ver: str

class Olt(OltCreate):
    id: int

class Onu(BaseModel):
    olt: OltCreate
    sn: str
    shelf: int
    slot: int
    port: int
    index: int

    def __str__(self):
        return f"gpon-onu_{self.shelf}/{self.slot}/{self.port}:{self.index}"