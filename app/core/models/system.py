"""
Definición de los modelos de sistema (OLT, Card, Port, ONU)
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, select, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.database import Base

class Olt(Base):
    """
    Modelo OLT, Representa al equipo OLT
    """
    __tablename__ = "olt"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    host = Column(String, nullable=False)
    telnet_port = Column(Integer, nullable=False)
    telnet_user = Column(String, nullable=False)
    telnet_password = Column(String, nullable=False)
    snmp_port = Column(Integer, nullable=False)
    snmp_read_com = Column(String, nullable=False)
    snmp_write_com = Column(String, nullable=False)
    hardware_ver = Column(String, nullable=False)
    software_ver = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    cards = relationship("Card", backref="olt")
    onus = relationship("Onu", backref="olt")

    @hybrid_property
    def connection_params(self):
        """Retorna los parametros de conexion a la OLT"""
        return {
            "host": self.host,
            "port": self.telnet_port,
            "username": self.telnet_user,
            "password": self.telnet_password
        }

class Card(Base):
    """
    Modelo Card, representa una tarjeta (Board) de la OLT
    """
    __tablename__ = "card"

    id = Column(Integer, primary_key=True, index=True)
    olt_id = Column(Integer, ForeignKey("olt.id"))
    #rack = Column(Integer, nullable=False)
    #shelf = Column(Integer, nullable=False)
    slot = Column(Integer, nullable=False)
    type = Column(String)
    real_type = Column(String)
    port = Column(Integer, nullable=False)
    #hardware_ver = Column(String)
    soft_ver = Column(String)
    status = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    ports = relationship("Port", backref="card")

class Port(Base):
    """
    Modelo Port, representa uno delos puertos (Port) de una tarjeta (Board) de la OLT
    """
    __tablename__ = "port"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("card.id"))
    slot = Column(Integer, nullable=False)
    port = Column(Integer, nullable=False)
    pon_type = Column(String, nullable=False)
    admin_status = Column(String, nullable=False, default="n/a")
    operation_status = Column(String, nullable=False, default="n/a")
    description = Column(String)
    tx_power = Column(String, nullable=False, default="n/a")
    onu_count = Column(Integer, nullable=False, default=0)
    average_onu_signal = Column(Integer, nullable=False, default=0)

    onus = relationship("Onu", backref="port")

    @hybrid_property
    def online_onu_count(self):
        """Retorna la cantidad de ONUs en estado Online"""
        return sum(onu.status == "Online" for onu in self.onus)

    @hybrid_property
    def offline_onu_count(self):
        """Retorna la cantidad de ONUs en estado Offline"""
        return sum(onu.status == "Offline" for onu in self.onus)

    @online_onu_count.expression
    def online_onu_count(self, cls):
        """Retorna la cantidad de ONUs en estado Online en expresion SQL"""
        return select(func.count(1).filter(Onu.status == "Online")). \
            where(Onu.port_id == cls.id). \
            label('online_onu_count')

    @offline_onu_count.expression
    def offline_onu_count(self, cls):
        """Retorna la cantidad de ONUs en estado Offline en expresion SQL"""
        return select(func.count(1).filter(Onu.status == "Offline")). \
            where(Onu.port_id == cls.id). \
            label('online_onu_count')

class Onu(Base):
    """
    Modelo Onu, representa una ONU autorizada en la OLT
    """
    __tablename__ = "onu"

    id = Column(Integer, primary_key=True, index=True)
    olt_id = Column(Integer, ForeignKey("olt.id"))
    port_id = Column(Integer, ForeignKey("port.id"))
    ext_id = Column(Integer, index=True)
    pon_type = Column(String, nullable=False, default="GPON")
    shelf = Column(Integer, nullable=False)
    slot = Column(Integer, nullable=False)
    port_no = Column(Integer, nullable=False)
    index = Column(Integer, nullable=False)
    serial_no = Column(String, unique=True, index=True, nullable=False)
    vlan = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    signal = Column(String, nullable=False)
    comment = Column(String, nullable=False)
    onu_mode = Column(String, nullable=False, default="Routing")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __str__(self):
        return f"gpon-onu_{self.shelf}/{self.slot}/{self.port_no}:{self.index}"