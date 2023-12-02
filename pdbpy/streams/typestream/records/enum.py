from ctypes import sizeof as c_sizeof

from dtypes.structify import structify
from dtypes.typedefs import uint16_t

from .base import record, PackedStructy, buffy, TypeProperties
from ..leaf_enum import LeafID
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
    def from_memory(cls, mem, offset, record_size : 'Optional[int]', debug : bool):
        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset
        post_read_offset = offset + my_size

        post_read_offset, self.name = ReadString(mem, post_read_offset, self.record_type)
        if self.properties.has_unique_name:
            post_read_offset, self.unique_name = ReadString(mem, post_read_offset, self.record_type)
        
        #print(record_size)
        #print("!!", bytes(buffy(mem, offset, offset+record_size)))
        #print(post_read_offset, bytes(buffy(mem, post_read_offset, post_read_offset+1)))

        return post_read_offset, self

assert Enum.underlying_type.offset == 6
