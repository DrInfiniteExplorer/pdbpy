from ctypes import sizeof as c_sizeof
from typing import Optional

from dtypes.structify import structify
from dtypes.typedefs import uint16_t

from .base import record, PackedStructy, PointerAttributes, PointerModeEnum
from ...typing import type_index
from pdbpy.codeview import LeafID

@record(LeafID.POINTER)
@structify
class Pointer(PackedStructy):

    record_type    : uint16_t
    reference_type : type_index
    attributes     : PointerAttributes

    @classmethod
    def from_memory(cls, mem : memoryview, offset : int, record_size : Optional[int], debug : bool):
        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(mem[offset: offset + my_size])
        self.addr = offset
        post_read_offset = offset + my_size

        # TODO
        # size according to https://llvm.org/docs/PDB/CodeViewTypes.html        
        # but https://pierrelib.pagesperso-orange.fr/exec_formats/MS_Symbol_Type_v1.0.pdf page 28
        # and https://github.com/moyix/pdbparse/blob/master/pdbparse/tpi.py#L896
        # and https://github.com/willglynn/pdb/blob/master/src/tpi/data.rs#L209-L224
        # all kinda disagree or something. yolo?
        
        if self.attributes.mode in (PointerModeEnum.Member, PointerModeEnum.MemberFunction):
            if self.attributes.kind == PointerTypeEnum.BITS_64:
                post_read_offset += 8
            else:
                assert False, f"Can't deal with {self.attributes.kind.name} for pointer size increase of {self}? 🤔"
        
        assert post_read_offset == offset + record_size, f"{post_read_offset} != {offset + record_size}\n{self}"
        return post_read_offset, self
