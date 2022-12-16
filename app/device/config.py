"""
Basic example showing how to create objects from data using a dynamic factory with
register/unregister methods.
"""

import json
from app.device.base import factory, loader
from app.device.base.device_base import OltDeviceBase


def initialize_modules() -> list[OltDeviceBase]:
    # lectura del archivo de parametrización de los módulos
    with open("app/device/modules/devices.json") as file:
        data = json.load(file)
        # carga los módulos o plugins
        loader.load_plugins(data["modules"])

        # crea los dispositivos
        return [factory.create(item) for item in data["devices"]]

