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

    def __init__(self, hardware_ver: str, device_type: str, software_ver: List, 
        pon_type: List[str], port_begin: int, cards: List[dict[str: str]], 
        command: dict[str: str], MIB: dict[str: str]) -> None:

        super().__init__(hardware_ver, device_type, software_ver, pon_type, port_begin, cards, command, MIB)


    def get_shelf(self) -> dict[str: any]:
        olt_shelf =  super().excecute_and_parse(self.command['get_olt_shelf'])

        shelf = {}

        shelf['shelf'] = olt_shelf[0]['shelf']
        shelf['type'] = olt_shelf[0]['shelf_type']
        shelf['shelf_sn'] = olt_shelf[0]['serial_no']

        return shelf
    
    def get_uncfg_onus(self) -> List[dict[str: any]]:
        return super().excecute_and_parse(self.command['get_uncfg_onu_pon'])


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

    def get_port_tx(self, shelf: int, slot: int, port: int):

        oid = self.MIB['zxAnOpticalPowerTxCurrValue'] + self.encode_gpon_onu_index_type_one(shelf, slot, port)

        result = super()._snmp_query(oid)
        level = round((int(result[oid]) / 1000), 4)

        return 0 if level == 2147483.647 else level


    def get_port_status(self, shelf: int, slot: int, port: int):

        oid = self.MIB['ifOperStatus'] + self.encode_gpon_olt_ifindex_type_one(shelf, slot, port)

        result = super()._snmp_query(oid)
        status = int(result[oid])

        return "Arriba" if status == 1 else "Abajo"


    def get_port_admin_state(self, shelf: int, slot: int, port: int):

        oid = self.MIB['ifAdminStatus'] + self.encode_gpon_olt_ifindex_type_one(shelf, slot, port)

        result = super()._snmp_query(oid)
        status = int(result[oid])

        return "Habilitado" if status == 1 else "Deshabilitado"

    
    def get_port_description(self, shelf: int, slot: int, port: int):

        oid = self.MIB['ifDescr'] + self.encode_gpon_olt_ifindex_type_one(shelf, slot, port)

        result = super()._snmp_query(oid)

        return result[oid]

    def get_onu_rx(self, shelf: int, slot: int, port: int, index: int):

        oid = self.MIB['zxGponPonRxOpticalLevel'] + self.encode_gpon_onu_index(shelf, slot, port, index) + '.1'

        result = super()._snmp_query(oid)

        return self._onu_rx_convert(int(result[oid]))


    def get_olt_rx(self, shelf: int, slot: int, port: int, index: int):

        oid = self.MIB['txPower'] + self.encode_gpon_onu_index(shelf, slot, port, index)

        result = super()._snmp_query(oid)

        return round((int(result[oid]) / 1000), 2)


    def get_onu_state(self, shelf: int, slot: int, port: int, index: int):
        
        oid = self.MIB['zxGponOntPhaseState'] + self.encode_gpon_onu_index(shelf, slot, port, index)

        result = super()._snmp_query(oid)

        result = int(result[oid])

        state = "En línea" if result == 3 else "LOS" if result == 1 else "Fuera de Línea" if result == 6 else "Falla Eléctrica" if result == 4 else "Otro\Desconocido" 
        return state

        
    def _onu_rx_convert(self, snmp_value):
        if snmp_value == 65535:
            return 0
        elif snmp_value > 30000:
            return (snmp_value - 65536) * 0.002 - 30
        return round((snmp_value * 0.002 - 30), 2)
        # return result[oid]


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

    def encode_gpon_onu_index(self, shelf: int, slot: int, port: int, index: int):
        index_type = self._dec_to_bin(1, 4)  # '0001'
        shelf = self._dec_to_bin(shelf - 1, 4)  # '0000'
        slot = self._dec_to_bin(slot, 8)
        port = self._dec_to_bin(port, 8)
        srv_prt_id = self._dec_to_bin(0, 8)

        print(str(hex(int((index_type + shelf + slot + port + srv_prt_id), 2))))
        return str(int((index_type + shelf + slot + port + srv_prt_id), 2)) + "." + str(index)


    def encode_gpon_onu_index_type_one(self, shelf: int, slot: int, port: int):
        # Slot conversion for ZTE C300 Shelf
        in_slot = slot
        composite_index_slot = 0
        if 2 <= in_slot < 9:
            composite_index_slot = in_slot - 2
        elif 12 <= slot <= 22:
            composite_index_slot = in_slot - 4

        index_type = self._dec_to_bin(1, 4)  # '0001'
        shelf = self._dec_to_bin(shelf - 1, 4)  # '0000'
        slot = self._dec_to_bin(composite_index_slot, 8)
        port = self._dec_to_bin(port - 1, 8)  # (Port No. or (OLT No. - 1)
        srv_prt_id = self._dec_to_bin(0, 8)

        return str(int((index_type + shelf + slot + port + srv_prt_id), 2))
    

    def encode_gpon_olt_ifindex_type_one(self, shelf: int, slot: int, port: int):

        index_type = self._dec_to_bin(1, 4)  # '0001'
        rack = self._dec_to_bin(1, 4)  # 'RACK -> 1'
        shelf = self._dec_to_bin(shelf, 8)
        slot = self._dec_to_bin(slot, 8)
        port = self._dec_to_bin(port, 8)  # (Port No. or (OLT No. - 1)

        return str(int((index_type + rack + shelf + slot + port), 2))

    def _dec_to_bin(self, decimal, bits):
        bnr = bin(decimal).replace('0b', '')
        x = bnr[::-1]

        while len(x) < bits:
            x += '0'
        bnr = x[::-1]
        return bnr
    
    def __repr__(self) -> str:
            return self.hardware_ver

def register() -> None:
    """Registro de módulo"""
    factory.register("zte", Zte)
    