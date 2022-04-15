
from pdbpy.msf import MultiStreamFile
from pdbpy.streams.streamdirectory import StreamDirectoryStream
from pdbpy.streams.pdbinfo import PdbInfoStream
from pdbpy.streams.pdbtype import PdbTypeStream
import pdbpy.utils.hash



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
        type_stream = PdbTypeStream(type_info_file, pdb_stream_directory, upfront_memory=False)
        #print(type_stream)

        actor_ti = 267711
        acty = type_stream.get_by_type_index(ti = actor_ti)
        print()
        print(acty)
        print()

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









if __name__ == '__main__':
    main()
