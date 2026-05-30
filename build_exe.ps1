# build_exe.ps1 - 打包 QQBotManager EXE

$workDir = "C:\Users\ID\.qclaw\workspace\qq-bot-pywebview"
Set-Location $workDir

Write-Host "=== 开始打包 QQBotManager ===" -ForegroundColor Cyan
Write-Host "工作目录: $workDir" -ForegroundColor Gray

# 使用 venv310 中的 python 执行 PyInstaller
$pythonExe = "$workDir\venv310\Scripts\python.exe"
Write-Host "Python 路径: $pythonExe" -ForegroundColor Gray

# 先关闭可能占着 EXE 的进程
Write-Host "检查是否有旧进程..." -ForegroundColor Yellow
$oldExe = "C:\Users\ID\Desktop\bbb\QQBotManager.exe"
if (Test-Path $oldExe) {
    $processes = Get-Process | Where-Object {$_.Path -eq $oldExe}
    if ($processes) {
        Write-Host "关闭旧进程..." -ForegroundColor Yellow
        Stop-Process -Id $processes.Id -Force
        Start-Sleep -Seconds 2
    }
}

# 执行打包
Write-Host "执行 PyInstaller..." -ForegroundColor Cyan
& $pythonExe -m PyInstaller `
    --onefile `
    --noconsole `
    --add-data "index.html;." `
    --name QQBotManager `
    --distpath "C:\Users\ID\Desktop\bbb" `
    main.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "=== 打包成功！===" -ForegroundColor Green
    Write-Host "输出路径: C:\Users\ID\Desktop\bbb\QQBotManager.exe" -ForegroundColor Green
} else {
    Write-Host "=== 打包失败，退出码: $LASTEXITCODE ===" -ForegroundColor Red
}

Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
