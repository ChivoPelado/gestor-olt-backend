from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.apis.v1.system import olt_crud
from app.core.schemas.system import OltCreate, OltResponse, PortResponse, CardResponse
from app.core.models.system import Card, Port, Olt
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
    new_olt = await olt_crud.create_olt(db, olt=olt)
    return IResponseBase[OltResponse](response=new_olt)

@router.get("/olt/get_cards/{olt_id}")
async def get_olt_cards_detail(olt_id:int, db: Session = Depends(get_db)): 
    olt = db.query(Olt).filter(Olt.id == olt_id).first()
    return olt.cards
    # db.add(Port(**dict(port)))
    # db.commit()

@router.get("/olt/get_ports/{olt_id}", response_model=list[CardResponse])
async def get_olt_port_detail(olt_id:int, db: Session = Depends(get_db)): 

    db_card = db.query(Card).join(Port).join(Olt).filter(Olt.id == olt_id).all()

    for card in db_card:
        for port in card.ports:
          print(port.online_onu_count)

    return db_card


   
    """ 
    @router.post("/olt/port")
    async def create_olt(port: PortCreate, db: Session = Depends(get_db)): 
        db.add(Port(**dict(port)))
        db.commit() """

    #return db_port


    """
        cards = []

    for card in db_card:
        cards_details = {
            "slot": card.slot,
            "cfg_type": card.cfg_type,
            "ports": []
        }
        cards.append(cards_details)

        for port in card.ports:
            ports_details = {
                "port_no": port.port_no,
                "pon_type": port.pon_type
            }
            cards_details["ports"].append(ports_details)
    """