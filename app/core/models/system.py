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


class Onu(Base):
    __tablename__ = "onu"

    id = Column(Integer, primary_key=True, index=True)
    olt_id = Column(Integer, ForeignKey("olt.id"))
    ext_id = Column(Integer, index=True)
    pon_type = Column(String, nullable=False, default="GPON")
    shelf = Column(Integer, nullable=False)
    slot = Column(Integer, nullable=False)
    port = Column(Integer, nullable=False)
    index = Column(Integer, nullable=False)
    serial_no = Column(String, unique=True, index=True, nullable=False)
    vlan = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    comment = Column(String, nullable=False)
    onu_mode = Column(String, nullable=False, default="Routing")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    olt = relationship("Olt")

    def __str__(self):
        return f"gpon-onu_{self.shelf}/{self.slot}/{self.port}:{self.index}"
