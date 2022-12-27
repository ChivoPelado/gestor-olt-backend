"""
APIs para la gestión de OLT
"""
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.schemas.system import OltResponse, CardResponse, VlanResponse, CardPortResponse
from app.core.utils.security import login_manager
from app.core.models.system import Card, Port, Olt, Vlan
from app.core.schemas.generic import IResponseBase
from typing import List
from . import olt_crud
import time

router = APIRouter()


# Creación de Olt
@router.post("/", response_model=IResponseBase[OltResponse])
async def create_olt(name: str = Form(), ip_address: str = Form(), telnet_port: int = Form(), telnet_user: str = Form(), 
    telnet_password: str = Form(), snmp_port: int = Form(), snmp_read_com: str = Form(), snmp_write_com: str = Form(),
    hardware_ver: str = Form(), software_ver: str = Form(), db_session: Session = Depends(get_db)): 
    """
    Agrega una OLT al sistema:

    - **name**: Nombre referencial para la OLT
    - **ip_address**: Dirección ip de administración de la OLT
    - **telnet_port**: Puerto SSH externo para acceso remoto
    - **telnet_user**: Nombre de usuario para protocolo SSH
    - **telnet_password**: Contraseña para protocolo SSH
    - **snmp_port**: Puerto SNMP externo para acceso remoto
    - **snmp_read_com**: Contraseña de comunidad de lectura de SNMP
    - **snmp_write_com**: Contraseña de escritura de SNMP
    - **hardware_ver**: Versión de hardware de la OLT
    - **software_ver**: Versión de software de la OLT
    \f
    :param db: DataBase Session.
    """

    if not olt_crud.vlidate_used_ports(db_session=db_session, olt_ip=ip_address, telnet_port=telnet_port, snmp_port=snmp_port):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="IP y puertos ingresados estan siendo utilizados por otra OLT"
            ) 

    new_olt = await olt_crud.create_olt(
        name = name, ip_address = ip_address, telnet_port = telnet_port, telnet_user = telnet_user, 
        telnet_password = telnet_password, snmp_port =snmp_port, snmp_read_com = snmp_read_com, 
        snmp_write_com = snmp_write_com, hardware_ver = hardware_ver, software_ver = software_ver,
        db_session=db_session
        )

    """ new_olt = True
    print(hardware_ver, software_ver)
    time.sleep(10) """

    return IResponseBase[OltResponse](response=new_olt)


@router.get("/")
async def get_olts(db: Session = Depends(get_db), user = Depends(login_manager)): 
    olt = db.query(Olt).all()
    return olt
    # db.add(Port(**dict(port)))
    # db.commit()

@router.get("/{olt_id}", response_model=OltResponse)
async def get_olts(olt_id: int, db: Session = Depends(get_db)): 
    olt = db.query(Olt).filter(Olt.id == olt_id).first()
    return olt

@router.delete("/{olt_id}", response_model=IResponseBase[bool])
async def delete_olt_by_id(olt_id: int, db_session: Session = Depends(get_db), user = Depends(login_manager)): 
    response = olt_crud.delete_olt_by_id(olt_id, db_session)
    return IResponseBase[bool](response=response)



@router.get("/get_cards/{olt_id}")
async def get_olt_cards_detail(olt_id:int, db: Session = Depends(get_db)): 
    olt = db.query(Olt).filter(Olt.id == olt_id).first()
    return olt.cards
    # db.add(Port(**dict(port)))
    # db.commit()


@router.get("/get_ports/{olt_id}", response_model=List[CardPortResponse])
async def get_olt_port_detail(olt_id:int, db: Session = Depends(get_db)): 

    db_card = db.query(Card).join(Port).join(Olt).filter(Olt.id == olt_id).all()

    """ port_dict = {}
    cards = []
    ports = []
    for card in db_card:
        if card.role == "GPON":
            port_dict = {
                "id": card.id,
                "slot": card.slot,
                "type": card.role,
                "ports": [port for port in card.ports]
            }

            cards.append(port_dict) """

    return list(db_card)

   


@router.get("/get_vlans/{olt_id}", response_model=IResponseBase[List[VlanResponse]])
async def get_olt_vlans(olt_id:int, db: Session = Depends(get_db)): 

    db_vlan = olt_crud.get_olt_vlans(db, olt_id)
    return IResponseBase[List[VlanResponse]](response=db_vlan) 


@router.get("/test_point/{olt_id}")
async def test_point(olt_id:int, request: Request, db: Session = Depends(get_db)): 
    print(request.client.host)
    response = await olt_crud.test_point(db=db, olt_id=olt_id)
    return response
