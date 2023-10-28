import os
import struct
from enum import Enum


MEMORY_SIZE = 6 * 1024 * 1024  # 6291456
TEXT_SIZE = 1 * 1024 * 1024
STARTING_ADDRESS = 0x400000
STATIC_DATA = 0

prog = bytearray(MEMORY_SIZE)
reg = [0] * (32 + 3)
sp = 0xA00000
gp = 0x508000
pc = STARTING_ADDRESS
machine_code_size = 0
my_ins = []
checkpoints = set()
# to_exit = False


REGS = {
    "_zero": 0,
    "_at": 1,
    "_v0": 2,
    "_v1": 3,
    "_a0": 4,
    "_a1": 5,
    "_a2": 6,
    "_a3": 7,
    "_t0": 8,
    "_t1": 9,
    "_t2": 10,
    "_t3": 11,
    "_t4": 12,
    "_t5": 13,
    "_t6": 14,
    "_t7": 15,
    "_s0": 16,
    "_s1": 17,
    "_s2": 18,
    "_s3": 19,
    "_s4": 20,
    "_s5": 21,
    "_s6": 22,
    "_s7": 23,
    "_t8": 24,
    "_t9": 25,
    "_k0": 26,
    "_k1": 27,
    "_gp": 28,
    "_sp": 29,
    "_fp": 30,
    "_ra": 31,
    "_pc": 32,
    "_hi": 33,
    "_lo": 34
}


def ignore_label(line):
    found = line.find(":")
    if found != -1:
        line = line[found + 1:]
    return line


def ignore_comment(line):
    found = line.find("#")
    if found != -1:
        line = line[:found]
    return line


def remove_front_space(line):
    while line and (line[0].isspace() or line[0] == '\t'):
        line = line[1:]
    return line


def remove_back_space(line):
    while line and (line[-1].isspace() or line[-1] == '\t'):
        line = line[:-1]
    return line


def remove_sub_string(sub, line):
    found = line.find(sub)
    if found != -1:
        line = line[found + len(sub):]
    return line


def get_char(ch):
    # Using a dictionary to simulate a switch-case statement
    char_map = {
        '\\': '\\',
        '\'': '\'',
        '\?': '\?',
        't': '\t',
        'n': '\n',
        'a': '\a',
        'b': '\b',
        'f': '\f',
        'r': '\r',
        'v': '\v'
    }
    # Returning the corresponding value if it exists in the dictionary, otherwise returning the original character
    return char_map.get(ch, ch)


def bin_to_num(binary_str):
    result = 0
    for c in binary_str:
        result <<= 1
        result |= int(c)
    return result


def to_binary(num, length):
    binary_str = ""
    while num:
        binary_str = ('1' if num & 1 else '0') + binary_str
        num >>= 1
    binary_str = binary_str.zfill(length)
    return binary_str


def to_hex(num, length):
    hex_str = format(num, 'x')
    hex_str = hex_str.zfill(length)
    return hex_str


def _add(rs, rt, rd):
    reg[rd] = reg[rs] + reg[rt]
    print("--add--", reg[rs], reg[rt], reg[rd])


def _addu(rs, rt, rd):
    reg[rd] = reg[rs] + reg[rt]
    print("--addu--", reg[rs], reg[rt], reg[rd])


def _and(rs, rt, rd):
    reg[rd] = reg[rs] & reg[rt]
    print("--and--", reg[rs], reg[rt], reg[rd])


def _div(rs, rt):
    reg[REGS.get("_lo")] = int(reg[rs] / reg[rt])
    reg[REGS.get("_hi")] = int(reg[rs] % reg[rt])
    print("--div--", reg[rs], reg[rt],
          reg[REGS.get("_lo")], reg[REGS.get("_hi")])


def _divu(rs, rt):
    reg[REGS.get("_lo")] = reg[rs] / reg[rt]
    reg[REGS.get("_hi")] = reg[rs] % reg[rt]
    print("--divu--", reg[rs], reg[rt],
          reg[REGS.get("_lo")], reg[REGS.get("_hi")])


def _jalr(rs, rd):
    reg[rd] = reg[REGS.get("_pc")]
    reg[REGS.get("_pc")] = reg[rs]
    print("--jalr--", reg[rs], reg[rd], reg[REGS.get("_pc")])


def _jr(rs):
    reg[REGS.get("_pc")] = reg[rs]
    print("--jr--", reg[rs], reg[REGS.get("_pc")])


def _mfhi(rd):
    reg[rd] = reg[REGS.get("_hi")]
    print("--mfhi--", reg[REGS.get("_hi")], reg[rd])


def _mflo(rd):
    reg[rd] = reg[REGS.get("_lo")]
    print("--mflo--", reg[REGS.get("_lo")], reg[rd])


def _mthi(rs):
    reg[REGS.get("_hi")] = reg[rs]
    print("--mthi--", reg[rs], reg[REGS.get("_hi")])


def _mtlo(rs):
    reg[REGS.get("_lo")] = reg[rs]
    print("--mtlo--", reg[rs], reg[REGS.get("_lo")])


def _mult(rt, rs):
    rst = reg[rs] * reg[rt]
    reg[REGS.get("_hi")] = int(rst >> 32)
    reg[REGS.get("_lo")] = int(rst & 0xffffffff)
    print("--mult--", reg[rs], reg[rt],
          reg[REGS.get("_hi")], reg[REGS.get("_lo")])


def _multu(rs, rt):
    rst = reg[rs] * reg[rt]
    reg[REGS.get("_hi")] = int(rst >> 32)
    reg[REGS.get("_lo")] = int(rst & 0xffffffff)
    print("--multu--", reg[rs], reg[rt],
          reg[REGS.get("_hi")], reg[REGS.get("_lo")])


def _nor(rs, rt, rd):
    reg[rd] = ~(reg[rs] | reg[rt])
    print("--nor--", reg[rs], reg[rt], reg[rd])


def _or(rs, rt, rd):
    reg[rd] = reg[rs] | reg[rt]
    print("--or--", reg[rs], reg[rt], reg[rd])


def _sll(rd, rt, sa):
    reg[rd] = reg[rt] << sa
    print("--sll--", reg[rt], sa, reg[rd])


def _sllv(rd, rs, rt):
    reg[rd] = reg[rt] << reg[rs]
    print("--sllv--", reg[rt], reg[rs], reg[rd])


def _slt(rd, rs, rt):
    reg[rd] = 1 if int(reg[rs]) < int(reg[rt]) else 0
    print("--slt--", reg[rs], reg[rt], reg[rd])


def _sltu(rd, rs, rt):
    reg[rd] = 1 if reg[rs] < reg[rt] else 0
    print("--sltu--", reg[rs], reg[rt], reg[rd])


def _sra(rd, rt, sa):
    sign_bit = 0x80000000 & reg[rt]
    reg[rd] = reg[rt] >> sa
    if sign_bit:
        for i in range(min(32, sa)):
            reg[rd] |= sign_bit >> i
    print("--sra--", reg[rt], sa, reg[rd])


def _srav(rd, rs, rt):
    sign_bit = 0x80000000 & reg[rt]
    reg[rd] = reg[rt] >> reg[rs]
    if sign_bit:
        for i in range(min(32, reg[rs])):
            reg[rd] |= sign_bit >> i
    print("--srav--", reg[rt], reg[rs], reg[rd])


def _srl(rd, rt, sa):
    reg[rd] = reg[rt] >> sa
    print("--srl--", reg[rt], sa, reg[rd])


def _srlv(rd, rs, rt):
    reg[rd] = reg[rt] >> reg[rs]
    print("--srlv--", reg[rt], reg[rs], reg[rd])


def _sub(rd, rs, rt):
    reg[rd] = reg[rs] - reg[rt]
    print("--sub--", reg[rs], reg[rt], reg[rd])


def _subu(rd, rs, rt):
    reg[rd] = reg[rs] - reg[rt]
    print("--subu--", reg[rs], reg[rt], reg[rd])


def _xor(rd, rs, rt):
    reg[rd] = reg[rs] ^ reg[rt]
    print("--xor--", reg[rs], reg[rt], reg[rd])


def _addi(rt, rs, imm):
    if imm & 0x8000:
        imm = imm - 0x10000
    reg[rt] = reg[rs] + imm
    print("--addi--", reg[rs], imm, reg[rt])


def _addiu(rt, rs, imm):
    reg[rt] = reg[rs] + imm
    print("--addiu--", reg[rs], imm, reg[rt])


def _andi(rt, rs, imm):
    reg[rt] = reg[rs] & (imm & 0xffff)
    print("--andi--", reg[rs], imm, reg[rt])


def _beq(rs, rt, imm):
    if reg[rs] == reg[rt]:
        reg[REGS.get("_pc")] += imm * 4
        print("--beq--", reg[rs], reg[rt], imm, reg[REGS.get("_pc")])


def _bgez(rs, imm):
    if int(reg[rs]) >= 0:
        reg[REGS.get("_pc")] += imm * 4
        print("--bgez--", reg[rs], imm, reg[REGS.get("_pc")])


def _bgtz(rs, imm):
    if int(reg[rs]) > 0:
        reg[REGS.get("_pc")] += imm * 4
        print("--bgtz--", reg[rs], imm, reg[REGS.get("_pc")])


def _blez(rs, imm):
    if int(reg[rs]) <= 0:
        reg[REGS.get("_pc")] += imm * 4
        print("--blez--", reg[rs], imm, reg[REGS.get("_pc")])


def _bltz(rs, imm):
    if int(reg[rs]) < 0:
        reg[REGS.get("_pc")] += imm * 4
        print("--bltz--", reg[rs], imm, reg[REGS.get("_pc")])


def _bne(rs, rt, imm):
    if reg[rs] != reg[rt]:
        reg[REGS.get("_pc")] += imm * 4
        print("--bne--", reg[rs], reg[rt], imm, reg[REGS.get("_pc")])


def _lb(rt, rs, imm):
    reg[rt] = int(prog[reg[rs] + imm - STARTING_ADDRESS])
    print("--lb--", reg[rs], imm, reg[rt])


def _lbu(rt, rs, imm):
    reg[rt] = prog[reg[rs] + imm - STARTING_ADDRESS]
    print("--lbu--", reg[rs], imm, reg[rt])


def _lh(rs, rt, imm):
    hi = prog[reg[rs] + imm - STARTING_ADDRESS + 1]
    lo = prog[reg[rs] + imm - STARTING_ADDRESS]
    reg[rt] = lo | (hi << 8)
    if hi & 0x80:
        reg[rt] |= 0xffff << 16
    print("--lh--", reg[rs], imm, reg[rt])


def _lhu(rs, rt, imm):
    hi = prog[reg[rs] + imm - STARTING_ADDRESS + 1]
    lo = prog[reg[rs] + imm - STARTING_ADDRESS]
    reg[rt] = lo | (hi << 8)
    print("--lhu--", reg[rs], imm, reg[rt])


def _lui(rt, imm):
    reg[rt] = imm << 16
    print("--lui--", imm, reg[rt])


def _lw(rs, rt, imm):
    idx = reg[rs] + imm - STARTING_ADDRESS
    base = bytearray(prog[idx:idx + 4])  # 获取prog中的4个字节作为bytearray
    reg[rt] = base[0] | (base[1] << 8) | (base[2] << 16) | (base[3] << 24)
    print("--lw--", reg[rs], imm, reg[rt])


def _ori(rs, rt, imm):
    reg[rt] = reg[rs] | imm
    print("--ori--", reg[rs], imm, reg[rt])


def _sb(rs, rt, imm):
    prog[reg[rs] + imm - STARTING_ADDRESS] = reg[rt] & 0xff
    print("--sb--", reg[rs], reg[rt], imm)


def _slti(rs, rt, imm):
    reg[rt] = 1 if int(reg[rs]) < imm else 0
    print("--slti--", reg[rs], imm, reg[rt])


def _sltiu(rs, rt, imm):
    reg[rt] = 1 if reg[rs] < imm else 0
    print("--sltiu--", reg[rs], imm, reg[rt])


def _sh(rs, rt, imm):
    base = prog + reg[rs] + imm - STARTING_ADDRESS
    base[0] = reg[rt] & 0xff
    base[1] = reg[rt] >> 8
    print("--sh--", reg[rs], reg[rt], imm)


def _sw(rs, rt, imm):
    imm = imm & 0xFFFF
    if imm & 0x8000:
        imm = imm - 0x10000
    print("--sw--", reg[rs], reg[rt], imm)
    base_index = reg[rs] + imm - STARTING_ADDRESS
    prog[base_index] = reg[rt] & 0xff
    prog[base_index + 1] = (reg[rt] >> 8) & 0xff
    prog[base_index + 2] = (reg[rt] >> 16) & 0xff
    prog[base_index + 3] = (reg[rt] >> 24) & 0xff


def _xori(rs, rt, imm):
    reg[rt] = reg[rs] ^ imm
    print("--xori--", reg[rs], imm, reg[rt])


def _lwl(rs, rt, imm):
    idx = reg[rs] + imm - STARTING_ADDRESS
    lower_bound = idx & (~3)
    for i in range(idx, lower_bound - 1, -1):
        reg[rt] &= ~(0xff << (i % 4) * 8)
        reg[rt] |= prog[i] << (i % 4) * 8
    print("--lwl--", reg[rs], imm, reg[rt])


def _lwr(rs, rt, imm):
    idx = reg[rs] + imm - STARTING_ADDRESS
    upper_bound = (idx + 4) & (~3)
    for i in range(idx, upper_bound):
        reg[rt] &= ~(0xff << (i % 4) * 8)
        reg[rt] |= prog[i] << (i % 4) * 8
    print("--lwr--", reg[rs], imm, reg[rt])


def _swl(rs, rt, imm):
    idx = reg[rs] + imm - STARTING_ADDRESS
    lower_bound = idx & (~3)
    for i in range(idx, lower_bound - 1, -1):
        prog[i] = (reg[rt] >> (i % 4) * 8) & 0xff
    print("--swl--", reg[rs], imm, reg[rt])


def _swr(rs, rt, imm):
    idx = reg[rs] + imm - STARTING_ADDRESS
    upper_bound = (idx + 4) & (~3)
    for i in range(idx, upper_bound):
        prog[i] = (reg[rt] >> (i % 4) * 8) & 0xff
    print("--swr--", reg[rs], reg[rt], imm, prog)


def _j(target):
    reg[REGS.get("_pc")] &= 0xf0000000
    reg[REGS.get("_pc")] |= target << 2
    print("--j--", target, reg[REGS.get("_pc")])


def _jal(target):
    reg[REGS.get("_ra")] = reg[REGS.get("_pc")]
    reg[REGS.get("_pc")] &= 0xf0000000
    reg[REGS.get("_pc")] |= target << 2
    print("--jal--", target, reg[REGS.get("_ra")], reg[REGS.get("_pc")])


def _print_int(fout):
    fout.write(str(int(reg[REGS.get("_a0")])))
    fout.flush()


def _print_string(fout):
    print("--print string--", reg[REGS.get("_a0")] - STARTING_ADDRESS)
    start_address = reg[REGS.get("_a0")] - STARTING_ADDRESS
    fout.write(bytearray(prog[start_address:]).decode(
        'utf-8', errors='replace'))
    fout.flush()


def _read_int(fin):
    line = fin.readline().strip()
    if line:
        print("--read int--", line)
        reg[REGS.get("_v0")] = int(line)
    else:
        print("--read int--", "empty line")


def _read_string(fin):
    str_len = reg[REGS.get("_a1")]
    str_input = fin.read(str_len)
    prog[reg[REGS.get("_a0")] - STARTING_ADDRESS:reg[REGS.get("_a0")] -
         STARTING_ADDRESS + str_len] = str_input


def _sbrk():
    global STATIC_DATA
    reg[REGS.get("_v0")] = STARTING_ADDRESS + STATIC_DATA + TEXT_SIZE
    STATIC_DATA += reg[REGS.get("_a0")]


def _exit(to_exit):
    print("--exit--", reg[REGS.get("_a0")])
    to_exit = True
    return 0


def _print_char(fout):
    print("--print char--")
    fout.write(chr(reg[REGS.get("_a0")]))
    fout.flush()


def _read_char(fin):
    print("--read char--")
    reg[REGS.get("_v0")] = ord(fin.read(1))


def _open():
    print("--open--")
    reg[REGS.get("_a0")] = os.open(prog + reg[REGS.get("_a0")] -
                                   STARTING_ADDRESS, reg[REGS.get("_a1")], reg[REGS._a2])


def _read():
    print("--read--")
    reg[REGS.get("_a0")] = os.read(reg[REGS.get("_a0")], prog +
                                   reg[REGS.get("_a1")] - STARTING_ADDRESS, reg[REGS._a2])


def _write():
    print("--write--")
    reg[REGS.get("_a0")] = os.write(reg[REGS.get("_a0")], prog +
                                    reg[REGS.get("_a1")] - STARTING_ADDRESS, reg[REGS._a2])


def _close():
    print("--close--")
    os.close(reg[REGS.get("_a0")])


def _exit2(to_exit):
    print("--exit2--", reg[REGS.get("_a0")])
    to_exit = True
    return reg[REGS.get("_a0")]


def _syscall(fin, fout, to_exit, return_val):
    print("--sys--", REGS.get("_v0"))
    syscall_number = reg[int(REGS.get("_v0"))]
    print("--sys num--", reg[REGS.get("_v0")])

    if syscall_number == 1:
        _print_int(fout)
    elif syscall_number == 4:
        _print_string(fout)
    elif syscall_number == 5:
        _read_int(fin)
    elif syscall_number == 8:
        _read_string(fin)
    elif syscall_number == 9:
        _sbrk()
    elif syscall_number == 10:
        return_val = _exit(to_exit)
        return [True, return_val]
    elif syscall_number == 11:
        _print_char(fout)
    elif syscall_number == 12:
        _read_char(fin)
    elif syscall_number == 13:
        _open()
    elif syscall_number == 14:
        _read()
    elif syscall_number == 15:
        _write()
    elif syscall_number == 16:
        _close()
    elif syscall_number == 17:
        return_val = _exit2(to_exit)
        return [True, return_val]
    else:
        return []
