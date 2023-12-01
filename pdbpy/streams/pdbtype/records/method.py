from ctypes import sizeof as c_sizeof

from dtypes.structify import structify
from dtypes.typedefs import uint16_t

from .base import record, PackedStructy, buffy
from ..leaf_enum import LeafID
from ...typing import type_index


@record(LeafID.METHOD)
@structify
class Method(PackedStructy):
    record_type     : uint16_t
    count           : uint16_t
    method_list     : type_index
    # name


    @classmethod
    def from_memory(cls, mem, offset, record_size : int, debug : bool):

        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset
        post_read_offset = offset + my_size

        post_read_offset, self.name  = ReadString(mem, post_read_offset, self.record_type)

        return post_read_offset, self
