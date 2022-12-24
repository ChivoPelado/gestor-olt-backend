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

@dataclass
class PortTXValue(ICommand):
    shelf: int
    slot: int
    port: int

    _command_str = "Pontencia Tx de Puerto "

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_port_tx(self.shelf, self.slot, self.port)

    def description(self):
        return self._command_str

@dataclass
class PortStatus(ICommand):
    shelf: int
    slot: int
    port: int

    _command_str = "Estatus de Puerto "

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_port_status(self.shelf, self.slot, self.port)

    def description(self):
        return self._command_str

@dataclass
class PortAdminState(ICommand):
    shelf: int
    slot: int
    port: int

    _command_str = "Estado Administrativo de Puerto "

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_port_admin_state(self.shelf, self.slot, self.port)

    def description(self):
        return self._command_str



@dataclass
class PortDescription(ICommand):
    shelf: int
    slot: int
    port: int

    _command_str = "Descripción del Puerto Óptico "

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_port_description(self.shelf, self.slot, self.port)

    def description(self):
        return self._command_str


@dataclass
class OnuRXSignal(ICommand):
    shelf: int
    slot: int
    port: int
    index: int

    _command_str = "Potencia óptica de ONU "

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_onu_rx(self.shelf, self.slot, self.port, self.index)

    def description(self):
        return self._command_str


@dataclass
class OltRXSignal(ICommand):
    shelf: int
    slot: int
    port: int
    index: int

    _command_str = "Potencia óptica de OLT "

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_olt_rx(self.shelf, self.slot, self.port, self.index)

    def description(self):
        return self._command_str

    
@dataclass
class OnuState(ICommand):
    shelf: int
    slot: int
    port: int
    index: int

    _command_str = "Estado de la ONU"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_onu_state(self.shelf, self.slot, self.port, self.index)

    def description(self):
        return self._command_str