from lib import *
from lib_mem import *
from sys import argv

if __name__ == '__main__':
    # Initialization of program memory and register
    for i in range(32 + 3):
        reg[i] = 0

    # for i in range(len(argv)):
    #     print("--argv[%d]--" % i)
    #     print(argv[i])

    prog = bytearray(MEMORY_SIZE)
    reg[REGS.get("_pc")] = pc
    reg[REGS.get("_gp")] = gp
    reg[REGS.get("_sp")] = sp
    reg[REGS.get("_fp")] = sp

    # load in checkpoints
    init_checkpoints(argv[3])
    print("--checkpoints--", checkpoints)

    # load .data and .text segment in memory
    data_handler(argv[1])
    text_seg(argv[2])

    # open file of [fileName].in and [fileName].out
    infile = open(argv[4], 'r')
    outfile = open(argv[5], 'w')

    # initialize essential value
    return_val = 0
    to_exit = False
    curr_ins = 0
    total_ins = 0

    # start simulation
    while curr_ins >= 0 and curr_ins < len(my_ins):
        # check if the instruction needs to be dumped
        checkpoint_memory(total_ins)
        checkpoint_register(total_ins)

        # syscall: _exit() || _exit2()
        if to_exit:
            break

        inst = my_ins[curr_ins]
        reg[REGS.get("_pc")] += 4
        execute_cmd(inst, infile, outfile, to_exit, return_val)
        curr_ins = (reg[REGS.get("_pc")] - STARTING_ADDRESS) >> 2
        total_ins += 1

    checkpoint_memory(total_ins)
    checkpoint_register(total_ins)

    infile.close()
    outfile.close()
