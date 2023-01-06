from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.core.models.system import OnuType, SpeedProfileUp, SpeedProfileDown, Onu

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


def get_total_catv_onus(db: Session) -> int:

    response = {}
    total_onus = db.query(Onu).count()
    disabled_onus = db.query(Onu).filter(Onu.admin_status == "Disabled").count()
    critical_signal = db.query(Onu).filter(Onu.signal == "Critical").count()
    warning_signal = db.query(Onu).filter(Onu.signal == "Warning").count()
    good_signal = db.query(Onu).filter(Onu.signal == "Very good").count()
    total_tv = db.query(Onu).filter(Onu.catv != "Not supported by ONU-Type").count()
    tv_off = db.query(Onu).filter(Onu.catv == "Disabled").count()

    total_doble_pack = db.query(Onu).filter(Onu.catv != "Not supported by ONU-Type", Onu.download_speed != "_Cable_Familia_1M").count()
    total_solo_internet = db.query(Onu).filter(Onu.catv == "Not supported by ONU-Type").count()
    total_solo_tv = db.query(Onu).filter(Onu.catv != "Not supported by ONU-Type", Onu.download_speed == "_Cable_Familia_1M").count()

    mb_10 = db.query(Onu.download_speed).filter(Onu.download_speed == "10M").count()
    mb_20 = db.query(Onu.download_speed).filter(Onu.download_speed == "20M").count()
    mb_40 = db.query(Onu.download_speed).filter(Onu.download_speed == "40M").count()
    mb_50 = db.query(Onu.download_speed).filter(Onu.download_speed == "50M").count()
    mb_60 = db.query(Onu.download_speed).filter(Onu.download_speed == "60M").count()
    mb_70 = db.query(Onu.download_speed).filter(Onu.download_speed == "70M").count()
    mb_80 = db.query(Onu.download_speed).filter(Onu.download_speed == "80M").count()
    mb_100 = db.query(Onu.download_speed).filter(Onu.download_speed == "100M").count()

    response['total_onus'] = total_onus
    response['disabled_onus'] = disabled_onus
    response['total_tv'] = total_tv
    response['tv_off'] = tv_off
    response['critical_signal'] = critical_signal
    response['warning_signal'] = warning_signal
    response['good_signal'] = good_signal
    response['total_doble_pack'] = total_doble_pack
    response['total_solo_internet'] = total_solo_internet
    response['total_solo_tv'] = total_solo_tv
    response['mb_20'] = mb_20
    response['services_chart'] = {
        'labels': ['Internet', 'TV', 'Doblepack'],
        'datasets': [
          {
            'data': [total_solo_internet, total_solo_tv, total_doble_pack],
            'backgroundColor': [
              '#FF6384',
              '#36A2EB',
              '#FFCE56'
            ],
            'hoverBackgroundColor': [
              '#FF6384',
              '#36A2EB',
              '#FFCE56'
            ]
          }
        ]
      }
    response['bw_chart'] = {
        'labels': ['10 Mbps','20 Mbps', '40 Mbps', '50 Mbps', '60 Mbps', '70 Mbps', '80 Mbps', '100 Mbps'],
        'datasets': [
          {
            'label': 'Clientes',
            'backgroundColor': '#00bb7e',
            'data': [mb_10, mb_20, mb_40, mb_50, mb_60, mb_70, mb_80, mb_100]
          }
        ]
      }



     
    return response