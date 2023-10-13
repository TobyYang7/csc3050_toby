cd "/home/csc3050/hello_world/csc3050_toby/CSC3050_P1"
input_file="testfile2.asm"
output_file="output.txt"
expected_output_file="expectedoutput2.txt"

python phase1.py "$input_file"
python tester.py "$input_file" "$output_file" "$expected_output_file"
