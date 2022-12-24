
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from app.core.models.system import Olt, Onu, Shelf, Port, Card, OnuType, SpeedProfileUp, SpeedProfileDown
from app.device.command.controller import OltController
from app.device.command.commands import (
    AuthorizeONU,
    GetUncfgONUs,
    OnuRXSignal,
    OltRXSignal,
    OnuState
)


controller = OltController()

def get_uncfg_onus(db: Session):

    uncfg_onus = []
    response = {}

    for olt in db.query(Olt).all():
        result = controller.get(GetUncfgONUs(), olt)
        response = {
            "olt_id": olt.id,
            "olt_name": olt.name,
            "uncfg_onus": [onus for onus in result]
        }

        uncfg_onus.append(response)
    
    return uncfg_onus

# Autoriza una nueva onu (Mock)
def authorize_onu(olt_id: int, slot: int, port: int, onu_sn: str, onu_type: str,  onu_mode: str,
        vlan: int, down_speed: str, up_speed: str, name: str, comment: str, onu_ext_id: int,
        db: Session) -> Onu:

    olt, card_id, port_id, onu_type, speed_down, speed_up = db.query(
        Olt, Card.id, Port.id, OnuType, SpeedProfileDown, SpeedProfileUp) \
        .join(Olt) \
        .join(Port) \
        .filter(
            and_(
                Card.slot == slot, 
                Port.port == port,
                OnuType.name.like(onu_type),
                SpeedProfileDown.name.like(down_speed),
                SpeedProfileUp.name.like(up_speed)
                )
            ) \
        .first()

    db_shelf = olt.shelf[0].shelf

    db_speed_profile_up_name = f"SMARTOLT-{speed_up.name}-UP"
    db_speed_profile_down_name = f"SMARTOLT-{speed_down.name}-DOWN"


    new_onu = Onu(olt_id = olt_id, port_id = port_id, onu_type_id = onu_type.id, speed_profile_up_id = speed_up.id,
        speed_profile_down_id = speed_down.id, ext_id = onu_ext_id, shelf = db_shelf, slot = slot,
        port_no = port, serial_no = onu_sn, vlan = vlan, name = name, comment = comment, onu_mode = onu_mode)
     
    
    result = controller.get(AuthorizeONU(
        new_onu, onu_type, db_speed_profile_up_name, db_speed_profile_down_name), olt)

    if result:
        new_onu.index = result
  
    db.add(new_onu)
    db.commit()
    
    return new_onu

def get_onu_signals_by_ext_id(onu_ext_id: int, db_session: Session) -> Onu:
    db_onu, db_olt = db_session.query(Onu, Olt) \
        .join(Olt) \
        .filter(Onu.ext_id == onu_ext_id).first()

    shelf = int(db_onu.shelf)
    slot = int(db_onu.slot)
    port = int(db_onu.port_no)
    index = int(db_onu.index)

    onu_tx =  controller.get(OnuRXSignal(shelf, slot, port, index), db_olt) 
    olt_tx =  controller.get(OltRXSignal(shelf, slot, port, index), db_olt) 
    onu_state =  controller.get(OnuState(shelf, slot, port, index), db_olt) 

    db_onu.signal = olt_tx
    db_onu.status = onu_state
    db_onu.signal_1310 = onu_tx

    db_session.commit()

    

    return db_onu