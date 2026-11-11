<#
.SYNOPSIS
  Packs the test build into one zip that any mod manager can install.

.DESCRIPTION
  Writes build\TheLastMeridian-Dev.zip, laid out the way a Fallout 4 Data
  folder is:
    TheLastMeridian.esp
    Scripts\TLM\*.pex
    Scripts\Source\User\TLM\*.psc
  Install it in Vortex with "Install From File" (or drop the zip on the Mods
  page), or in Mod Organizer with "Install a new mod from an archive".

  This script only writes inside the repository's build folder. It does not
  touch the game, a mod manager, profiles or load order.

  Status: tested on Linux PowerShell 7. Not yet run on Windows, and the zip
  has not yet been installed with a real mod manager.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\win\Package-Dev.ps1
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$build = Join-Path $repo 'build'
$plugin = Join-Path $build 'TheLastMeridian.esp'
if (-not (Test-Path -LiteralPath $plugin)) { throw "Missing $plugin. Run tools\win\Run-FirstBuild.ps1 first." }
$pexDir = Join-Path (Join-Path $build 'Scripts') 'TLM'
$pex = @()
if (Test-Path -LiteralPath $pexDir) { $pex = @(Get-ChildItem -LiteralPath $pexDir -Filter '*.pex' -File) }
if ($pex.Count -eq 0) { throw "No compiled scripts in $pexDir. The scripts have to compile before the build can be packaged." }
$pscDir = Join-Path (Join-Path (Join-Path (Join-Path $repo 'scripts') 'Source') 'User') 'TLM'
$psc = @(Get-ChildItem -LiteralPath $pscDir -Filter '*.psc' -File)
if ($pex.Count -ne $psc.Count) { throw "Found $($pex.Count) compiled scripts for $($psc.Count) sources. Recompile before packaging." }

# Stage the files in the layout of a Data folder, then zip the staged tree.
$stage = Join-Path $build 'package'
if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
$stagePex = Join-Path (Join-Path $stage 'Scripts') 'TLM'
$stagePsc = Join-Path (Join-Path (Join-Path (Join-Path $stage 'Scripts') 'Source') 'User') 'TLM'
New-Item -ItemType Directory -Force -Path $stagePex | Out-Null
New-Item -ItemType Directory -Force -Path $stagePsc | Out-Null
Copy-Item -LiteralPath $plugin -Destination $stage
foreach ($f in $pex) { Copy-Item -LiteralPath $f.FullName -Destination $stagePex }
foreach ($f in $psc) { Copy-Item -LiteralPath $f.FullName -Destination $stagePsc }

$zip = Join-Path $build 'TheLastMeridian-Dev.zip'
if (Test-Path -LiteralPath $zip) { Remove-Item -LiteralPath $zip -Force }
Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $zip
Remove-Item -LiteralPath $stage -Recurse -Force

$count = 1 + $pex.Count + $psc.Count
Write-Host "Wrote $zip ($count files, $([math]::Round((Get-Item -LiteralPath $zip).Length / 1KB)) KB)"
Write-Host 'Install it with your mod manager, in a test profile, then enable TheLastMeridian.esp.'
