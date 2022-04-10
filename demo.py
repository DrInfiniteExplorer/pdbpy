
from pdbpy.msf import MultiStreamFile
from pdbpy.streams.streamdirectory import StreamDirectoryStream
from pdbpy.streams.pdbinfo import PdbInfoStream
from pdbpy.streams.pdbtype import PdbTypeStream




def main():
    import sys
    assert len(sys.argv) == 2, "Accepts only a path to a pdb as argument."
    with open(sys.argv[1], "rb") as f:
        msf = MultiStreamFile(f)
        stream = msf.get("Directory")

        print(f"pdb-stream, skip(1), take(16): {stream.read_pages(byte_offset = 1)[0:16]}")

        pdb_stream_directory = StreamDirectoryStream(stream)

        pdb_info_file = pdb_stream_directory.get_stream_by_index(1)
        info_stream = PdbInfoStream(pdb_info_file)
        print(info_stream)

        type_info_file = pdb_stream_directory.get_stream_by_index(2)
        type_stream = PdbTypeStream(type_info_file, upfront_memory=False)
        #print(type_stream)








if __name__ == '__main__':
    main()
