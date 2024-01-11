

from typing import Generator, List, Optional
from pdbpy.codeview.records.symbols.base import SymbolBase, associate_symbols
from pdbpy.codeview.symbols import SymEnum
from pdbpy.msf import MultiStreamFileStream
from dtypes.structify import Structy, structify
from dtypes.typedefs import uint16_t, uint32_t
from ctypes import sizeof as c_sizeof


@structify
class SymbolInformation(Structy):
    _pack_ = 1
    symtype   : uint32_t
    offset    : uint32_t
    segment   : uint16_t
    # name

assert c_sizeof(SymbolInformation) == 4+4+2


class PdbSymbolRecordStream:

    def __init__(self, file: MultiStreamFileStream, upfront_memory : bool = False, debug : bool=False):
        self.debug = debug
        self.file = file

        if upfront_memory:
            self.file = bytes(file)
        
    def symbols(self, types: Optional[List[SymEnum]] = None) -> Generator[SymbolBase, None, None]:
        memory = self.file[:]
        while len(memory):

            base = SymbolBase.from_buffer_copy(memory[0:4])
            record_length = base.record_length

            assert record_length >= 2
            assert record_length <= len(memory)-2, f"Record says it wants to read {record_length} out of {len(memory)-2} available bytes"
            record_data = memory[:record_length+2]

            memory = memory[record_length+2:]

            typ = base.record_type
            #if typ in (SymEnum.S_ALIGN, SymEnum.S_SKIP):
            #    continue
            if types is not None:
                if typ not in types:
                    continue

            klass = associate_symbols.registry.get(typ, None)
            if klass is None:
                #print(f"Found no class for {typ.name}")
                continue
            symbol = klass.from_memory(memoryview(record_data), record_length, base.record_type)
            yield symbol



