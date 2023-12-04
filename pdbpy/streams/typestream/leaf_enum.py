from enum import IntEnum, auto

from pdbpy.streams.typing import type_index

# Lifted from https:#github.com/microsoft/microsoft-pdb/blob/1d60e041600117a5004de84baa960d2c953a6aa6/include/cvinfo.h#L772
class LeafID(IntEnum):
    yolo = 0

    MODIFIER_16t     = 0x0001
    POINTER_16t      = 0x0002
    ARRAY_16t        = 0x0003
    CLASS_16t        = 0x0004
    STRUCTURE_16t    = 0x0005
    UNION_16t        = 0x0006
    ENUM_16t         = 0x0007
    PROCEDURE_16t    = 0x0008
    MFUNCTION_16t    = 0x0009
    VTSHAPE          = 0x000a
    COBOL0_16t       = 0x000b
    COBOL1           = 0x000c
    BARRAY_16t       = 0x000d
    LABEL            = 0x000e
    NULL             = 0x000f
    NOTTRAN          = 0x0010
    DIMARRAY_16t     = 0x0011
    VFTPATH_16t      = 0x0012
    PRECOMP_16t      = 0x0013       # not referenced from symbol
    ENDPRECOMP       = 0x0014       # not referenced from symbol
    OEM_16t          = 0x0015       # oem definable type string
    TYPESERVER_ST    = 0x0016       # not referenced from symbol

    # leaf indices starting records but referenced only from type records

    SKIP_16t         = 0x0200
    ARGLIST_16t      = 0x0201
    DEFARG_16t       = 0x0202
    LIST             = 0x0203
    FIELDLIST_16t    = 0x0204
    DERIVED_16t      = 0x0205
    BITFIELD_16t     = 0x0206
    METHODLIST_16t   = 0x0207
    DIMCONU_16t      = 0x0208
    DIMCONLU_16t     = 0x0209
    DIMVARU_16t      = 0x020a
    DIMVARLU_16t     = 0x020b
    REFSYM           = 0x020c

    BCLASS_16t       = 0x0400
    VBCLASS_16t      = 0x0401
    IVBCLASS_16t     = 0x0402
    ENUMERATE_ST     = 0x0403
    FRIENDFCN_16t    = 0x0404
    INDEX_16t        = 0x0405
    MEMBER_16t       = 0x0406
    STMEMBER_16t     = 0x0407
    METHOD_16t       = 0x0408
    NESTTYPE_16t     = 0x0409
    VFUNCTAB_16t     = 0x040a
    FRIENDCLS_16t    = 0x040b
    ONEMETHOD_16t    = 0x040c
    VFUNCOFF_16t     = 0x040d

# 32-bit type index versions of leaves all have the 0x1000 bit set
#
    TI16_MAX         = 0x1000

    MODIFIER         = 0x1001
    POINTER          = 0x1002
    ARRAY_ST         = 0x1003
    CLASS_ST         = 0x1004
    STRUCTURE_ST     = 0x1005
    UNION_ST         = 0x1006
    ENUM_ST          = 0x1007
    PROCEDURE        = 0x1008
    MFUNCTION        = 0x1009
    COBOL0           = 0x100a
    BARRAY           = 0x100b
    DIMARRAY_ST      = 0x100c
    VFTPATH          = 0x100d
    PRECOMP_ST       = 0x100e       # not referenced from symbol
    OEM              = 0x100f       # oem definable type string
    ALIAS_ST         = 0x1010       # alias (typedef) type
    OEM2             = 0x1011       # oem definable type string

    # leaf indices starting records but referenced only from type records

    SKIP             = 0x1200
    ARGLIST          = 0x1201
    DEFARG_ST        = 0x1202
    FIELDLIST        = 0x1203
    DERIVED          = 0x1204
    BITFIELD         = 0x1205
    METHODLIST       = 0x1206
    DIMCONU          = 0x1207
    DIMCONLU         = 0x1208
    DIMVARU          = 0x1209
    DIMVARLU         = 0x120a

    BCLASS           = 0x1400
    VBCLASS          = 0x1401
    IVBCLASS         = 0x1402
    FRIENDFCN_ST     = 0x1403
    INDEX            = 0x1404
    MEMBER_ST        = 0x1405
    STMEMBER_ST      = 0x1406
    METHOD_ST        = 0x1407
    NESTTYPE_ST      = 0x1408
    VFUNCTAB         = 0x1409
    FRIENDCLS        = 0x140a
    ONEMETHOD_ST     = 0x140b
    VFUNCOFF         = 0x140c
    NESTTYPEEX_ST    = 0x140d
    MEMBERMODIFY_ST  = 0x140e
    MANAGED_ST       = 0x140f

    # Types w/ SZ names

    ST_MAX           = 0x1500

    TYPESERVER       = 0x1501       # not referenced from symbol
    ENUMERATE        = 0x1502
    ARRAY            = 0x1503
    CLASS            = 0x1504
    STRUCTURE        = 0x1505
    UNION            = 0x1506
    ENUM             = 0x1507
    DIMARRAY         = 0x1508
    PRECOMP          = 0x1509       # not referenced from symbol
    ALIAS            = 0x150a       # alias (typedef) type
    DEFARG           = 0x150b
    FRIENDFCN        = 0x150c
    MEMBER           = 0x150d
    STMEMBER         = 0x150e
    METHOD           = 0x150f
    NESTTYPE         = 0x1510
    ONEMETHOD        = 0x1511
    NESTTYPEEX       = 0x1512
    MEMBERMODIFY     = 0x1513
    MANAGED          = 0x1514
    TYPESERVER2      = 0x1515

    STRIDED_ARRAY    = 0x1516    # same as ARRAY but with stride between adjacent elements
    HLSL             = 0x1517
    MODIFIER_EX      = 0x1518
    INTERFACE        = 0x1519
    BINTERFACE       = 0x151a
    VECTOR           = 0x151b
    MATRIX           = 0x151c

    VFTABLE          = 0x151d      # a virtual function table
    ENDOFLEAFRECORD  = VFTABLE

    TYPE_LAST        = ENDOFLEAFRECORD + 1 # one greater than the last type record
    TYPE_MAX         = TYPE_LAST - 1

    FUNC_ID          = 0x1601    # global func ID
    MFUNC_ID         = 0x1602    # member func ID
    BUILDINFO        = 0x1603    # build info: tool version command line src/pdb file
    SUBSTR_LIST      = 0x1604    # similar to ARGLIST for list of sub strings
    STRING_ID        = 0x1605    # string ID

    UDT_SRC_LINE     = 0x1606    # source and line on where an UDT is defined
                                     # only generated by compiler

    UDT_MOD_SRC_LINE = 0x1607    # module source and line on where an UDT is defined
                                     # only generated by linker

    ID_LAST          = UDT_MOD_SRC_LINE + 1   # one greater than the last ID record
    ID_MAX           = ID_LAST - 1

    NUMERIC          = 0x8000
    CHAR             = 0x8000
    SHORT            = 0x8001
    USHORT           = 0x8002
    LONG             = 0x8003
    ULONG            = 0x8004
    REAL32           = 0x8005
    REAL64           = 0x8006
    REAL80           = 0x8007
    REAL128          = 0x8008
    QUADWORD         = 0x8009
    UQUADWORD        = 0x800a
    REAL48           = 0x800b
    COMPLEX32        = 0x800c
    COMPLEX64        = 0x800d
    COMPLEX80        = 0x800e
    COMPLEX128       = 0x800f
    VARSTRING        = 0x8010

    OCTWORD          = 0x8017
    UOCTWORD         = 0x8018

    DECIMAL          = 0x8019
    DATE             = 0x801a
    UTF8STRING       = 0x801b

    REAL16           = 0x801c
    
    PAD0             = 0xf0
    PAD1             = 0xf1
    PAD2             = 0xf2
    PAD3             = 0xf3
    PAD4             = 0xf4
    PAD5             = 0xf5
    PAD6             = 0xf6
    PAD7             = 0xf7
    PAD8             = 0xf8
    PAD9             = 0xf9
    PAD10            = 0xfa
    PAD11            = 0xfb
    PAD12            = 0xfc
    PAD13            = 0xfd
    PAD14            = 0xfe
    PAD15            = 0xff