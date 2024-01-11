from enum import IntEnum

from pdbpy.codeview.types import type_index

# See https://llvm.org/docs/PDB/TpiStream.html
class BasicTypeEnum(IntEnum):
  NoType             = 0x0000          # uncharacterized type (no type)
  Void               = 0x0003          # void
  NotTranslated      = 0x0007          # type not translated by cvpack
  HResult            = 0x0008          # OLE/COM HRESULT

  SignedCharacter    = 0x0010          # 8 bit signed
  NarrowCharacter    = 0x0070          # really a char
  SByte              = 0x0068          # 8 bit signed int
  Character8         = 0x007c          # char8_t

  Boolean8           = 0x0030   # 8 bit boolean
  UnsignedCharacter  = 0x0020          # 8 bit unsigned
  Byte               = 0x0069          # 8 bit unsigned int

  WideCharacter      = 0x0071          # wide char
  Character16        = 0x007a          # char16_t
  Int16Short         = 0x0011          # 16 bit signed
  Int16              = 0x0072          # 16 bit signed int


  Boolean16          = 0x0031  # 16 bit boolean
  UInt16Short        = 0x0021          # 16 bit unsigned
  UInt16             = 0x0073          # 16 bit unsigned int

  Character32        = 0x007b          # char32_t
  Int32Long          = 0x0012          # 32 bit signed
  Int32              = 0x0074          # 32 bit signed int

  Boolean32          = 0x0032  # 32 bit boolean
  UInt32Long         = 0x0022          # 32 bit unsigned
  UInt32             = 0x0075          # 32 bit unsigned int

  Int64Quad          = 0x0013          # 64 bit signed
  Int64              = 0x0076          # 64 bit signed int

  Boolean64          = 0x0033  # 64 bit boolean
  UInt64Quad         = 0x0023          # 64 bit unsigned
  UInt64             = 0x0077          # 64 bit unsigned int

  Int128Oct          = 0x0014          # 128 bit signed int
  Int128             = 0x0078          # 128 bit signed int

  Boolean128         = 0x0034 # 128 bit boolean    
  UInt128Oct         = 0x0024          # 128 bit unsigned int
  UInt128            = 0x0079          # 128 bit unsigned int

  Float16            = 0x0046                 # 16 bit real
  Float32            = 0x0040                 # 32 bit real
  Float32PartialPrecision = 0x0045 # 32 bit PP real
  Float48            = 0x0044                 # 48 bit real
  Float64            = 0x0041                 # 64 bit real
  Float80            = 0x0042                 # 80 bit real
  Float128           = 0x0043                # 128 bit real

  Complex16          = 0x0056                 # 16 bit complex
  Complex32          = 0x0050                 # 32 bit complex
  Complex32PartialPrecision = 0x0055 # 32 bit PP complex
  Complex48         = 0x0054                 # 48 bit complex
  Complex64         = 0x0051                 # 64 bit complex
  Complex80         = 0x0052                 # 80 bit complex
  Complex128        = 0x0053                # 128 bit complex

    
class BasicTypeModifier(IntEnum):
  Direct          = 0        # Not a pointer
  NearPointer     = 1   # Near pointer
  FarPointer      = 2    # Far pointer
  HugePointer     = 3   # Huge pointer
  NearPointer32   = 4 # 32 bit near pointer
  FarPointer32    = 5  # 32 bit far pointer
  NearPointer64   = 6 # 64 bit near pointer
  NearPointer128  = 7 # 128 bit near pointer

# Void = (Void, NearPointerXX)
# nullptr = (Void, NearPointer)


class BasicTypeInfo:
  def __init__(self, ti : type_index):
    assert ti <= 4095, f"Automagic decomposition of ti {ti} into a basic type assumes ti <= 4095"

    type_num = ti & 0xFF
    mod_num = (ti >> 8) & 0xF

    self.type = BasicTypeEnum(type_num)
    self.mod = BasicTypeModifier(mod_num)
  
  def __str__(self):
    if self.mod != BasicTypeModifier.Direct:
      return f"{self.mod.name} to {self.type.name}"
    return self.type.name

  def __eq__(self, other):
    if isinstance(other, BasicTypeInfo):
      return self.type == other.type and self.mod == other.mod
    if isinstance(other, tuple) and len(other) == 2:
      typ, mod = other
      return self.type == typ and self.mod == mod


__all__ = ('BasicTypeEnum', 'BasicTypeModifier', 'BasicTypeInfo')
