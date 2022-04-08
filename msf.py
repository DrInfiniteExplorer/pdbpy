
from io import IOBase
from typing import Sequence
import mmap
import ctypes

from pdbpy.utils.ctypes import (Structy, structify, uint32_t)

@structify
class BigHeader(Structy):
    magic: ctypes.c_char*30
    page_size: uint32_t
    free_page_map: uint32_t
    pages_used: uint32_t
    directory_size_in_bytes: uint32_t
    _reserved: uint32_t



class MultiStreamFileStream(IOBase):
    """
    Usually created by `StreamDirectoryStream.get_stream_by_index`, which you'd do by
    > msf_stream = msf.get("Directory")
    > directory = pdbpy.streams.StreamDirectoryStream(msf_stream)
    > desired_stream = directory.get_stream_by_index(idx)

    Often you'd pass this along to a specific stream-reader,
     just as is done with to `pdbpy.streams.StreamDirectoryStream`.

    Contains info about where it belongs within the parent `MultiStreamFile`.
    Forwards read-requests to `MultiStreamFile` with it's own information.
    Incomplete IOBase -interface.

    Content mapping / reading is as described in `MultiStreamFile`, with the addition
     that one can slice the stream using `[start : stop]` notation to get a view
     of the corresponding bytes.
    NOTE that slicing across page boundaries can't result in a contiguous mapping,
     and raises an error. It's possible to pass the string 'copy' as a last argument
     to the slicing to obtain a stitched copy of the bytes across boundaries,
     like this: `stream[:-10:'copy']` which would return a copy(if necessary) of the
     last 10 bytes in the stream.

    """
    def __init__(self, parent : 'MultiStreamFile', page_list : Sequence[int], size_bytes : int, streamname : str, debug = False):
        assert streamname not in parent.children, f"A stream called {streamname} is already registered in the parent MultiStreamFile"

        self.parent = parent
        self.page_list = page_list
        self.streamname = streamname

        self.size_bytes = size_bytes
        self.pos = 0

        self.debug = debug

        parent.children[streamname] = self
    
    def __repr__(self):
        return str(self.__dict__)
    
    def write(self, bytes):
        raise UnsupportedOperation("MultiStreamFileStream does not (currently yolo) implement 'write'")
    
    def read(self, bytes) -> bytes:
        data = parent.read_pages(self.page_list, byte_offset = self.pos, byte_count = bytes)
        self.pos += bytes
        return data
    
    def map_pages(self, **kwargs) -> 'List[memory(sub?)view]':
        args = dict(**kwargs)
        args.update(byte_count = kwargs.get('byte_count', self.size_bytes))
        return self.parent.map_pages(page_list = self.page_list, **args)

    def read_pages(self, **kwargs) -> bytes:
        args = dict(**kwargs)
        args.update(byte_count = kwargs.get('byte_count', self.size_bytes))
        return self.parent.read_pages(page_list = self.page_list, **args)
    
    def __getitem__(self, key):
        if type(key) is int:
            return read_pages(byte_offset = key, byte_count=1)[0]
        if isinstance(key, slice):
            start, stop = key.start, key.stop
            size_bytes = self.size_bytes
            if start is None:
                start = 0
            if stop is None:
                stop = size_bytes
            if start < 0:
                start = size_bytes + start
            if stop < 0:
                stop = size_bytes + stop
            
            if self.debug:
                print("!", start, stop)

            start_page = start // self.parent.page_size
            stop_page = stop // self.parent.page_size
            
            all_me = self.map_pages(byte_offset = start, byte_count = stop - start, debug=self.debug)
            if start_page != stop_page:
                if key.step != 'copy':
                    raise ValueError(f"Can't slice MultiStreamFileStream across pages unless the 'step' in the slice is 'copy' in which case a copy is returned instead of a memory(sub)view (reading bytes {start}-{stop} from pages {start_page} to {stop_page})")
                return b''.join(all_me)
            #print(all_me)
            assert len(all_me) == 1            
            return all_me[0]
            


class MultiStreamFile:
    """
    A multi-stream-file contains streams n shit.
    They are split into pages of a certain size, and the pages can be scattered throughout the file.
    A _page list_ is a list of page numbers in the file.
    Read them in the specified order and stitch their contents together to get the data you want.

    First is a header.
    Next up is a list of the streams: How many bytes they are comprised of, and what their page-lists are.

    But this "stream directory" -information can itself be >1page, so to read it, we need to read the
     stream-directory page-list.
    Then we can stich those pages together to get the List[Pair[StreamByteCount, List[PageNumbers]]] -info.
    
    Since directory/root -information is scattered with (byte_count, [page_number, ...]), it itself is
     essentially a stream, and is often considered to be "stream 0".


    
    Reading is done through a memory-mapped file by calling `map_pages`.
    You give it a page-list, an optional byte-offset, and an optional count of bytes to read.
    A list of memoryviews corresponding to the pages(and their relevant content) are returned,
     and it's up to the caller to use that properly when doing lookups.
    
    If a list of memory views is to bothersome, there is `read_pages` which calls `map_pages`,
     joins the mapped bytes into a single object, and returns it.
    
    Reading should likely be done through a `MultiStreamFileStream`-object instead instead, but the
     semantics for reading that is the same as here.

    """

    def __init__(self, file):
        self.file = file
        self.mmap = mmap.mmap(file.fileno(), length = 0, access = mmap.ACCESS_READ)
        self.mem = memoryview(self.mmap)

        self.children = dict()

        self.header = BigHeader.from_buffer_copy(self.mem)
        assert self.header.magic == b"Microsoft C/C++ MSF 7.00\r\n\x1a\x44\x53", f"Can only deal with 'big' header type and 'MSF 7.0' version, got {self.header.magic}"
        print(f"page size: {self.header.page_size}")

        for name, type in self.header._fields_[1:]:
            setattr(self, name, getattr(self.header, name))

        # The directory may be fragmented into a number of pages scattered throughout the file.
        # How many pages do we need, to make an index of all those pages?
        directory_indices_count = self.pages_to_contain_bytes(self.directory_size_in_bytes)

        print(f"Directory size: {self.directory_size_in_bytes}")
        print(f"Directory indices count: {directory_indices_count}")

        # How many pages are needed to store the index above?
        # Every index is 4 bytes, so we need pages for index_length*4 bytes
        page_count_to_contain_directory_page_indices = self.pages_to_contain_bytes(4 * directory_indices_count)
        print(f"Page count to contain directory page indices: {page_count_to_contain_directory_page_indices}")

        SizeOfBigHeader = ctypes.sizeof(BigHeader)
        list_of_pages_that_contain_directory_indices = (uint32_t * page_count_to_contain_directory_page_indices).from_buffer_copy(self.mem, SizeOfBigHeader)
        print(f"Page numbers that contain directory indices: {list(list_of_pages_that_contain_directory_indices)}")

        # Read all pages with directory indices
        directory_page_indices_data = self.read_pages(list_of_pages_that_contain_directory_indices, byte_count = 4 * directory_indices_count)

        directory_page_indices = (uint32_t * directory_indices_count).from_buffer_copy(directory_page_indices_data)
        print(f"Directory page indices: {list(directory_page_indices)}")

        self.pdb_root_stream_pages = list(directory_page_indices)

        ############# READING ROOT PDB STREAM YEEEEEEEEEEEEEE???

        pdb_stream = MultiStreamFileStream(parent=self, page_list = self.pdb_root_stream_pages, size_bytes = self.directory_size_in_bytes, streamname="Directory")

    def __repr__(self):
        return str(self.__dict__)


    def map_pages(self, page_list, yeet=None, byte_offset = 0, byte_count=None, debug=False) -> 'List[memory(sub?)view]':
        """
        Returns a list of memory-subviews that represent the area requested.
        Join yourself or use `read_pages` to get a corresponding contiguous bytes-object.
        """

        assert yeet is None, "yeet got a value; pass byte_offset and/or byte_count by name!"

        page_size = self.page_size

        start_page = byte_offset // page_size
        end_page = (byte_offset + byte_count) // page_size
        byte_offset = byte_offset % page_size

        if start_page == end_page:
            start = page_list[start_page] * page_size + byte_offset
            return (self.mem[start : start + byte_count],)

        pages_to_read = page_list[start_page:]

        # TODO: Massage pages_to_read to be a zip of (page_start, page_size) to merge continuous page numbers


        if byte_count is None:
            bytes_left = len(pages_to_read) * page_size - byte_offset 
        else:
            bytes_left = byte_count
        #bytes_left = len(pages_to_read) * page_size - byte_offset if byte_count is None else byte_count
        
        #if debug:
        #    print()
        #    print(f"Start page: {start_page}")
        #    print(f"Byte offset: {byte_offset}")
        #    print(f"Pages: {pages_to_read}")
        #    print(f"Bytes to read: {bytes_left}")



        
        #if debug:
        #    print()

        areas = []
        page_list_iter = iter(pages_to_read)

        #def range_iterator(offset, count, lst):
        #    lst_iter = iter(lst)
        #    if offset != 0:
        #        dist = min(offset + count, page_size) - offset
        #        yield (offset, offset + dist, next(lst))
        #    while count > 0:
        #        dist = min(count, page_size)
        #        yield (0, dist, next(lst))
        #        count -= dist



        while bytes_left > 0:
            #if debug: print()       
            page_num = next(page_list_iter)
            #if debug: print(f"Page num: {page_num}")
            addr = page_size * page_num
            read_amount = min(byte_offset + bytes_left, page_size) - byte_offset
            #if debug: print(f"Read amount: {read_amount}")
            #if debug: print(f"Reading from {byte_offset} to {byte_offset + read_amount}")
            area = self.mem[addr + byte_offset : addr + byte_offset + read_amount]
            areas.append(area)
            byte_offset = 0
            bytes_left -= read_amount
        #if debug: print()
        return areas

    def read_pages(self, page_list: 'List[int]', yeet=None, byte_offset = 0, byte_count=None) -> bytes :
        """
        Returns a copied byte-object containing the desired data.
        """

        return b''.join(self.map_pages(page_list, yeet=yeet, byte_offset = byte_offset, byte_count = byte_count))

    def pages_to_contain_bytes(self, byte_count) -> int:
        """
        How many pages do we need to contain byte_count
        """
        page_size = self.page_size
        return (byte_count + page_size - 1 ) // page_size
    
    def get(self, streamname) -> MultiStreamFileStream:
        stream = self.children.get(streamname, None)
        if stream is None:
            raise ValueError(f"No stream named {streamname} available")
        return stream
