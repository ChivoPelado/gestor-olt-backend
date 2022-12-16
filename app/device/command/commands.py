from dataclasses import dataclass
from app.device.command.protocol import ICommand, IOnu, IOnuType
from app.device.base.device_base import OltDeviceBase


class GetOLTShelf(ICommand):

    _command_str = "Lista el Shelf o Frame de OLT"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_shelf()

    def description(self):
        return self._command_str

class GetUncfgONUs(ICommand):

    _command_str = "Lista de ONUs sin autorización"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_uncfg_onus()

    def description(self):
        return self._command_str


class GetOLTCards(ICommand):

    _command_str = "Extrae información de Tarjetas de OLT"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_cards()

    def description(self):
        return self._command_str


class GetOLTPorts(ICommand):

    _command_str = "Extrae información de Puertos de OLT"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_ports()

    def description(self):
        return self._command_str



class GetOLTVlans(ICommand):

    _command_str = "Extrae información de VLANs de OLT"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_vlans()

    def description(self):
        return self._command_str


@dataclass
class AuthorizeONU(ICommand):
    onu: IOnu
    onu_type: IOnuType
    speed_profile_up: str
    speed_profile_down: str

    _command_str = "autorización de ONU "

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.authorize_onu(
            self.onu, self.onu_type, self.speed_profile_up, self.speed_profile_down
        )

    def description(self):
        return self._command_str