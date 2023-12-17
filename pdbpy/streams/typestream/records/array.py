from ctypes import sizeof as c_sizeof

from dtypes.structify import structify
from dtypes.typedefs import uint16_t

from pdbpy.parsing import read_numeric, read_string

from .base import record, PackedStructy
from pdbpy.codeview import LeafID
from ...typing import type_index

@record(LeafID.ARRAY)
@structify
class Array(PackedStructy):
    record_type     : uint16_t
    element_type    : type_index
    index_type      : type_index
    # array_size_bytes
    # name


    @classmethod
    def from_memory(cls, mem: memoryview, offset: int, record_size : int, debug : bool):

        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(mem[offset:offset + my_size])
        self.addr = offset
        post_read_offset = offset + my_size

        post_read_offset, self.array_size_bytes = read_numeric(mem, post_read_offset)
        post_read_offset, self.name = read_string(mem, post_read_offset, self.record_type)
        #print(f"Array bytecount: {self.array_size_bytes}")
        #print(f"Array name: {self.name}")
        #yeet()

        return post_read_offset, self
