"""
Parametrización de características generales**
"""
from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from app.database import get_db
from app.apis.v1.system import general_crud
from app.core.schemas.system import (
    OnuTypeCreate, OnuTypeResponseList,
    SpeedProfileCreate, SpeedProfileResponseList
    )
from app.core.schemas.generic import IResponseBase


router = APIRouter()


@router.get("/onu_types", response_model=IResponseBase[OnuTypeResponseList])
async def get_onu_types(db: Session = Depends(get_db)): 
    db_onu_types = general_crud.get_onu_types(db=db)
    response = {"data": db_onu_types}
    return IResponseBase[OnuTypeResponseList](response=response)


@router.post("/onu_types",)
async def add_onu_types(onu_type: List[OnuTypeCreate], db: Session = Depends(get_db)): 
    db_onu_types = general_crud.add_onu_types(onu_types=onu_type, db=db)
    if db_onu_types:
        return IResponseBase[str](response='Tipos de onu agregados satisfactoriamente' )
    return IResponseBase[str](response='Existió un error al agregar tipos de onus' )


@router.get("/speed_profiles", response_model=IResponseBase[SpeedProfileResponseList])
async def get_speed_profiles(direction: str = "all", db: Session = Depends(get_db)): 
    db_speed_profiles = general_crud.get_speed_profiles(direction=direction, db=db)
    response = {"data": db_speed_profiles}
    return IResponseBase[SpeedProfileResponseList](response=response)



@router.post("/speed_profiles",)
async def add_speed_profiles(speed_profile: List[SpeedProfileCreate], db: Session = Depends(get_db)): 
    db_onu_types = general_crud.add_speed_profiles(profile=speed_profile, db=db)
    if db_onu_types:
        return IResponseBase[str](response='Tipos de onu agregados satisfactoriamente' )
    return IResponseBase[str](response='Existió un error al agregar tipos de onus' )