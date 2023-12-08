make clean
make
echo ""
echo "Compare: "
cmp data.bin bin/instructions1.bin
python cmp.py data.bin bin/instructions1.bin
