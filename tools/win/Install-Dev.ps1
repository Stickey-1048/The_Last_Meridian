<#
.SYNOPSIS
  Copies the built plugin and scripts into a Fallout 4 Data folder for testing.

.DESCRIPTION
  Copies:
    build\TheLastMeridian.esp          -> Data\
    build\Scripts\TLM\*.pex            -> Data\Scripts\TLM\
    scripts\Source\User\TLM\*.psc      -> Data\Scripts\Source\User\TLM\   (so the Creation Kit can open them)

  Any file it would overwrite is first copied to build\backup\<time>\.
  Every file it writes is recorded in build\install-manifest.json so
  Uninstall-Dev.ps1 can remove exactly those files.

  With -ModOrganizerRoot the files go into a Mod Organizer mod folder instead
  (<mods>\TheLastMeridian-Dev\...), and the game folder is not touched at all.
  This is the right mode whenever the game is run through Mod Organizer.

  It does NOT enable the plugin or the mod (plugins.txt, modlist.txt and the
  profiles are left alone) and refuses to touch a Fallout London install
  unless -AllowFalloutLondon is given.
  Use -WhatIf to see what would be copied without copying anything.

  Status: tested against a stand-in folder tree, not yet on a real install.
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$GameRoot,
    # A Mod Organizer 2 instance folder. Installs as a mod there instead of into the game.
    [string]$ModOrganizerRoot,
    [string]$ModName = 'TheLastMeridian-Dev',
    [switch]$AllowFalloutLondon,
    [string]$SteamRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Tlm.psm1') -Force

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$gameRootResolved = Select-DevInstall -GameRoot $GameRoot -SteamRoot $SteamRoot -ModOrganizerRoot $ModOrganizerRoot
$gameData = Join-Path $gameRootResolved 'Data'
if ((Test-Path -LiteralPath (Join-Path $gameData 'LondonWorldSpace.esm')) -and -not $AllowFalloutLondon) {
    throw "$gameRootResolved is a Fallout London install. Refusing to install for it. Pass -AllowFalloutLondon only if you mean it."
}
$modFolder = $null
if ($ModOrganizerRoot) {
    $mo = Get-ModOrganizerInfo -Root $ModOrganizerRoot
    if ($ModName -notmatch '^[\w .\-]+$') { throw "Unusable mod name: $ModName" }
    $modFolder = Join-Path $mo.ModsDirectory $ModName
    # In a Mod Organizer mod, the folder itself stands in for the game's Data folder.
    $root = $modFolder
    $data = $modFolder
} else {
    $root = $gameRootResolved
    $data = $gameData
}

$build = Join-Path $repo 'build'
$plugin = Join-Path $build 'TheLastMeridian.esp'
if (-not (Test-Path -LiteralPath $plugin)) { throw "Missing $plugin. Run: dotnet run --project tools/PluginBuilder -- --fallout4-esm `"$(Join-Path $gameData 'Fallout4.esm')`"" }
$pexDir = Join-Path (Join-Path $build 'Scripts') 'TLM'
$pex = @()
if (Test-Path -LiteralPath $pexDir) { $pex = @(Get-ChildItem -LiteralPath $pexDir -Filter '*.pex' -File) }
if ($pex.Count -eq 0) { throw "No compiled scripts in $pexDir. Run tools\win\Build-Scripts.ps1 first." }
$pscDir = Join-Path (Join-Path (Join-Path (Join-Path $repo 'scripts') 'Source') 'User') 'TLM'
$psc = @(Get-ChildItem -LiteralPath $pscDir -Filter '*.psc' -File)

$plan = New-Object System.Collections.Generic.List[object]
$plan.Add([pscustomobject]@{ From = $plugin; To = Join-Path $data 'TheLastMeridian.esp' })
foreach ($f in $pex) { $plan.Add([pscustomobject]@{ From = $f.FullName; To = Join-Path (Join-Path (Join-Path $data 'Scripts') 'TLM') $f.Name }) }
foreach ($f in $psc) { $plan.Add([pscustomobject]@{ From = $f.FullName; To = Join-Path (Join-Path (Join-Path (Join-Path (Join-Path $data 'Scripts') 'Source') 'User') 'TLM') $f.Name }) }

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupRoot = Join-Path (Join-Path $build 'backup') $stamp
$written = New-Object System.Collections.Generic.List[string]
$backedUp = 0
foreach ($p in $plan) {
    if (-not $PSCmdlet.ShouldProcess($p.To, "Copy from $($p.From)")) { continue }
    $dir = Split-Path -Parent $p.To
    if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    if (Test-Path -LiteralPath $p.To) {
        $same = (Get-FileHash -LiteralPath $p.To).Hash -eq (Get-FileHash -LiteralPath $p.From).Hash
        if (-not $same) {
            $relTo = $p.To.Substring($root.Length).TrimStart('\', '/')
            $bk = Join-Path $backupRoot $relTo
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $bk) | Out-Null
            Copy-Item -LiteralPath $p.To -Destination $bk
            $backedUp++
        }
    }
    Copy-Item -LiteralPath $p.From -Destination $p.To -Force
    $written.Add($p.To)
}

if ($written.Count -gt 0) {
    $manifestPath = Join-Path $build 'install-manifest.json'
    $all = @($written)
    if (Test-Path -LiteralPath $manifestPath) {
        $old = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
        if ($old.Root -eq $root) { $all = @(@($old.Files) + $all | Sort-Object -Unique) }
    }
    [pscustomobject]@{ Root = $root; ModFolder = $modFolder; Installed = (Get-Date -Format 'o'); Files = $all } |
        ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $manifestPath -Encoding utf8
}

Write-Host "Install target : $root"
Write-Host "Files copied   : $($written.Count) of $($plan.Count)   (backed up before overwrite: $backedUp)"
if ($written.Count -gt 0) {
    Write-Host ''
    Write-Host 'The plugin is NOT enabled. To test:'
    if ($modFolder) {
        Write-Host '  1. In Mod Organizer, make a copy of your profile for testing and select it.'
        Write-Host "     Refresh (F5), tick '$ModName' in the left pane and TheLastMeridian.esp in the right pane."
        Write-Host '     Start the game from Mod Organizer, the same way you normally do.'
    } else {
        Write-Host '  1. Enable TheLastMeridian.esp in your mod manager or the in-game Mods menu.'
        Write-Host '     (That setting is shared by every Fallout 4 install on this PC.)'
    }
    Write-Host '  2. Load a disposable save, open the console and run:  cqf TLM_Core DevStart'
    Write-Host '  3. Follow docs/design/TEST_RUNBOOK.md.'
    Write-Host 'To remove everything this script copied:  pwsh tools/win/Uninstall-Dev.ps1'
}
