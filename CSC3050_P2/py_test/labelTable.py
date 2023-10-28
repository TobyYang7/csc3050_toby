import functions as f

reg = [
    "zero", "at", "v0", "v1", "a0", "a1", "a2", "a3",
    "t0",   "t1", "t2", "t3", "t4", "t5", "t6", "t7",
    "s0",   "s1", "s2", "s3", "s4", "s5", "s6", "s7",
    "t8",   "t9", "k0", "k1", "gp", "sp", "fp", "ra"
]


MIPS_instruction_table = {
    # R-Type
    "add": {"type": "R", "opcode": 0x00, "function": 0x20},
    "addu": {"type": "R", "opcode": 0x00, "function": 0x21},
    "and": {"type": "R", "opcode": 0x00, "function": 0x24},
    "div": {"type": "R", "opcode": 0x00, "function": 0x1a},
    "divu": {"type": "R", "opcode": 0x00, "function": 0x1b},
    "jalr": {"type": "R", "opcode": 0x00, "function": 0x09},
    "jr": {"type": "R", "opcode": 0x00, "function": 0x08},
    "mfhi": {"type": "R", "opcode": 0x00, "function": 0x10},
    "mflo": {"type": "R", "opcode": 0x00, "function": 0x12},
    "mthi": {"type": "R", "opcode": 0x00, "function": 0x11},
    "mtlo": {"type": "R", "opcode": 0x00, "function": 0x13},
    "mult": {"type": "R", "opcode": 0x00, "function": 0x18},
    "multu": {"type": "R", "opcode": 0x00, "function": 0x19},
    "nor": {"type": "R", "opcode": 0x00, "function": 0x27},
    "or": {"type": "R", "opcode": 0x00, "function": 0x25},
    "sll": {"type": "R", "opcode": 0x00, "function": 0x00},
    "sllv": {"type": "R", "opcode": 0x00, "function": 0x04},
    "slt": {"type": "R", "opcode": 0x00, "function": 0x2a},
    "sltu": {"type": "R", "opcode": 0x00, "function": 0x2b},
    "sra": {"type": "R", "opcode": 0x00, "function": 0x03},
    "srav": {"type": "R", "opcode": 0x00, "function": 0x07},
    "srl": {"type": "R", "opcode": 0x00, "function": 0x02},
    "srlv": {"type": "R", "opcode": 0x00, "function": 0x06},
    "sub": {"type": "R", "opcode": 0x00, "function": 0x22},
    "subu": {"type": "R", "opcode": 0x00, "function": 0x23},
    "syscall": {"type": "R", "opcode": 0x00, "function": 0x0c},
    "xor": {"type": "R", "opcode": 0x00, "function": 0x26},

    # I-type
    "addi": {"type": "I", "opcode": 0x08},
    "addiu": {"type": "I", "opcode": 0x09},
    "andi": {"type": "I", "opcode": 0x0c},
    "beq": {"type": "I", "opcode": 0x04},
    "bgez": {"type": "I", "opcode": 0x01, "rt": 0x01},
    "bgtz": {"type": "I", "opcode": 0x07, "rt": 0x00},
    "blez": {"type": "I", "opcode": 0x06, "rt": 0x00},
    "bltz": {"type": "I", "opcode": 0x01, "rt": 0x00},
    "bltzal": {"type": "I", "opcode": 0x01, "rt": 0x10},
    "bne": {"type": "I", "opcode": 0x05},
    "lb": {"type": "I", "opcode": 0x20},
    "lbu": {"type": "I", "opcode": 0x24},
    "lh": {"type": "I", "opcode": 0x21},
    "lhu": {"type": "I", "opcode": 0x25},
    "lui": {"type": "I", "opcode": 0x0f},
    "lw": {"type": "I", "opcode": 0x23},
    "ori": {"type": "I", "opcode": 0x0d},
    "sb": {"type": "I", "opcode": 0x28},
    "sh": {"type": "I", "opcode": 0x29},
    "slti": {"type": "I", "opcode": 0x0a},
    "sltiu": {"type": "I", "opcode": 0x0b},
    "sw": {"type": "I", "opcode": 0x2b},
    "xori": {"type": "I", "opcode": 0x0e},
    "lwl": {"type": "I", "opcode": 0x22},
    "lwr": {"type": "I", "opcode": 0x26},
    "swl": {"type": "I", "opcode": 0x2a},
    "swr": {"type": "I", "opcode": 0x2e},

    # J-type
    "j": {"type": "J", "opcode": 0x02},
    "jal": {"type": "J", "opcode": 0x03}
}

R_type = {"opcode", "rs", "rt", "rd", "sa", "function"}
I_type = {"opcode", "rs", "rt", "imm"}
J_type = {"opcode", "imm"}

# xxx rd, rs, rt
type1 = {
    "add": {"opcode": 0x00, "function": 0x20},
    "addu": {"opcode": 0x00, "function": 0x21},
    "and": {"opcode": 0x00, "function": 0x24},
    "nor": {"opcode": 0x00, "function": 0x27},
    "or": {"opcode": 0x00, "function": 0x25},
    "slt": {"opcode": 0x00, "function": 0x2a},
    "sltu": {"opcode": 0x00, "function": 0x2b},
    "sub": {"opcode": 0x00, "function": 0x22},
    "subu": {"opcode": 0x00, "function": 0x23},
    "xor": {"opcode": 0x00, "function": 0x26},
}

# xxx rt, rs, imm
type2 = {
    "addi": {"opcode": 0x08},
    "addiu": {"opcode": 0x09},
    "andi": {"opcode": 0x0c},
    "slti": {"opcode": 0x0a},
    "sltiu": {"opcode": 0x0b},
    "ori": {"opcode": 0x0d},
    "xori": {"opcode": 0x0e},
}

# xxx rd, rs
type3 = {
    "jalr": {"opcode": 0x00, "function": 0x09},
}

# xxx rs, rt
type4 = {
    "div": {"opcode": 0x00, "function": 0x1a},
    "divu": {"opcode": 0x00, "function": 0x1b},
    "mult": {"opcode": 0x00, "function": 0x18},
    "multu": {"opcode": 0x00, "function": 0x19},
}

# xxx rd, rt, sa
type5 = {
    "sll": {"opcode": 0x00, "function": 0x00},
    "sra": {"opcode": 0x00, "function": 0x03},
    "srl": {"opcode": 0x00, "function": 0x02},
}

# xxx rs, rt, label
type6 = {
    "beq": {"opcode": 0x04},
    "bne": {"opcode": 0x05},
}

# xxx rs, label
type7 = {
    "bgez": {"opcode": 0x01, "rt": 0x01},
    "bgtz": {"opcode": 0x07, "rt": 0x00},
    "blez": {"opcode": 0x06, "rt": 0x00},
    "bltz": {"opcode": 0x01, "rt": 0x00},

}

# xxx label
type8 = {
    "j": {"opcode": 0x02},
    "jal": {"opcode": 0x03}
}

# xxx rs
type9 = {
    "jr": {"opcode": 0x00, "function": 0x08},
    "mthi": {"opcode": 0x00, "function": 0x11},
    "mtlo": {"opcode": 0x00, "function": 0x13},
}

# xxx rd
type10 = {
    "mfhi": {"opcode": 0x00, "function": 0x10},
    "mflo": {"opcode": 0x00, "function": 0x12},
}

# xxx rt, address
type11 = {
    "lb": {"opcode": 0x20},
    "lbu": {"opcode": 0x24},
    "lh": {"opcode": 0x21},
    "lhu": {"opcode": 0x25},
    "lw": {"opcode": 0x23},
    "sb": {"opcode": 0x28},
    "sh": {"opcode": 0x29},
    "sw": {"opcode": 0x2b},
    "lwl": {"opcode": 0x22},
    "lwr": {"opcode": 0x26},
    "swl": {"opcode": 0x2a},
    "swr": {"opcode": 0x2e},
}

# xxx rt, imm
type12 = {
    "lui": {"opcode": 0x0f},
}

type_list = [type1, type2, type3, type4, type5, type6,
             type7, type8, type9, type10, type11, type12]
