cd "/home/parallels/toby_dev/csc3050_toby/CSC3050_P2"
python3 simulator.py Example_test_cases/test_basic-hello-world/test.asm Example_test_cases/test_basic-hello-world/test.txt Example_test_cases/test_basic-hello-world/test_checkpts.txt Example_test_cases/test_basic-hello-world/test.in test.out

a=0
cmp register_$a.bin Example_test_cases/test_basic-hello-world/correct_dump/register_$a.bin
if [ $? -eq 1 ]
then
    hexdump register_$a.bin > register_$a.txt
    hexdump Example_test_cases/test_basic-hello-world/correct_dump/register_$a.bin > correct_register_$a.txt
fi
cmp memory_$a.bin Example_test_cases/test_basic-hello-world/correct_dump/memory_$a.bin
if [ $? -eq 1 ]
then
    hexdump memory_$a.bin > memory_$a.txt
    hexdump Example_test_cases/test_basic-hello-world/correct_dump/memory_$a.bin > correct_memory_$a.txt
fi


cmp test.out Example_test_cases/test_basic-hello-world/test_correct.out
if [ $? -eq 1 ]
then
    echo "Final Result: FAIL"
else
    echo "Final Result: CORRECT"
fi