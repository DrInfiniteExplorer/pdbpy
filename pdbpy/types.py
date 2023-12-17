

from typing import TypeAlias
from dtypes.typedefs import uint16_t, uint32_t

StreamNumber16  : TypeAlias = uint16_t # SN    in microsoft-pdb https://github.com/microsoft/microsoft-pdb/blob/082c5290e5aff028ae84e43affa8be717aa7af73/PDB/include/msf.h#L39
ModuleIndex16   : TypeAlias = uint16_t # IMOD  in microsoft-pdb https://github.com/microsoft/microsoft-pdb/blob/082c5290e5aff028ae84e43affa8be717aa7af73/PDB/include/pdbtypdefs.h#L41
SectionIndex16  : TypeAlias = uint16_t # ISECT in microsoft-pdb https://github.com/microsoft/microsoft-pdb/blob/082c5290e5aff028ae84e43affa8be717aa7af73/PDB/include/pdbtypdefs.h#L42
ByteCount32     : TypeAlias = uint32_t # CB    in microsoft-pdb https://github.com/microsoft/microsoft-pdb/blob/082c5290e5aff028ae84e43affa8be717aa7af73/PDB/include/pdbtypdefs.h#L13
Offset32        : TypeAlias = uint32_t # OFF   in microsoft-pdb https://github.com/microsoft/microsoft-pdb/blob/082c5290e5aff028ae84e43affa8be717aa7af73/PDB/include/pdbtypdefs.h#L14
FileCount16     : TypeAlias = uint16_t # IFILE in microsoft-pdb https://github.com/microsoft/microsoft-pdb/blob/805655a28bd8198004be2ac27e6e0290121a5e89/PDB/dbi/dbiimpl.h#L50
NameIndex32     : TypeAlias = uint32_t # NI    in microsoft-pdb https://github.com/microsoft/microsoft-pdb/blob/805655a28bd8198004be2ac27e6e0290121a5e89/langapi/include/pdb.h#L134
