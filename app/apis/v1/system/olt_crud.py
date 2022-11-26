from typing import List
from sqlalchemy.orm import Session
from app.core.models.system import Olt
from app.core.models.system import Card
from app.interface.commands import show_card
from app.interface.utils import Payload
from app.celery_task.tasks import olt_get_card_task


# Crea una nueva OLT
def create_olt(db: Session, olt: Olt) -> Olt:
    db_olt = Olt(**dict(olt))
    db.add(db_olt)
    db.commit()
    db.refresh(db_olt) 
    # olt_id = db.query(Olt).filter(Olt.name == olt.name and Olt.ip_address == olt.ip_address).first()
    get_olt_cards(db, olt=db_olt)
    return db_olt


# Almacena en db las Tarjetas(Cards) de la OLT 
def get_olt_cards(db:Session, olt: Olt):
    cards: dict = {}
    objects = []
    connection_payload = Payload(
        olt_type = "ZTE",
        olt_name = olt.name,
        olt_ip_address = olt.ip_address,
        ssh_port = olt.ssh_port,
        ssh_user = olt.ssh_user,
        ssh_password = olt.ssh_password,
        snmp_port = olt.snmp_port,
        snmp_read_com = olt.snmp_read_com,
        snmp_write_com =olt.snmp_write_com,
        onu_interface = "",
        shelf = "",
        slot = "",
        port = "",
        index = ""
    )

    task = olt_get_card_task.apply_async(args=[connection_payload], queue='olt')
    cards = task.get(disable_sync_subtasks=False)
    # cards = 
    # cards = show_card.get_olt()

    for card in cards:
        db_item = Card(olt_id = olt.id, **card)
        """             rack = card['rack'],
            shelf = card['shelf'],
            slot = card['slot'],
            cfg_type = card['cfgtype'],
            real_type = card['realtype'],
            port = card['port'],
            hardware_ver = card['hardver'],
            software_ver = card['softver'],
            status = card['status']  
        )"""
        objects.append(db_item)
    
    db.bulk_save_objects(objects)
    db.commit()
    return cards


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
    