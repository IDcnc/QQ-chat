#!/usr/bin/env python3
# pack_en.py - Package QQBotManager (English only, no encoding issues)

import os
import sys
import subprocess
import shutil

def run_cmd(cmd, ignore_error=False):
    """Run command and return True if success"""
    print(f"\n[CMD] {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if not ignore_error and result.returncode != 0:
        print(f"[ERROR] Command failed with code {result.returncode}")
        return False
    return True

def main():
    print("=" * 60)
    print("Package QQBotManager (Official Version)")
    print("=" * 60)
    
    # Set working directory
    work_dir = r"C:\Users\ID\.qclaw\workspace\qq-bot-pywebview"
    os.chdir(work_dir)
    print(f"\n[INFO] Working directory: {work_dir}")
    
    # Step 1: Check Python
    print("\n[1/6] Checking Python...")
    if not run_cmd("python --version"):
        print("[ERROR] Python not found! Please install Python first.")
        input("\nPress Enter to exit...")
        return
    
    # Step 2: Install qq-botpy
    print("\n[2/6] Installing qq-botpy v1.2.1...")
    if run_cmd("python -m pip install qq-botpy==1.2.1", ignore_error=True):
        print("[INFO] qq-botpy installed successfully")
    else:
        print("[WARNING] qq-botpy installation failed, will use simulation mode")
    
    # Step 3: Install PyInstaller
    print("\n[3/6] Installing PyInstaller...")
    if not run_cmd("python -m pip install pyinstaller", ignore_error=True):
        print("[ERROR] PyInstaller installation failed!")
        input("\nPress Enter to exit...")
        return
    
    # Step 4: Kill old process
    print("\n[4/6] Killing old process...")
    run_cmd("taskkill /f /im QQBotManager.exe", ignore_error=True)
    
    # Step 5: Clean old files
    print("\n[5/6] Cleaning old files...")
    for d in ["build", "dist"]:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"  Deleted: {d}")
    if os.path.exists("QQBotManager.spec"):
        os.remove("QQBotManager.spec")
        print("  Deleted: QQBotManager.spec")
    
    # Step 6: Run PyInstaller
    print("\n[6/6] Running PyInstaller...")
    cmd = (
        "python -m PyInstaller "
        "--onefile "
        "--noconsole "
        '--add-data "index.html;." '
        "--name QQBotManager "
        '--distpath "C:\\Users\\ID\\Desktop\\bbb" '
        "main.py"
    )
    if run_cmd(cmd):
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("Output: C:\\Users\\ID\\Desktop\\bbb\\QQBotManager.exe")
        print("=" * 60)
    else:
        print("\n[ERROR] Packaging failed!")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
