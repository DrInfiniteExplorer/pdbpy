from ctypes import sizeof as c_sizeof
from typing import Optional

from dtypes.structify import structify
from dtypes.typedefs import uint16_t

from pdbpy.codeview.types import type_index

from .base import record, PackedStructy, FieldAttributes
from pdbpy.codeview import LeafID

@record(LeafID.ONEMETHOD)
@structify
class OneMethod(PackedStructy):
    """
    Non-overridden method
    """
    record_type     : uint16_t
    attributes      : FieldAttributes
    method_type     : type_index
    # vtable_offset
    # name


    @classmethod
    def from_memory(cls, mem : memoryview, offset : int, record_size : Optional[int], debug : bool):
        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(mem[offset: offset + my_size])
        self.addr = offset
    
        post_read_offset = offset + my_size
        if self.attributes.mprop in (MethodPropertiesEnum.intro, MethodPropertiesEnum.pureintro):
            self.vtable_offset = uint32_t.from_buffer_copy(mem[post_read_offset: post_read_offset+4])
            post_read_offset += 4
        post_read_offset, self.name = read_string(mem, post_read_offset, self.record_type)

        return post_read_offset, self


__all__ = ('OneMethod',)
