
import ctypes

from enum import IntEnum

class BasicWrapperBase(ctypes.Structure):
    pass

def BasicWrapper(Type, name):
    return type(name, (BasicWrapperBase,), dict(
            __str__ = lambda self: str(self.value),
            _fields_ = (("value", Type),)
        )
    )

# These are for allowing "getting" from a struct without py-typifying and losing address of the thing.
# suffix "w" is for "wrapper"
int8_tw = BasicWrapper (ctypes.c_int8,  "int8_tw")
int16_tw = BasicWrapper(ctypes.c_int16, "int16_tw")
int32_tw = BasicWrapper(ctypes.c_int32, "int32_tw")
int64_tw = BasicWrapper(ctypes.c_int64, "int64_tw")
uint8_tw = BasicWrapper (ctypes.c_uint8,  "uint8_tw")
uint16_tw = BasicWrapper(ctypes.c_uint16, "uint16_tw")
uint32_tw = BasicWrapper(ctypes.c_uint32, "uint32_tw")
uint64_tw = BasicWrapper(ctypes.c_uint64, "uint64_tw")

int8_t = ctypes.c_int8
int16_t = ctypes.c_int16
int32_t = ctypes.c_int32
int64_t = ctypes.c_int64
uint8_t = ctypes.c_uint8
uint16_t = ctypes.c_uint16
uint32_t = ctypes.c_uint32
uint64_t = ctypes.c_uint64

float32_t = ctypes.c_float
float64_t = ctypes.c_double


def structify(cls):
    """
    A decorator that can turn simpler class definitions into the more line-noisy
     format that ctypes parses.

    > @structify
    > class BigHeader(ctypes.Structure):
    >     magic: ctypes.c_char*30
    >     page_size: uint32_t
    >     free_page_map: uint32_t
    >     pages_used: uint32_t
    >     directory_size_in_bytes: uint32_t
    >     _reserved: uint32_t

    Also supports bitfields
    > @structify
    > class TypeProperty(Structy):
    >     packed: (uint16_t, 1)
    >     ctor: (uint16_t, 1)
    >     overloaded_operators: (uint16_t, 1)


    """
    fields = []
    for data in cls.__annotations__.items():
        name = data[0]
        rest = data[1]
        rest = rest if isinstance(rest, tuple) else (rest,)
        fields.append((name, *rest))
    #print(fields)
    cls._fields_ = fields

    return cls

#TODO: Memoize???
def get_name_adjusted_fields(struct):
    fields = list(struct._fields_)
    for idx, field in enumerate(fields):
        name = field[0]
        if name.startswith('_') and hasattr(struct, name[1:]):
            fields[idx] = (name[1:], *field[1:])
    return fields



class Structy(ctypes.Structure):
    """
    Helper baseclass that prints contents of fields in repr (no py members tho)
    """
    def __repr__(self):
        names = [f[0] for f in get_name_adjusted_fields(self)]
        names += list(self.__dict__.keys())
        return type(self).__name__ + str({name : getattr(self, name) for name in names})


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


