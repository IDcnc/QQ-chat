@echo off
chcp 65001 > nul
echo ===================================
echo 打包 QQBotManager 正式环境
echo ===================================

REM 设置工作目录
cd /d C:\Users\ID\.qclaw\workspace\qq-bot-pywebview

REM 检查 Python 是否可用
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] Python 未安装或不在 PATH 中
    pause
    exit /b 1
)

echo [信息] 使用 Python:
python --version

REM 安装 qq-botpy（正式环境必需）
echo [信息] 检查 qq-botpy...
python -c "import botpy" > nul 2>&1
if errorlevel 1 (
    echo [信息] 正在安装 qq-botpy v1.2.1...
    python -m pip install qq-botpy==1.2.1 -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo [错误] 安装 qq-botpy 失败！
        pause
        exit /b 1
    )
) else (
    echo [信息] qq-botpy 已安装
)

REM 检查 PyInstaller 是否安装
echo [信息] 检查 PyInstaller...
python -m PyInstaller --version > nul 2>&1
if errorlevel 1 (
    echo [信息] 正在安装 PyInstaller...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo [错误] 安装 PyInstaller 失败！
        pause
        exit /b 1
    )
)

REM 关闭可能占用 EXE 的进程
echo [信息] 检查是否有旧进程...
taskkill /f /im QQBotManager.exe > nul 2>&1

REM 清理旧的构建文件
echo [信息] 清理旧文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist QQBotManager.spec del /q QQBotManager.spec

REM 执行打包
echo [信息] 开始打包正式环境...
python -m PyInstaller ^
    --onefile ^
    --noconsole ^
    --add-data "index.html;." ^
    --name QQBotManager ^
    --distpath "C:\Users\ID\Desktop\bbb" ^
    main.py

if errorlevel 1 (
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo.
echo ===================================
echo 打包成功！
echo 输出路径: C:\Users\ID\Desktop\bbb\QQBotManager.exe
echo.
echo 注意: 此版本包含 qq-botpy 正式环境
echo ===================================
echo.
pause
