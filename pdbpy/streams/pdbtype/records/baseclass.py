from ctypes import sizeof as c_sizeof

from dtypes.structify import structify
from dtypes.typedefs import uint16_t

from .base import record, PackedStructy, buffy, FieldAttributes
from ..leaf_enum import LeafID
from ...typing import type_index


@record(LeafID.BCLASS, LeafID.INTERFACE)
@structify
class BaseClass(PackedStructy):
    record_type     : uint16_t
    attributes      : FieldAttributes
    index           : type_index
    # offset

    @classmethod
    def from_memory(cls, mem, offset, record_size : 'Optional[int]', debug : bool):
        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset
        post_read_offset = offset + my_size

        post_read_offset, self.offset = ReadNumeric(mem, post_read_offset)

        return post_read_offset, self
