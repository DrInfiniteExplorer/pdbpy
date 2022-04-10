import ctypes

from enum import IntEnum

from .leaf_enum import LeafID

from pdbpy.msf import MultiStreamFileStream
from pdbpy.utils.ctypes import (Structy, Flaggy, structify,
    int8_t,  int16_t,  int32_t,  int64_t,
    uint8_t, uint16_t, uint32_t, uint64_t)

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

assert ctypes.sizeof(TypeProperties) == 2








LeafNumericToCType = {
    LeafID.CHAR      : ctypes.c_char,
    LeafID.SHORT     : int16_t,
    LeafID.USHORT    : uint16_t,
    LeafID.LONG      : int32_t,
    LeafID.ULONG     : uint32_t,
    LeafID.QUADWORD  : int64_t,
    LeafID.UQUADWORD : uint64_t,
    LeafID.REAL32    : ctypes.c_float,
    LeafID.REAL64    : ctypes.c_double,
    LeafID.REAL80    : ctypes.c_byte * 10,
    LeafID.REAL128   : ctypes.c_byte * 16,
}

# same functionality different name
# https://github.com/Microsoft/microsoft-pdb/blob/082c5290e5aff028ae84e43affa8be717aa7af73/pdbdump/pdbdump.cpp#L2417-L2456

# matching functionality and name but waddafack 
# https://github.com/microsoft/microsoft-pdb/blob/e6b1dec61e154b568357537792e1d17a13525d5d/PDB/include/symtypeutils.h#L7-L51 ->
#  https://github.com/fungosforks/Windows-NT-4.0-Source/blob/7a9a4aa4c3f950d0cd5512af11224084205e8fc0/private/sdktools/vctools/pdb/mre/mretype.cpp#L37-L94

def ReadNumeric(mem, offset):
    """
    Reads a number from the memory offset, returns tuple of (post_read_offset, value).

    Variable size number (or string? 🤔) encoding.
    Reads a u16. If the read value is less than NUMERIC, return it directly.
    Else reads [u]int[16|32], float, double, reals, or a variable string.
    Strings and floats>65bits are returned as bytes-objects
    """

    number_or_leaf_id = uint16_t.from_buffer_copy(mem[offset : offset + 2]).value
    data_offset = offset + 2

    match number_or_leaf_id:
        case int(id) if id < LeafID.NUMERIC:
            return data_offset, number_or_leaf_id
        case LeafID.VARSTRING:
            print(mem[data_offset : data_offset+10])
            asd()
            length = uint16_t.from_buffer_copy(mem[data_offset : data_offset + 2])
            return data_offset + 2 + length, mem[data_offset + 2 : data_offset + 2 + length]
        case _:
            typ = LeafNumericToCType.get(number_or_leaf_id)
            #print(typ)
            #asd()

            size = ctypes.sizeof(typ)
            value = typ.from_buffer_copy(mem[data_offset : data_offset + size])
            return data_offset + size, value
    
    raise ValueError(f"How did we get here? {offset}, {number_or_leaf_id}, {data_offset}")

def ReadString(mem, offset, leafy):
    """
    Reads a string and returns byte (though is always UTF8????)

    Returns (post_read_offset, string)

    Depending on the input leaf type thing, is either a zero-terminated string,
     or a uint8_t followed by number of bytes specified in the uint8_t.

    """
    if leafy > LeafID.ST_MAX:
        print("sZ string")
        # read until zero-terminator

        # TODO seriously consider rewriting to use file-like interface with seeking and page-caching
        #  instead of "fully random access through not-quite-memory-like interface"
        stuff = []
        zero = b'\x00'
        while True:
            byte = buffy(mem, offset, offset+1)
            offset += 1
            if byte == zero:
                joined = b''.join(stuff)
                try:
                    return offset, joined.decode('utf8')
                except UnicodeDecodeError as e:
                    return offset, joined
            stuff.append(byte)
    else:
        # read u8, then that number of bytes
        print("Pascal string")
        count = uint8_t.from_buffer_copy(buffy(mem, offset, offset+1)).value
        post_read_offset = offset + 1
        return post_read_offset+count, bytes(buffy(mem, post_read_offset, post_read_offset+count)).decode('utf8')

def SzBytesToString(data):
    return data[:data.index(0)].decode('utf8')



class PackedStructy(Structy):
    _pack_ = 1

class MethodPropertiesEnum(IntEnum):
    vanilla     = 0
    virtual     = 1
    static      = 2
    friend      = 3
    intro       = 4
    purevirtual = 5
    pureintro   = 6

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

class PointerMemberEnum(IntEnum):
    Undef             = 0x00 # not specified (pre VC8)
    Data_Single       = 0x01 # member data, single inheritance
    Data_Multiple     = 0x02 # member data, multiple inheritance
    Data_Virtual      = 0x03 # member data, virtual inheritance
    Data_General      = 0x04 # member data, most general
    Function_Single   = 0x05 # member function, single inheritance
    Function_Multiple = 0x06 # member function, multiple inheritance
    Function_Virtual  = 0x07 # member function, virtual inheritance
    Function_General  = 0x08 # member function, most general

@structify
class FieldAttributes(Flaggy):
    access      : (uint8_t, 2)
    mprop       : (uint8_t, 3) # MethodPropertiesEnum
    pseudo      : (uint8_t, 1)
    noinherit   : (uint8_t, 1)
    noconstruct : (uint8_t, 1) #cant be constructed
    compgenx    : (uint8_t, 1)
    sealed      : (uint8_t, 1) # final
    unused      : (uint8_t, 6)

assert ctypes.sizeof(FieldAttributes) == 2

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

assert ctypes.sizeof(PointerAttributes) == 4, ctypes.sizeof(PointerAttributes)


@structify
class FunctionAttributes(Flaggy):
    cxxreturnudt : (uint8_t, 1)
    ctor         : (uint8_t, 1)
    ctorvbase    : (uint8_t, 1)
    unused       : (uint8_t, 5)

assert ctypes.sizeof(FunctionAttributes) == 1



@record(LeafID.MEMBER, LeafID.MEMBER_ST, LeafID.STMEMBER, LeafID.STMEMBER_ST)
@structify
class Member(PackedStructy):
    record_type      : uint16_t
    field_attributes : FieldAttributes
    field_type       : type_index
    #offset
    #name

    #static

    @classmethod
    def from_memory(cls, mem, offset, record_size : 'Optional[int]', debug : bool):
        my_size = ctypes.sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset

        post_read_offset = offset + my_size
        self.static = self.record_type in (LeafID.STMEMBER, LeafID.STMEMBER_ST)

        if not self.static:
            post_read_offset, self.offset = ReadNumeric(mem, post_read_offset)
        post_read_offset, self.name = ReadString(mem, post_read_offset, self.record_type)

        return post_read_offset, self




@record(LeafID.MFUNCTION)
@structify
class MemberFunction(PackedStructy):
    record_type     : uint16_t
    return_type     : type_index
    class_type      : type_index
    this_ptr_type   : type_index
    call_convention : uint8_t
    attributes      : FunctionAttributes
    parameter_count : uint16_t
    arg_list        : type_index
    this_adjustment : uint32_t


    @classmethod
    def from_memory(cls, mem, offset, record_size : 'Optional[int]', debug : bool):
        my_size = ctypes.sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset

        post_read_offset = offset + my_size

        return post_read_offset, self

@record(LeafID.ONEMETHOD)
@structify
class OneMethod(PackedStructy):
    record_type     : uint16_t
    attributes      : FieldAttributes
    method_type     : type_index
    # vtable_offset
    # name


    @classmethod
    def from_memory(cls, mem, offset, record_size : 'Optional[int]', debug : bool):
        my_size = ctypes.sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset
    
        post_read_offset = offset + my_size
        if self.attributes.mprop in (MethodPropertiesEnum.intro, MethodPropertiesEnum.pureintro):
            self.vtable_offset = uint32_t.from_buffer_copy(buffy(mem, post_read_offset, post_read_offset+4))
            post_read_offset += 4
        post_read_offset, self.name = ReadString(mem, post_read_offset, self.record_type)

        return post_read_offset, self



@record(LeafID.BCLASS, LeafID.INTERFACE)
@structify
class BaseClass(PackedStructy):
    record_type     : uint16_t
    attributes      : FieldAttributes
    index           : type_index
    # offset

    @classmethod
    def from_memory(cls, mem, offset, record_size : 'Optional[int]', debug : bool):
        my_size = ctypes.sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset
        post_read_offset = offset + my_size

        post_read_offset, self.offset = ReadNumeric(mem, post_read_offset)

        return post_read_offset, self

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
    def from_memory(cls, mem, offset, record_size : 'Optional[int]', debug : bool):
        my_size = ctypes.sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset
        post_read_offset = offset + my_size

        return post_read_offset, self



@record(LeafID.VFUNCTAB)
@structify
class VFuncTab(PackedStructy):
    record_type     : uint16_t
    padding         : uint16_t
    vtable_ptr      : type_index

    @classmethod
    def from_memory(cls, mem, offset, record_size : 'Optional[int]', debug : bool):
        my_size = ctypes.sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset
        post_read_offset = offset + my_size

        return post_read_offset, self


@record(LeafID.POINTER)
@structify
class Pointer(PackedStructy):

    record_type    : uint16_t
    reference_type : type_index
    attributes     : PointerAttributes

    @classmethod
    def from_memory(cls, mem, offset, record_size : 'Optional[int]', debug : bool):
        my_size = ctypes.sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
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
    def from_memory(cls, mem, offset, record_size : 'Optional[int]', debug : bool):
        my_size = ctypes.sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset
        post_read_offset = offset + my_size

        return post_read_offset, self

@record(LeafID.MODIFIER)
@structify
class Modifier(PackedStructy):
    record_type     : uint16_t
    reference       : type_index
    flags           : uint16_t

    @classmethod
    def from_memory(cls, mem, offset, record_size : 'Optional[int]', debug : bool):
        my_size = ctypes.sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset
        post_read_offset = offset + my_size

        return post_read_offset, self

@record(LeafID.ENUM, LeafID.ENUM_ST)
@structify
class Enum(PackedStructy):
    _pack_ = 2
    record_type     : uint16_t
    count           : uint16_t
    properties      : TypeProperties
    underlying_type : type_index
    fields          : type_index
    # name
    # unique_name

    @classmethod
    def from_memory(cls, mem, offset, record_size : 'Optional[int]', debug : bool):
        my_size = ctypes.sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset
        post_read_offset = offset + my_size

        post_read_offset, self.name = ReadString(mem, post_read_offset, self.record_type)
        if self.properties.has_unique_name:
            post_read_offset, self.unique_name = ReadString(mem, post_read_offset, self.record_type)
        
        #print(record_size)
        #print("!!", bytes(buffy(mem, offset, offset+record_size)))
        #print(post_read_offset, bytes(buffy(mem, post_read_offset, post_read_offset+1)))

        return post_read_offset, self

assert Enum.underlying_type.offset == 6


@record(LeafID.ENUMERATE, LeafID.ENUMERATE_ST)
@structify
class Enumerate(PackedStructy):
    record_type     : uint16_t
    attributes      : FieldAttributes
    #value           : uint16_t # should be ReadNumeric?
    # name

    @classmethod
    def from_memory(cls, mem, offset, record_size : 'Optional[int]', debug : bool):
        my_size = ctypes.sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset
        post_read_offset = offset + my_size

        post_read_offset, self.value = ReadNumeric(mem, post_read_offset)
        post_read_offset, self.name  = ReadString(mem, post_read_offset, self.record_type)

        return post_read_offset, self

@record(LeafID.FIELDLIST)
@structify
class FieldList(PackedStructy):
    record_type     : uint16_t

    @classmethod
    def from_memory(cls, mem, offset, record_size : int, debug : bool):

        assert isinstance(record_size, int), "Parsing a field list requires knowledge of how large the total record is!"

        my_size = ctypes.sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset
        post_read_offset = offset + my_size

        post_record = offset + record_size

        self.members = []

        while post_read_offset < post_record:

            post_read_offset, member = ParseType(mem, post_read_offset, padding_cricital=True, debug=debug)
            self.members = [member]
            #print(f"Member is {member}")
            #print(f"{post_read_offset} - {post_record}")

            # paddy padd!
            if post_read_offset < post_record:
                paddy = extract_padding(mem, post_read_offset, required=False)
                if debug:
                    print(f"Padding {post_read_offset} with {paddy}")
                post_read_offset += paddy


        return post_read_offset, self


@record(LeafID.METHOD)
@structify
class Method(PackedStructy):
    record_type     : uint16_t
    count           : uint16_t
    method_list     : type_index
    # name


    @classmethod
    def from_memory(cls, mem, offset, record_size : int, debug : bool):

        my_size = ctypes.sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset
        post_read_offset = offset + my_size

        post_read_offset, self.name  = ReadString(mem, post_read_offset, self.record_type)

        return post_read_offset, self


@record(LeafID.NESTTYPE)
@structify
class NestType(PackedStructy):
    record_type     : uint16_t
    padding         : uint16_t
    nested_type     : type_index
    # name

    @classmethod
    def from_memory(cls, mem, offset, record_size : int, debug : bool):

        my_size = ctypes.sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset
        post_read_offset = offset + my_size

        post_read_offset, self.name  = ReadString(mem, post_read_offset, self.record_type)

        return post_read_offset, self

@record(LeafID.yolo)
@structify
class ASD(PackedStructy):
    record_type     : uint16_t

    @classmethod
    def from_memory(cls, mem, offset, record_size : int, debug : bool):

        my_size = ctypes.sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset, offset + my_size))
        self.addr = offset
        post_read_offset = offset + my_size

        return post_read_offset, self




@record(LeafID.CLASS, LeafID.STRUCTURE, LeafID.INTERFACE, LeafID.CLASS_ST, LeafID.STRUCTURE_ST, LeafID.INTERFACE)
@structify
class TypeStructLike(PackedStructy):
    record_type   : uint16_t
    element_count : uint16_t
    properties    : TypeProperties
    field         : type_index     # the record which contains the field list (ie. members n methods)
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


        header_sizeof = ctypes.sizeof(cls)
        self = cls.from_buffer_copy(buffy(mem, offset , offset + header_sizeof))
        self.addr = offset
        #print(self)

        # Name reading from https://github.com/microsoft/microsoft-pdb/blob/e6b1dec61e154b568357537792e1d17a13525d5d/PDB/include/symtypeutils.h#L24        
        #print(bytes(mem[offset : offset + header_sizeof : 'copy']))
        #print(bytes(mem[offset : offset + self.size_bytes : 'copy']))
        #print(bytes(mem[offset + header_sizeof : offset + self.size_bytes: 'copy']))
        name_offset, self.struct_size_bytes = ReadNumeric(mem, offset + header_sizeof)
        #print(f"x={x}")
        #name_data = buffy(mem, name_offset , offset + self.size_bytes)
        #print(SzBytesToString(bytes(name_data)))
        
        post_read_offset, name_data = ReadString(mem, name_offset, self.record_type)
        self.name = name_data
        if self.properties.has_unique_name:
            post_read_offset, self.unique_name = ReadString(mem, post_read_offset, self.record_type)
            #print(self.unique_name)
        #print(self.name)


        return post_read_offset, self
    


        
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

@structify
# https://github.com/microsoft/microsoft-pdb/blob/1d60e041600117a5004de84baa960d2c953a6aa6/include/cvinfo.h#L1175
class CodeViewRecordHeader(PackedStructy):    
    """
    """
    size_bytes : uint16_t
    record_type: uint16_t # called 'leaf' by dudes but they are pretty far from leafs most of the time 🤔


def extract_padding(mem, offset, required : bool):
    next_byte = uint8_t.from_buffer_copy(buffy(mem, offset, offset+1)).value
    matches_format = next_byte > 0xf0
    if not matches_format:
        assert not required, f"Pad byte not in expected 0xF? -format: 0x{next_byte:02X}\n@-5,+15:\n{bytes(buffy(mem, offset-5, offset+15))}"
        return 0
    padding = next_byte & 0xf
    return padding



def ParseType(mem, record_content_offset, record_type = None, record_size_bytes = None, padding_cricital = False, debug=False):
    if record_type is None:
        record_type = uint16_t.from_buffer_copy(mem[record_content_offset : record_content_offset + 2]).value

    if debug:
        print(f"Record type: {record_type} | 0x{record_type:X}")
    
    
    typ = records_by_id.get(record_type, None)
    if typ is None:
        if debug:
            print(f"Can't deal with {LeafID(record_type).name} yet")
        return
    
    post_read_offset, parsed = typ.from_memory(mem, record_content_offset, record_size = record_size_bytes, debug=debug)
    if debug:
        print(parsed)

    padding = 0
    if record_size_bytes is not None:
        expected_end = record_content_offset + record_size_bytes
        assert post_read_offset <= expected_end, f"READ TOO FAR! Read to {post_read_offset}, ought to have read to {expected_end}, which is {post_read_offset-expected_end} too much!"
        if post_read_offset != expected_end:
            if debug:
                print(f"Read to {post_read_offset}, expected to land at {expected_end}")
            if padding_cricital:
                padding = extract_padding(mem, post_read_offset, required=True)
                assert post_read_offset + padding == expected_end, f"{post_read_offset} is not {record_content_offset + record_size_bytes} as was expected, we didn't read the previous record correctly???"
                if debug:
                    print(f"Padding-bytes made short work if the inconsistency")
    
    return post_read_offset + padding, parsed


def take(count, it):
    if count == 'all':
        yield from it
        return
    for _ in range(count):
        yield next(it)

def skip(count, it):
    for _ in range(count):
        next(it)
    yield from it

class PdbTypeStream:
    def __init__(self, file: MultiStreamFileStream, lookup_skip = 10, upfront_memory = False, debug=False):
        """
        lookup_skip sets the "skip" value when adding offsets to the speedreader-cache;
         Every `lookup_skip` pairs of (type_index, stream_offset) is added to a cache.
        """
        self.file = file
        header = PDBTypeStreamHeader.from_buffer_copy(self.file[:ctypes.sizeof(PDBTypeStreamHeader)])
        if upfront_memory:
            self.file = file[::'copy']

        self.header = header
        self.num_types = header.ti_max - header.ti_min

        self.lookup_skip = lookup_skip
        self.lookup = []

        self.debug = debug
        
        debug = True

        if debug:
            for stream_offset, info in take(3, self.iter_ti_headers(self.header.ti_min)):
                print(f"{stream_offset} - {info}")


        #Type index: 6c7eb of 1bfec6
        #Record type: 4105 | 0x1009
        #MemberFunction{'record_type': 4105, 'return_type': 1539, 'class_type': 444245, 'this_ptr_type': 444247, 'call_convention': 0, 'attributes': , 'parameter_count': 1, 'arg_list': 4158, 'this_adjustment': 24, 'addr': 31226170}

        i = self.header.ti_min
        i = 0x6c7eb
        for stream_offset, info in take('all', self.iter_ti_headers(i)):
            print(f"Type index: {i:x} of {self.header.ti_max:x}")
            i+=1
            ParseType(self.file, stream_offset+2, record_type=info.record_type, record_size_bytes = info.size_bytes, debug=debug)
            print()

        
    
    def get_ti_info(self, TI : type_index):
        return next(self.iter_ti_headers(start_ti = TI))
    
    def get_closest_start_pos_for_ti(self, ti) -> 'tuple(type_index, int)':
        """
        Returns the closest stored lookup position for a given type_index.

        Returns a (idx, stream_byte_offset) with the `idx` as 0-start, not a type_index
        """
        assert ti >= self.header.ti_min
        assert ti < self.header.ti_max

        lookup_len = len(self.lookup)
        if lookup_len == 0:
            return 0, ctypes.sizeof(PDBTypeStreamHeader)

        idx = ti - self.header.ti_min
        lookup_idx = idx // self.lookup_skip
        
        lookup_idx = min(lookup_idx, lookup_len-1)
        pos = self.lookup[lookup_idx]
        return lookup_idx * self.lookup_skip, pos


    def iter_ti_headers(self, start_ti : type_index = None):
        type_size = ctypes.sizeof(CodeViewRecordHeader)
        extra_bytes_to_advance = CodeViewRecordHeader.size_bytes.size
        if start_ti is None:
            start_index = 0
            yield_start_index = 0
            pos = ctypes.sizeof(PDBTypeStreamHeader)
        else:
            assert start_ti >= self.header.ti_min
            assert start_ti < self.header.ti_max
            yield_start_index = start_ti - self.header.ti_min
            start_index, pos = self.get_closest_start_pos_for_ti(start_ti)
            
        for idx in range(start_index, self.num_types):
            if idx % self.lookup_skip == 0:
                lookup_idx = idx // self.lookup_skip
                lookup = self.lookup
                if len(lookup) <= lookup_idx:
                    self.lookup.append(pos)
            info = CodeViewRecordHeader.from_buffer_copy(buffy(self.file, pos,  pos + type_size))
            if idx >= yield_start_index:
                yield pos, info
            pos += extra_bytes_to_advance + info.size_bytes

    def __repr__(self):
        return str(self.__dict__)

    