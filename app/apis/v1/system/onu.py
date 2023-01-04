"""
APIs para la gestión de ONUs
"""
from fastapi import APIRouter, Request, HTTPException, status, Form, Depends
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
    req: Request,
    olt_id: int = Form(),
    slot: int = Form(),
    port: int = Form(),
    onu_sn: str = Form(), 
    onu_type: str = Form(),
    onu_mode: str = Form(),
    vlan: int = Form(),
    region: int = Form(),
    zone: int = Form(),
    nap: int = Form(),
    down_speed: str = Form(),
    up_speed: str = Form(),
    name: str = Form(),
    comment: str = Form(),
    onu_ext_id: int = Form(),
    db: Session = Depends(get_db),
    user = Depends(login_manager)): 
    
    authorized_onu = onu_crud.authorize_onu( olt_id, slot, port, onu_sn, onu_type, onu_mode, vlan,
       region, zone, nap, down_speed, up_speed, name, comment, onu_ext_id=onu_ext_id, db_session=db, user_id=user.id,
       user_ip = req.client.host)

    return authorized_onu #IResponseBase[OnuResponse](response=authorized_onu)


@router.get("/",  response_model=IResponseBase[OnuResponse])
async def authorize_onu(onu: OnuCreate, db: Session = Depends(get_db)): 
    authorized_onu = onu_crud.authorize_onu(db, onu=onu)
    return IResponseBase[OnuResponse](response=authorized_onu)


@router.get("/get_onu_by_ext_id/{external_id}",  response_model=IResponseBase[OnuResponse])
async def get_onu_by_ext_id(external_id: int, db: Session = Depends(get_db)): 
   
    if not db.query(Onu).filter(Onu.ext_id == external_id).first():
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ONU con id {external_id} no existe")

    response = {}
    db_onu, olt_name, onu_type, speed_up_name, speed_down_name = db.query(
        Onu, Olt.name, OnuType, SpeedProfileUp.name, SpeedProfileDown.name) \
        .join(Olt) \
        .join(OnuType) \
        .join(Port) \
        .join(SpeedProfileUp) \
        .join(SpeedProfileDown) \
        .filter(Onu.ext_id == external_id).first()
    
    if not db_onu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ONU con id {external_id} no existe")

    response = db_onu.__dict__.copy()
    response['olt_name'] = olt_name
    response['onu_type_name'] = onu_type.name
    response['upload_speed'] = speed_up_name.lstrip("SMARTOLT-").rstrip("-UP")
    response['download_speed'] = speed_down_name.lstrip("SMARTOLT-").rstrip("-DOWN")
    response['interface'] = db_onu.interface
    response['onu_type'] = onu_type

    
    """     for onu, olt_name, onu_type_name, speed_profile_name, port_desc in db_onu:
        print(olt_name, onu_type_name, speed_profile_name, port_desc ) """
    return IResponseBase[OnuResponse](response=response)


@router.get("/get_onu_signal/{ext_id}", response_model = IResponseBase[OnuSignals] )
def get_onu_signals(ext_id: int,  db_session: Session = Depends(get_db)) -> dict:
    """
    Retorna la potencia óptica de la ONU
    """
    response = onu_crud.get_onu_signals_by_ext_id(ext_id, db_session)

    # time.sleep(5)


    return IResponseBase[OnuSignals](response=response)


@router.get("/get_all_onus/", response_model = IResponseBase[List[OnuResponse]] )
def get_all_onus( db_session: Session = Depends(get_db)) -> dict:
  
    db_onus = db_session.query(
        Onu, Olt.name, SpeedProfileDown.name, SpeedProfileUp.name, OnuType.name
        ) \
        .join(Olt) \
        .where(
            Onu.olt_id == Olt.id, 
            Onu.speed_profile_down_id == SpeedProfileDown.id,
            Onu.speed_profile_up_id == SpeedProfileUp.id,
            Onu.onu_type_id == OnuType.id
            ).all()

    response = []
    onu = {}
    for query in db_onus:
        onu = query[0].__dict__
        onu['olt_name'] = query[1]
        onu['download_speed'] = query[2].lstrip("SMARTOLT-").rstrip("-DOWN")
        onu['upload_speed'] = query[3].lstrip("SMARTOLT-").rstrip("-UP")
        onu['onu_type_name'] = query[4]
        onu['interface'] = query[0].interface

        response.append(onu)

    return IResponseBase[List[OnuResponse]](response=list(response))


@router.delete("/{ext_id}", response_model = IResponseBase[str] )
def delete_onu_by_ext_id(ext_id: int,  req: Request, db_session: Session = Depends(get_db), user = Depends(login_manager)) -> dict:
    """
    Elimina ONU en base al ID externo
    """
    response = onu_crud.delete_onu_by_ext_id(db_session=db_session, onu_ext_id=ext_id, user_id=user.id, user_ip=req.client.host)

    if response:
        return IResponseBase[str](response="ONT eliminada satisfactiriamente")

    return IResponseBase[str](status=False, response="Existió un error al eliminar ONT")



@router.post("/deactivate/{ext_id}", response_model = IResponseBase[str] )
def deactivate_onu_by_ext_id(ext_id: int,  req: Request, db_session: Session = Depends(get_db), user = Depends(login_manager)) -> dict:
    """
    Deshabilita ONU en base al ID externo
    """
    response = onu_crud.deactivate_onu_by_ext_id(db_session=db_session, onu_ext_id=ext_id, user_id=user.id, user_ip=req.client.host)

    if response:
        return IResponseBase[str](response="ONT desactivada correctamente")

    return IResponseBase[str](status=False, response="Existió un error al deshabilitar ONT")



@router.post("/activate/{ext_id}", response_model = IResponseBase[str] )
def activate_onu_by_ext_id(ext_id: int,  req: Request, db_session: Session = Depends(get_db), user = Depends(login_manager)) -> dict:
    """
    Habilita ONU en base al ID externo
    """
    response = onu_crud.activate_onu_by_ext_id(db_session=db_session, onu_ext_id=ext_id, user_id=user.id, user_ip=req.client.host)

    if response:
        return IResponseBase[str](response="ONT habilitada correctamente")

    return IResponseBase[str](status=False, response="Existió un error al habilitar ONT")



@router.post("/reboot/{ext_id}", response_model = IResponseBase[str] )
def reboot_onu_by_ext_id(ext_id: int,  req: Request, db_session: Session = Depends(get_db), user = Depends(login_manager)) -> dict:
    """
    Reinicia la ONU en base al ID externo
    """
    response = onu_crud.reboot_onu_by_ext_id(db_session=db_session, onu_ext_id=ext_id, user_id=user.id, user_ip=req.client.host)

    if response:
        return IResponseBase[str](response="ONT reiniciada correctamente")

    return IResponseBase[str](status=False, response="Existió un error al reiniciar ONT")


@router.post("/set_mode/{ext_id}", response_model = IResponseBase[str] )
def set_onu_mode_by_ext_id(ext_id: int,  req: Request, mode: str = Form(), db_session: Session = Depends(get_db), user = Depends(login_manager)) -> dict:
    """
    Reinicia la ONU en base al ID externo
    """
    response = onu_crud.set_onu_mode(db_session=db_session, onu_ext_id=ext_id, mode=mode, user_id=user.id, user_ip=req.client.host)

    if response:
        return IResponseBase[str](response="Modo de ONT cambiada correctamente a " + mode)

    return IResponseBase[str](status=False, response="Existió un error al cambiar modo de ONT")



@router.post("/enable_catv/{ext_id}", response_model = IResponseBase[str] )
def enable_catv_by_onu_ext_id(ext_id: int,  req: Request, db_session: Session = Depends(get_db), user = Depends(login_manager)) -> dict:
    """
    Activa puerto CATV de la ONU en base al ID externo
    """
    response = onu_crud.enable_onu_catv(db_session=db_session, onu_ext_id=ext_id, user_id=user.id, user_ip=req.client.host)

    if response:
        return IResponseBase[str](response="CATV activado correctamente")

    return IResponseBase[str](status=False, response="Existió un error al activar puerto CATV")


@router.post("/disable_catv/{ext_id}", response_model = IResponseBase[str] )
def disable_catv_by_onu_ext_id(ext_id: int,  req: Request, db_session: Session = Depends(get_db), user = Depends(login_manager)) -> dict:
    """
    Desactiva el puerto CATV de la ONU en base al ID externo
    """
    response = onu_crud.disable_onu_catv(db_session=db_session, onu_ext_id=ext_id, user_id=user.id, user_ip=req.client.host)

    if response:
        return IResponseBase[str](response="CATV desactivado correctamente")

    return IResponseBase[str](status=False, response="Existió un error al desactivar puerto CATV")



@router.post("/resync_config/{ext_id}", response_model = IResponseBase[str] )
def resync_config_onu_by_ext_id(ext_id: int,  req: Request, db_session: Session = Depends(get_db), user = Depends(login_manager)) -> dict:
    """
    Resincroniza la configuración de la ONT desde la base de datos
    """
    response = onu_crud.resync_onu(db_session=db_session, onu_ext_id=ext_id, user_id=user.id, user_ip=req.client.host)

    if response:
        return IResponseBase[str](response="ONT resincronizada correctamente")

    return IResponseBase[str](status=False, response="Existió un error al resincronizar ONT")


@router.get("/running_config/{ext_id}")
def resync_config_onu_by_ext_id(ext_id: int,  req: Request, db_session: Session = Depends(get_db), user = Depends(login_manager)) -> dict:
    """
    Resincroniza la configuración de la ONT desde la base de datos
    """
    response = onu_crud.get_onu_running_config(db_session=db_session, onu_ext_id=ext_id, user_id=user.id, user_ip=req.client.host)

    if response:
        return response

    return None