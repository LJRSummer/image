#!/bin/bash

# 进入工作目录（系统会自动设置到 /app）
cd "$(dirname "$0")"

# 设置中文字符支持（防止文件名乱码）
export LANG=C.UTF-8

# 执行您的检测脚本（图片.py）
python 图片.py
