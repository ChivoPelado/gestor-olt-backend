"""
APIs para la gestión de ONUs
"""
from fastapi import APIRouter, Form, Depends
from typing import List
from sqlalchemy.orm import Session
from app.database import get_db
from app.apis.v1.system import onu_crud
from app.core.schemas.system import OnuResponse, OnuCreate, UncfgOnuResponse, OnuSignals
from app.core.models.system import Onu, Olt, Port, Card, OnuType, OnuType, SpeedProfileDown, SpeedProfileUp
from app.core.utils.security import login_manager
from app.core.schemas.generic import IResponseBase
import time


router = APIRouter()

@router.get("/unconfigured", response_model=IResponseBase[List[UncfgOnuResponse]])
async def get_uncfg_onus(db: Session = Depends(get_db), user = Depends(login_manager)):
    uncfg_onus = onu_crud.get_uncfg_onus(db)
    return IResponseBase[List[UncfgOnuResponse]](response=list(uncfg_onus))



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


@router.get("/get_onu_by_ext_id/{external_id}",  response_model=IResponseBase[OnuResponse])
async def get_onu_by_ext_id(external_id: int, db: Session = Depends(get_db)): 
   
    response = {}
    db_onu, olt_name, onu_type_name, speed_up_name, speed_down_name = db.query(
        Onu, Olt.name, OnuType.name, SpeedProfileUp.name, SpeedProfileDown.name) \
        .join(Olt) \
        .join(OnuType) \
        .join(Port) \
        .join(SpeedProfileUp) \
        .join(SpeedProfileDown) \
        .filter(Onu.ext_id == external_id).first()

    print(olt_name, onu_type_name, speed_down_name, speed_up_name)

    response = db_onu.__dict__.copy()
    response['olt_name'] = olt_name
    response['onu_type_name'] = onu_type_name
    response['speed_profile_up_name'] = speed_up_name
    response['speed_profile_down_name'] = speed_down_name

    
    """     for onu, olt_name, onu_type_name, speed_profile_name, port_desc in db_onu:
        print(olt_name, onu_type_name, speed_profile_name, port_desc ) """
    return IResponseBase[OnuResponse](response=response)


@router.get("/get_onu_signal/{ext_id}", response_model = IResponseBase[OnuSignals] )
def get_onu_signals(ext_id: int,  db_session: Session = Depends(get_db)) -> dict:
    """
    Retorna la potencia óptica de la ONU
    """
    response = onu_crud.get_onu_signals_by_ext_id(ext_id, db_session)

    time.sleep(5)


    return IResponseBase[OnuSignals](response=response)
