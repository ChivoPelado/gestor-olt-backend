from dataclasses import dataclass
from app.interface.protocols.snmp import get_request
from app.interface.task import Task
from app.interface.utils import Payload
from app.interface.utils import (
    encode_gpon_onu_index_type_one
)

zte_mib = {
    'olt_rx': '1.3.6.1.4.1.3902.1015.1010.11.2.1.2.',
    'onu_rx': '1.3.6.1.4.1.3902.1012.3.50.12.1.1.10.',
    'onu_status': '1.3.6.1.4.1.3902.1012.3.28.2.1.4.',
    'onu_uncfg_sn': '1.3.6.1.4.1.3902.1012.3.13.3.1.2.',
    'port_tx_signal_level': '1.3.6.1.4.1.3902.1015.3.1.13.1.4.'
}

@dataclass
class PonTxSignal(Task):
    payload: Payload
    description = "Get PON Port signal"

    def execute(self):

        port_tx_oid = zte_mib['port_tx_signal_level'] + encode_gpon_onu_index_type_one(self.payload)

        try:
            result = get_request(self.payload.olt_ip_address, [port_tx_oid], self.payload.snmp_read_com, self.payload.snmp_port)
            level = round((int(result[port_tx_oid]) / 1000), 4)

            return 0 if level == 2147483.647 else level


        except ValueError:
            return {}

    def _get_onu_rx(self, snmp_value):
        if snmp_value == 65535:
            return 0
        elif snmp_value > 30000:
            return (snmp_value - 65536) * 0.002 - 30
        return round((snmp_value * 0.002 - 30), 2)