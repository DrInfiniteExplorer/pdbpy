from ctypes import sizeof as c_sizeof

from dtypes.structify import structify
from dtypes.typedefs import uint16_t

from .base import record, PackedStructy, extract_padding
from ..leaf_enum import LeafID

from ..parse import parse_record

@record(LeafID.FIELDLIST)
@structify
class FieldList(PackedStructy):
    record_type     : uint16_t
    # members : List[PackedStructy]

    @classmethod
    def from_memory(cls, mem, offset, record_size : int, debug : bool):

        assert isinstance(record_size, int), "Parsing a field list requires knowledge of how large the total record is!"

        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(mem[offset: offset + my_size])
        self.addr = offset
        post_read_offset = offset + my_size

        post_record = offset + record_size

        self.members = []

        while post_read_offset < post_record:

            post_read_offset, member = parse_record(mem, post_read_offset, padding_cricital=True, debug=debug)
            self.members.append(member)
            #print(f"Member is {member}")
            #print(f"{post_read_offset} - {post_record}")

            # paddy padd!
            if post_read_offset < post_record:
                paddy = extract_padding(mem, post_read_offset, required=False)
                if debug:
                    print(f"Padding {post_read_offset} with {paddy}")
                post_read_offset += paddy


        return post_read_offset, self
