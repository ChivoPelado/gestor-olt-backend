"""Respuesta base de la interacción con la OLT."""

from celery import shared_task
from typing import List
from ntc_templates.parse import parse_output
from app.device.protocols import telnet, snmp
from app.device.base.interface import IOlt, IOnu, IOnuType
from abc import ABC, abstractmethod
import os

# Directorio para las plantillas NTC-TEMPLATES 
os.environ["NTC_TEMPLATES_DIR"] = "app/device/ntc-templates"


class OltDeviceBase(ABC):
    """ 
    Clase Abstracta BASE para la interacción con las OLTs basados en 
    sistemas de módulos
    
    Los módulos a implementarse deben heredar de esta clase y implementar
    los métodos abstractos adaptando la respuesta de entrada a una respuesta
    estándar de salida 
    """

    def __init__(self, hardware_ver: str, device_type: str, software_ver: List, pon_type: List[str],
        port_begin: int, cards: List[dict[str:any]], command: dict[str: any], MIB: dict[str: any],
        _connection_pars = {}
    ) -> None:

        """ 
        Constructor.

        Estos argumentos son automáticamente complementados por los módulos en base al formato
        devices.json establecido en la carpeta de módulos.
        """
        self.device_type = device_type              # tipo de dispositivo (nombre del fabricante)
        self.hardware_ver = hardware_ver            # versión de hardware del dispositivo 
        self.software_ver = software_ver            # version(es) de software soportados [Lista]
        self.pon_type = pon_type                    # estándard PON Ex. ["GPON"] ["GPON, EPON"] [Lista]
        self.port_begin = port_begin                # indicador de inicio del primer puerto
        self.cards = cards                          # tarjetas soportadas, número de puertos y rol
        self.command = command                      # listas de comandos
        self.MIB = MIB
        
        #Uso interno para recolección de información de conexión
        
        self._connection_pars = _connection_pars    
    
    @property
    def connection_pars(self):
        """getter"""
        self._connection_pars
        
    @connection_pars.setter
    def connection_pars(self, pars):  
        """setter"""
        self._connection_pars = {          
            **pars,
            "device_type": self.device_type
        }
        return self
        
    ############################################################
    # Métodos abstractos a ser implementados en módulos
    ############################################################
    
    @abstractmethod
    def get_shelf(self) -> dict[str: any]:
        """ Devuelve shelf o frame de OLT"""
        ...
    
    @abstractmethod
    def get_cards(self) -> List[dict[str: any]]:
        """ Devuelve las tarjetas de OLT instaladas"""
        ...

    @abstractmethod
    def get_vlans(self) -> List[dict[str: any]]:
        """ Devuelve las VLANs configuradas en OLT"""
        ...

    @abstractmethod
    def get_ports(self) -> List[dict[str: any]]:
        """ Devuelve los puertos correspondientes a las tarjetas de OLT"""
        ...

    @abstractmethod
    def get_uncfg_onus(self) -> List[dict[str: any]]:
        """ Devuelve las ONT sin configuración / autorización"""
        ...

    @abstractmethod
    def get_srvcprt_and_onu_index(self, shelf: int, slot: int, port: int, vlan: int = None) -> tuple:
        """ Metodo interno para determinar el indice ONU disponible desde una secuencia"""
        ...

    @abstractmethod 
    def authorize_onu(self, onu: IOnu,  onu_type: IOnuType,  profile_up: str, profile_down: str) -> bool: 
        """ Gestión de autorizacion de ONTs"""
        ...

    @abstractmethod
    def set_onu_mode_routing(self, onu:IOnu, onu_type: IOnuType) -> List[str]:
        """ Define el modo de ONT a tipo Routing"""
        ...

    @abstractmethod
    def set_onu_mode_bridging(self, onu: IOnu, onu_type: IOnuType) -> List[str]:
        """ Define el modo de ONT a tipo Bridging"""
        ...
    
    @abstractmethod
    def enable_catv(self, onu: IOnu) -> bool:
        """ Habilita el puerto CATV de la ONT"""
        ...

    @abstractmethod
    def disable_catv(self, onu: IOnu) -> bool:
        """ Deshabilita el puerto CATV de la ONT"""
        ...

    @abstractmethod
    def resync_onu(self, onu: IOnu, onu_type: IOnuType) -> bool:
        """ Resincroniza ONT con la desde una fuente de datos con OLT"""
        ...

    @abstractmethod
    def get_port_tx(self, shelf: int, slot: int, port: int) -> int:
        """ Devuelve la potencia o´tica de un puerto PON"""
        ...
    
    @abstractmethod
    def get_port_status(self, shelf: int, slot: int, port: int) -> str:
        """ Devuelve el estado de un puerto PON"""
        ...

    @abstractmethod
    def get_port_admin_state(self, shelf: int, slot: int, port: int) -> str:
        """ Devuelve el estado administrativo de un puerto """
        ...

    @abstractmethod
    def get_port_description(self, shelf: int, slot: int, port: int) -> str:
        """ Devuelve la descripción de un puerto PON"""
        ...

    @abstractmethod
    def get_onu_rx(self, onu: IOnu) -> int:
        """ Retorna la potencia óptica de la onu"""
        ...

    @abstractmethod
    def get_olt_rx(self, onu: IOnu) -> int:
        """ Retorna la potencia óptica de la OLT recibida de la OLT"""
        ...

    @abstractmethod
    def get_onu_state(self, onu: IOnu) -> str:
        """ Devuelve el estado de la onu """
        ...

    @abstractmethod
    def deactivate_onu(self, onu: IOnu) -> bool:
        """ Desactiva administrativamente una ONT"""
        ...

    @abstractmethod
    def activate_onu(self, onu: IOnu) -> bool:
        """ Activa administrativamente una ONT"""
        ...  

    @abstractmethod
    def reboot_onu(self, onu: IOnu) -> bool:
        """ Reinicia la ONT """
        ...

    @abstractmethod
    def delete_onu(self, onu: IOnu) -> bool:
        """ Elimina ONT de la OLT"""
        ...

    @abstractmethod
    def show_onu_running_config(self, onu: IOnu) -> str:
        """ devuelve la configuración de la ont"""
        ...

    @abstractmethod
    def show_onu_general_status(self, onu: IOnu) -> str:
        """ Muesta un resumen de datos de ont extraidos del shell de la OLT"""
        ...

    ############################################################
    # Implementacines base para la interacción con dispositivos
    ############################################################

    def get_device_type(self) -> str:
        return self.device_type
    

    def excecute(self, command: List, expect_string=None) -> List[dict[str: any]]:
        """ Punto de ejecución de comandos desde los módulos implementados"""

        return self._excecute(command, expect_string)

    def excecute_and_parse(self, command: str, expected_string=None) -> List[dict[str: any]]:
        """ Punto de ejecución de comandos desde los módulos implementados"""

        return self._excecute_and_parse(command, expected_string)
    
    
    ############################################################
    # Métodos de uso exclusivo interno
    ############################################################
    def _excecute_and_parse(self, command, expect_string=None) -> List[dict[str: any]]:
        """ Ejecuta el/los comandos mediante telnet usando Netmiko """
        
        
        task = telnet.send_command.apply_async(args=[self._connection_pars, [command], expect_string], queue='olt')
        result = task.get(disable_sync_subtasks=False)
        return  parse_output(platform=self.device_type, command=command, data=result.get(command))

    
    def _excecute(self, command, expect_string=None) -> List[dict[str: any]]:
        """ Ejecuta el/los comandos mediante telnet usando Netmiko """
        
        task = telnet.send_command.apply_async(args=[self._connection_pars, command, expect_string], queue='olt')
        result = task.get(disable_sync_subtasks=False)
        return  result
    

    def _snmp_query(self, oid: str) -> any:
        """ Ejecuta las consultas SNMP desde la OID entregada"""

        task = snmp.get_request(
            self._connection_pars.get('host'), 
            [oid], 
            self._connection_pars.get('snmp_write_com'),
            self._connection_pars.get('snmp_port')
            )
        #result = task.get(disable_sync_subtasks=False)
        return task