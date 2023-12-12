#!/bin/bash

# Set the test number as a variable
test_number=7

# cd CSC3050_P4 || exit
python convert.py cpu_test/machine_code${test_number}.txt CPU_instruction.bin t2b

make clean
make test

echo ""
python convert.py data.bin data.out b2t
python cmp.py data.out cpu_test/DATA_RAM${test_number}.txt
