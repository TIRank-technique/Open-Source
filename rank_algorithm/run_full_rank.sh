#!/bin/bash

# 检查是否提供了两个参数
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_file> <output_file>"
    exit 1
fi

# 获取参数
input_file=$1
output_file=$2

# 执行 Python 脚本
python3 DivideSet.py
python3 TagTheMatrix.py "$input_file"
python3 GenScoreCard.py "$input_file"
python3 ScoreTheMatrix.py "$input_file" "$output_file"
