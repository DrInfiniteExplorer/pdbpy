



# same functionality different name
# https://github.com/Microsoft/microsoft-pdb/blob/082c5290e5aff028ae84e43affa8be717aa7af73/pdbdump/pdbdump.cpp#L2417-L2456

# matching functionality and name but waddafack 
# https://github.com/microsoft/microsoft-pdb/blob/e6b1dec61e154b568357537792e1d17a13525d5d/PDB/include/symtypeutils.h#L7-L51 ->
#  https://github.com/fungosforks/Windows-NT-4.0-Source/blob/7a9a4aa4c3f950d0cd5512af11224084205e8fc0/private/sdktools/vctools/pdb/mre/mretype.cpp#L37-L94


from typing import List, Tuple, Union
from dtypes.typedefs import uint8_t, uint16_t, uint32_t, uint64_t
from dtypes.typedefs import int16_t, int32_t, int64_t
from dtypes.typedefs import float32_t, float64_t
from ctypes import sizeof as c_sizeof


from pdbpy.codeview import LeafID

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

def read_pascalstring(mem: memoryview) -> Tuple[str, int]:
    count : int = mem[0]
    return bytes(mem[1: 1+count]).decode('utf8'), 1+count


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
        string, bytecount = read_pascalstring(mem[offset:])
        return offset + bytecount, string
