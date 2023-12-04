from pdbpy.msf import MultiStreamFileStream
from pdbpy.streams.typing import type_index
import pdbpy.utils.hash

from typing import List, Iterable, Tuple

from .records.base import PackedStructy
from .records.codeviewrecordheader import CodeViewRecordHeader

from ctypes import sizeof as c_sizeof
from dtypes.structify import Structy, structify
from dtypes.typedefs import uint32_t, int32_t, uint16_t
import struct

from .parse import parse_record


@structify
class OffsetSizePair(Structy):
    offset     : int32_t
    byte_count : int32_t

@structify
class PDBTypeStreamHeader(Structy):
    version                 : uint32_t
    header_size_bytes       : int32_t
    ti_min                  : uint32_t # ti is type index?
    ti_max                  : uint32_t
    records_byte_count      : uint32_t
    hash_stream_number      : uint16_t
    aux_hash_stream_num     : uint16_t # ignore yolo
    hash_key_size_bytes     : int32_t
    buckets                 : uint32_t
    hash_value_buffer       : OffsetSizePair
    index_offset_buffer     : OffsetSizePair
    hash_adjustment_buffer  : OffsetSizePair

@structify
class TypeIndexOffset(Structy):
    ti          : type_index
    byte_offset : uint32_t

assert c_sizeof(TypeIndexOffset) == 8


class PdbTypeStream:
    def __init__(self, file: MultiStreamFileStream, stream_directory : 'StreamDirectoryStream',  lookup_skip = 10, upfront_memory = False, debug=False):
        """
        lookup_skip sets the "skip" value when adding offsets to the speedreader-cache;
         Every `lookup_skip` pairs of (type_index, stream_offset) is added to a cache.
        """
        self.file = file
        self.stream_directory = stream_directory

        if upfront_memory:
            self.file = bytes(file)

        header = PDBTypeStreamHeader.from_buffer_copy(self.file[:c_sizeof(PDBTypeStreamHeader)])

        self.header = header
        self.num_types = header.ti_max - header.ti_min

        self.lookup_skip = lookup_skip
        self.lookup = []

        self.debug = debug


        assert header.hash_key_size_bytes == 4, f"Can't deal with non-4-byte hash indices (got {header.hash_key_size_bytes} !)"
        assert header.hash_value_buffer.byte_count / header.hash_key_size_bytes in (self.num_types, 0), "yeet"
        assert header.hash_adjustment_buffer.byte_count == 0, "cant deal with this yet"

        header.index_offset_buffer.byte_count

        #print("Loading hash")
        #import time
        #s = time.perf_counter()
        self.hash_stream = stream_directory.get_stream_by_index(self.header.hash_stream_number)
        
        hash_data = bytes(self.hash_stream[header.hash_value_buffer.offset : header.hash_value_buffer.offset + header.hash_value_buffer.byte_count])
        self.hash = [[] for _ in range(self.header.buckets)]

        idx = header.ti_min
        for (hashy,) in struct.iter_unpack("<I", hash_data):
            self.hash[hashy].append(idx)
            idx+=1
        
        #print("b", self.header.buckets)
        #print("Loading hash completed after (s): ", time.perf_counter()-s)


        if debug:
            for stream_offset, info in take(3, self.iter_ti_headers(self.header.ti_min)):
                print(f"{stream_offset} - {info}")

        #i = self.header.ti_min
        ##i = 0x6c7eb
        #for stream_offset, info in take('all', self.iter_ti_headers(i)):
        #    print(f"Type index: {i:x} of {self.header.ti_max:x}")
        #    i+=1
        #    parse_record(self.file, stream_offset+2, record_type=info.record_type, record_size_bytes = info.size_bytes, debug=debug)
        #    print()

    def get_hash_for_ti(self, ti : type_index):
        """
        Reads the hash from the hash stream.
        The hash is the "bucket modulo limited" hash as written into the stream.
        """
        offset = self.header.hash_value_buffer.offset
        # 4 == see assert in __init__
        offset += (ti - self.header.ti_min) * 4
        return struct.unpack("<I", self.hash_stream[offset : offset + 4])[0]
    
    def get_ti_for_string_by_hash(self, string : str) -> List[type_index]:
        """
        Given a string as a name, determine which hash-bucket the name fits in,
         and return a list of type_index that _might_ match the string.
        """
        hashy = pdbpy.utils.hash.get_hash_for_string(string)
        bucket = hashy % self.header.buckets
        return self.hash[bucket]
    
    def get_ti_and_record_for_name(self, /, name : str) -> Iterable[Tuple[type_index, PackedStructy]]:
        """
        Iterates the list of potential TIs in the same bucket as the name.
        If records are found matching the given name, the TI and record are yielded
        """
        potential_ti = self.get_ti_for_string_by_hash(name)
        for ti in potential_ti:
            record = self.get_by_type_index(ti)
            if getattr(record, 'name', None) == name:
                yield (ti, record)

        
    
    def get_structy_by_name(self, /, name : str, skip_forward = True) -> 'tuple[type_index, structyboi]':
        #print(f"Searching for {name} / {unique_name}")

        hashy = pdbpy.utils.hash.get_hash_for_string(name)
        bucket = hashy % self.header.buckets
        for ti in self.hash[bucket]:
            record = self.get_by_type_index(ti)
            if record is None or record.record_type not in structy_types:
                continue
            if name == getattr(record, 'name', None):
                return ti, record
        assert False, f"yolo? couldn't find {name} 🤔"

        assert name is not None or unique_name is not None, "Need at least a name of any kind!!"
        for stream_offset, info in self.iter_ti_headers():
            if info.record_type in structy_types:
                _, typ = parse_record(self.file, stream_offset+2, record_type=info.record_type, record_size_bytes = info.size_bytes)
                if name is not None and name != typ.name: continue
                if unique_name is not None and unique_name != typ.unique_name: continue

                if skip_forward and typ.properties.is_forward_definition:
                    continue
                #print("gottem")
                return info.ti, typ
    
    def get_by_type_index(self, ti : type_index):
        stream_offset, info = self.get_ti_info(ti)
        _, typ = parse_record(self.file, stream_offset+2, record_type=info.record_type, record_size_bytes = info.size_bytes)
        return typ

    
    def get_ti_info(self, TI : type_index):
        return next(self.iter_ti_headers(start_ti = TI))
    
    def get_closest_start_pos_for_ti(self, ti) -> 'tuple[type_index_zero_based, int]':
        """
        Returns the closest stored lookup position for a given type_index.

        Returns a (idx, stream_byte_offset) with the `idx` as 0-start, not a type_index
        """
        assert ti >= self.header.ti_min, f"{ti} >= {self.header.ti_min}"
        assert ti < self.header.ti_max, f"{ti} < {self.header.ti_max}"


        ratio = (ti - self.header.ti_min) / (self.num_types)

        io_sizeof = c_sizeof(TypeIndexOffset)
        io_size = self.header.index_offset_buffer.byte_count        
        io_count = io_size / io_sizeof

        guess_index = io_count * ratio
        guess_index = int(guess_index) # // 1 # stupid way to floor ¯\_(ツ)_/¯

        def get_io(idx):
            offset = self.header.index_offset_buffer.offset + io_sizeof * idx
            guess = TypeIndexOffset.from_buffer_copy(self.hash_stream[offset : offset + io_sizeof])
            return guess
        
        guess = get_io(guess_index)

        if guess_index != io_count-1 and guess_index != 0 and guess.ti != ti:
            if guess.ti < ti:
                # advance until not (limit || above)
                next_guess = guess
                while next_guess.ti < ti:
                    guess = next_guess
                    guess_index += 1                    
                    next_guess = get_io(guess_index)
            else:
                # retreat until 0 or below
                while guess.ti > ti:
                    guess_index -= 1
                    guess = get_io(guess_index)

        #print(f"Starting search at {guess}")
        return guess.ti - self.header.ti_min, guess.byte_offset + c_sizeof(PDBTypeStreamHeader)


    def iter_ti_headers(self, start_ti : type_index = None) -> tuple[int, CodeViewRecordHeader]:
        type_size = c_sizeof(CodeViewRecordHeader)
        extra_bytes_to_advance = CodeViewRecordHeader.size_bytes.size
        if start_ti is None:
            start_index = 0
            yield_start_index = 0
            pos = c_sizeof(PDBTypeStreamHeader)
        else:
            assert start_ti >= self.header.ti_min, f"{start_ti} >= {self.header.ti_min}"
            assert start_ti < self.header.ti_max,  f"{start_ti} < {self.header.ti_max}"
            yield_start_index = start_ti - self.header.ti_min
            start_index, pos = self.get_closest_start_pos_for_ti(start_ti)
            
        for idx in range(start_index, self.num_types):
            if idx % self.lookup_skip == 0:
                lookup_idx = idx // self.lookup_skip
                lookup = self.lookup
                if len(lookup) <= lookup_idx:
                    self.lookup.append(pos)
            _, info = CodeViewRecordHeader.from_memory(self.file, pos, type_size, debug=self.debug)
            info.ti = idx + self.header.ti_min
            if idx >= yield_start_index:
                yield pos, info
            pos += extra_bytes_to_advance + info.size_bytes

    #def __repr__(self):
    #    return str(self.__dict__)

    