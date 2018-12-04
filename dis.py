import struct
from consts import const
const = const()

class LuaDec:
    def __init__(self, fileName):
        self.ptr = 0
        self.readFile(fileName)
        self.readHeader()
        self.readFunction()

    def readFile(self, fileName):
        f = open(fileName, "rb")
        self.fileBuf = f.read()
        f.close()

    def readUInt32(self):
        result = struct.unpack("<I", self.fileBuf[self.ptr:self.ptr + 4])[0]
        self.ptr += 4
        return result

    def readUInt64(self):
        result = struct.unpack("<Q", self.fileBuf[self.ptr:self.ptr + 8])[0]
        self.ptr += 8
        return result

    def readHeader(self):
        magic = self.fileBuf[:4]
        if magic != b"\x1bLua":
            raise Exception("Unknown magic: {0}".format(magic.hex()))

        version = self.fileBuf[4]
        if version != 82:
            raise Exception("This program support ONLY Lua 5.2")

        lua_tail = self.fileBuf[12:18]
        if lua_tail != b"\x19\x93\r\n\x1a\n":
            raise Exception("Unexcepted lua_tail value: {0}".format(lua_tail.hex()))
        self.ptr = 18

    def readFunction(self):
        #ProtoHeader
        protoheader = struct.unpack("<IIccc", self.fileBuf[self.ptr:self.ptr + 11])
        self.ptr += 11
        lineDefined     = protoheader[0]
        lastLineDefined = protoheader[1]
        numParams       = ord(protoheader[2])
        is_vararg       = ord(protoheader[3])
        maxStackSize    = ord(protoheader[4])
        print("Function defined on line {0} - {1} have {2} params".format(lineDefined, lastLineDefined, numParams))
        
        #Code
        sizeCode = self.readUInt32()
        print("Code total size: {0}".format(sizeCode))
        for i in range(sizeCode):
            ins = self.readUInt32()
            self.processInstruction(ins)
            #print("Instruction: {0}".format(hex(ins)))

        #Constants
        sizeConstants = self.readUInt32()
        print("Constants total size: {0}".format(sizeConstants))
        for i in range(sizeConstants):
            const_type = self.fileBuf[self.ptr]
            self.ptr += 1
            if const_type == const.LUA_DATATYPE['LUA_TNIL']:
                const_val = self.fileBuf[self.ptr]
                self.ptr += 1
            elif const_type == const.LUA_DATATYPE['LUA_TNUMBER']:
                #lua的number=double(8 bytes)
                const_val = struct.unpack("<d", self.fileBuf[self.ptr:self.ptr + 8])[0]
                self.ptr += 8
            elif const_type == const.LUA_DATATYPE['LUA_TBOOLEAN']:
                const_val = bool(self.fileBuf[self.ptr])
                self.ptr += 1
            elif const_type == const.LUA_DATATYPE['LUA_TSTRING']:
                str_len = self.readUInt32()
                const_val = str(self.fileBuf[self.ptr:self.ptr + str_len - 1], encoding="utf8")
                self.ptr += str_len
                if self.fileBuf[self.ptr - 1] != 0:
                    raise Exception("Bad string")
            else:
                raise Exception("Undefined constant type.")
            print("Constant: {0}".format(const_val))

        #Protos
        sizeProtos = self.readUInt32()
        print("Protos total size: {0}".format(sizeProtos))
        for i in range(sizeProtos):
            self.readFunction()

        #Upvalue
        sizeUpvalue = self.readUInt32()
        print("Upvalue total size: {0}".format(sizeUpvalue))
        for i in range(sizeUpvalue):
            instack = self.fileBuf[self.ptr]
            idx     = self.fileBuf[self.ptr + 1]
            self.ptr += 2
            print("Upvalue: {0} {1}".format(instack, idx))

        #srcName
        sizeSrcName = self.readUInt32()
        print("srcName size: {0}".format(sizeSrcName))
        if sizeSrcName > 0:
            srcName = str(self.fileBuf[self.ptr:self.ptr + sizeSrcName], encoding="utf8")
            self.ptr += sizeSrcName
            print("srcName: " + srcName)

        #Lines
        sizeLines = self.readUInt32()
        self.ptr += sizeLines

        #LocVars
        sizeLocVars = self.readUInt32()
        #for i in sizeLocVars:
        #    varname_size = 
        #TODO: sizeLocVars不为0的情况（未strip）

        #UpvalNames
        sizeUpvalNames = self.readUInt32()

    def processInstruction(self, ins):
        opCode = ins % (1 << 6)
        opMode = const.opMode[opCode]

        if opMode[4] == "iABC":
            A   = (ins >> 6 ) % (1 << 8)
            B   = (ins >> 23)#% (1 << 9)
            C   = (ins >> 14) % (1 << 9)
        elif opMode[4] == "iABx":
            A   = (ins >> 6 ) % (1 << 8)
            B   = (ins >> 14)#% (1 << 18)
        elif opMode[4] == "iAsBx":
            A   = (ins >> 6 ) % (1 << 8)
            B   = (ins >> 14) % (1 << 17)
            if ins >> 31:
                B = (1 << 18) - B
        elif opMode[4] == "iAx":
            A   = (ins >> 6 )#% (1 << 26)
        else:
            raise Exception("Unknown opMode {0}".format(opMode[4]))
        
        try:
            print("opCode: {0} \t{1} \t{2} \t{3}".format(const.opCode[opCode], hex(A), hex(B), hex(C)))
        except:
            pass

d = LuaDec("start.lua")