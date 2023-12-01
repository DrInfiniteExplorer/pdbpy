import pytest

import pdbpy
from pdbpy.msf import MultiStreamFile
from pdbpy.streams.streamdirectory import StreamDirectoryStream
from pdbpy.streams.pdbinfo import PdbInfoStream
from pdbpy.streams.pdbtype import PdbTypeStream
import pdbpy.utils.hash

from pdbpy.streams.pdbtype.records import TypeStructLike, FieldList, Member

from pdbpy.streams.pdbtype.records.base import TypeProperties

from pdbpy.primitivetypes import BasicTypeEnum, BasicTypeModifier, BasicTypeInfo


@pytest.fixture
def setup_windows_pdb() -> MultiStreamFile:
    with open("example_pdbs/windows.pdb", "rb") as f:
        msf = MultiStreamFile(f)
        return msf

@pytest.fixture
def setup_directory_stream(setup_windows_pdb : MultiStreamFile) -> StreamDirectoryStream:
    stream = setup_windows_pdb.get("Directory")
    return StreamDirectoryStream(stream)

@pytest.fixture
def setup_info_stream(setup_windows_pdb, setup_directory_stream : StreamDirectoryStream) -> PdbInfoStream:
    pdb_info_file = setup_directory_stream.get_stream_by_index(1)
    assert pdb_info_file is not None
    info_stream = PdbInfoStream(pdb_info_file)
    return info_stream

@pytest.fixture
def setup_type_stream(setup_directory_stream : StreamDirectoryStream) -> PdbTypeStream:
    type_info_file = setup_directory_stream.get_stream_by_index(2)
    assert type_info_file is not None
    type_stream = PdbTypeStream(type_info_file, setup_directory_stream, upfront_memory=False)
    return type_stream

def test_can_open(setup_windows_pdb : MultiStreamFile):
    assert setup_windows_pdb is not None

def test_directory_exists(setup_directory_stream : StreamDirectoryStream):
    assert setup_directory_stream is not None

def test_directory_info_exists(setup_info_stream : PdbInfoStream):
    assert setup_info_stream is not None

def test_directory_type_exists(setup_type_stream : PdbTypeStream):
    assert setup_type_stream is not None

def test_type_lookup_by_type_index(setup_type_stream : PdbTypeStream):
    typeindex = 4096 # first dynamic TI is 4096
    ptr = setup_type_stream.get_by_type_index(ti = typeindex)

    from pdbpy.streams.pdbtype.leaf_enum import LeafID
    assert ptr.record_type == LeafID.POINTER
    assert isinstance(ptr, pdbpy.streams.pdbtype.Pointer)

    assert BasicTypeInfo(ptr.reference_type) == (BasicTypeEnum.NarrowCharacter, BasicTypeModifier.NearPointer64)

    from pdbpy.streams.pdbtype import PointerTypeEnum, PointerModeEnum

    assert ptr.attributes.kind == PointerTypeEnum.BITS_64
    assert ptr.attributes.mode == PointerModeEnum.Normal

    print(ptr.attributes.kind)
    print(ptr.attributes.mode)
    print(ptr.attributes)

def test_type_lookup_by_type_name(setup_type_stream : PdbTypeStream):

    for ti, record in setup_type_stream.get_ti_and_record_for_name(name = "Yolo"):
        assert ti == 13523
        assert isinstance(record, TypeStructLike)
        assert record.element_count == 3
        expected_properties = TypeProperties(has_unique_name = 1)
        #expected_properties.has_unique_name = 1
        assert record.properties == expected_properties
        assert record.fields == 13522
        assert record.derived == 0
        assert record.vshape == 0
        assert record.unique_name == '.?AUYolo@@'

        field_record = setup_type_stream.get_by_type_index(ti = record.fields)
        print(field_record)
        assert isinstance(field_record, FieldList)
        assert len(field_record.members) == 3
        assert all(isinstance(member, Member) for member in field_record.members)
        x,y,z = field_record.members
        assert x.name == "x"
        assert y.name == "y"
        assert z.name == "z"
        print(x)
        print(BasicTypeInfo(z.field_type))
        assert BasicTypeInfo(x.field_type) == (BasicTypeEnum.Int32,   BasicTypeModifier.Direct)
        assert BasicTypeInfo(y.field_type) == (BasicTypeEnum.Float32, BasicTypeModifier.Direct)
        assert BasicTypeInfo(z.field_type) == (BasicTypeEnum.Float64, BasicTypeModifier.NearPointer64)

    asd()




def main():
        import sys


        #print(type_stream)


        calc_hash = pdbpy.utils.hash.get_hash_for_string(acty.name)
        print("Calculated hash for actor: ", calc_hash)
        print("Calculated bucket for actor: ", calc_hash % type_stream.header.buckets)
        
        print(f"Hash for actor:               {type_stream.get_hash_for_ti(actor_ti)}")
        print()


        errory_name = 'TWeakObjectPtr<AActor,FWeakObjectPtr>'
        errory_ti = 0x000408ad
        calc_hash = pdbpy.utils.hash.get_hash_for_string(errory_name)
        print(f"Calculated hash for errory:    {calc_hash:x}")
        print(f"Calculated bucket for errory:  {(calc_hash % type_stream.header.buckets):x}")
        print(f"Hash for errory:               {type_stream.get_hash_for_ti(errory_ti):x}")
        print(f"Hash for errory(fwd):          {type_stream.get_hash_for_ti(0x2578):x}")
        print()

        print(type_stream.get_structy_by_name(errory_name))


        import time
        s = time.perf_counter()
        acty = type_stream.get_by_type_index(ti = type_stream.header.ti_max-1) # 3.9s before thingy
        #acty = type_stream.get_by_type_index(ti = type_stream.header.ti_min+3)
        #acty = type_stream.get_by_type_index(ti = actor_ti)
        print(acty, "\n", time.perf_counter()-s)


        s = time.perf_counter()
        ti, typ = type_stream.get_structy_by_name('AActor')
        print("TI: ", ti)
        print("actor class:", typ, "\n", time.perf_counter()-s)
#
        #members_typ = type_stream.get_by_type_index(typ.field)
        #print("members: ")
        #for member in members_typ.members:
        #    print(member)

