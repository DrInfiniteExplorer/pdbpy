import struct
from collections import defaultdict
from ctypes import sizeof as c_sizeof
from typing import TypeAlias

from dtypes.structify import Structy, structify
from dtypes.typedefs import uint32_t
from memorywrapper import MemoryWrapper

from pdbpy.codeview.types import dynamic_type_index, type_index
from pdbpy.msf import MultiStreamFileStream
from pdbpy.streams.typestream.typestreamheader import PDBTypeStreamHeader
from pdbpy.utils.hash import Hash, get_hash_for_string

TruncatedHash: TypeAlias = int


@structify
class TypeIndexOffset(Structy):
    ti: type_index
    byte_offset: uint32_t


assert c_sizeof(TypeIndexOffset) == 8


class PdbTypeHashStream:
    file: MultiStreamFileStream | bytes
    debug: bool

    hash_memory: MemoryWrapper | bytes
    index_memory: MemoryWrapper | bytes

    hash: dict[TruncatedHash, list[type_index]]

    start_ti: type_index
    num_types: int
    buckets: int

    def __init__(
        self,
        file: MultiStreamFileStream,
        type_header: PDBTypeStreamHeader,
        upfront_memory: bool = False,
        debug: bool = False,
    ):
        self.file = file
        self.debug = debug
        if upfront_memory:
            self.file = bytes(file)

        hash_start = type_header.hash_value_buffer
        self.hash_memory = self.file[hash_start.offset : hash_start.offset + hash_start.byte_count]  # type: ignore
        index_start = type_header.index_offset_buffer
        self.index_memory = self.file[index_start.offset : index_start.offset + index_start.byte_count]  # type: ignore

        self.hash = defaultdict(list)  # [[] for _ in range(self.header.buckets)]
        self.start_ti = type_header.ti_min
        self.num_types = int(hash_start.byte_count) // 4
        self.buckets = int(type_header.buckets)

        ti = self.start_ti
        trunc_hash: TruncatedHash
        for (trunc_hash,) in struct.iter_unpack("<I", self.hash_memory):
            self.hash[trunc_hash].append(ti)
            ti += 1

    def truncate_hash(self, hash: Hash) -> TruncatedHash:
        return hash % self.buckets

    def get_hash_for_ti(self, ti: type_index):
        """
        Reads the hash from the hash stream.
        The hash is the "bucket modulo limited" hash as written into the stream.
        """
        # 4 == see assert in __init__
        dynamic_index: dynamic_type_index = dynamic_type_index(ti - self.start_ti)  # type: ignore
        offset: int = dynamic_index.value * 4
        return struct.unpack("<I", self.hash_memory[offset : offset + 4])[0]

    def get_possible_ti_for_string_by_hash(self, string: str) -> list[type_index]:
        """
        Given a string as a name, determine which hash-bucket the name fits in,
         and return a list of type_index that _might_ match the string.
        """
        hash: Hash = get_hash_for_string(string)
        truncated = self.truncate_hash(hash)
        return self.hash[truncated]

    def get_index_offset(self, idx: dynamic_type_index) -> TypeIndexOffset:
        io_sizeof = c_sizeof(TypeIndexOffset)
        offset = io_sizeof * idx.value
        return TypeIndexOffset.from_buffer_copy(self.index_memory[offset : offset + io_sizeof])

    def get_closest_start_pos_for_ti(self, ti: type_index) -> tuple[type_index, int]:
        """
        Returns the closest stored lookup position for a given type_index.

        Returns a (idx, stream_byte_offset) with the `idx` as 0-start, not a type_index
        """

        assert ti >= self.start_ti, f"{ti} >= {self.start_ti}"  # type: ignore

        ratio = float(ti - self.start_ti) / self.num_types  # type: ignore

        io_sizeof = c_sizeof(TypeIndexOffset)
        io_size = len(self.index_memory)
        io_count = io_size // io_sizeof

        guess_index = io_count * ratio
        guess_index = dynamic_type_index(int(guess_index))  # Passing through int to floor the value.
        last_dynamic_ti = dynamic_type_index(io_count - 1)

        guess = self.get_index_offset(guess_index)

        if guess_index.value == last_dynamic_ti:
            return guess.ti, guess.byte_offset.value

        if guess_index.value == 0:
            return guess.ti, guess.byte_offset

        if guess.ti == ti:
            return guess.ti, guess.byte_offset

        if guess.ti.value < ti.value:
            # advance until not (limit || above)
            next_guess = guess
            while next_guess.ti.value < ti.value:
                guess = next_guess
                guess_index.value += 1
                next_guess = self.get_index_offset(guess_index)
        else:
            # retreat until 0 or below
            while guess.ti.value > ti.value:
                guess_index.value -= 1
                guess = self.get_index_offset(guess_index)

        # print(f"Starting search at {guess}")
        return guess.ti, guess.byte_offset.value
