from ctypes import sizeof as c_sizeof

from dtypes.structify import structify
from dtypes.typedefs import uint16_t

from .base import PackedStructy, buffy
from ...typing import type_index

@structify
# https://github.com/microsoft/microsoft-pdb/blob/1d60e041600117a5004de84baa960d2c953a6aa6/include/cvinfo.h#L1175
class CodeViewRecordHeader(PackedStructy):    
    """
    """
    size_bytes : uint16_t
    record_type: uint16_t # called 'leaf' by dudes but they are pretty far from leafs most of the time 🤔

    # ti : type_index

    @classmethod
    def from_memory(cls, mem, offset, record_size : 'Optional[int]', debug : bool):
        my_size = c_sizeof(cls)
        post_read_offset = offset + my_size
        self = CodeViewRecordHeader.from_buffer_copy(buffy(mem, offset,  offset + my_size))

        return post_read_offset, self
