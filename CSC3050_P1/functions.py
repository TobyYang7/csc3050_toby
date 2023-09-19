import MIPS_table as m


def test_machine_code():
    expected_output_file = input(
        "Enter the path to the expected output file: ")
    with open(expected_output_file, 'r') as f:
        expected_output = f.readlines()

    actual_output_file = input("Enter the path to the actual output file: ")
    with open(actual_output_file, 'r') as f:
        actual_output = f.readlines()

    assert expected_output == actual_output


def print_file(file):
    with open(file, 'r') as file:
        contents = file.read()
        print(contents)


def pre_process(file):
    text = rm(file)
    text = load_text(text)
    label_dict = find_labels(text)
    text = rm_labels(text)
    return text, label_dict


# remove all the comments and empty lines
def rm(file):
    with open(file, 'r') as f:
        contents = f.readlines()
        new_contents = []
        for line in contents:
            if line.strip() and not line.strip().startswith('#'):
                new_contents.append(line)
        contents = ''.join(new_contents)
        while True:
            start_index = contents.find('#')
            if start_index == -1:
                break
            end_index = contents.find('\n', start_index)
            if end_index == -1:
                end_index = len(contents)
            contents = contents[:start_index] + contents[end_index:]
        return contents


def rm_labels(text):
    contents = text.split('\n')
    new_contents = []
    for line in contents:
        # Check if the line ends with a colon (":") to identify labels
        if not line.strip().endswith(':'):
            # Split the line by the first colon to separate label and code
            parts = line.split(':', 1)
            if len(parts) == 1:
                # If there is no colon, add the entire line without leading spaces
                new_contents.append(line.lstrip())
            else:
                # If there is a colon, add only the code part without leading spaces
                new_contents.append(parts[1].strip())
    return '\n'.join(new_contents)


# load the .text section
def load_text(text):
    # todo: return .text section
    return text


# find all the labels and their addresses
def find_labels(text):
    labels = {}
    contents = text.split('\n')
    counter = 0
    for line in contents:
        line = line.strip('')
        if '.text' in line:
            continue
        if ":" in line:
            label = line[:line.index(":")]
            labels[label] = contents.index(line)
            labels[label] = counter * 4
        else:
            counter += 1
    return labels


def list_to_string(lst):
    return ''.join(str(e) for e in lst)


def translate(type_num, inst, reg, address, imm, label):
    # reg[], address["reg"], address["imm"]
    # inst["opcode"], inst["function"]
    match type_num:
        case 1:
            # xxx rd, rs, rt
            return {"opcode": inst["opcode"], "rd": reg[0], "rs": reg[1], "rt": reg[2], "function": inst["function"]}
        case 2:
            # xxx rt, rs, imm
            return {"opcode": inst["opcode"], "rt": reg[0], "rs": reg[1], "imm": imm}
        case 3:
            # xxx rd, rs
            return {"opcode": inst["opcode"], "rd": reg[0], "rs": reg[1], "function": inst["function"]}
        case 4:
            # xxx rs, rt
            return {"opcode": inst["opcode"], "rs": reg[0], "rt": reg[1], "function": inst["function"]}
        case 5:
            # xxx rd, rt, sa
            return {"opcode": inst["opcode"], "rd": reg[0], "rt": reg[1], "sa": reg[2], "function": inst["function"]}
        case 6:
            # xxx rs, rt, label
            return {"opcode": inst["opcode"], "rs": reg[0], "rt": reg[1], "imm": label}
        case 7:
            # xxx rs, label
            return {"opcode": inst["opcode"], "rs": reg[0], "imm": label, "function": inst["function"]}
        case 8:
            # xxx label
            return {"opcode": inst["opcode"], "imm": label}
        case 9:
            # xxx rs
            return {"opcode": inst["opcode"], "rs": reg[0], "function": inst["function"]}
        case 10:
            # xxx rd
            return {"opcode": inst["opcode"], "rd": reg[0], "function": inst["function"]}
        case 11:
            # xxx rt, address
            return {"opcode": inst["opcode"], "rt": reg[0], "rs": address["reg"], "imm": address["imm"]}
        case 12:
            # xxx rt, imm
            return {"opcode": inst["opcode"], "rt": reg[0], "imm": imm}
