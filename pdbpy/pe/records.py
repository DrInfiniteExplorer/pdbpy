import ctypes
from dtypes.structify import Structy, structify
from dtypes.typedefs import uint16_t, uint32_t


@structify
class AddressOrSize(ctypes.Union):
    _pack_ = 1
    physical_address: uint32_t
    virtual_size    : uint32_t


@structify
class ImageSectionHeader(Structy):
    _pack_ = 1
    _anonymous_ = ('addr_or_size',)

    name                    : ctypes.c_char * 8
    addr_or_size            : AddressOrSize
    virtual_address         : uint32_t
    size_of_raw_data        : uint32_t
    pointer_to_raw_data     : uint32_t
    pointer_to_relocations  : uint32_t
    pointer_to_line_numbers : uint32_t
    number_of_relocations   : uint16_t
    number_of_line_numbers  : uint16_t
    characteristics         : uint32_t

assert ctypes.sizeof(ImageSectionHeader) == 8+4+4+4+4+4+4+2+2+4
