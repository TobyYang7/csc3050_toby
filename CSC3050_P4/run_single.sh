#!/bin/bash

python convert.py cpu_test/machine_code8.txt CPU_instruction.bin

make clean
make test

echo ""
python convert.py data.bin data.out
python cmp.py data.out cpu_test/DATA_RAM8.txt