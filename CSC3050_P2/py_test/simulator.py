import simulator_functions as sim
import os
import sys

TEXT_START = 0x400000
TEXT_END = 0x500000
DATA_START = 0x500000
DATA_END = 0x600000
STACK_END = 0x9fffff

read_index = 0
memory = ['0'*32]*(6*2**18)
register = ['0'*32]*35
register[28] = '0'*8+'10000000'+'01010000'+'0'*8
register[29] = '0'*16+'1010'+'0'*12
register[30] = '0'*16+'1010'+'0'*12
register[32] = '0'*16+'0100'+'0'*12


test_asm = sys.argv[1]
test_txt = sys.argv[2]
test_checkpoints = sys.argv[3]
test_in = sys.argv[4]
test_out = sys.argv[5]


with open(test_asm, "r") as file1:
    content = file1.readlines()
no_comment_content = sim.delete_comment(content)
memory, dynamic_index = sim.static_data(no_comment_content, memory, 2**18)

# Assemble the codes
# test_txt = 'D:\Daerxia\CSC3050\Assignment2\\new\\tests\many\many.txt'
memory = sim.assemble_machine_code(memory, test_txt)

with open(test_checkpoints, 'r') as file1:
    checkpoints_list = file1.readlines()

for i in range(0, len(checkpoints_list)):
    print('checkpoints:', checkpoints_list[i])
    checkpoints_list[i] = int(checkpoints_list[i].strip())

# Calculate the beginning index of dynamic address
dynamic_address = (dynamic_index-2**18)*4 + 5242880

# Main simulation
sim.simulation(memory, register, dynamic_address, read_index,
               checkpoints_list, test_in, test_out)
