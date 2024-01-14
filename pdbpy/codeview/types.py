from typing import TypeAlias

from dtypes.typedefs import uint32_t

_typ_t: TypeAlias = uint32_t

# type_index has two ranges: 0-4095 are "hard known types" while 4096+
#  are specified dynamically in the PDB type stream.
# (the actual dynamic start value is part of the type stream header)
type_index: TypeAlias = _typ_t

# Same underlying type as type_index, but is used to keep track of
#  the counted number of a dynamic type. That is to say,
#  type_index(4096) == dynamic_type_index(0).
dynamic_type_index: TypeAlias = _typ_t

__all__ = ("type_index", "dynamic_type_index")
