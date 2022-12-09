"""
Basic example showing how to create objects from data using a dynamic factory with
register/unregister methods.
"""

import json
from dataclasses import dataclass
from app.device.base import factory, loader
from app.device.base.device_base import OltDeviceBase


@dataclass
class Olt:
    host: str
    port: int
    username: str
    password: str
    hardware_ver:str
    software_ver:str
    
    def connection_params(self):
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password
        }

def initialize_modules() -> list[OltDeviceBase]:
    # lectura del archivo de parametrización de los módulos
    with open("app/device/modules/devices.json") as file:
        data = json.load(file)
        # carga los módulos o plugins
        loader.load_plugins(data["modules"])

        # crea los dispositivos
        return [factory.create(item) for item in data["devices"]]


def main() -> None:
    """Create game characters from a file containg a level definition."""

    print("registered OLT modules")
    
    modules = initialize_modules()
    for module in modules:
        print(module)
        
    """ olt = Olt(
        host="200.24.155.111",
        port=2333,
        username="aherrera",
        password="CableFAM2022*",
        hardware_ver="Huawei-MA5800-X15",
        software_ver="R018") """
        
    olt = Olt(
        host="200.24.155.121",
        port=2334,
        username="aherrera",
        password="CableFAM2022*",
        hardware_ver="ZTE-C300",
        software_ver="2.x")
    
    try:
        (vendor,) = [device for device in modules if device.hardware_ver == olt.hardware_ver 
                     and olt.software_ver in device.software_ver]
        
        print(f"Detected vendor: {vendor.hardware_ver}, software ver {olt.software_ver}", )
        
        vendor.connection_pars = olt.connection_params()
        result_parsed = vendor.get_uncfg_onus()

        print(result_parsed)
    
    except ValueError:
        print("Error al validar tipo de olt")
    
    
if __name__ == "__main__":
    main()
