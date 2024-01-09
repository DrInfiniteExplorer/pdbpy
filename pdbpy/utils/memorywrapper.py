

from typing import List, Optional, Sequence, Union, overload

def _test_observe_dummy(flags: int, buffer: memoryview):
    ...

class MemoryWrapper():
    def __init__(self, sources : Sequence[Union[bytes, memoryview]], length : Optional[int] = None):
        self.memorywrapper_sources : Sequence[memoryview] = list(map(memoryview, sources))
        self.memorywrapper_copied : Optional[bytes] = None
        self.memorywrapper_length = length or sum(map(len, self.memorywrapper_sources))
        self._test_observe = _test_observe_dummy
    
    def __len__(self):
        return self.memorywrapper_length
    
    def __buffer__(self, flags : int):
        ret = None
        if len(self.memorywrapper_sources) == 1:
            ret = memoryview(self.memorywrapper_sources[0])
        else:
            if self.memorywrapper_copied is None:
                self.memorywrapper_copied = b''.join(self.memorywrapper_sources)
            ret = memoryview(self.memorywrapper_copied)
        self._test_observe(flags, ret)
        return ret

    @overload
    def __getitem__(self, key : int) -> int:
        ...
    
    @overload
    def __getitem__(self, key : slice) -> 'MemoryWrapper':
        ...

    def __getitem__(self, key : Union[slice, int]) -> Union[int, 'MemoryWrapper']:
        if isinstance(key, int):
            if key >= self.memorywrapper_length:
                raise ValueError(f"Bad index {key} out of {self.memorywrapper_length}")
            if self.memorywrapper_copied:
                return self.memorywrapper_copied[key]
            cur = 0
            for source in self.memorywrapper_sources:
                idx = key + self.memorywrapper_length if key < 0 else key
                length = len(source)
                end = cur + length
                if idx < end:
                    return source[idx-cur]
                cur = end
            raise ValueError("End of the line")

        if self.memorywrapper_copied:
            return MemoryWrapper((self.memorywrapper_copied[key],))

        start, stop = key.start, key.stop
        if start is None and stop is None:
            return MemoryWrapper(self.memorywrapper_sources, self.memorywrapper_length)
        if start is None:
            start = 0
        if start > self.memorywrapper_length:
            raise ValueError(f"Bad index {key} out of {self.memorywrapper_length}")
        if stop is None:
            stop = self.memorywrapper_length
        if stop < 0:
            stop = stop + self.memorywrapper_length

        current_idx = 0
        sublist : List[memoryview] =[]
        to_eat = stop-start
        for source in self.memorywrapper_sources:
            current_len = len(source)
            current_end = current_idx + current_len

            sub_list_start = max(start - current_idx, 0)
            current_idx = current_end
            if sub_list_start > current_len:
                continue
            
            eat = min(to_eat, current_len)
            if eat < 0:
                break

            view = memoryview(source)
            view = view[sub_list_start:sub_list_start+eat]
            to_eat -= len(view)
            sublist.append(view)

        return MemoryWrapper(sublist, length=stop-start)
