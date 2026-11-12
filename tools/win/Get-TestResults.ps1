<#
.SYNOPSIS
  Collects what the game wrote during an in-game test, and what the game was
  given to load, and puts it on the clipboard.

.DESCRIPTION
  READ-ONLY. After a test session in the game (console:
  cqf TLM_Core RunSelfTest), this gathers into build\test-results.txt, and
  copies to the clipboard:

    - a verdict: did the plugin load, did the self-test run, what did it report
    - the self-test's own log   Documents\My Games\Fallout4\Logs\Script\User\TLM.0.log
    - from the game's script log (Papyrus.0.log): its first lines, and every
      line that mentions this project's scripts; and a short digest of the
      logs the game kept from the three sessions before
    - what the game was given: the installed mod folder, the test profile's
      lists and settings
    - which copy of the game each program registered in Mod Organizer starts,
      the game folder recorded in the Windows registry, and whether the game
      folders hold Fallout London files
    - the lines of Mod Organizer's own log that concern starting programs

  Both script logs only exist if Papyrus logging was on for the session; the
  test profile made by Install-Dev.ps1 -CreateProfile turns it on.
  The Windows user folder name is replaced with %USERPROFILE%.

  Each part is collected on its own: if one part fails, the report says so in
  that part and the rest is still written.

  Start-TestGame.ps1 runs this by itself when the game closes.

  Status: tested on Linux PowerShell 7 against stand-in folders and log files.
  The first version ran on the owner's PC on 2026-11-12; this one has not.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\win\Get-TestResults.ps1
#>
[CmdletBinding()]
param(
    [string]$DocumentsRoot,
    [string]$LocalAppDataRoot,
    # The Mod Organizer instance. Default: the one the build was installed into.
    [string]$ModOrganizerRoot,
    # Lines to show right under the header (Start-TestGame.ps1 passes what it saw).
    [string[]]$Preface = @(),
    # When the test session started. Logs written before this are marked as old.
    [datetime]$Since = [datetime]::MinValue,
    [switch]$NoClipboard
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Tlm.psm1') -Force

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$build = Join-Path $repo 'build'
New-Item -ItemType Directory -Force -Path $build | Out-Null
if (-not $DocumentsRoot) { $DocumentsRoot = [Environment]::GetFolderPath('MyDocuments') }
if (-not $LocalAppDataRoot) { $LocalAppDataRoot = $env:LOCALAPPDATA }
$myGames = Join-Path (Join-Path $DocumentsRoot 'My Games') 'Fallout4'
$scriptLogs = Join-Path (Join-Path $myGames 'Logs') 'Script'
$userLog = Join-Path (Join-Path $scriptLogs 'User') 'TLM.0.log'
$papyrusLog = Join-Path $scriptLogs 'Papyrus.0.log'
$haveSince = $Since -gt [datetime]::MinValue

$manifestPath = Join-Path $build 'install-manifest.json'
$m = $null
try { if (Test-Path -LiteralPath $manifestPath) { $m = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json } } catch { $m = $null }
function Get-ManifestValue([string]$name) {
    if ($m -and ($m.PSObject.Properties.Name -contains $name)) { return $m.$name }
    return $null
}
if (-not $ModOrganizerRoot) { $ModOrganizerRoot = Get-ManifestValue 'ModOrganizerRoot' }
if (-not $ModOrganizerRoot) { $ModOrganizerRoot = 'C:\Modlists\TMR' }

# ---------------------------------------------------------------- helpers
# Each part of the report is collected separately, then put in reading order.
function New-Part { return , (New-Object System.Collections.Generic.List[string]) }
function Add-Failure($part, $err) {
    $part.Add("  ** this part of the report could not be completed: $($err.Exception.Message) **")
    if ($err.InvocationInfo) { $part.Add("     (Get-TestResults.ps1 line $($err.InvocationInfo.ScriptLineNumber))") }
}
function Get-Stamp($file) { return $file.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss') }
function Get-FileNote([string]$path) {
    $f = Get-Item -LiteralPath $path
    $age = [int]((Get-Date) - $f.LastWriteTime).TotalMinutes
    $old = if ($haveSince -and $f.LastWriteTime -lt $Since) { '  ** written BEFORE this test session: not from this run **' } else { '' }
    return "$path  (written $(Get-Stamp $f), $age minute(s) ago, $($f.Length) bytes)$old"
}
function Test-FromThisRun([string]$path) {
    if (-not (Test-Path -LiteralPath $path)) { return $false }
    if (-not $haveSince) { return $true }
    return ((Get-Item -LiteralPath $path).LastWriteTime -ge $Since)
}
function Add-FileLines($part, [string]$path, [int]$max = 40) {
    if (-not (Test-Path -LiteralPath $path)) { $part.Add("  (missing) $path"); return }
    $f = Get-Item -LiteralPath $path
    $part.Add("  $($f.Name)  (written $(Get-Stamp $f), $($f.Length) bytes)")
    $n = 0
    foreach ($l in @(Read-RawLines $path)) {
        if ($n -ge $max) { $part.Add('      ...'); break }
        $part.Add("      $l"); $n++
    }
}
function Get-FileCount([string]$dir, [int]$cap = 5000) {
    # Counts files under a folder, stopping at the cap so a huge folder costs little.
    $n = 0
    try {
        foreach ($f in [System.IO.Directory]::EnumerateFiles($dir, '*', [System.IO.SearchOption]::AllDirectories)) {
            $n++
            if ($n -ge $cap) { return "$cap+" }
        }
    } catch { return '?' }
    return "$n"
}
function Get-LondonLines([string]$path, [int]$max = 6) {
    if (-not (Test-Path -LiteralPath $path)) { return @() }
    return @(@(Read-RawLines $path) | Where-Object { $_ -match '(?i)london' } | Select-Object -First $max)
}
function Get-FolderKind([string]$root) {
    if (-not $root) { return 'unknown' }
    if (-not (Test-Path -LiteralPath $root)) { return 'folder does not exist' }
    if (Test-FalloutLondonFolder $root) { return 'FALLOUT LONDON copy' }
    if (Test-Path -LiteralPath (Join-Path $root 'Fallout4.exe')) { return "base game, Fallout4.exe $(Get-ExeVersion (Join-Path $root 'Fallout4.exe'))" }
    return 'no Fallout4.exe here'
}
function Add-DataNotes($part, [string]$root, [string]$label) {
    $part.Add("$label : $root")
    $data = Join-Path $root 'Data'
    if (-not (Test-Path -LiteralPath $data)) { $part.Add('    no Data folder'); return }
    $londonFiles = @(Get-ChildItem -LiteralPath $data -File -Filter 'London*' -ErrorAction SilentlyContinue)
    $part.Add("    Fallout London master in Data: $(if (Test-FalloutLondonFolder $root) { 'YES' } else { 'no' }); files in Data named London*: $($londonFiles.Count)")
    $dirs = @(Get-ChildItem -LiteralPath $data -Directory -ErrorAction SilentlyContinue | Sort-Object Name)
    if ($dirs.Count) {
        $notes = @($dirs | Select-Object -First 24 | ForEach-Object { "$($_.Name) ($(Get-FileCount $_.FullName))" })
        $part.Add("    Loose-file folders in Data (file counts): $($notes -join ', ')$(if ($dirs.Count -gt 24) { ', ...' })")
    } else {
        $part.Add('    Loose-file folders in Data: none')
    }
    $menuVideo = Join-Path (Join-Path $data 'Video') 'MainMenuLoop.bk2'
    if (Test-Path -LiteralPath $menuVideo) { $f = Get-Item -LiteralPath $menuVideo; $part.Add("    Main-menu video Data\Video\MainMenuLoop.bk2: $($f.Length) bytes, $(Get-Stamp $f)") }
    else { $part.Add('    Main-menu video Data\Video\MainMenuLoop.bk2: not present') }
    foreach ($name in 'MainMenu.swf', 'LoadingMenu.swf') {
        $swf = Join-Path (Join-Path $data 'Interface') $name
        if (Test-Path -LiteralPath $swf) { $f = Get-Item -LiteralPath $swf; $part.Add("    Loose Data\Interface\$name : $($f.Length) bytes, $(Get-Stamp $f)") }
    }
}

# What later parts need from earlier ones; set here so a failed part leaves them defined.
$selfLines = @()
$selfFromRun = $false
$papLines = @()
$papFromRun = $false
$mo = $null
$registryPath = $null

# ------------------------------------------------------------------ logs
$selfTest = New-Part
try {
    $selfFromRun = Test-FromThisRun $userLog
    if (Test-Path -LiteralPath $userLog) {
        $selfTest.Add((Get-FileNote $userLog))
        $selfLines = @(Get-Content -LiteralPath $userLog)
        foreach ($l in $selfLines) { $selfTest.Add("  $l") }
    } else {
        $selfTest.Add("Not found: $userLog")
        $selfTest.Add('Either the self-test did not run, or Papyrus logging was off for that session.')
    }
} catch { Add-Failure $selfTest $_ }

$papyrus = New-Part
try {
    $papFromRun = Test-FromThisRun $papyrusLog
    if (Test-Path -LiteralPath $papyrusLog) {
        $papyrus.Add((Get-FileNote $papyrusLog))
        $papLines = @(Get-Content -LiteralPath $papyrusLog)
        $papyrus.Add("Lines in all: $($papLines.Count)")
        $papyrus.Add('-- first 12 lines --')
        foreach ($l in ($papLines | Select-Object -First 12)) { $papyrus.Add("  $l") }
        $papyrus.Add("Lines naming Fallout London: $(@($papLines | Where-Object { $_ -match '(?i)london|folon' }).Count)")
        $ours = @($papLines | Where-Object { $_ -match 'TLM' })
        $papyrus.Add("-- lines mentioning this project: $($ours.Count)$(if ($ours.Count -gt 250) { ' (first 250 shown)' }) --")
        foreach ($l in ($ours | Select-Object -First 250)) { $papyrus.Add("  $l") }
    } else {
        $papyrus.Add("Not found: $papyrusLog")
        $papyrus.Add('Papyrus logging was off, or the game has not been run with it on.')
    }
} catch { Add-Failure $papyrus $_ }

# The game keeps the logs of the three sessions before the last one. A short
# digest of each: enough to tell which game data an earlier session had loaded.
$olderLogs = New-Part
try {
    foreach ($n in 1..3) {
        $p = Join-Path $scriptLogs "Papyrus.$n.log"
        if (-not (Test-Path -LiteralPath $p)) { continue }
        $f = Get-Item -LiteralPath $p
        $ls = @(Get-Content -LiteralPath $p)
        $tlm = @($ls | Where-Object { $_ -match 'TLM' })
        $lon = @($ls | Where-Object { $_ -match '(?i)london|folon' })
        $olderLogs.Add("Papyrus.$n.log  (written $(Get-Stamp $f), $($f.Length) bytes, $($ls.Count) lines; naming this project: $($tlm.Count); naming Fallout London: $($lon.Count))")
        foreach ($l in ($ls | Select-Object -First 4)) { $olderLogs.Add("    $l") }
        foreach ($l in ($tlm | Select-Object -First 6)) { $olderLogs.Add("    this project: $l") }
        foreach ($l in ($lon | Select-Object -First 4)) { $olderLogs.Add("    London: $l") }
    }
} catch { Add-Failure $olderLogs $_ }

# --------------------------------------------------------------- verdict
$verdict = New-Part
try {
    $coreStarted = $papFromRun -and [bool](@($papLines | Where-Object { $_ -match 'TLM_Core: started' }).Count)
    $scriptErrors = @()
    # The game writes "error: ..." and "warning: ..." itself; the self-test's own lines are not that.
    if ($papFromRun) { $scriptErrors = @($papLines | Where-Object { $_ -match 'TLM' -and $_ -notmatch 'TLM_SelfTest:' -and $_ -match '(?i)\b(error|warning):' }) }
    $resultLine = $null
    $passCount = 0
    $failLines = @()
    $aborted = $false
    if ($selfFromRun) {
        $resultLine = @($selfLines | Where-Object { $_ -match '==== RESULT:' }) | Select-Object -Last 1
        $passCount = @($selfLines | Where-Object { $_ -match '\]\s*PASS\s' }).Count
        $failLines = @($selfLines | Where-Object { $_ -match '\]\s*FAIL\s' })
        $aborted = [bool](@($selfLines | Where-Object { $_ -match 'ABORTED' }).Count)
    }
    if (-not (Test-Path -LiteralPath $papyrusLog)) {
        $verdict.Add('Game script log     : none. The game did not write one, so the test profile''s settings were not in effect')
        $verdict.Add('                      for that session (or the game was never started with them).')
    } elseif (-not $papFromRun) {
        $verdict.Add('Game script log     : only an OLD one, from before this session. The game did not write one this time.')
    } else {
        $when = if ($haveSince) { 'written this session' } else { "found, written $(Get-Stamp (Get-Item -LiteralPath $papyrusLog)); check that time against your last session" }
        $verdict.Add("Game script log     : $when ($($papLines.Count) lines)")
    }
    if ($coreStarted) {
        $verdict.Add('Plugin and scripts  : LOADED. The core quest started and its script ran ("TLM_Core: started" is in the log).')
    } elseif ($papFromRun) {
        $verdict.Add('Plugin and scripts  : NO SIGN of them. The core quest''s start line is not in the log, so the plugin was not loaded,')
        $verdict.Add('                      its script was not found, or the session began from an older save.')
    } else {
        $verdict.Add('Plugin and scripts  : unknown (no script log from this session)')
    }
    if ($scriptErrors.Count) {
        $verdict.Add("Script problems     : $($scriptErrors.Count) error or warning line(s) in the game's log name this project$(if ($scriptErrors.Count -gt 12) { ' (first 12 shown)' }):")
        foreach ($l in ($scriptErrors | Select-Object -First 12)) { $verdict.Add("    $l") }
    } elseif ($papFromRun) {
        $verdict.Add('Script problems     : none reported by the game for this project''s scripts')
    }
    if ($aborted) {
        $verdict.Add('Self-test           : NOT RUN: the quests had already been started in that session. Use a fresh session.')
    } elseif ($resultLine) {
        $verdict.Add("Self-test           : RAN. $(($resultLine -replace '^.*==== RESULT:\s*', '') -replace '\s*====\s*$', '')  (PASS lines counted: $passCount, FAIL lines: $($failLines.Count))")
        foreach ($l in $failLines) { $verdict.Add("    $l") }
    } elseif ($selfFromRun) {
        $verdict.Add("Self-test           : STARTED BUT DID NOT FINISH: the log has no RESULT line ($passCount PASS, $($failLines.Count) FAIL so far)")
    } elseif (Test-Path -LiteralPath $userLog) {
        $verdict.Add('Self-test           : not run this session (the only self-test log is an old one)')
    } else {
        $verdict.Add('Self-test           : not run (no self-test log)')
    }
    $verdict.Add('A pass here means the scripted rules behaved as the model predicts in the game. It is not a test of the')
    $verdict.Add('quest as a player would meet it: nothing is placed in the world yet.')
} catch { Add-Failure $verdict $_ }

# -------------------------------------------- what the game was given
$given = New-Part
try {
    $modFolder = Get-ManifestValue 'ModFolder'
    if ($modFolder -and (Test-Path -LiteralPath $modFolder)) {
        $given.Add("Mod folder: $modFolder")
        foreach ($f in @(Get-ChildItem -LiteralPath $modFolder -Recurse -File | Where-Object { $_.Extension -in '.esp', '.pex' } | Sort-Object FullName)) {
            $rel = $f.FullName.Substring($modFolder.Length).TrimStart('\', '/')
            $src = if ($f.Extension -eq '.esp') { Join-Path $build $f.Name } else { Join-Path (Join-Path (Join-Path $build 'Scripts') 'TLM') $f.Name }
            $same = 'no build file to compare'
            if (Test-Path -LiteralPath $src) {
                if ((Get-FileHash -LiteralPath $src).Hash -eq (Get-FileHash -LiteralPath $f.FullName).Hash) { $same = 'same as the build' }
                else { $same = 'DIFFERS from the build (run the install again)' }
            }
            $given.Add(("  {0,-34} {1,8} bytes  {2}  {3}" -f $rel, $f.Length, (Get-Stamp $f), $same))
        }
    } else {
        $given.Add("Mod folder not found: $modFolder")
    }
} catch { Add-Failure $given $_ }

try {
    $profileFolder = Get-ManifestValue 'ProfileFolder'
    $given.Add('')
    if ($profileFolder -and (Test-Path -LiteralPath $profileFolder)) {
        $given.Add("Test profile: $profileFolder")
        foreach ($f in @(Get-ChildItem -LiteralPath $profileFolder -File | Sort-Object Name)) {
            $given.Add(("  {0,-24} {1,8} bytes  {2}" -f $f.Name, $f.Length, (Get-Stamp $f)))
        }
        $saves = Join-Path $profileFolder 'saves'
        if (Test-Path -LiteralPath $saves) { $given.Add("  saves folder: $(@(Get-ChildItem -LiteralPath $saves -File).Count) file(s)") }
        $given.Add('plugins.txt (a leading * means active; Mod Organizer leaves the game''s own master files out):')
        Add-FileLines $given (Join-Path $profileFolder 'plugins.txt') 30
        $on = @(@(Read-RawLines (Join-Path $profileFolder 'modlist.txt')) | Where-Object { $_.StartsWith('+') })
        $given.Add("modlist.txt: $($on.Count) mod(s) switched on: $(($on | Select-Object -First 8) -join ', ')")
        $given.Add('settings.ini:')
        Add-FileLines $given (Join-Path $profileFolder 'settings.ini') 20
        $given.Add('Settings the game reads from this profile:')
        foreach ($name in 'fallout4.ini', 'fallout4prefs.ini', 'fallout4custom.ini') {
            $ini = Join-Path $profileFolder $name
            if (-not (Test-Path -LiteralPath $ini)) { $given.Add("  $name : MISSING"); continue }
            $vals = New-Object System.Collections.Generic.List[string]
            foreach ($pair in @(
                    @('Display', 'iSize W'), @('Display', 'iSize H'), @('Display', 'bFull Screen'), @('Display', 'bBorderless'),
                    @('Launcher', 'bEnableFileSelection'), @('General', 'sStartingConsoleCommand'), @('General', 'sTestFile1'),
                    @('General', 'sLocalSavePath'), @('Papyrus', 'bEnableLogging'), @('Papyrus', 'bEnableTrace'),
                    @('Archive', 'bInvalidateOlderFiles'), @('Archive', 'sResourceDataDirsFinal'))) {
                $v = Get-IniValue $ini $pair[0] $pair[1]
                if ($null -ne $v) { $vals.Add("[$($pair[0])] $($pair[1])=$v") }
            }
            $given.Add("  $name : $(if ($vals.Count) { $vals -join '; ' } else { '(none of the settings looked for)' })")
            foreach ($l in (Get-LondonLines $ini)) { $given.Add("      mentions London: $l") }
        }
    } else {
        $given.Add("Test profile not found: $profileFolder")
    }
} catch { Add-Failure $given $_ }

# ------------------------------------------------- which game gets started
$launch = New-Part
try {
    if (Test-Path -LiteralPath (Join-Path $ModOrganizerRoot 'ModOrganizer.ini')) { $mo = Get-ModOrganizerInfo -Root $ModOrganizerRoot }
    $registryPath = Get-BethesdaInstalledPath
    if ($mo) {
        $launch.Add("Mod Organizer instance : $($mo.Root)  (version $($mo.Version))")
        $launch.Add("Game folder it manages : $($mo.GamePath)  [$(Get-FolderKind $mo.GamePath)]")
        $launch.Add("Profile selected now   : $($mo.SelectedProfile)")
        $launch.Add('Programs in its Run list, and the file each one starts:')
        foreach ($e in $mo.Executables) {
            $bin = $e.Binary
            $exists = if ($bin -and (Test-Path -LiteralPath $bin)) { 'yes' } else { 'NO' }
            $folder = if ($bin) { Split-Path -Parent $bin } else { $null }
            $where = 'outside the managed game folder'
            if (Test-SamePath $folder $mo.GamePath) { $where = 'in the managed game folder' }
            elseif ($folder -and (Test-FalloutLondonFolder $folder)) { $where = 'IN A FALLOUT LONDON COPY' }
            $launch.Add(("  {0,2}. {1,-18} {2}" -f $e.Index, $e.Title, $bin))
            $launch.Add(("        file exists: {0}; {1}{2}{3}" -f $exists, $where, $(if ($e.Arguments) { "; arguments: $($e.Arguments)" } else { '' }), $(if ($e.Hidden) { '; hidden' } else { '' })))
        }
    } else {
        $launch.Add("No Mod Organizer instance at $ModOrganizerRoot")
    }
    if ($registryPath) {
        $launch.Add("Game folder in the Windows registry : $registryPath  [$(Get-FolderKind $registryPath)]")
        if ($mo -and -not (Test-SamePath $registryPath $mo.GamePath)) {
            $launch.Add('  This is NOT the folder Mod Organizer manages. The game''s own launcher (Fallout4Launcher.exe, "Fallout Launcher"')
            $launch.Add('  in the Run list) is reported to start the copy named here, whichever folder the launcher itself is in.')
            $launch.Add('  Start-TestGame.ps1 does not use the launcher: it starts Fallout4.exe in the managed folder by its full path.')
        }
    } else {
        $launch.Add('Game folder in the Windows registry : not recorded (or not Windows)')
    }
} catch { Add-Failure $launch $_ }

$folders = New-Part
try {
    if ($mo -and $mo.GamePath -and (Test-Path -LiteralPath $mo.GamePath)) { Add-DataNotes $folders $mo.GamePath 'Managed game folder' }
    if ($registryPath -and (Test-Path -LiteralPath $registryPath) -and -not ($mo -and (Test-SamePath $registryPath $mo.GamePath))) { Add-DataNotes $folders $registryPath 'Registry game folder' }
    if ($mo) {
        $ow = Join-Path $mo.Root 'overwrite'
        if (Test-Path -LiteralPath $ow) {
            $owFiles = @(Get-ChildItem -LiteralPath $ow -Recurse -File -ErrorAction SilentlyContinue)
            $folders.Add("Mod Organizer 'overwrite' folder (always loaded, in every profile): $($owFiles.Count) file(s)")
            foreach ($f in ($owFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 12)) {
                $folders.Add(("    {0,-60} {1,9} bytes  {2}" -f $f.FullName.Substring($ow.Length).TrimStart('\', '/'), $f.Length, (Get-Stamp $f)))
            }
        }
    }
} catch { Add-Failure $folders $_ }

# ----------------------------------------------- shared settings and logs
$shared = New-Part
try {
    $shared.Add("Settings folder every copy of the game shares: $myGames")
    if (Test-Path -LiteralPath $myGames) {
        foreach ($name in 'Fallout4.ini', 'Fallout4Prefs.ini', 'Fallout4Custom.ini') {
            $ini = Join-Path $myGames $name
            if (Test-Path -LiteralPath $ini) {
                $f = Get-Item -LiteralPath $ini
                $shared.Add(("  {0,-20} {1,8} bytes  {2}  lines mentioning London: {3}" -f $name, $f.Length, (Get-Stamp $f), @(Get-LondonLines $ini 999).Count))
            } else { $shared.Add("  $name : not present") }
        }
        # The last day, not just this session: an earlier attempt may have written here too.
        $dayAgo = (Get-Date).AddHours(-24)
        $recent = @(Get-ChildItem -LiteralPath $myGames -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -ge $dayAgo } | Sort-Object LastWriteTime -Descending)
        $shared.Add("  Files written there in the last 24 hours: $($recent.Count)$(if ($recent.Count -gt 20) { ' (newest 20 shown)' })")
        foreach ($f in ($recent | Select-Object -First 20)) {
            $mark = if ($haveSince -and $f.LastWriteTime -ge $Since) { '  (this session)' } else { '' }
            $shared.Add(("    {0,-56} {1,9} bytes  {2}{3}" -f $f.FullName.Substring($myGames.Length).TrimStart('\', '/'), $f.Length, (Get-Stamp $f), $mark))
        }
    } else {
        $shared.Add('  (folder not found)')
    }
    if ($LocalAppDataRoot) {
        $sharedPlugins = Join-Path (Join-Path $LocalAppDataRoot 'Fallout4') 'plugins.txt'
        $shared.Add('Shared load order (used when the game is started outside Mod Organizer):')
        Add-FileLines $shared $sharedPlugins 12
    }
} catch { Add-Failure $shared $_ }

$moLog = New-Part
try {
    if ($mo) {
        $logDir = Join-Path $mo.Root 'logs'
        if (Test-Path -LiteralPath $logDir) {
            $logFiles = @(Get-ChildItem -LiteralPath $logDir -File | Sort-Object LastWriteTime -Descending)
            foreach ($f in ($logFiles | Select-Object -First 6)) { $moLog.Add(("  {0,-36} {1,9} bytes  {2}" -f $f.Name, $f.Length, (Get-Stamp $f))) }
            $main = @($logFiles | Where-Object { $_.Name -like 'mo_interface*.log' } | Select-Object -First 1)
            if ($main.Count) {
                # Mod Organizer may still hold this file open; Get-Content can read it then, a plain byte read may not.
                $all = @(Get-Content -LiteralPath $main[0].FullName)
                # A "spawning binary:" entry is followed by indented lines giving the file, folder and whether it was hooked.
                $keep = New-Object System.Collections.Generic.List[string]
                $inBlock = $false
                foreach ($l in $all) {
                    if ($l -match '(?i)nexus|api.?key|token|passw|account') { $inBlock = $false; continue }
                    if ($l -match '(?i)spawning') { $keep.Add($l); $inBlock = $true; continue }
                    if ($inBlock -and $l -match '^\s+\.\s') { $keep.Add($l); continue }
                    $inBlock = $false
                    if ($l -match '(?i)using game plugin|command line|\[E\]|\[W\]|error|failed|usvfs|profile|Fallout4|f4se') { $keep.Add($l) }
                }
                $moLog.Add("$($main[0].Name): $($all.Count) lines; the last 45 about the game, profiles, starting programs or problems:")
                foreach ($l in ($keep | Select-Object -Last 45)) { $moLog.Add("  $l") }
                if (-not @($keep | Where-Object { $_ -match '(?i)spawning' }).Count) {
                    $moLog.Add('  (No "spawning binary" entries: Mod Organizer only records which file it started when its log level is Debug.)')
                }
            }
        } else {
            $moLog.Add("  no logs folder at $logDir")
        }
    }
} catch { Add-Failure $moLog $_ }

$otherLogs = New-Part
try {
    if ($env:USERPROFILE) {
        foreach ($d in @((Join-Path $env:USERPROFILE 'Documents'), (Join-Path (Join-Path $env:USERPROFILE 'OneDrive') 'Documents'))) {
            $cand = Join-Path (Join-Path (Join-Path (Join-Path $d 'My Games') 'Fallout4') 'Logs') 'Script'
            if ((Test-Path -LiteralPath $cand) -and -not (Test-SamePath $cand $scriptLogs)) {
                $otherLogs.Add("Another script-log folder exists: $cand")
                foreach ($f in @(Get-ChildItem -LiteralPath $cand -Recurse -File | Sort-Object LastWriteTime -Descending | Select-Object -First 5)) {
                    $otherLogs.Add(("  {0,-30} {1,9} bytes  {2}" -f $f.Name, $f.Length, (Get-Stamp $f)))
                }
            }
        }
    }
} catch { Add-Failure $otherLogs $_ }

# --------------------------------------------------------------- assemble
$out = New-Object System.Collections.Generic.List[string]
function Add-Section([string]$title, $part) {
    if ($part.Count -eq 0) { return }
    $out.Add('')
    $out.Add("== $title ==")
    foreach ($l in $part) { $out.Add($l) }
}
$out.Add("The Last Meridian: in-game test results   $(Get-Date -Format 'yyyy-MM-dd HH:mm')")
try {
    $head = Invoke-Native -Exe 'git' -Arguments @('-C', $repo, 'log', '--oneline', '-1')
    if ($head.Found -and $head.ExitCode -eq 0) { $out.Add("Repository commit: $($head.Output | Select-Object -First 1)") }
} catch { }
if ($m) { $out.Add("Installed build  : $(Get-ManifestValue 'Root')  ($(Get-ManifestValue 'Installed'))") }
else { $out.Add('Installed build  : no install manifest (Install-Dev.ps1 has not been run from this folder)') }
if ($haveSince) { $out.Add("Test session began: $($Since.ToString('yyyy-MM-dd HH:mm:ss'))") }
if ($Preface.Count) { $out.Add(''); foreach ($l in $Preface) { $out.Add($l) } }

Add-Section 'Verdict' $verdict
Add-Section 'Self-test log (TLM.0.log)' $selfTest
Add-Section 'Game script log (Papyrus.0.log)' $papyrus
Add-Section 'Script logs of earlier sessions' $olderLogs
Add-Section 'What the game was given' $given
Add-Section 'Which copy of the game gets started' $launch
Add-Section 'Game folders' $folders
Add-Section 'Shared settings' $shared
Add-Section 'Mod Organizer log' $moLog
Add-Section 'Other log folders' $otherLogs

$text = Hide-UserFolder ($out -join [Environment]::NewLine)
$resultPath = Join-Path $build 'test-results.txt'
Set-Content -LiteralPath $resultPath -Value $text -Encoding utf8
Write-Host $text
Write-Host ''
Write-Host "Written to: $resultPath"
$copied = $false
if (-not $NoClipboard -and (Get-Command Set-Clipboard -ErrorAction SilentlyContinue)) {
    try { Set-Clipboard -Value $text; $copied = $true } catch { }
}
if ($copied) { Write-Host 'It is also on your clipboard. Click in the chat and press Ctrl+V to send it.' }
