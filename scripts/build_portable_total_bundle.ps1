param(
    [string]$OutputRoot = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $OutputRoot = Join-Path $repoRoot "portable"
}

$envPyInstaller = Join-Path $repoRoot "env\Scripts\pyinstaller.exe"
$envPip = Join-Path $repoRoot "env\Scripts\pip.exe"
if (!(Test-Path $envPyInstaller)) {
    throw "No se encontro PyInstaller en env\Scripts\pyinstaller.exe"
}
if (!(Test-Path $envPip)) {
    throw "No se encontro pip en env\Scripts\pip.exe"
}

$frontDir = Join-Path $repoRoot "frontend"
$buildRoot = Join-Path $repoRoot "build\portable_total"
$pyiSpecRoot = Join-Path $buildRoot "spec"
$pyiWorkRoot = Join-Path $buildRoot "work"
$pyiDistRoot = Join-Path $buildRoot "dist"
$bundleRoot = Join-Path $OutputRoot "SistemasLaHuellaPortableTotal"

Write-Host "==> Build frontend (vite build)"
Push-Location $frontDir
try {
    & npm.cmd run build
}
finally {
    Pop-Location
}

Write-Host "==> Ensure portable build dependencies"
& $envPip install -r (Join-Path $repoRoot "requirements-api.txt")

Write-Host "==> Build portable API executable"
& $envPyInstaller `
    --noconfirm `
    --clean `
    --onedir `
    --name "lahuella-api-portable" `
    --distpath $pyiDistRoot `
    --workpath (Join-Path $pyiWorkRoot "api") `
    --specpath $pyiSpecRoot `
    --paths $repoRoot `
    --icon (Join-Path $repoRoot "application\icon.ico") `
    --collect-all uvicorn `
    --collect-all fastapi `
    --collect-all anyio `
    --collect-all starlette `
    --collect-all paramiko `
    (Join-Path $repoRoot "portable_api_entry.py")

Write-Host "==> Build portable web executable"
& $envPyInstaller `
    --noconfirm `
    --clean `
    --onedir `
    --name "lahuella-web-portable" `
    --distpath $pyiDistRoot `
    --workpath (Join-Path $pyiWorkRoot "web") `
    --specpath $pyiSpecRoot `
    --paths $repoRoot `
    --icon (Join-Path $repoRoot "application\icon.ico") `
    (Join-Path $repoRoot "portable_web_entry.py")

Write-Host "==> Recreate bundle folder: $bundleRoot"
if (Test-Path $bundleRoot) {
    Remove-Item $bundleRoot -Recurse -Force
}

New-Item -ItemType Directory -Path $bundleRoot | Out-Null
New-Item -ItemType Directory -Path (Join-Path $bundleRoot "data") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $bundleRoot ".run") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $bundleRoot "scripts") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $bundleRoot "runtime") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $bundleRoot "runtime\api") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $bundleRoot "runtime\web") | Out-Null

Write-Host "==> Copy runtime files"
$filesToCopy = @(
    "logoLH.webp",
    "application\icon.ico",
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
        $destination = if ($relative -eq "application\icon.ico") {
            Join-Path $bundleRoot "icon.ico"
        }
        else {
            Join-Path $bundleRoot ([IO.Path]::GetFileName($relative))
        }
        Copy-Item $source -Destination $destination -Force
    }
}

Write-Host "==> Copy frontend dist"
Copy-Item (Join-Path $frontDir "dist") -Destination (Join-Path $bundleRoot "frontend") -Recurse -Force

Write-Host "==> Copy executables"
Copy-Item (Join-Path $pyiDistRoot "lahuella-api-portable\*") -Destination (Join-Path $bundleRoot "runtime\api") -Recurse -Force
Copy-Item (Join-Path $pyiDistRoot "lahuella-web-portable\*") -Destination (Join-Path $bundleRoot "runtime\web") -Recurse -Force

Write-Host "==> Copy optional data"
$optionalData = @(
    "data\hosts.json",
    "data\audit_events.json",
    "data\infra_map.json"
)

foreach ($relative in $optionalData) {
    $source = Join-Path $repoRoot $relative
    if (Test-Path $source) {
        $destination = Join-Path (Join-Path $bundleRoot "data") ([IO.Path]::GetFileName($relative))
        Copy-Item $source -Destination $destination -Force
    }
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
Write-Host "Bundle portable total listo:"
Write-Host $bundleRoot
Write-Host ""
Write-Host "Inicio silencioso: start_portable_silent.vbs"
Write-Host "Parada silenciosa: stop_portable_silent.vbs"
Write-Host "No requiere Python ni Node en la PC destino."
