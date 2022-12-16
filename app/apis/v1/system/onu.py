"""
APIs para la gestión de ONUs
"""
from fastapi import APIRouter, Form, Depends
from typing import List
from sqlalchemy.orm import Session
from app.database import get_db
from app.apis.v1.system import onu_crud
from app.core.schemas.system import OnuResponse, OnuCreate
from app.core.models.system import Onu, Olt, Port, Card, OnuType
from app.celery_task.tasks import get_onu_signal_level
from app.core.schemas.generic import IResponseBase



router = APIRouter()

@router.post("/authorize") #,  response_model=IResponseBase[OnuResponse])
async def authorize_onu(
    olt_id: int = Form(),
    slot: int = Form(),
    port: int = Form(),
    onu_sn: str = Form(), 
    onu_type: str = Form(),
    onu_mode: str = Form(),
    vlan: int = Form(),
    down_speed: str = Form(),
    up_speed: str = Form(),
    name: str = Form(),
    comment: str = Form(),
    onu_ext_id: int = Form(),
    
    db: Session = Depends(get_db)): 
    authorized_onu = onu_crud.authorize_onu( 
        olt_id,
        slot,
        port,
        onu_sn, 
        onu_type,
        onu_mode,
        vlan,
        down_speed,
        up_speed,
        name,
        comment,
        onu_ext_id,
        db=db)
    return authorized_onu #IResponseBase[OnuResponse](response=authorized_onu)

@router.get("/",  response_model=IResponseBase[OnuResponse])
async def authorize_onu(onu: OnuCreate, db: Session = Depends(get_db)): 
    authorized_onu = onu_crud.authorize_onu(db, onu=onu)
    return IResponseBase[OnuResponse](response=authorized_onu)



@router.get("/get_onu_signal/{ext_id}")
def get_onu_signal(ext_id: int,  db: Session = Depends(get_db)) -> dict:
    """
    Retorna la potencia óptica de la ONU
    """

    ##db_onu = db.query(Onu).join(Olt, Onu.olt_id == Olt.id).filter(Onu.ext_id == ext_id).first()
    # db_onu = db.query(Card).join(Olt, Card.olt_id == Olt.id).filter(Onu.ext_id == ext_id).first()
    db_onu = db.query(Onu).join(Port, Onu.port_id == Port.id).filter(Onu.ext_id == ext_id).first()
   
    print(db_onu.port.card)
    """     connection_payload = Payload(
        olt_type = "ZTE",
        olt_name = db_onu.olt.name,
        olt_ip_address = db_onu.olt.ip_address,
        ssh_port = db_onu.olt.ssh_port,
        ssh_user = db_onu.olt.ssh_user,
        ssh_password = db_onu.olt.ssh_password,
        snmp_port = db_onu.olt.snmp_port,
        snmp_read_com = db_onu.olt.snmp_read_com,
        snmp_write_com =db_onu.olt.snmp_write_com,
        onu_interface = str(db_onu),
        shelf = db_onu.shelf,
        slot = db_onu.slot,
        port = db_onu.port,
        index = db_onu.index
    )

    task = get_onu_signal_level.apply_async(args=[connection_payload])
    res = task.get(disable_sync_subtasks=False) """

    return db_onu
