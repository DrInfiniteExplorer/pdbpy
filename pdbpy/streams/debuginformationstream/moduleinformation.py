from typing import Tuple
from dtypes.structify import Structy, structify
from dtypes.typedefs import uint16_t, uint32_t
from ctypes import sizeof as c_sizeof
from pdbpy.parsing import read_stringz

from pdbpy.types import ByteCount32, FileCount16, ModuleIndex16, NameIndex32, Offset32, SectionIndex16, StreamNumber16

# https://github.com/microsoft/microsoft-pdb/blob/082c5290e5aff028ae84e43affa8be717aa7af73/PDB/include/dbicommon.h#L19,L44
# https://github.com/willglynn/pdb/blob/master/src/dbi.rs#L399
# https://github.com/moyix/pdbparse/blob/master/pdbparse/dbi.py#L17
@structify
class SectionContribution(Structy):
    _pack_ = 1
    index            : SectionIndex16
    _padding         : uint16_t
    offset           : Offset32
    size             : ByteCount32
    characteristicts : uint32_t # https://github.com/willglynn/pdb/blob/master/src/pe.rs#L102 -> [`IMAGE_SCN_`]: https://docs.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_section_header
    module           : ModuleIndex16
    _padding2        : uint16_t
    data_crc         : uint32_t
    reloc_crc        : uint32_t

assert c_sizeof(SectionContribution) == 2+2+4+4+4+2+2+4+4


# https://github.com/Microsoft/microsoft-pdb/blob/082c5290e5aff028ae84e43affa8be717aa7af73/PDB/dbi/dbi.h#L1197
@structify
class ModuleInformation(Structy):
    _pack_ = 1

    # https://github.com/Microsoft/microsoft-pdb/blob/082c5290e5aff028ae84e43affa8be717aa7af73/PDB/dbi/dbi.h#L1199
    #     Mod* = https://github.com/microsoft/microsoft-pdb/blob/082c5290e5aff028ae84e43affa8be717aa7af73/langapi/include/pdb.h#L966
    # "opened" https://github.com/moyix/pdbparse/blob/master/pdbparse/dbi.py#L87C24-L87C24
    # "opened" https://github.com/willglynn/pdb/blob/master/src/dbi.rs#L426
    _internal_leakage     : uint32_t # holds pointer when loaded in ms-pdb, wasted disk space
    section_contribution  : SectionContribution
    written               : (uint16_t, 1)
    EC_enabled            : (uint16_t, 1)
    _unused               : (uint16_t, 6)
    iTSM                  : (uint16_t, 8)
    module_debug_info     : StreamNumber16
    local_symbols_size    : ByteCount32
    line_numbers_size     : ByteCount32
    c13_line_numbers_size : ByteCount32
    file_count            : FileCount16
    _padding              : uint16_t
    _internal_leakage2    : uint32_t # holds pointer when loaded in ms-pdb, wasted disk space
    src_filename          : NameIndex32
    pdb_filename          : NameIndex32
    # https://github.com/willglynn/pdb/blob/master/src/dbi.rs#L523
    # https://github.com/moyix/pdbparse/blob/master/pdbparse/dbi.py#L99
    # microsoft-pdb reads the whole buffer, then interprets the strings from there https://github.com/microsoft/microsoft-pdb/blob/082c5290e5aff028ae84e43affa8be717aa7af73/PDB/dbi/dbi.cpp#L508
    #module : str # cstring
    #object : str # cstring

    def __init__(self):
        super().__init__(self)
        self.module : str = "" # Usually object file (which might have gone into lib)
        self.object : str = "" # Usually lib file (or same as object file)


    @classmethod
    def from_memory(cls, mem : memoryview, debug : bool) -> Tuple['ModuleInformation', int]:
        my_size = c_sizeof(cls)
        self : ModuleInformation = cls.from_buffer_copy(mem)
        self.module, bytecount_module = read_stringz(mem[my_size:])
        self.object, bytecount_object = read_stringz(mem[my_size + bytecount_module:])

        return self, ((my_size + bytecount_module + bytecount_object + 3) // 4) * 4



_ = 4+c_sizeof(SectionContribution)+2+2+4+4+4+2+2+4+4+4
assert c_sizeof(ModuleInformation) == _, f"{c_sizeof(ModuleInformation)} wasn't {_} as expected"

