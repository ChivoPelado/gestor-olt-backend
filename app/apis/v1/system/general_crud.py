from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.core.models.system import OnuType, SpeedProfile


def add_onu_types(onu_types: List[OnuType], db: Session) -> bool:

    types = []
    for o_type in onu_types:
        onu_type = OnuType(**dict(o_type))
        types.append(onu_type)

    try:
        db.bulk_save_objects(types)
        db.commit()
        return True
    except IntegrityError:
        # Nombres de tipo de onus duplicados
        return False

def get_onu_types(db: Session) -> List[OnuType]:
    db_onu_types = db.query(OnuType).all()
    return db_onu_types


def add_speed_profiles(profile: List[SpeedProfile], db: Session) -> bool:

    profiles = []
    for s_profile in profile:
        speed_profile = SpeedProfile(**dict(s_profile))
        profiles.append(speed_profile)

    try:
        db.bulk_save_objects(profiles)
        db.commit()
        return True
    except IntegrityError:
        # Nombres de tipo de onus duplicados
        return False


def get_speed_profiles(direction: str, db: Session) -> List[SpeedProfile]:
    if direction == "all" or direction == None:
        db_speed_profiles = db.query(SpeedProfile).all()
    elif direction == "upload":
        db_speed_profiles = db.query(SpeedProfile).filter(SpeedProfile.direction == "upload").all()
    elif direction == "download":
        db_speed_profiles = db.query(SpeedProfile).filter(SpeedProfile.direction == "download").all()
    else:
        db_speed_profiles = []
    return db_speed_profiles
