REM /GS- /Gs9999999 /link /STACK:0x100000,0x100000 to enable >4kb stack

del *.exe *.pdb *.obj *.pdb *.txt *.yml *.ilk *.lib

call :build minimal
call :build addr
goto :EOF

:build

cl @%1.rsp
..\..\microsoft-pdb\cvdump\cvdump.exe %1.pdb > %1_cvdump.txt
llvm-pdbutil dump -all %1.pdb > %1_llvm-pdbutil_dump.txt
llvm-pdbutil diadump %1.pdb > %1_llvm-pdbutil_diadump.txt
llvm-pdbutil pdb2yaml %1.pdb > %1_llvm-pdbutil_dump.yml
llvm-pdbutil pretty -all %1.pdb > %1_llvm-pdbutil_pretty.txt

%1.exe > %1.txt
goto :EOF