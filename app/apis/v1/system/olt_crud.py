from typing import List
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.models.system import Olt, Shelf, Card, Port, Vlan, Onu
from app.device.command.controller import OltController
from app.device.command.commands import (
    GetUncfgONUs,
    GetOLTCards,
    GetOLTPorts,
    GetOLTVlans,
    GetOLTShelf,
    PortTXValue,
    PortAdminState,
    PortStatus,
    PortDescription,
    OnuRXSignal,
    OltRXSignal,
    OnuState,
    GetONUAttenuation,
    TestAuthorizeONU
)
from celery import shared_task
from fastapi_utils.tasks import repeat_every
from fastapi import Request


controller = OltController()

# 
@shared_task(name='recurrent:update_olt_values')
def update_olt_values():

    print("Actualizando parámetros de OLT...")

    db_session: Session = next(get_db())

    for olt in db_session.query(Olt).all():
        for card in olt.cards:
            for port in card.ports:
                shelf = olt.shelf[0].shelf
                slot = port.slot
                port_no = port.port
                
                tx_power = controller.get(PortTXValue(shelf, slot, port_no), olt)
                admin_state = controller.get(PortAdminState(shelf, slot, port_no), olt)
                port_status = controller.get(PortStatus(shelf, slot, port_no), olt)
                port_descr = controller.get(PortDescription(shelf, slot, port_no), olt)
                
                port.tx_power = str(tx_power) 
                port.admin_status = admin_state
                port.operation_status = port_status
                port.description = port_descr

                db_session.commit()


@repeat_every(seconds=300, raise_exceptions=True)
def start_recurrent_task():
    task = update_olt_values.apply_async(queue='recurrent')
    print(task.id)


def test_point(db: Session, olt_id: int, request: Request, user: any):
    
    db_olt = db.query(Olt).filter(Olt.id == olt_id).first()
    db_onu = db.query(Onu).first()

    """     onu_tx = controller.get(OnuRXSignal(1, 6, 16, 2), db_olt) 
    olt_tx = controller.get(OltRXSignal(1, 6, 16, 2), db_olt) 
    onu_state = controller.get(OnuState(1, 6, 16, 2), db_olt)  """
    
    response = controller.get(TestAuthorizeONU(), db_olt)
    # delete_onu = controller.get(GetONUAttenuation(db_onu), db_olt)
    # await update_olt_values()
    
    #print(delete_onu)
    # print(onu_tx, olt_tx, onu_state)
    #return result_parsed
    return response

# Crea una nueva OLT
async def create_olt(name: str, ip_address: str, telnet_port: int, telnet_user: str, 
    telnet_password: str, snmp_port: int, snmp_read_com: str, snmp_write_com: str,
    hardware_ver: str, software_ver: str, db_session: Session) -> Olt:
    """ 
    Proceso de ingreso de una nueva OLT.
    El proceso descubre las tarjetas y los puertos de la olt
    y las aagrega a la base de datos    
    """

    # Registrar olt
    db_olt = Olt(
        name = name, host = ip_address, telnet_port = telnet_port, telnet_user = telnet_user, 
        telnet_password = telnet_password, snmp_port =snmp_port, snmp_read_com = snmp_read_com, 
        snmp_write_com = snmp_write_com, hardware_ver = hardware_ver, software_ver = software_ver
        )

    db_session.add(db_olt)
    db_session.commit()
    
    # Obtener Shelf/Frame
    await get_olt_shelf_from(olt=db_olt, db_session=db_session)

    # Obtener tarjetas
    await get_olt_cards_from(olt=db_olt, db_session=db_session)

    # Obtener puertos
    await get_card_ports_from(olt=db_olt, db_session=db_session)

    # Obtener VLANs
    await get_vlans_from(olt=db_olt, db_session=db_session)

    # Actualiza detalles de Olt e inicia termporizador
    # await update_olt_values()
    await start_recurrent_task()
    #task = update_olt_values.apply_async(queue='recurrent')
    #result = task.get(disable_sync_subtasks=False)

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


def get_olt_vlans(db: Session, olt_id: int):

    return db.query(Vlan).filter(Vlan.olt_id == olt_id).all()


def delete_olt_by_id(olt_id: int, db_session: Session) -> bool:
    """Elimina una OLT del sistema y todos sus elementos hijos.

    Args:
        olt_id (int): ID de OLT a eliminar
        db_session (Session): Session de Base de Datos

    Returns:
        bool: Verdadero si se elimina correctamente, Falso en el caso de no existir OLT
    """
    db_olt = db_session.query(Olt).filter(Olt.id == olt_id).first()
    if db_olt:
        db_session.delete(db_olt)
        db_session.commit()

        return True
    return False



# Devuelve OLT desde el ip ingresado
def vlidate_used_ports(db_session: Session, olt_ip: str, telnet_port: int, snmp_port: int) -> bool:
    db_olts = db_session.query(Olt).filter(Olt.host == olt_ip).all()
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
    

