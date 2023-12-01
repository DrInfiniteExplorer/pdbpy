from ctypes import sizeof as c_sizeof

from dtypes.structify import structify
from dtypes.typedefs import uint16_t

from .base import record, PackedStructy, buffy, TypeProperties, read_numeric, read_string
from ..leaf_enum import LeafID
from ...typing import type_index


structy_types = (LeafID.CLASS, LeafID.STRUCTURE, LeafID.INTERFACE, LeafID.CLASS_ST, LeafID.STRUCTURE_ST, LeafID.INTERFACE)

@record(*structy_types)
@structify
class TypeStructLike(PackedStructy):
    record_type   : uint16_t
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
    
    @classmethod
    def from_memory(cls, mem, offset, record_size : 'Optional[int]', debug : bool):


        header_sizeof = c_sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset , offset + header_sizeof))
        self.addr = offset
        #print(self)

        # Name reading from https://github.com/microsoft/microsoft-pdb/blob/e6b1dec61e154b568357537792e1d17a13525d5d/PDB/include/symtypeutils.h#L24        
        #print(bytes(mem[offset : offset + header_sizeof : 'copy']))
        #print(bytes(mem[offset : offset + self.size_bytes : 'copy']))
        #print(bytes(mem[offset + header_sizeof : offset + self.size_bytes: 'copy']))
        name_offset, self.struct_size_bytes = read_numeric(mem, offset + header_sizeof)
        #print(f"x={x}")
        #name_data = buffy(mem, name_offset , offset + self.size_bytes)
        #print(SzBytesToString(bytes(name_data)))
        
        post_read_offset, name_data = read_string(mem, name_offset, self.record_type)
        self.name = name_data
        if self.properties.has_unique_name:
            post_read_offset, self.unique_name = read_string(mem, post_read_offset, self.record_type)
            #print(self.unique_name)
        #print(self.name)


        return post_read_offset, self
    


        
        #fields_byte_count =  
        