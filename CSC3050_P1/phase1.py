import functions as f
import labelTable as m

file = "csc3050_toby/CSC3050_P1/testfile3.asm"
text, label_dict = f.pre_process(file)


a = 0b00010000000000000000000000
b = 0b00000100000000000000000000
c = 0x400000
d = 0b100
print(bin(d >> 1))

print(0b100000-0b1000)
