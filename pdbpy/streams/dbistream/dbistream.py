from ctypes import sizeof as c_sizeof
from dtypes.structify import Structy, structify
from dtypes.typedefs import uint32_t, int32_t, uint16_t

from pdbpy.msf import MultiStreamFileStream

# https://github.com/moyix/pdbparse/blob/c895f8ff7439f912ce4944489656e6cc7f960fb6/pdbparse/dbi.py#L103
# https://github.com/microsoft/microsoft-pdb/blob/805655a28bd8198004be2ac27e6e0290121a5e89/PDB/dbi/dbi.cpp#L279
# https://github.com/microsoft/microsoft-pdb/blob/805655a28bd8198004be2ac27e6e0290121a5e89/PDB/dbi/dbi.h#L95
# https://github.com/microsoft/microsoft-pdb/blob/805655a28bd8198004be2ac27e6e0290121a5e89/PDB/dbi/dbi.h#L124 NEW HEADER
@structify
class PDBDbiStreamHeader(Structy):
    version                 : uint32_t


a = PDBDbiStreamHeader()

class PdbDbiStream:
    def __init__(self, file: MultiStreamFileStream, stream_directory : 'StreamDirectoryStream',  upfront_memory = False, debug=False):
        self.debug = debug
        self.file = file
        self.stream_directory = stream_directory

        if upfront_memory:
            self.file = file[::'copy']

        header = PDBDbiStreamHeader.from_buffer_copy(self.file[:c_sizeof(PDBDbiStreamHeader)])
