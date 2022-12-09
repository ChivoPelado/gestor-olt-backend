"""Agrega modulo para interactuar con olt Huawei."""

from dataclasses import dataclass
from typing import List
from app.device.base import factory
from app.device.base.device_base import OltDeviceBase


@dataclass
class Huawei(OltDeviceBase):
    """Modulo de gestión de comandos de equipo Huawei"""

       
    def get_uncfg_onus(self) -> dict[str: any]:
        """ Ajusta la respuesta dando formato a el SN """
        response = []
        parsed_response = OltDeviceBase.get_uncfg_onus(self)
        
        for data in parsed_response:
            data['sn'] = data['sn'].replace("-", "")
            response.append(data)
   
        return response
    
    
    def get_cards(self) -> List[dict[str: any]]:
        """ Devuelve las tarjetas de OLT instaladas"""

        response = []
        card = {}
        parsed_response = OltDeviceBase.get_cards(self)

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
    
    def __repr__(self) -> str:
        return self.hardware_ver
   
def register() -> None:
    factory.register("huawei", Huawei)