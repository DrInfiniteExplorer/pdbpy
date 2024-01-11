from ctypes import sizeof as c_sizeof
from typing import Optional

from dtypes.structify import structify
from dtypes.typedefs import uint16_t

from pdbpy.codeview import LeafID
from pdbpy.codeview.types import type_index

from .base import record, PackedStructy


@record(LeafID.VFUNCTAB)
@structify
class VFuncTab(PackedStructy):
    record_type     : uint16_t
    padding         : uint16_t
    vtable_ptr      : type_index

    @classmethod
    def from_memory(cls, mem : memoryview, offset : int, record_size : Optional[int], debug : bool):
        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(mem[offset: offset + my_size])
        self.addr = offset
        post_read_offset = offset + my_size

        return post_read_offset, self


__all__ = ('VFuncTab',)
