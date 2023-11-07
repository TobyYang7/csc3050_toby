import struct
from lib import *
from sys import argv


def read_bin_file(filename):
    with open(filename, "rb") as fp:
        # 从二进制文件中读取数据
        data = fp.read()

    # 使用struct.unpack解析二进制数据
    reg_size = len(reg)
    reg_data = struct.unpack('i' * reg_size, data)

    return list(reg_data)


def write_to_txt(reg_data, filename):
    with open(filename, "w") as fp:
        for value in reg_data:
            fp.write(str(value) + "\n")


# 使用示例

file = argv[1]
my = argv[2]
ins_count = int(argv[3])

reg_from_file = read_bin_file(file)
output_filename = f"true_reg_{ins_count}.txt"
write_to_txt(reg_from_file, output_filename)

my_reg_from_file = read_bin_file(my)
my_output_filename = f"my_{ins_count}.txt"
write_to_txt(my_reg_from_file, my_output_filename)
