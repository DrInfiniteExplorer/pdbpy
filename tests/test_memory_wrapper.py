



from pdbpy.utils.memorywrapper import MemoryWrapper


def test_wrapper():


    
    a = bytes([1,2,3])
    b = bytes([4,5,6])

    c = MemoryWrapper([a,b])

    assert memoryview(c[:]) == bytes([1,2,3,4,5,6])

    assert memoryview(c[0:1]) == bytes([1])
    assert memoryview(c[0:2]) == bytes([1,2])
    assert memoryview(c[0:3]) == bytes([1,2,3])
    assert memoryview(c[1:3]) == bytes([2,3])
    assert memoryview(c[2:3]) == bytes([3])

    assert memoryview(c[3:4]) == bytes([4])
    assert memoryview(c[3:5]) == bytes([4,5])
    assert memoryview(c[3:6]) == bytes([4,5,6])
    assert memoryview(c[4:6]) == bytes([5,6])
    assert memoryview(c[5:6]) == bytes([6])

    assert memoryview(c[1:]) == bytes([2,3,4,5,6])
    assert memoryview(c[:-1]) == bytes([1,2,3,4,5])

    import struct
    struct.unpack_from("c", c, offset=2)

