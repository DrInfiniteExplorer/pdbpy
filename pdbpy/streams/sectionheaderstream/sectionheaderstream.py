

from typing import Generator, List, Optional, Sequence
from pdbpy.codeview.records.symbols.base import SymbolBase, associate_symbols
from pdbpy.codeview.symbols import SymEnum
from pdbpy.msf import MultiStreamFileStream
from dtypes.structify import Structy, structify
from dtypes.typedefs import uint16_t, uint32_t
from ctypes import sizeof as c_sizeof

from pdbpy.pe.records import ImageSectionHeader
from pdbpy.utils.range_keys import chunk


class PdbSectionHeaderStream:

    sections: Sequence[ImageSectionHeader]

    def __init__(self, file: MultiStreamFileStream, upfront_memory : bool = False, debug : bool=False):
        self.debug = debug
        self.file = file

        if upfront_memory:
            self.file = bytes(file)
        
        file_chunks = chunk(self.file, c_sizeof(ImageSectionHeader))
        self.sections = [ImageSectionHeader.from_buffer_copy(section_mem) for section_mem in file_chunks]
