import sys
import os

TEXT_START = 0x400000
TEXT_END = 0x500000
DATA_START = 0x500000
DATA_END = 0x600000
STACK_END = 0x9fffff

# For memory: one element represent 1 memory address = 4 byte
# For register: same with memory
# When computing pc_counter, we first convert to decimal and calculate the absolute address, then
# we convert into binary forms


def assemble_machine_code(memory, input_code):
    """
    Assemble the input code into machine code and store it in memory.

    Args:
    memory (list): A list representing the memory of the simulated machine.
    input_code (str): The file path of the input code to be assembled.

    Returns:
    list: The updated memory with the assembled machine code.
    """
    index = 0
    with open(input_code, 'r') as file1:
        lines = file1.readlines()
        for line in lines:
            # Remove unnecessary characters and extract the machine code
            line = line.replace("\n", "").replace(
                " ", "").replace("\t", "").strip()
            machine_code = line[24:32]+line[16:24]+line[8:16]+line[0:8]
            # Store the machine code in memory
            memory[index] = machine_code
            index += 1
    return memory


def little_endian(string1):
    """
    This function takes a hexadecimal string as input and returns its little-endian representation.
    If the input string is 32 characters long, it is split into 4 bytes and rearranged in little-endian order.
    If the input string is 16 characters long, it is split into 2 bytes and rearranged in little-endian order.
    """
    if len(string1) == 32:
        # If the input string is 32 characters long, split it into 4 bytes and rearrange in little-endian order
        string2 = string1[24:32]+string1[16:24]+string1[8:16]+string1[0:8]
    elif len(string1) == 16:
        # If the input string is 16 characters long, split it into 2 bytes and rearrange in little-endian order
        string2 = string1[8:16]+string1[0:8]
    return string2


def extended(binary_number, length):
    if length >= len(binary_number):
        binary_number = (length-len(binary_number))*'0' + binary_number
    return binary_number


# Scan the file and Discard comments
def delete_comment(content):
    for i in range(len(content)):
        if content[i].find('#') != -1:
            comment_position = content[i].find('#')
            content[i] = content[i][:comment_position]   # Discard comments
    return (content)


# .asciiz and .ascii is big endian
def as_string(string1, memory, index, type):
    """
    Converts a string to its binary representation and stores it in memory.

    Args:
    string1 (str): The string to be converted.
    memory (list): The memory to store the binary representation.
    index (int): The starting index in memory to store the binary representation.
    type (str): The type of string, either '.ascii' or '.asciiz'.

    Returns:
    tuple: A tuple containing the updated memory and index.

    """
    begin_index = string1.find('"')+1
    end_index = string1[begin_index:].find('"')+begin_index
    static_string = string1[begin_index:end_index].replace('\\n', '\n')
    block_num = len(static_string)//4
    remainder = len(static_string) % 4
    for i in range(0, block_num):
        substring = static_string[4*i:4*i+4]
        # Convert each character in the substring to its binary representation and store it in memory
        memory[index] = ''.join(extended(format(ord(c), 'b'), 8)
                                for c in substring)
        index += 1
    if not (remainder == 0 and type == '.ascii'):
        remain_string = static_string[4*block_num:]
        # Store the remaining characters in memory
        memory = last_block(memory, index, remain_string, remainder, type)[0]
        index = last_block(memory, index, remain_string, remainder, type)[1]
    return (memory, index)


def last_block(memory, index, remain_string, remainder, type):
    """
    This function is used to fill the last block of memory with the remaining string.
    If the remainder is 0 and the type is '.asciiz', it fills the block with all zeros.
    If the remainder is 1, it fills the block with the remaining string and appends 24 zeros.
    If the remainder is 2, it fills the block with the remaining string and appends 16 zeros.
    If the remainder is 3, it fills the block with the remaining string and appends 8 zeros.

    Args:
    memory (list): The memory block to be filled.
    index (int): The index of the current block.
    remain_string (str): The remaining string to be filled in the last block.
    remainder (int): The remainder of the remaining string length divided by 4.
    type (str): The type of the remaining string.

    Returns:
    tuple: A tuple containing the updated memory block and index.
    """
    if remainder == 0 and type == '.asciiz':
        # If remainder is 0 and type is '.asciiz', fill the block with all zeros.
        memory[index] = '0'*32
    elif remainder == 1:
        # If remainder is 1, fill the block with the remaining string and append 24 zeros.
        memory[index] = ''.join(extended(format(ord(c), 'b'), 8)
                                for c in remain_string) + '0'*24
    elif remainder == 2:
        # If remainder is 2, fill the block with the remaining string and append 16 zeros.
        memory[index] = ''.join(extended(format(ord(c), 'b'), 8)
                                for c in remain_string) + '0'*16
    elif remainder == 3:
        # If remainder is 3, fill the block with the remaining string and append 8 zeros.
        memory[index] = ''.join(extended(format(ord(c), 'b'), 8)
                                for c in remain_string) + '0'*8
    index += 1
    return (memory, index)


def static_data(content, memory, index):
    """
    This function extracts static data from the given content and stores it in memory.

    Args:
    - content (list): A list of strings representing the content of a file.
    - memory (dict): A dictionary representing the memory of the simulator.
    - index (int): An integer representing the current index of memory.

    Returns:
    - A tuple containing the updated memory and index.

    """
    tag_data = False
    for i in content:
        if ".data" in i:
            tag_data = True
        elif ".text" in i:
            break
        if tag_data:
            if ".asciiz" in i:
                memory = as_string(i, memory, index, ".asciiz")[0]
                index = as_string(i, memory, index, ".asciiz")[1]
    return (memory, index)


def sign_extended(binary_number, length):
    if length >= len(binary_number):
        if binary_number[0] == '0':
            extened_num = (length-len(binary_number))*'0' + binary_number
        else:
            extened_num = (length-len(binary_number))*'1' + binary_number
    else:
        print('error')
    return extened_num


def extended(binary_number, length):
    if length >= len(binary_number):
        binary_number = (length-len(binary_number))*'0' + binary_number
    return binary_number


def unsign_bin_to_dec(string1):
    decimal_int = 0
    for i in range(0, len(string1)):
        decimal_int += int(string1[i]) * 2**(len(string1)-1-i)
    return decimal_int


def unsign_dec_to_bin(integer1, length):
    string1 = extended(bin(integer1)[2:], length)
    return string1


def sign_bin_to_dec(string1):
    decimal_int = 0
    if len(string1) == 1:
        decimal_int = -1*int(string1)
    else:
        for i in range(1, len(string1)):
            decimal_int += int(string1[i]) * 2**(len(string1)-1-i)
        if string1[0] == '1':
            decimal_int += -2**(len(string1)-1)
    return decimal_int


def sign_dec_to_bin(integer1, length):
    if integer1 >= 0:
        string1 = extended(bin(integer1)[2:], length)
    else:
        result = '0' + bin(-integer1)[2:]
        tag = False
        i = len(result)-1
        two_complement = ''
        while i >= 0:
            if tag:
                if result[i] == '1':
                    two_complement = '0' + two_complement
                else:
                    two_complement = '1' + two_complement
            else:
                two_complement = result[i] + two_complement
            if result[i] == '1':
                tag = True
            i -= 1
        string1 = sign_extended(two_complement, length)
    return string1


def store_register_integer(register, index, value):
    """
    Store an integer value in a register at a given index.

    Args:
        register (list): A list of 32-bit binary strings representing the registers.
        index (int): The index of the register to store the value in.
        value (int): The integer value to store in the register.

    Returns:
        list: The updated register list with the new value stored at the given index.
    """
    # Convert the integer value to a 32-bit binary string and then to little-endian format
    string1 = little_endian(sign_dec_to_bin(value, 32))
    # Store the little-endian binary string in the register at the given index
    register[index] = string1
    # Return the updated register list
    return register


def get_register_integer(register, index):
    """
    Converts a binary string from a register at a given index to a signed integer.

    Args:
        register (list): A list of 32-bit binary strings representing the register.
        index (int): The index of the binary string to convert.

    Returns:
        int: The signed integer value of the binary string at the given index.
    """
    # Convert the binary string to a signed integer
    register_value = sign_bin_to_dec(little_endian(register[index]))
    return register_value


def R_sll(register, rd, rt, sa):
    """
    Shift the bits in the value of register[rt] left by sa bits and store the result in register[rd].
    The bits shifted out of the left end are discarded and the vacated bits on the right are filled with zeros.

    Args:
        register (list): A list of 32-bit registers.
        rd (int): The index of the destination register.
        rt (int): The index of the source register.
        sa (int): The number of bits to shift left.

    Returns:
        list: The updated list of registers.
    """
    rt_value = little_endian(
        register[rt])  # Convert the value of register[rt] to little-endian format.
    # Shift the bits in rt_value left by sa bits and store the result in register[rd].
    register[rd] = little_endian(rt_value[sa:] + sa*'0')
    return register


def syscall_print_string(memory, register, test_out):
    """
    Print a string to the console.

    Args:
    - memory: a list of strings representing the memory of the simulated system
    - register: an integer representing the register containing the address of the string to print
    - test_out: a string representing the file path to write the output to

    Returns:
    - None
    """
    address = get_register_integer(register, 4)
    index = (address - 4194304)//4  # need align
    tag = True
    with open(test_out, 'a') as file1:
        while tag == True:
            for i in range(0, 4):
                char1 = chr(unsign_bin_to_dec(memory[index][i*8:(i+1)*8]))
                if memory[index][i*8:(i+1)*8] == '00000000':
                    tag = False
                    break
                else:
                    file1.write(char1)
            if tag == True:
                index += 1


def syscall_exit():
    os._exit(0)


def I_addi(register, rs, rt, immediate):
    """
    Adds the immediate value to the value in the specified register and stores the result in another register.

    Args:
        register (dict): A dictionary representing the register file.
        rs (str): The name of the source register.
        rt (str): The name of the destination register.
        immediate (str): A string representing the immediate value in binary.

    Returns:
        dict: The updated register file with the result stored in the destination register.
    """
    immediate_value = sign_bin_to_dec(
        immediate)  # Convert the immediate value from binary to decimal.
    # Get the value in the source register.
    rs_value = get_register_integer(register, rs)
    # Add the immediate value to the source register value.
    result = rs_value + immediate_value
    # Store the result in the destination register.
    register = store_register_integer(register, rt, result)
    return register


def R_execution(memory, register, read_index, machine_code, dynamic_address, test_in, test_out):
    """
    Executes R-type instructions.

    Args:
        memory (list): The memory of the simulated machine.
        register (list): The register of the simulated machine.
        read_index (int): The index of the next instruction to be executed.
        machine_code (str): The machine code of the instruction to be executed.
        dynamic_address (int): The dynamic address of the instruction to be executed.
        test_in (list): The input for the test case.
        test_out (list): The expected output for the test case.

    Returns:
        tuple: A tuple containing the updated memory, register, read_index, and dynamic_address.
    """

    # Extracting fields from the machine code
    rs = machine_code[6:11]
    rt = machine_code[11:16]
    rd = machine_code[16:21]
    sa = machine_code[21:26]
    func_code = machine_code[26:]

    # Converting binary fields to decimal
    rs_decimal = unsign_bin_to_dec(rs)
    rt_decimal = unsign_bin_to_dec(rt)
    rd_decimal = unsign_bin_to_dec(rd)
    sa_decimal = unsign_bin_to_dec(sa)

    # shift logical
    if func_code == '000000':
        # Shifts the value in rt left by sa bits and stores the result in rd
        register = R_sll(register, rd_decimal, rt_decimal, sa_decimal)

    # syscall
    elif func_code == '001100':
        # Gets the value in register v0
        v0 = get_register_integer(register, 2)

        # If v0 is 4, print the string in memory starting from the address in register a0
        if v0 == 4:
            syscall_print_string(memory, register, test_out)

        # If v0 is 10, exit the program
        elif v0 == 10:
            syscall_exit()

    return (memory, register, read_index, dynamic_address)


def I_execution(memory, register, machine_code):
    """
    Executes an I-format instruction.

    Args:
        memory (list): The memory of the simulated machine.
        register (list): The register file of the simulated machine.
        machine_code (str): The machine code of the instruction to be executed.

    Returns:
        tuple: A tuple containing the updated memory and register file.
    """
    # Extract the opcode, rs, rt, and immediate fields from the machine code
    opcode = machine_code[:6]
    rs = machine_code[6:11]
    rt = machine_code[11:16]
    immediate = machine_code[16:32]

    # Convert rs and rt from binary to decimal
    rs_decimal = unsign_bin_to_dec(rs)
    rt_decimal = unsign_bin_to_dec(rt)

    # Execute the instruction based on the opcode
    if opcode == '001000':
        register = I_addi(register, rs_decimal, rt_decimal, immediate)

    # Return the updated memory and register file
    return (memory, register)


def J_execution(register, machine_code):
    # todo: check
    opcode = machine_code[:6]
    address = machine_code[6:]
    address_decimal = unsign_bin_to_dec(address)
    if opcode == '000010':
        register[32] = unsign_dec_to_bin(address_decimal*4, 32)
    elif opcode == '000011':
        register[32] = unsign_dec_to_bin(address_decimal*4, 32)
    return register


# Execute the instruction
def execution(memory, register, read_index, machine_code, dynamic_address, test_in, test_out):
    """
    Executes the given machine code instruction based on its opcode type.

    Args:
        memory (list): The current state of the memory.
        register (list): The current state of the register.
        read_index (int): The current index of the memory to be read.
        machine_code (str): The machine code instruction to be executed.
        dynamic_address (int): The current dynamic address.
        test_in (list): The input values for testing.
        test_out (list): The expected output values for testing.

    Returns:
        tuple: A tuple containing the updated memory, register, read_index, and dynamic_address values.
    """

    # Check if the opcode is R-type
    if machine_code[0:6] == '000000':
        # Call R_execution function to execute the instruction
        (memory, register, read_index, dynamic_address) = R_execution(
            memory, register, read_index, machine_code, dynamic_address, test_in, test_out)
    # Check if the opcode is J-type
    elif machine_code[0:6] == '000010' or machine_code[0:6] == '000011':
        # Call J_execution function to execute the instruction
        register = J_execution(register, machine_code)
    # Otherwise, the opcode is I-type
    else:
        # Call I_execution function to execute the instruction
        memory, register = I_execution(memory, register, machine_code)

    # Return the updated memory, register, read_index, and dynamic_address values
    return (memory, register, read_index, dynamic_address)


def dump(checkpoints_list, memory, register, iteration):
    """
    Dump the contents of memory and register to binary files if the current iteration matches the first checkpoint in the list.

    Args:
        checkpoints_list (list): A list of iteration numbers that indicate when to dump the contents of memory and register.
        memory (list): A list of bit strings representing the contents of memory.
        register (list): A list of bit strings representing the contents of register.
        iteration (int): The current iteration number.

    Returns:
        list: A new list of checkpoints with the first checkpoint removed if the current iteration matches the first checkpoint in the original list.
    """
    if checkpoints_list[0] == iteration:
        # Create file names for memory and register binary files
        memory_bin = 'memory_' + str(iteration) + '.bin'
        register_bin = 'register_' + str(iteration) + '.bin'

        # Write memory contents to binary file
        with open(memory_bin, 'wb') as f1:
            for i in memory:
                bit_strings = [i[j:j + 8] for j in range(0, len(i), 8)]
                byte_list = [int(b, 2) for b in bit_strings]
                f1.write(bytearray(byte_list))

        # Write register contents to binary file
        with open(register_bin, 'wb') as f2:
            for i in range(0, len(register)):
                element = register[i]
                bit_strings = [element[j:j + 8]
                               for j in range(0, len(element), 8)]
                byte_list = [int(b, 2) for b in bit_strings]
                f2.write(bytearray(byte_list))

        # Remove the first checkpoint from the list
        checkpoints_list = checkpoints_list[1:]

    return checkpoints_list


# Start simulation
# register[32] is program counter
def simulation(memory, register, dynamic_address, read_index, checkpoints_list, test_in, test_out):
    """
    This function simulates the execution of machine code stored in memory.

    Args:
    - memory: a list of strings representing the memory of the simulated machine
    - register: a list of strings representing the registers of the simulated machine
    - dynamic_address: an integer representing the dynamic memory address of the simulated machine
    - read_index: an integer representing the read index of the simulated machine
    - checkpoints_list: a list of dictionaries representing the checkpoints of the simulated machine
    - test_in: a list of strings representing the input of the simulated machine
    - test_out: a list of strings representing the output of the simulated machine

    Returns:
    - None
    """

    # Set the start index of the machine code in memory
    start_index = 4194304

    # Initialize the iteration counter
    iteration = 0

    # Calculate the index of the first instruction to be executed
    index = (get_register_integer(register, 32)-start_index)//4

    # Execute the machine code until the end of the program is reached
    while memory[index] != '0'*32:

        # Dump the current state of the machine if checkpoints are enabled
        if checkpoints_list != []:
            checkpoints_list = dump(
                checkpoints_list, memory, register, iteration)

        # Get the machine code instruction to be executed
        # The machine code is stored in little endian format in memory
        machine_code = little_endian(memory[index])

        # Update the program counter
        register[32] = little_endian(unsign_dec_to_bin(
            get_register_integer(register, 32)+4, 32))

        # Execute the machine code instruction
        memory, register, read_index, dynamic_address = execution(
            memory, register, read_index, machine_code, dynamic_address, test_in, test_out)

        # Increment the iteration counter
        iteration += 1
