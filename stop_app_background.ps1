$ErrorActionPreference = "Continue"

$root = $PSScriptRoot
$runDir = Join-Path $root ".run"
$apiPidFile = Join-Path $runDir "lahuella-api.pid"
$webPidFile = Join-Path $runDir "lahuella-web.pid"

function Stop-ByPidFile {
    param([string]$PidFile)
    if (!(Test-Path $PidFile)) { return }
    $raw = Get-Content $PidFile -ErrorAction SilentlyContinue
    if ($raw -match "^\d+$") {
        Stop-Process -Id ([int]$raw) -Force -ErrorAction SilentlyContinue
    }
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}

Stop-ByPidFile -PidFile $apiPidFile
Stop-ByPidFile -PidFile $webPidFile

# Fallback by well-known ports
foreach ($port in 8000, 5173) {
    $pids = netstat -ano | Select-String -Pattern (":{0}\s+.*LISTENING\s+(\d+)$" -f $port)
    foreach ($line in $pids) {
        if ($line.Matches.Count -gt 0) {
            $procId = [int]$line.Matches[0].Groups[1].Value
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
    }
}
