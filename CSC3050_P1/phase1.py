import functions as f
import labelTable as m

file = "csc3050_toby/CSC3050_P1/testfile.asm"
text, label_dict = f.pre_process(file)

print(text)
