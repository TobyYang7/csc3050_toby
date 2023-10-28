from lib import *
from lib import _add, _addu, _and, _div, _divu, _jalr, _jr, _mfhi, _mflo, _mthi, _mtlo, _mult, _multu, _nor, _or, _sll, _sllv, _slt, _sltu, _sra, _srav, _srl, _srlv, _sub, _subu, _xor
from lib import _addi, _addiu, _andi, _beq, _bgez, _bgtz, _blez, _bltz, _bne, _lb, _lbu, _lh, _lhu, _lui, _lw, _ori, _sb, _slti, _sltiu, _sh, _sw, _xori
from lib import _lwl, _lwr, _swl, _swr, _j, _jal, _print_int, _print_string, _read_int, _read_string, _sbrk, _exit, _print_char, _read_char, _open, _read, _write, _close, _exit2, _syscall


def init_checkpoints(checkpoint_file):
    with open(checkpoint_file, "r") as fp:
        for line in fp:
            checkpoints.add(int(line.strip()))


# todo: check
def checkpoint_memory(ins_count):
    if ins_count not in checkpoints:
        # print("--mem count not in--", ins_count)
        return
    print("--mem count in--", ins_count)
    name = f"memory_{ins_count}.bin"
    with open(name, "wb") as fp:
        fp.write(prog[:0x600000])


def checkpoint_register(ins_count):
    if ins_count not in checkpoints:
        return
    print("--reg count in--", ins_count)
    name = f"register_{ins_count}.bin"
    with open(name, "wb") as fp:
        fp.write(struct.pack('i' * len(reg), *reg))


def data_handler(file_name):
    global STATIC_DATA, prog

    infile = open(file_name, 'r')
    line = ""
    data_type = ""
    quantity = ""
    my_hex = ""
    nums = []
    ss = ""
    num = 0
    ch = ""
    ptr = bytearray()
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
            at_dot_data = True
            continue

        if ".text" in line:
            at_dot_text = True
            break

        if at_dot_data and not at_dot_text:
            data_type = line[:line.find("\"")]

            if ".asciiz" in data_type:
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
                            prog[TEXT_SIZE + STATIC_DATA + length] = line[i]
                            length += 1
                            contin_bs = 0
                    elif line[i] == '\\' and line[i + 1] != '\\':
                        contin_bs += 1
                        if contin_bs % 2 == 1:
                            continue
                        else:
                            prog[TEXT_SIZE + STATIC_DATA +
                                 length] = get_char(line[i])
                            length += 1
                            contin_bs = 0
                    elif line[i] != '\\':
                        if contin_bs == 0:
                            prog[TEXT_SIZE + STATIC_DATA + length] = line[i]
                            length += 1
                        elif contin_bs != 0:
                            prog[TEXT_SIZE + STATIC_DATA +
                                 length] = get_char(line[i])
                            length += 1
                            contin_bs = 0

                if contin_bs % 2 != 0:
                    prog[TEXT_SIZE + STATIC_DATA + length] = get_char(line[-1])
                    contin_bs = 0
                elif contin_bs % 2 == 0:
                    prog[TEXT_SIZE + STATIC_DATA + length] = line[-1]
                    contin_bs = 0

                length += 1
                prog[TEXT_SIZE + STATIC_DATA + length] = '\0'
                length += 1

                if length % 4 == 0:
                    STATIC_DATA += length
                else:
                    STATIC_DATA += length
                    STATIC_DATA += (4 - length % 4)

                continue

            if ".ascii" in data_type:
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
                            prog[TEXT_SIZE + STATIC_DATA + length] = line[i]
                            length += 1
                            contin_bs = 0
                    elif line[i] == '\\' and line[i + 1] != '\\':
                        contin_bs += 1
                        if contin_bs % 2 == 1:
                            continue
                        else:
                            prog[TEXT_SIZE + STATIC_DATA +
                                 length] = get_char(line[i])
                            length += 1
                            contin_bs = 0
                    elif line[i] != '\\':
                        if contin_bs == 0:
                            prog[TEXT_SIZE + STATIC_DATA + length] = line[i]
                            length += 1
                        elif contin_bs != 0:
                            prog[TEXT_SIZE + STATIC_DATA +
                                 length] = get_char(line[i])
                            length += 1
                            contin_bs = 0

                if contin_bs % 2 != 0:
                    prog[TEXT_SIZE + STATIC_DATA + length] = get_char(line[-1])
                    contin_bs = 0
                elif contin_bs % 2 == 0:
                    prog[TEXT_SIZE + STATIC_DATA + length] = line[-1]
                    contin_bs = 0

                length += 1

                if length % 4 == 0:
                    STATIC_DATA += length
                else:
                    STATIC_DATA += length
                    STATIC_DATA += (4 - length % 4)

                continue

            if ".word" in line:
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
                    if ptr_index + 4 > len(prog):
                        print(
                            f"Not enough space in prog at index {ptr_index} to store the number {num}")
                        continue

                    prog[ptr_index] = num & 0xff
                    prog[ptr_index + 1] = (num >> 8) & 0xff
                    prog[ptr_index + 2] = (num >> 16) & 0xff
                    prog[ptr_index + 3] = (num >> 24) & 0xff
                    STATIC_DATA += 4

            if ".byte" in data_type:
                line = line[line.find(".byte") + 5:]
                ss = line
                nums = []

                while ss:
                    num, ss = ss.split(maxsplit=1)
                    nums.append(int(num))

                length = len(nums)

                for i in range(length):
                    ptr = prog + TEXT_SIZE + STATIC_DATA
                    ptr[0] = nums[i] & 0xff
                    STATIC_DATA += 1

                if length % 4 != 0:
                    STATIC_DATA += (4 - length % 4)

                continue

            if ".half" in data_type:
                line = line[line.find(".half") + 5:]
                ss = line
                nums = []

                while ss:
                    num, ss = ss.split(maxsplit=1)
                    nums.append(int(num))

                length = len(nums)

                for i in range(length):
                    ptr = prog + TEXT_SIZE + STATIC_DATA
                    ptr[0] = nums[i] & 0xff
                    ptr[1] = (nums[i] >> 8) & 0xff
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
            prog[machine_code_size + 3 -
                 i] = bin_to_num(line[8 * i:8 * (i + 1)])

        machine_code_size += 4

    infile.close()


def execute_cmd(machine_code, infile, outfile, to_exit, return_val):
    op_code = machine_code[:6]

    # print("--infile--", infile)

    if op_code == "000000":
        rs = bin_to_num(machine_code[6:11])
        rt = bin_to_num(machine_code[11:16])
        rd = bin_to_num(machine_code[16:21])
        sa = bin_to_num(machine_code[21:26])
        func = bin_to_num(machine_code[26:32])

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

        switch.get(func, lambda: None)()

    elif op_code == "000010" or op_code == "000011":
        target = bin_to_num(machine_code[6:32])

        if op_code == "000010":
            _j(target)
        else:
            _jal(target)

    else:
        rs = bin_to_num(machine_code[6:11])
        rt = bin_to_num(machine_code[11:16])
        imm = bin_to_num(machine_code[16:32])

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
