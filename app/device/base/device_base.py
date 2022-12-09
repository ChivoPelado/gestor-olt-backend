"""Respuesta base de la interacción con la OLT."""
from celery import shared_task
from typing import List
from dataclasses import dataclass
from ntc_templates.parse import parse_output
from app.device.protocols import telnet
import os

os.environ["NTC_TEMPLATES_DIR"] = "app/device/templates"

@dataclass
class OltDeviceBase:
    """ Clase base para la gestión de interacción con OLT"""
    
    hardware_ver: str
    device_type: str
    software_ver: List
    pon_type: List[str]
    port_begin: int
    cards: List[dict[str:str]]
    command: dict[str: str]
    _connection_pars = {}
    
    @property
    def connection_pars(self):
        self._connection_pars
        
    @connection_pars.setter
    def connection_pars(self, pars):  
        self._connection_pars = {          
            **pars,
            "device_type": self.device_type
        }
        return self
        
    
    def get_uncfg_onus(self) -> List[dict[str: any]]:
        """ Devuelve las ONUs no authorizadas"""
        
        return  self._parse_result(self.command['get_uncfg_onu'])
    
    def get_cards(self) -> List[dict[str: any]]:
        """ Devuelve las tarjetas de OLT instaladas"""
        
        return  self._parse_result(self.command['get_cards'])

    def get_onu_types(self) -> List[dict[str: any]]:
        """ Devuelve las los tipos de ONU registrados en OLT"""
        
        return  self._parse_result(self.command['get_onu_types'])


    def get_device_type(self) -> str:
        return self.device_type
    
    
    def _parse_result(self, command) -> List[dict[str: any]]:
        """ Ejecuta el/los comandos mediante telnet usando Netmiko """
        
        task = telnet.send_command.apply_async(args=[self._connection_pars, [command]], queue='olt')
        result = task.get(disable_sync_subtasks=False)
        return  parse_output(platform=self.device_type, command=command, data=result.get(command))
    