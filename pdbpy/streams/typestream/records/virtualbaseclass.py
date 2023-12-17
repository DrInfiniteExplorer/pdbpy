from ctypes import sizeof as c_sizeof
from typing import Optional

from dtypes.structify import structify
from dtypes.typedefs import uint16_t, uint32_t

from pdbpy.codeview import LeafID

from .base import record, PackedStructy, FieldAttributes
from ...typing import type_index

@record(LeafID.VBCLASS, LeafID.IVBCLASS)
@structify
class VirtualBaseClass(PackedStructy): # also indirect virtual
    record_type     : uint16_t
    attributes      : FieldAttributes
    base_class      : type_index
    base_ptr        : uint32_t
    base_ptr_offset : uint16_t
    virt_ptr_offset : uint16_t


    # offset

    @classmethod
    def from_memory(cls, mem : memoryview, offset : int, record_size : Optional[int], debug : bool):
        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(mem[offset: offset + my_size])
        self.addr = offset
        post_read_offset = offset + my_size

        return post_read_offset, self
