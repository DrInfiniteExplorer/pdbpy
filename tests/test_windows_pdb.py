import pytest
from pdbpy.codeview import LeafID

from pdbpy.msf import MultiStreamFile
from pdbpy.streams.debuginformationstream.debuginformationstream import PdbDebugInformationStream
from pdbpy.streams.directorystream import StreamDirectoryStream
from pdbpy.streams.pdbinfo import PdbInfoStream
from pdbpy.streams.typestream.pdbtypestream import PdbTypeStream

from pdbpy.streams.typestream.records import TypeStructLike, FieldList, Member, Pointer

from pdbpy.streams.typestream.records.base import TypeProperties, PointerTypeEnum, PointerModeEnum

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
def setup_info_stream(setup_windows_pdb: MultiStreamFile, setup_directory_stream : StreamDirectoryStream) -> PdbInfoStream:
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

@pytest.fixture
def setup_debuginformation_stream(setup_directory_stream : StreamDirectoryStream) -> PdbDebugInformationStream:
    debug_information_file = setup_directory_stream.get_stream_by_index(3)
    assert debug_information_file is not None
    debug_infomation_stream = PdbDebugInformationStream(debug_information_file, setup_directory_stream)
    return debug_infomation_stream

def test_can_open(setup_windows_pdb : MultiStreamFile):
    assert setup_windows_pdb is not None

def test_directory_exists(setup_directory_stream : StreamDirectoryStream):
    assert setup_directory_stream is not None

def test_directory_info_exists(setup_info_stream : PdbInfoStream):
    assert setup_info_stream is not None

def test_directory_type_exists(setup_type_stream : PdbTypeStream):
    assert setup_type_stream is not None

def test_debug_information_stream(setup_debuginformation_stream : PdbDebugInformationStream):
    assert setup_debuginformation_stream is not None

def test_type_lookup_by_type_index(setup_type_stream : PdbTypeStream):
    typeindex = 4096 # first dynamic TI is 4096
    ptr = setup_type_stream.get_by_type_index(ti = typeindex) # type: ignore

    assert ptr.record_type == LeafID.POINTER
    assert isinstance(ptr, Pointer)

    assert BasicTypeInfo(ptr.reference_type) == (BasicTypeEnum.NarrowCharacter, BasicTypeModifier.NearPointer64)

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
        assert record.name == 'Yolo'
        assert record.unique_name == '.?AUYolo@@'

        field_record = setup_type_stream.get_by_type_index(ti = record.fields) # type: ignore

        assert isinstance(field_record, FieldList)
        assert len(field_record.members) == 3
        assert all(isinstance(member, Member) for member in field_record.members)
        x,y,z = field_record.members
        assert x.name == "x"
        assert y.name == "y"
        assert z.name == "z"

        assert BasicTypeInfo(x.field_type) == (BasicTypeEnum.Int32,   BasicTypeModifier.Direct)
        assert BasicTypeInfo(y.field_type) == (BasicTypeEnum.Float32, BasicTypeModifier.Direct)
        assert BasicTypeInfo(z.field_type) == (BasicTypeEnum.Float64, BasicTypeModifier.NearPointer64)


