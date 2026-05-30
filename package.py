#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQBotManager 正式环境打包脚本
"""

import os
import sys
import subprocess
import shutil

def run_cmd(cmd, check=True):
    """执行命令并处理输出"""
    print(f"\n[执行] {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if check and result.returncode != 0:
        print(f"[错误] 命令执行失败，退出码: {result.returncode}")
        sys.exit(1)
    return result

def main():
    print("=" * 50)
    print("打包 QQBotManager 正式环境")
    print("=" * 50)
    
    # 设置工作目录
    work_dir = r"C:\Users\ID\.qclaw\workspace\qq-bot-pywebview"
    os.chdir(work_dir)
    print(f"\n[信息] 工作目录: {work_dir}")
    
    # 1. 检查 Python
    print("\n[1/6] 检查 Python...")
    run_cmd("python --version")
    
    # 2. 安装 qq-botpy
    print("\n[2/6] 安装 qq-botpy v1.2.1...")
    run_cmd("python -m pip install qq-botpy==1.2.1 -i https://pypi.tuna.tsinghua.edu.cn/simple", check=False)
    
    # 3. 安装 PyInstaller
    print("\n[3/6] 安装 PyInstaller...")
    run_cmd("python -m pip install pyinstaller", check=False)
    
    # 4. 关闭旧进程
    print("\n[4/6] 关闭旧进程...")
    run_cmd("taskkill /f /im QQBotManager.exe", check=False)
    
    # 5. 清理旧文件
    print("\n[5/6] 清理旧构建文件...")
    for d in ["build", "dist"]:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"  已删除: {d}")
    if os.path.exists("QQBotManager.spec"):
        os.remove("QQBotManager.spec")
        print("  已删除: QQBotManager.spec")
    
    # 6. 执行打包
    print("\n[6/6] 执行打包...")
    cmd = (
        "python -m PyInstaller "
        "--onefile "
        "--noconsole "
        '--add-data "index.html;." '
        "--name QQBotManager "
        '--distpath "C:\\Users\\ID\\Desktop\\bbb" '
        "main.py"
    )
    run_cmd(cmd)
    
    print("\n" + "=" * 50)
    print("打包成功！")
    print("输出路径: C:\\Users\\ID\\Desktop\\bbb\\QQBotManager.exe")
    print("=" * 50)
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
