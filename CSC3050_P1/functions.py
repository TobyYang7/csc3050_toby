import labelTable as m
START_ADDRESS = 0x400000


def print_file(file):
    with open(file, 'r') as file:
        contents = file.read()
        print(contents)


def pre_process(file):
    """
    Pre-processes the given file by removing unwanted text, loading the text, finding labels, and removing labels.

    Args:
        file (str): The file to be pre-processed.

    Returns:
        tuple: A tuple containing the pre-processed text and a dictionary of labels found in the text.
    """
    # Remove unwanted text
    text = rm(file)

    # Add space to the end of the text
    text += " "

    # Load the text
    text = load_text(text)

    # Find labels in the text
    label_dict = find_labels(text)

    # Remove labels from the text
    text = rm_labels(text)

    # Return the pre-processed text and the dictionary of labels
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
                new_contents.append(line.strip())
            else:
                # If there is a colon, add only the code part without leading spaces
                new_contents.append(parts[1].strip())
    return '\n'.join(new_contents)


# load the .text section
def load_text(text):
    start_index = text.find('.text')
    end_index = text.find('.data')
    if end_index != -1 and end_index < start_index:
        end_index = -1
    if start_index == -1:
        return text
    else:
        return text[start_index:end_index]


# find all the labels and their addresses
def find_labels(text):
    labels = {}
    contents = text.split('\n')
    counter = 0
    for line in contents:
        line = line.strip()
        if '.text' in line:
            continue
        if ":" in line:
            label = line[:line.index(":")]
            labels[label] = counter
            if line[line.index(":")+1:].strip() != "":
                counter += 1
        else:
            counter += 1
    return labels


def list_to_string(lst):
    return ''.join(str(e) for e in lst)


def Jtype_drop(num):
    """
    Drops the upper 4 bits and lower 2 bits of a 32-bit binary number.

    Args:
        num (int): A 32-bit binary number.

    Returns:
        int: The result of dropping the upper 4 bits and lower 2 bits of the input number.
    """
    # Convert num to 32-bit binary string
    binary_str = format(num, '032b')
    # Drop upper 4 bits and lower 2 bits
    binary_str = binary_str[4:-2]
    # Convert binary string to integer
    result = int(binary_str, 2)
    return result


def translate(type_num, inst, reg, address, imm, label, current):
    """
    Translates the given instruction into its corresponding binary format.

    Parameters:
    type_num (int): The type of instruction.
    inst (dict): The instruction dictionary containing the opcode and function fields.
    reg (list): The list of registers used in the instruction.
    address (dict): The dictionary containing the register and immediate fields used in the instruction.
    imm (int): The immediate value used in the instruction.
    label (int): The label value used in the instruction.
    current (int): The current instruction address.

    Returns:
    dict: The dictionary containing the binary format of the instruction.
    """
    # reg[], address["reg"], address["imm"]
    # inst["opcode"], inst["function"]
    if type_num == 1:
        # xxx rd, rs, rt
        return {"opcode": inst["opcode"], "rd": reg[0], "rs": reg[1], "rt": reg[2], "function": inst["function"]}
    elif type_num == 2:
        # xxx rt, rs, imm
        return {"opcode": inst["opcode"], "rt": reg[0], "rs": reg[1], "imm": imm}
    elif type_num == 3:
        # xxx rd, rs
        return {"opcode": inst["opcode"], "rd": reg[0], "rs": reg[1], "function": inst["function"]}
    elif type_num == 4:
        # xxx rs, rt
        return {"opcode": inst["opcode"], "rs": reg[0], "rt": reg[1], "function": inst["function"]}
    elif type_num == 5:  # fix: sa
        # xxx rd, rt, sa
        return {"opcode": inst["opcode"], "rd": reg[0], "rt": reg[1], "sa": imm, "function": inst["function"]}
    elif type_num == 6:
        # xxx rs, rt, label
        # branch
        return {"opcode": inst["opcode"], "rs": reg[0], "rt": reg[1], "imm": int(label-current)}
    elif type_num == 7:  # fix: check
        # xxx rs, label
        # branch
        return {"opcode": inst["opcode"], "rs": reg[0], "imm": int(label-current)}
    elif type_num == 8:  # fix: check
        # xxx label
        # print("PC%d" % current)
        # print("label:", label)
        address = START_ADDRESS + label*4
        num = Jtype_drop(address)
        return {"opcode": inst["opcode"], "imm": num}
    elif type_num == 9:
        # xxx rs
        return {"opcode": inst["opcode"], "rs": reg[0], "function": inst["function"]}
    elif type_num == 10:
        # xxx rd
        return {"opcode": inst["opcode"], "rd": reg[0], "function": inst["function"]}
    elif type_num == 11:
        # xxx rt, address
        return {"opcode": inst["opcode"], "rt": reg[0], "rs": address["reg"], "imm": address["imm"]}
    elif type_num == 12:
        # xxx rt, imm
        return {"opcode": inst["opcode"], "rt": reg[0], "imm": imm}
