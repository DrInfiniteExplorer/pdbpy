from ctypes import sizeof as c_sizeof

from dtypes.structify import structify
from dtypes.typedefs import uint16_t

from .base import record, PackedStructy, buffy, FieldAttributes
from ..leaf_enum import LeafID
from ...typing import type_index

@record(LeafID.ONEMETHOD)
@structify
class OneMethod(PackedStructy):
    record_type     : uint16_t
    attributes      : FieldAttributes
    method_type     : type_index
    # vtable_offset
    # name


    @classmethod
    def from_memory(cls, mem, offset, record_size : 'Optional[int]', debug : bool):
        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset
    
        post_read_offset = offset + my_size
        if self.attributes.mprop in (MethodPropertiesEnum.intro, MethodPropertiesEnum.pureintro):
            self.vtable_offset = uint32_t.from_buffer_copy(buffy(mem, post_read_offset, post_read_offset+4))
            post_read_offset += 4
        post_read_offset, self.name = ReadString(mem, post_read_offset, self.record_type)

        return post_read_offset, self

