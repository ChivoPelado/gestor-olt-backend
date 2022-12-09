"""Agrega modulo para interactuar con olt ZTE."""

from dataclasses import dataclass
from typing import List
from app.device.base import factory
from app.device.base.device_base import OltDeviceBase


@dataclass
class Zte(OltDeviceBase):
    """Modulo de gestión de comandos de equipo ZTE"""

    def get_cards(self) -> List[dict[str: any]]:
        """ Devuelve las tarjetas de OLT instaladas"""

        response = []
        card = {}
        parsed_response = OltDeviceBase.get_cards(self)

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
    
    def __repr__(self) -> str:
        return self.hardware_ver

def register() -> None:
    """Registro de módulo"""
    factory.register("zte", Zte)
    