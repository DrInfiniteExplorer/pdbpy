REM /GS- /Gs9999999 /link /STACK:0x100000,0x100000 to enable >4kb stack

del windows.exe windows.pdb windows.obj vc140.pdb *.txt *.yml

cl -Gm- -GR- -EHa- -Oi windows.cpp /Zi -link -NODEFAULTLIB -subsystem:windows
..\..\microsoft-pdb\cvdump\cvdump.exe windows.pdb > windows_pdb_cvdump.txt
llvm-pdbutil dump -all windows.pdb > windows_pdb_llvm-pdbutil_dump.txt
llvm-pdbutil diadump windows.pdb > windows_pdb_llvm-pdbutil_diadump.txt
llvm-pdbutil pdb2yaml windows.pdb > windows_pdb_llvm-pdbutil_dump.yml
llvm-pdbutil pretty -all windows.pdb > windows_pdb_llvm-pdbutil_pretty.txt
