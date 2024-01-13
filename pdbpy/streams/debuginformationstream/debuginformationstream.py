from ctypes import sizeof as c_sizeof
from typing import List

from memorywrapper import make_slices

from pdbpy.msf import MultiStreamFileStream
from pdbpy.streams.debuginformationstream.dbidbgheader import DbiDbgHeader
from pdbpy.streams.debuginformationstream.dbistreamheader import PDBDbiStreamHeader
from pdbpy.streams.debuginformationstream.moduleinformation import ModuleInformation
from pdbpy.streams.debuginformationstream.sectionmap import (
    SectionMapEntry,
    SectionMapHeader,
)


class PdbDebugInformationStream:
    """
    This is often called the DBI stream.

    """

    dbg_header: DbiDbgHeader

    def __init__(
        self,
        file: MultiStreamFileStream,
        upfront_memory: bool = False,
        debug: bool = False,
    ):
        self.debug = debug
        self.file = file
        self.modules: List[ModuleInformation] = []
        self.section_map: List[SectionMapEntry] = []

        if upfront_memory:
            self.file = bytes(file)

        self.header = PDBDbiStreamHeader.from_buffer_copy(self.file[: c_sizeof(PDBDbiStreamHeader)])

        assert (
            self.header.magic == 0xFFFFFFFF
        ), f"DebugInformationStream magic bytes expected to be 0xFFFFFFFF, was 0x{self.header.magic:X}"
        # print(self.header)

        # Parse modules (variable sized)
        dbiex_area = memoryview(
            bytes(self.file[c_sizeof(self.header) : c_sizeof(self.header) + self.header.module_size])
        )
        while len(dbiex_area) != 0:
            module_info, bytecount = ModuleInformation.from_memory(memoryview(dbiex_area), False)
            # print(f"0x{len(self.modules):X}: {module_info.module} {module_info.object}")
            dbiex_area = dbiex_area[bytecount:]
            self.modules.append(module_info)

        # Skip section contribution until we figure out why we want that I guess
        # https://github.com/microsoft/microsoft-pdb/blob/082c5290e5aff028ae84e43affa8be717aa7af73/PDB/dbi/dbi.cpp#L540
        section_contribution_start: int = c_sizeof(PDBDbiStreamHeader) + self.header.module_size
        section_contribution_end: int = section_contribution_start + self.header.section_contribution_stream_size

        # Thought this was going to be relevant, but it's not useful at all.
        # See notes in `sectionmap.py` about usefullness.
        section_map_start: int = section_contribution_end
        section_map_end: int = section_map_start + self.header.section_map_size
        section_map_memory = self.file[section_map_start:section_map_end]
        section_map_header = SectionMapHeader.from_buffer_copy(section_map_memory)
        section_map_header.segment_count
        section_map_memory = section_map_memory[4:]
        section_entry_views = make_slices(section_map_memory, c_sizeof(SectionMapEntry))
        self.section_map = [SectionMapEntry.from_buffer_copy(view) for view in section_entry_views]

        file_info_start: int = section_map_end
        file_info_end: int = file_info_start + self.header.file_info_size

        tsm_start: int = file_info_end
        tsm_end: int = tsm_start + self.header.typeserver_map_stream_size

        ec_start: int = tsm_end
        ec_end: int = ec_start + self.header.ecinfo_stream_size

        # https://github.com/microsoft/microsoft-pdb/blob/082c5290e5aff028ae84e43affa8be717aa7af73/PDB/dbi/dbi.cpp#L689
        # https://github.com/willglynn/pdb/blob/master/src/dbi.rs#L614
        # potentially not enough to fill a full struct, and internal implementation leakage?
        dbg_start: int = ec_end
        dbg_end: int = dbg_start + self.header.dbg_header_size
        # We pad with 0 since we're not guaranteed to get data for all fields.
        dbg_memory = bytes(self.file[dbg_start:dbg_end]) + b"\x00" * c_sizeof(DbiDbgHeader)
        self.dbg_header = DbiDbgHeader.from_buffer_copy(dbg_memory)
