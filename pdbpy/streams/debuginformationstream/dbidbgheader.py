from dtypes.structify import Structy, structify


from pdbpy.types import StreamNumber16

# https://github.com/moyix/pdbparse/blob/c895f8ff7439f912ce4944489656e6cc7f960fb6/pdbparse/dbi.py#L103
# https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/symbols/windows/pdb.json#L570
# https://github.com/willglynn/pdb/blob/master/src/dbi.rs#L590
# https://github.com/Microsoft/microsoft-pdb/blob/082c5290e5aff028ae84e43affa8be717aa7af73/PDB/dbi/dbi.h#L250-L274
@structify
class DbiDbgHeader(Structy):
    _pack_ = 1

    FPO              : StreamNumber16
    exception        : StreamNumber16
    fixup            : StreamNumber16
    omap_to_src      : StreamNumber16
    src_to_omap      : StreamNumber16
    section_header   : StreamNumber16
    token_rid_map    : StreamNumber16
    xdata            : StreamNumber16
    pdata            : StreamNumber16
    new_FPO          : StreamNumber16
    section_hdr_orig : StreamNumber16

