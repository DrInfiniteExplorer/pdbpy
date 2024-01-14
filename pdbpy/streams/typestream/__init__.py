from enum import IntEnum

from .pdbtypestream import PdbTypeStream


class PointerMemberEnum(IntEnum):
    Undef = 0x00  # not specified (pre VC8)
    Data_Single = 0x01  # member data, single inheritance
    Data_Multiple = 0x02  # member data, multiple inheritance
    Data_Virtual = 0x03  # member data, virtual inheritance
    Data_General = 0x04  # member data, most general
    Function_Single = 0x05  # member function, single inheritance
    Function_Multiple = 0x06  # member function, multiple inheritance
    Function_Virtual = 0x07  # member function, virtual inheritance
    Function_General = 0x08  # member function, most general


__all__ = ["PdbTypeStream"]
