"""
APIs, para la gestión de Localización (Regiones, zonas y naps)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.schemas.location import (
    RegionCreate, RegionResponse, ZoneCreate, ZoneResponse, NapCreate, NapResponse
) 
from app.core.schemas.generic import IResponseBase
from app.database import get_db
from typing import List
from . import crud


router = APIRouter()

#######################################################################################
# RUTAS PARA GESTION DE REGIONES
#######################################################################################

@router.post("/region",  response_model=IResponseBase[RegionResponse])
async def create_region(region: RegionCreate, db_session: Session = Depends(get_db)):
    """
    Agrega una Región al sistema:
    """

    db_region = crud.get_region_by_name(db_session, region.name)
    if db_region:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Región existe")
    new_region = crud.create_region(db_session, region=region)
    return IResponseBase[RegionResponse](response=new_region)


@router.get("/region/{region_id}", response_model=IResponseBase[RegionResponse])
async def read_region(region_id: int, db_session: Session = Depends(get_db)):
    """API para la lectura de region a partir del ID"""

    db_region = crud.get_region(db_session, agent_id=region_id)
    if db_region is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Region no encontrada")
    return IResponseBase[RegionResponse](response=db_region)


@router.get("/region/get_regions/", response_model=IResponseBase[List[RegionResponse]])
async def list_regions(db_session: Session = Depends(get_db)):
    """API para la lectura de  todas las regiones"""

    db_regions = crud.get_regions(db_session)

    return IResponseBase[List[RegionResponse]](response=list(db_regions))


@router.put("/region/{region_id}", response_model=IResponseBase[RegionResponse])
async def edit_region(region_id: int, new_region: RegionCreate, db_session: Session = Depends(get_db)):
    """API para la edición de  región por ID"""

    db_region = crud.get_region(db_session, region_id=region_id)
    if db_region is None:
        raise HTTPException(status_code=404, detail="Region no encontrada")
    updated_region = crud.update_region(db_session, current_region=db_region, new_region=new_region)
    return IResponseBase[RegionResponse](response=updated_region)


@router.delete("/region/{region_id}", response_model=IResponseBase[str])
async def delete_region(region_id: int, db_session: Session = Depends(get_db)):
    """API para la eliminación de región por ID"""

    db_region = crud.get_region(db_session, region_id=region_id)
    if db_region is None:
        raise HTTPException(status_code=404, detail="Región no encontrada")

    crud.delete_region(db_session, db_region)
    return  IResponseBase[str](response="Region eliminada satisfactoriamente")


#######################################################################################
# RUTAS PARA GESTION DE ZONAS
#######################################################################################

@router.post("/zone",  response_model=IResponseBase[ZoneResponse])
async def create_zone(zone: ZoneCreate, db_session: Session = Depends(get_db)):
    """
    Agrega una Zona al sistema:
    """

    db_zone = crud.get_zone_by_name(db_session, zone.name)
    if db_zone:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Zona existe")
    new_zone = crud.create_zone(db_session, zone=zone)
    return IResponseBase[ZoneResponse](response=new_zone)


@router.post("/zones",)
async def add_zones(zone: List[ZoneCreate], db: Session = Depends(get_db)): 
    db_zones = crud.create_zones(zone=zone, db=db)
    if db_zones:
        return IResponseBase[str](response='Zonas agregados satisfactoriamente' )
    return IResponseBase[str](response='Existió un error al agregar zonas' )


@router.get("/zone/{zone_id}", response_model=IResponseBase[ZoneResponse])
async def read_zone(zone_id: int, db_session: Session = Depends(get_db)):
    """API para la lectura de zona a partir del ID"""

    db_zone = crud.get_zone(db_session, zone_id=zone_id)
    if db_zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zona no encontrada")
    return IResponseBase[ZoneResponse](response=db_zone)


@router.get("/zone/get_zones/", response_model=IResponseBase[List[ZoneResponse]])
async def list_zones(db_session: Session = Depends(get_db)):
    """API para la lectura de  todas las zonas"""

    db_zones = crud.get_zones(db_session)

    return IResponseBase[List[ZoneResponse]](response=list(db_zones))


@router.get("/zone/get_zones/{region_id}", response_model=IResponseBase[List[ZoneResponse]])
async def list_zones_by_region_id(region_id: int, db_session: Session = Depends(get_db)):
    """API para la lectura de  todas las zonas reñacionadas a una región"""

    db_zones = crud.get_zones_by_region_id(region_id, db_session)

    return IResponseBase[List[ZoneResponse]](response=list(db_zones))


@router.put("/zone/{zone_id}", response_model=IResponseBase[ZoneResponse])
async def edit_zone(zone_id: int, new_zone: ZoneCreate, db_session: Session = Depends(get_db)):
    """API para la edición de  agente por ID"""

    db_zone = crud.get_zone(db_session, zone_id=zone_id)
    if db_zone is None:
        raise HTTPException(status_code=404, detail="Region no encontrada")
    updated_zone = crud.update_zone(db_session, current_zone=db_zone, new_zone=new_zone)
    return IResponseBase[ZoneResponse](response=updated_zone)


@router.delete("/zone/{zone_id}", response_model=IResponseBase[str])
async def delete_zone(zone_id: int, db_session: Session = Depends(get_db)):
    """API para la eliminación de zona por ID"""

    db_zone = crud.get_zone(db_session, zone_id=zone_id)
    if db_zone is None:
        raise HTTPException(status_code=404, detail="Zona no encontrada")

    crud.delete_zone(db_session, db_zone)
    return  IResponseBase[str](response="Zona eliminada satisfactoriamente")


#######################################################################################
# RUTAS PARA GESTION DE NAPS
#######################################################################################


@router.post("/nap",  response_model=IResponseBase[NapResponse])
async def create_nap(nap: NapCreate, db_session: Session = Depends(get_db)):
    """
    Agrega una Nap al sistema:
    """

    db_nap = crud.get_zone_by_name(db_session, nap.name)
    if db_nap:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nap existe")
    new_nap = crud.create_nap(db_session, nap=nap)
    return IResponseBase[NapResponse](response=new_nap)


@router.get("/nap/{nap_id}", response_model=IResponseBase[NapResponse])
async def read_nap(nap_id: int, db_session: Session = Depends(get_db)):
    """API para la lectura de nap a partir del ID"""

    db_zone = crud.get_nap(db_session, nap_id=nap_id)
    if db_zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nap no encontrada")
    return IResponseBase[NapResponse](response=db_zone)


@router.post("/naps",)
async def add_naps(nap: List[NapCreate], db: Session = Depends(get_db)): 
    db_naps = crud.create_naps(nap=nap, db=db)
    if db_naps:
        return IResponseBase[str](response='NAPs agregadss satisfactoriamente' )
    return IResponseBase[str](response='Existió un error al agregar NAPs' )


@router.get("/nap/get_naps/", response_model=IResponseBase[List[NapResponse]])
async def list_naps(db_session: Session = Depends(get_db)):
    """API para la lectura de  todas las naps"""

    db_naps = crud.get_naps(db_session)

    return IResponseBase[List[NapResponse]](response=list(db_naps))


@router.get("/nap/get_naps/by_region/{region_id}", response_model=IResponseBase[List[NapResponse]])
async def list_naps_by_region_id(region_id: int, db_session: Session = Depends(get_db)):
    """API para la lectura de  todas las zonas relacionadas a una región"""

    db_naps = crud.get_naps_by_region_id(region_id, db_session)

    return IResponseBase[List[NapResponse]](response=list(db_naps))


@router.get("/nap/get_naps/by_zone/{zone_id}", response_model=IResponseBase[List[NapResponse]])
async def list_naps_by_zone_id(zone_id: int, db_session: Session = Depends(get_db)):
    """API para la lectura de  todas las zonas relacionadas a una zona"""

    db_naps = crud.get_naps_by_zone_id(zone_id, db_session)

    return IResponseBase[List[NapResponse]](response=list(db_naps))


@router.put("/nap/{nap_id}", response_model=IResponseBase[NapResponse])
async def edit_nap(nap_id: int, new_nap: NapCreate, db_session: Session = Depends(get_db)):
    """API para la edición de  Nap por ID"""

    db_nap = crud.get_zone(db_session, zone_id=nap_id)
    if db_nap is None:
        raise HTTPException(status_code=404, detail="Nap no encontrada")
    updated_nap = crud.update_region(db_session, current_nap=db_nap, new_nap=new_nap)
    return IResponseBase[NapResponse](response=updated_nap)


@router.delete("/nap/{nap_id}", response_model=IResponseBase[str])
async def delete_nap(nap_id: int, db_session: Session = Depends(get_db)):
    """API para la eliminación de Nap por ID"""

    db_nap = crud.get_nap(db_session, nap_id=nap_id)
    if db_nap is None:
        raise HTTPException(status_code=404, detail="Zona no encontrada")

    crud.delete_nap(db_session, db_nap)
    return  IResponseBase[str](response="Nap eliminada satisfactoriamente")