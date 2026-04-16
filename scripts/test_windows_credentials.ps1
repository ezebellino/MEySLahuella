param(
    [Parameter(Mandatory = $true)]
    [string]$Server,
    [Parameter(Mandatory = $true)]
    [string]$Username,
    [Parameter(Mandatory = $true)]
    [string]$Password,
    [switch]$CleanupOnly
)

$ErrorActionPreference = "Continue"

function Clear-NetUse {
    cmd.exe /c "net use * /delete /y" | Out-Null
}

if ($CleanupOnly) {
    Clear-NetUse
    Write-Host "Conexiones SMB limpiadas."
    exit 0
}

Clear-NetUse

$ipcPath = "\\$Server\IPC$"
$cmd = "net use $ipcPath /user:$Username `"$Password`""
$output = cmd.exe /c $cmd 2>&1
$code = $LASTEXITCODE

[pscustomobject]@{
    Server = $Server
    Username = $Username
    ExitCode = $code
    Success = ($code -eq 0)
    Output = ($output | Out-String).Trim()
} | Format-List

if ($code -eq 0) {
    Write-Host "`nPrueba OK. Estado actual de net use:"
    cmd.exe /c "net use"
}

