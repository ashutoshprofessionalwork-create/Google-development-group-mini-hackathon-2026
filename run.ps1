# VayuNetra One-Click Launcher
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $projectDir

Write-Host "Launching VayuNetra Backend API..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$projectDir\backend'; python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 2

Write-Host "Opening VayuNetra Portal..." -ForegroundColor Green
Start-Process "$projectDir\frontend\frontend.html"

Write-Host "VayuNetra launched successfully!" -ForegroundColor Cyan
