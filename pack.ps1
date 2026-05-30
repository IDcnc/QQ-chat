# pack.ps1 - 打包 QQBotManager 正式环境
# 使用方法: 在 PowerShell 中运行 .\pack.ps1

Write-Host "==========" -ForegroundColor Cyan
Write-Host "Package QQBotManager" -ForegroundColor Cyan
Write-Host "==========" -ForegroundColor Cyan

$workDir = "C:\Users\ID\.qclaw\workspace\qq-bot-pywebview"
Set-Location $workDir

# Step 1: Check Python
Write-Host "`n[Step 1] Check Python..." -ForegroundColor Yellow
& python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "[Error] Python not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 2: Install qq-botpy
Write-Host "`n[Step 2] Install qq-botpy..." -ForegroundColor Yellow
& python -m pip install qq-botpy==1.2.1 -i https://pypi.tuna.tsinghua.edu.cn/simple
if ($LASTEXITCODE -ne 0) {
    Write-Host "[Warning] qq-botpy installation failed, will use simulation mode" -ForegroundColor Yellow
}

# Step 3: Install PyInstaller
Write-Host "`n[Step 3] Install PyInstaller..." -ForegroundColor Yellow
& python -m pip install pyinstaller
if ($LASTEXITCODE -ne 0) {
    Write-Host "[Error] PyInstaller installation failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 4: Kill old process
Write-Host "`n[Step 4] Kill old process..." -ForegroundColor Yellow
Get-Process -Name "QQBotManager" -ErrorAction SilentlyContinue | Stop-Process -Force

# Step 5: Clean old files
Write-Host "`n[Step 5] Clean old files..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Path "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item -Path "dist" -Recurse -Force }
if (Test-Path "QQBotManager.spec") { Remove-Item -Path "QQBotManager.spec" -Force }

# Step 6: Run PyInstaller
Write-Host "`n[Step 6] Run PyInstaller..." -ForegroundColor Yellow
$cmd = "python -m PyInstaller --onefile --noconsole --add-data `"index.html;.`" --name QQBotManager --distpath `"C:\Users\ID\Desktop\bbb`" main.py"
Invoke-Expression $cmd

if ($LASTEXITCODE -ne 0) {
    Write-Host "[Error] Packaging failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`n==========" -ForegroundColor Green
Write-Host "Success!" -ForegroundColor Green
Write-Host "Output: C:\Users\ID\Desktop\bbb\QQBotManager.exe" -ForegroundColor Green
Write-Host "==========" -ForegroundColor Green

Read-Host "`nPress Enter to exit"
