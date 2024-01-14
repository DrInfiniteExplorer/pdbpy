from ctypes import sizeof as c_sizeof

from dtypes.structify import structify
from dtypes.typedefs import uint16_t, uint32_t

from pdbpy.codeview.symbols import SymEnum
from pdbpy.codeview.types import type_index
from pdbpy.parsing import read_pascalstring, read_stringz

from .base import SymbolBase, associate_symbols


@associate_symbols(
    SymEnum.S_LDATA32_ST,
    SymEnum.S_LDATA32,
    SymEnum.S_GDATA32_ST,
    SymEnum.S_GDATA32,
    SymEnum.S_LTHREAD32_ST,
    SymEnum.S_LTHREAD32,
    SymEnum.S_GTHREAD32_ST,
    SymEnum.S_GTHREAD32,
)
@structify
class DataSym(SymbolBase):
    # from base class:
    # record_length     : uint16_t
    # record_type       : uint16_t
    typ: type_index
    _offset: uint32_t
    _segment: uint16_t
    # name : str

    @property
    def offset(self) -> int:
        return self._offset  # type: ignore

    @property
    def segment(self) -> int:
        return self._segment  # type: ignore

    @classmethod
    def from_memory(cls, mem: memoryview, length: int, type: SymEnum) -> "DataSym":
        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(mem[:my_size])
        self.memory = mem

        if self.record_type > SymEnum.S_ST_MAX:
            self.name, bytecount = read_stringz(mem[my_size:])
        else:
            self.name, bytecount = read_pascalstring(mem[my_size:])

        return self

    def __str__(self):
        return f"{self.record_type.name} {self.name:40} at {self.offset:8}@{self.segment}"


__all__ = ("DataSym",)
