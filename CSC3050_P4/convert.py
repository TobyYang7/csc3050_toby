import sys
def convert_binary_to_text(input_file, output_file):
    with open(input_file, 'rb') as f:
        binary_data = f.read()
    text_data = binary_data.decode('utf-8')
    with open(output_file, 'w') as f:
        f.write(text_data)

def convert_text_to_binary(input_file, output_file):
    with open(input_file, 'r') as f:
        text_data = f.read()
    binary_data = text_data.encode('utf-8')
    with open(output_file, 'wb') as f:
        f.write(binary_data)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python convert.py input_file output_file")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        type = sys.argv[3]
        if type == 't2b':
            convert_text_to_binary(input_file, output_file)
        elif type == 'b2t':
            convert_binary_to_text(input_file, output_file)
