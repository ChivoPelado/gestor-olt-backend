from typing import List
from sqlalchemy.orm import Session
from app.core.models.system import Olt, Card, Port
from app.interface.utils import Payload
from app.celery_task.tasks import get_port_tx_signal_level
from app.device.config import initialize_modules
from app.device.base.device_base import OltDeviceBase

modules = initialize_modules()

def get_olt_vendor_item(olt: Olt) -> OltDeviceBase:
    try:
        (vendor,) = [device for device in modules if device.hardware_ver == olt.hardware_ver 
                        and olt.software_ver in device.software_ver]
        
        vendor.connection_pars = olt.connection_params

        return vendor

    except ValueError:
        print("Error al validar tipo de olt")


async def test_point(db: Session, olt_id: int):
    db_olt = db.query(Olt).filter(Olt.id == olt_id).first()
    
    vendor = get_olt_vendor_item(db_olt)
    result_parsed = vendor.get_onu_types()

    return result_parsed


# Crea una nueva OLT
async def create_olt(db: Session, olt: Olt) -> Olt:
    """ 
    Proceso de ingreso de una nueva OLT.
    El proceso descubre las tarjetas y los puertos de la olt
    y las aagrega a la base de datos    
    """
    # Registrar olt
    db_olt = Olt(**dict(olt))
    db.add(db_olt)
    db.commit()
    db.refresh(db_olt) 
    
    # Obtener tarjetas
    await get_olt_cards(db, olt=db_olt)

    # Obtener puertos
    await get_card_ports(db, olt=db_olt)

    return db_olt


# Almacena en db las Tarjetas(Cards) de la OLT 
async def get_olt_cards(db:Session, olt: Olt):
    db_cards = []
    vendor = get_olt_vendor_item(olt)
    result_parsed = vendor.get_cards()

    for card in result_parsed:
        db_item = Card(olt_id = olt.id, **card)
        db_cards.append(db_item)
    
    db.bulk_save_objects(db_cards)
    db.commit()
    return result_parsed


async def get_card_ports(db:Session, olt: Olt):
    db_ports = []
    vendor = get_olt_vendor_item(olt)

    for card in olt.cards:
        if card.role == "GPON":
            for port_number in (port + vendor.port_begin for port in range(card.port)):
                db_port = Port(
                    card_id = card.id,
                    slot = card.slot,
                    port = port_number,
                    pon_type = card.role,
                )

                db_ports.append(db_port)

    db.bulk_save_objects(db_ports)
    db.commit()
    return db_ports


# Devuelve OLT desde el ip ingresado
def vlidate_used_ports(db: Session, olt_ip: str, telnet_port: int, snmp_port: int) -> bool:
    db_olts = db.query(Olt).filter(Olt.host == olt_ip).all()
    for olt in db_olts:
        if olt.telnet_port == telnet_port or olt.snmp_port == snmp_port:
            return False
    return True


# Devuelve OLT desde el id
def get_olt(db: Session, olt_id: int) -> Olt:
    return db.query(Olt).filter(Olt.id == olt_id).first()


# Devuelve todas las OLTs
def get_olts(db: Session, skip: int = 0, limit: int = 100) -> List[Olt]:
    return db.query(Olt).offset(skip).limit(limit).all()
    



""" async def get_card_ports(db:Session, olt: Olt):
    db_ports = []
    ports: dict = {}

    for card in olt.cards:
        if card.cfg_type == "GTGH":
            for port_number in (port + 1 for port in range(card.port)):
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
                    shelf = card.shelf,
                    slot = card.slot,
                    port = port_number,
                    index = ""
                )
                task = get_port_tx_signal_level.apply_async(args=[connection_payload], queue='olt')
                tx_power = task.get(disable_sync_subtasks=False)
                print(tx_power)
                db_port = Port(
                    card_id = card.id,
                    port_no = port_number,
                    pon_type = "GPON",
                    admin_status = "Enabled",
                    operation_status = "Up",
                    description = "Description",
                    tx_power = tx_power,
                    onu_count = 0,
                    # online_onu_count = 0,
                    average_onu_signal = 0
                )

                print(db_port.port_no)
                db_ports.append(db_port)
    db.bulk_save_objects(db_ports)
    db.commit()
    return db_ports """
