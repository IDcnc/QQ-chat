#!/usr/bin/env python3
# pack_simple.py - 超简单打包脚本

import os
import sys
import subprocess

# 设置工作目录
os.chdir(r"C:\Users\ID\.qclaw\workspace\qq-bot-pywebview")

print("=" * 60)
print("QQBotManager 打包工具")
print("=" * 60)

# 步骤 1: 安装依赖
print("\n[1/3] 安装依赖...")
cmds = [
    "python -m pip install qq-botpy==1.2.1",
    "python -m pip install pyinstaller"
]
for cmd in cmds:
    print(f"执行: {cmd}")
    subprocess.run(cmd, shell=True)

# 步骤 2: 关闭旧进程
print("\n[2/3] 关闭旧进程...")
subprocess.run("taskkill /f /im QQBotManager.exe", shell=True, capture_output=True)

# 步骤 3: 打包
print("\n[3/3] 开始打包...")
cmd = (
    "python -m PyInstaller "
    "--onefile "
    "--noconsole "
    '--add-data "index.html;." '
    "--name QQBotManager "
    '--distpath "C:\\Users\\ID\\Desktop\\bbb" '
    "main.py"
)
print(f"执行: {cmd}")
result = subprocess.run(cmd, shell=True)

if result.returncode == 0:
    print("\n" + "=" * 60)
    print("✅ 打包成功！")
    print("输出路径: C:\\Users\\ID\\Desktop\\bbb\\QQBotManager.exe")
    print("=" * 60)
else:
    print("\n❌ 打包失败，请检查错误信息")

input("\n按回车键退出...")
