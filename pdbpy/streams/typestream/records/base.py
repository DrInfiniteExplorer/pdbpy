from ctypes import sizeof as c_sizeof
from enum import IntEnum
from typing import Dict, Optional

from dtypes.structify import Structy, structify
from dtypes.typedefs import uint8_t, uint16_t, uint32_t

from pdbpy.codeview import LeafID
from pdbpy.utils.ctypes import Flaggy


def sz_bytes_to_string(data: bytes):
    return data[: data.index(0)].decode("utf8")


def extract_padding(mem: memoryview, offset: int, required: bool):
    next_byte = mem[offset]
    matches_format = next_byte > 0xF0
    if not matches_format:
        assert (
            not required
        ), f"Pad byte not in expected 0xF? -format: 0x{next_byte:02X}\n@-5,+15:\n{bytes(mem[offset-5: offset+15])}"
        return 0
    padding = next_byte & 0xF
    return padding


class PackedStructy(Structy):
    _pack_ = 1


records_by_id: Dict[LeafID, type[PackedStructy]] = {}


def record(*type_ids: LeafID):
    def the_types_tho(typ: type[PackedStructy]):
        for id_ in type_ids:
            records_by_id[id_] = typ
        typ.__record_types = [*type_ids]  # type: ignore
        return typ

    return the_types_tho


def get_record_type_by_leaf_type(record_type: LeafID) -> Optional[type[PackedStructy]]:
    return records_by_id.get(record_type, None)


class AccessEnum(IntEnum):
    Private = (1,)
    Protected = (2,)
    Public = 3


class MethodPropertiesEnum(IntEnum):
    vanilla = 0
    virtual = 1
    static = 2
    friend = 3
    intro = 4
    purevirtual = 5
    pureintro = 6


@structify
class FieldAttributes(Flaggy):
    _access: (uint8_t, 2)
    _mprop: (uint8_t, 3)  # MethodPropertiesEnum
    pseudo: (uint8_t, 1)
    noinherit: (uint8_t, 1)
    noconstruct: (uint8_t, 1)  # cant be constructed
    compgenx: (uint8_t, 1)
    sealed: (uint8_t, 1)  # final
    unused: (uint8_t, 6)

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
    packed: (uint16_t, 1)
    ctor: (uint16_t, 1)
    overloaded_operators: (uint16_t, 1)
    is_nested: (uint16_t, 1)
    contains_nested: (uint16_t, 1)
    overloaded_assignment: (uint16_t, 1)
    overloaded_casts: (uint16_t, 1)
    is_forward_definition: (uint16_t, 1)
    scoped_definition: (uint16_t, 1)
    has_unique_name: (uint16_t, 1)  # a decorated name follows the regular name
    is_final: (uint16_t, 1)
    hfa: (uint16_t, 2)  # what is CV_HFA_e
    intrinsic: (uint16_t, 1)  # intrinsic type, like __m128d
    mocom: (uint16_t, 2)  # what is CV_MOCOM_UDT_e


assert c_sizeof(TypeProperties) == 2


@structify
class FunctionAttributes(Flaggy):
    cxxreturnudt: (uint8_t, 1)
    ctor: (uint8_t, 1)
    ctorvbase: (uint8_t, 1)
    unused: (uint8_t, 5)


assert c_sizeof(FunctionAttributes) == 1


class PointerTypeEnum(IntEnum):
    NEAR = 0x00
    FAR = 0x01
    HUGE = 0x02
    BASE_SEG = 0x03
    BASE_VAL = 0x04
    BASE_SEGVAL = 0x05
    BASE_ADDR = 0x06
    BASE_SEGADDR = 0x07
    BASE_TYPE = 0x08
    BASE_SELF = 0x09
    NEAR32 = 0x0A
    FAR32 = 0x0B
    BITS_64 = 0x0C
    UNUSEDPTR = 0x0D


class PointerModeEnum(IntEnum):
    Normal = 0x00
    OldGenericReference = 0x01
    LValueReference = 0x01
    Member = 0x02
    MemberFunction = 0x03
    RValueReference = 0x04
    RESERVED = 0x05


@structify
class PointerAttributes(Flaggy):
    _kind: (uint32_t, 5)  # PointerTypeEnum
    _mode: (uint32_t, 3)  # PointerModeEnum

    flat32: (uint32_t, 1)
    volatile: (uint32_t, 1)
    const: (uint32_t, 1)
    unaligned: (uint32_t, 1)
    restrict: (uint32_t, 1)

    size: (uint32_t, 6)

    ismocom: (uint32_t, 1)
    islref: (uint32_t, 1)
    isrred: (uint32_t, 1)

    unused: (uint32_t, 10)

    @property
    def kind(self):
        return PointerTypeEnum(self._kind)

    @property
    def mode(self):
        return PointerModeEnum(self._mode)


assert c_sizeof(PointerAttributes) == 4, c_sizeof(PointerAttributes)
