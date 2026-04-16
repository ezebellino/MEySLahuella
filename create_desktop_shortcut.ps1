param(
    [ValidateSet("portable", "local")]
    [string]$Mode = "portable",
    [ValidateSet("start", "stop")]
    [string]$Action = "start",
    [string]$ShortcutName = "",
    [string]$DesktopPath = "",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$desktop = if ([string]::IsNullOrWhiteSpace($DesktopPath)) {
    [Environment]::GetFolderPath("Desktop")
} else {
    $DesktopPath
}

$targetMap = @{
    "portable:start" = Join-Path $root "start_portable_silent.vbs"
    "portable:stop"  = Join-Path $root "stop_portable_silent.vbs"
    "local:start"    = Join-Path $root "start_app_silent.vbs"
    "local:stop"     = Join-Path $root "stop_app_silent.vbs"
}

$targetKey = "$Mode`:$Action"
$target = $targetMap[$targetKey]
$iconPath = Join-Path $root "icon.ico"
$resolvedShortcutName = if ([string]::IsNullOrWhiteSpace($ShortcutName)) {
    if ($Action -eq "start") {
        "Sistemas La Huella"
    }
    else {
        "Detener Sistemas La Huella"
    }
}
else {
    $ShortcutName
}
$shortcutPath = Join-Path $desktop ($resolvedShortcutName + ".lnk")

if (!(Test-Path $target)) {
    throw "No se encontro el lanzador: $target"
}

if (!(Test-Path $iconPath)) {
    throw "No se encontro el icono: $iconPath"
}

if ((Test-Path $shortcutPath) -and -not $Force) {
    throw "El acceso directo ya existe: $shortcutPath. Usa -Force para reemplazarlo."
}

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $target
$shortcut.WorkingDirectory = $root
$shortcut.IconLocation = "$iconPath,0"
$shortcut.Description = if ($Action -eq "start") {
    "Iniciar Sistemas La Huella en modo $Mode"
}
else {
    "Detener Sistemas La Huella en modo $Mode"
}
$shortcut.Save()

Write-Output $shortcutPath
