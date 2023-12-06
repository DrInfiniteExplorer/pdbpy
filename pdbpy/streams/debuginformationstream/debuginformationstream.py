from ctypes import sizeof as c_sizeof
from typing import TypeAlias
from dtypes.structify import Structy, structify
from dtypes.typedefs import uint8_t, uint16_t, uint32_t


from pdbpy.msf import MultiStreamFileStream
from pdbpy.streams.directorystream.streamdirectory import StreamDirectoryStream
from pdbpy.utils.ctypes import Flaggy

StreamNumber : TypeAlias = uint16_t

# https://github.com/microsoft/microsoft-pdb/blob/805655a28bd8198004be2ac27e6e0290121a5e89/PDB/dbi/dbi.h#L187
@structify
class PDBDbiStreamHeaderFlags(Flaggy):
    incremental_link    : (uint8_t, 1)
    stripped            : (uint8_t, 1)
    c_types             : (uint8_t, 1) # CTypes??
    unused              : (uint16_t, 13)

# https://github.com/moyix/pdbparse/blob/c895f8ff7439f912ce4944489656e6cc7f960fb6/pdbparse/dbi.py#L31
# https://github.com/microsoft/microsoft-pdb/blob/805655a28bd8198004be2ac27e6e0290121a5e89/PDB/dbi/dbi.cpp#L279
# https://github.com/microsoft/microsoft-pdb/blob/805655a28bd8198004be2ac27e6e0290121a5e89/PDB/dbi/dbi.h#L124 NEW HEADER
# https://github.com/volatilityfoundation/volatility3/blob/8e420dec41861993f0cd2837721af2d3e7a6d07a/volatility3/framework/symbols/windows/pdb.json#L420
@structify
class PDBDbiStreamHeader(Structy):
    _pack_ = 1

    magic                            : uint32_t # 0xFFFFFFFF
    version                          : uint32_t
    age                              : uint32_t
    global_symbol_stream_index       : StreamNumber
    vers                             : uint16_t # https://github.com/microsoft/microsoft-pdb/blob/805655a28bd8198004be2ac27e6e0290121a5e89/PDB/dbi/dbi.h#L143-L155
    public_symbol_stream_index       : StreamNumber
    pdb_building_dll_version         : uint16_t # version of DLL that built PDB
    symbol_record_stream             : StreamNumber
    pdb_building_dll_rbld_version    : uint16_t # like the version above, but... rbld?
    _module_size                      : uint32_t # Total size of extended headers following this header
    section_contribution_stream_size : uint32_t
    section_map_size                 : uint32_t
    file_info_size                   : uint32_t
    typeserver_map_stream_size       : uint32_t
    mfc_type_server_index            : uint32_t
    dbg_header_size                  : uint32_t # at end of stream
    ecinfo_stream_size               : uint32_t
    flags                            : PDBDbiStreamHeaderFlags
    machine                          : uint16_t
    reserved                         : uint32_t

    @property
    def module(self) -> int: return self._module




class PdbDebugInformationStream:
    """
    This is often called the DBI stream.

    """
    def __init__(self, file: MultiStreamFileStream, stream_directory : StreamDirectoryStream, upfront_memory : bool = False, debug : bool=False):
        self.debug = debug
        self.file = file

        if upfront_memory:

            self.file = bytes(file)

        self.header = PDBDbiStreamHeader.from_buffer_copy(self.file[:c_sizeof(PDBDbiStreamHeader)])

        assert self.header.magic == 0xFFFFFFFF, f"DebugInformationStream magic bytes expected to be 0xFFFFFFFF, was 0x{self.header.magic:X}"
        print(self.header)

        #print(stream_directory.stream_count)
        #public = stream_directory.get_stream_by_index(self.header.public_symbol_stream_index)
        #print(public)
        #print(stream_directory.get_stream_by_index(self.header.global_symbol_stream_index))

        dbiex_area = self.file[c_sizeof(self.header) : c_sizeof(self.header) + self.header.module_size]

