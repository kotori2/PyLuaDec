import struct
from consts import const
from treelib import Tree
const = const()

class LuaDec:
    def __init__(self, fileName):
        self.ptr = 0
        self.pc = 0
        self.tree = Tree()
        self.readFile(fileName)
        self.readHeader()
        self.readFunction()
        #self.tree.show()

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

    def formatValue(self, val):
        if type(val) == str:
            return "\"{}\"".format(val)
        elif type(val) == bool:
            if val:
                return "true"
            else:
                return "false"
        elif val is None:
            return "nil"
        elif type(val) == float and int(val) == val:
            return int(val)
        else:
            return val

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

    def readFunction(self, parent=None):
        #处理tree
        if parent:
            funcName = "function"
            funcSuffix = []
            #强烈谴责py不支持do...while
            #别问我这堆东西怎么工作的，it just works!!
            pNode = self.tree.get_node(parent).identifier
            funcSuffix.append("_{0}".format(len(self.tree.children(pNode))))
            while self.tree.parent(pNode):
                pNode = self.tree.parent(pNode).identifier
                funcSuffix.append("_{0}".format(len(self.tree.children(pNode)) - 1))
            
            funcSuffix.reverse()
            for i in funcSuffix:
                funcName += i
        else:
            funcName = "root"
        #self.tree.show()

        #ProtoHeader
        protoheader = struct.unpack("<IIccc", self.fileBuf[self.ptr:self.ptr + 11])
        self.ptr += 11
        lineDefined     = protoheader[0]
        lastLineDefined = protoheader[1]
        numParams       = ord(protoheader[2])
        is_vararg       = ord(protoheader[3])
        maxStackSize    = ord(protoheader[4])
        
        #Code
        sizeCode = self.readUInt32()
        instructions = []
        #print("Code total size: {0}".format(sizeCode))
        for i in range(sizeCode):
            ins = self.readUInt32()
            instructions.append(ins)
            #self.processInstruction(ins)
            #print("Instruction: {0}".format(hex(ins)))

        #Constants
        sizeConstants = self.readUInt32()
        constants = []
        #print("Constants total size: {0}".format(sizeConstants))
        for i in range(sizeConstants):
            const_type = self.fileBuf[self.ptr]
            self.ptr += 1
            if const_type == const.LUA_DATATYPE['LUA_TNIL']:
                const_val = None
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
                raise Exception("Undefined constant type {0}.".format(hex(const_type)))
            constants.append(const_val)
            #print("Constant: {0}".format(const_val))

        #Skip Protos
        ptrBackupStart = self.ptr #备份protos的位置，先处理后面的upvalue等东西
        sizeProtos = self.readUInt32()
        for i in range(sizeProtos):
            self.skipFunction()

        #Upvalue
        sizeUpvalue = self.readUInt32()
        upvalues = []
        #print("Upvalue total size: {0}".format(sizeUpvalue))
        for i in range(sizeUpvalue):
            instack = self.fileBuf[self.ptr]
            idx     = self.fileBuf[self.ptr + 1]
            self.ptr += 2
            upvalues.append([instack, idx])
            #print("Upvalue: {0} {1}".format(instack, idx))

        #srcName
        sizeSrcName = self.readUInt32()
        #print("srcName size: {0}".format(sizeSrcName))
        if sizeSrcName > 0:
            srcName = str(self.fileBuf[self.ptr:self.ptr + sizeSrcName], encoding="utf8")
            self.ptr += sizeSrcName
            #print("srcName: " + srcName)

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

        #将内容写入tree
        data = {
            "instructions": instructions,
            "constants":    constants,
            "upvalues":     upvalues,
        }
        self.tree.create_node(funcName, funcName, parent=parent, data=data)
        
        print("; {:<20s}{}".format("Function", funcName))
        print("; {:<20s}{}".format("Defined from line", lineDefined))
        print("; {:<20s}{}".format("Defined to line", lastLineDefined))
        print("; {:<20s}{}".format("#Upvalues", sizeUpvalue))
        print("; {:<20s}{}".format("#Parameters", numParams))
        print("; {:<20s}{}".format("Is_vararg", is_vararg))
        print("; {:<20s}{}\n".format("Max Stack Size", maxStackSize))
        
        #生成一个Upvalue和Constant的拼接表
        fmtVals = {}
        count = 0
        for i in data['constants']:
            fmtVals["K{}".format(count)] = self.formatValue(i)
            count += 1
        count = 0
        for i in data['upvalues']:
            fmtVals["U{}".format(count)] = "U{}".format(count)
            count += 1

        #处理单个指令
        self.pc = 0
        self.currFunc = funcName
        self.fmtVals = fmtVals
        for i in data['instructions']:
            self.processInstruction(i)
            self.pc += 1

        print("\n; Constants")
        count = 0
        for i in data['constants']:
            print("{:>5s} {}".format(str(count), i))
            count += 1

        print("\n; Upvalues")
        count = 0
        for i in data['upvalues']:
            print("{:>5s}\t{}\t{}".format(str(count), i[0], i[1]))
            count += 1
        
        print("\n")

        #Proto
        ptrBackupEnd = self.ptr
        self.ptr = ptrBackupStart
        sizeProtos = self.readUInt32()
        #print("Protos total size: {0}".format(sizeProtos))
        for i in range(sizeProtos):
            self.readFunction(parent=funcName)
        self.ptr = ptrBackupEnd

    #跳过函数，用于需要获取后面的指针位置的情况
    def skipFunction(self):
        #print("Start skipping Proto, current ptr at {0}".format(hex(self.ptr)))
        #ProtoHeader
        self.ptr += 11

        #Code
        sizeCode = self.readUInt32()
        for i in range(sizeCode):
            self.ptr += 4

        #Constants
        sizeConstants = self.readUInt32()
        for i in range(sizeConstants):
            const_type = self.fileBuf[self.ptr]
            self.ptr += 1
            if const_type == const.LUA_DATATYPE['LUA_TNIL']:
                pass
            elif const_type == const.LUA_DATATYPE['LUA_TNUMBER']:
                self.ptr += 8
            elif const_type == const.LUA_DATATYPE['LUA_TBOOLEAN']:
                self.ptr += 1
            elif const_type == const.LUA_DATATYPE['LUA_TSTRING']:
                str_len = self.readUInt32()
                self.ptr += str_len
            else:
                raise Exception("Undefined constant type {0}.".format(hex(const_type)))

        #Protos
        sizeProtos = self.readUInt32()
        for i in range(sizeProtos):
            self.skipFunction()

        #Upvalue
        sizeUpvalue = self.readUInt32()
        for i in range(sizeUpvalue):
            self.ptr += 2

        #srcName
        sizeSrcName = self.readUInt32()
        if sizeSrcName > 0:
            self.ptr += sizeSrcName

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
        #print("End skipping Proto. Current ptr at {0}".format(hex(self.ptr)))

    def processInstruction(self, ins):
        opCode = ins % (1 << 6)
        opMode = const.opMode[opCode]
        A = 0
        B = 0
        C = 0

        if opMode[4] == "iABC":
            A   = (ins >> 6 ) % (1 << 8)
            B   = (ins >> 23)#% (1 << 9)
            C   = (ins >> 14) % (1 << 9)
        elif opMode[4] == "iABx":
            A   = (ins >> 6 ) % (1 << 8)
            B   = (ins >> 14)#% (1 << 18)
        elif opMode[4] == "iAsBx":
            A   = (ins >> 6 ) % (1 << 8)
            B   = (ins >> 14) - (1 << 17) + 1
        elif opMode[4] == "iAx":
            A   = (ins >> 6 )#% (1 << 26)
        else:
            raise Exception("Unknown opMode {0}".format(opMode[4]))

        #format A
        if opMode[1] == 1:
            parsedA = "R{0}".format(A)
        elif opMode[1] == 0:
            if const.opCode[opCode] == "OP_SETTABUP":
                parsedA = "U{0}".format(A)
            elif const.opCode[opCode] in ["OP_EQ", "OP_LT", "OP_LE"]:
                parsedA = A
            else:
                parsedA = "R{0}".format(A)
        else:
            raise Exception("Unknown A Mode {0}".format(opMode[1]))

        #format B
        if opMode[2] == 1:
            if const.opCode[opCode].find("UP") >= 0:
                parsedB = "U{0}".format(B)
            else:
                parsedB = "{0}".format(B)
        elif opMode[2] == 0:
            parsedB = ""
        elif opMode[2] == 2 or opMode[2] == 3:
            if opMode[4] == "iAsBx":
                #B为sBx的时候，只有可能是立即数而不是寄存器
                parsedB = "{0}".format(B)
            elif const.opCode[opCode] == "OP_LOADK":
                #LOADK一定是读Kx而不是Rx
                parsedB = "K{0}".format(B)
            elif B < 0x100:
                parsedB = "R{0}".format(B)
            else:
                parsedB = "K{0}".format(B - 0x100)
                B -= 0x100
        else:
            raise Exception("Unknown B Mode {0}".format(opMode[2]))

        #format C
        if opMode[3] == 1:
            if const.opCode[opCode].find("UP") >= 0:
                parsedC = "U{0}".format(C)
            else:
                parsedC = "{0}".format(C)
        elif opMode[3] == 0:
            parsedC = ""
        elif opMode[3] == 2 or opMode[3] == 3:
            if C < 0x100:
                parsedC = "R{0}".format(C)
            else:
                parsedC = "K{0}".format(C - 0x100)
                C -= 0x100
        else:
            raise Exception("Unknown C Mode {0}".format(opMode[3]))

        # parse comment
        #先用模板拼接
        if len(parsedB) > 0 and (parsedB[0] == 'K' or parsedB[0] == 'U'):
            parsedB_ = "{{{}}}".format(parsedB)
        else:
            parsedB_ = parsedB
        if len(parsedC) > 0 and (parsedC[0] == 'K' or parsedC[0] == 'U'):
            parsedC_ = "{{{}}}".format(parsedC)
        else:
            parsedC_ = parsedC
        comment = const.pseudoCode[opCode].format(A=A,B=B,C=C,PB=parsedB_,PC=parsedC_)

        #预处理
        #if BForceK:
        #    comment = comment.replace("R{}".format(B), "K{}".format(B))
        #if const.opCode[opCode] == "OP_SETTABLE" and CForceK:
        #    comment = comment.replace("R{}".format(C), "{{K{}}}".format(C))

        #再处理Upvalue和Constants
        comment = comment.format(**self.fmtVals)

        #对部分需要处理的命令进行处理
        if const.opCode[opCode] == "OP_LOADBOOL":
            #把0/1转换成false/true
            comment = comment[:-1]
            if B:
                comment += "true"
            else:
                comment += "false"
            #处理跳转
            if C:
                comment += "; goto {0}".format(self.pc + 2)
        elif const.opCode[opCode] == "OP_LOADNIL":
            comment = ""
            for i in range(B + 1):
                comment += "R{0}, ".format(A + i)
            comment = comment[:-2]
            comment += " := nil"
        elif const.opCode[opCode] == "OP_SELF":
            comment = "R{}".format(A+1) + comment[2:]
        elif const.opCode[opCode] == "OP_JMP":
            comment += " (goto {0})".format(self.pc + 1 + B)
        elif const.opCode[opCode] in ["OP_EQ", "OP_LT", "OP_LE", "OP_TEST", "OP_TESTSET"]:
            if const.opCode[opCode] == "OP_EQ" and A:
                comment = comment.replace("==", "~=")
            if const.opCode[opCode] == "OP_LT" and A:
                comment = comment.replace("<", ">=")
            if const.opCode[opCode] == "OP_LE" and A:
                comment = comment.replace("<=", ">")
            comment += " goto {0} else goto {1}".format(self.pc + 2, self.pc + 1)
            if C == 0:
                comment = comment.replace("not ", "")
        elif const.opCode[opCode] == "OP_CALL":
            comment = ""
            for i in range(C - 1):
                comment += "R{}, ".format(A + i)
            if C > 1:
                comment = comment[:-2] + " := R{}(".format(A)
            elif C == 1:
                comment += " := R{}(".format(A)
            else:
                comment = "R{} to top := R{}(".format(A, A)
            
            for i in range(B - 1):
                comment += "R{}, ".format(A + i + 1)
            if B > 1:
                comment = comment[:-2] + ")"
            elif B == 1:
                comment += ")"
            else:
                comment += "R{} to top)".format(C)
        elif const.opCode[opCode] == "OP_TAILCALL":
            comment = "R{} to top := R{}(".format(A, A)
            for i in range(B - 1):
                comment += "R{}, ".format(A + i + 1)
            if B > 1:
                comment = comment[:-2] + ")"
            else:
                comment = comment + ")"
        elif const.opCode[opCode] == "OP_RETURN":
            for i in range(B - 1):
                comment += "R{}, ".format(A + i)
            if B > 1:
                comment = comment[:-2]
            elif B == 0:
                comment += "R{} to top".format(A)
        elif const.opCode[opCode] == "OP_FORLOOP":
            comment = comment.replace("RD", "R{}".format(A + 1))
            comment = comment.replace("RE", "R{}".format(A + 2))
            comment = comment.replace("RF", "R{}".format(A + 3))
            comment += "goto {} end".format(self.pc + B + 1)
        elif const.opCode[opCode] == "OP_FORPREP":
            comment = comment.replace("RD", "R{}".format(A + 2))
            comment += "(goto {})".format(self.pc + B + 1)
        elif const.opCode[opCode] == "OP_TFORCALL":
            comment = comment.replace("RD", "R{}".format(A + 1))
            comment = comment.replace("RE", "R{}".format(A + 2))
            comment = comment.replace("RF", "R{}".format(A + 3))
            comment = comment.replace("RG", "R{}".format(A + 4))
        elif const.opCode[opCode] == "OP_TFORLOOP":
            comment = comment.replace("RD", "R{}".format(A + 1))
            comment += " (goto {}))".format(self.pc + B + 1)
        elif const.opCode[opCode] == "OP_CLOSURE":
            if self.currFunc == "root":
                comment += "function_{})".format(B)
            else:
                comment += self.currFunc + "_{})".format(B)
        
        seq = []
        for i in [parsedA, parsedB, parsedC]:
            if i != "":
                seq.append(str(i))
        regsFmt = " ".join(seq)
        print("{:>5s} [-]: {:<10s}{:<13s}; {}".format(str(self.pc), const.opCode[opCode][3:], regsFmt, comment))
