# pdbpy
A pure python implementation of Program Database file parsing

## Motivation

I want to be able to parse PDB files using python. I want to understand their structure.

There are other libraries and implementations (see below). This one differs in that it works
 out of the box, and it lazily loads only what is requested. Working with a file 1GB+ large
 and only want to know how to parse a single structure? Only want to know the address of a
 symbol? No problem, only the minumum will be loaded!

The PDB is memory-mapped. The underlying MSF format makes data possibly non-contiguous,
 but using the `memorywrapper` library that becomes (mostly) a non-issue, as it can
 provide a memoryview-like self-sliceable non-copying front for the data. Bytes
 are only copied when the view is accessed as a buffer. Unfortunately the data needs to
 be copied at that point, as the buffer protocol does not support wildly discontiguous
 memory areas.

### Features!
-------------

| Feature                                                   | pdbpy                     |
| :---                                                      | :---:                     |
| Can open PDB                                              |  ✅                      |
| Can find a given type by name                             |  ✅                      |
| Uses the _Hash Stream_ to accelerate type lookup by name? |  ✅                      |
| Can look up symbols given name?                           |  ✅ (from global table)  |
| Can look up symbols given addresses?                      |  ❌                      |

## Installation

`pip install pdbpy`


### Getting started
-------------------

From `test_symbol_address` in [test_windows_pdb.py](tests/test_windows_pdb.py)
```py
    pdb = PDB("example_pdbs/addr.pdb")
    addr = pdb.find_symbol_address("global_variable")
```

#### Explain the type hash stream
---------------------------------

The hash stream consists of two parts:
An ordered list of _truncated hashes_, and a list of of {TI, byteoffset} pairs to accelerate lookup.

The _truncated hashes_ are hashes of the TI records, modulo'ed by the _number of buckets_.
The number of buckets can be found in the header of the type stream.
This can be loaded into a `hash = Dict[TruncatedHash, List[TI]]`
Given the hash of a TI-record, we can find a list of potential TIs.

The second part of the hash stream accelerates this. It contains a list of monotonically increasing
 `Tuple[TI, ByteOffset]`-pairs. If we have a TI, we can find the offset of the closes preceeding TI
 and parse the TI-records from there until we find the exact one we want.

Combining the two functionalities offered by the hash stream, we thus find a list of potential TIs given
 a hash, and then use the second part to accelerate the lookup of the actual records, which we need
 to examine in order to determine if we found the TI matching the non-truncated hash.

The hash of TI-records is often the hash of the unique name (if there is one).
If there isn't any unique name, it's a hash of the bytes of entire record.
The functions used to compute the hashes are different for the unique name strings
 and for the bytes of the records.

##### Sources and references
* [volatility3](https://github.com/volatilityfoundation/volatility3) has some under `/volatility3/framework/symbols/windows/[pdb.json|pdbconv.py]`
    * At least in commit `8e420dec41861993f0cd2837721af2d3e7a6d07a`
* [radare2](https://github.com/radareorg/radare2)
* [microsoft-pdb](https://github.com/microsoft/microsoft-pdb/blob/805655a28bd8198004be2ac27e6e0290121a5e89/PDB/) but it's not really well explained
* [moyix/pdbparse](https://github.com/moyix/pdbparse) - Iconic python implementation
* [willglynn/pdb](https://github.com/willglynn/pdb) - Rust implementation of reader

* [Air14/SymbolicAccess](https://github.com/Air14/SymbolicAccess)
    * [https://github.com/Oxygen1a1/oxgenPdb](https://github.com/Oxygen1a1/oxgenPdb) derivative