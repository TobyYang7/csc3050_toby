cd "/csc3050_toby/CSC3050_P1"
input_file="testfile6.asm"
output_file="output.txt"
expected_output_file="expectedoutput6.txt"

python phase1.py "$input_file"
python tester.py "$input_file" "$output_file" "$expected_output_file"
