import functions as f
import labelTable as m
import sys
START_ADDRESS = 0x400000

file = sys.argv[1]
text, label_dict = f.pre_process(file)

print("Label:")
for label in label_dict:
    print(
        f"{label_dict[label]:<4} {hex(4 * label_dict[label] + 0x400000):<10} {label}")

print("------------------------------------------")
print("output of phase1.py:\n")
print(text)
print("------------------------------------------")
print("output of phase2.py:\n")
