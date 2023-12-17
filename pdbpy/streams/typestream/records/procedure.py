from ctypes import sizeof as c_sizeof
from typing import Optional

from dtypes.structify import structify
from dtypes.typedefs import uint8_t, uint16_t

from pdbpy.codeview import LeafID

from .base import record, PackedStructy, FunctionAttributes
from ...typing import type_index


@record(LeafID.PROCEDURE)
@structify
class Procedure(PackedStructy):
    record_type     : uint16_t
    return_type     : type_index
    call_convention : uint8_t
    func_attributes : FunctionAttributes
    parameter_count : uint16_t
    arg_list        : type_index


    @classmethod
    def from_memory(cls, mem : memoryview, offset : int, record_size : Optional[int], debug : bool):
        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(mem[offset: offset + my_size])
        self.addr = offset
        post_read_offset = offset + my_size

        return post_read_offset, self
