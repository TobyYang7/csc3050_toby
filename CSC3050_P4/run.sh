#!/bin/bash

# cd CSC3050_P4 || exit
for i in {1..8}; do
    echo "------------------TEST ${i}----------------------"
    python convert.py cpu_test/machine_code${i}.txt CPU_instruction.bin t2b

    make clean
    make test

    echo ""
    python convert.py data.bin data.out b2t
    python cmp.py data.out cpu_test/DATA_RAM${i}.txt
done
