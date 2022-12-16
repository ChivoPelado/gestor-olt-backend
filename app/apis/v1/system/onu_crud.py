
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.core.models.system import Olt, Onu, Port, Card, OnuType, SpeedProfile
from app.device.command.controller import OltController
from app.device.command.commands import (
    AuthorizeONU
)

controller = OltController()

# Autoriza una nueva onu (Mock)
def authorize_onu(
        olt_id: int,
        slot: int,
        port: int,
        onu_sn: str, 
        onu_type: str,
        onu_mode: str,
        vlan: int,
        down_speed: str,
        up_speed: str,
        name: str,
        comment: str,
        onu_ext_id: int,
        db: Session) -> Onu:

    db_olt = db.query(Olt).filter(Olt.id == olt_id).first()

    db_card = db.query(Card).join(Olt, Card.olt_id == olt_id).filter(
        Card.slot == slot).first()

    db_port = db.query(Port).join(Card, Port.card_id == db_card.id).filter(
        Port.port == port).first() 

    db_onu_type = db.query(OnuType).filter(OnuType.name == onu_type).first()
    
    db_speed_profile_up = db.query(SpeedProfile).filter(
        SpeedProfile.direction == "upload", SpeedProfile.name == up_speed).first()

    db_speed_profile_down = db.query(SpeedProfile).filter(
        SpeedProfile.direction == "download", SpeedProfile.name == down_speed).first()

    db_speed_profile_up_name = f"SMARTOLT-{db_speed_profile_up.name}-UP"
    db_speed_profile_down_name = f"SMARTOLT-{db_speed_profile_down.name}-DOWN"

    db_shelf = db_olt.shelf[0].shelf

    new_onu = Onu(
        olt_id = olt_id,
        port_id = db_port.id,
        onu_type_id = db_onu_type.id,
        speed_profile_id = db_speed_profile_up.id,
        ext_id = onu_ext_id,
        shelf = db_shelf,
        slot = slot,
        port_no = port,
        serial_no = onu_sn,
        vlan = vlan,
        name = name,
        comment = comment,
        onu_mode = onu_mode
    )
     

    result = controller.get(AuthorizeONU(
        new_onu, db_onu_type, db_speed_profile_up_name, db_speed_profile_down_name), db_olt)

    if result:
        new_onu.index = result
  
    db.add(new_onu)
    db.commit()
    db.refresh(new_onu)
    
    return new_onu

