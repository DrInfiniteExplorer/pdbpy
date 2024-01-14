
from typing import Dict, Optional, Self
from dtypes.structify import structify, Structy
from dtypes.typedefs import uint16_t

from pdbpy.codeview.symbols import SymEnum

@structify
class SymbolBase(Structy):
    _pack_ = 1
    _record_length     : uint16_t 
    _record_type       : uint16_t # SymType

    @property
    def record_length(self) -> int: return self._record_length # type: ignore

    @property
    def record_type(self) -> SymEnum: return SymEnum(self._record_type) # type: ignore

    @classmethod
    def from_memory(cls, mem: memoryview, length : int, type: SymEnum) -> Self:
        raise NotImplementedError()


class Associator[Id, Type]:
    def __init__(self, registry: Optional[Dict[Id, Type]] = None):
        self.registry = registry or dict()
    def __call__(self, *ids : Id):
        def the_types_tho(typ : Type) -> Type:
            for id in ids:
                self.registry[id] = typ
            return typ
        return the_types_tho

associate_symbols = Associator[SymEnum, type[SymbolBase]]()

