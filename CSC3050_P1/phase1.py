import functions as f
import labelTable as m
START_ADDRESS = 0x400000

file = "testfile2.asm"
text, label_dict = f.pre_process(file)

for label in label_dict:
    print(label)
    print(label_dict[label])
    print(hex(4*label_dict[label]+0x400000))
    print('--------')
print(text)
