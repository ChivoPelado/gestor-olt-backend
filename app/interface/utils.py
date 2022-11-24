from dataclasses import dataclass


@dataclass
class Payload:
    olt_type: str
    olt_name: str
    olt_ip_address: str
    ssh_port: int
    ssh_user: str
    ssh_password: str
    snmp_port: str
    snmp_read_com: str
    snmp_write_com: str
    onu_interface: str
    shelf: int
    slot: int
    port: int
    index: int


def encoded_gpon_onu_index(payload: Payload):
    index_type = _dec_to_bin(1, 4)  # '0001'
    shelf = _dec_to_bin(payload.shelf - 1, 4)  # '0000'
    slot = _dec_to_bin(payload.slot, 8)
    port = _dec_to_bin(payload.port, 8)
    srv_prt_id = _dec_to_bin(0, 8)

    return str(int((index_type + shelf + slot + port + srv_prt_id), 2)) + "." + str(payload.index)

def decode_gpon_onu_index(encoded_onu):
    onu = encoded_onu.split(".")
    onu_bin = _dec_to_bin(int(onu[0]), 32)

    index_type = onu_bin[0:4]
    shelf = onu_bin[4:8]
    slot = onu_bin[8:16]
    port = onu_bin[16:24]
    srv_prt_id = onu_bin[24:32]

    return [int(shelf, 2) + 1, int(slot, 2), int(port, 2), int(onu[1])]

def _dec_to_bin(decimal, bits):
    bnr = bin(decimal).replace('0b', '')
    x = bnr[::-1]

    while len(x) < bits:
        x += '0'
    bnr = x[::-1]
    return bnr