from typing import List
from sqlalchemy.orm import Session
from app.core.utils.security import Hasher
from app.core.models.system import Olt


# Crea una nueva OLT
def create_olt(db: Session, olt: Olt) -> Olt:
    db_olt = Olt(
        name = olt.name, 
        ip_address = olt.ip_address,
        ssh_port = olt.ssh_port,
        ssh_user = olt.ssh_user,
        ssh_password = olt.ssh_password,
        snmp_port= olt.snmp_port,
        snmp_read_com = olt.snmp_read_com,
        snmp_write_com = olt.snmp_write_com,
        hardware_ver = olt.hardware_ver,
        software_ver = olt.software_ver 
    )
    db.add(db_olt)
    db.commit()
    db.refresh(db_olt) 
    return db_olt


# Devuelve OLT desde el ip ingresado
def vlidate_used_ports(db: Session, olt_ip: str, olt_ssh_port: int, olt_snmp_port: int) -> bool:
    db_olts = db.query(Olt).filter(Olt.ip_address == olt_ip).all()
    for olt in db_olts:
        if olt.ssh_port == olt_ssh_port or olt.snmp_port == olt_snmp_port:
            return False
    return True


# Devuelve OLT desde el id
def get_olt(db: Session, olt_id: int) -> Olt:
    return db.query(Olt).filter(Olt.id == olt_id).first()


# Devuelve todas las OLTs
def get_olts(db: Session, skip: int = 0, limit: int = 100) -> List[Olt]:
    return db.query(Olt).offset(skip).limit(limit).all()
    