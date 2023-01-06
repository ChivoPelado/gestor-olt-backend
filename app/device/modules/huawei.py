"""Agrega modulo para interactuar con olt Huawei."""

from typing import List
from app.device.base import factory
from app.device.base.device_base import OltDeviceBase
from app.device.base.interface import IOnu, IOnuType

DEFAULT_LINE_PROFILE_ID = 2
DEFAULT_LINE_PROFILE_NAME = "SMARTOLT_FLEXIBLE_GPON"
GEMPORT = 1
PRIORITY = 0

class Huawei(OltDeviceBase):
    """Modulo de gestión de comandos de equipo Huawei"""

    def __init__(self, hardware_ver: str, device_type: str, software_ver: List, pon_type: List[str], 
        port_begin: int, cards: List[dict[str: any]], command: dict[str: any], MIB: dict[str: str]) -> None:
        super().__init__(hardware_ver, device_type, software_ver, pon_type, port_begin, cards, command, MIB)
    

    def get_shelf(self) -> dict[str: any]:
        olt_shelf =  super().excecute_and_parse(self.command['get_olt_shelf'])

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
    
    def get_srvcprt_and_onu_index(self, shelf: int, slot: int, port: int, vlan: int = None) -> tuple:
        """ Metodo interno para determinar service port disponible desde una secuencia"""
        
        olt_interface = f"{shelf}/{slot}/{port}"
        return self._get_srvcprt_and_onu_index(olt_interface, vlan)


    def authorize_onu(self, onu: IOnu, onu_type: IOnuType):

        olt_interface = f"gpon {onu.shelf}/{onu.slot}"
        olt_interface_port = f"{onu.shelf}/{onu.slot}/{onu.port_no}"

        onu_sn = onu.serial_no
        vendor_hex = onu_sn[:4].encode("utf-8").hex() + onu_sn[4:]

        onu_name_dscr = onu.name.replace(" ", "_") + '_descr_' + onu.comment.replace(" ", "_")

        commands = []

        commands += [self.command['enter_configutation_mode']]
        commands += [self.command['select_interface'] % olt_interface]
        commands += [self.command['ont_add'] % (onu.port_no, onu.index, vendor_hex, DEFAULT_LINE_PROFILE_NAME, onu_type.name, onu_name_dscr)]

        """ if onu.onu_mode == "Bridging":
            commands += self.set_onu_mode_bridging(onu, onu_type) """

        commands += [self.command['exit_mode']]
        commands += [self.command['set_srvc_port'] % (onu.srvc_port, onu.vlan, olt_interface_port, onu.index, GEMPORT, onu.vlan, onu.upload_speed, onu.download_speed)]
        commands += [self.command['exit_mode']]
        commands += [self.command['exit_mode']]

        #result = super().excecute(commands, expect_string='[#\?$]')

        try:
            result = super().excecute(commands, expect_string='[#\?$]')

            if onu.onu_mode == "Routing":
                self.set_onu_mode_routing(onu, onu_type)

            else:
                self.set_onu_mode_bridging(onu, onu_type)
        
        except Exception as err:
            print("Error en proceso de autorización de ONT: ", err)
            #return False

        return result


    def set_onu_mode_routing(self, onu: IOnu, onu_type: IOnuType ) -> List[str]:

        olt_interface = f"gpon {onu.shelf}/{onu.slot}"
        
        commands = []

        commands += [self.command['enter_configutation_mode']]
        commands += [self.command['select_interface'] % olt_interface]

        for index in range(onu_type.ethernet_ports):
            eth = f"eth {index + 1}"
            commands += [self.command['remove_mode_bridge'] % (onu.port_no, onu.index, eth, PRIORITY)]

        for index in range(onu_type.ethernet_ports):
            eth = f"eth {index + 1}"
            commands += [self.command['set_mode_routing'] % (onu.port_no, onu.index, eth) ]

        commands += [self.command['exit_mode']]
        commands += [self.command['exit_mode']]

        try:
            result = super().excecute(commands, expect_string='[#\?$]')
        except Exception as err:
            print("Error en proceso de de cambio de modo a a Routing de ONT: ", err)
            return False

        return True
        
        #return commands


    def set_onu_mode_bridging(self, onu: IOnu, onu_type: IOnuType) -> List[str]:
       
        olt_interface = f"gpon {onu.shelf}/{onu.slot}"
        
        commands = []

        commands += [self.command['enter_configutation_mode']]
        commands += [self.command['select_interface'] % olt_interface]

        for index in range(onu_type.ethernet_ports):
            eth = f"eth {index + 1}"
            commands += [self.command['remove_mode_routing'] % (onu.port_no, onu.index, eth)]

        for index in range(onu_type.ethernet_ports):
            eth = f"eth {index + 1}"
            commands += [self.command['set_mode_bridge'] % (onu.port_no, onu.index, eth, onu.vlan, PRIORITY) ]

        commands += [self.command['exit_mode']]
        commands += [self.command['exit_mode']]

        try:
            result = super().excecute(commands, expect_string='[#\?$]')
        except Exception as err:
            print("Error en proceso de de cambio de modo a a Bridging de ONT: ", err)
            return False

        return True


    def enable_catv(self, onu: IOnu) -> bool:
           
        olt_interface = f"gpon {onu.shelf}/{onu.slot}"
        commands = []

        commands += [self.command['enter_configutation_mode']]
        commands += [self.command['select_interface'] % olt_interface]
        commands += [self.command['activate_catv'] % (onu.port_no, onu.index)]
        commands += [self.command['exit_mode']]
        commands += [self.command['exit_mode']]

        try:
            result = super().excecute(commands, expect_string='[#\?$]')
        except Exception as err:
            print("Error en proceso de activación de CATV: ", err)
            return False

        return True


    def disable_catv(self, onu: IOnu) -> bool:
           
        olt_interface = f"gpon {onu.shelf}/{onu.slot}"
        commands = []

        commands += [self.command['enter_configutation_mode']]
        commands += [self.command['select_interface'] % olt_interface]
        commands += [self.command['deactivate_catv'] % (onu.port_no, onu.index)]
        commands += [self.command['exit_mode']]
        commands += [self.command['exit_mode']]

        try:
            result = super().excecute(commands, expect_string='[#\?$]')
        except Exception as err:
            print("Error en proceso de desactivación de CATV: ", err)
            return False

        return True


    def resync_onu(self, onu: IOnu, onu_type: IOnuType) -> bool:
        
        try:
            self.delete_onu(onu)
            self.authorize_onu(onu, onu_type)

        except Exception as err:
            print("Existió un error al resincronizar ONT ", err)

        return True


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


    def get_onu_rx(self, onu: IOnu):

        shelf = int(onu.shelf)
        slot = int(onu.slot)
        port = int(onu.port_no)
        index = str(onu.index)

        oid = self.MIB['HUAWEI-XPON-MIB::hwGponOntOpticalDdmRxPower'] + self._encode_ifindex(shelf, slot, port) + '.' + index

        result = super()._snmp_query(oid)

        level = round((int(result[oid]) / 100), 2)

        return 0 if level == 21474836.47 else level


    def get_olt_rx(self, onu: IOnu):

        shelf = int(onu.shelf)
        slot = int(onu.slot)
        port = int(onu.port_no)
        index = str(onu.index)

        oid = self.MIB['HUAWEI-XPON-MIB::hwGponOntOpticalDdmOltRxOntPower'] + self._encode_ifindex(shelf, slot, port) + '.' + index

        result = super()._snmp_query(oid)

        level = round((result[oid] - 10000) / 100, 2)

        return 0 if level == 21474736.47 else level 


    def get_onu_state(self, onu: IOnu):

        shelf = int(onu.shelf)
        slot = int(onu.slot)
        port = int(onu.port_no)
        index = str(onu.index)
        
        oid = self.MIB['HUAWEI-XPON-MIB::hwGponDeviceOntControlRunStatus'] + self._encode_ifindex(shelf, slot, port) + '.' + index

        result = super()._snmp_query(oid)

        result = int(result[oid])

        if result == 1:
            return "En Línea"
        
        return self._get_down_cause(onu)

    def delete_onu(self, onu: IOnu) -> bool:

        olt_interface = f"gpon {onu.shelf}/{onu.slot}"

        commands = []

        try:
            commands += [self.command['enter_configutation_mode']]
            commands += [self.command['delete_srvc_port'] % onu.srvc_port]
            commands += [self.command['select_interface'] % olt_interface]
            commands += [self.command['delete_onu'] % (onu.port_no, onu.index)]
            commands += [self.command['exit_mode']]
            commands += [self.command['exit_mode']]

            result = super().excecute(commands, expect_string='[#\?$]')
        except Exception as error:
            print(error)

            return False

        return True


    def deactivate_onu(self, onu: IOnu) -> bool:

        olt_interface = f"gpon {onu.shelf}/{onu.slot}"

        commands = []

        try:
            commands += [self.command['enter_configutation_mode']]
            commands += [self.command['select_interface'] % olt_interface]
            commands += [self.command['deactivate_onu'] % (onu.port_no, onu.index)]
            commands += [self.command['exit_mode']]
            commands += [self.command['exit_mode']]

            result = super().excecute(commands, expect_string='[#\?$]')

        except Exception as error:
            print(error)

            return False

        return True


    def activate_onu(self, onu: IOnu) -> bool:

        olt_interface = f"gpon {onu.shelf}/{onu.slot}"

        commands = []

        try:
            commands += [self.command['enter_configutation_mode']]
            commands += [self.command['select_interface'] % olt_interface]
            commands += [self.command['activate_onu'] % (onu.port_no, onu.index)]
            commands += [self.command['exit_mode']]
            commands += [self.command['exit_mode']]

            result = super().excecute(commands, expect_string='[#\?$]')

        except Exception as error:
            print(error)

            return False

        return True


    def reboot_onu(self, onu: IOnu) -> bool:

        olt_interface = f"gpon {onu.shelf}/{onu.slot}"

        commands = []

        try:
            commands += [self.command['enter_configutation_mode']]
            commands += [self.command['select_interface'] % olt_interface]
            commands += [self.command['reboot_onu'] % (onu.port_no, onu.index)]
            commands += [self.command['confirm']]
            commands += [self.command['exit_mode']]
            commands += [self.command['exit_mode']]

            result = super().excecute(commands, expect_string='[#\?$]')

        except Exception as error:
            print(error)

            return False

        return True


    def show_onu_running_config(self, onu: IOnu):

        onu_interface = f"{onu.shelf}/{onu.slot}/{onu.port_no} {onu.index}"

        commands = []

        get_onu_running = self.command['show_onu_running_config'] % onu_interface

       
        try:
            commands += [get_onu_running]
            commands += [self.command['exit_mode']]

            result = super().excecute(commands, expect_string='[#\?$]')

        
        except Exception as error:
            print(error)

        return result.get(get_onu_running)

    def show_onu_general_status(self, onu: IOnu):
        pass


   ############################################################
    # Helper Methods 
    ############################################################

    def  _get_down_cause(self, onu: IOnu):

        shelf = int(onu.shelf)
        slot = int(onu.slot)
        port = int(onu.port_no)
        index = str(onu.index)
        
        oid = self.MIB['HUAWEI-XPON-MIB::hwGponDeviceOntControlLastDownCause'] + self._encode_ifindex(shelf, slot, port) + '.' + index

        result = super()._snmp_query(oid)

        result = int(result[oid])

        # Complementar https://ixnfo.com/en/oid-and-mib-for-huawei-olt-and-onu.html
        state = "LOS" if result == 1  else "Falla Eléctrica" if result == 13 else "Deshabilitada" if result == 8 else"Otro \ Desconocido" 

        return state
    



    def get_srvcprt_and_onu_index(self, shelf: int, slot: int, port: int, vlan: int = None) -> tuple:
        """ Metodo interno para determinar service port disponible desde una secuencia"""
        
        olt_interface = f"{shelf}/{slot}/{port}"
        return self._get_srvcprt_and_onu_index(olt_interface, vlan)


    def _get_srvcprt_and_onu_index(self, olt_interface: str, vlan: int) -> tuple:
        """ Metodo interno para determinar service port disponible desde una secuencia"""

       # Se obtiene onus desde una interface OLT
        parsed_response = super().excecute_and_parse(self.command['get_srvc-prt_sort_by_vlan'] % olt_interface)

        # Se extraen los service-port usados a una lista
        srvcprt = []
        indexes = []
        available_srvcprt = int
        available_index = int

        for res in parsed_response:
            
            indexes.append(int(res['onu_index']))
            if int(res['vlan_id']) == vlan:
                srvcprt.append(int(res['srv_prt']))

        if len(srvcprt) > 1:
            try:
                srvcprt.sort()
                # Si existen fatantes en la secuencia, los enlista
                available_srvcprt = [index for index in range(srvcprt[0], srvcprt[-1]+1) if index not in srvcprt]

                # Extrae el primer faltante en la secuencia
                available_srvcprt = available_srvcprt[0]

                # Si no existen faltantes en la secuencia, entregár el indice siguiente
                if not available_srvcprt:
                    available_srvcprt = srvcprt.pop() + 1

            except IndexError:
                # La vlan provista no ha sido asignada a ninguna ont en esta interface, por ende 1
                available_srvcprt = 1
        else:
            available_srvcprt = srvcprt.pop() + 1

        if len(indexes) > 1:
            indexes.sort()

            # Si existen fatantes en la secuencia, los enlista
            available_index = [index for index in range(indexes[0], indexes[-1]+1) if index not in indexes]

            # Extrae el primer faltante en la secuencia
            available_index = available_index[0]

            # Si no existen faltantes en la secuencia, entregár el indice siguiente
            if not available_index:
                available_index = indexes.pop() + 1
        else:
            available_index = indexes.pop() + 1


        # Retorna el indice
        return available_srvcprt, available_index


    def _encode_ifindex(self, shelf: int, slot: int, port: int):
        """Determina el indice codificado de la interface"""

        return str((4194304000 + (slot * (256 * 32)) + port * 256))

    def __repr__(self) -> str:
        return self.hardware_ver
   

############################################################
# REGISTRO DE MODULO
############################################################

def register() -> None:
    factory.register("huawei", Huawei)