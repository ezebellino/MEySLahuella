param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$scriptPath = Join-Path $root "create_desktop_shortcut.ps1"

if (!(Test-Path $scriptPath)) {
    throw "No se encontro create_desktop_shortcut.ps1 en $root"
}

$commonArgs = @(
    "-ExecutionPolicy", "Bypass",
    "-File", $scriptPath,
    "-Mode", "portable"
)

if ($Force) {
    & powershell @($commonArgs + @("-Action", "start", "-Force"))
    & powershell @($commonArgs + @("-Action", "stop", "-Force"))
}
else {
    & powershell @($commonArgs + @("-Action", "start"))
    & powershell @($commonArgs + @("-Action", "stop"))
}
