#!/bin/bash

for i in {1..8}
do
    echo "----------Task ${i}---------"
    python convert.py cpu_test/machine_code${i}.txt CPU_instruction.bin

    make clean
    make test

    echo ""
    python convert.py data.bin data.out
    python cmp.py data.out cpu_test/DATA_RAM${i}.txt
done