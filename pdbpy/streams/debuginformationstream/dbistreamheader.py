from ctypes import sizeof as c_sizeof
from dtypes.structify import Structy, structify
from dtypes.typedefs import uint16_t, uint32_t

from pdbpy.utils.ctypes import Flaggy

from pdbpy.types import StreamNumber16


# https://github.com/microsoft/microsoft-pdb/blob/805655a28bd8198004be2ac27e6e0290121a5e89/PDB/dbi/dbi.h#L187
@structify
class PDBDbiStreamHeaderFlags(Flaggy):
    _pack_ = 1
    incremental_link    : (uint16_t, 1)
    stripped            : (uint16_t, 1)
    c_types             : (uint16_t, 1) # CTypes??
    unused              : (uint16_t, 13)
assert c_sizeof(PDBDbiStreamHeaderFlags) == 2

# https://github.com/moyix/pdbparse/blob/c895f8ff7439f912ce4944489656e6cc7f960fb6/pdbparse/dbi.py#L31
# https://github.com/microsoft/microsoft-pdb/blob/805655a28bd8198004be2ac27e6e0290121a5e89/PDB/dbi/dbi.cpp#L279
# https://github.com/microsoft/microsoft-pdb/blob/805655a28bd8198004be2ac27e6e0290121a5e89/PDB/dbi/dbi.h#L124 NEW HEADER
# https://github.com/volatilityfoundation/volatility3/blob/8e420dec41861993f0cd2837721af2d3e7a6d07a/volatility3/framework/symbols/windows/pdb.json#L420
@structify
class PDBDbiStreamHeader(Structy):
    _pack_ = 1

    magic                             : uint32_t # 0xFFFFFFFF
    version                           : uint32_t
    age                               : uint32_t
    # snGSSyms in microsoft-pdb.
    # Used in `OpenGlobals` https://github.com/microsoft/microsoft-pdb/blob/805655a28bd8198004be2ac27e6e0290121a5e89/PDB/dbi/dbi.cpp#L1385
    # Corresponds to "*** GLOBALS" in cvdump
    # Is a hash table stream into symbol_record_stream (hash of fqn)
    global_symbol_stream_index        : StreamNumber16
    vers                              : uint16_t # https://github.com/microsoft/microsoft-pdb/blob/805655a28bd8198004be2ac27e6e0290121a5e89/PDB/dbi/dbi.h#L143-L155

    # snPSSyms n microsoft-pdb.
    # Used in `OpenPublics` https://github.com/microsoft/microsoft-pdb/blob/805655a28bd8198004be2ac27e6e0290121a5e89/PDB/dbi/dbi.cpp#L1420
    # Corresponds to "*** PUBLICS" in cvdump
    # Is a hash table stream into symbol_record_stream (hash of mangled)
    public_symbol_stream_index        : StreamNumber16

    pdb_building_dll_version          : uint16_t # version of DLL that built PDB


    # snSymRecs in microsoft-pdb.
    # just symbols in general?? what? :sob:
    # willglyn/pdb refers to this as the global symbol stream, though it isn't by microsoft? https://github.com/willglynn/pdb/blob/b052964e09d03eb190c8a60dc76344150ff8a9df/src/pdb.rs#L175
    # moyix/pdbparse also parses this stream instead of the other streams https://github.com/moyix/pdbparse/blob/c895f8ff7439f912ce4944489656e6cc7f960fb6/pdbparse/__init__.py#L285
    # volatility3 calls it symrecStream https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/symbols/windows/pdb.json#L475
    symbol_record_stream              : StreamNumber16
    pdb_building_dll_rbld_version     : uint16_t # like the version above, but... rbld?
    _module_size                      : uint32_t # Total size of extended headers following this header? Also called `cbGpModi` in microsoft-pdb
    _section_contribution_stream_size : uint32_t # cbSC       in microsoft-pdb
    _section_map_size                 : uint32_t # cbSecMap   in microsoft-pdb
    _file_info_size                   : uint32_t # cbFileInfo in microsoft-pdb
    _typeserver_map_stream_size       : uint32_t # cbTSMap    in microsoft-pdb
    mfc_type_server_index             : uint32_t
    _dbg_header_size                  : uint32_t # at end of stream
    _ecinfo_stream_size               : uint32_t # cbECInfo   in microsoft-pdb
    flags                             : PDBDbiStreamHeaderFlags
    machine                           : uint16_t
    reserved                          : uint32_t

    @property
    def module_size(self) -> int: return self._module_size # type: ignore
    @property
    def section_contribution_stream_size(self) -> int: return self._section_contribution_stream_size # type: ignore
    @property
    def section_map_size(self) -> int: return self._section_map_size # type: ignore
    @property
    def file_info_size(self) -> int: return self._file_info_size # type: ignore
    @property
    def typeserver_map_stream_size(self) -> int: return self._typeserver_map_stream_size # type: ignore
    @property
    def ecinfo_stream_size(self) -> int: return self._ecinfo_stream_size # type: ignore
    @property
    def dbg_header_size(self) -> int: return self._dbg_header_size # type: ignore

