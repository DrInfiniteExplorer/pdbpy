from pdbpy.msf import MultiStreamFileStream

from dtypes.structify import (Structy, structify)
from dtypes.typedefs import (
    int8_t, int16_t, int32_t,
    uint8_t, uint16_t, uint32_t)


class StreamDirectoryStream:
    def __init__(self, file : MultiStreamFileStream):
        self.file = file

        stream_count = uint32_t.from_buffer_copy(file[:4]).value
        self.stream_count = stream_count
        #print(f"Streams in PDB: {stream_count}")

        stream_sizes = (uint32_t * stream_count).from_buffer_copy(file[4:4+4*stream_count])
        #stream_sizes = list(stream_sizes)
        #print(f"Stream sizes: {[hex(x) for x in stream_sizes]}")

        page_indices_for_streams = []

        start = 4+4*stream_count
        for idx in range(stream_count):
            size_bytes = stream_sizes[idx]
            pages_for_stream = file.parent.pages_to_contain_bytes(size_bytes) if size_bytes != 0xFFFFFFFF else 0
            #print(pages_for_stream)
            if pages_for_stream == 0:
                page_indices_for_streams.append(())
            else:
                indices = (uint32_t * pages_for_stream).from_buffer_copy(file[start : start + 4*pages_for_stream : 'copy'])[:]
                start += 4 * len(indices)
                page_indices_for_streams.append(indices)
        #print(page_indices_for_streams)

        stream_sizes_and_page_lists = list(zip(stream_sizes, page_indices_for_streams))
        self._stream_sizes_and_page_lists = stream_sizes_and_page_lists



    def get_stream_by_index(self, stream_index : int):
        # TODO: Make a small cache of (page_num, read_offset) and make reading of
        #  streams happen on-demand in relation to that?
        assert stream_index >= 0
        assert stream_index < self.stream_count

        byte_count, page_list = self._stream_sizes_and_page_lists[stream_index]

        return MultiStreamFileStream(parent=self.file.parent, page_list = page_list, size_bytes = byte_count, streamname=stream_index)
