from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func


class Olt(Base):
    __tablename__ = "olt"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    ip_address = Column(String, nullable=False)
    ssh_port = Column(Integer, nullable=False)
    ssh_user = Column(String, nullable=False)
    ssh_password = Column(String, nullable=False)
    snmp_port = Column(Integer, nullable=False)
    snmp_read_com = Column(String, nullable=False)
    snmp_write_com = Column(String, nullable=False)
    hardware_ver = Column(String, nullable=False)
    software_ver = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())



class Card(Base):
    __tablename__ = "card"

    id = Column(Integer, primary_key=True, index=True)
    olt_id = Column(Integer, ForeignKey("olt.id"))
    rack = Column(Integer, nullable=False)
    shelf = Column(Integer, nullable=False)
    slot = Column(Integer, nullable=False)
    cfg_type = Column(String)
    real_type = Column(String)
    port = Column(Integer, nullable=False)
    hardware_ver = Column(String)
    software_ver = Column(String)
    status = Column(String, nullable=False)
    
    olt = relationship("Olt", backref="card")

class Port(Base):
    __tablename__ = "port"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("card.id"))
    port_no = Column(Integer, nullable=False)
    pon_type = Column(String, nullable=False)
    admin_status = Column(String, nullable=False)
    operation_status = Column(String, nullable=False)
    description = Column(String)
    tx_power = Column(String)
    onu_count = Column(Integer, nullable=False)
    online_onu_count = Column(Integer, nullable=False)
    average_onu_signal = Column(Integer, nullable=False)
    
    # olt = relationship("Card", backref="port")
   # onus = relationship("Onu")

    ##onus = relationship("Onu")

class Onu(Base):
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
    comment = Column(String, nullable=False)
    onu_mode = Column(String, nullable=False, default="Routing")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    port = relationship("Port", backref="onu")
    # olt = relationship("Olt")

    def __str__(self):
        return f"gpon-onu_{self.shelf}/{self.slot}/{self.port}:{self.index}"



""" class Port(Base):
    __tablename__ = "port"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("card.id"))
    port_no = Column(Integer, nullable=False)
    pon_type = Column(String, nullable=False)
    admin_status = Column(String, nullable=False)
    operation_status = Column(String, nullable=False)
    description = Column(String)
    tx_power = Column(String)
    onu_count = Column(Integer, nullable=False)
    online_onu_count = Column(Integer, nullable=False)
    average_onu_signal = Column(Integer, nullable=False)
    
    olt = relationship("Olt", backref="port")
    onus = relationship("Onu") """

