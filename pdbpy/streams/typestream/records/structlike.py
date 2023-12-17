from ctypes import sizeof as c_sizeof
from typing import Optional

from dtypes.structify import structify
from dtypes.typedefs import uint16_t

from pdbpy.codeview import LeafID
from pdbpy.parsing import read_numeric, read_string

from .base import record, PackedStructy, TypeProperties
from ...typing import type_index


structy_types = (LeafID.CLASS, LeafID.STRUCTURE, LeafID.INTERFACE, LeafID.CLASS_ST, LeafID.STRUCTURE_ST, LeafID.INTERFACE)

@record(*structy_types)
@structify
class TypeStructLike(PackedStructy):
    _record_type   : uint16_t
    element_count : uint16_t
    properties    : TypeProperties
    fields        : type_index     # the record which contains the field list (ie. members n methods)
    derived       : type_index
    vshape        : type_index
    # followed by "data describing length of structure in bytes and name"? 🤔

    def __init__(self):
        self.addr = None
        self.struct_size_bytes = None
        self.name = None
        self.unique_name = None
    
    @property
    def record_type(self) -> int: return self._record_type  # type: ignore
    
    @classmethod
    def from_memory(cls, mem : memoryview, offset : int, record_size : Optional[int], debug : bool):


        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(mem[offset: offset + my_size])
        self.addr = offset
        #print(self)

        # Name reading from https://github.com/microsoft/microsoft-pdb/blob/e6b1dec61e154b568357537792e1d17a13525d5d/PDB/include/symtypeutils.h#L24        
        name_offset, self.struct_size_bytes = read_numeric(mem, offset + my_size)
        
        post_read_offset, name_data = read_string(mem, name_offset, self.record_type)
        self.name = name_data
        if self.properties.has_unique_name:
            post_read_offset, self.unique_name = read_string(mem, post_read_offset, self.record_type)
            #print(self.unique_name)
        #print(self.name)


        return post_read_offset, self
    


        
        #fields_byte_count =  
        