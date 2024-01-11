
from typing import Any, Generator, List, Sequence, TypeVar

def chunk_slices(limit: int, chunksize: int) -> List[slice]:
    cnt = (limit+chunksize-1)//chunksize
    lst: List[slice]=[]
    for idx in range(0, cnt):
        lst.append(slice(idx*chunksize, (idx+1)*chunksize))
    return lst

def chunk[T: Any](something: T, chunksize: int) -> Generator[T, None, None]:
    """
    Provide a way to cut something like bytes, memoryview, or memorywrapper into equal-sized chunks.
    """
    for slice in chunk_slices(len(something), chunksize=chunksize):
        yield something[slice]
