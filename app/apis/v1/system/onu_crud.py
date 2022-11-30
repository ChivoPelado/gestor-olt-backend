
from sqlalchemy.orm import Session
from app.core.models.system import Olt, Onu

# Autoriza una nueva onu (Mock)
def authorize_onu(db: Session, onu: Onu) -> Onu:
    auth_onu = Onu(
        ext_id = onu.ext_id,
        olt_id = onu.olt_id,
        port_id = onu.port_id,
        pon_type = onu.pon_type,
        shelf = onu.shelf,
        slot = onu.slot,
        port_no = onu.port_no,
        index = onu.index,
        serial_no = onu.serial_no,
        vlan = onu.vlan,
        name = str(onu.name).replace(" ", "_"),
        status = onu.status,
        signal = onu.signal,
        comment = str(onu.comment).replace(" ", "_"),
        onu_mode = onu.onu_mode,
    )
    db.add(auth_onu)
    db.commit()
    db.refresh(auth_onu) 
    return auth_onu
