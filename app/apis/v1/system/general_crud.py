from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.core.models.system import OnuType, SpeedProfileUp, SpeedProfileDown

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


def add_speed_profiles_up(profile: List[SpeedProfileUp], db: Session) -> bool:

    profiles = []
    for s_profile in profile:
        speed_profile = SpeedProfileUp(**dict(s_profile))
        profiles.append(speed_profile)

    try:
        db.bulk_save_objects(profiles)
        db.commit()
        return True
    except IntegrityError:
        # Nombres de tipo de onus duplicados
        return False

def add_speed_profiles_down(profile: List[SpeedProfileDown], db: Session) -> bool:

    profiles = []
    for s_profile in profile:
        speed_profile = SpeedProfileDown(**dict(s_profile))
        profiles.append(speed_profile)

    try:
        db.bulk_save_objects(profiles)
        db.commit()
        return True
    except IntegrityError:
        # Nombres de tipo de onus duplicados
        return False


def get_speed_profiles_up(db: Session) -> List[SpeedProfileUp]:

    db_speed_profiles = db.query(SpeedProfileUp).all()
    return db_speed_profiles


def get_speed_profiles_down(db: Session) -> List[SpeedProfileDown]:

    db_speed_profiles = db.query(SpeedProfileDown).all()
    return db_speed_profiles