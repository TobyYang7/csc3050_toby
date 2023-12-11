import argparse


def compare_txt_files(file1, file2):
    flag = 0
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        i = 1
        while True:
            line1 = f1.readline().strip()
            line2 = f2.readline().strip()

            if not line1 or not line2:
                break

            # Convert binary strings to decimal
            num1 = int(line1, 2) - (1 << 32) if line1[0] == '1' else int(line1, 2)
            num2 = int(line2, 2) - (1 << 32) if line2[0] == '1' else int(line2, 2)

            if num1 != num2:
                print(f'DATA_MEM [{i-1}]')
                print(f'MY : {num1}\nANS: {num2}')
                flag = 1

            i += 1

    if flag == 0:
        print('>>>> Correct >>>>')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compare two text files.')
    parser.add_argument('file1', help='The first text file to compare.')
    parser.add_argument('file2', help='The second text file to compare.')

    args = parser.parse_args()

    compare_txt_files(args.file1, args.file2)
