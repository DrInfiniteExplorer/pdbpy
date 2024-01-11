from ctypes import sizeof as c_sizeof

from dtypes.structify import structify
from dtypes.typedefs import uint16_t, uint8_t

from pdbpy.codeview.types import type_index

from .base import record, PackedStructy
from pdbpy.codeview import LeafID

@record(LeafID.BITFIELD)
@structify
class Bitfield(PackedStructy):
    record_type     : uint16_t
    base_type       : type_index
    length          : uint8_t
    position        : uint8_t

    @classmethod
    def from_memory(cls, mem: memoryview, offset: int, record_size : int, debug : bool):

        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(mem[offset: offset + my_size])
        self.addr = offset
        post_read_offset = offset + my_size

        return post_read_offset, self
__all__ = ('Bitfield',)