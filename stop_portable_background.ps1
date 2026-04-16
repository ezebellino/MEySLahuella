$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$runDir = Join-Path $root ".run"
$apiPidFile = Join-Path $runDir "lahuella-portable-api.pid"
$webPidFile = Join-Path $runDir "lahuella-portable-web.pid"

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

Stop-ByPidFile -PidFile $apiPidFile
Stop-ByPidFile -PidFile $webPidFile

$ports = @(8000, 5173)
foreach ($p in $ports) {
    $listeners = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
    foreach ($l in $listeners) {
        Stop-Process -Id $l.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}
