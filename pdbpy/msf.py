
from io import IOBase
from typing import Sequence, List, Optional

import mmap
import ctypes

from dtypes.structify import (Structy, structify)
from dtypes.typedefs import uint32_t

from pdbpy.utils.memorywrapper import MemoryWrapper

@structify
class BigHeader(Structy):
    _magic: ctypes.c_char*30
    _page_size: uint32_t
    _free_page_map: uint32_t
    _pages_used: uint32_t
    _directory_size_in_bytes: uint32_t
    _reserved: uint32_t

    # These are just to make the type system happy.
    #  (Accesses turn the types into ints, but the type system doesn't realize that.)
    @property
    def magic(self) -> int: return self._magic # type: ignore
    @property
    def page_size(self) -> int: return self._page_size # type: ignore
    @property
    def free_page_map(self) -> int: return self._free_page_map # type: ignore
    @property
    def pages_used(self) -> int: return self._pages_used # type: ignore
    @property
    def directory_size_in_bytes(self) -> int: return self._directory_size_in_bytes # type: ignore

class MultiStreamFileStream(MemoryWrapper):
    """
    Usually created by `StreamDirectoryStream.get_stream_by_index`, which you'd do by
    > msf_stream = msf.get("Directory")
    > directory = pdbpy.streams.directorystreamStream(msf_stream)
    > desired_stream = directory.get_stream_by_index(idx)

    Often you'd pass this along to a specific stream-reader,
     just as is done with to `pdbpy.streams.directorystreamStream`.

    Contains info about where it belongs within the parent `MultiStreamFile`.

    Behaves like a MemoryWrapper - Initializer pulls memoryviews of the entire stream
     and wraps it up like a good boy! This makes copies delegated until they are needed.
    """
    def __init__(self, parent : 'MultiStreamFile', page_list : Sequence[int], size_bytes : int, streamname : str, debug : bool = False):
        assert streamname not in parent.children, f"A stream called {streamname} is already registered in the parent MultiStreamFile"

        self.parent = parent
        self.page_list = page_list
        
        self.streamname = streamname
        parent.children[streamname] = self

        MemoryWrapper.__init__(self, sources = parent.map_pages(page_list))

class MultiStreamFile(BigHeader):
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
    
    Reading should likely be done through a `MultiStreamFileStream`-object instead instead.
    It wraps those page views in a MemoryWrapper object for easy access.
    """

    def __init__(self, file : IOBase):
        self.file = file
        self.mmap = mmap.mmap(file.fileno(), length = 0, access = mmap.ACCESS_READ)
        self.mem = memoryview(self.mmap)

        self.children : dict[str, MultiStreamFileStream] = dict()

        self.header = BigHeader.from_buffer_copy(self.mem)
        assert self.header.magic == b"Microsoft C/C++ MSF 7.00\r\n\x1a\x44\x53", f"Can only deal with 'big' header type and 'MSF 7.0' version, got {self.header.magic}"
        #print(f"page size: {self.header.page_size}")

        # Init fields in/from BigHeader
        for name, _ in self.header._fields_[1:]:
            setattr(self, name, getattr(self.header, name))

        # The directory may be fragmented into a number of pages scattered throughout the file.
        # How many pages do we need, to make an index of all those pages?
        directory_indices_count = self.pages_to_contain_bytes(self.directory_size_in_bytes)

        #print(f"Directory size: {self.directory_size_in_bytes}")
        #print(f"Directory indices count: {directory_indices_count}")

        # How many pages are needed to store the index above?
        # Every index is 4 bytes, so we need pages for index_length*4 bytes
        page_count_to_contain_directory_page_indices = self.pages_to_contain_bytes(4 * directory_indices_count)
        #print(f"Page count to contain directory page indices: {page_count_to_contain_directory_page_indices}")

        SizeOfBigHeader = ctypes.sizeof(BigHeader)
        list_of_pages_that_contain_directory_indices = (uint32_t * page_count_to_contain_directory_page_indices).from_buffer_copy(self.mem, SizeOfBigHeader)[:]
        #print(f"Page numbers that contain directory indices: {list(list_of_pages_that_contain_directory_indices)}")

        # Read all pages with directory indices
        directory_page_indices_data = self.read_pages(list_of_pages_that_contain_directory_indices, byte_count = 4 * directory_indices_count)

        directory_page_indices = (uint32_t * directory_indices_count).from_buffer_copy(directory_page_indices_data)
        #print(f"Directory page indices: {list(directory_page_indices)}")

        self.pdb_root_stream_pages = list(directory_page_indices)

        ############# READING ROOT PDB STREAM (it seeds .children)
        MultiStreamFileStream(parent=self, page_list = self.pdb_root_stream_pages, size_bytes = self.directory_size_in_bytes, streamname="Directory")
        

    def __repr__(self):
        return str(self.__dict__)


    def map_pages(self, page_list : Sequence[int], *, byte_offset : int = 0, byte_count : Optional[int]=None, debug : bool=False) -> Sequence[memoryview]:
        """
        Returns a list of memory-subviews that represent the area requested.
        Join yourself or use `read_pages` to get a corresponding contiguous bytes-object.
        """

        page_size = self.page_size

        start_page = byte_offset // page_size
        byte_offset = byte_offset % page_size


        pages_to_read = page_list[start_page:]

        # TODO: Massage pages_to_read to be a zip of (page_start, page_size) to merge continuous page numbers


        if byte_count is None:
            bytes_left = len(pages_to_read) * page_size - byte_offset 
        else:
            end_page = (byte_offset + byte_count) // page_size
            if start_page == end_page:
                start = page_list[start_page] * page_size + byte_offset
                return (self.mem[start : start + byte_count],)
            bytes_left = byte_count

        areas : List[memoryview] = []
        page_list_iter = iter(pages_to_read)

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

    def read_pages(self, page_list: Sequence[int], * , byte_offset : int = 0, byte_count : Optional[int]=None) -> bytes :
        """
        Returns a copied byte-object containing the desired data.
        """

        return b''.join(self.map_pages(page_list, byte_offset = byte_offset, byte_count = byte_count))

    def pages_to_contain_bytes(self, byte_count : int) -> int:
        """
        How many pages do we need to contain byte_count
        """
        page_size = self.page_size
        return (byte_count + page_size - 1 ) // page_size
    
    def get(self, streamname : str) -> MultiStreamFileStream:
        stream = self.children.get(streamname, None)
        if stream is None:
            raise ValueError(f"No stream named {streamname} available")
        return stream
