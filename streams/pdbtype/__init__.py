import ctypes

from .leaf_enum import LeafID

from pdbpy.msf import MultiStreamFileStream
from pdbpy.utils.ctypes import (Structy, Flaggy, structify,
    int8_t, int16_t, int32_t,
    uint8_t, uint16_t, uint32_t)

typ_t = uint32_t
type_index = typ_t


records_by_id = {}

def record(*type_ids):
    def the_types_tho(typ):
        for id_ in type_ids:
            records_by_id[id_] = typ
        typ.__record_types = [*type_ids]
        return typ
    return the_types_tho

def buffy(x, start, end):
    if isinstance(x, MultiStreamFileStream):
        return x[start : end : 'copy']
    return x[start : end]

@structify
# https://github.com/microsoft/microsoft-pdb/blob/1d60e041600117a5004de84baa960d2c953a6aa6/include/cvinfo.h#L1120
class TypeProperty(Flaggy):
    packed                : (uint16_t, 1)
    ctor                  : (uint16_t, 1)
    overloaded_operators  : (uint16_t, 1)
    is_nested             : (uint16_t, 1)
    contains_nested       : (uint16_t, 1)
    overloaded_assignment : (uint16_t, 1)
    overloaded_casts      : (uint16_t, 1)
    is_forward_definition : (uint16_t, 1)
    scoped_definition     : (uint16_t, 1)
    has_unique_name       : (uint16_t, 1) # a decorated name follows the regular name
    is_final              : (uint16_t, 1)
    hfa                   : (uint16_t, 2) # what is CV_HFA_e
    intrinsic             : (uint16_t, 1) # intrinsic type, like __m128d
    mocom                 : (uint16_t, 2) # what is CV_MOCOM_UDT_e









LeafNumericToCType = {
    LeafID.CHAR    : ctypes.c_char,
    LeafID.SHORT   : int16_t,
    LeafID.USHORT  : uint16_t,
    LeafID.LONG    : int32_t,
    LeafID.ULONG   : uint32_t,
    LeafID.REAL32  : ctypes.c_float,
    LeafID.REAL64  : ctypes.c_double,
    LeafID.REAL80  : ctypes.c_byte * 10,
    LeafID.REAL128 : ctypes.c_byte * 16,
}
def ReadNumeric(mem, offset):

    leaf_id = uint16_t.from_buffer_copy(mem[offset : offset + 2]).value
    data_offset = offset + 2

    match leaf_id:
        case int(id) if id < LeafID.NUMERIC:
            return data_offset, leaf_id
        case LeafID.VARSTRING:
            asd()
            length = uint16_t.from_buffer_copy(mem[data_offset : data_offset + 2])
            return data_offset + 2 + length, mem[data_offset + 2 : data_offset + 2 + length]
        case _:
            typ = LeafNumericToCType.get(leaf_id)
            #print(typ)
            #asd()

            size = ctypes.sizeof(typ)
            value = typ.from_buffer_copy(mem[data_offset : data_offset + size])
            return data_offset + size, value
    
    raise ValueError(f"How did we get here? {offset}, {leaf_id}, {data_offset}")


def SzBytesToString(data):
    return data[:data.index(0)].decode('utf8')


@structify
# https://github.com/microsoft/microsoft-pdb/blob/1d60e041600117a5004de84baa960d2c953a6aa6/include/cvinfo.h#L1175
class PDBTypesType(Structy):    
    size_bytes : uint16_t
    record_type: uint16_t # called 'leaf' by dudes but they are pretty far from leafs most of the time 🤔

@record(LeafID.CLASS, LeafID.STRUCTURE, LeafID.INTERFACE)
@structify
class TypeStructLike(PDBTypesType):
    element_count: uint16_t
    property_ : TypeProperty
    field : type_index
    derived : type_index
    vshape: type_index
    # followed by "data describing length of structure in bytes and name"? 🤔
    
    @classmethod
    def from_memory(cls, mem, offset):
        header_sizeof = ctypes.sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset , offset + header_sizeof))
        #print(self)

        # Name reading from https://github.com/microsoft/microsoft-pdb/blob/e6b1dec61e154b568357537792e1d17a13525d5d/PDB/include/symtypeutils.h#L24        
        #print(bytes(mem[offset : offset + header_sizeof : 'copy']))
        #print(bytes(mem[offset : offset + self.size_bytes : 'copy']))
        #print(bytes(mem[offset + header_sizeof : offset + self.size_bytes: 'copy']))
        name_offset, x = ReadNumeric(mem, offset + header_sizeof)
        #print(f"x={x}")
        name_data = buffy(mem, name_offset , offset + self.size_bytes)
        #print(SzBytesToString(bytes(name_data)))
        return


        
        #fields_byte_count =  
        

@structify
class PDBTypeStreamOffsetSizePair(ctypes.Structure):
    offset     : int32_t
    byte_count : int32_t


@structify
class PDBTypeStreamHash(ctypes.Structure):
    hash_stream_number : uint16_t
    padding            : uint16_t
    hash_key           : int32_t
    buckets            : uint32_t
    hash_value_offsets : PDBTypeStreamOffsetSizePair
    type_info_offsets  : PDBTypeStreamOffsetSizePair
    hash_adj           : PDBTypeStreamOffsetSizePair

    def __repr__(self):
        return str({name:getattr(self, name) for name,_ in self._fields_})


@structify
class PDBTypeStreamHeader(ctypes.Structure):
    version            : uint32_t
    header_size_bytes  : int32_t
    ti_min             : uint32_t # ti is type index?
    ti_max             : uint32_t
    records_byte_count : uint32_t
    hash_stuff         : PDBTypeStreamHash

    def __repr__(self):
        return str({name:getattr(self, name) for name,_ in self._fields_})


class PdbTypeStream:
    def __init__(self, file: MultiStreamFileStream):
        self.file = file
        stuff = PDBTypeStreamHeader.from_buffer_copy(self.file[:ctypes.sizeof(PDBTypeStreamHeader)])
        #self.file = file[::'copy']
        #print(len(self.file))
        #for name, _ in stuff._fields_:
        #    setattr(self, name, getattr(stuff, name))

        self.header = stuff
        self.num_types = stuff.ti_max - stuff.ti_min

        pos = ctypes.sizeof(stuff)
        type_size = ctypes.sizeof(PDBTypesType)
        extra_bytes_to_advance = PDBTypesType.size_bytes.size
        #for info in self.iter_ti_headers():
        #    print(info)
        
        #print(self.get_ti_info(self.header.ti_min+6))

        for stream_offset, info in self.iter_ti_headers():
            #print(info)
            typ = records_by_id.get(info.record_type, None)
            if typ is not None:
                #print(stream_offset, info)
                a = typ.from_memory(self.file, stream_offset)
                #print(a)
                #asd()
                ...

        
    
    def get_ti_info(self, TI : int):
        # TODO: Use lookup or something instead of iterating until @target.
        assert TI >= self.header.ti_min
        assert TI < self.header.ti_max
        it = iter(self.iter_ti_headers())
        info = None
        for _ in range(TI - self.header.ti_min):
            info = next(it)
        return info

    def iter_ti_headers(self):
        pos = ctypes.sizeof(PDBTypeStreamHeader)
        type_size = ctypes.sizeof(PDBTypesType)
        extra_bytes_to_advance = PDBTypesType.size_bytes.size
        for idx in range(self.num_types):
            info = PDBTypesType.from_buffer_copy(buffy(self.file, pos,  pos + type_size))
            yield pos, info
            pos += extra_bytes_to_advance + info.size_bytes

    def __repr__(self):
        return str(self.__dict__)

    