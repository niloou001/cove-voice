@echo off
start "" "https://chatgpt.com/"
where codex >nul 2>nul
if not errorlevel 1 start "" powershell.exe -NoExit -Command "Set-Location -LiteralPath $env:USERPROFILE; codex"
