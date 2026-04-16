param(
    [string]$ApiBase = "http://127.0.0.1:8000/api",
    [string]$Username = "LAHUELLA\Via",
    [string]$Password = "",
    [ValidateSet("10", "192")]
    [string]$Range = "10",
    [string]$HostType = "windows"
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Password)) {
    throw "Password es obligatorio. Usar: -Password 'tu_clave'"
}

$targets = @()
if ($Range -eq "10") {
    $targets += @{ name = "Servidor La Huella"; address = "10.95.25.10" }
    $targets += @{ name = "Via 51"; address = "10.95.25.151" }
    $targets += @{ name = "Via 52"; address = "10.95.25.152" }
    $targets += @{ name = "Via 53"; address = "10.95.25.153" }
    $targets += @{ name = "Via 54"; address = "10.95.25.154" }
    $targets += @{ name = "Via 55"; address = "10.95.25.155" }
    $targets += @{ name = "Via 07"; address = "10.95.25.107" }
    $targets += @{ name = "Via 08"; address = "10.95.25.108" }
    $targets += @{ name = "Via 09"; address = "10.95.25.109" }
    $targets += @{ name = "Via 10"; address = "10.95.25.110" }
    $targets += @{ name = "Via 11"; address = "10.95.25.111" }
}
else {
    $targets += @{ name = "Servidor La Huella"; address = "192.168.2.10" }
    $targets += @{ name = "Via 51"; address = "192.168.2.151" }
    $targets += @{ name = "Via 52"; address = "192.168.2.152" }
    $targets += @{ name = "Via 53"; address = "192.168.2.153" }
    $targets += @{ name = "Via 54"; address = "192.168.2.154" }
    $targets += @{ name = "Via 55"; address = "192.168.2.155" }
    $targets += @{ name = "Via 07"; address = "192.168.2.107" }
    $targets += @{ name = "Via 08"; address = "192.168.2.108" }
    $targets += @{ name = "Via 09"; address = "192.168.2.109" }
    $targets += @{ name = "Via 10"; address = "192.168.2.110" }
    $targets += @{ name = "Via 11"; address = "192.168.2.111" }
}

$existing = (Invoke-RestMethod -Uri "$ApiBase/hosts" -Method Get).items
$created = 0
$skipped = 0

foreach ($target in $targets) {
    if ($existing | Where-Object { $_.address -eq $target.address }) {
        $skipped++
        continue
    }

    $payload = @{
        name = $target.name
        address = $target.address
        port = 445
        username = $Username
        password = $Password
        host_type = $HostType
        winrm_port = 5985
        base_path = "C:\\"
        restart_command = "shutdown /r /t 5 /f"
    } | ConvertTo-Json

    Invoke-RestMethod -Uri "$ApiBase/hosts" -Method Post -Body $payload -ContentType "application/json" | Out-Null
    $created++
}

Write-Host "Hosts creados: $created"
Write-Host "Hosts ya existentes: $skipped"
