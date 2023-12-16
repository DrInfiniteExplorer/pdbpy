from enum import IntEnum
from typing import Dict, List, Optional, Tuple, Union

from dtypes.structify import structify, Structy
from dtypes.typedefs import uint8_t, uint16_t, uint32_t, uint64_t
from dtypes.typedefs import int16_t, int32_t, int64_t
from dtypes.typedefs import float32_t, float64_t
from ctypes import sizeof as c_sizeof

from ..leaf_enum import LeafID

from pdbpy.utils.ctypes import Flaggy


# same functionality different name
# https://github.com/Microsoft/microsoft-pdb/blob/082c5290e5aff028ae84e43affa8be717aa7af73/pdbdump/pdbdump.cpp#L2417-L2456

# matching functionality and name but waddafack 
# https://github.com/microsoft/microsoft-pdb/blob/e6b1dec61e154b568357537792e1d17a13525d5d/PDB/include/symtypeutils.h#L7-L51 ->
#  https://github.com/fungosforks/Windows-NT-4.0-Source/blob/7a9a4aa4c3f950d0cd5512af11224084205e8fc0/private/sdktools/vctools/pdb/mre/mretype.cpp#L37-L94

LeafNumericToCType = {
    #LeafID.CHAR      : ctypes.c_char,
    LeafID.CHAR      : uint8_t,
    LeafID.SHORT     : int16_t,
    LeafID.USHORT    : uint16_t,
    LeafID.LONG      : int32_t,
    LeafID.ULONG     : uint32_t,
    LeafID.QUADWORD  : int64_t,
    LeafID.UQUADWORD : uint64_t,
    LeafID.REAL32    : float32_t,
    LeafID.REAL64    : float64_t,
    LeafID.REAL80    : uint8_t * 10,
    LeafID.REAL128   : uint8_t * 16,
}
def read_numeric(mem : memoryview, offset : int):
    """
    Reads a number from the memory offset, returns tuple of (post_read_offset, value).

    Variable size number (or string? 🤔) encoding.
    Reads a u16. If the read value is less than NUMERIC, return it directly.
    Else reads [u]int[16|32], float, double, reals, or a variable string.
    Strings and floats>65bits are returned as bytes-objects
    """

    number_or_leaf_id : int = uint16_t.from_buffer_copy(mem[offset : offset + 2]).value
    data_offset = offset + 2

    match number_or_leaf_id:
        case int(id) if id < LeafID.NUMERIC:
            return data_offset, number_or_leaf_id
        case LeafID.VARSTRING:
            print(mem[data_offset : data_offset+10])
            raise RuntimeError("Implement this as needed")
            length = uint16_t.from_buffer_copy(mem[data_offset : data_offset + 2])
            return data_offset + 2 + length, mem[data_offset + 2 : data_offset + 2 + length]
        case _:
            typ = LeafNumericToCType.get(LeafID(number_or_leaf_id), None)
            if typ is None:
                raise ValueError(f"Type based in ID {number_or_leaf_id} (leafif: {LeafID(number_or_leaf_id)}) did not match anything in the conversion table")

            size = c_sizeof(typ)
            value = typ.from_buffer_copy(mem[data_offset : data_offset + size]).value
            return data_offset + size, value
    
    raise ValueError(f"How did we get here? {offset}, {number_or_leaf_id}, {data_offset}")

def read_stringz(mem: memoryview) -> Tuple[str, int]:
    """
    Returns a tuple of [string, bytes including zero terminator]
    """
    stuff : List[int] = []
    offset = 0
    while True:
        byte = mem[offset]
        offset += 1
        if byte == 0:
            joined = bytes(stuff)
            try:
                return joined.decode('utf8'), offset
            except UnicodeDecodeError as e:
                return joined, offset
        stuff.append(byte)



def read_string(mem : memoryview, offset : int, leafy : Union[LeafID, int]) -> Tuple[int, str]:
    """
    Reads a string and returns byte (though is always UTF8????)

    Returns (post_read_offset, string)

    Depending on the input leaf type thing, is either a zero-terminated string,
     or a uint8_t followed by number of bytes specified in the uint8_t.

    """
    if leafy > LeafID.ST_MAX:
        #print("sZ string")
        # read until zero-terminator

        # TODO seriously consider rewriting to use file-like interface with seeking and page-caching
        #  instead of "fully random access through not-quite-memory-like interface"
        string, bytecount = read_stringz(mem[offset:])
        return offset + bytecount, string
    else:
        # read u8, then that number of bytes
        #print("Pascal string")
        count = mem[offset]
        post_read_offset = offset + 1
        return post_read_offset+count, bytes(mem[post_read_offset: post_read_offset+count]).decode('utf8')

def sz_bytes_to_string(data : bytes):
    return data[:data.index(0)].decode('utf8')

def extract_padding(mem : memoryview, offset : int, required : bool):
    next_byte = mem[offset]
    matches_format = next_byte > 0xf0
    if not matches_format:
        assert not required, f"Pad byte not in expected 0xF? -format: 0x{next_byte:02X}\n@-5,+15:\n{bytes(mem[offset-5: offset+15])}"
        return 0
    padding = next_byte & 0xf
    return padding

class PackedStructy(Structy):
    _pack_ = 1

records_by_id : Dict[LeafID, type[PackedStructy]]= {}

def record(*type_ids : LeafID):
    def the_types_tho(typ : type[PackedStructy]):
        for id_ in type_ids:
            records_by_id[id_] = typ
        typ.__record_types = [*type_ids] # type: ignore
        return typ
    return the_types_tho

def get_record_type_by_leaf_type(record_type : LeafID) -> Optional[type[PackedStructy]]:
    return records_by_id.get(record_type, None)

class AccessEnum(IntEnum):
    Private   = 1,
    Protected = 2,
    Public    = 3

class MethodPropertiesEnum(IntEnum):
    vanilla     = 0
    virtual     = 1
    static      = 2
    friend      = 3
    intro       = 4
    purevirtual = 5
    pureintro   = 6

@structify
class FieldAttributes(Flaggy):
    _access      : (uint8_t, 2)
    _mprop       : (uint8_t, 3) # MethodPropertiesEnum
    pseudo      : (uint8_t, 1)
    noinherit   : (uint8_t, 1)
    noconstruct : (uint8_t, 1) #cant be constructed
    compgenx    : (uint8_t, 1)
    sealed      : (uint8_t, 1) # final
    unused      : (uint8_t, 6)

    @property
    def mprop(self):
        return MethodPropertiesEnum(self._mprop)

    @property
    def access(self):
        return AccessEnum(self._access)

assert c_sizeof(FieldAttributes) == 2

@structify
# https://github.com/microsoft/microsoft-pdb/blob/1d60e041600117a5004de84baa960d2c953a6aa6/include/cvinfo.h#L1120
class TypeProperties(Flaggy):
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

assert c_sizeof(TypeProperties) == 2

@structify
class FunctionAttributes(Flaggy):
    cxxreturnudt : (uint8_t, 1)
    ctor         : (uint8_t, 1)
    ctorvbase    : (uint8_t, 1)
    unused       : (uint8_t, 5)

assert c_sizeof(FunctionAttributes) == 1

class PointerTypeEnum(IntEnum):
    NEAR         = 0x00
    FAR          = 0x01
    HUGE         = 0x02
    BASE_SEG     = 0x03
    BASE_VAL     = 0x04
    BASE_SEGVAL  = 0x05
    BASE_ADDR    = 0x06
    BASE_SEGADDR = 0x07
    BASE_TYPE    = 0x08
    BASE_SELF    = 0x09
    NEAR32       = 0x0a
    FAR32        = 0x0b
    BITS_64      = 0x0c
    UNUSEDPTR    = 0x0d

class PointerModeEnum(IntEnum):
    Normal              = 0x00
    OldGenericReference = 0x01
    LValueReference     = 0x01
    Member              = 0x02
    MemberFunction      = 0x03
    RValueReference     = 0x04
    RESERVED            = 0x05

@structify
class PointerAttributes(Flaggy):
    _kind      : (uint32_t, 5) #PointerTypeEnum
    _mode      : (uint32_t, 3) #PointerModeEnum


    flat32    : (uint32_t, 1)
    volatile  : (uint32_t, 1)
    const     : (uint32_t, 1)
    unaligned : (uint32_t, 1)
    restrict  : (uint32_t, 1)
    
    size      : (uint32_t, 6)

    ismocom   : (uint32_t, 1)
    islref    : (uint32_t, 1)
    isrred    : (uint32_t, 1)

    unused    : (uint32_t, 10)

    @property
    def kind(self):
        return PointerTypeEnum(self._kind)
    
    @property
    def mode(self):
        return PointerModeEnum(self._mode)

assert c_sizeof(PointerAttributes) == 4, c_sizeof(PointerAttributes)
