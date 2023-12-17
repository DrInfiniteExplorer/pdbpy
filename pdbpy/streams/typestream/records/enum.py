from ctypes import sizeof as c_sizeof

from dtypes.structify import structify
from dtypes.typedefs import uint16_t

from pdbpy.parsing import read_string

from .base import record, PackedStructy, TypeProperties
from pdbpy.codeview import LeafID
from ...typing import type_index

@record(LeafID.ENUM, LeafID.ENUM_ST)
@structify
class Enum(PackedStructy):
    _pack_ = 2
    record_type     : uint16_t
    count           : uint16_t
    properties      : TypeProperties
    underlying_type : type_index
    fields          : type_index
    # name
    # unique_name

    @classmethod
    def from_memory(cls, mem: memoryview, offset: int, record_size: int, debug : bool):
        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(mem[offset: offset + my_size])
        self.addr = offset
        post_read_offset = offset + my_size

        post_read_offset, self.name = read_string(mem, post_read_offset, self.record_type)
        if self.properties.has_unique_name:
            post_read_offset, self.unique_name = read_string(mem, post_read_offset, self.record_type)

        return post_read_offset, self

assert Enum.underlying_type.offset == 6
