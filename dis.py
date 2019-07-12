import sys
from disassembler import LuaDec

if len(sys.argv) > 2:
    d = LuaDec(sys.argv[1], sys.argv[2])
elif len(sys.argv) > 1:
    d = LuaDec(sys.argv[1])
else:
    print("PyLuaDec")
    print("Usage: python dis.py <filename> [OUTPUT_FORMAT=luadec]")