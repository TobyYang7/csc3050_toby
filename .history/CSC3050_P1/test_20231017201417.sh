input_file="testfile3.asm"
output_file="output.txt"
expected_output_file="expectedoutput3.txt"

python phase1.py "$input_file"
python tester.py "$input_file" "$output_file" "$expected_output_file"
