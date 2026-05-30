@echo off
chcp 65001 > nul
echo ===================================
echo 打包 QQBotManager 正式环境 v2
echo ===================================

cd /d C:\Users\ID\.qclaw\workspace\qq-bot-pywebview

echo [1/5] 检查 Python...
python --version
if errorlevel 1 (
    echo [错误] Python 未安装！
    pause
    exit /b 1
)

echo [2/5] 安装 qq-botpy...
python -m pip install qq-botpy==1.2.1 -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo [警告] qq-botpy 安装失败，将使用模拟模式
) else (
    echo [信息] qq-botpy 安装成功
)

echo [3/5] 安装 PyInstaller...
python -m pip install pyinstaller
if errorlevel 1 (
    echo [错误] PyInstaller 安装失败！
    pause
    exit /b 1
)

echo [4/5] 关闭旧进程...
taskkill /f /im QQBotManager.exe > nul 2>&1

echo [5/5] 执行打包...
python -m PyInstaller --onefile --noconsole --add-data "index.html;." --name QQBotManager --distpath "C:\Users\ID\Desktop\bbb" main.py

if errorlevel 1 (
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo.
echo ===================================
echo 打包成功！
echo 输出路径: C:\Users\ID\Desktop\bbb\QQBotManager.exe
echo ===================================
echo.
pause
