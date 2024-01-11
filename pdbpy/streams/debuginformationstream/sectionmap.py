from ctypes import sizeof as c_sizeof
from dtypes.structify import Structy, structify
from dtypes.typedefs import uint16_t, uint32_t

from pdbpy.utils.ctypes import Flaggy

# Section map entries seem pretty useless?
# https://github.com/llvm/llvm-project/blob/7dd20637c801b429f2dd1040941d00141459d64e/llvm/lib/DebugInfo/PDB/Native/DbiStreamBuilder.cpp#L348
# Corresponds to `*** SEGMENT MAP` output from dvdump
# Also partly corresponds to S_SECTION and section headers, though they have more information like RVA and name.

@structify
class SectionMapEntryFlags(Flaggy):
    Read              : (uint16_t, 1)
    Write             : (uint16_t, 1)
    Execute           : (uint16_t, 1)
    AddresIs32Bit     : (uint16_t, 1)
    IsSelector        : (uint16_t, 1)
    IsAbsoluteAddress : (uint16_t, 1)
    IsGroup           : (uint16_t, 1)
assert c_sizeof(SectionMapEntryFlags) == 2

@structify
class SectionMapHeader(Structy):
    _pack_ = 1
    segment_count         : uint16_t
    logical_segment_count : uint16_t
assert c_sizeof(SectionMapHeader) == 4
    

@structify
class SectionMapEntry(Structy):
    _pack_ = 1
    flags                  : SectionMapEntryFlags
    logical_overlay_number : uint16_t
    group                  : uint16_t
    frame                  : uint16_t
    section_name           : uint16_t # byte index in string table or 0xFFFF
    class_name             : uint16_t # byte index in string table or 0xFFFF
    offset                 : uint32_t # offset of logical segment in physical segment, or offset in group (if group in flags)
    section_length         : uint32_t # byte count of segment/group
assert c_sizeof(SectionMapEntry) == 2+2+2+2+2+2+4+4


    
