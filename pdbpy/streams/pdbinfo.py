import ctypes

from pdbpy.msf import MultiStreamFileStream

from dtypes.structify import (Structy, structify)
from dtypes.typedefs import (uint8_t, uint16_t, uint32_t)

@structify
class GUID(Structy):
    data1: uint32_t
    data2: uint16_t
    data3: uint16_t
    data4: uint8_t * 8

    def __repr__(self):
        return f"{self.data1:X}-{self.data2:X}-{self.data3:X}-" + "".join(f"{x:X}" for x in self.data4)

@structify
class PDBInfoHeader(Structy):
    version: uint32_t
    version_timestamp: uint32_t
    age: uint32_t
    guid: GUID
    byte_count_for_names: uint32_t


class PdbInfoStream:
    def __init__(self, file: MultiStreamFileStream):
        self.file = file
        mem = self.file[:]
        stuff = PDBInfoHeader.from_buffer_copy(mem)
        for name, _ in stuff._fields_:
            setattr(self, name, getattr(stuff, name))
        
        header_size = ctypes.sizeof(stuff)
        self.names = bytes(mem[header_size : header_size + self.byte_count_for_names])

    def __repr__(self):
        return str(self.__dict__)
