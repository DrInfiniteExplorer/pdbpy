from ctypes import sizeof as c_sizeof

from dtypes.structify import structify
from dtypes.typedefs import uint16_t

from pdbpy.parsing import read_numeric, read_string

from .base import record, PackedStructy, FieldAttributes
from pdbpy.codeview import LeafID


@record(LeafID.ENUMERATE, LeafID.ENUMERATE_ST)
@structify
class Enumerate(PackedStructy):
    record_type     : uint16_t
    attributes      : FieldAttributes
    #value           : uint16_t # should be ReadNumeric?
    # name

    @classmethod
    def from_memory(cls, mem: memoryview, offset: int, record_size: int, debug : bool):
        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(mem[offset: offset + my_size])
        self.addr = offset
        post_read_offset = offset + my_size

        post_read_offset, self.value = read_numeric(mem, post_read_offset)
        post_read_offset, self.name  = read_string(mem, post_read_offset, self.record_type)

        return post_read_offset, self
