@echo off
chcp 437 > nul
echo ==========
echo Package QQBotManager
echo ==========

cd C:\Users\ID\.qclaw\workspace\qq-bot-pywebview

echo [Step 1] Check Python...
python --version
if errorlevel 1 goto :error

echo [Step 2] Install qq-botpy...
python -m pip install qq-botpy==1.2.1
if errorlevel 1 echo [Warning] qq-botpy install failed

echo [Step 3] Install PyInstaller...
python -m pip install pyinstaller
if errorlevel 1 goto :error

echo [Step 4] Kill old process...
taskkill /f /im QQBotManager.exe > nul 2>&1

echo [Step 5] Clean old files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist QQBotManager.spec del /q QQBotManager.spec

echo [Step 6] Run PyInstaller...
python -m PyInstaller --onefile --noconsole --add-data "index.html;." --name QQBotManager --distpath "C:\Users\ID\Desktop\bbb" main.py
if errorlevel 1 goto :error

echo.
echo ==========
echo Success!
echo Output: C:\Users\ID\Desktop\bbb\QQBotManager.exe
echo ==========
goto :end

:error
echo.
echo ==========
echo Error occurred!
echo ==========

:end
pause
