from ctypes import sizeof as c_sizeof
from typing import Optional

from dtypes.structify import structify
from dtypes.typedefs import uint16_t

from pdbpy.codeview.types import type_index

from .base import record, PackedStructy
from pdbpy.codeview import LeafID

@record(LeafID.MODIFIER)
@structify
class Modifier(PackedStructy):
    record_type     : uint16_t
    reference       : type_index
    flags           : uint16_t

    @classmethod
    def from_memory(cls, mem : memoryview, offset : int, record_size : Optional[int], debug : bool):
        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(mem[offset: offset + my_size])
        self.addr = offset
        post_read_offset = offset + my_size

        return post_read_offset, self

__all__ = ('Modifier',)
