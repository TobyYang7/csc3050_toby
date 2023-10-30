import struct
from lib import *


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
filename = "/home/parallels/toby_dev/csc3050_toby/CSC3050_P2/register_12.bin"  # 替换成你的实际文件名
reg_from_file = read_bin_file(filename)

output_filename = "reg_output.txt"  # 替换成你想要的输出文件名
write_to_txt(reg_from_file, output_filename)
