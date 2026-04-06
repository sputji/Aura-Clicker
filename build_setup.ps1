param(
    [string]$ProjectRoot = "."
)

$ErrorActionPreference = 'Stop'
Set-Location $ProjectRoot

$venvPython = Join-Path $PWD ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Venv introuvable: $venvPython"
}

& $venvPython -m pyinstaller --noconfirm --clean --windowed --name "Aura-Clicker" --icon "aura_clicker\assets\logo_aura_clicker.ico" --add-data "aura_clicker\assets;aura_clicker\assets" main.py

$isccCandidates = @(
    "E:\Logiciel\Innosetup\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)

$iscc = $isccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $iscc) {
    throw "ISCC.exe introuvable. Installe Inno Setup 6."
}

Set-Location (Join-Path $PWD "installer")
& $iscc "AuraClicker.iss"

Write-Output "Setup généré: $(Join-Path (Split-Path $PWD -Parent) 'dist-installer\Aura-Clicker-Setup-0.1.4.exe')"
