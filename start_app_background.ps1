param(
    [switch]$ForceRestart
)

$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$front = Join-Path $root "frontend"
$runDir = Join-Path $root ".run"
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

$apiPidFile = Join-Path $runDir "lahuella-api.pid"
$webPidFile = Join-Path $runDir "lahuella-web.pid"
$apiLog = Join-Path $root "api.log"
$apiErr = Join-Path $root "api.err.log"
$webLog = Join-Path $front "web.log"
$webErr = Join-Path $front "web.err.log"

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

if ($ForceRestart) {
    Stop-ByPidFile -PidFile $apiPidFile
    Stop-ByPidFile -PidFile $webPidFile
    Start-Sleep -Seconds 1
}

if (!(Test-Up "http://127.0.0.1:8000/api/health")) {
    Remove-Item $apiLog -Force -ErrorAction SilentlyContinue
    Remove-Item $apiErr -Force -ErrorAction SilentlyContinue
    $apiProc = Start-Process -FilePath "py" `
        -ArgumentList @("-3", "-m", "uvicorn", "api_server:app", "--host", "127.0.0.1", "--port", "8000") `
        -WorkingDirectory $root `
        -RedirectStandardOutput $apiLog `
        -RedirectStandardError $apiErr `
        -WindowStyle Hidden `
        -PassThru
    $apiProc.Id | Out-File -FilePath $apiPidFile -Encoding ascii -NoNewline
}

if (!(Test-Up "http://127.0.0.1:5173")) {
    Remove-Item $webLog -Force -ErrorAction SilentlyContinue
    Remove-Item $webErr -Force -ErrorAction SilentlyContinue
    $webProc = Start-Process -FilePath "npm.cmd" `
        -ArgumentList @("run", "dev", "--", "--host", "127.0.0.1", "--port", "5173") `
        -WorkingDirectory $front `
        -RedirectStandardOutput $webLog `
        -RedirectStandardError $webErr `
        -WindowStyle Hidden `
        -PassThru
    $webProc.Id | Out-File -FilePath $webPidFile -Encoding ascii -NoNewline
}

$status = [pscustomobject]@{
    timestamp = (Get-Date).ToString("s")
    api_up = (Test-Up "http://127.0.0.1:8000/api/health")
    web_up = (Test-Up "http://127.0.0.1:5173")
    api_pid = if (Test-Path $apiPidFile) { Get-Content $apiPidFile } else { "" }
    web_pid = if (Test-Path $webPidFile) { Get-Content $webPidFile } else { "" }
}

$status | ConvertTo-Json | Out-File -FilePath (Join-Path $runDir "lahuella-status.json") -Encoding utf8

