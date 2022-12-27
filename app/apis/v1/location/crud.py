"""
CRUD para la gestión de Regiones
"""
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.models.location import Region, Zone, Nap


#######################################################################################
# CRUD PARA GESTION DE REGIONES
#######################################################################################

def get_region(db_session: Session, region_id: int) -> Region:
    """Retorna Region desde la base de datos en base al ID

    Args:
        db_session (Session): Sesión de la base de datos
        region_id (int): ID de region

    Returns:
        Region: Objeto Region desde la base de datos
    """

    return db_session.query(Region).filter(Region.id == region_id).first()


def get_region_by_name(db_session: Session, name: str) -> Region:
    """Retorna Region desde la base de datos en base al nombre de region

    Args:
        db_session (Session): Sesión de la base de datos
        nombre (str): Nombre registrada de region

    Returns:
        Region: Objeto Region desde la base de datos
    """

    return db_session.query(Region).filter(Region.name == name).first()


# Devuelve todos los agentes
def get_regions(db_session: Session) -> List[Region]:
    """Retorna todos las regiones registradas desde la base de datos

    Args:
        db_session (Session): Sesión de la base de datos


    Returns:
        List[Region]: Lista de Regiones registrados en la base de datos
    """

    return db_session.query(Region).all()



def create_region(db_session: Session, region: Region) -> Region:
    """Gestión de creación de un nuevo agente en la base de datos

    Args:
        db_session (Session): Sesión de la base de datos
        region (Region): Region

    Returns:
        Region: Objeto Region desde la base de datos
    """

    db_region = Region(
        name = region.name,
        description = region.description,
    )
    db_session.add(db_region)
    db_session.commit()

    return db_region


# Revisar proceso....
def delete_region(db_session: Session, region: Region) -> None:
    """Elimina un agente desde un objeto Agente entregado

    Args:
        db_session (Session): Sesión de la base de datos
        region (Region): Objeto Region
    """
    db_region = get_region(db_session, region.id)
    db_session.delete(db_region)

    db_session.commit()


def update_region(db_session: Session, current_region: Region, new_region: Region) -> Region:
    """Actualiza un Agente desde un Objeto agente provisto

    Args:
        db_session (Session): Sesión de la base de datos
        current_region (Region): Objeto Region a editar
        new_region (Region): Objeto Region con los cambios a aplicar

    Returns:
        Region: Region editado
    """

    current_region.name = new_region.name
    current_region.description = new_region.description

    db_session.commit()
    db_session.refresh(current_region)

    return current_region

#######################################################################################
# CRUD PARA GESTION DE ZONAS
#######################################################################################


def get_zone(db_session: Session, zone_id: int) -> Zone:
    """Retorna Region desde la base de datos en base al ID

    Args:
        db_session (Session): Sesión de la base de datos
        zone_id (int): ID de zona

    Returns:
        Zone: Objeto Zone desde la base de datos
    """

    return db_session.query(Zone).filter(Zone.id == zone_id).first()


def get_zone_by_name(db_session: Session, name: str) -> Zone:
    """Retorna Zone desde la base de datos en base al nombre de zona

    Args:
        db_session (Session): Sesión de la base de datos
        nombre (str): Nombre registrada de zona

    Returns:
        Zone: Objeto Zone desde la base de datos
    """

    return db_session.query(Zone).filter(Zone.name == name).first()


# Devuelve todos los agentes
def get_zones(db_session: Session) -> List[Zone]:
    """Retorna todos las zonas registradas desde la base de datos

    Args:
        db_session (Session): Sesión de la base de datos


    Returns:
        List[Zone]: Lista de Zonas registradoas en la base de datos
    """

    return db_session.query(Zone).all()


# Devuelve todos los agentes
def get_zones_by_region_id(region_id: int, db_session: Session) -> List[Zone]:
    """Retorna todos las zonas registradas desde la base de datos relacionadas a una región

    Args:
        region_id: ID de región de búsquda
        db_session (Session): Sesión de la base de datos


    Returns:
        List[Zone]: Lista de Zonas registradoas en la base de datos
    """

    return db_session.query(Zone).filter(Zone.region_id == region_id).all()



def create_zone(db_session: Session, region_id: int, zone: Zone) -> Zone:
    """Gestión de creación de un nuevo agente en la base de datos

    Args:
        db_session (Session): Sesión de la base de datos
        zone (Zone): Zone

    Returns:
        Zone: Objeto Zone desde la base de datos
    """

    db_zone = Zone(
        region_id = region_id,
        name = zone.name,
        description = zone.description,
    )
    db_session.add(db_zone)
    db_session.commit()

    return db_zone


def create_zones(zone: List[Zone], db: Session) -> bool:

    zones = []
    for o_zone in zone:
        print(o_zone)
        zones.append(Zone(**dict(o_zone)))

    try:
        db.bulk_save_objects(zones)
        db.commit()
        return True

    except IntegrityError:
        return False



# Revisar proceso....
def delete_zone(db_session: Session, zone: Zone) -> None:
    """Elimina una zona desde un objeto Zone entregado

    Args:
        db_session (Session): Sesión de la base de datos
        zone (Zone): Objeto Zone
    """
    db_zone = get_zone(db_session, zone.id)
    db_session.delete(db_zone)

    db_session.commit()


def update_zone(db_session: Session, current_zone: Zone, new_zone: Zone) -> Zone:
    """Actualiza una zona desde un Objeto zona provisto

    Args:
        db_session (Session): Sesión de la base de datos
        current_zone (Zone): Objeto Zona a editar
        new_zone (Zone): Objeto Zona con los cambios a aplicar

    Returns:
        Zone: Zona editada
    """
    
    current_zone.region_id = new_zone.region_id
    current_zone.name = new_zone.name
    current_zone.description = new_zone.description

    db_session.commit()
    db_session.refresh(current_zone)

    return current_zone


#######################################################################################
# CRUD PARA GESTION DE NAPS
#######################################################################################


def get_nap(db_session: Session, nap_id: int) -> Nap:
    """Retorna Nap desde la base de datos en base al ID

    Args:
        db_session (Session): Sesión de la base de datos
        nap_id (int): ID de nap

    Returns:
        Nap: Objeto Nap desde la base de datos
    """

    return db_session.query(Nap).filter(Nap.id == nap_id).first()


def get_nap_by_name(db_session: Session, name: str) -> Nap:
    """Retorna Nap desde la base de datos en base al nombre de la nap

    Args:
        db_session (Session): Sesión de la base de datos
        nombre (str): Nombre registrada de nap

    Returns:
        Nap: Objeto Nap desde la base de datos
    """

    return db_session.query(Nap).filter(Nap.name == name).first()


# Devuelve todos los agentes
def get_naps(db_session: Session) -> List[Nap]:
    """Retorna todos las naps registradas desde la base de datos

    Args:
        db_session (Session): Sesión de la base de datos


    Returns:
        List[Nap]: Lista de Naps registradoas en la base de datos
    """

    return db_session.query(Nap).all()


def get_naps_by_region_id(region_id: int, db_session: Session) -> List[Nap]:
    """Retorna todos las naps registradas desde la base de datos relacionadas a una región

    Args:
        region_id: ID de región de búsquda
        db_session (Session): Sesión de la base de datos


    Returns:
        List[Nap]: Lista de Naps registradoas en la base de datos
    """

    return db_session.query(Nap).filter(Nap.region_id == region_id).all()


def get_naps_by_zone_id(zone_id: int, db_session: Session) -> List[Nap]:
    """Retorna todos las naps registradas desde la base de datos relacionadas a una zona

    Args:
        zone_id: ID de zona de búsquda
        db_session (Session): Sesión de la base de datos


    Returns:
        List[Nap]: Lista de Naps registradoas en la base de datos
    """

    return db_session.query(Nap).filter(Nap.zone_id == zone_id).all()
    

def create_nap(db_session: Session, zone_id: int, nap: Nap) -> Nap:
    """Gestión de creación de un nuevo agente en la base de datos

    Args:
        db_session (Session): Sesión de la base de datos
        nap (Nap): Nap

    Returns:
        Nap: Objeto Nap desde la base de datos
    """

    db_nap = Nap(
        zone_id = zone_id,
        name = nap.name,
        ports = nap.ports,
        lat = nap.lat,
        long = nap.long,
        description = nap.description,
    )
    db_session.add(db_nap)
    db_session.commit()

    return db_nap


def create_naps(nap: List[Nap], db: Session) -> bool:

    naps = []
    for o_nap in nap:
        naps.append(Nap(**dict(o_nap)))

    try:
        db.bulk_save_objects(naps)
        db.commit()
        return True

    except IntegrityError as err:
        print(err)
        return False

# Revisar proceso....
def delete_nap(db_session: Session, nap: Nap) -> None:
    """Elimina una nap desde un objeto Nap entregado

    Args:
        db_session (Session): Sesión de la base de datos
        nap (Nap): Objeto Nap
    """
    db_nap = get_zone(db_session, nap.id)
    db_session.delete(db_nap)

    db_session.commit()


def update_nap(db_session: Session, current_nap: Nap, new_nap: Nap) -> Nap:
    """Actualiza una zona desde un Objeto zona provisto

    Args:
        db_session (Session): Sesión de la base de datos
        current_nap (Nap): Objeto Nap a editar
        new_znap (Nap): Objeto ZNapna con los cambios a aplicar

    Returns:
        Nap: Nap editada
    """
    
    current_nap.zone_id = new_nap.zone_id
    current_nap.name = new_nap.name
    current_nap.ports = new_nap.ports
    current_nap.lat = new_nap.lat
    current_nap.long = new_nap.long
    current_nap.description = new_nap.description

    db_session.commit()
    db_session.refresh(current_nap)

    return current_nap
