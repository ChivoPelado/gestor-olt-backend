"""
Invoker Class
"""
import time
from dataclasses import dataclass
from datetime import datetime
# from app.interface.task import Task
from app.device.command.protocol import ICommand, IOlt, IOnu
from app.device.base.device_base import OltDeviceBase
from app.device.config import initialize_modules



@dataclass
class OltController:
    _commands = {}
    _history = []

    def get(self, command: ICommand, olt: IOlt, onu: IOnu = None) -> None:
        vendor = self._get_olt_vendor_item(olt)
        self._history.append((time.time(), command.description(), olt.name))
        return command.execute(vendor)


    """     def register(self, task: Task) -> None:
        self._commands[task] = task """


    def get_command_history(self):
        for row in self._history:
            print(
                f"{datetime.fromtimestamp(row[0]).strftime('%d-%B-%Y %H:%M:%S')}"
                f" : {row[1]}"
                f" : {row[2]}"
            )
    

    def _get_olt_vendor_item(self, olt: IOlt) -> OltDeviceBase:

        modules = initialize_modules()
        
        try:
            (vendor,) = [device for device in modules if device.hardware_ver == olt.hardware_ver 
                            and olt.software_ver in device.software_ver]
            
            vendor.connection_pars = {
                "host": olt.host,
                "port": olt.telnet_port,
                "username": olt.telnet_user,
                "password": olt.telnet_password,
                "snmp_port": olt.snmp_port,
                "snmp_read_com": olt.snmp_read_com,
                "snmp_write_com": olt.snmp_write_com
            }

            return vendor

        except ValueError:
            print("Error al validar tipo de olt")