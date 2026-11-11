<#
.SYNOPSIS
  Removes exactly the files Install-Dev.ps1 copied into the game folder.

.DESCRIPTION
  Reads build\install-manifest.json and deletes the files listed there, then
  removes the TLM script folders if they are empty. Nothing else is touched:
  not plugins.txt, not saves, not any file this project did not copy.
  Use -WhatIf to see what would be removed.
#>
[CmdletBinding(SupportsShouldProcess)]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$manifestPath = Join-Path (Join-Path $repo 'build') 'install-manifest.json'
if (-not (Test-Path -LiteralPath $manifestPath)) { Write-Host 'Nothing to remove: no install manifest.'; return }
$m = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json

$removed = 0
$dirs = New-Object System.Collections.Generic.HashSet[string]
foreach ($f in @($m.Files)) {
    if (Test-Path -LiteralPath $f) {
        if ($PSCmdlet.ShouldProcess($f, 'Remove')) { Remove-Item -LiteralPath $f -Force; $removed++ }
    }
    [void]$dirs.Add((Split-Path -Parent $f))
}
foreach ($d in $dirs) {
    if ((Split-Path -Leaf $d) -eq 'TLM' -and (Test-Path -LiteralPath $d) -and @(Get-ChildItem -LiteralPath $d -Force).Count -eq 0) {
        if ($PSCmdlet.ShouldProcess($d, 'Remove empty folder')) { Remove-Item -LiteralPath $d -Force }
    }
}
# A Mod Organizer mod folder that now holds nothing of ours is removed whole,
# including the meta.ini Mod Organizer may have added.
$modFolder = $null
if ($m.PSObject.Properties.Name -contains 'ModFolder') { $modFolder = $m.ModFolder }
if ($modFolder -and (Test-Path -LiteralPath $modFolder) -and -not $WhatIfPreference) {
    Get-ChildItem -LiteralPath $modFolder -Recurse -Directory | Sort-Object { $_.FullName.Length } -Descending | ForEach-Object {
        if (@(Get-ChildItem -LiteralPath $_.FullName -Force).Count -eq 0) { Remove-Item -LiteralPath $_.FullName -Force }
    }
    $left = @(Get-ChildItem -LiteralPath $modFolder -Force | Where-Object { $_.Name -ne 'meta.ini' })
    if ($left.Count -eq 0) { Remove-Item -LiteralPath $modFolder -Recurse -Force }
    else { Write-Host "Left $modFolder in place: it contains files this project did not copy." }
}
if (-not $WhatIfPreference) { Remove-Item -LiteralPath $manifestPath -Force }
Write-Host "Removed $removed file(s) from $($m.Root)."
Write-Host 'If TheLastMeridian.esp was enabled, disable it in your mod manager. Saves made with it loaded may warn about missing content.'
