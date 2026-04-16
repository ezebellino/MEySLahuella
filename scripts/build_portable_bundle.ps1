param(
    [string]$OutputRoot = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $OutputRoot = Join-Path $repoRoot "portable"
}

$bundleRoot = Join-Path $OutputRoot "SistemasLaHuellaPortable"
$frontDir = Join-Path $repoRoot "frontend"

Write-Host "==> Build frontend (vite build)"
Push-Location $frontDir
try {
    & npm.cmd run build
}
finally {
    Pop-Location
}

Write-Host "==> Recreate bundle folder: $bundleRoot"
if (Test-Path $bundleRoot) {
    Remove-Item $bundleRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $bundleRoot | Out-Null
New-Item -ItemType Directory -Path (Join-Path $bundleRoot "data") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $bundleRoot ".run") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $bundleRoot "scripts") | Out-Null

Write-Host "==> Copy runtime files"
$filesToCopy = @(
    "api_server.py",
    "requirements-api.txt",
    "logoLH.webp",
    "icon.ico",
    "check_estacion_peaje.md",
    "validacion_estacion_peaje.md",
    "GUIA_RAPIDA_ESTACION.md",
    "MANUAL_USO_Y_ALCANCE.md",
    "PORTABLE_PENDRIVE.md",
    "create_desktop_shortcut.ps1",
    "install_desktop_shortcuts.ps1",
    "Instalar en Escritorio.bat",
    "start_portable_background.ps1",
    "stop_portable_background.ps1",
    "start_portable_silent.vbs",
    "stop_portable_silent.vbs",
    "start_portable.bat",
    "stop_portable.bat"
)

foreach ($relative in $filesToCopy) {
    $source = Join-Path $repoRoot $relative
    if (Test-Path $source) {
        Copy-Item $source -Destination (Join-Path $bundleRoot $relative) -Force
    }
}

Write-Host "==> Copy frontend dist"
Copy-Item (Join-Path $frontDir "dist") -Destination (Join-Path $bundleRoot "frontend") -Recurse -Force

Write-Host "==> Copy optional data"
$hostsFile = Join-Path $repoRoot "data\hosts.json"
if (Test-Path $hostsFile) {
    Copy-Item $hostsFile -Destination (Join-Path $bundleRoot "data\hosts.json") -Force
}

$auditFile = Join-Path $repoRoot "data\audit_events.json"
if (Test-Path $auditFile) {
    Copy-Item $auditFile -Destination (Join-Path $bundleRoot "data\audit_events.json") -Force
}

$infraFile = Join-Path $repoRoot "data\infra_map.json"
if (Test-Path $infraFile) {
    Copy-Item $infraFile -Destination (Join-Path $bundleRoot "data\infra_map.json") -Force
}

Write-Host "==> Copy support scripts"
$scriptFiles = @(
    "collect_network_diagnostics.ps1",
    "test_windows_credentials.ps1",
    "preload_vias.ps1"
)
foreach ($sf in $scriptFiles) {
    $src = Join-Path $repoRoot "scripts\$sf"
    if (Test-Path $src) {
        Copy-Item $src -Destination (Join-Path $bundleRoot "scripts\$sf") -Force
    }
}

Write-Host ""
Write-Host "Bundle portable listo:"
Write-Host $bundleRoot
Write-Host ""
Write-Host "Inicio silencioso: start_portable_silent.vbs"
Write-Host "Parada silenciosa: stop_portable_silent.vbs"
