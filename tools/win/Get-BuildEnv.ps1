<#
.SYNOPSIS
  Records the build environment in docs/design/BUILD_ENV.md.

.DESCRIPTION
  READ-ONLY. Looks for Fallout 4 installs (Steam, GOG), reads version numbers,
  checks for the Creation Kit, the Papyrus compiler and its sources, script
  extenders, DLC, Fallout London, and the shared settings folders. Writes one
  Markdown file into the repository and changes nothing else.

  Save names and contents are never read; only a count and the newest date.

.EXAMPLE
  pwsh tools/win/Get-BuildEnv.ps1
  pwsh tools/win/Get-BuildEnv.ps1 -ExtraRoot 'D:\Games\Fallout 4 GOTY'
#>
[CmdletBinding()]
param(
    # Extra folders containing Fallout4.exe to include.
    [string[]]$ExtraRoot = @(),
    # A Mod Organizer 2 instance folder (the one holding ModOrganizer.ini).
    [string]$ModOrganizerRoot,
    # Folder the Creation Kit is installed in, if it is not found through Steam.
    [string]$CreationKitRoot,
    # Overrides for testing off Windows.
    [string]$SteamRoot,
    [string]$DocumentsRoot,
    [string]$LocalAppDataRoot,
    [string]$AppDataRoot,
    [string]$OutFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Tlm.psm1') -Force

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if (-not $OutFile) { $OutFile = Join-Path (Join-Path (Join-Path $repo 'docs') 'design') 'BUILD_ENV.md' }

function YesNo([bool]$b) { if ($b) { 'yes' } else { 'no' } }
function OrDash($v) { if ($null -eq $v -or "$v" -eq '') { '-' } else { "$v" } }

$mo = $null
if ($ModOrganizerRoot) {
    $mo = Get-ModOrganizerInfo -Root $ModOrganizerRoot
    if (-not $mo) { throw "No ModOrganizer.ini in $ModOrganizerRoot" }
    if ($mo.GamePath -and ($ExtraRoot -notcontains $mo.GamePath)) { $ExtraRoot += $mo.GamePath }
}
$installs = @(Find-Fallout4Installs -SteamRoot $SteamRoot -ExtraRoot $ExtraRoot)
$infos = @($installs | ForEach-Object {
        $i = Get-Fallout4InstallInfo -Root $_.Root
        $i | Add-Member -NotePropertyName Store -NotePropertyValue $_.Store
        $i | Add-Member -NotePropertyName FoundBy -NotePropertyValue $_.FoundBy
        $i
    })
$user = Get-Fallout4UserState -DocumentsRoot $DocumentsRoot -LocalAppDataRoot $LocalAppDataRoot
$vortex = Get-VortexInfo -AppDataRoot $AppDataRoot
$ckFolders = @(Find-CreationKitFolders -SteamRoot $SteamRoot -Extra (@($CreationKitRoot) + @($installs | ForEach-Object Root) + $ExtraRoot))

$md = New-Object System.Text.StringBuilder
function Line([string]$s = '') { [void]$md.AppendLine($s) }

Line '# Build environment'
Line
Line "Recorded $(Get-Date -Format 'yyyy-MM-dd HH:mm') by ``tools/win/Get-BuildEnv.ps1`` (read-only scan). Re-run it after any game or Creation Kit update."
Line
Line 'Paths inside the Windows user folder are written as `%USERPROFILE%`, so this file can be committed without naming the account.'
Line
Line "- OS: $([System.Runtime.InteropServices.RuntimeInformation]::OSDescription)"
Line "- PowerShell: $($PSVersionTable.PSVersion)"
$r = Invoke-Native -Exe 'dotnet' -Arguments @('--version'); $dotnet = if ($r.Found -and $r.ExitCode -eq 0) { $r.Output | Select-Object -First 1 } else { $null }
$r = Invoke-Native -Exe 'git' -Arguments @('--version'); $git = if ($r.Found -and $r.ExitCode -eq 0) { $r.Output | Select-Object -First 1 } else { $null }
Line "- .NET SDK: $(OrDash $dotnet)"
Line "- git: $(OrDash $git)"
Line

Line '## Fallout 4 installs'
Line
if ($infos.Count -eq 0) {
    Line 'None found. Re-run with `-ExtraRoot <folder containing Fallout4.exe>`.'
} else {
    foreach ($i in $infos) {
        Line "### $($i.Store): ``$($i.Root)``"
        Line
        Line '| Item | Value |'
        Line '|---|---|'
        Line "| Found by | $($i.FoundBy) |"
        Line "| Fallout4.exe | $(OrDash $i.GameVersion) ($($i.GameGeneration)) |"
        Line "| CreationKit.exe | $(OrDash $i.CreationKitVersion) |"
        Line "| Papyrus compiler | $(YesNo $i.PapyrusCompiler) |"
        Line "| Base script sources | $($i.BaseSourceCount) .psc extracted; Base.zip present: $(YesNo $i.BaseSourceZip); flags file: $(YesNo $i.FlagsFile) |"
        Line "| F4SE | $(OrDash $i.F4SEVersion) |"
        Line "| DLC masters | $(if ($i.DlcPresent.Count) { $i.DlcPresent -join ', ' } else { 'none' }) |"
        Line "| Creation Club plugins | $($i.CreationClubCount) |"
        Line "| Fallout London | $(YesNo $i.FalloutLondon) |"
        Line "| Other plugins in Data | $($i.OtherPlugins.Count) |"
        Line "| GOG product | $(if ($i.GogProducts.Count) { $i.GogProducts -join '; ' } else { '-' }) |"
        Line "| Mod manager | $($i.ModManagerHint) |"
        if ($i.VortexDeployment) {
            $vd = $i.VortexDeployment
            Line "| Vortex deployment in Data | $($vd.Files) file(s) from $($vd.Mods) mod(s); method $(OrDash $vd.Method); staging folder ``$(OrDash $vd.Staging)`` |"
        } else {
            Line '| Vortex deployment in Data | none |'
        }
        Line "| TheLastMeridian.esp in Data | $(YesNo $i.TlmInstalled) |"
        Line
    }
}

Line '## Creation Kit'
Line
if ($ckFolders.Count -eq 0) {
    Line 'Not found.'
    Line
} else {
    foreach ($ck in $ckFolders) {
        $ckBase = Join-Path (Join-Path (Join-Path (Join-Path $ck 'Data') 'Scripts') 'Source') 'Base'
        $ckPsc = 0
        if (Test-Path -LiteralPath $ckBase) { $ckPsc = @(Get-ChildItem -LiteralPath $ckBase -Filter '*.psc' -File -ErrorAction SilentlyContinue).Count }
        Line "### ``$ck``"
        Line
        Line '| Item | Value |'
        Line '|---|---|'
        Line "| CreationKit.exe | $(OrDash (Get-ExeVersion (Join-Path $ck 'CreationKit.exe'))) |"
        Line "| Papyrus compiler | $(YesNo (Test-Path -LiteralPath (Join-Path (Join-Path $ck 'Papyrus Compiler') 'PapyrusCompiler.exe'))) |"
        Line "| Base script sources | $ckPsc .psc extracted; Base.zip present: $(YesNo (Test-Path -LiteralPath (Join-Path $ckBase 'Base.zip'))) |"
        Line "| Game beside it | Fallout4.exe $(OrDash (Get-ExeVersion (Join-Path $ck 'Fallout4.exe'))) |"
        Line "| Fallout London | $(YesNo (Test-Path -LiteralPath (Join-Path (Join-Path $ck 'Data') 'LondonWorldSpace.esm'))) |"
        Line
    }
}

if ($mo) {
    Line '## Mod Organizer 2'
    Line
    Line '| Item | Value |'
    Line '|---|---|'
    Line "| Instance | ``$($mo.Root)`` (version $(OrDash $mo.Version)); ModOrganizer.exe present: $(YesNo $mo.ExePresent) |"
    Line "| Manages | $(OrDash $mo.GameName) at ``$(OrDash $mo.GamePath)`` |"
    Line "| Mods folder | ``$($mo.ModsDirectory)`` ($($mo.ModCount) mod folders) |"
    Line "| Selected profile | $(OrDash $mo.SelectedProfile) |"
    Line "| Registered tools | $(if ($mo.Tools.Count) { $mo.Tools -join ', ' } else { 'none of interest' }) |"
    Line "| Base script sources in a mod | $(if ($mo.BaseSourceDirs.Count) { ($mo.BaseSourceDirs | ForEach-Object { '``' + $_ + '``' }) -join ', ' } else { 'none found' }) |"
    Line "| TheLastMeridian-Dev mod folder | $(YesNo $mo.TlmModInstalled) |"
    Line
    Line '| Profile | Selected | Mods on | Plugins on | Own settings | Own saves | Loose files | Papyrus log | TLM mod on | TLM plugin on |'
    Line '|---|---|---|---|---|---|---|---|---|---|'
    foreach ($p in $mo.Profiles) {
        Line "| $($p.Name) | $(YesNo $p.Selected) | $($p.ModsEnabled) | $($p.PluginsActive) | $(OrDash $p.LocalSettings) | $(OrDash $p.LocalSaves) | $(OrDash $p.InvalidateOlderFiles) | $(OrDash $p.PapyrusLogging) | $(YesNo $p.TlmModEnabled) | $(YesNo $p.TlmPluginActive) |"
    }
    Line
}

Line '## Vortex'
Line
if (-not $vortex) {
    Line 'No Vortex data folder found for this Windows account.'
} elseif (@($vortex.Games).Count -eq 0) {
    Line "Vortex data folder found at ``$($vortex.Root)``, with no managed games in it."
} else {
    Line "Vortex data folder: ``$($vortex.Root)``"
    Line
    Line '| Game folder name | Staged mods | Profiles |'
    Line '|---|---|---|'
    foreach ($g in $vortex.Games) { Line "| $($g.Name) | $($g.StagedMods) | $($g.Profiles) |" }
}
Line

Line '## Shared settings, saves and load order'
Line
Line 'These live outside the game folder. To our knowledge every Fallout 4 install on the machine (Steam and GOG alike) reads the same ones, so a plugin enabled for one install is enabled for the other. A Mod Organizer profile with its own settings overrides them while the game is started through Mod Organizer.'
Line
Line '| Item | Value |'
Line '|---|---|'
Line "| My Games folder | ``$($user.MyGamesFolder)`` (exists: $(YesNo $user.MyGamesExists)) |"
Line "| Fallout4Custom.ini | exists: $(YesNo $user.CustomIniExists) |"
Line "| Loose files enabled | bInvalidateOlderFiles=$(OrDash $user.InvalidateOlderFiles); sResourceDataDirsFinal=$(if ($null -eq $user.ResourceDataDirs) { '-' } elseif ($user.ResourceDataDirs -eq '') { '(empty, as required)' } else { $user.ResourceDataDirs }) |"
Line "| Papyrus logging | bEnableLogging=$(OrDash $user.PapyrusLogging); log file present: $(YesNo $user.PapyrusLogExists) |"
Line "| Saves | $($user.SaveCount) file(s); newest $(OrDash $user.NewestSave) |"
foreach ($p in $user.PluginLists) {
    Line "| Load order | ``$($p.Path)``: $($p.Active) active of $($p.Listed); lists Fallout London's plugins: $(YesNo $p.MentionsLondon); TheLastMeridian.esp listed: $(YesNo $p.TlmListed), active: $(YesNo $p.TlmActive) |"
}
if (@($user.PluginLists).Count -eq 0) { Line '| Load order | no plugins.txt found |' }
foreach ($f in $user.MyGamesFolders) {
    Line "| Settings folder ``My Games\$($f.Name)`` | $($f.Saves) save(s); settings files: $(if ($f.IniFiles.Count) { $f.IniFiles -join ', ' } else { 'none' }) |"
}
Line "| Fallout folders in the local app data | $(if ($user.AppDataFolders.Count) { $user.AppDataFolders -join ', ' } else { 'none' }) |"
Line

Line '## What this means for the build'
Line
$notes = New-Object System.Collections.Generic.List[string]
$dev = @($infos | Where-Object { $_.CreationKitVersion -and -not $_.FalloutLondon })
if ($mo) {
    $target = @($infos | Where-Object { $_.Root.TrimEnd('\', '/') -ieq "$($mo.GamePath)".TrimEnd('\', '/') })
    if ($target.Count -eq 1) {
        $notes.Add("Build against the install Mod Organizer manages: ``$($target[0].Root)`` ($($target[0].Store), game $(OrDash $target[0].GameVersion)). Install the test build as a Mod Organizer mod (``Install-Dev.ps1 -ModOrganizerRoot``), never into the game folder.")
        if (-not $target[0].CreationKitVersion) {
            $ckElsewhere = @($ckFolders | Where-Object { -not (Test-Path -LiteralPath (Join-Path (Join-Path $_ 'Data') 'LondonWorldSpace.esm')) })
            if ($ckElsewhere.Count -gt 0) {
                $notes.Add("That install has no CreationKit.exe. The Creation Kit in ``$($ckElsewhere[0])`` ($(OrDash (Get-ExeVersion (Join-Path $ckElsewhere[0] 'CreationKit.exe')))) supplies the Papyrus compiler and the base script sources (``Build-Scripts.ps1 -CreationKitRoot``).")
            } else {
                $notes.Add('That install has no CreationKit.exe, and none was found elsewhere. The Creation Kit supplies the Papyrus compiler and the base script sources, so scripts cannot be compiled until it is installed.')
            }
        }
    } else {
        $notes.Add("Mod Organizer points at ``$($mo.GamePath)``, but no Fallout4.exe was found there.")
    }
    $notes.Add('Use a separate Mod Organizer profile for testing (copy the current one) so the existing mod list is untouched.')
    $sel = @($mo.Profiles | Where-Object Selected)
    if ($sel.Count -eq 1 -and "$($sel[0].LocalSettings)" -ine 'true') { $notes.Add("Profile '$($sel[0].Name)' does not use its own settings, so the shared Fallout4Custom.ini below applies to it.") }
} elseif ($infos.Count -eq 0) {
    $notes.Add('No install found, so nothing can be built or tested yet.')
} elseif ($dev.Count -eq 1) {
    $notes.Add("Build against: ``$($dev[0].Root)`` ($($dev[0].Store), game $($dev[0].GameVersion), Creation Kit $($dev[0].CreationKitVersion)).")
} elseif ($dev.Count -eq 0) {
    $notes.Add('No install has the Creation Kit (or the only one that does is a Fallout London install). Install the Creation Kit next to the Steam copy, or name the install to use.')
} else {
    $notes.Add('More than one install has the Creation Kit. Name the one to build against with `-GameRoot`.')
}
foreach ($i in $infos) {
    if ($i.FalloutLondon) { $notes.Add("``$($i.Root)`` is a Fallout London install. The build scripts refuse to copy files into it unless told otherwise.") }
    if ($i.CreationKitVersion -and -not $i.PapyrusCompiler) { $notes.Add("``$($i.Root)``: Creation Kit present but ``Papyrus Compiler\PapyrusCompiler.exe`` is missing.") }
    if ($i.PapyrusCompiler -and $i.BaseSourceCount -eq 0) {
        if ($i.BaseSourceZip) { $notes.Add("``$($i.Root)``: base script sources are still zipped. Scripts cannot compile until ``Data\Scripts\Source\Base\Base.zip`` is extracted in place (``Build-Scripts.ps1 -ExtractBase`` does it).") }
        else { $notes.Add("``$($i.Root)``: base script sources not found under ``Data\Scripts\Source\Base``. Scripts cannot compile without them.") }
    }
    if ($i.F4SEVersion) { $notes.Add("``$($i.Root)``: F4SE is installed. Starting the game through it is fine, but the project's own scripts must not call F4SE functions.") }
}
# Which settings file actually applies: a Mod Organizer profile with its own
# settings, or the shared one in Documents.
$iniOwner = 'the shared Fallout4Custom.ini'
$loose = $user.InvalidateOlderFiles
$logging = $user.PapyrusLogging
if ($mo) {
    $sel = @($mo.Profiles | Where-Object Selected)
    if ($sel.Count -eq 1 -and "$($sel[0].LocalSettings)" -ieq 'true') {
        $iniOwner = "Mod Organizer profile '$($sel[0].Name)' (fallout4custom.ini in the profile folder)"
        $loose = $sel[0].InvalidateOlderFiles
        $logging = $sel[0].PapyrusLogging
    }
} elseif ($infos.Count -gt 1) {
    $notes.Add('More than one install shares the settings and load order above. Enabling the test plugin affects all of them. A mod manager profile is the clean way to isolate it.')
}
if ($loose -ne '1') { $notes.Add("Loose files are not enabled in $iniOwner, so compiled scripts will not load. Needs ``[Archive] bInvalidateOlderFiles=1`` and ``sResourceDataDirsFinal=`` (empty).") }
if ($logging -ne '1') { $notes.Add("Papyrus logging is off in $iniOwner. Turn it on for testing (``[Papyrus] bEnableLogging=1``, ``bEnableTrace=1``, ``bLoadDebugInformation=1``).") }
foreach ($n in $notes) { Line "- $n" }
Line

# The Windows user folder name identifies the account; keep it out of the file
# and out of anything printed, since both may end up in a public repository.
$dir = Split-Path -Parent $OutFile
if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
Set-Content -LiteralPath $OutFile -Value (Hide-UserFolder $md.ToString()) -Encoding utf8
Write-Host "Wrote $OutFile"
Write-Host "Installs found: $($infos.Count)"
foreach ($n in $notes) { Write-Host (Hide-UserFolder " - $n") }
