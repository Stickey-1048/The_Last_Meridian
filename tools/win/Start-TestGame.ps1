<#
.SYNOPSIS
  Starts the base game through Mod Organizer in the test profile, reports which
  copy of the game actually started, waits for it to close, and collects the
  results.

.DESCRIPTION
  Why this exists: on a PC with more than one copy of Fallout 4, picking a
  program in Mod Organizer's Run list is not enough to be sure which copy
  runs. The game's own launcher is reported to start the copy recorded in the
  Windows registry, and a Run-list entry can point at another folder. On
  2026-11-12 the first in-game attempt showed the Fallout London menu, and the
  console could not find this project's quest. This script removes the guess.

  What it does:
    1. Checks the test build is installed and switched on in the test profile.
    2. Starts Mod Organizer with
           ModOrganizer.exe -p "<profile>" run "<managed game folder>\Fallout4.exe"
       which is Mod Organizer's own command for running one program inside its
       virtual file system, in a named profile. The launcher is not involved.
    3. When Fallout4.exe appears, reads from the running process which file it
       was started from and whether Mod Organizer's file system is loaded in it.
    4. Waits until the game is closed, then runs Get-TestResults.ps1, which
       puts everything on the clipboard.

  What it changes: Mod Organizer remembers the test profile as the selected
  one, exactly as if it had been picked in the Profile list. Nothing else. It
  refuses to run if the folder Mod Organizer manages is a Fallout London copy,
  and it never closes or stops a program itself.

  Status: tested on Linux PowerShell 7 with stand-ins for Mod Organizer and
  the game. The Mod Organizer command line was read from the 2.5.2 source
  (src/commandline.cpp, "run"); it has NOT yet been run against a real Mod
  Organizer.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\win\Start-TestGame.ps1
#>
[CmdletBinding()]
param(
    # Defaults come from build\install-manifest.json (written by Install-Dev.ps1).
    [string]$ModOrganizerRoot,
    [string]$ProfileName,
    # How long to wait for Fallout4.exe to appear after starting Mod Organizer.
    [int]$StartTimeoutSeconds = 180,
    # If Mod Organizer opened but started nothing: how long to wait for the game to be started by hand.
    [int]$ManualTimeoutSeconds = 900,
    # How long to wait for an open Mod Organizer or game to be closed first.
    [int]$CloseTimeoutMinutes = 10,
    # Lines to show at the top of the collected results.
    [string[]]$Preface = @(),
    # Overrides for testing off Windows.
    [string]$DocumentsRoot,
    [string]$LocalAppDataRoot,
    [switch]$NoClipboard
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Tlm.psm1') -Force

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$build = Join-Path $repo 'build'
$modName = 'TheLastMeridian-Dev'
$pluginName = 'TheLastMeridian.esp'

$manifestPath = Join-Path $build 'install-manifest.json'
$m = $null
if (Test-Path -LiteralPath $manifestPath) { $m = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json }
function Get-ManifestValue([string]$name) {
    if ($m -and ($m.PSObject.Properties.Name -contains $name)) { return $m.$name }
    return $null
}
if (-not $ModOrganizerRoot) { $ModOrganizerRoot = Get-ManifestValue 'ModOrganizerRoot' }
if (-not $ModOrganizerRoot) { $ModOrganizerRoot = 'C:\Modlists\TMR' }
if (-not $ProfileName) { $ProfileName = Get-ManifestValue 'ProfileName' }
if (-not $ProfileName) {
    $pf = Get-ManifestValue 'ProfileFolder'
    $ProfileName = if ($pf) { Split-Path -Leaf $pf } else { 'TLM-Dev' }
}
if ($ProfileName -notmatch '^[\w .\-]+$') { throw "Unusable profile name: $ProfileName" }

# ------------------------------------------------------------- checks
$mo = Get-ModOrganizerInfo -Root $ModOrganizerRoot
if (-not $mo) { throw "No ModOrganizer.ini in $ModOrganizerRoot" }
$moExe = Join-Path $mo.Root 'ModOrganizer.exe'
if (-not (Test-Path -LiteralPath $moExe)) { throw "No ModOrganizer.exe in $($mo.Root)" }
if (-not $mo.GamePath) { throw "ModOrganizer.ini in $($mo.Root) names no game folder." }
if (Test-FalloutLondonFolder $mo.GamePath) {
    throw "The folder Mod Organizer manages, $($mo.GamePath), is a Fallout London copy. This project is tested on the base game only; nothing was started."
}
$gameExe = Join-Path $mo.GamePath 'Fallout4.exe'
if (-not (Test-Path -LiteralPath $gameExe)) { throw "No Fallout4.exe in $($mo.GamePath)" }

$profileFolder = Join-Path $mo.ProfilesDirectory $ProfileName
$installHint = 'Run:  powershell -ExecutionPolicy Bypass -File tools\win\Run-FirstBuild.ps1 -Install'
if (-not (Test-Path -LiteralPath $profileFolder)) { throw "The test profile '$ProfileName' does not exist yet. $installHint" }
$modOn = [bool](@(@(Read-RawLines (Join-Path $profileFolder 'modlist.txt')) | Where-Object { $_ -ieq "+$modName" }).Count)
$pluginOn = [bool](@(@(Read-RawLines (Join-Path $profileFolder 'plugins.txt')) | Where-Object { $_ -ieq "*$pluginName" }).Count)
if (-not $modOn) { throw "The mod '$modName' is not switched on in profile '$ProfileName'. $installHint" }
if (-not $pluginOn) { throw "$pluginName is not active in profile '$ProfileName'. $installHint" }
$installedPlugin = Join-Path (Join-Path $mo.ModsDirectory $modName) $pluginName
if (-not (Test-Path -LiteralPath $installedPlugin)) { throw "The test build is not installed ($installedPlugin is missing). $installHint" }

# Mod Organizer has to start fresh for the profile to be the one named here, and a
# game that is already running would be mistaken for the one this script starts.
if (-not (Wait-GameAndManagerClosed -TimeoutMinutes $CloseTimeoutMinutes)) {
    throw 'Mod Organizer or Fallout 4 is still open. Close them, then run this again.'
}

# ------------------------------------------------------------- start
$ev = New-Object System.Collections.Generic.List[string]
foreach ($l in $Preface) { $ev.Add($l) }
function Say([string]$s = '') { $ev.Add($s); Write-Host $s }

# From here on nothing is allowed to stop the script before the results are
# collected: whatever goes wrong is written into them instead.
$startedAt = Get-Date
$game = $null
$rightGame = $false
$startedFrom = $null
try {
    $builtPlugin = Join-Path $build $pluginName
    $sameAsBuild = if (-not (Test-Path -LiteralPath $builtPlugin)) { 'no build file to compare with' }
    elseif ((Get-FileHash -LiteralPath $builtPlugin).Hash -eq (Get-FileHash -LiteralPath $installedPlugin).Hash) { 'yes' }
    else { 'NO: the installed plugin is not the one in build\. Run the install again.' }

    $argLine = '-p "{0}" run "{1}"' -f $ProfileName, $gameExe
    Say '== Starting the game =='
    Say "Game to start        : $gameExe  (Fallout4.exe $(Get-ExeVersion $gameExe))"
    Say "Through              : $moExe"
    Say "Command line         : ModOrganizer.exe $argLine"
    Say "Profile              : $ProfileName  (mod switched on: $modOn; plugin active: $pluginOn)"
    Say "Installed plugin is the current build: $sameAsBuild"
    $registryPath = Get-BethesdaInstalledPath
    if ($registryPath) { Say "Game folder in the Windows registry: $registryPath$(if (Test-SamePath $registryPath $mo.GamePath) { '  (the managed folder)' } else { '  (NOT the managed folder; the launcher would start this one)' })" }
    Say "Started at           : $($startedAt.ToString('yyyy-MM-dd HH:mm:ss'))"

    $moProc = Start-Process -FilePath $moExe -ArgumentList $argLine -WorkingDirectory $mo.Root -PassThru
    # Windows PowerShell 5.1 only reports the exit code later if the handle was read while the process lived.
    try { $null = $moProc.Handle } catch { }

    Write-Host ''
    Write-Host 'Waiting for the game to appear. Mod Organizer needs a moment to start first.'

    # Waits for a Fallout4.exe process. Gives up early if Mod Organizer has gone.
    function Wait-ForGame([int]$seconds) {
        $deadline = (Get-Date).AddSeconds($seconds)
        $lastNote = Get-Date
        while ((Get-Date) -lt $deadline) {
            $running = @(Get-RunningGame)
            if ($running.Count) { return $running[0] }
            if ($moProc.HasExited -and -not (Test-ModOrganizerRunning)) { return $null }
            if (((Get-Date) - $lastNote).TotalSeconds -ge 20) {
                Write-Host '  ... still waiting. If Mod Organizer is showing a question or a message, answer it.'
                $lastNote = Get-Date
            }
            Start-Sleep -Milliseconds 500
        }
        return $null
    }

    $game = Wait-ForGame $StartTimeoutSeconds
    $byHand = $false
    if (-not $game -and -not ($moProc.HasExited -and -not (Test-ModOrganizerRunning))) {
        # Mod Organizer is open but started nothing: carry on by hand in its window.
        $byHand = $true
        Say ''
        Say "Mod Organizer did not start the game by itself within $StartTimeoutSeconds seconds."
        Write-Host 'Do it by hand in the Mod Organizer window that is open:'
        Write-Host "  1. Profile list (top): choose   $ProfileName"
        Write-Host '  2. List next to the Run button (top right): choose   Fallout 4   (NOT Fallout Launcher, NOT F4SE)'
        Write-Host '  3. Click Run.'
        Write-Host "This window keeps watching for the game for another $([int]($ManualTimeoutSeconds / 60)) minutes."
        $game = Wait-ForGame $ManualTimeoutSeconds
    }

    if (-not $game) {
        Say ''
        if ($moProc.HasExited -and -not (Test-ModOrganizerRunning)) { Say "RESULT: the game did NOT start. Mod Organizer closed again$(if ($moProc.HasExited) { " (exit code $($moProc.ExitCode))" })." }
        else { Say 'RESULT: the game did NOT start. Mod Organizer is still open; look at its window for a message.' }
        Write-Host ''
        Write-Host 'To run the test by hand instead: open Mod Organizer, choose the profile above in the Profile list,'
        Write-Host 'choose   Fallout 4   (NOT Fallout Launcher) in the list next to the Run button, click Run, do the'
        Write-Host 'test in the game, quit, and then run:'
        Write-Host '    powershell -ExecutionPolicy Bypass -File tools\win\Get-TestResults.ps1'
    } else {
        # Give the process a moment to load its libraries before looking at them.
        Start-Sleep -Seconds 4
        $facts = Get-ProcessFacts $game
        for ($i = 0; $i -lt 5 -and -not @($facts.Modules | Where-Object { $_ -match '(?i)^usvfs' }).Count; $i++) {
            Start-Sleep -Seconds 2
            if (-not @(Get-RunningGame | Where-Object { $_.Id -eq $game.Id }).Count) { break }
            $facts = Get-ProcessFacts $game
        }
        $usvfs = @($facts.Modules | Where-Object { $_ -match '(?i)^usvfs' })
        $f4se = @($facts.Modules | Where-Object { $_ -match '(?i)^f4se' })

        # Windows' own process table: a second way to read the file name, and who started the process.
        $parent = $null
        $startedFrom = $facts.Path
        if (Get-Command Get-CimInstance -ErrorAction SilentlyContinue) {
            try {
                $cim = Get-CimInstance Win32_Process -Filter "ProcessId = $($game.Id)" -ErrorAction Stop
                if ($cim) {
                    if (-not $startedFrom -and $cim.ExecutablePath) { $startedFrom = $cim.ExecutablePath }
                    $pp = Get-Process -Id $cim.ParentProcessId -ErrorAction SilentlyContinue
                    $parent = if ($pp) { "$($pp.ProcessName) (id $($cim.ParentProcessId))" } else { "process $($cim.ParentProcessId), which has already ended" }
                }
            } catch { }
        }
        $rightGame = [bool]$startedFrom -and (Test-SamePath $startedFrom $gameExe)

        Say ''
        Say '== The game that actually started =='
        if ($byHand) { Say 'Started by hand from the Mod Organizer window, not by this script''s command.' }
        Say "Process              : id $($facts.Id)$(if ($facts.Started) { ", started $($facts.Started.ToString('HH:mm:ss'))" })$(if ($parent) { ", started by $parent" })"
        Say "Started from         : $(if ($startedFrom) { $startedFrom } else { '(could not be read)' })"
        if (-not $startedFrom) { Say 'Is the managed base game : UNKNOWN: Windows did not let this script read the file name.' }
        elseif ($rightGame) { Say 'Is the managed base game : YES' }
        else {
            $kind = if (Test-FalloutLondonFolder (Split-Path -Parent $startedFrom)) { 'It is a FALLOUT LONDON copy.' } else { 'It is another copy of the game.' }
            Say "Is the managed base game : NO. $kind This project's files are not visible to it."
        }
        Say "Mod Organizer's file system inside the game : $(if ($usvfs.Count) { "YES ($($usvfs -join ', ') is loaded)" } elseif ($facts.Modules.Count) { "NOT DETECTED among $($facts.Modules.Count) loaded libraries" } else { 'UNKNOWN: the list of loaded libraries could not be read' })"
        Say "Script extender (F4SE) inside the game      : $(if ($f4se.Count) { "yes ($($f4se -join ', '))" } elseif ($facts.Modules.Count) { 'no' } else { 'unknown' })"

        Write-Host ''
        if ($startedFrom -and -not $rightGame) {
            Write-Host 'This is the wrong copy of the game, so there is nothing to test in it. Quit the game;'
            Write-Host 'this window will then collect what it can and put it on the clipboard.'
        } else {
            Write-Host 'IN THE GAME NOW:'
            Write-Host '  1. At the main menu press the ~ key (left of the 1 key), type   coc qasmoke   and press Enter.'
            Write-Host '  2. When the room has loaded, press ~ to close the console. Within about ten seconds a line should'
            Write-Host '     appear in the top-left corner:  The Last Meridian test build is loaded.'
            Write-Host '     (If it never appears, the plugin is not loaded. Skip step 3 and quit.)'
            Write-Host '  3. Press ~, type   cqf TLM_Core RunSelfTest   press Enter, press ~ again to close the console,'
            Write-Host '     and wait for a message box (about 15 seconds).'
            Write-Host '  4. Quit the game: Esc, Quit, Quit to Desktop.'
        Write-Host '  (Another scenario: add its number, for example   cqf TLM_Core RunSelfTest 2   . One fresh session each.)'
            Write-Host 'Leave this window open. When the game closes it collects the results by itself.'
        }

        while (@(Get-RunningGame).Count) { Start-Sleep -Seconds 2 }
        $endedAt = Get-Date
        Say "Game closed at       : $($endedAt.ToString('HH:mm:ss'))  (ran for $([int]($endedAt - $startedAt).TotalSeconds) seconds)"
    }

    # Mod Organizer tidies up and closes by itself after a command-line run.
    $moDeadline = (Get-Date).AddSeconds(90)
    while ((Test-ModOrganizerRunning) -and (Get-Date) -lt $moDeadline) { Start-Sleep -Seconds 1 }
    if (Test-ModOrganizerRunning) { Say 'Mod Organizer is still open. That is harmless; close it when you like.' }
    Say "Mod Organizer now has profile '$ProfileName' selected. Switch back to your own profile before you play."
} catch {
    Say ''
    Say "UNEXPECTED ERROR in Start-TestGame.ps1: $($_.Exception.Message)"
    foreach ($line in ("$($_.ScriptStackTrace)" -split "`r?`n")) { Say "    $line" }
}

# ------------------------------------------------------------ collect
Write-Host ''
$resArgs = @{ ModOrganizerRoot = $mo.Root; Since = $startedAt; Preface = $ev.ToArray() }
if ($DocumentsRoot) { $resArgs['DocumentsRoot'] = $DocumentsRoot }
if ($LocalAppDataRoot) { $resArgs['LocalAppDataRoot'] = $LocalAppDataRoot }
if ($NoClipboard) { $resArgs['NoClipboard'] = $true }
try {
    & (Join-Path $PSScriptRoot 'Get-TestResults.ps1') @resArgs
} catch {
    # Even then, what this script saw goes on the clipboard.
    $lines = @($ev) + @('', "Get-TestResults.ps1 failed: $($_.Exception.Message)") + @("$($_.ScriptStackTrace)" -split "`r?`n")
    $text = Hide-UserFolder ($lines -join [Environment]::NewLine)
    Write-Host $text
    try { Set-Content -LiteralPath (Join-Path $build 'test-results.txt') -Value $text -Encoding utf8 } catch { }
    if (-not $NoClipboard -and (Get-Command Set-Clipboard -ErrorAction SilentlyContinue)) {
        try { Set-Clipboard -Value $text; Write-Host 'That text is on your clipboard. Click in the chat and press Ctrl+V to send it.' } catch { }
    }
}

if (-not $game -or ($startedFrom -and -not $rightGame)) { exit 1 }
