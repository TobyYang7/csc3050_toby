import sys
def convert_binary_to_text(input_file, output_file):
    with open(input_file, 'rb') as f:
        binary_data = f.read()
    text_data = binary_data.decode('utf-8')
    with open(output_file, 'w') as f:
        f.write(text_data)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert.py input_file output_file")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        convert_binary_to_text(input_file, output_file)
