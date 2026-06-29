$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

if (Get-Command doctor-link -ErrorAction SilentlyContinue) {
    doctor-link wizard
    exit $LASTEXITCODE
}

$venvDoctorLink = Join-Path (Get-Location) ".venv\Scripts\doctor-link.exe"
if (Test-Path $venvDoctorLink) {
    & $venvDoctorLink wizard
    exit $LASTEXITCODE
}

Write-Host "Doctor link is not installed."
Write-Host "Next step: pip install -e ."
exit 1