from typing import List
import pytest
from pdbpy.codeview import LeafID
from pdbpy.codeview.records.symbols.datasym import DataSym
from pdbpy.codeview.symbols import SymEnum

from pdbpy.msf import MultiStreamFile
from pdbpy.pe.records import ImageSectionHeader
from pdbpy.streams.debuginformationstream.debuginformationstream import PdbDebugInformationStream
from pdbpy.streams.directorystream import StreamDirectoryStream
from pdbpy.streams.pdbinfo import PdbInfoStream
from pdbpy.streams.symbolsstream import PdbSymbolRecordStream
from pdbpy.streams.typestream.pdbtypestream import PdbTypeStream

from pdbpy.streams.typestream.records import TypeStructLike, FieldList, Member, Pointer

from pdbpy.streams.typestream.records.base import TypeProperties, PointerTypeEnum, PointerModeEnum

from pdbpy.primitivetypes import BasicTypeEnum, BasicTypeModifier, BasicTypeInfo
from pdbpy.utils.range_keys import chunk


@pytest.fixture
def setup_windows_pdb() -> MultiStreamFile:
    with open("example_pdbs/minimal.pdb", "rb") as f:
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
    debug_infomation_stream = PdbDebugInformationStream(debug_information_file)
    return debug_infomation_stream

@pytest.fixture
def setup_symbol_record_stream(setup_directory_stream : StreamDirectoryStream,
                               setup_debuginformation_stream : PdbDebugInformationStream) -> PdbSymbolRecordStream:
    symbol_record_stream_number = setup_debuginformation_stream.header.symbol_record_stream
    #print(symbol_record_stream_number)

    symbol_record_stream_file = setup_directory_stream.get_stream_by_index(int(symbol_record_stream_number))
    assert symbol_record_stream_file is not None

    symbol_record_stream = PdbSymbolRecordStream(symbol_record_stream_file)

    return symbol_record_stream


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
    typeindex = 4100
    ptr = setup_type_stream.get_by_type_index(ti = typeindex) # type: ignore

    assert ptr.record_type == LeafID.POINTER
    assert isinstance(ptr, Pointer)

    assert BasicTypeInfo(ptr.reference_type) == (BasicTypeEnum.NarrowCharacter, BasicTypeModifier.NearPointer64)

    assert ptr.attributes.kind == PointerTypeEnum.BITS_64
    assert ptr.attributes.mode == PointerModeEnum.Normal

def test_type_lookup_by_type_name(setup_type_stream : PdbTypeStream):

    for ti, record in setup_type_stream.get_ti_and_record_for_name(name = "Yolo"):
        assert ti == 4099
        assert isinstance(record, TypeStructLike)
        assert record.element_count == 3
        expected_properties = TypeProperties(has_unique_name = 1)
        #expected_properties.has_unique_name = 1
        assert record.properties == expected_properties
        assert record.fields == 4098
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

def test_module_information(setup_debuginformation_stream : PdbDebugInformationStream):
    for module in setup_debuginformation_stream.modules:
        if module.module.lower().endswith('.obj'):
            assert module.object.lower().endswith('.lib') or module.object == module.module
        #print(module)
    #print(setup_debuginformation_stream.header)

def test_symbol_records_stream(setup_symbol_record_stream: PdbSymbolRecordStream,
                               setup_type_stream : PdbTypeStream):
    assert setup_symbol_record_stream is not None

    symbols: List[str] = []
    for symbol in setup_symbol_record_stream.symbols():
        if isinstance(symbol, DataSym):
            symbols.append(symbol.name)

            typ = symbol.typ
            if typ > 4096:
                t = setup_type_stream.get_by_type_index(typ)
            else:
                t = BasicTypeInfo(typ)
            print(f"{symbol} : {t}")
        else:
            print(f"Symbol: {symbol}")

    expected_symbols = ['_fltused', 'global_char_ptr_ptr', 'static_global_char_ptr_ptr', 'namespaced_global_char_ptr_ptr', 'export_global_char_ptr_ptr']
    assert expected_symbols == symbols

def test_symbol_address():
    with open("example_pdbs/addr.pdb", "rb") as f:
        msf = MultiStreamFile(f)
    stream = msf.get("Directory")
    stream_directory = StreamDirectoryStream(stream)
    info_file = stream_directory.get_stream_by_index(1)
    info_stream = PdbInfoStream(info_file)

    type_info_file = stream_directory.get_stream_by_index(2)
    type_stream = PdbTypeStream(type_info_file, stream_directory, upfront_memory=False)

    debug_information_file = stream_directory.get_stream_by_index(3)
    debug_infomation_stream = PdbDebugInformationStream(debug_information_file)

    symbol_record_stream_number = debug_infomation_stream.header.symbol_record_stream

    symbol_record_stream_file = stream_directory.get_stream_by_index(int(symbol_record_stream_number))
    assert symbol_record_stream_file is not None

    symbol_record_stream = PdbSymbolRecordStream(symbol_record_stream_file)

    for symbol in symbol_record_stream.symbols(types=[SymEnum.S_GDATA32]):
        if isinstance(symbol, DataSym):
            if symbol.name == "global_variable":
                break
    assert symbol.name == "global_variable"
    print(symbol)
    symbol.offset
    symbol.segment
    s=debug_infomation_stream.section_map[symbol.segment-1]
    print(s)
    sections = stream_directory.get_stream_by_index(int(debug_infomation_stream.dbg_header.section_header))
    from ctypes import sizeof as c_sizeof
    sections = [ImageSectionHeader.from_buffer_copy(section_mem) for section_mem in chunk(sections, c_sizeof(ImageSectionHeader))]
    section = sections[symbol.segment-1]
    print(section)
    addr = section.virtual_address + symbol.offset
    print(addr)
    print(f"0x{addr:08X}")
        



    asd()







    

