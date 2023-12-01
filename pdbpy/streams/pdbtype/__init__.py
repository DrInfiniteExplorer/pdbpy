from enum import IntEnum
from ctypes import sizeof as c_sizeof
import struct

from typing import Dict, Tuple, List, Iterable


from dtypes.structify import (Structy, structify)
from dtypes.typedefs import (
    int8_t,  int16_t,  int32_t,  int64_t,
    uint8_t, uint16_t, uint32_t, uint64_t)

from .leaf_enum import LeafID

from pdbpy.utils.ctypes import Flaggy

from pdbpy.streams.typing import type_index





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

from .pdbtypestream import PdbTypeStream

__all__ = [
    PdbTypeStream
]
