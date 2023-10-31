from lib import *
from sys import argv

if __name__ == '__main__':
    # Initialization of program memory and register
    for i in range(32 + 3):
        reg[i] = 0

    # for i in range(len(argv)):
    #     print("--argv[%d]--" % i)
    #     print(argv[i])

    mem = bytearray(MEMORY_SIZE)
    reg[REGS.get("_pc")] = pc
    reg[REGS.get("_gp")] = gp
    reg[REGS.get("_sp")] = sp
    reg[REGS.get("_fp")] = sp

    # load in checkpoints
    init_checkpoints(argv[3])
    print("--checkpoints--", checkpoints)
    print("---mem len---", len(mem))

    print("=========init==================")
    print(reg)
    print("===============================")

    # load .data and .text segment in memory
    data_handler(argv[1])
    text_seg(argv[2])

    # open file of [fileName].in and [fileName].out
    infile = open(argv[4], 'r')
    outfile = open(argv[5], 'w')

    # initialize essential value
    return_val = 0
    curr_ins = 0
    total_ins = 0
    to_exit = False
    flag = []

    # start simulation
    while curr_ins >= 0 and curr_ins < len(my_ins):
        print("-------------------%d---------" % curr_ins)
        print("a0:%d a2:%d" % (reg[4], reg[REGS.get("_a2")]))
        # print("--to exit--", to_exit)
        # check if the instruction needs to be dumped
        checkpoint_memory(total_ins)
        checkpoint_register(total_ins)

        inst = my_ins[curr_ins]
        reg[REGS.get("_pc")] += 4
        flag = execute_cmd(inst, infile, outfile, to_exit, return_val)
        # print("--flag--", flag)
        curr_ins = (reg[REGS.get("_pc")] - STARTING_ADDRESS) >> 2
        total_ins += 1

        if True in flag:
            print("=========exit==================")
            print("--return--", flag[1])
            break

    print("=========final output==========")
    for element in out_file:
        print(element, end='')
    print("\n")
    checkpoint_memory(total_ins)
    checkpoint_register(total_ins)

    final_out = open("test.out", 'w')
    for element in out_file:
        final_out.write(element)
    final_out.close()

    infile.close()
    outfile.close()
