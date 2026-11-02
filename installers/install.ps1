# OpenPalm — fully automatic installer for Windows.
# Clones, installs deps, starts the server, and opens the browser.
# Usage: irm https://raw.githubusercontent.com/RechargedIdeas/OpenPalm/main/installers/install.ps1 | iex

$ErrorActionPreference = "Stop"
$Prefix = "$env:USERPROFILE\.openpalm"
$Port = 8765
$NoDeps = $args -contains "--no-deps"

Write-Host "OpenPalm — automatic install"
New-Item -ItemType Directory -Force -Path $Prefix | Out-Null

if (-not $NoDeps) {
  Write-Host "Installing system dependencies…"
  if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
  }
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements
  }
}

if (Test-Path "$Prefix\OpenPalm") {
  git -C "$Prefix\OpenPalm" pull --ff-only
} else {
  git clone --depth 1 https://github.com/RechargedIdeas/OpenPalm.git "$Prefix\OpenPalm"
}

Set-Location "$Prefix\OpenPalm\sidecar"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -q --upgrade pip
if (Test-Path requirements.txt) { pip install -q -r requirements.txt } else { pip install -q fastapi uvicorn }

$launcher = @"
@echo off
cd /d $Prefix\OpenPalm\sidecar
call .venv\Scripts\activate.bat
set OPENPALM_CPU_ONLY=1
python -m uvicorn harness_sidecar.api.server:app --host 127.0.0.1 --port $Port
"@
Set-Content -Path "$Prefix\openpalm.bat" -Value $launcher

Write-Host "Starting OpenPalm…"
Start-Process -FilePath "$Prefix\openpalm.bat" -WindowStyle Hidden -RedirectStandardOutput "$Prefix\openpalm.log" -RedirectStandardError "$Prefix\openpalm.err"

Start-Sleep -Seconds 5
Start-Process "http://127.0.0.1:$Port"

Write-Host "OpenPalm is running at http://127.0.0.1:$Port"
Write-Host "Log: $Prefix\openpalm.log"
