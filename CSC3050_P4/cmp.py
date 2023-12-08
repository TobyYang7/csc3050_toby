import argparse

def compare_bin_files(file1, file2):
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        i = 0
        while True:
            block1 = f1.read(4)
            block2 = f2.read(4)

            # if block1 != block2:
            #     print(f'Difference at 32-bit block {i}')

            if not block1:
                return

            i += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compare two binary files.')
    parser.add_argument('file1', help='The first binary file to compare.')
    parser.add_argument('file2', help='The second binary file to compare.')

    args = parser.parse_args()

    compare_bin_files(args.file1, args.file2)