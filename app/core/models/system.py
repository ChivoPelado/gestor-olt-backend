from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Olt(Base):
    __tablename__="olt"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    ip_address = Column(String)
    ssh_port = Column(Integer)
    ssh_user = Column(String)
    ssh_password = Column(String)
    snmp_port = Column(Integer)
    snmp_read_com = Column(String)
    snmp_write_com = Column(String)
    hardware_ver = Column(String)
    software_ver = Column(String)