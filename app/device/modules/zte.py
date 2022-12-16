"""Agrega modulo para interactuar con olt ZTE."""

from typing import List
from app.device.base import factory
from app.device.base.device_base import OltDeviceBase
from app.device.command.protocol import IOnu, IOnuType


VPORT = 1
GEMPORT = 1
TCONT = 1
SRVC_PORT = 1
FLOW_MODE = 1
PRIORITY = 0
IPHOST = 1
VEIP = 1


class Zte(OltDeviceBase):
    """Modulo de gestión de comandos de equipo ZTE"""

    def __init__(self, hardware_ver: str, device_type: str, software_ver: List, pon_type: List[str], port_begin: int, cards: List[dict[str: str]], command: dict[str: str]) -> None:
        super().__init__(hardware_ver, device_type, software_ver, pon_type, port_begin, cards, command)

    def get_shelf(self) -> dict[str: any]:
        olt_shelf =  super().excecute_and_parse(self.command['get_olt_shelf'])

        shelf = {}

        shelf['shelf'] = olt_shelf[0]['shelf']
        shelf['type'] = olt_shelf[0]['shelf_type']
        shelf['shelf_sn'] = olt_shelf[0]['serial_no']

        return shelf
    
    def get_uncfg_onus(self) -> List[dict[str: any]]:
        return super().excecute_and_parse(self.command['get_uncfg_onu'])


    def get_cards(self) -> List[dict[str: any]]:
        """ Devuelve las tarjetas de OLT instaladas"""

        response = []
        card = {}
        parsed_response = super().excecute_and_parse(self.command['get_cards'])

        for data in parsed_response:
            role = None
            for data_card in self.cards:
                if data['cfgtype'] == data_card['name']:
                    role = data_card['role']
            
            card['slot'] = int(data['slot'])
            card['type'] = data['cfgtype']
            card['real_type'] = data['realtype']
            card['port'] = int(data['port'])
            card['soft_ver'] = data['softver']
            card['status'] = data['status']
            card['role'] = role
            
            response.append(card.copy())

        return response

    def get_vlans(self) -> List[dict[str: any]]:
        """ Formatea la respuesta entregada desde la clase padre:
        Formato original Ex.->
        [
            {
                "vlans": "1,100,200,300,400,500,600,700,4091-4092,4094"
            }
        ]
        Formato requerido ->
        [
            {
                "vlan": "100",
                "description": null,
                "scope": "Internet"
            },
            ...
        ]
        """

        # Lista predefinida de VLANs reservadas en OLT Zte.
        reserved_vlans = ["1", "4091-4092", "4094"]

        # Se obtiene el resultado original desde la clase Padre
        parsed_response = super().excecute_and_parse(self.command['get_vlans'])

        # Se extrae los valores separados por coma a una lista
        vlans_list = parsed_response[0]['vlans'].split(",")

        # Se filtra la lista original de VLANs
        filtered_vlans = [vlan for vlan in vlans_list if vlan not in reserved_vlans]

        response = []
        vlan = {}
        for response_vlans in filtered_vlans:
            vlan['vlan'] = int(response_vlans)      # Vlan Filtrada
            vlan['description'] = None              # Sin detalles
            vlan['scope'] = "Internet"              # Todas las VLANs al servicio de Internet

            response.append(vlan.copy())

        return response

    def get_ports(self) -> List[dict[str: any]]:
        ports = []
        port = {}
        parsed_response = self.get_cards()

        for card in parsed_response:
            if card['role'] == "GPON":
                for port_number in (port + self.port_begin for port in range(card['port'])): 
                    # port['card_id'] = card.id,
                    port['slot'] = card['slot']
                    port['port'] = port_number
                    port['pon_type'] = card['role']

                    ports.append(port.copy())

        return ports

        
    def authorize_onu(self, onu: IOnu,  onu_type: IOnuType,  profile_up: str, profile_down: str) -> None:
       
        olt_interface = f"gpon-olt_{onu.shelf}/{onu.slot}/{onu.port_no}"

        onu_index =self._get_next_avail_index(olt_interface)

        onu_interface = f"gpon-onu_{onu.shelf}/{onu.slot}/{onu.port_no}:{onu_index}"


        commands = []

        commands += [self.command['enter_configutation_mode']]
        commands += [self.command['select_interface'] % olt_interface]
        commands += [self.command['bind_onu_type_sn'] % (onu_index, onu_type.name, onu.serial_no)]
        commands += [self.command['exit_mode']]
        commands += [self.command['select_interface'] % onu_interface] 
        commands += [self.command['set_onu_name'] % onu.name]
        commands += [self.command['set_onu_description'] % onu.comment]
        commands += [self.command['sn_bind_enable']]
        commands += [self.command['set_tcont_profile'] % (TCONT, profile_up)]
        commands += [self.command['set_gemport'] % (GEMPORT, TCONT)]
        commands += [self.command['set_downstream_limit'] % (GEMPORT, profile_down)]
        commands += [self.command['set_switchport_mode_hybrid'] % VPORT]
        commands += [self.command['set_service_port'] % (SRVC_PORT, VPORT, onu.vlan, onu.vlan)]
        commands += [self.command['exit_mode']]

        if onu.onu_mode == "Routing":
            commands += self.set_onu_mode_routing(onu, onu_interface, onu_type)

        commands += [self.command['enable_mode_forward']]
        commands += [self.command['enable_ingress_type']]

        commands += [self.command['exit_mode']]
        commands += [self.command['exit_mode']]

        result = super().excecute(commands, expect_string='[#\?$]')

        return onu_index


    def set_onu_mode_routing(self, onu:IOnu, onu_interface: str, onu_type: IOnuType ) -> List[str]:

        commands = []

        commands += [self.command['manage_pon_onu'] % onu_interface]
        commands += [self.command['set_flow_mode_filter_discard'] % FLOW_MODE]
        commands += [self.command['set_flow_prority'] % (FLOW_MODE, PRIORITY, onu.vlan)]
        commands += [self.command['set_gemport_flow'] % (GEMPORT, FLOW_MODE)]
        commands += [self.command['bind_switch_port_ip_host'] % IPHOST]
        commands += [self.command['bind_switch_port_veip'] % VEIP]
        commands += [self.command['set_vlan_filter_mode'] % IPHOST]
        commands += [self.command['set_vlan_filter_priority'] % (IPHOST, PRIORITY, onu.vlan)]

        print("ETH PORTs", onu_type.ethernet_ports)

        for index in range(onu_type.ethernet_ports):
            eth = f"eth_0/{index + 1}"
            commands += [self.command['set_dhcp_on_ports'] % eth ]

        return commands


    def set_onu_mode_bridge():
        pass


    def _get_next_avail_index(self, olt_interface: str) -> int:
        """ Metodo interno para determinar el indice ONU disponible desde una secuencia"""
        
        # Se obtiene onus desde una interface OLT
        parsed_response = super().excecute_and_parse(self.command['show_onus_by_if'] % olt_interface)

        # Se extraen los indices usados a una lista
        indexes = []
        available_index = int
        for index in parsed_response:
            indexes.append(int(index['index']))

        # Si existen fatantes en la secuencia, los enlista
        available_index = [index for index in range(indexes[0], indexes[-1]+1) if index not in indexes]

        # Extrae el primer faltante en la secuencia
        available_index = available_index[0]

        # Si no existen faltantes en la secuencia, entregár el indice siguiente
        if not available_index:
            available_index = indexes.pop() + 1

        # Retorna el indice
        return available_index


    def __repr__(self) -> str:
        return self.hardware_ver

def register() -> None:
    """Registro de módulo"""
    factory.register("zte", Zte)
    