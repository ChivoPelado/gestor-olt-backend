from dataclasses import dataclass
from app.interface.protocols.snmp import get_request
from app.interface.task import Task
from app.core.schemas.system import Onu
from app.interface.utils import (
    decode_gpon_onu_index,
    encoded_gpon_onu_index
)

zte_mib = {
    'olt_rx': '1.3.6.1.4.1.3902.1015.1010.11.2.1.2.',
    'onu_rx': '1.3.6.1.4.1.3902.1012.3.50.12.1.1.10.',
    'onu_status': '1.3.6.1.4.1.3902.1012.3.28.2.1.4.',
    'onu_uncfg_sn': '1.3.6.1.4.1.3902.1012.3.13.3.1.2.'
}

@dataclass
class OnuSignal(Task):
    onu: Onu
    description = "Get ONU signal"

    @property
    def olt(self):
        return self.onu.olt

    def execute(self):

        olt_rx_oid = zte_mib['olt_rx'] + encoded_gpon_onu_index(self.onu)
        onu_rx_oid = zte_mib['onu_rx'] + encoded_gpon_onu_index(self.onu) + '.1'

        try:
            result = get_request(self.olt.ip_address, [olt_rx_oid, onu_rx_oid], self.olt.snmp_read_com, self.olt.snmp_port)

            onu_signal_1490 = round((int(result[olt_rx_oid]) / 1000), 2)
            onu_signal_1310 = self._get_onu_rx(int(result[onu_rx_oid]))
            onu_signal_value = f"{onu_signal_1310} dBm / {onu_signal_1490} dBm"

            return {
                'onu_signal_value': onu_signal_value,
                'onu_signal_1490': onu_signal_1490,
                'onu_signal_1310': onu_signal_1310
            }
        except ValueError:
            return {}

    def _get_onu_rx(self, snmp_value):
        if snmp_value == 65535:
            return 0
        elif snmp_value > 30000:
            return (snmp_value - 65536) * 0.002 - 30
        return round((snmp_value * 0.002 - 30), 2)