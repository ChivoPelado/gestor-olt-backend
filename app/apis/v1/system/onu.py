from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.apis.v1.system import onu_crud
from app.core.schemas.system import OnuResponse, OnuCreate
from app.core.models.system import Onu, Olt
from app.celery_task.tasks import get_onu_signal_level
from app.core.schemas.generic import IResponseBase
from app.interface.utils import Payload


router = APIRouter()

@router.post("/onu/authorize",  response_model=IResponseBase[OnuResponse])
async def authorize_onu(onu: OnuCreate, db: Session = Depends(get_db)): 
    authorized_onu = onu_crud.authorize_onu(db, onu=onu)
    return IResponseBase[OnuResponse](response=authorized_onu)

@router.get("/onu",  response_model=IResponseBase[OnuResponse])
async def authorize_onu(onu: OnuCreate, db: Session = Depends(get_db)): 
    authorized_onu = onu_crud.authorize_onu(db, onu=onu)
    return IResponseBase[OnuResponse](response=authorized_onu)


@router.get("/sys/onu/get_onu_signal/{ext_id}")
def get_onu_signal(ext_id: int,  db: Session = Depends(get_db)) -> dict:
    """
    Retorna la potencia óptica de la ONU
    """
    db_onu = db.query(Onu).join(Olt, Onu.olt_id == Olt.id).filter(Onu.ext_id == ext_id).first()

    connection_payload = Payload(
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
    res = task.get(disable_sync_subtasks=False)

    return res
