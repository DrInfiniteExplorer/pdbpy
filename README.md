# pdbpy
A pure python implementation of Program Database file parsing

OK so lets start with adding some notes and references and stuff.

#### Notes and references and stuff
-----------------------------------

Over at [my blog](https://blog.luben.se/debugsymbols.html) I have some raw notes and links that might or might not be of interest.



### Getting started
-------------------

**In the future** just do `pip install pdbpy` and be happy!


<examples n shit>


### Features!
-------------

| Feature                                                   | pdbpy |
| :---                                                      | :---: |
| Can open PDB                                              |  ✅  |
| Can find a given type by name                             |  ✅  |
| Uses the _Hash Stream_ to accelerate type lookup by name? |  ✅  |
| Can look up symbols?                                      |  ❌  |
| Can look up addresses?                                    |  ❌  |




#### Explain the type hash stream
---------------------------------

The type hash stream contains a list.
The list is (#types) long.
The entries in the list correspond to the **truncated** hash of the corresponding type entry.

For most type entries, the hash for the type-entry is the hash of the not-unique name.
For other entries, it's _another_ hash if the binary data involved in the type entry.

The stored hashes are **truncated** by applying a modulo operation.
It is modulo'ed with the _number of hash buckets_. The number of buckets is specified in the type stream header.

Since what is stored in the hash-stream is the hash, and it is implicitly associated with the (zero based) type index, we can
 easily obtain the truncated hash for a given type index.

But if we want to go from truncated hash to type index, we need to parse the hash stream and build a reverse-map.

Since multiple hashes can be truncated into the same value when applying the modulo operation, the map goes from a key(truncated hash) to a list of potential type indices.

`Dict[TruncatedHash, List[ZeroBasedTypeIndex]]`

We need to examine each type index in the list to find the correct one.


