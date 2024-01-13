from ctypes import sizeof as c_sizeof
from typing import Sequence

from memorywrapper import make_slices

from pdbpy.msf import MultiStreamFileStream
from pdbpy.pe.records import ImageSectionHeader


class PdbSectionHeaderStream:
    sections: Sequence[ImageSectionHeader]

    def __init__(
        self,
        file: MultiStreamFileStream,
        upfront_memory: bool = False,
        debug: bool = False,
    ):
        self.debug = debug
        self.file = file

        if upfront_memory:
            self.file = bytes(file)

        file_chunks = make_slices(self.file, c_sizeof(ImageSectionHeader))
        self.sections = [ImageSectionHeader.from_buffer_copy(section_mem) for section_mem in file_chunks]
