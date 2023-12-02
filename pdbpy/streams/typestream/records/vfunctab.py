from ctypes import sizeof as c_sizeof

from dtypes.structify import structify
from dtypes.typedefs import uint16_t

from .base import record, PackedStructy, buffy
from ..leaf_enum import LeafID
from ...typing import type_index


@record(LeafID.VFUNCTAB)
@structify
class VFuncTab(PackedStructy):
    record_type     : uint16_t
    padding         : uint16_t
    vtable_ptr      : type_index

    @classmethod
    def from_memory(cls, mem, offset, record_size : 'Optional[int]', debug : bool):
        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset
        post_read_offset = offset + my_size

        return post_read_offset, self

