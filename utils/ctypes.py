
import ctypes

from enum import IntEnum

from dtypes.structify import get_name_adjusted_fields

class Flaggy(ctypes.Structure):
    """
    Helper baseclass that prints contents of fields in repr (no py members tho)
    """
    def __repr__(self):        
        stuff = []
        for s in get_name_adjusted_fields(self):
            name = s[0]
            size = s[2]
            val = getattr(self, name)
            if val:
                if isinstance(val, IntEnum):
                    val = f"{val.name}={val}"
                stuff.append(f"{name}" if size == 1 else f"{name}({val})")
        return " | ".join(stuff)


# https://stackoverflow.com/questions/23131237/python-ctype-bitfields-get-bitfield-location
def DebugPrintBitfield(Type):
    for field_descr in Type._fields_:        
        name = field_descr[0]
        field = getattr(Type, name)    
        bfield_bits = field.size >> 16    
        if bfield_bits:
            start = 8 * field.offset + field.size & 0xFFFF
            stop = start + bfield_bits
        else:
            start = 8 * field.offset
            stop = start + 8 * field.size
        print("{:>10s}: bits {:>2d}:{:>2d}".format(
            name, start, stop))


