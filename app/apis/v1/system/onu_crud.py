
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
import time
from app.core.models.system import Olt, Onu, Shelf, Port, Card, OnuType, SpeedProfileUp, SpeedProfileDown
from app.core.models.location import Region, Zone, Nap
from app.core.models.log import ActionLog
from app.device.command.controller import OltController
from app.device.command.commands import (
    AuthorizeONU,
    GetSrvcPrtAndIndex,
    GetUncfgONUs,
    OnuRXSignal,
    OltRXSignal,
    DeleteOnu,
    OnuState,
    DeactivateOnu,
    ActivateOnu,
    RebooteOnu,
    SetOnuModeBridging,
    SetOnuModeRouting,
    EnableONUCatv,
    DisableONUCatv,
    ResyncONU,
    GetONURunningConfig,
    GetONUGeneralStatus
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


def authorize_onu(olt_id: int, slot: int, port: int, onu_sn: str, onu_type: str,  onu_mode: str,
        vlan: int, region_id: int, zone_id: int, nap_id: int, down_speed: str, up_speed: str, name: str, comment: str, onu_ext_id: int,
        db_session: Session, user_id: int, user_ip: str) -> Onu:

    olt, card_id, port_id, onu_type, speed_down, speed_up = db_session.query(
        Olt, Card.id, Port.id, OnuType, SpeedProfileDown, SpeedProfileUp) \
        .join(Olt) \
        .join(Port) \
        .filter(
            and_(
                Olt.id == olt_id,
                Card.slot == slot, 
                Port.port == port,
                OnuType.name.like(onu_type),
                SpeedProfileDown.name.like(down_speed),
                SpeedProfileUp.name.like(up_speed)
                )
            ) \
        .first()

    db_shelf = olt.shelf[0].shelf

    catv = "Enabled" if onu_type.catv == '1' else "Not supported by onu type" 

    db_speed_profile_up_name = f"SMARTOLT-{speed_up.name}-UP"
    db_speed_profile_down_name = f"SMARTOLT-{speed_down.name}-DOWN"

    onu_srvcprt, onu_index = controller.get(GetSrvcPrtAndIndex(db_shelf, slot, port, vlan), olt)

    new_onu = Onu(olt_id = olt_id, port_id = port_id, onu_type_id = onu_type.id, speed_profile_up_id = speed_up.id,
        speed_profile_down_id = speed_down.id, region_id = region_id, zone_id = zone_id, nap_id = nap_id, ext_id = onu_ext_id, 
        shelf = db_shelf, slot = slot, port_no = port, index = onu_index, srvc_port=onu_srvcprt, serial_no = onu_sn, vlan = vlan, 
        upload_speed = db_speed_profile_up_name, download_speed = db_speed_profile_down_name, name = name, comment = comment, 
        catv = catv, onu_mode = onu_mode)

    result, log = controller.get(AuthorizeONU(new_onu, onu_type), olt)

    if result:

        new_log = ActionLog(
        olt_id=log[1], action=log[0], onu_ext_id=new_onu.ext_id, agent_id=user_id, ip_address=user_ip)

        db_session.add(new_onu)
        db_session.add(new_log)
        db_session.commit()
        
    return new_onu


def get_onu_signals_by_ext_id(onu_ext_id: int, db_session: Session) -> Onu:
    db_onu, db_olt = db_session.query(Onu, Olt) \
        .join(Olt) \
        .filter(Onu.ext_id == onu_ext_id).first()

    time.sleep(5)

    onu_tx = controller.get(OnuRXSignal(db_onu), db_olt) 
    olt_tx = controller.get(OltRXSignal(db_onu), db_olt) 
    onu_state = controller.get(OnuState(db_onu), db_olt) 

    db_onu.signal = olt_tx
    db_onu.status = onu_state
    db_onu.signal_1310 = onu_tx

    db_session.commit()

    return db_onu


#@controller.log
def delete_onu_by_ext_id(db_session: Session, onu_ext_id: int, user_id: int, user_ip: str):
        
        db_onu: Onu
        db_olt: Olt

        db_onu, db_olt = db_session.query(Onu, Olt) \
        .join(Olt) \
        .filter(Onu.ext_id == onu_ext_id).first()

        try:

            response, log = controller.get(DeleteOnu(db_onu), db_olt)

            if response:
                db_session.delete(db_onu)

            new_log = ActionLog(
                olt_id=log[1], action=log[0], onu_ext_id=db_onu.ext_id, agent_id=user_id, ip_address=user_ip)

            db_session.add(new_log)
            db_session.commit()

            return True

        except Exception as err:
            print(err)
        
        return False


def deactivate_onu_by_ext_id(db_session: Session, onu_ext_id: int, user_id: int, user_ip: str):
        
        db_onu: Onu
        db_olt: Olt

        db_onu, db_olt = db_session.query(Onu, Olt) \
        .join(Olt) \
        .filter(Onu.ext_id == onu_ext_id).first()

        try:

            response, log = controller.get(DeactivateOnu(db_onu), db_olt)

            if response:
                db_onu.admin_status = "Disabled"

            new_log = ActionLog(
                olt_id=log[1], action=log[0], onu_ext_id=db_onu.ext_id, agent_id=user_id, ip_address=user_ip)

            db_session.add(new_log)
            db_session.commit()

            return True

        except Exception as err:
            print(err)

        return False


def activate_onu_by_ext_id(db_session: Session, onu_ext_id: int, user_id: int, user_ip: str):
        
        db_onu: Onu
        db_olt: Olt

        db_onu, db_olt = db_session.query(Onu, Olt) \
        .join(Olt) \
        .filter(Onu.ext_id == onu_ext_id).first()

        try:

            response, log = controller.get(ActivateOnu(db_onu), db_olt)

            if response:
                db_onu.admin_status = "Enabled"

            new_log = ActionLog(
                olt_id=log[1], action=log[0], onu_ext_id=db_onu.ext_id, agent_id=user_id, ip_address=user_ip)

            db_session.add(new_log)
            db_session.commit()

            return True

        except Exception as err:
            print(err)

        return False


def reboot_onu_by_ext_id(db_session: Session, onu_ext_id: int, user_id: int, user_ip: str):
        
        db_onu: Onu
        db_olt: Olt

        db_onu, db_olt = db_session.query(Onu, Olt) \
        .join(Olt) \
        .filter(Onu.ext_id == onu_ext_id).first()

        try:

            response, log = controller.get(RebooteOnu(db_onu), db_olt)

            new_log = ActionLog(
                olt_id=log[1], action=log[0], onu_ext_id=db_onu.ext_id, agent_id=user_id, ip_address=user_ip)

            db_session.add(new_log)
            db_session.commit()

            return True

        except Exception as err:
            print(err)

        return False


def set_onu_mode(db_session: Session, onu_ext_id: int, mode: str, user_id: int, user_ip: str):
    
    db_onu: Onu
    db_olt: Olt

    db_onu, db_olt, db_onu_type = db_session.query(Onu, Olt, OnuType) \
    .join(Olt) \
    .join(OnuType) \
    .filter(Onu.ext_id == onu_ext_id, Onu.onu_type_id == OnuType.id).first()

    try:

        if mode == "Bridging":
            response, log = controller.get(SetOnuModeBridging(db_onu, db_onu_type), db_olt)

        elif mode == "Routing":
            response, log = controller.get(SetOnuModeRouting(db_onu, db_onu_type), db_olt)
            
        db_onu.onu_mode = mode

        new_log = ActionLog(
            olt_id=log[1], action=log[0], onu_ext_id=db_onu.ext_id, agent_id=user_id, ip_address=user_ip)

        db_session.add(new_log)
        db_session.commit()

        return True

    except Exception as err:
        print(err)

    return False


def enable_onu_catv(db_session: Session, onu_ext_id: int, user_id: int, user_ip: str):
    
    db_onu: Onu
    db_olt: Olt

    db_onu, db_olt = db_session.query(Onu, Olt) \
    .join(Olt) \
    .filter(Onu.ext_id == onu_ext_id).first()

    try:

        response, log = controller.get(EnableONUCatv(db_onu), db_olt)

        if response:
            db_onu.catv = "Enabled"

        new_log = ActionLog(
            olt_id=log[1], action=log[0], onu_ext_id=db_onu.ext_id, agent_id=user_id, ip_address=user_ip)

        db_session.add(new_log)
        db_session.commit()

        return True

    except Exception as err:
        print(err)

    return False


def disable_onu_catv(db_session: Session, onu_ext_id: int, user_id: int, user_ip: str):
    
    db_onu: Onu
    db_olt: Olt

    db_onu, db_olt = db_session.query(Onu, Olt) \
    .join(Olt) \
    .filter(Onu.ext_id == onu_ext_id).first()

    try:

        response, log = controller.get(DisableONUCatv(db_onu), db_olt)

        if response:
            db_onu.catv = "Disabled"

        new_log = ActionLog(
            olt_id=log[1], action=log[0], onu_ext_id=db_onu.ext_id, agent_id=user_id, ip_address=user_ip)

        db_session.add(new_log)
        db_session.commit()

        return True

    except Exception as err:
        print(err)

    return False


def resync_onu(db_session: Session, onu_ext_id: int, user_id: int, user_ip: str):

    db_onu, db_olt, db_onu_type = db_session.query(Onu, Olt, OnuType) \
        .join(Olt) \
        .join(OnuType) \
        .filter(Onu.ext_id == onu_ext_id, Onu.onu_type_id == OnuType.id).first()

    try:

        response, log = controller.get(ResyncONU(db_onu, db_onu_type), db_olt)

        new_log = ActionLog(
            olt_id=log[1], action=log[0], onu_ext_id=db_onu.ext_id, agent_id=user_id, ip_address=user_ip)

        db_session.add(new_log)
        db_session.commit()

        return True

    except Exception as err:
        print(err)

    return False


def get_onu_running_config(db_session: Session, onu_ext_id: int, user_id: int, user_ip: str):

    db_onu: Onu
    db_olt: Olt

    db_onu, db_olt = db_session.query(Onu, Olt) \
    .join(Olt) \
    .filter(Onu.ext_id == onu_ext_id).first()

    try:

        response = controller.get(GetONURunningConfig(db_onu), db_olt)

        return response

    except Exception as err:
        print("Error al ejecutar commando ", err)

    return None

def get_onu_general_status(db_session: Session, onu_ext_id: int, user_id: int, user_ip: str):

    db_onu: Onu
    db_olt: Olt

    db_onu, db_olt = db_session.query(Onu, Olt) \
    .join(Olt) \
    .filter(Onu.ext_id == onu_ext_id).first()

    try:

        response = controller.get(GetONUGeneralStatus(db_onu), db_olt)

        return response

    except Exception as err:
        print("Error al ejecutar commando ", err)

    return None

def create_onus(onus: List[Onu], db: Session):
    

    db_onus = []
    for onu in onus:
     
        db_onu_id = db.query(OnuType.id).filter(OnuType.name == onu['onu_type_name']).first()
        port_id, card_id = db.query(Port.id, Card.id).join(Card, Olt) \
            .filter(
                Card.slot == onu['slot'],
                Olt.id == onu['olt_id'], 
                Port.port == onu['port_no']
             ).first()

        zone_id, region_id = db.query(Zone.id, Zone.region_id).filter(Zone.name == onu['zone_name']).first()
        nap_id = db.query(Nap.id).filter(Nap.name == onu['nap_name']).first()
        speed_up_id = db.query(SpeedProfileUp.id).filter(SpeedProfileUp.name == onu['upload_speed']).first()
        speed_down_id = db.query(SpeedProfileDown.id).filter(SpeedProfileDown.name == onu['download_speed']).first()

        
        new_onu = Onu(
            olt_id = onu['olt_id'],
            port_id = port_id,
            onu_type_id = db_onu_id[0],
            speed_profile_up_id = speed_up_id[0],
            speed_profile_down_id = speed_down_id[0],
            region_id = region_id,
            zone_id = zone_id,
            nap_id = nap_id[0],
            ext_id = onu['ext_id'],
            pon_type = onu['pon_type'],
            shelf = onu['shelf'],
            slot = onu['slot'],
            port_no = onu['port_no'],
            index = onu['index'],
            srvc_port = onu['srvc_port'],
            serial_no = onu['serial_no'],
            vlan = onu['vlan'],
            upload_speed = onu['upload_speed'],
            download_speed = onu['download_speed'],
            name = onu['name'],
            comment = onu['comment'],
            catv = onu['catv'],
            admin_status = onu['admin_status'],
            status = "En Línea" if onu['status'] == "Online" else "Fuera de Línea" if onu['status'] == 'Offline' else "Falla Eléctrica" if onu['status'] == "Power fail" else onu['status'],
            signal = onu['signal'],
            signal_1310 = str(float(onu['signal_1310'])/1000),
            onu_mode = onu['onu_mode'],

        )

        db_onus.append(new_onu)
    
    try:
        db.bulk_save_objects(db_onus)
        db.commit()
        return True

    except Exception as err:
        print(err)
        return False
            