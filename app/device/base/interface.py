
from abc import ABC, abstractmethod

class IOlt(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def host(self) -> str:
        ...

    @property
    @abstractmethod
    def telnet_port(self) -> int:
        ...

    @property
    @abstractmethod   
    def telnet_user(self) -> str:
        ...

    @property
    @abstractmethod   
    def telnet_password(self) -> str:
        ...

    @property
    @abstractmethod   
    def snmp_port(self) -> str:
        ...

    @property
    @abstractmethod   
    def snmp_read_com(self) -> str:
        ...

    @property
    @abstractmethod   
    def snmp_write_com(self) -> str:
        ...

    @property
    @abstractmethod   
    def hardware_ver(self) -> str:
        ...

    @property
    @abstractmethod   
    def software_ver(self) -> str:
        ...


class IOnu(ABC):

    @property
    @abstractmethod
    def shelf(self) -> int:
        ...

    @property
    @abstractmethod
    def slot(self) -> int:
        ...

    @property
    @abstractmethod
    def port_no(self) -> int:
        ...

    @property
    @abstractmethod
    def index(self) -> int:
        ...

    @property
    @abstractmethod
    def srvc_port(self) -> int:
        ...

    @property
    @abstractmethod
    def upload_speed(self) -> str:
        ...

    @property
    @abstractmethod
    def download_speed(self) -> str:
        ...

    @property
    @abstractmethod   
    def serial_no(self) -> str:
        ...

    @property
    @abstractmethod   
    def name(self) -> str:
        ...

    @property
    @abstractmethod   
    def comment(self) -> str:
        ...

    @property
    @abstractmethod   
    def vlan(self) -> int:
        ...

    @property
    @abstractmethod   
    def onu_mode(self) -> str:
        ...


class IOnuType(ABC):

    @property
    @abstractmethod   
    def name(self) -> str:
        ...

    @property
    @abstractmethod   
    def capability(self) -> str:
        ...

    @property
    @abstractmethod   
    def ethernet_ports(self) -> int:
        ...

    @property
    @abstractmethod   
    def catv(self) -> int:
        ...
 

 