from ctypes import sizeof as c_sizeof

@record(LeafID.yolo)
@structify
class ASD(PackedStructy):
    record_type     : uint16_t

    @classmethod
    def from_memory(cls, mem, offset, record_size : int, debug : bool):

        my_size = c_sizeof(cls)
        self = cls.from_buffer_copy(mem[offset: offset + my_size])
        self.addr = offset
        post_read_offset = offset + my_size

        return post_read_offset, self
