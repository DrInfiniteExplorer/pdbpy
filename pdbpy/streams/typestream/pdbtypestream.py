from ctypes import sizeof as c_sizeof
from typing import Iterable, List, Tuple

from pdbpy.codeview.types import dynamic_type_index, type_index
from pdbpy.msf import MultiStreamFileStream
from pdbpy.streams.typestream.records.baseclass import BaseClass
from pdbpy.streams.typestream.records.pdbtypehashstream import PdbTypeHashStream
from pdbpy.streams.typestream.typestreamheader import PDBTypeStreamHeader

from .parse import parse_record
from .records.base import PackedStructy
from .records.codeviewrecordheader import CodeViewRecordHeader


class PdbTypeStream:
    file: MultiStreamFileStream | bytes
    debug: bool

    hash_stream: PdbTypeHashStream | None

    header: PDBTypeStreamHeader
    num_types: int

    # These two are intended to be populated as types are iterated and found,
    #  like a dynamic version of the second part of the hash stream.
    # Not fully implemented yet.
    lookup: List[int]
    lookup_skip: int

    def __init__(
        self,
        file: MultiStreamFileStream,
        lookup_skip: int = 10,
        upfront_memory: bool = False,
        debug: bool = False,
    ):
        """
        lookup_skip sets the "skip" value when adding offsets to the speedreader-cache;
         Every `lookup_skip` pairs of (type_index, stream_offset) is added to a cache.
        """
        self.file = file
        self.debug = debug

        self.hash_stream = None

        if upfront_memory:
            self.file = bytes(file)

        header = PDBTypeStreamHeader.from_buffer_copy(self.file[: c_sizeof(PDBTypeStreamHeader)])

        self.header = header
        self.num_types = header.ti_max - header.ti_min  # type: ignore

        self.lookup_skip = lookup_skip
        self.lookup = []

        assert (
            header.hash_key_size_bytes == 4
        ), f"Can't deal with non-4-byte hash indices (got {header.hash_key_size_bytes} !)"
        assert header.hash_value_buffer.byte_count / header.hash_key_size_bytes in (  # type: ignore
            self.num_types,
            0,
        ), "yeet"
        assert header.hash_adjustment_buffer.byte_count == 0, "cant deal with this yet"

        header.index_offset_buffer.byte_count

        # hash_stream = stream_directory.get_stream_by_index(self.header.hash_stream_number)
        # PdbTypeHashStream(
        #   hash_stream,
        #   start_ti=header.ti_min,
        #   hash_start = header.hash_value_buffer,
        #   index_start = header.index_offset_buffer,
        #   hash_buckets=header.buckets.value,
        # )

    def set_hash_stream(self, stream: PdbTypeHashStream) -> None:
        self.hash_stream = stream

    def get_ti_and_record_for_name(self, /, name: str) -> Iterable[Tuple[type_index, PackedStructy]]:
        """
        Iterates the list of potential TIs in the same bucket as the name.
        If records are found matching the given name, the TI and record are yielded
        """
        assert self.hash_stream

        potential_ti = self.hash_stream.get_possible_ti_for_string_by_hash(name)
        for ti in potential_ti:
            record = self.get_by_type_index(ti)
            if getattr(record, "name", None) == name:
                yield (ti, record)

    def get_structy_by_name(self, /, name: str, skip_forward: bool = True) -> Tuple[type_index, BaseClass]:
        assert self.hash_stream

        potential_ti = self.hash_stream.get_possible_ti_for_string_by_hash(name)
        for ti in potential_ti:
            record = self.get_by_type_index(ti)
            if record is None or record.record_type not in structy_types:
                continue
            if name == getattr(record, "name", None):
                return ti, record
        assert False, f"yolo? couldn't find {name} 🤔"

        assert name is not None or unique_name is not None, "Need at least a name of any kind!!"
        for stream_offset, info in self.iter_ti_headers():
            if info.record_type in structy_types:
                _, typ = parse_record(
                    self.file, stream_offset + 2, record_type=info.record_type, record_size_bytes=info.size_bytes
                )
                if name is not None and name != typ.name:
                    continue
                if unique_name is not None and unique_name != typ.unique_name:
                    continue

                if skip_forward and typ.properties.is_forward_definition:
                    continue
                # print("gottem")
                return info.ti, typ

    def get_by_type_index(self, ti: type_index):
        stream_offset, info = self.get_ti_info(ti)
        _, typ = parse_record(
            self.file, stream_offset + 2, record_type=info.record_type, record_size_bytes=info.size_bytes
        )
        return typ

    def get_ti_info(self, TI: type_index):
        return next(self.iter_ti_headers(start_ti=TI))

    def dynamic_to_absolute(self, dynamic_index: dynamic_type_index) -> type_index:
        return dynamic_index + self.header.ti_min  # type: ignore

    def absolute_to_dynamic(self, absolute_index: type_index) -> dynamic_type_index:
        return absolute_index - self.header.ti_min  # type: ignore

    def get_closest_start_pos_for_ti(self, ti: type_index) -> tuple[dynamic_type_index, int]:
        assert self.hash_stream

        ti, offset = self.hash_stream.get_closest_start_pos_for_ti(ti)
        dynamic_index = self.absolute_to_dynamic(ti)
        return dynamic_index, offset + c_sizeof(PDBTypeStreamHeader)

    def iter_ti_headers(self, start_ti: type_index = None) -> tuple[int, CodeViewRecordHeader]:
        type_size = c_sizeof(CodeViewRecordHeader)
        extra_bytes_to_advance = CodeViewRecordHeader.size_bytes.size
        if start_ti is None:
            start_index = 0
            yield_start_index = 0
            pos = c_sizeof(PDBTypeStreamHeader)
        else:
            assert start_ti >= self.header.ti_min, f"{start_ti} >= {self.header.ti_min}"
            assert start_ti < self.header.ti_max, f"{start_ti} < {self.header.ti_max}"
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

    # def __repr__(self):
    #    return str(self.__dict__)
