from dtypes.structify import Structy, structify
from dtypes.typedefs import int32_t, uint16_t, uint32_t

from pdbpy.codeview.types import type_index


@structify
class OffsetSizePair(Structy):
    offset: int32_t
    byte_count: int32_t


@structify
class PDBTypeStreamHeader(Structy):
    version: uint32_t
    header_size_bytes: int32_t
    ti_min: type_index
    ti_max: type_index
    records_byte_count: uint32_t
    hash_stream_number: uint16_t
    aux_hash_stream_num: uint16_t  # ignore yolo
    hash_key_size_bytes: int32_t
    buckets: uint32_t
    hash_value_buffer: OffsetSizePair
    index_offset_buffer: OffsetSizePair
    hash_adjustment_buffer: OffsetSizePair
