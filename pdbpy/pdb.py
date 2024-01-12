

from typing import List, Optional
from pdbpy.codeview.records.symbols.base import SymbolBase
from pdbpy.codeview.records.symbols.datasym import DataSym
from pdbpy.codeview.symbols import SymEnum

from pdbpy.msf import MultiStreamFile
from pdbpy.streams.debuginformationstream.debuginformationstream import PdbDebugInformationStream
from pdbpy.streams.directorystream.streamdirectory import StreamDirectoryStream
from pdbpy.streams.pdbinfo import PdbInfoStream
from pdbpy.streams.sectionheaderstream.sectionheaderstream import PdbSectionHeaderStream
from pdbpy.streams.symbolsstream.symbolsstream import PdbSymbolRecordStream
from pdbpy.streams.typestream.pdbtypestream import PdbTypeStream


class PDB:
    msf:            Optional[MultiStreamFile]
    _directory:      Optional[StreamDirectoryStream]
    _info:           Optional[PdbInfoStream]
    _types:          Optional[PdbTypeStream]
    _debuginfo:      Optional[PdbDebugInformationStream]
    _symbols:        Optional[PdbSymbolRecordStream]
    _sectionheaders: Optional[PdbSectionHeaderStream]

    def __init__(self, filepath: Optional[str]):
        self.msf = None
        self._directory = None
        self._info = None
        self._types = None
        self._debuginfo = None
        self._symbols = None
        self._sectionheaders = None
        if filepath:
            self.load(filepath)
    
    def load(self, filepath: str):
        assert self.msf is None
        with open(filepath, "rb") as f:
            self.msf = MultiStreamFile(f)

    @property
    def directory(self):
        assert self.msf
        if self._directory:
            return self._directory
        stream = self.msf.get("Directory")
        self._directory = StreamDirectoryStream(stream)
        return self._directory

    @property
    def info(self):
        if self._info:
            return self._info
        info_file = self.directory.get_stream_by_index(1)
        self._info = PdbInfoStream(info_file)
        return self._info
    
    @property
    def types(self):
        if self._types:
            return self._types
        type_info_file = self.directory.get_stream_by_index(2)
        self._types = PdbTypeStream(type_info_file, self._directory, upfront_memory=False)
        return self._types
    
    @property
    def debuginfo(self):
        if self._debuginfo:
            return self._debuginfo
        debug_information_file = self.directory.get_stream_by_index(3)
        self._debuginfo = PdbDebugInformationStream(debug_information_file)
        return self._debuginfo
    
    @property
    def symbols(self):
        if self._symbols:
            return self._symbols
        symbol_record_stream_number = self.debuginfo.header.symbol_record_stream
        symbol_record_stream_file = self.directory.get_stream_by_index(int(symbol_record_stream_number))
        assert symbol_record_stream_file is not None

        self._symbols = PdbSymbolRecordStream(symbol_record_stream_file)
        return self._symbols
    
    @property
    def sectionheaders(self):
        if self._sectionheaders:
            return self._sectionheaders
        header = self.debuginfo.dbg_header
        stream_num = int(header.section_hdr_orig)
        if stream_num == 0xFFFF:
            stream_num = int(header.section_header)
        assert stream_num != 0xFFFF

        sections_file = self.directory.get_stream_by_index(stream_num)
        self._sectionheaders = PdbSectionHeaderStream(sections_file)
        return self._sectionheaders

    def find_symbol(self, name: str, types: Optional[List[SymEnum]] = None) -> Optional[SymbolBase]:
        for symbol in self.symbols.symbols(types):
            if getattr(symbol, 'name', None) == name:
                return symbol
    
    def find_symbol_address(self, name:str, imagebase: int=0, types: Optional[List[SymEnum]] = None):
        symbol = self.find_symbol(name, types=types)
        if symbol is None:
            return None
        if isinstance(symbol, DataSym):
            segment: int = symbol.segment
            section = self.sectionheaders.sections[segment-1]
            # maybe imagebase needs to be adjusted n things, who knows
            return imagebase + section.virtual_address + symbol.offset
        
            

        