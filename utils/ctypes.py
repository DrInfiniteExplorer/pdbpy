
import ctypes

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
    print(fields)
    cls._fields_ = fields

    return cls

class Structy(ctypes.Structure):
    """
    Helper baseclass that prints contents of fields in repr (no py members tho)
    """
    def __repr__(self):
        return str({stuff[0] : getattr(self, stuff[0]) for stuff in self._fields_})


class Flaggy(ctypes.Structure):
    """
    Helper baseclass that prints contents of fields in repr (no py members tho)
    """
    def __repr__(self):        
        stuff = []
        for s in self._fields_:
            name = s[0]
            size = s[2]
            val = getattr(self, name)
            if val:
                stuff.append(f"{name}" if size == 1 else f"{name}({val})")
        return " | ".join(stuff)

