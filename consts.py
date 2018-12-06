class const:
    def __init__(self):
        self.LUA_DATATYPE = {
            "LUA_TNIL": 0,
            "LUA_TBOOLEAN": 1,
            "LUA_TLIGHTUSERDATA": 2,
            "LUA_TNUMBER": 3,
            "LUA_TSTRING": 4,
            "LUA_TTABLE": 5,
            "LUA_TFUNCTION": 6,
            "LUA_TUSERDATA": 7,
            "LUA_TTHREAD": 8,
            "LUA_NUMTAGS": 9,
        }

        self.opCode = [
            "OP_MOVE",#/*	A B	R(A) := R(B)					*/
            "OP_LOADK",#/*	A Bx	R(A) := Kst(Bx)					*/
            "OP_LOADKX",#/*	A 	R(A) := Kst(extra arg)				*/
            "OP_LOADBOOL",#/*	A B C	R(A) := (Bool)B; if (C) pc++			*/
            "OP_LOADNIL",#/*	A B	R(A), R(A+1), ..., R(A+B) := nil		*/
            "OP_GETUPVAL",#/*	A B	R(A) := UpValue[B]				*/

            "OP_GETTABUP",#/*	A B C	R(A) := UpValue[B][RK(C)]			*/
            "OP_GETTABLE",#/*	A B C	R(A) := R(B)[RK(C)]				*/

            "OP_SETTABUP",#/*	A B C	UpValue[A][RK(B)] := RK(C)			*/
            "OP_SETUPVAL",#/*	A B	UpValue[B] := R(A)				*/
            "OP_SETTABLE",#/*	A B C	R(A)[RK(B)] := RK(C)				*/

            "OP_NEWTABLE",#/*	A B C	R(A) := {} (size = B,C)				*/

            "OP_SELF",#/*	A B C	R(A+1) := R(B); R(A) := R(B)[RK(C)]		*/

            "OP_ADD",#/*	A B C	R(A) := RK(B) + RK(C)				*/
            "OP_SUB",#/*	A B C	R(A) := RK(B) - RK(C)				*/
            "OP_MUL",#/*	A B C	R(A) := RK(B) * RK(C)				*/
            "OP_DIV",#/*	A B C	R(A) := RK(B) / RK(C)				*/
            "OP_MOD",#/*	A B C	R(A) := RK(B) % RK(C)				*/
            "OP_POW",#/*	A B C	R(A) := RK(B) ^ RK(C)				*/
            "OP_UNM",#/*	A B	R(A) := -R(B)					*/
            "OP_NOT",#/*	A B	R(A) := not R(B)				*/
            "OP_LEN",#/*	A B	R(A) := length of R(B)				*/

            "OP_CONCAT",#/*	A B C	R(A) := R(B).. ... ..R(C)			*/

            "OP_JMP",#/*	A sBx	pc+=sBx; if (A) close all upvalues >= R(A - 1)	*/
            "OP_EQ",#/*	A B C	if ((RK(B) == RK(C)) ~= A) then pc++		*/
            "OP_LT",#/*	A B C	if ((RK(B) <  RK(C)) ~= A) then pc++		*/
            "OP_LE",#/*	A B C	if ((RK(B) <= RK(C)) ~= A) then pc++		*/

            "OP_TEST",#/*	A C	if not (R(A) <=> C) then pc++			*/
            "OP_TESTSET",#/*	A B C	if (R(B) <=> C) then R(A) := R(B) else pc++	*/

            "OP_CALL",#/*	A B C	R(A), ... ,R(A+C-2) := R(A)(R(A+1), ... ,R(A+B-1)) */
            "OP_TAILCALL",#/*	A B C	return R(A)(R(A+1), ... ,R(A+B-1))		*/
            "OP_RETURN",#/*	A B	return R(A), ... ,R(A+B-2)	(see note)	*/

            "OP_FORLOOP",#/*	A sBx	R(A)+=R(A+2);
            			#if R(A) <?= R(A+1) then { pc+=sBx; R(A+3)=R(A) }*/
            "OP_FORPREP",#/*	A sBx	R(A)-=R(A+2); pc+=sBx				*/

            "OP_TFORCALL",#/*	A C	R(A+3), ... ,R(A+2+C) := R(A)(R(A+1), R(A+2));	*/
            "OP_TFORLOOP",#/*	A sBx	if R(A+1) ~= nil then { R(A)=R(A+1); pc += sBx }*/

            "OP_SETLIST",#/*	A B C	R(A)[(C-1)*FPF+i] := R(A+i), 1 <= i <= B	*/

            "OP_CLOSURE",#/*	A Bx	R(A) := closure(KPROTO[Bx])			*/

            "OP_VARARG",#/*	A B	R(A), R(A+1), ..., R(A+B-2) = vararg		*/

            "OP_EXTRAARG"#/*	Ax	extra (larger) argument for previous opcode	*/
        ]

        self.pseudoCode = [
            "R{A} := R{B}",
            "R{A} := {{K{B}}}",
            "UNSUPPORTED",
            "R{A} := {B}",
            "",                                     #R(A+1), ..., R(A+B) := nil，没法用模板
            "R{A} := {{U{B}}}",
            "R{A} := {{U{B}}}[{PC}]",
            "R{A} := R{B}[{PC}]",
            "{{U{A}}}[{PB}] := {PC}",
            "{{U{B}}} := R{A}",
            "R{A}[{PB}] := R{C}",
            "R{A} := {{{{}}}} (size = {B}, {C})",
            "RD := R{B}; R{A} := R{B}[{PC}]",
            "R{A} := {PB} + {PC}",
            "R{A} := {PB} - {PC}",
            "R{A} := {PB} * {PC}",
            "R{A} := {PB} / {PC}",
            "R{A} := {PB} % {PC}",
            "R{A} := {PB} ^ {PC}",
            "R{A} := -R{B}",
            "R{A} := not R{B}",
            "R{A} := #R{B}",
            "R{A} := R{B} .. R{C}",
            "PC += {B}",
            "if {PB} ~= {PC} then",
            "if {PB} < {PC} then",
            "if {PB} <= {PC} then",
            "if not R{A} then",
            "if R{B} then R{A} := R{B};",
            "",                                     #R(A), ... ,R(A+C-2) := R(A)(R(A+1), ... ,R(A+B-1))
            "",                                     #return R(A)(R(A+1), ... ,R(A+B-1))
            "return ",
            "R{A} += RE; if R{A} <= RD then RF := R{A}; PC += {B}, ",
            "R{A} -= RD; PC += {B} ",
            "RF, RG := R{A}(RD, RE)",
            "if RD ~= nil then (R{A} := RD; PC += {B}",
            "UNSUPPORTED",
            "R{A} := closure(",
            "UNSUPPORTED",
            "UNSUPPORTED"
        ]

        OpArgN = 0  #参数未被使用
        OpArgU = 1  #已使用参数
        OpArgR = 2  #参数是寄存器或跳转偏移
        OpArgK = 3  #参数是常量或寄存器常量

        self.opMode = [
            #T  A    B       C     mode		        opcode
            (0, 1, OpArgR, OpArgN, "iABC"),		# OP_MOVE 
            (0, 1, OpArgK, OpArgN, "iABx"),		# OP_LOADK 
            (0, 1, OpArgN, OpArgN, "iABx"),		# OP_LOADKX 
            (0, 1, OpArgU, OpArgU, "iABC"),		# OP_LOADBOOL 
            (0, 1, OpArgU, OpArgN, "iABC"),		# OP_LOADNIL 
            (0, 1, OpArgU, OpArgN, "iABC"),		# OP_GETUPVAL 
            (0, 1, OpArgU, OpArgK, "iABC"),		# OP_GETTABUP 
            (0, 1, OpArgR, OpArgK, "iABC"),		# OP_GETTABLE 
            (0, 0, OpArgK, OpArgK, "iABC"),		# OP_SETTABUP 
            (0, 0, OpArgU, OpArgN, "iABC"),		# OP_SETUPVAL 
            (0, 0, OpArgK, OpArgK, "iABC"),		# OP_SETTABLE 
            (0, 1, OpArgU, OpArgU, "iABC"),		# OP_NEWTABLE 
            (0, 1, OpArgR, OpArgK, "iABC"),		# OP_SELF 
            (0, 1, OpArgK, OpArgK, "iABC"),		# OP_ADD 
            (0, 1, OpArgK, OpArgK, "iABC"),		# OP_SUB 
            (0, 1, OpArgK, OpArgK, "iABC"),		# OP_MUL 
            (0, 1, OpArgK, OpArgK, "iABC"),		# OP_DIV 
            (0, 1, OpArgK, OpArgK, "iABC"),		# OP_MOD 
            (0, 1, OpArgK, OpArgK, "iABC"),		# OP_POW 
            (0, 1, OpArgR, OpArgN, "iABC"),		# OP_UNM 
            (0, 1, OpArgR, OpArgN, "iABC"),		# OP_NOT 
            (0, 1, OpArgR, OpArgN, "iABC"),		# OP_LEN 
            (0, 1, OpArgR, OpArgR, "iABC"),		# OP_CONCAT 
            (0, 0, OpArgR, OpArgN, "iAsBx"),	# OP_JMP 
            (1, 0, OpArgK, OpArgK, "iABC"),		# OP_EQ 
            (1, 0, OpArgK, OpArgK, "iABC"),		# OP_LT 
            (1, 0, OpArgK, OpArgK, "iABC"),		# OP_LE 
            (1, 0, OpArgN, OpArgU, "iABC"),		# OP_TEST 
            (1, 1, OpArgR, OpArgU, "iABC"),		# OP_TESTSET 
            (0, 1, OpArgU, OpArgU, "iABC"),		# OP_CALL 
            (0, 1, OpArgU, OpArgU, "iABC"),		# OP_TAILCALL 
            (0, 0, OpArgU, OpArgN, "iABC"),		# OP_RETURN 
            (0, 1, OpArgR, OpArgN, "iAsBx"),	# OP_FORLOOP 
            (0, 1, OpArgR, OpArgN, "iAsBx"),	# OP_FORPREP 
            (0, 0, OpArgN, OpArgU, "iABC"),		# OP_TFORCALL 
            (0, 1, OpArgR, OpArgN, "iAsBx"),	# OP_TFORLOOP 
            (0, 0, OpArgU, OpArgU, "iABC"),		# OP_SETLIST 
            (0, 1, OpArgU, OpArgN, "iABx"),		# OP_CLOSURE 
            (0, 1, OpArgU, OpArgN, "iABC"),		# OP_VARARG 
            (0, 0, OpArgU, OpArgU, "iAx"),		# OP_EXTRAARG 
        ]