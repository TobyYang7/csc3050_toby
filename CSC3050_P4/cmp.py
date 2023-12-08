import argparse

def compare_txt_files(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        i = 0
        while True:
            line1 = f1.readline()
            line2 = f2.readline()

            if line1 != line2:
                print(f'Difference at line {i}')
                print(f'File 1: {line1}File 2: {line2}')
                flag = 1

            if not line1:
                return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compare two text files.')
    parser.add_argument('file1', help='The first text file to compare.')
    parser.add_argument('file2', help='The second text file to compare.')

    args = parser.parse_args()

    compare_txt_files(args.file1, args.file2)
