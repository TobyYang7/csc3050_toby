import os
import struct
from enum import Enum


MEMORY_SIZE = 6 * 1024 * 1024  # 6291456
TEXT_SIZE = 1 * 1024 * 1024
STARTING_ADDRESS = 0x400000
STATIC_DATA = 0

mem = bytearray(MEMORY_SIZE)
reg = [0] * (32 + 3)
sp = 0xA00000
gp = 0x508000
pc = STARTING_ADDRESS
machine_code_size = 0
my_ins = []
checkpoints = set()
count = 0
out_file = []


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
    if imm & 0x8000:
        imm = imm - 0x10000
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
    if imm & 0x8000:
        imm = imm - 0x10000
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
    reg[rt] = int(mem[reg[rs] + imm - STARTING_ADDRESS])
    print("--lb--", reg[rs], imm, reg[rt])


def _lbu(rt, rs, imm):
    reg[rt] = mem[reg[rs] + imm - STARTING_ADDRESS]
    print("--lbu--", reg[rs], imm, reg[rt])


def _lh(rs, rt, imm):
    hi = mem[reg[rs] + imm - STARTING_ADDRESS + 1]
    lo = mem[reg[rs] + imm - STARTING_ADDRESS]
    reg[rt] = lo | (hi << 8)
    if hi & 0x80:
        reg[rt] |= 0xffff << 16
    print("--lh--", reg[rs], imm, reg[rt])


def _lhu(rs, rt, imm):
    hi = mem[reg[rs] + imm - STARTING_ADDRESS + 1]
    lo = mem[reg[rs] + imm - STARTING_ADDRESS]
    reg[rt] = lo | (hi << 8)
    print("--lhu--", reg[rs], imm, reg[rt])


def _lui(rt, imm):  # fix
    print("--lui--", imm, reg[rt])
    imm = imm << 16
    reg[rt] = imm


def _lw(rs, rt, imm):
    idx = reg[rs] + imm - STARTING_ADDRESS
    base = bytearray(mem[idx:idx + 4])  # 获取prog中的4个字节作为bytearray
    reg[rt] = base[0] | (base[1] << 8) | (base[2] << 16) | (base[3] << 24)
    print("--lw--", reg[rs], imm, reg[rt])


def _ori(rs, rt, imm):
    reg[rt] = reg[rs] | imm
    print("--ori--", reg[rs], imm, reg[rt])


def _sb(rs, rt, imm):
    mem[reg[rs] + imm - STARTING_ADDRESS] = reg[rt] & 0xff
    print("--sb--", reg[rs], reg[rt], imm)


def _slti(rs, rt, imm):
    reg[rt] = 1 if int(reg[rs]) < imm else 0
    print("--slti--", reg[rs], imm, reg[rt])


def _sltiu(rs, rt, imm):
    reg[rt] = 1 if reg[rs] < imm else 0
    print("--sltiu--", reg[rs], imm, reg[rt])


def _sh(rs, rt, imm):
    base = mem + reg[rs] + imm - STARTING_ADDRESS
    base[0] = reg[rt] & 0xff
    base[1] = reg[rt] >> 8
    print("--sh--", reg[rs], reg[rt], imm)


def _sw(rs, rt, imm):
    imm = imm & 0xFFFF
    if imm & 0x8000:
        imm = imm - 0x10000
    print("--sw--", reg[rs], reg[rt], imm)
    base_index = reg[rs] + imm - STARTING_ADDRESS
    mem[base_index] = reg[rt] & 0xff
    mem[base_index + 1] = (reg[rt] >> 8) & 0xff
    mem[base_index + 2] = (reg[rt] >> 16) & 0xff
    mem[base_index + 3] = (reg[rt] >> 24) & 0xff


def _xori(rs, rt, imm):
    reg[rt] = reg[rs] ^ imm
    print("--xori--", reg[rs], imm, reg[rt])


def _lwl(rs, rt, imm):
    idx = reg[rs] + imm - STARTING_ADDRESS
    lower_bound = idx & (~3)
    for i in range(idx, lower_bound - 1, -1):
        reg[rt] &= ~(0xff << (i % 4) * 8)
        reg[rt] |= mem[i] << (i % 4) * 8
    print("--lwl--", reg[rs], imm, reg[rt])


def _lwr(rs, rt, imm):
    idx = reg[rs] + imm - STARTING_ADDRESS
    upper_bound = (idx + 4) & (~3)
    for i in range(idx, upper_bound):
        reg[rt] &= ~(0xff << (i % 4) * 8)
        reg[rt] |= mem[i] << (i % 4) * 8
    print("--lwr--", reg[rs], imm, reg[rt])


def _swl(rs, rt, imm):
    idx = reg[rs] + imm - STARTING_ADDRESS
    lower_bound = idx & (~3)
    for i in range(idx, lower_bound - 1, -1):
        mem[i] = (reg[rt] >> (i % 4) * 8) & 0xff
    print("--swl--", reg[rs], imm, reg[rt])


def _swr(rs, rt, imm):
    idx = reg[rs] + imm - STARTING_ADDRESS
    upper_bound = (idx + 4) & (~3)
    for i in range(idx, upper_bound):
        mem[i] = (reg[rt] >> (i % 4) * 8) & 0xff
    print("--swr--", reg[rs], reg[rt], imm, mem)


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
    print("--print int--", int(reg[REGS.get("_a0")]))
    out_file.append(str(int(reg[REGS.get("_a0")])))
    fout.write(str(int(reg[REGS.get("_a0")])).encode('ascii'))
    fout.flush()


def _print_string(fout):
    global out_file

    start_address = reg[REGS.get("_a0")] - STARTING_ADDRESS

    # Finding the null terminator of the string
    end_address = start_address

    char_count = 0
    while mem[end_address] != 0:
        print("this char in: ", hex(end_address), repr(chr(mem[end_address])))
        end_address += 1
        char_count += 1
    print("total char: ", char_count)

    string_to_write = mem[start_address:end_address]

    print("--print string--", hex(start_address), hex(end_address))

    print(string_to_write.decode('utf-8'))
    out_file.append(string_to_write.decode('utf-8'))
    fout.write(string_to_write)
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
    print("--read string--", str_input)
    byte_array = bytearray(str_input.encode('utf-8'))
    # prog_start = reg[REGS.get("_a0")] - STARTING_ADDRESS
    # prog_end = prog_start + len(byte_array)
    # mem[prog_start:prog_end] = byte_array
    buffer = reg[REGS.get("_a0")] - STARTING_ADDRESS
    mem[buffer:buffer + str_len] = byte_array


def _sbrk():
    global STATIC_DATA
    print("--sbrk--")
    reg[REGS.get("_v0")] = STARTING_ADDRESS + STATIC_DATA + TEXT_SIZE
    STATIC_DATA += reg[REGS.get("_a0")]


def _exit(to_exit):
    print("--exit--", reg[REGS.get("_a0")])
    to_exit = True
    return 0


def _print_char(fout):
    print("--print char--")
    out_file.append(chr(reg[REGS.get("_a0")]))
    fout.write(chr(reg[REGS.get("_a0")]).encode('ascii'))
    fout.flush()


def _read_char(fin):
    print("--read char--")
    reg[REGS.get("_v0")] = ord(fin.read(1))


def _open():
    file_name_address = reg[REGS.get("_a0")]
    start_idx = file_name_address - STARTING_ADDRESS
    file_name = bytearray(mem[start_idx:])

    # Find the null terminator in the bytearray
    null_idx = file_name.find(0)  # fix: 54
    if null_idx != -1:
        tmp = file_name[:null_idx]
        print("--open--", tmp)
        file_name = tmp.decode('utf-8')
    else:
        file_name = file_name.decode('utf-8')

    flag = reg[REGS.get("_a1")]
    mode = reg[REGS.get("_a2")]
    print("--open--", file_name, flag, mode)
    file_descriptor = os.open(file_name, flag, mode)
    reg[REGS.get("_a0")] = file_descriptor


def _read():  # fix
    fd = reg[REGS.get("_a0")]
    buffer = reg[REGS.get("_a1")] - STARTING_ADDRESS
    length = reg[REGS.get("_a2")]

    # print("--read--", hex(file_descriptor), hex(buffer_address))

    # if file_descriptor == 0:  # 标准输入
    #     input_data = os.read(0, size)  # 从标准输入读取数据
    #     mem[buffer_address - STARTING_ADDRESS: buffer_address -
    #         STARTING_ADDRESS + len(input_data)] = input_data
    #     reg[REGS.get("_v0")] = len(input_data)
    # elif file_descriptor == 1 or file_descriptor == 2:  # 防止尝试从标准输出或标准错误读取
    #     reg[REGS.get("_v0")] = -1
    # else:
    #     buffer_data = bytes(mem[buffer_address - STARTING_ADDRESS:])

    input_data = os.read(fd, length)

    mem[buffer:buffer + length] = input_data


# def _read():
#     _a0 = REGS.get("_a0")
#     _a1 = REGS.get("_a1")
#     _a2 = REGS.get("_a2")

#     if None in (_a0, _a1, _a2):
#         print("Error: Registers _a0, _a1, or _a2 not found in REGS.")
#         return

#     # Calculate the buffer offset
#     buffer_offset = _a1 - STARTING_ADDRESS

#     # Calculate the position in the memory (bytearray)
#     data_position = buffer_offset

#     # Ensure the position and length are valid
#     if data_position < 0 or data_position + _a2 > len(mem):
#         print("Error: Invalid data position or length.")
#         return

#     # Create a bytes object to store the read data
#     data_read = bytearray(_a2)

#     # Read the data and update the register
#     bytes_read = os.read(_a0, data_read)
#     REGS[_a0] = bytes_read

#     # Store the read data back to the simulated memory (prog)
#     mem[data_position:data_position+bytes_read] = data_read[:bytes_read]


def _write():
    fd = REGS.get("_a0")
    buffer = reg[REGS.get("_a1")] - STARTING_ADDRESS
    length = reg[REGS.get("_a2")]

    print("--write--")
    print(fd, buffer, length)

    data = mem[buffer:buffer + length]
    reg[REGS.get("_a0")] = os.write(fd, data)


def _close():
    _a0 = REGS.get("_a0")
    fd = reg[_a0]

    print("--close--", hex(fd))
    os.close(fd)


def _exit2(to_exit):
    print("--exit2--", reg[REGS.get("_a0")])
    to_exit = True
    return reg[REGS.get("_a0")]


def _syscall(fin, fout, to_exit, return_val):
    syscall_number = reg[int(REGS.get("_v0"))]
    print("====syscall====", reg[REGS.get("_v0")])

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


def init_checkpoints(checkpoint_file):
    with open(checkpoint_file, "r") as fp:
        for line in fp:
            checkpoints.add(int(line.strip()))


def checkpoint_memory(ins_count):
    if ins_count not in checkpoints:
        # print("--mem count not in--", ins_count)
        return
    # print("--mem change--", ins_count)
    name = f"memory_{ins_count}.bin"
    with open(name, "wb") as fp:
        fp.write(mem[:0x600000])


def checkpoint_register(ins_count):
    if ins_count not in checkpoints:
        return
    # print("--reg change--", ins_count)
    name = f"register_{ins_count}.bin"
    with open(name, "wb") as fp:
        fp.write(struct.pack('i' * len(reg), *reg))


def data_handler(file_name):
    global STATIC_DATA, mem

    infile = open(file_name, 'r')
    line = ""
    data_type = ""
    nums = []
    num = 0
    length = 0
    end = 0
    contin_bs = 0
    at_dot_data = False
    at_dot_text = False

    # if infile.fail():
    #     print(f"Fail to open {file_name}")
    #     infile.close()
    #     return

    while line := infile.readline():
        line = ignore_label(line)
        line = ignore_comment(line)
        line = line.strip()

        if ".data" in line:
            print(">>data>>")
            at_dot_data = True
            continue

        if ".text" in line:
            print(">>text>>")
            at_dot_text = True
            break

        if at_dot_data and not at_dot_text:
            data_type = line[:line.find("\"")]

            if ".asciiz" in data_type:
                print(">>asciiz>>")
                line = line[line.find("\"") + 1:]
                end = 0

                for i in range(len(line) - 1, -1, -1):
                    if line[i] == '\"':
                        end = i
                        break

                line = line[:end]
                length = 0
                contin_bs = 0

                for i in range(len(line) - 1):
                    if line[i] == '\\' and line[i + 1] == '\\':
                        contin_bs += 1
                        if contin_bs % 2 == 1:
                            continue
                        else:
                            mem[TEXT_SIZE + STATIC_DATA + length] = line[i]
                            length += 1
                            contin_bs = 0
                    elif line[i] == '\\' and line[i + 1] != '\\':
                        contin_bs += 1
                        if contin_bs % 2 == 1:
                            continue
                        else:
                            mem[TEXT_SIZE + STATIC_DATA +
                                length] = get_char(line[i])
                            length += 1
                            contin_bs = 0
                    elif line[i] != '\\':
                        if contin_bs == 0:
                            mem[TEXT_SIZE + STATIC_DATA +
                                length] = ord(line[i])
                            length += 1
                        elif contin_bs != 0:
                            mem[TEXT_SIZE + STATIC_DATA +
                                length] = ord(get_char(line[i]))
                            length += 1
                            contin_bs = 0

                if contin_bs % 2 != 0:
                    print(hex(TEXT_SIZE+STATIC_DATA+length),
                          ord(get_char(line[-1])))
                    mem[TEXT_SIZE + STATIC_DATA +
                        length] = ord(get_char(line[-1]))
                    contin_bs = 0
                elif contin_bs % 2 == 0:
                    print(hex(TEXT_SIZE+STATIC_DATA+length),
                          ord(line[-1]))
                    mem[TEXT_SIZE + STATIC_DATA + length] = ord(line[-1])
                    contin_bs = 0

                length += 1
                mem[TEXT_SIZE + STATIC_DATA + length] = ord('\0')
                length += 1

                if length % 4 == 0:
                    STATIC_DATA += length
                else:
                    STATIC_DATA += length
                    STATIC_DATA += (4 - length % 4)

                continue

            if ".ascii" in data_type:
                print(">>ascii>>")

                line = line[line.find("\"") + 1:]
                end = 0

                for i in range(len(line) - 1, -1, -1):
                    if line[i] == '\"':
                        end = i
                        break

                line = line[:end]
                length = 0
                contin_bs = 0

                for i in range(len(line) - 1):
                    if line[i] == '\\' and line[i + 1] == '\\':
                        contin_bs += 1
                        if contin_bs % 2 == 1:
                            continue
                        else:
                            mem[TEXT_SIZE + STATIC_DATA + length] = line[i]
                            length += 1
                            contin_bs = 0
                    elif line[i] == '\\' and line[i + 1] != '\\':
                        contin_bs += 1
                        if contin_bs % 2 == 1:
                            continue
                        else:
                            mem[TEXT_SIZE + STATIC_DATA +
                                length] = get_char(line[i])
                            length += 1
                            contin_bs = 0
                    elif line[i] != '\\':
                        if contin_bs == 0:
                            mem[TEXT_SIZE + STATIC_DATA +
                                length] = ord(line[i])
                            length += 1
                        elif contin_bs != 0:
                            mem[TEXT_SIZE + STATIC_DATA +
                                length] = get_char(line[i])
                            length += 1
                            contin_bs = 0

                if contin_bs % 2 != 0:
                    print(hex(TEXT_SIZE+STATIC_DATA+length),
                          ord(get_char(line[-1])))
                    mem[TEXT_SIZE + STATIC_DATA +
                        length] = ord(get_char(line[-1]))
                    contin_bs = 0
                elif contin_bs % 2 == 0:
                    print(hex(TEXT_SIZE+STATIC_DATA+length),
                          ord(line[-1]))
                    mem[TEXT_SIZE + STATIC_DATA + length] = line[-1]
                    contin_bs = 0

                length += 1

                if length % 4 == 0:
                    STATIC_DATA += length
                else:
                    STATIC_DATA += length
                    STATIC_DATA += (4 - length % 4)

                continue

            if ".word" in line:
                print(">>word>>")
                line = line[line.find(".word") + 5:].strip()
                nums = line.replace(',', ' ').split()

                for num_str in nums:
                    try:
                        num = int(num_str)
                    except ValueError:
                        print(f"Invalid number: {num_str}")
                        continue
                    print("--word num--", num)

                    ptr_index = TEXT_SIZE + STATIC_DATA
                    if ptr_index + 4 > len(mem):
                        print(
                            f"Not enough space in prog at index {ptr_index} to store the number {num}")
                        continue

                    mem[ptr_index] = num & 0xff
                    mem[ptr_index + 1] = (num >> 8) & 0xff
                    mem[ptr_index + 2] = (num >> 16) & 0xff
                    mem[ptr_index + 3] = (num >> 24) & 0xff
                    STATIC_DATA += 4

            if ".byte" in data_type:
                print(">>byte>>")
                line = line[line.find(".byte") + 6:]
                # ss = line
                nums = line.split(",")

                # while ss:
                #     num, ss = ss.split(maxsplit=1)
                #     nums.append(int(num))

                length = len(nums)

                for i in range(length):
                    mem[TEXT_SIZE + STATIC_DATA] = int(nums[i]) & 0xff
                    STATIC_DATA += 1

                if length % 4 != 0:
                    STATIC_DATA += (4 - length % 4)

                continue

            if ".half" in data_type:
                print(">>half>>")
                line = line[line.find(".half") + 6:]
                # ss = line
                nums = line.split(",")

                # while ss:
                #     num, ss = ss.split(maxsplit=1)
                #     nums.append(int(num))

                length = len(nums)

                for i in range(length):
                    mem[TEXT_SIZE + STATIC_DATA] = int(nums[i]) & 0xff
                    mem[TEXT_SIZE + STATIC_DATA +
                        1] = (int(nums[i]) >> 8) & 0xff
                    STATIC_DATA += 2

                if length % 2 != 0:
                    STATIC_DATA += 2

                continue

    infile.close()


def text_seg(file_name):
    global machine_code_size

    infile = open(file_name, 'r')
    line = ""

    # if infile.fail():
    #     print(f"Fail to open {file_name}")
    #     infile.close()
    #     return

    while line := infile.readline():
        if len(line) < 32:
            continue

        my_ins.append(line)

        for i in range(3, -1, -1):
            mem[machine_code_size + 3 -
                i] = bin_to_num(line[8 * i:8 * (i + 1)])

        machine_code_size += 4

    infile.close()


def execute_cmd(machine_code, infile, outfile, to_exit, return_val):
    global count
    res = []
    op_code = machine_code[:6]
    if op_code == "000000":
        rs = bin_to_num(machine_code[6:11])
        rt = bin_to_num(machine_code[11:16])
        rd = bin_to_num(machine_code[16:21])
        sa = bin_to_num(machine_code[21:26])
        func = bin_to_num(machine_code[26:32])

        # print("=========000000================")
        # print("--rs rt imm--", rs, rt, imm)
        # print(reg)
        # print("--sp--", reg[REGS.get("_sp")])
        # print("===============================")

        switch = {
            0b100000: lambda: _add(rs, rt, rd),
            0b100001: lambda: _addu(rs, rt, rd),
            0b100100: lambda: _and(rs, rt, rd),
            0b011010: lambda: _div(rs, rt),
            0b011011: lambda: _divu(rs, rt),
            0b001001: lambda: _jalr(rs, rd),
            0b001000: lambda: _jr(rs),
            0b010000: lambda: _mfhi(rd),
            0b010010: lambda: _mflo(rd),
            0b010001: lambda: _mthi(rs),
            0b010011: lambda: _mtlo(rs),
            0b011000: lambda: _mult(rt, rs),
            0b011001: lambda: _multu(rt, rs),
            0b100111: lambda: _nor(rs, rt, rd),
            0b100101: lambda: _or(rs, rt, rd),
            0b000000: lambda: _sll(rd, rt, sa),
            0b000100: lambda: _sllv(rd, rs, rt),
            0b101010: lambda: _slt(rd, rs, rt),
            0b101011: lambda: _sltu(rd, rs, rt),
            0b000011: lambda: _sra(rd, rt, sa),
            0b000111: lambda: _srav(rd, rs, rt),
            0b000010: lambda: _srl(rd, rt, sa),
            0b000110: lambda: _srlv(rd, rs, rt),
            0b100010: lambda: _sub(rd, rs, rt),
            0b100011: lambda: _subu(rd, rs, rt),
            0b001100: lambda: _syscall(infile, outfile, to_exit, return_val),
            0b100110: lambda: _xor(rd, rs, rt),
        }

        tmp = switch.get(func, lambda: None)()
        if tmp is not None:
            res = tmp

    elif op_code == "000010" or op_code == "000011":
        target = bin_to_num(machine_code[6:32])

        # print("==========jump=================")
        # print("--rs rt imm--", rs, rt, imm)
        # print(reg)
        # print("--sp--", reg[REGS.get("_sp")])
        # print("===============================")

        if op_code == "000010":
            _j(target)
        else:
            _jal(target)

    else:
        rs = bin_to_num(machine_code[6:11])
        rt = bin_to_num(machine_code[11:16])
        imm = bin_to_num(machine_code[16:32])

        # print("==========case3================")
        print("--rs rt imm--", rs, rt, imm)
        # print(reg)
        # print("--sp--", reg[REGS.get("_sp")])
        # print("===============================")

        switch = {
            0b001000: lambda: _addi(rt, rs, imm),
            0b001001: lambda: _addiu(rs, rs, imm),
            0b001100: lambda: _andi(rt, rs, imm),
            0b000100: lambda: _beq(rs, rt, imm),
            0b000001: lambda: _bgez(rs, imm) if rt == 0b00001 else _bltz(rs, imm) if rt == 0b00000 else None,
            0b000111: lambda: _bgtz(rs, imm),
            0b000110: lambda: _blez(rs, imm),
            0b000101: lambda: _bne(rs, rt, imm),
            0b100000: lambda: _lb(rt, rs, imm),
            0b100100: lambda: _lbu(rt, rs, imm),
            0b100001: lambda: _lh(rs, rt, imm),
            0b100101: lambda: _lhu(rs, rt, imm),
            0b001111: lambda: _lui(rt, imm),
            0b100011: lambda: _lw(rs, rt, imm),
            0b001101: lambda: _ori(rs, rt, imm),
            0b101000: lambda: _sb(rs, rt, imm),
            0b001010: lambda: _slti(rs, rt, imm),
            0b001011: lambda: _sltiu(rs, rt, imm),
            0b101001: lambda: _sh(rs, rt, imm),
            0b101011: lambda: _sw(rs, rt, imm),
            0b001110: lambda: _xori(rs, rt, imm),
            0b100010: lambda: _lwl(rs, rt, imm),
            0b100110: lambda: _lwr(rs, rt, imm),
            0b101010: lambda: _swl(rs, rt, imm),
            0b101110: lambda: _swr(rs, rt, imm),
        }

        switch.get(bin_to_num(op_code), lambda: None)()
    if count in checkpoints:
        print("=========check: %d=============" % count)
    count += 1
    return res
