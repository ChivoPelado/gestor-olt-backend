from dataclasses import dataclass
from app.device.command.protocol import ICommand
from app.device.base.device_base import OltDeviceBase
from app.device.base.interface import IOnu, IOnuType


class GetOLTShelf(ICommand):

    loggable = False
    _command_str = "Lista el Shelf o Frame de OLT"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_shelf()

    def description(self):
        return self._command_str

class GetUncfgONUs(ICommand):

    loggable = False
    _command_str = "Lista de ONUs sin autorización"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_uncfg_onus()

    def description(self):
        return self._command_str


class GetOLTCards(ICommand):

    loggable = False
    _command_str = "Extrae información de Tarjetas de OLT"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_cards()

    def description(self):
        return self._command_str


class GetOLTPorts(ICommand):

    loggable = False
    _command_str = "Extrae información de Puertos de OLT"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_ports()

    def description(self):
        return self._command_str


class GetOLTVlans(ICommand):

    loggable = False
    _command_str = "Extrae información de VLANs de OLT"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_vlans()

    def description(self):
        return self._command_str

@dataclass
class GetSrvcPrtAndIndex(ICommand):
    shelf: int
    slot: int
    port: int
    vlan: int

    loggable = False
    _command_str = None

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_srvcprt_and_onu_index(self.shelf, self.slot, self.port, self.vlan)

    def description(self):
        return self._command_str


@dataclass
class TestAuthorizeONU(ICommand):

    loggable = False

    def execute(self, olt_vendor: OltDeviceBase) -> list[dict[str: any]]:
        return olt_vendor.authorize_onu()

    def description(self) -> str:
        return ""

    
@dataclass
class AuthorizeONU(ICommand):
    onu: IOnu
    onu_type: IOnuType

    loggable = True
    _command_str = "ONT con SN %s Interfaz %s Autorizada "

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.authorize_onu(self.onu, self.onu_type)

    def description(self):
        interfaz = f'gpon-onu_{self.onu.shelf}/{self.onu.slot}/{self.onu.port_no}:{self.onu.index}'
        action_str = self._command_str % (self.onu.serial_no, interfaz)
        return action_str


@dataclass
class SetOnuModeBridging(ICommand):
    onu: IOnu
    onu_type: IOnuType

    loggable = True
    _command_str = "Cambio de modo de ONT a bridging"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.set_onu_mode_bridging(self.onu, self.onu_type)

    def description(self):
        return self._command_str


@dataclass
class SetOnuModeRouting(ICommand):
    onu: IOnu
    onu_type: IOnuType

    loggable = True
    _command_str = "Cambio de modo de ONT a routing"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.set_onu_mode_routing(self.onu, self.onu_type)

    def description(self):
        return self._command_str


@dataclass
class PortTXValue(ICommand):
    shelf: int
    slot: int
    port: int

    loggable = False
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

    loggable = False
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

    loggable = False
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

    loggable = False
    _command_str = "Descripción del Puerto Óptico "

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_port_description(self.shelf, self.slot, self.port)

    def description(self):
        return self._command_str


@dataclass
class OnuRXSignal(ICommand):
    onu: IOnu

    loggable = False
    _command_str = "Potencia óptica de ONT "

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_onu_rx(self.onu)

    def description(self):
        return self._command_str


@dataclass
class OltRXSignal(ICommand):
    onu: IOnu

    loggable = False
    _command_str = "Potencia óptica de OLT "

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_olt_rx(self.onu)

    def description(self):
        return self._command_str

    
@dataclass
class OnuState(ICommand):
    onu: IOnu

    loggable = False
    _command_str = "Estado de la ONT"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.get_onu_state(self.onu)

    def description(self):
        return self._command_str



@dataclass
class DeleteOnu(ICommand):
    onu: IOnu

    loggable = True
    _command_str = "ONT eliminada"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.delete_onu(self.onu)

    def description(self):
        return self._command_str

@dataclass
class DeactivateOnu(ICommand):
    onu: IOnu

    loggable = True
    _command_str = "ONT deshabilitada"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.deactivate_onu(self.onu)

    def description(self):
        return self._command_str


@dataclass
class ActivateOnu(ICommand):
    onu: IOnu

    loggable = True
    _command_str = "ONT habilitada"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.activate_onu(self.onu)

    def description(self):
        return self._command_str


@dataclass
class RebooteOnu(ICommand):
    onu: IOnu

    loggable = True
    _command_str = "ONT reiniciada"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.reboot_onu(self.onu)

    def description(self):
        return self._command_str


@dataclass
class EnableONUCatv(ICommand):
    onu: IOnu

    loggable = True
    _command_str = "CATV Activado"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.enable_catv(self.onu)

    def description(self):
        return self._command_str


@dataclass
class DisableONUCatv(ICommand):
    onu: IOnu

    loggable = True
    _command_str = "CATV Desactivado"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.disable_catv(self.onu)

    def description(self):
        return self._command_str


@dataclass
class GetONUAttenuation(ICommand):
    onu: IOnu

    loggable = False
    _command_str = "Atenuacion de ONT"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.show_onu_power_attn(self.onu)

    def description(self):
        return self._command_str


@dataclass
class ResyncONU(ICommand):
    onu: IOnu
    onu_type: IOnuType

    loggable = True
    _command_str = "Resincronización de ONT"

    def execute(self, olt_vendor: OltDeviceBase):
        return olt_vendor.resync_onu(self.onu, self.onu_type)

    def description(self):
        return self._command_str



@dataclass
class GetONURunningConfig(ICommand):
    onu: IOnu

    loggable = False
    _command_str = "Obtiene las configuraciones de interface y ONT"

    def execute(self, olt_vendor: OltDeviceBase):
        value =  olt_vendor.show_onu_running_config(self.onu)
        print(value)
        return value

    def description(self):
        return self._command_str


@dataclass
class GetONUGeneralStatus(ICommand):
    onu: IOnu

    loggable = False
    _command_str = "Información general de ONT"

    def execute(self, olt_vendor: OltDeviceBase):
        value =  olt_vendor.show_onu_general_status(self.onu)
        print(value)
        return value

    def description(self):
        return self._command_str