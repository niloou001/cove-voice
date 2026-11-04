$ErrorActionPreference = 'Stop'
$base = Join-Path $env:LOCALAPPDATA 'Cove'
$listener = Join-Path $base 'listener.py'
Get-CimInstance Win32_Process -Filter "Name = 'pythonw.exe'" | Where-Object {
    $_.CommandLine -and $_.CommandLine.Contains($listener)
} | ForEach-Object {
    Stop-Process -Id $_.ProcessId -ErrorAction SilentlyContinue
}
Start-Sleep -Milliseconds 700
Start-Process -FilePath (Join-Path $base 'venv\Scripts\pythonw.exe') -ArgumentList ('"' + $listener + '"') -WorkingDirectory $base -WindowStyle Hidden
