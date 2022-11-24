from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.apis.v1.system import olt_crud
from app.core.schemas.system import OltCreate, OltResponse
from app.interface.commands import show_card
from app.core.schemas.generic import IResponseBase

router = APIRouter()


# Creación de Olt
@router.post("/olt/",  response_model=IResponseBase[OltResponse])
async def create_olt(olt: OltCreate, db: Session = Depends(get_db)): 
    if not olt_crud.vlidate_used_ports(db=db, olt_ip=olt.ip_address, olt_ssh_port=olt.ssh_port, olt_snmp_port=olt.snmp_port):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="IP y puertos detallados estan siendo utilizados por otra OLT"
            ) 
    new_olt = olt_crud.create_olt(db, olt=olt)
    return IResponseBase[OltResponse](response=new_olt)

@router.get("/olt/get_card/")
def get_olt_card() -> dict:
    """
    Retorna información de las tarjetas de OLT
    """
    data: dict = {}
    data =  show_card.get_olt()
    return data
