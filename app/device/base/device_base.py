"""Respuesta base de la interacción con la OLT."""

from celery import shared_task
from typing import List
from ntc_templates.parse import parse_output
from app.device.protocols import telnet
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
        port_begin: int, cards: List[dict[str:any]], command: dict[str: any],_connection_pars = {}
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
    def get_uncfg_onus(self) -> List[dict[str: any]]:
        """ Devuelve las ONUs no authorizadas"""
        ...
    
    @abstractmethod
    def get_cards(self) -> List[dict[str: any]]:
        """ Devuelve las tarjetas de OLT instaladas"""
        ...

    @abstractmethod
    def get_ports(self) -> List[dict[str: any]]:
        """ Devuelve los puertos correspondientes a las tarjetas de OLT"""
        ...

    def get_onu_types(self) -> List[dict[str: any]]:
        """ Devuelve las los tipos de ONU registrados en OLT"""
        
        return  self._excecute_and_parse(self.command['get_onu_types'])


    @abstractmethod
    def get_vlans(self) -> List[dict[str: any]]:
        """ Devuelve las VLANs configuradas en OLT"""
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
    