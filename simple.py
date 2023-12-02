
from pdbpy.msf import MultiStreamFile
from pdbpy.streams.directorystream import StreamDirectoryStream
from pdbpy.streams.pdbinfo import PdbInfoStream
import pdbpy.streams.typestream
import pdbpy.streams.typestream.leaf_enum as leafs


from dtypes.typedefs import (
    int8_t,  int16_t,  int32_t,  int64_t,
    uint8_t, uint16_t, uint32_t, uint64_t,
    float32_t, float64_t)


class Member(object):
    def __init__(self, parent, cache, definition: pdbpy.streams.typestream.Member):
        self.parent = parent
        self.cache = cache
        self.definition = definition
        self.ti         = definition.field_type
        self.name       = definition.name
        self.static     = definition.static
        self.offset     = -1 if self.static else definition.offset

        attr = definition.field_attributes
        self.access = attr.access

        self.resolved = None
    
    def get_type(self):
        if self.resolved is None:
            self.resolved = self.cache.resolve_id(self.ti)
        return self.resolved
    
    def __str__(self):
        try:
            return f"@{self.offset} {self.access.name} {self.get_type()} {self.name} from {self.parent.name}"
        except Exception as e:
            print(f"ERROR RESOLVING TYPE OF {self.name}")
            raise e




class Typ(object):
    def __init__(self, structy : pdbpy.streams.typestream.TypeStructLike, cache : 'ResolveCache'):
        self.structy = structy
        self.cache = cache

        self.name = structy.name
        self.raw_fields = cache.resolve_id(structy.fields).members
        self.members = [Member(self, cache, member) for member in self.raw_fields if isinstance(member, pdbpy.streams.typestream.Member)]
        self._parents = None
    
    @property
    def parents(self):
        if self._parents is None:
            self._parents = [self.cache.resolve_id(field.index) for field in self.raw_fields if isinstance(field, pdbpy.streams.typestream.BaseClass)]
        return self._parents
    
    def iter_members(self, from_parents=False):
        if from_parents:
            for parent in self.parents:
                yield from parent.iter_members(from_parents=True) # idk mb ¯\_(ツ)_/¯
        yield from self.members

    def get_members(self, from_parents=False):
        return list(self.iter_members(from_parents=from_parents))
    
    def get_methods(self):
        ...
    
    def get_parents(self):
        ...
    
    def __str__(self):
        return f"struct {self.name}"

class Enum(object):
    def __init__(self, definition: pdbpy.streams.typestream.Enum, cache : 'ResolveCache'):
        self.definition = definition
        self.cache = cache        
        self.resolved = None
        members = cache.resolve_id(self.definition.fields).members
        self.members = [(e.name, e.value) for e in members]
    
    @property
    def underlying_type(self):
        if self.resolved is None:
            self.resolved = self.cache.resolve_id(self.definition.underlying_type)
        return self.resolved
    
    def __str__(self):
        return f"enum {self.definition.name} : {self.underlying_type}"
        return f"{self.definition.name}(" + ",".join(f"{name}={val}" for name, val in self.members) + ")"

class Pointer(object):
    def __init__(self, definition: pdbpy.streams.typestream.Enum, cache : 'ResolveCache'):
        self.definition = definition
        self.cache = cache        
        self.resolved = None
    
    @property
    def reference_type(self):
        if self.resolved is None:
            self.resolved = self.cache.resolve_id(self.definition.reference_type)
        return self.resolved
    
    def __str__(self):
        return f"PTR({self.reference_type})"

class Array(object):
    def __init__(self, definition: pdbpy.streams.typestream.Array, cache : 'ResolveCache'):
        self.definition = definition
        self.cache = cache        
        self.resolved = None
    
    @property
    def reference_type(self):
        if self.resolved is None:
            self.resolved = self.cache.resolve_id(self.definition.element_type)
        return self.resolved
    
    def __str__(self):
        return f"ARRAY({self.reference_type})"


def wrap(raw, cache):
    if raw is None: return None
    match type(raw):
        case pdbpy.streams.typestream.TypeStructLike:
            return Typ(raw, cache)
        case pdbpy.streams.typestream.FieldList:
            return raw
        case pdbpy.streams.typestream.Bitfield:
            return raw
        case pdbpy.streams.typestream.Enum:
            return Enum(raw, cache)
        case pdbpy.streams.typestream.Pointer:
            return Pointer(raw, cache)
        case pdbpy.streams.typestream.Modifier:
            return cache.resolve_id(raw.reference)
        case pdbpy.streams.typestream.Array:
            return Array(raw, cache)
        
            

    
    assert False, f"yo boi dont be here go away we don't take kindly to people of your kind around here! {type(raw)}"


class ResolveCache(object):

    class Primitive(object):
        def __init__(self, ctype):
            self.ctype = ctype
        
        def __str__(self):
            return str(self.ctype)

    def __init__(self, type_stream : pdbpy.streams.typestream.PdbTypeStream):
        self.type_stream = type_stream
        self.cache = dict()

        def MakePrimitive(ctype, *matches):
            primitive = self.Primitive(ctype)
            for match in matches:
                for modifier in leafs.BasicTypeModifier:
                    combined = modifier << 8 | match
                    self.cache[combined] = primitive
                    #print(f"0x{combined:04x} = {primitive.ctype}")

        b = leafs.BasicTypeEnum
        MakePrimitive(int8_t,  b.SignedCharacter,   b.NarrowCharacter, b.SByte, b.Character8)
        MakePrimitive(uint8_t, b.Boolean8, b.UnsignedCharacter, b.Byte)

        MakePrimitive(int16_t,  b.WideCharacter, b.Character16, b.Int16Short, b.Int16)
        MakePrimitive(uint16_t, b.Boolean16, b.UInt16Short, b.UInt16)

        MakePrimitive(int32_t,  b.Character32, b.Int32Long, b.Int32)
        MakePrimitive(uint32_t, b.Boolean32, b.UInt32Long, b.UInt32)

        MakePrimitive(int64_t,  b.Int64Quad, b.Int64)
        MakePrimitive(uint64_t, b.Boolean64, b.UInt64Quad, b.UInt64)

        # lets give up on 128 bits for now ok good!

        MakePrimitive(float32_t, b.Float32)
        MakePrimitive(float64_t, b.Float64)


    def resolve_id(self, ti : pdbpy.streams.typestream.type_index):
        #if ti < self.type_stream.header.ti_min:
        #    primitive = PrimitiveMap.get(ti, None)
        #    assert primitive is not None, "Yo boi {ti} is unknown territorty"
        #    return primitive

        cached = self.cache.get(ti, None)
        if cached is not None:
            return cached
                
        typ = self.type_stream.get_by_type_index(ti)
        if isinstance(typ, pdbpy.streams.typestream.TypeStructLike):
            if typ.properties.is_forward_definition:
                real_ti, real_typ = self.type_stream.get_structy_by_name(name = typ.name)
                wrappy = self.cache.get(real_ti, None)
                if wrappy is None:
                    wrappy = wrap(real_typ, self)
                    self.cache[real_ti] = wrappy
        else:
            wrappy = wrap(typ, self)
        
        self.cache[ti] = wrappy
        return wrappy

    def resolve_name(self, name : str):
        ti, typ = self.type_stream.get_structy_by_name(name)
        assert ti not in self.cache
        wrappy = wrap(typ, self)
        self.cache[ti] = wrappy
        return wrappy


class Pdb(object):

    def __init__(self, file):
        self.msf = MultiStreamFile(file)
        self.directory = StreamDirectoryStream(self.msf.get("Directory"))
        type_info = self.directory.get_stream_by_index(2)
        self.type_stream = pdbpy.streams.typestream.PdbTypeStream(type_info, self.directory)

        self.cache = ResolveCache(self.type_stream)
    
    def get_type(self, name : str):
        return self.cache.resolve_name(name)


def main():
    import sys
    assert len(sys.argv) == 2, "Accepts only a path to a pdb as argument."
    with open(sys.argv[1], "rb") as f:

        pdb = Pdb(f)
        actor = pdb.get_type("AActor")
        print(actor.parents)

        resolving = []
        def recursePrint(typ, indent=1):
            if typ in resolving:
                print(" " * indent, "<resolving recursively!>")
                return
            resolving.append(typ)
            for member in typ.get_members(from_parents=True):
                desc = str(member)
                print(" " * indent, desc)
                member_type = member.get_type()
                if isinstance(member_type, Typ):
                    recursePrint(member_type, indent+2)
            #resolving.remove(typ)
        recursePrint(actor, 0)
        print(actor.parents[0].parents[0].name)
        #for f in actor.raw_fields:
        #    print(f)


if __name__ == '__main__':
    main()

