import functions as f
import labelTable as m

file = "testfile2.asm"
text, label_dict = f.pre_process(file)
for label in label_dict:
    print(label)
print(text)
