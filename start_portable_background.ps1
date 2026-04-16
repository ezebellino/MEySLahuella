param(
    [switch]$ForceRestart
)

$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$frontDist = Join-Path $root "frontend\dist"
$frontStaticRoot = if (Test-Path $frontDist) { $frontDist } else { Join-Path $root "frontend" }
$runDir = Join-Path $root ".run"
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

$apiPidFile = Join-Path $runDir "lahuella-portable-api.pid"
$webPidFile = Join-Path $runDir "lahuella-portable-web.pid"
$apiLog = Join-Path $root "portable.api.log"
$apiErr = Join-Path $root "portable.api.err.log"
$webLog = Join-Path $root "portable.web.log"
$webErr = Join-Path $root "portable.web.err.log"
$apiExe = Join-Path $root "runtime\api\lahuella-api-portable.exe"
$webExe = Join-Path $root "runtime\web\lahuella-web-portable.exe"
$shortcutFlagFile = Join-Path $runDir "desktop-shortcuts-installed.flag"

function Test-Up {
    param([string]$Url)
    try {
        $r = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 3
        return ($r.StatusCode -ge 200)
    }
    catch {
        return $false
    }
}

function Stop-ByPidFile {
    param([string]$PidFile)
    if (!(Test-Path $PidFile)) { return }
    $raw = Get-Content $PidFile -ErrorAction SilentlyContinue
    if ($raw -match "^\d+$") {
        $pid = [int]$raw
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}

function Ensure-DesktopShortcut {
    param(
        [string]$Name,
        [string]$TargetPath,
        [string]$IconPath
    )
    $desktop = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = Join-Path $desktop ($Name + ".lnk")
    if (Test-Path $shortcutPath) { return }

    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $TargetPath
    $shortcut.WorkingDirectory = $root
    $shortcut.IconLocation = "$IconPath,0"
    $shortcut.Save()
}

function Install-DesktopShortcutsIfNeeded {
    if (Test-Path $shortcutFlagFile) { return }
    $iconPath = Join-Path $root "icon.ico"
    $startTarget = Join-Path $root "start_portable_silent.vbs"
    $stopTarget = Join-Path $root "stop_portable_silent.vbs"
    if (!(Test-Path $iconPath) -or !(Test-Path $startTarget) -or !(Test-Path $stopTarget)) { return }

    try {
        Ensure-DesktopShortcut -Name "Sistemas La Huella" -TargetPath $startTarget -IconPath $iconPath
        Ensure-DesktopShortcut -Name "Detener Sistemas La Huella" -TargetPath $stopTarget -IconPath $iconPath
        Set-Content -Path $shortcutFlagFile -Value (Get-Date).ToString("s") -Encoding ascii
    }
    catch {
        # No bloquear el inicio de la app si falla la creacion de accesos directos.
    }
}

if (!(Test-Path $frontStaticRoot)) {
    throw "No se encontro frontend ni frontend\\dist. Ejecuta el builder portable correspondiente."
}

Install-DesktopShortcutsIfNeeded

if ($ForceRestart) {
    Stop-ByPidFile -PidFile $apiPidFile
    Stop-ByPidFile -PidFile $webPidFile
    Start-Sleep -Seconds 1
}

if (!(Test-Up "http://127.0.0.1:8000/api/health")) {
    Remove-Item $apiLog -Force -ErrorAction SilentlyContinue
    Remove-Item $apiErr -Force -ErrorAction SilentlyContinue
    if (Test-Path $apiExe) {
        $apiProc = Start-Process -FilePath $apiExe `
            -ArgumentList @("--root", $root, "--host", "127.0.0.1", "--port", "8000") `
            -WorkingDirectory $root `
            -RedirectStandardOutput $apiLog `
            -RedirectStandardError $apiErr `
            -WindowStyle Hidden `
            -PassThru
    }
    else {
        $apiProc = Start-Process -FilePath "py" `
            -ArgumentList @("-3", "-m", "uvicorn", "api_server:app", "--host", "127.0.0.1", "--port", "8000") `
            -WorkingDirectory $root `
            -RedirectStandardOutput $apiLog `
            -RedirectStandardError $apiErr `
            -WindowStyle Hidden `
            -PassThru
    }
    $apiProc.Id | Out-File -FilePath $apiPidFile -Encoding ascii -NoNewline
}

if (!(Test-Up "http://127.0.0.1:5173")) {
    Remove-Item $webLog -Force -ErrorAction SilentlyContinue
    Remove-Item $webErr -Force -ErrorAction SilentlyContinue
    if (Test-Path $webExe) {
        $webProc = Start-Process -FilePath $webExe `
            -ArgumentList @("--root", $root, "--host", "127.0.0.1", "--port", "5173") `
            -WorkingDirectory $root `
            -RedirectStandardOutput $webLog `
            -RedirectStandardError $webErr `
            -WindowStyle Hidden `
            -PassThru
    }
    else {
        $webProc = Start-Process -FilePath "py" `
            -ArgumentList @("-3", "-m", "http.server", "5173", "--bind", "127.0.0.1", "--directory", $frontStaticRoot) `
            -WorkingDirectory $root `
            -RedirectStandardOutput $webLog `
            -RedirectStandardError $webErr `
            -WindowStyle Hidden `
            -PassThru
    }
    $webProc.Id | Out-File -FilePath $webPidFile -Encoding ascii -NoNewline
}

$status = [pscustomobject]@{
    timestamp = (Get-Date).ToString("s")
    mode = "portable"
    api_up = (Test-Up "http://127.0.0.1:8000/api/health")
    web_up = (Test-Up "http://127.0.0.1:5173")
    api_pid = if (Test-Path $apiPidFile) { Get-Content $apiPidFile } else { "" }
    web_pid = if (Test-Path $webPidFile) { Get-Content $webPidFile } else { "" }
}

$status | ConvertTo-Json | Out-File -FilePath (Join-Path $runDir "lahuella-portable-status.json") -Encoding utf8
