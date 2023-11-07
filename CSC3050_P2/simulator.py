from lib import *
from sys import argv

if __name__ == '__main__':

    for i in range(32 + 3):
        reg[i] = 0

    mem = bytearray(MEMORY_SIZE)
    reg[REGS.get("_pc")] = pc
    reg[REGS.get("_gp")] = gp
    reg[REGS.get("_sp")] = sp
    reg[REGS.get("_fp")] = sp
    init_checkpoints(argv[3])
    print("--checkpoints--", checkpoints)
    print("---mem len---", len(mem))
    print("=========init==================")
    print(reg)
    print("===============================")

    data_handler(argv[1])
    text_seg(argv[2])
    infile = open(argv[4], 'r')
    outfile = open(argv[5], 'w')

    return_val = 0
    curr_ins = 0
    total_ins = 0
    to_exit = False
    flag = []

    while curr_ins >= 0 and curr_ins < len(my_ins):
        print("-------------------%d---------" % curr_ins)
        print("a0:%d a2:%d" % (reg[4], reg[REGS.get("_a2")]))

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
    checkpoint_memory(total_ins)
    checkpoint_register(total_ins)

    infile.close()
    outfile.close()

    print("\n=========check=================")
