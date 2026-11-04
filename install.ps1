param(
    [string]$PythonExe,
    [switch]$NoStartup
)
$ErrorActionPreference = 'Stop'
if (-not $PythonExe) {
    $candidates = @()
    $py = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($py) {
        try {
            $detected = & $py.Source -3 -c 'import sys; print(sys.executable)' 2>$null
            if ($LASTEXITCODE -eq 0) { $candidates += $detected }
        } catch { }
    }
    $candidates += Get-ChildItem -Path "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe" -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -ExpandProperty FullName
    $python = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($python) { $candidates += $python.Source }
    foreach ($candidate in $candidates) {
        try {
            & $candidate -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>$null
            if ($LASTEXITCODE -eq 0) { $PythonExe = $candidate; break }
        } catch { continue }
    }
}
if (-not $PythonExe) { throw 'Instale Python 3.10+ de 64 bits ou informe -PythonExe com o caminho do python.exe.' }
& $PythonExe (Join-Path $PSScriptRoot 'install.py')
if ($LASTEXITCODE -ne 0) { throw 'Falha na instalacao. Confira a mensagem acima.' }
$base = Join-Path $env:LOCALAPPDATA 'Cove'
$shell = New-Object -ComObject WScript.Shell
$links = @(Join-Path ([Environment]::GetFolderPath('Desktop')) 'Ativar Cove por voz.lnk')
if (-not $NoStartup) { $links += Join-Path ([Environment]::GetFolderPath('Startup')) 'Cove Voz.lnk' }
foreach ($path in $links) {
    $shortcut = $shell.CreateShortcut($path)
    $shortcut.TargetPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
    $shortcut.Arguments = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + (Join-Path $base 'start.ps1') + '"'
    $shortcut.WorkingDirectory = $base
    $shortcut.WindowStyle = 7
    $shortcut.Description = 'Ativacao local do Cove por voz'
    $shortcut.Save()
}
Write-Host 'Instalacao concluida. Abra Ativar Cove por voz na Area de Trabalho para iniciar agora.'
if (-not $NoStartup) { Write-Host 'O ouvinte tambem iniciara automaticamente no proximo login do Windows.' }
