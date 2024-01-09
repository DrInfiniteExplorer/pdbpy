

import struct
import pytest
from pdbpy.utils.memorywrapper import MemoryWrapper

@pytest.fixture
def bytes123() -> bytes:
    return bytes([1,2,3])

@pytest.fixture
def bytes456() -> bytes:
    return bytes([4,5,6])

@pytest.fixture
def wrapper_123_456(bytes123 : bytes, bytes456 : bytes) -> MemoryWrapper:
    return MemoryWrapper([bytes123, bytes456])

def test_wrapper_full_range(wrapper_123_456 : MemoryWrapper):
    assert memoryview(wrapper_123_456) == bytes([1,2,3,4,5,6])
    assert memoryview(wrapper_123_456[:]) == bytes([1,2,3,4,5,6])

def test_wrapper_first_part_subaccess(wrapper_123_456 : MemoryWrapper):
    assert memoryview(wrapper_123_456[0:1]) == bytes([1])
    assert memoryview(wrapper_123_456[0:2]) == bytes([1,2])
    assert memoryview(wrapper_123_456[0:3]) == bytes([1,2,3])
    assert memoryview(wrapper_123_456[1:3]) == bytes([2,3])
    assert memoryview(wrapper_123_456[2:3]) == bytes([3])

def test_wrapper_second_part_subaccess(wrapper_123_456 : MemoryWrapper):
    assert memoryview(wrapper_123_456[3:4]) == bytes([4])
    assert memoryview(wrapper_123_456[3:5]) == bytes([4,5])
    assert memoryview(wrapper_123_456[3:6]) == bytes([4,5,6])
    assert memoryview(wrapper_123_456[4:6]) == bytes([5,6])
    assert memoryview(wrapper_123_456[5:6]) == bytes([6])

def test_wrapper_skip_edges(wrapper_123_456 : MemoryWrapper):
    assert memoryview(wrapper_123_456[1:]) == bytes([2,3,4,5,6])
    assert memoryview(wrapper_123_456[:-1]) == bytes([1,2,3,4,5])

def test_wrapper_struct_unpack_subaccess(wrapper_123_456 : MemoryWrapper, monkeypatch : pytest.MonkeyPatch):
    """
    Regardless of where or how much is requested, `struct.unpack` will ask that the entire buffer be created :(
    """
    with monkeypatch.context():
        length = None
        def observe(flags : int, buffer : memoryview):
            nonlocal length
            length = len(buffer)
        
        monkeypatch.setattr(wrapper_123_456, '_test_observe', observe)
        assert struct.unpack_from("c", wrapper_123_456, offset=2) == (b'\x03',)

        assert length == len(wrapper_123_456)

