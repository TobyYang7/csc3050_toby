import functions as f
import MIPS_table as m


file = "csc3050_toby/CSC3050_P1/testfile.asm"
text, label_dict = f.pre_process(file)

# todo: text
# print(text)

counter = 0
machine_code = []
for line in text.split('\n'):
    if line == '' or line == '\n':
        continue
    line.replace(',', '')
    elements = line.split(' ')

    # instruction detection
    instruction = None
    if elements[0] in m.MIPS_instruction_table:
        instruction = elements[0]
        counter += 1
    else:
        continue

    # register detection
    registers = []
    for slot in elements[1:]:
        if slot == '' or slot == ',':
            elements.remove(slot)
        if slot.startswith('$'):
            slot = slot.replace('$', '')
            slot = slot.replace(',', '')
            registers.append(m.reg.index(slot))

    # imm detection
    imm = None
    for idx in range(-1, -len(elements)-1, -1):
        string = elements[idx]
        if string.isdigit():
            imm = int(string)
            break
        elif string.startswith('-') and string[1:].isdigit():
            imm = int(string)
            break
        elif string.startswith('+') and string[1:].isdigit():
            imm = int(string[1:])
            break

    # address detection  (imm)reg
    address = {}
    for slot in elements[1:]:
        if '(' and ')' in slot:
            reg = slot[slot.index('(')+2:slot.index(')')]
            address["reg"] = m.reg.index(reg)
            imm = slot[:slot.index('(')]
            address["imm"] = int(imm)

    # type detection
    type_dict = {}
    type_num = None
    for type in m.type_list:
        if instruction in type:
            type_dict = type[instruction]
            type_num = m.type_list.index(type)+1
            break

    # label detection
    label = None
    if elements[-1] in label_dict:
        label = label_dict[elements[-1]]

    # divide MIPS code into different types
    # translate(type_num, inst, reg, address, imm, label)
    MIPS_element = f.translate(
        type_num, m.MIPS_instruction_table[instruction], registers, address, imm, label)
    instr_type = m.MIPS_instruction_table[instruction]["type"]

    # todo:test
    # print(counter, type_num, instruction)

    machine_code_line = [0]*32  # 32 bits
    match instr_type:
        case "R":
            # R_type = {"opcode", "rs", "rt", "rd", "sa", "function"}
            for code in m.R_type:
                match code:
                    case "opcode":
                        machine_code_line[0:6] = f"{int(MIPS_element[code]):06b}"
                    case "rs":
                        if "rs" in MIPS_element:
                            machine_code_line[6:11] = f"{int(MIPS_element[code]):05b}"
                    case "rt":
                        if "rt" in MIPS_element:
                            machine_code_line[11:
                                              16] = f"{int(MIPS_element[code]):05b}"
                    case "rd":
                        if "rd" in MIPS_element:
                            machine_code_line[16:
                                              21] = f"{int(MIPS_element[code]):05b}"
                    case "sa":
                        if "sa" in MIPS_element:
                            machine_code_line[21:
                                              26] = f"{int(MIPS_element[code]):05b}"
                    case "function":
                        machine_code_line[26:
                                          32] = f"{int(MIPS_element[code]):06b}"

        case "I":
            # I_type = {"opcode", "rs", "rt", "imm"}
            for code in m.I_type:
                match code:
                    case "opcode":
                        machine_code_line[0:6] = f"{int(MIPS_element[code]):06b}"
                    case "rs":
                        if "rs" in MIPS_element:
                            machine_code_line[6:11] = f"{int(MIPS_element[code]):05b}"
                    case "rt":
                        if "rt" in MIPS_element:
                            machine_code_line[11:
                                              16] = f"{int(MIPS_element[code]):05b}"
                    case "imm":
                        if "imm" in MIPS_element:
                            if int(MIPS_element[code]) < 0:
                                # Convert negative number to 16-bit two's complement
                                machine_code_line[16:32] = f"{(1 << 16) + int(MIPS_element[code]):016b}"
                            else:
                                machine_code_line[16:
                                                  32] = f"{int(MIPS_element[code]):016b}"

        case "J":
            # J_type = {"opcode", "imm"}
            for code in m.J_type:
                match code:
                    case "opcode":
                        machine_code_line[0:6] = f"{int(MIPS_element[code]):06b}"
                    case "imm":
                        if int(MIPS_element[code]) < 0:
                            # Convert negative number to 16-bit two's complement
                            machine_code_line[6:32] = f"{(1 << 16) + int(MIPS_element[code]):026b}"
                        else:
                            machine_code_line[6:
                                              32] = f"{int(MIPS_element[code]):026b}"

    machine_code.append(f.list_to_string(machine_code_line))
    machine_code.append('\n')


machine_code = f.list_to_string(machine_code)
