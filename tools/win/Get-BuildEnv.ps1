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
    # Overrides for testing off Windows.
    [string]$SteamRoot,
    [string]$DocumentsRoot,
    [string]$LocalAppDataRoot,
    [string]$OutFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Tlm.psm1') -Force

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if (-not $OutFile) { $OutFile = Join-Path (Join-Path (Join-Path $repo 'docs') 'design') 'BUILD_ENV.md' }

function YesNo([bool]$b) { if ($b) { 'yes' } else { 'no' } }
function OrDash($v) { if ($null -eq $v -or "$v" -eq '') { '-' } else { "$v" } }

$installs = @(Find-Fallout4Installs -SteamRoot $SteamRoot -ExtraRoot $ExtraRoot)
$infos = @($installs | ForEach-Object {
        $i = Get-Fallout4InstallInfo -Root $_.Root
        $i | Add-Member -NotePropertyName Store -NotePropertyValue $_.Store
        $i | Add-Member -NotePropertyName FoundBy -NotePropertyValue $_.FoundBy
        $i
    })
$user = Get-Fallout4UserState -DocumentsRoot $DocumentsRoot -LocalAppDataRoot $LocalAppDataRoot

$md = New-Object System.Text.StringBuilder
function Line([string]$s = '') { [void]$md.AppendLine($s) }

Line '# Build environment'
Line
Line "Recorded $(Get-Date -Format 'yyyy-MM-dd HH:mm') by ``tools/win/Get-BuildEnv.ps1`` (read-only scan). Re-run it after any game or Creation Kit update."
Line
Line "- OS: $([System.Runtime.InteropServices.RuntimeInformation]::OSDescription)"
Line "- PowerShell: $($PSVersionTable.PSVersion)"
$dotnet = $null; try { $dotnet = (& dotnet --version 2>$null) } catch { }
$git = $null; try { $git = (& git --version 2>$null) } catch { }
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
        Line "| Mod manager | $($i.ModManagerHint) |"
        Line "| TheLastMeridian.esp in Data | $(YesNo $i.TlmInstalled) |"
        Line
    }
}

Line '## Shared settings, saves and load order'
Line
Line 'These live outside the game folder. To our knowledge every Fallout 4 install on the machine (Steam and GOG alike) reads the same ones, so a plugin enabled for one install is enabled for the other.'
Line
Line '| Item | Value |'
Line '|---|---|'
Line "| My Games folder | ``$($user.MyGamesFolder)`` (exists: $(YesNo $user.MyGamesExists)) |"
Line "| Fallout4Custom.ini | exists: $(YesNo $user.CustomIniExists) |"
Line "| Loose files enabled | bInvalidateOlderFiles=$(OrDash $user.InvalidateOlderFiles); sResourceDataDirsFinal=$(if ($null -eq $user.ResourceDataDirs) { '-' } elseif ($user.ResourceDataDirs -eq '') { '(empty, as required)' } else { $user.ResourceDataDirs }) |"
Line "| Papyrus logging | bEnableLogging=$(OrDash $user.PapyrusLogging); log file present: $(YesNo $user.PapyrusLogExists) |"
Line "| Saves | $($user.SaveCount) file(s); newest $(OrDash $user.NewestSave) |"
foreach ($p in $user.PluginLists) {
    Line "| Load order | ``$($p.Path)``: $($p.Active) active of $($p.Listed); TheLastMeridian.esp listed: $(YesNo $p.TlmListed), active: $(YesNo $p.TlmActive) |"
}
if (@($user.PluginLists).Count -eq 0) { Line '| Load order | no plugins.txt found |' }
Line

Line '## What this means for the build'
Line
$notes = New-Object System.Collections.Generic.List[string]
$dev = @($infos | Where-Object { $_.CreationKitVersion -and -not $_.FalloutLondon })
if ($infos.Count -eq 0) {
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
    if ($i.F4SEVersion) { $notes.Add("``$($i.Root)``: F4SE is installed. The slice must not depend on it; test launches should use Fallout4.exe directly.") }
}
if ($infos.Count -gt 1) { $notes.Add('More than one install shares the settings and load order above. Enabling the test plugin affects all of them. A mod manager profile or a separate test profile is the clean way to isolate it.') }
if ($user.InvalidateOlderFiles -ne '1') { $notes.Add('Loose files are not enabled in Fallout4Custom.ini, so compiled scripts placed in Data\Scripts will not load. Needs `[Archive] bInvalidateOlderFiles=1` and `sResourceDataDirsFinal=` (empty).') }
if ($user.PapyrusLogging -ne '1') { $notes.Add('Papyrus logging is off. Turn it on for testing (`[Papyrus] bEnableLogging=1`, `bEnableTrace=1`, `bLoadDebugInformation=1`).') }
foreach ($n in $notes) { Line "- $n" }
Line

$dir = Split-Path -Parent $OutFile
if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
Set-Content -LiteralPath $OutFile -Value $md.ToString() -Encoding utf8
Write-Host "Wrote $OutFile"
Write-Host "Installs found: $($infos.Count)"
foreach ($n in $notes) { Write-Host " - $n" }
