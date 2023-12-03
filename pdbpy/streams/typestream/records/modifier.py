from ctypes import sizeof as c_sizeof

from dtypes.structify import structify
from dtypes.typedefs import uint16_t

from .base import record, PackedStructy
from ..leaf_enum import LeafID
from ...typing import type_index

@record(LeafID.MODIFIER)
@structify
class Modifier(PackedStructy):
    record_type     : uint16_t
    reference       : type_index
    flags           : uint16_t

    @classmethod
    def from_memory(cls, mem, offset, record_size : 'Optional[int]', debug : bool):
        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(mem[offset: offset + my_size])
        self.addr = offset
        post_read_offset = offset + my_size

        return post_read_offset, self
