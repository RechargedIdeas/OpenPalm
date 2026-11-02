# OpenPalm installer for Windows — auto-downloads dependencies.
# Usage: irm https://raw.githubusercontent.com/RechargedIdeas/OpenPalm/main/installers/install.ps1 | iex

$ErrorActionPreference = "Stop"
$Prefix = "$env:USERPROFILE\.openpalm"
$NoDeps = $args -contains "--no-deps"

Write-Host "OpenPalm installer (Windows)"
Write-Host "  prefix: $Prefix"

New-Item -ItemType Directory -Force -Path $Prefix | Out-Null

if (-not $NoDeps) {
  Write-Host "Installing dependencies…"
  if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
  }
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements
  }
}

if (Test-Path "$Prefix\OpenPalm") {
  Write-Host "Updating…"
  git -C "$Prefix\OpenPalm" pull --ff-only
} else {
  Write-Host "Cloning…"
  git clone --depth 1 https://github.com/RechargedIdeas/OpenPalm.git "$Prefix\OpenPalm"
}

Set-Location "$Prefix\OpenPalm\sidecar"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -q --upgrade pip
if (Test-Path requirements.txt) { pip install -q -r requirements.txt } else { pip install -q fastapi uvicorn }

$launcher = @"
@echo off
cd /d %USERPROFILE%\.openpalm\OpenPalm\sidecar
call .venv\Scripts\activate.bat
set OPENPALM_CPU_ONLY=1
python -m uvicorn harness_sidecar.api.server:app --host 127.0.0.1 --port 8765
"@
Set-Content -Path "$Prefix\openpalm.bat" -Value $launcher

Write-Host ""
Write-Host "Installed. Run: $Prefix\openpalm.bat"
Write-Host "Then open http://127.0.0.1:8765"
