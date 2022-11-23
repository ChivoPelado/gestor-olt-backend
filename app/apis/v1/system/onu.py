from fastapi import APIRouter
from app.core.schemas.system import OltCreate, Onu
from app.celery_task.tasks import get_onu_signal_level


router = APIRouter()

@router.get("/sys/onu/get_onu_signal/")
def get_onu_signal() -> dict:
    """
    Retorna la potencia óptica de la ONU
    """

    #Obtener la instancia de la OLT (Mock) 
    # Se remueven datos por seguridad -- Actualizar
    olt = OltCreate(
        name="ZTE",
        ip_address="x.x.x.x", 
        ssh_port="223",
        ssh_user="xxx",
        ssh_password="223",
        snmp_port=2162,
        snmp_read_com="xxx",
        snmp_write_com="",
        hardware_ver="ZTE",
        software_ver="2.0"
    )

    # Obtener ONU desde la db (Mock)
    onu3 = Onu(olt=olt, sn='DC60B3D13497', shelf=1, slot=6, port=8, index=39)

    task = get_onu_signal_level.apply_async(args=[onu3])
    res = task.get(disable_sync_subtasks=False)

    return res

