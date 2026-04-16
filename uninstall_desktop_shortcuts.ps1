param()

$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutFlagFile = Join-Path $root ".run\desktop-shortcuts-installed.flag"

$shortcutNames = @(
    "Sistemas La Huella.lnk",
    "Detener Sistemas La Huella.lnk"
)

foreach ($shortcutName in $shortcutNames) {
    $shortcutPath = Join-Path $desktop $shortcutName
    if (Test-Path $shortcutPath) {
        Remove-Item $shortcutPath -Force -ErrorAction SilentlyContinue
    }
}

if (Test-Path $shortcutFlagFile) {
    Remove-Item $shortcutFlagFile -Force -ErrorAction SilentlyContinue
}
