# Builds InkFlowBuilder.exe (one file, windowed) with PyInstaller from the venv in C:\__DEV.
# Usage : powershell -ExecutionPolicy Bypass -File build_exe.ps1
$ErrorActionPreference = "Stop"
$builder = $PSScriptRoot
$templates = Join-Path (Split-Path $builder) "templates"
$exeRoot = "C:\__DEV\cyberpunk\ink_flow\exe"
$venv = Join-Path $exeRoot "venv"
if (-not (Test-Path (Join-Path $venv "Scripts\pyinstaller.exe"))) {
    python -m venv $venv
    & (Join-Path $venv "Scripts\python.exe") -m pip install --quiet --disable-pip-version-check pyinstaller
}
# numpy : the arm conversion (inkflow\armconv.py, 1.4.0) ; pinned so a rebuild bundles the same code
& (Join-Path $venv "Scripts\python.exe") -m pip install --quiet --disable-pip-version-check "numpy==2.4.6"
$version = (Select-String -Path (Join-Path $builder "inkflow\__init__.py") -Pattern 'VERSION = "([^"]+)"').Matches[0].Groups[1].Value
& (Join-Path $venv "Scripts\pyinstaller.exe") --noconfirm --clean --onefile --windowed `
    --name "InkFlowBuilder" `
    --add-data "$templates;templates" `
    --distpath (Join-Path $exeRoot "dist") `
    --workpath (Join-Path $exeRoot "work") `
    --specpath (Join-Path $exeRoot "work") `
    (Join-Path $builder "InkFlowBuilder.py")
$exe = Join-Path $exeRoot "dist\InkFlowBuilder.exe"
$item = Get-Item $exe
$sha = (Get-FileHash $exe -Algorithm SHA256).Hash
"InkFlowBuilder $version : $exe ($([math]::Round($item.Length / 1MB, 1)) MB) SHA-256 $sha"
