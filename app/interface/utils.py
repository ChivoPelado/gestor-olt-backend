from app.core.schemas.system import Onu

def encoded_gpon_onu_index(onu: Onu):
    index_type = _dec_to_bin(1, 4)  # '0001'
    shelf = _dec_to_bin(onu.shelf - 1, 4)  # '0000'
    slot = _dec_to_bin(onu.slot, 8)
    port = _dec_to_bin(onu.port, 8)
    srv_prt_id = _dec_to_bin(0, 8)

    return str(int((index_type + shelf + slot + port + srv_prt_id), 2)) + "." + str(onu.index)

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