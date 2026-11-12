<#
.SYNOPSIS
  Installs the built plugin and scripts for testing.

.DESCRIPTION
  Copies:
    build\TheLastMeridian.esp          -> <target>\
    build\Scripts\TLM\*.pex            -> <target>\Scripts\TLM\
    scripts\Source\User\TLM\*.psc      -> <target>\Scripts\Source\User\TLM\   (so the Creation Kit can open them)

  With -ModOrganizerRoot (the right mode whenever Mod Organizer is used) the
  target is a mod folder, <mods>\TheLastMeridian-Dev, and the game folder is
  not touched at all. Mod Organizer must be closed.

  With -CreateProfile as well, a Mod Organizer profile for testing is created
  (default name TLM-Dev) as a copy of an existing profile's files, with every
  other mod and plugin switched off, its own settings and saves, Papyrus
  logging on and loose files on. Existing profiles are only read. If the test
  profile already exists, only this project's lines in it are refreshed.

  Without -ModOrganizerRoot the target is the game's Data folder; any file it
  would overwrite is first copied to build\backup\<time>\, and nothing is
  enabled (plugins.txt is left alone).

  Every file written is recorded in build\install-manifest.json so
  Uninstall-Dev.ps1 can remove exactly those files. A Fallout London install
  is refused unless -AllowFalloutLondon is given. -WhatIf shows what would be
  copied without copying anything (it does not preview the profile).

  Status: tested on Linux PowerShell 7 against stand-in folder trees. Not yet
  run on a real PC, and a profile made this way has not yet been opened by a
  real Mod Organizer.
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$GameRoot,
    # A Mod Organizer 2 instance folder. Installs as a mod there instead of into the game.
    [string]$ModOrganizerRoot,
    [string]$ModName = 'TheLastMeridian-Dev',
    # Also create or refresh a Mod Organizer profile for testing.
    [switch]$CreateProfile,
    [string]$ProfileName = 'TLM-Dev',
    # Profile whose files are copied to make the test profile. Default: the selected one.
    [string]$SourceProfile,
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
if ($CreateProfile -and -not $ModOrganizerRoot) { throw '-CreateProfile needs -ModOrganizerRoot.' }

$modFolder = $null
$mo = $null
if ($ModOrganizerRoot) {
    $mo = Get-ModOrganizerInfo -Root $ModOrganizerRoot
    if (-not $mo) { throw "No ModOrganizer.ini in $ModOrganizerRoot" }
    if ($ModName -notmatch '^[\w .\-]+$') { throw "Unusable mod name: $ModName" }
    if (Test-ModOrganizerRunning) { throw 'Mod Organizer is running. Close it, then run this again.' }
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
if (-not (Test-Path -LiteralPath $plugin)) { throw "Missing $plugin. Run tools\win\Run-FirstBuild.ps1 first." }
$pexDir = Join-Path (Join-Path $build 'Scripts') 'TLM'
$pscDir = Join-Path (Join-Path (Join-Path (Join-Path $repo 'scripts') 'Source') 'User') 'TLM'
$psc = @(Get-ChildItem -LiteralPath $pscDir -Filter '*.psc' -File)

# One compiled script per source, no more: a leftover from a renamed or
# deleted script must not be installed, and a missing one must stop the install.
$pex = @()
foreach ($s in $psc) {
    $compiled = Join-Path $pexDir ($s.BaseName + '.pex')
    if (-not (Test-Path -LiteralPath $compiled)) { throw "No compiled script for $($s.Name) in $pexDir. Compile first (tools\win\Run-FirstBuild.ps1)." }
    $pex += (Get-Item -LiteralPath $compiled)
}

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
    if ((Test-Path -LiteralPath $p.To) -and -not $modFolder) {
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

$profileInfo = $null
if ($CreateProfile -and $written.Count -gt 0) {
    $profileInfo = New-TlmDevProfile -ModOrganizerRoot $ModOrganizerRoot -ProfileName $ProfileName -SourceProfile $SourceProfile -ModName $ModName
}

if ($written.Count -gt 0) {
    $manifestPath = Join-Path $build 'install-manifest.json'
    $all = @($written)
    $profileFolder = $null
    if (Test-Path -LiteralPath $manifestPath) {
        $old = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
        if ($old.Root -eq $root) {
            $all = @(@($old.Files) + $all | Sort-Object -Unique)
            if ($old.PSObject.Properties.Name -contains 'ProfileFolder') { $profileFolder = $old.ProfileFolder }
        }
    }
    if ($profileInfo) { $profileFolder = $profileInfo.Path }
    [pscustomobject]@{ Root = $root; ModFolder = $modFolder; ProfileFolder = $profileFolder; Installed = (Get-Date -Format 'o'); Files = $all } |
        ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $manifestPath -Encoding utf8
}

Write-Host "Install target : $root"
Write-Host "Files copied   : $($written.Count) of $($plan.Count)$(if (-not $modFolder) { "   (backed up before overwrite: $backedUp)" })"
if ($profileInfo) {
    if ($profileInfo.Created) {
        Write-Host "Test profile   : created '$($profileInfo.Name)' from '$($profileInfo.SourceProfile)' ($($profileInfo.ModsSwitchedOff) other mods switched off in the copy)"
    } else {
        Write-Host "Test profile   : '$($profileInfo.Name)' already existed; refreshed this project's lines in it"
    }
    Write-Host "                 $($profileInfo.Path)"
}
if ($written.Count -eq 0) { return }

Write-Host ''
if ($profileInfo) {
    $title = if ($profileInfo.GameTitle) { "'$($profileInfo.GameTitle)'" } else { 'the entry that starts Fallout4.exe (not F4SE, not the launcher)' }
    Write-Host 'NEXT STEPS'
    Write-Host "  1. Start Mod Organizer:  $(Join-Path $mo.Root 'ModOrganizer.exe')"
    Write-Host "  2. In the Profile list at the top, choose:  $($profileInfo.Name)"
    Write-Host "  3. In the list next to the Run button (top right), choose:  $title"
    Write-Host '  4. Click Run. At the game''s main menu press the ~ key (left of the 1 key) and type:'
    Write-Host '         coc qasmoke'
    Write-Host '     When the room has loaded, press ~ again and type:'
    Write-Host '         cqf TLM_Core RunSelfTest'
    Write-Host '     Press ~ to close the console and wait for a message box (about 15 seconds).'
    Write-Host '  5. Quit the game, then in this window run:'
    Write-Host '         powershell -ExecutionPolicy Bypass -File tools\win\Get-TestResults.ps1'
    Write-Host '     and paste the result into the chat (Ctrl+V).'
    Write-Host ''
    Write-Host 'When you are done, switch Mod Organizer back to your own profile.'
} elseif ($modFolder) {
    Write-Host 'The mod is NOT enabled. In Mod Organizer, in a profile used only for testing,'
    Write-Host "tick '$ModName' in the left pane and TheLastMeridian.esp in the right pane."
    Write-Host '(Running this script with -CreateProfile sets such a profile up.)'
} else {
    Write-Host 'The plugin is NOT enabled. Enable TheLastMeridian.esp yourself.'
    Write-Host 'That setting is shared by every Fallout 4 install on this PC.'
}
Write-Host 'To remove what this script copied:  powershell -ExecutionPolicy Bypass -File tools\win\Uninstall-Dev.ps1'
