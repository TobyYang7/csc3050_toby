#!/bin/bash

# 指定要清除的目录
dir="/home/parallels/toby_dev/csc3050_toby/CSC3050_P2"

# 清除所有 .bin 和 .out 文件
find "$dir" -type f \( -name "*.bin" -o -name "*.out" \) -delete

echo "All .bin and .out files have been deleted."