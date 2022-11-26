from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.apis.v1.system import olt_crud
from app.core.schemas.system import OltCreate, OltResponse, PortCreate, PortResponse
from app.core.models.system import Card, Port
from app.interface.commands import show_card
from app.core.schemas.generic import IResponseBase

router = APIRouter()


# Creación de Olt
@router.post("/olt/",  response_model=IResponseBase[OltResponse])
async def create_olt(olt: OltCreate, db: Session = Depends(get_db)): 
    """
    Agrega una OLT al sistema:

    - **name**: Nombre referencial para la OLT
    - **ip_address**: Dirección ip de administración de la OLT
    - **ssh_port**: Puerto SSH externo para acceso remoto
    - **ssh_user**: Nombre de usuario para protocolo SSH
    - **ssh_password**: Contraseña para protocolo SSH
    - **snmp_port**: Puerto SNMP externo para acceso remoto
    - **snmp_read_com**: Contraseña de comunidad de lectura de SNMP
    - **snmp_write_com**: Contraseña de escritura de SNMP
    - **hardware_ver**: Versión de hardware de la OLT
    - **software_ver**: Versión de software de la OLT
    \f
    :param olt: OltCreate Model.
    :param db: DataBase Session.
    """
    if not olt_crud.vlidate_used_ports(db=db, olt_ip=olt.ip_address, olt_ssh_port=olt.ssh_port, olt_snmp_port=olt.snmp_port):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="IP y puertos ingresados estan siendo utilizados por otra OLT"
            ) 
    new_olt = olt_crud.create_olt(db, olt=olt)
    return IResponseBase[OltResponse](response=new_olt)

@router.post("/olt/port")
async def create_olt(port: PortCreate, db: Session = Depends(get_db)): 
    db.add(Port(**dict(port)))
    db.commit()

    #return db_port