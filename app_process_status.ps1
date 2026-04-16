$root = $PSScriptRoot
$runDir = Join-Path $root ".run"
$apiPidFile = Join-Path $runDir "lahuella-api.pid"
$webPidFile = Join-Path $runDir "lahuella-web.pid"

function Read-PidSafe {
    param([string]$Path)
    if (Test-Path $Path) {
        $v = Get-Content $Path -ErrorAction SilentlyContinue
        if ($v -match "^\d+$") { return [int]$v }
    }
    return $null
}

$apiPid = Read-PidSafe $apiPidFile
$webPid = Read-PidSafe $webPidFile

$apiProc = if ($apiPid) { Get-Process -Id $apiPid -ErrorAction SilentlyContinue } else { $null }
$webProc = if ($webPid) { Get-Process -Id $webPid -ErrorAction SilentlyContinue } else { $null }

[pscustomobject]@{
    api_pid = $apiPid
    api_running = [bool]$apiProc
    web_pid = $webPid
    web_running = [bool]$webProc
    api_url = "http://127.0.0.1:8000/api/health"
    web_url = "http://127.0.0.1:5173"
} | Format-List

