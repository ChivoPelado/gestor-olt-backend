from typing import List
from sqlalchemy.orm import Session
from app.core.models.system import Olt, Shelf, Card, Port, Vlan
from app.interface.utils import Payload
from app.celery_task.tasks import get_port_tx_signal_level
from app.device.config import initialize_modules
from app.device.base.device_base import OltDeviceBase
from app.device.command.controller import OltController
from app.device.command.commands import (
    GetUncfgONUs,
    GetOLTCards,
    GetOLTPorts,
    GetOLTVlans,
    GetOLTShelf
)
import functools

controller = OltController()

def decorator_test(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        #Acciones anteriores
        #print('*ARGS', args[0])
        print('**KWRGS', kwargs['db'])
        value = func(*args, **kwargs)
        #Acciones posteriores
        
        return value
    return wrapper_decorator


#@decorator_test
async def test_point(db: Session, olt_id: int):
    db_olt = db.query(Olt).filter(Olt.id == olt_id).first()
    
    result_parsed = controller.get(GetOLTShelf(), db_olt)
    #print(controller.get_command_history())



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
    
    # Obtener Shelf/Frame
    await get_olt_shelf_from(olt=db_olt, db_session=db)

    # Obtener tarjetas
    await get_olt_cards_from(olt=db_olt, db_session=db)

    # Obtener puertos
    await get_card_ports_from(olt=db_olt, db_session=db)

    # Obtener VLANs
    await get_vlans_from(olt=db_olt, db_session=db)

    return db_olt


async def get_olt_shelf_from(olt: Olt, db_session:Session):
    result_parsed = controller.get(GetOLTShelf(), olt)

    db_shelf = Shelf(olt_id = olt.id, **result_parsed)

    db_session.add(db_shelf)
    db_session.commit()


# Extrae y almacena en db las Tarjetas(Cards) de la OLT 
async def get_olt_cards_from(olt: Olt, db_session:Session):
    db_cards = []
    result_parsed = controller.get(GetOLTCards(), olt)

    for card in result_parsed:
        db_item = Card(olt_id = olt.id, **card)
        db_cards.append(db_item)
    
    db_session.bulk_save_objects(db_cards)
    db_session.commit()
    return result_parsed


# Extrae y almacena en db los Puertos de las Tarjetas(Cards) de la OLT 
async def get_card_ports_from(olt: Olt, db_session: Session):
    
    db_ports = []
    db_card = {}
    result_parsed = controller.get(GetOLTPorts(), olt)

    index = 0
    for card in olt.cards:
        if card.role == "GPON":
            for _ in range(card.port):
                db_port = Port(
                    card_id = card.id,
                    slot = result_parsed[index]['slot'],
                    port = result_parsed[index]['port'],
                    pon_type = result_parsed[index]['pon_type']
                )
                index += 1

                db_ports.append(db_port)

    db_session.bulk_save_objects(db_ports)
    db_session.commit()
    return db_ports


# Extrae las VLANs de OLT y almacena en base de datos
async def get_vlans_from(olt: Olt, db_session: Session):
    
    result_parsed = controller.get(GetOLTVlans(), olt)

    db_vlan = []
    for vlan in result_parsed:
        db_item = Vlan(olt_id = olt.id, **vlan)
        db_vlan.append(db_item)

    
    db_session.bulk_save_objects(db_vlan)
    db_session.commit()
    return db_vlan


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
