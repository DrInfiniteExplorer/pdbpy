import struct

def get_hash_for_string(str):
    buff = str.encode('utf8')
    res = 0
    whole_uint32_count = int(len(buff)/4)
    for (u32,) in struct.iter_unpack("<I", buff[0:4 * whole_uint32_count]):
        res ^= u32
    rem = buff[whole_uint32_count * 4:]

    if len(rem) > 1:
        res ^= struct.unpack_from("<H", buffer=rem, offset = 0)[0]
        rem = rem[2:]
    if len(rem):
        res ^= struct.unpack_from("<B", buffer=rem, offset = 0)[0]
    
    to_lower_mask = 0x20202020
    res |= to_lower_mask
    res ^= res >> 11
    res ^= res >> 16

    return res
