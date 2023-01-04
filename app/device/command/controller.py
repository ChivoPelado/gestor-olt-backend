"""
Invoker Class
"""
from app.device.command.protocol import ICommand
from app.device.base.interface import IOlt, IOnu
from app.device.base.device_base import OltDeviceBase
from app.device.config import initialize_modules


class OltController:

    def get(self, command: ICommand, olt: IOlt, onu: IOnu = None):

        vendor = self._get_olt_vendor_item(olt)

        if command.loggable:
        
            return command.execute(vendor), (command.description(), olt.id)

        return command.execute(vendor)
    

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