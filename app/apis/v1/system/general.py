"""
Parametrización de características generales**
"""
from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from app.database import get_db
from app.apis.v1.system import general_crud
from app.core.schemas.system import (
    OnuTypeCreate, OnuTypeResponse,
    SpeedProfileCreate, SpeedProfileResponse
    )
from app.core.schemas.generic import IResponseBase


router = APIRouter()


@router.get("/onu_types", response_model=IResponseBase[List[OnuTypeResponse]])
async def get_onu_types(db: Session = Depends(get_db)): 
    db_onu_types = general_crud.get_onu_types(db=db)
    # response = {"data": db_onu_types}
    return IResponseBase[List[OnuTypeResponse]](response=list(db_onu_types))


@router.post("/onu_types",)
async def add_onu_types(onu_type: List[OnuTypeCreate], db: Session = Depends(get_db)): 
    db_onu_types = general_crud.add_onu_types(onu_types=onu_type, db=db)
    if db_onu_types:
        return IResponseBase[str](response='Tipos de onu agregados satisfactoriamente' )
    return IResponseBase[str](response='Existió un error al agregar tipos de onus' )



@router.get("/speed_profiles", response_model=IResponseBase[List[SpeedProfileResponse]])
async def get_speed_profiles(direction: str = "all", db: Session = Depends(get_db)): 
    
    db_speed_profiles = []
    if direction == "download":
        db_speed_profiles = general_crud.get_speed_profiles_down(db=db)
    elif direction == "upload":
        db_speed_profiles = general_crud.get_speed_profiles_up(db=db)
    elif direction == "all":
        db_speed_profiles_up = general_crud.get_speed_profiles_down(db=db)
        db_speed_profiles_down = general_crud.get_speed_profiles_up(db=db)
        db_speed_profiles = db_speed_profiles_up + db_speed_profiles_down
    return IResponseBase[List[SpeedProfileResponse]](response=list(db_speed_profiles))


@router.post("/speed_profiles/down",)
async def add_speed_profiles(speed_profile: List[SpeedProfileCreate], db: Session = Depends(get_db)): 
    db_onu_types = general_crud.add_speed_profiles_down(profile=speed_profile, db=db)
    if db_onu_types:
        return IResponseBase[str](response='Perfiles de velocidad de bajada agregados correctamente' )
    return IResponseBase[str](response='Existió un error al agregar perfil de velocidad' )


@router.post("/speed_profiles/up",)
async def add_speed_profiles(speed_profile: List[SpeedProfileCreate], db: Session = Depends(get_db)): 
    db_onu_types = general_crud.add_speed_profiles_up(profile=speed_profile, db=db)
    if db_onu_types:
        return IResponseBase[str](response='Perfiles de velocidad de subida agregados correctamente' )
    return IResponseBase[str](response='Existió un error al agregar perfil de velocidad' )


@router.get("/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    return general_crud.get_total_catv_onus(db)