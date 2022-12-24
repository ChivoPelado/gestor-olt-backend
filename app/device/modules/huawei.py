"""Agrega modulo para interactuar con olt Huawei."""

from typing import List
from app.device.base import factory
from app.device.base.device_base import OltDeviceBase



class Huawei(OltDeviceBase):
    """Modulo de gestión de comandos de equipo Huawei"""

    def __init__(self, hardware_ver: str, device_type: str, software_ver: List, pon_type: List[str], 
        port_begin: int, cards: List[dict[str: any]], command: dict[str: any], MIB: dict[str: str]) -> None:
        super().__init__(hardware_ver, device_type, software_ver, pon_type, port_begin, cards, command, MIB)
    

    def get_shelf(self) -> dict[str: any]:
        olt_shelf =  super().excecute_and_parse(self.command['get_olt_shelf'])

        print(olt_shelf)

        shelf = {}

        shelf['shelf'] = olt_shelf[0]['frame_id']
        shelf['type'] = olt_shelf[0]['frame_desc']
        shelf['shelf_sn'] = olt_shelf[0]['frame_sn']

        return shelf

    
    def get_uncfg_onus(self) -> dict[str: any]:
        """ Ajusta la respuesta dando formato a el SN """
        response = []
        parsed_response = super().excecute_and_parse(self.command['get_uncfg_onu'])
        
        for data in parsed_response:
            data['sn'] = data['sn'].replace("-", "")
            response.append(data)
   
        return response
    
    
    def get_cards(self) -> List[dict[str: any]]:
        """ Devuelve las tarjetas de OLT instaladas"""

        response = []
        card = {}
        parsed_response = super().excecute_and_parse(self.command['get_cards'])

        for data in parsed_response:
            ports = 0
            role = None
            for data_card in self.cards:
                if data['type'] == data_card['name']:
                    ports = data_card['ports']
                    role = data_card['role']
            
            card['slot'] = int(data['slot'])
            card['type'] = data['type']
            card['real_type'] = data['type']
            card['port'] = ports
            card['soft_ver'] = ""
            card['status'] = data['status']
            card['role'] = role
            
            response.append(card.copy())

        return response


    def get_vlans(self) -> List[dict[str: any]]:
        """ Formatea la respuesta entregada desde la clase padre:
        Formato original Ex.->
        [
             {
                "vlan": "1",
                "type": "smart",
                "atribs": "common",
                "stndprt": "8",
                "srvprt": "0",
                "vlancon": "-"
            },
            ...
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
        reserved_vlans = ["1"]

        # Se obtiene el resultado original desde la clase Padre
        parsed_response = super().excecute_and_parse(self.command['get_vlans'])
        

        response = []
        vlan = {}
        for response_vlans in parsed_response:
            if response_vlans['vlan'] not in reserved_vlans:
                vlan['vlan'] = response_vlans['vlan']
                vlan['description'] = None            # Sin detalles
                vlan['scope'] = "Internet"            # Todas las VLANs al servicio de Internet
        
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

    def get_port_tx(self, shelf: int, slot: int, port: int):

        oid = self.MIB['HUAWEI-XPON-MIB::hwGponOltOpticsDdmInfoTxPower'] + self._encode_ifindex(shelf, slot, port)

        result = super()._snmp_query(oid)
        level = round((int(result[oid]) / 100), 4)

        return 0 if level == 21474836.47 else level
    

    def get_port_status(self, shelf: int, slot: int, port: int):

        oid = self.MIB['HUAWEI-XPON-MIB::hwGponDeviceOltControlStatus'] + self._encode_ifindex(shelf, slot, port)

        result = super()._snmp_query(oid)
        status = int(result[oid])

        return "Arriba" if status == 1 else "Abajo  "


    def get_port_admin_state(self, shelf: int, slot: int, port: int):

        oid = self.MIB['HUAWEI-XPON-MIB::hwGponDeviceOltControlOpticModuleStatus'] + self._encode_ifindex(shelf, slot, port)

        result = super()._snmp_query(oid)
        status = int(result[oid])

        return "Habilitado" if status == 1 else "Deshabilitado"

    def get_port_description(self, shelf: int, slot: int, port: int):

        oid = self.MIB['HUAWEI-XPON-MIB::hwGponDeviceOltControlDespt'] + self._encode_ifindex(shelf, slot, port)

        result = super()._snmp_query(oid)

        return result[oid]


    def _encode_ifindex(self, shelf: int, slot: int, port: int):
        """Determina el indice codificado de la interface"""

        return str((4194304000 + (slot * (256 * 32)) + port * 256))

    def __repr__(self) -> str:
        return self.hardware_ver
   
    
def register() -> None:
    factory.register("huawei", Huawei)