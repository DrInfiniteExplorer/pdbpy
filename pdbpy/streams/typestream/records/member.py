from ctypes import sizeof as c_sizeof
from typing import Optional

from dtypes.structify import structify
from dtypes.typedefs import uint16_t
from pdbpy.codeview.types import type_index

from pdbpy.parsing import read_numeric, read_string

from .base import record, PackedStructy, FieldAttributes
from pdbpy.codeview import LeafID

@record(LeafID.MEMBER, LeafID.MEMBER_ST, LeafID.STMEMBER, LeafID.STMEMBER_ST)
@structify
class Member(PackedStructy):
    record_type      : uint16_t
    field_attributes : FieldAttributes
    field_type       : type_index
    #static
    #offset
    #name

    @classmethod
    def from_memory(cls, mem: memoryview, offset: int, record_size: Optional[int], debug : bool):
        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(mem[offset: offset + my_size])
        self.addr = offset

        post_read_offset = offset + my_size
        self.static = self.record_type in (LeafID.STMEMBER, LeafID.STMEMBER_ST)

        if not self.static:
            post_read_offset, self.offset = read_numeric(mem, post_read_offset)
        post_read_offset, self.name = read_string(mem, post_read_offset, self.record_type)

        return post_read_offset, self

__all__ = ('Member',)