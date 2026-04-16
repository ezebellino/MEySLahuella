param(
    [string]$OutputDir = "C:\Temp",
    [string[]]$Targets = @(
        "10.95.25.10",
        "10.95.25.107", "10.95.25.108", "10.95.25.109", "10.95.25.110", "10.95.25.111",
        "10.95.25.151", "10.95.25.152", "10.95.25.153", "10.95.25.154", "10.95.25.155"
    ),
    [int[]]$Ports = @(22, 80, 135, 139, 443, 445, 3389, 5985, 5986),
    [string[]]$DnsToTest = @("10.95.20.112", "10.100.20.112", "192.168.2.1"),
    [string]$LookupHost = "srvlahuella.lahuella.local"
)

$ErrorActionPreference = "Continue"
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
$outFile = Join-Path $OutputDir ("la_huella_diag_{0}.txt" -f (Get-Date -Format "yyyyMMdd_HHmmss"))

function Write-Section {
    param([string]$Title)
    Add-Content -Path $outFile -Value "`n===== $Title ====="
}

function Write-CmdOutput {
    param(
        [string]$Command,
        [scriptblock]$Script
    )
    Add-Content -Path $outFile -Value "`n$ $Command"
    try {
        $result = & $Script 2>&1 | Out-String
        Add-Content -Path $outFile -Value $result
    }
    catch {
        Add-Content -Path $outFile -Value ("ERROR: {0}" -f $_.Exception.Message)
    }
}

"===== CONTEXTO =====" | Out-File -FilePath $outFile -Encoding utf8
("DATE: {0}" -f (Get-Date)) | Add-Content -Path $outFile
("HOSTNAME: {0}" -f $env:COMPUTERNAME) | Add-Content -Path $outFile
("WHOAMI: {0}" -f (whoami)) | Add-Content -Path $outFile

Write-Section "IPCONFIG /ALL"
Write-CmdOutput "ipconfig /all" { ipconfig /all }

Write-Section "ROUTE PRINT"
Write-CmdOutput "route print" { route print }

Write-Section "DNS CLIENT"
Write-CmdOutput "Get-DnsClientServerAddress -AddressFamily IPv4" { Get-DnsClientServerAddress -AddressFamily IPv4 | Format-Table -AutoSize }

Write-Section "NSLOOKUP"
foreach ($dns in $DnsToTest) {
    Write-CmdOutput "nslookup $LookupHost $dns" { nslookup $LookupHost $dns }
}

Write-Section "PING + PUERTOS"
foreach ($target in $Targets) {
    Add-Content -Path $outFile -Value "`n---- $target ----"
    Write-CmdOutput "ping -n 1 $target" { ping -n 1 $target }
    foreach ($port in $Ports) {
        Write-CmdOutput "Test-NetConnection $target -Port $port" {
            $r = Test-NetConnection $target -Port $port -WarningAction SilentlyContinue
            [pscustomobject]@{
                Target = $target
                Port = $port
                PingSucceeded = $r.PingSucceeded
                TcpTestSucceeded = $r.TcpTestSucceeded
                SourceAddress = $r.SourceAddress
            }
        }
    }
}

Write-Host ("Reporte generado: {0}" -f $outFile)

