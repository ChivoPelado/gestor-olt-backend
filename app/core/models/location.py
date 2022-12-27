"""
Definición del modelo de Localizaión
"""
from app.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, select, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.models.system import Onu


class Region(Base):
    __tablename__ = "region"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

    zones = relationship("Zone", backref="region", cascade="all,delete")
    naps = relationship("Nap", backref="region", cascade="all,delete")
    onus = relationship("Onu", backref="region")

    
class Zone(Base):
    __tablename__ = "zone"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("region.id"))
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

    naps = relationship("Nap", backref="zone", cascade="all,delete")


class Nap(Base):
    __tablename__ = "nap"
    
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("region.id"))
    zone_id = Column(Integer, ForeignKey("zone.id"))
    name = Column(String, unique=True, nullable=False)
    ports = Column(Integer, nullable=False, default=16)
    latitude = Column(Float)
    longitude = Column(Float)
    description = Column(Text)

    onus = relationship("Onu", backref="nap")

    @hybrid_property
    def online_onu_count(self):
        """Retorna la cantidad de ONUs en estado Online"""
        return sum(onu.status == "En Línea" for onu in self.onus)

    @online_onu_count.expression
    def online_onu_count(self, cls):
        """Retorna la cantidad de ONUs en estado Online en expresion SQL"""
        return select(func.count(1).filter(Onu.status == "En Línea")). \
            where(Onu.port_id == cls.id). \
            label('online_onu_count')