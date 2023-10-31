cd "/home/parallels/toby_dev/csc3050_toby/CSC3050_P2"
clear
python3 simulator.py Example_test_cases/many/many.asm Example_test_cases/many/many.txt Example_test_cases/many/many_checkpts.txt Example_test_cases/many/many.in many.out

values=(0 23 97)

for a in "${values[@]}"
do
    cmp register_$a.bin Example_test_cases/many/correct_dump/register_$a.bin
    if [ $? -eq 1 ]
    then
        hexdump register_$a.bin > register_$a.txt
        hexdump Example_test_cases/many/correct_dump/register_$a.bin > correct_register_$a.txt
        python3 reg.py Example_test_cases/many/correct_dump/register_$a.bin register_$a.bin $a
        cmp true_reg_$a.txt my_$a.txt
    fi

    cmp memory_$a.bin Example_test_cases/many/correct_dump/memory_$a.bin
    if [ $? -eq 1 ]
    then
        hexdump memory_$a.bin > memory_$a.txt
        hexdump Example_test_cases/many/correct_dump/memory_$a.bin > correct_memory_$a.txt
    fi
done

cmp many.out Example_test_cases/many/many_correct.out
if [ $? -eq 1 ]
then
    echo "Final Result: FAIL"
else
    echo "Final Result: CORRECT"
fi