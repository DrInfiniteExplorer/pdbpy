
from typing import Optional, Tuple

from dtypes.typedefs import uint16_t

from .records.base import PackedStructy, get_record_type_by_leaf_type

def parse_record(mem : memoryview, record_content_offset:int, record_type:Optional[int] = None,
                 record_size_bytes:Optional[int] = None, padding_cricital:bool = False, debug:bool=False) -> Tuple[int, PackedStructy]:
    """
    Returns a tuple of (the first byte after the end of the record) and (the record object)
    """
    if record_type is None:
        record_type = uint16_t.from_buffer_copy(mem[record_content_offset : record_content_offset + 2]).value

    if debug:
        print(f"Record type: {record_type} | 0x{record_type:X}")
    
    
    typ = get_record_type_by_leaf_type(record_type)
    if typ is None:
        if debug or True:
            print(f"Can't deal with {LeafID(record_type).name} yet")
        return None, None
    
    post_read_offset, parsed = typ.from_memory(mem, record_content_offset, record_size = record_size_bytes, debug=debug)
    if debug:
        print(parsed)

    padding = 0
    if record_size_bytes is not None:
        expected_end = record_content_offset + record_size_bytes
        assert post_read_offset <= expected_end, f"READ TOO FAR! Read to {post_read_offset}, ought to have read to {expected_end}, which is {post_read_offset-expected_end} too much!"
        if post_read_offset != expected_end:
            if debug:
                print(f"Read to {post_read_offset}, expected to land at {expected_end}")
            if padding_cricital:
                padding = extract_padding(mem, post_read_offset, required=True)
                assert post_read_offset + padding == expected_end, f"{post_read_offset} is not {record_content_offset + record_size_bytes} as was expected, we didn't read the previous record correctly???"
                if debug:
                    print(f"Padding-bytes made short work if the inconsistency")
    
    return post_read_offset + padding, parsed
