<#
.SYNOPSIS
  Runs self-test scenarios in the game one after another, with nobody at the
  keyboard, and collects the results.

.DESCRIPTION
  Each scenario needs a fresh game session, because the quests run once. For
  every scenario in the list this script:

    1. writes the scenario number into the installed copy of the plugin (the
       value of one global variable, TLM_G_DevScenario: four bytes);
    2. starts the base game through Mod Organizer in the test profile, as
       Start-TestGame.ps1 does;
    3. lets the game enter the test room by itself: the test profile's
       fallout4custom.ini is given  [General] sStartingConsoleCommand=coc qasmoke
       for the duration of the run, and  bAlwaysActive=1  so the game keeps
       running when its window is not in front;
    4. waits. In the game TLM:Core sees the scenario number, runs that
       scenario of the self-test a few seconds after the room has loaded, and
       closes the game (Debug.QuitGame);
    5. reads the self-test's log and the game's script log for that session.

  At the end the scenario number is put back to 0 and the start-up console
  command is emptied, so the installed plugin is again identical to the build
  and a manual session behaves as before.

  WHAT IT CHANGES, all of it this project's own: the installed plugin in the
  Mod Organizer mod folder (four bytes, restored); the test profile's
  fallout4custom.ini (two settings, put back afterwards); which profile Mod
  Organizer has selected.

  IT CLOSES THE GAME IT STARTED if a scenario has not finished in time: first
  by asking the game's window to close, then, if that does nothing, by ending
  the process. It only runs if no game and no Mod Organizer was open when it
  began, so the game it closes is the one it started. No save is involved: the
  sessions are entered with coc and nothing is saved by hand.

  If the first scenario never starts by itself, the automatic entry does not
  work on this PC; the script stops there and says how to run the scenarios
  by hand instead.

  The scenarios (scripts/Source/User/TLM/SelfTest.psc):
    1  both quests by stage numbers alone, every alias empty
    2  actors made at run time, put into the main quest's aliases and killed
    3  distance events, and the main quest's "the player has left" watch
    4  the main quest played through with a caravan made at run time: evaded
    5  the same: a fight, the Cutter lead killed, the caravan saved
    6  the same: the ambush never met, resolved when the player reaches town
    7  the same: the caravan master killed by the player at the ambush
    8  the same: the caravan saved, then the caravan master killed
    9  the same: the Cutter lead's deal taken
    101 and up   the rows of the two test matrices, generated from the logic
                 model. tools\matrix_cases.json lists them: which rows each
                 stands for and the events it plays.

  -Scenarios takes numbers, ranges and names, separated by commas:
    all      1 to 9 and every matrix case (the default; about half an hour)
    basic    1 to 9
    matrix   every matrix case
    main     the matrix cases of the main quest (101 to 199)
    side     the matrix cases of the side quest (201 to 299)
    4,104-110,side   and so on

  A scenario that stops inside a call which never comes back is ended by a
  watchdog in the self-test itself, which writes where it stopped; the time
  limit here is the second line of defence.

  Status: ran on the owner's PC under Windows PowerShell 5.1 on 2026-11-12,
  three times. The chain works there: the game enters the room, starts the
  scenario and closes by itself, 36 seconds per scenario on average; 58
  scenarios in a row passed in 35 minutes. In the first run a scenario that
  never finished was closed by this script after the time limit.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\win\Run-Scenarios.ps1
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\win\Run-Scenarios.ps1 -Scenarios 2
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\win\Run-Scenarios.ps1 -Scenarios basic
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\win\Run-Scenarios.ps1 -Scenarios 119-121,side
#>
[CmdletBinding()]
param(
    # Numbers, ranges (101-128) and names (all, basic, matrix, main, side),
    # separated by commas; see the description.
    [string]$Scenarios = 'all',
    # Defaults come from build\install-manifest.json (written by Install-Dev.ps1).
    [string]$ModOrganizerRoot,
    [string]$ProfileName,
    # How long to wait for Fallout4.exe to appear after starting Mod Organizer.
    [int]$StartTimeoutSeconds = 180,
    # How long one scenario may take, from the game appearing to the game closing.
    [int]$ScenarioTimeoutSeconds = 240,
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
New-Item -ItemType Directory -Force -Path $build | Out-Null
$modName = 'TheLastMeridian-Dev'
$pluginName = 'TheLastMeridian.esp'
$globalName = 'TLM_G_DevScenario'
$enterCommand = 'coc qasmoke'

# The matrix cases, generated from the logic model: number -> what it is.
$caseTitles = @{}
$matrixNumbers = @()
$matrixFile = Join-Path (Join-Path $repo 'tools') 'matrix_cases.json'
if (Test-Path -LiteralPath $matrixFile) {
    foreach ($c in @((Get-Content -LiteralPath $matrixFile -Raw | ConvertFrom-Json).cases)) {
        $matrixNumbers += [int]$c.scenario
        $caseTitles[[int]$c.scenario] = "$(@($c.rows) -join ', '): $($c.title)"
    }
}
$basicNumbers = @(1..9)
$basicTitles = @{
    1 = 'both quests by stages alone'; 2 = 'actors made at run time, in the aliases, killed'
    3 = 'distance events and the quest''s "the player has left" watch'; 4 = 'evaded'; 5 = 'saved after a fight'
    6 = 'missed'; 7 = 'betrayal on the road'; 8 = 'murder after saving'; 9 = 'the deal'
}
foreach ($k in $basicTitles.Keys) { $caseTitles[[int]$k] = $basicTitles[$k] }

$list = New-Object System.Collections.Generic.List[int]
foreach ($word in @($Scenarios -split '[,; ]+' | Where-Object { $_ -ne '' })) {
    $add = @()
    switch -Regex ($word.ToLowerInvariant()) {
        '^all$'    { $add = $basicNumbers + $matrixNumbers; break }
        '^basic$'  { $add = $basicNumbers; break }
        '^matrix$' { $add = $matrixNumbers; break }
        '^main$'   { $add = @($matrixNumbers | Where-Object { $_ -ge 100 -and $_ -lt 200 }); break }
        '^side$'   { $add = @($matrixNumbers | Where-Object { $_ -ge 200 -and $_ -lt 300 }); break }
        '^(\d+)-(\d+)$' { $add = @([int]$Matches[1]..[int]$Matches[2]); break }
        '^\d+$'    { $add = @([int]$word); break }
        default    { throw "Not a scenario number, a range or a set name: $word" }
    }
    foreach ($n in $add) { if (-not $list.Contains([int]$n)) { $list.Add([int]$n) } }
}
if ($list.Count -eq 0) { throw 'No scenarios to run. (A set name gives nothing if tools\matrix_cases.json is missing.)' }
foreach ($n in $list) { if ($n -lt 1 -or $n -gt 999) { throw "Not a scenario number: $n" } }

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
if (-not $DocumentsRoot) { $DocumentsRoot = [Environment]::GetFolderPath('MyDocuments') }
$scriptLogs = Join-Path (Join-Path (Join-Path (Join-Path $DocumentsRoot 'My Games') 'Fallout4') 'Logs') 'Script'
$userLog = Join-Path (Join-Path $scriptLogs 'User') 'TLM.0.log'
$papyrusLog = Join-Path $scriptLogs 'Papyrus.0.log'

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
# Fails here, before anything is started, if the installed plugin predates the scenario number.
$valueAtStart = Get-PluginGlobal -Path $installedPlugin -EditorId $globalName
$customIni = Join-Path $profileFolder 'fallout4custom.ini'
$alwaysActiveBefore = Get-IniValue $customIni 'General' 'bAlwaysActive'

if (-not (Wait-GameAndManagerClosed)) { throw 'Mod Organizer or Fallout 4 is still open. Close them, then run this again.' }

# ------------------------------------------------------------- helpers
$ev = New-Object System.Collections.Generic.List[string]
foreach ($l in $Preface) { $ev.Add($l) }
function Say([string]$s = '') { $ev.Add($s); Write-Host $s }

function Close-StartedGame {
    # Asks the game's window to close; ends the process only if that does nothing.
    $how = 'asked its window to close'
    foreach ($p in @(Get-RunningGame)) { try { [void]$p.CloseMainWindow() } catch { } }
    $deadline = (Get-Date).AddSeconds(20)
    while (@(Get-RunningGame).Count -and (Get-Date) -lt $deadline) { Start-Sleep -Seconds 1 }
    if (@(Get-RunningGame).Count) {
        $how = 'ended its process'
        foreach ($p in @(Get-RunningGame)) { try { Stop-Process -Id $p.Id -Force } catch { } }
        $deadline = (Get-Date).AddSeconds(15)
        while (@(Get-RunningGame).Count -and (Get-Date) -lt $deadline) { Start-Sleep -Seconds 1 }
    }
    return $how
}

function Read-ScenarioLogs([datetime]$since) {
    # What the game wrote for the session that began at $since.
    $r = [ordered]@{
        HasUserLog = $false; Header = $null; ResultLine = $null; Passed = 0; FailLines = @(); InfoLines = @(); Aborted = $false
        LastStep = $null; LastLine = $null
        HasScriptLog = $false; CoreStarted = $false; Problems = @(); MqEvents = 0; SqEvents = 0; ScriptLogLines = 0
    }
    if ((Test-Path -LiteralPath $userLog) -and ((Get-Item -LiteralPath $userLog).LastWriteTime -ge $since)) {
        $lines = @(Get-Content -LiteralPath $userLog)
        $r.HasUserLog = $true
        $r.Header = @($lines | Where-Object { $_ -match '==== The Last Meridian self-test: scenario' }) | Select-Object -Last 1
        $r.ResultLine = @($lines | Where-Object { $_ -match '==== RESULT:' }) | Select-Object -Last 1
        $r.Passed = @($lines | Where-Object { $_ -match '\]\s*PASS\s' }).Count
        $r.FailLines = @($lines | Where-Object { $_ -match '\]\s*FAIL\s' })
        $r.InfoLines = @($lines | Where-Object { $_ -match '\]\s*INFO\s' })
        $r.Aborted = [bool](@($lines | Where-Object { $_ -match 'ABORTED' }).Count)
        # Where a scenario that did not finish had got to.
        $r.LastStep = @($lines | Where-Object { $_ -match '\]\s*STEP\s' }) | Select-Object -Last 1
        $r.LastLine = @($lines | Where-Object { "$_".Trim() -ne '' }) | Select-Object -Last 1
    }
    if ((Test-Path -LiteralPath $papyrusLog) -and ((Get-Item -LiteralPath $papyrusLog).LastWriteTime -ge $since)) {
        $lines = @(Get-Content -LiteralPath $papyrusLog)
        $r.HasScriptLog = $true
        $r.ScriptLogLines = $lines.Count
        $r.CoreStarted = [bool](@($lines | Where-Object { $_ -match 'TLM_Core: started' }).Count)
        $r.Problems = @($lines | Where-Object { $_ -match 'TLM' -and $_ -notmatch 'TLM_SelfTest:' -and $_ -match '(?i)\b(error|warning):' })
        $r.MqEvents = @($lines | Where-Object { $_ -match 'TLM_MQ01: stage \d+ item' }).Count
        $r.SqEvents = @($lines | Where-Object { $_ -match 'TLM_SQ01: stage \d+ item' }).Count
    }
    return [pscustomobject]$r
}

# ------------------------------------------------------------- the run
$results = New-Object System.Collections.Generic.List[object]
$stoppedEarly = $null
$restoreNotes = New-Object System.Collections.Generic.List[string]
$runStarted = Get-Date
try {
    Say '== Unattended scenario run =='
    Say "Scenarios            : $($list.Count) ($Scenarios)"
    Write-Host "This takes about $([math]::Max(1, [int][math]::Round($list.Count * 36 / 60))) minutes: $($list.Count) game sessions of roughly half a minute each."
    Say "Game to start        : $gameExe  (Fallout4.exe $(Get-ExeVersion $gameExe))"
    Say "Through              : $moExe   profile $ProfileName"
    Say "Scenario number in the installed plugin before the run: $valueAtStart"
    Say "Start-up command for the run: [General] sStartingConsoleCommand=$enterCommand  (in $customIni)"
    Set-IniValue $customIni 'General' 'sStartingConsoleCommand' $enterCommand
    # The game stops the clock when its window is not in front. Nobody is
    # watching this run, so it must keep going whatever else has the focus.
    Say "Keep running without focus for the run: [General] bAlwaysActive=1  (was: $(if ($null -eq $alwaysActiveBefore) { 'not set' } else { $alwaysActiveBefore }))"
    Set-IniValue $customIni 'General' 'bAlwaysActive' '1'

    $first = $true
    foreach ($n in $list) {
        Write-Host ''
        Write-Host "---- scenario $n ----"
        [void](Set-PluginGlobal -Path $installedPlugin -EditorId $globalName -Value $n)
        $since = Get-Date
        $argLine = '-p "{0}" run "{1}"' -f $ProfileName, $gameExe
        $moProc = Start-Process -FilePath $moExe -ArgumentList $argLine -WorkingDirectory $mo.Root -PassThru
        try { $null = $moProc.Handle } catch { }

        # wait for the game to appear
        $game = $null
        $deadline = $since.AddSeconds($StartTimeoutSeconds)
        while ((Get-Date) -lt $deadline) {
            $running = @(Get-RunningGame)
            if ($running.Count) { $game = $running[0]; break }
            if ($moProc.HasExited -and -not (Test-ModOrganizerRunning)) { break }
            Start-Sleep -Milliseconds 500
        }
        if (-not $game) {
            $results.Add([pscustomobject]@{ Scenario = $n; Status = 'NOT STARTED'; Seconds = [int]((Get-Date) - $since).TotalSeconds; Logs = $null; Note = 'the game did not appear after Mod Organizer was started' })
            $stoppedEarly = "Scenario ${n}: the game did not start. Nothing further was run."
            break
        }

        if ($first) {
            Start-Sleep -Seconds 4
            $facts = Get-ProcessFacts $game
            $startedFrom = $facts.Path
            if (-not $startedFrom -and (Get-Command Get-CimInstance -ErrorAction SilentlyContinue)) {
                try { $startedFrom = (Get-CimInstance Win32_Process -Filter "ProcessId = $($game.Id)" -ErrorAction Stop).ExecutablePath } catch { }
            }
            $usvfs = @($facts.Modules | Where-Object { $_ -match '(?i)^usvfs' })
            Say "Game process         : started from $(if ($startedFrom) { $startedFrom } else { '(could not be read)' })"
            Say "Mod Organizer's file system inside the game : $(if ($usvfs.Count) { 'yes' } elseif ($facts.Modules.Count) { 'NOT DETECTED' } else { 'unknown' })"
            if ($startedFrom -and -not (Test-SamePath $startedFrom $gameExe)) {
                Say 'This is NOT the managed base game. Close it. Nothing further was run.'
                while (@(Get-RunningGame).Count) { Start-Sleep -Seconds 2 }
                $results.Add([pscustomobject]@{ Scenario = $n; Status = 'WRONG GAME'; Seconds = [int]((Get-Date) - $since).TotalSeconds; Logs = $null; Note = "started from $startedFrom" })
                $stoppedEarly = 'The wrong copy of the game started.'
                break
            }
            Write-Host 'Do not touch the keyboard or mouse in the game: it enters the test room, runs the scenario and closes by itself.'
        }

        # wait for the game to close itself
        $deadline = (Get-Date).AddSeconds($ScenarioTimeoutSeconds)
        $lastNote = Get-Date
        while (@(Get-RunningGame).Count -and (Get-Date) -lt $deadline) {
            if (((Get-Date) - $lastNote).TotalSeconds -ge 30) { Write-Host "  ... scenario $n running for $([int]((Get-Date) - $since).TotalSeconds) seconds"; $lastNote = Get-Date }
            Start-Sleep -Seconds 1
        }
        $closedBy = 'the game closed itself'
        $timedOut = $false
        if (@(Get-RunningGame).Count) {
            $timedOut = $true
            $closedBy = "not finished after $ScenarioTimeoutSeconds seconds; this script $(Close-StartedGame)"
        }
        $moDeadline = (Get-Date).AddSeconds(60)
        while ((Test-ModOrganizerRunning) -and (Get-Date) -lt $moDeadline) { Start-Sleep -Seconds 1 }

        $logs = Read-ScenarioLogs $since
        $seconds = [int]((Get-Date) - $since).TotalSeconds
        $status = 'NO RESULT'
        $note = $closedBy
        if ($logs.ResultLine) {
            $status = if ($logs.FailLines.Count -eq 0) { 'PASSED' } else { 'FAILED' }
        } elseif ($logs.Aborted) {
            $status = 'REFUSED'
            $note = "the self-test refused to run (the quests were already started); $closedBy"
        } elseif ($logs.HasUserLog) {
            $status = 'UNFINISHED'
            $note = "the scenario started but wrote no RESULT line; $closedBy"
        } elseif ($logs.CoreStarted) {
            $note = "the game entered a session and the core quest started, but the scenario did not start; $closedBy"
        } elseif ($logs.HasScriptLog) {
            $note = "the game ran, but the core quest never started: the game did not enter the test room by itself; $closedBy"
        } else {
            $note = "the game wrote no script log for this session; $closedBy"
        }
        $results.Add([pscustomobject]@{ Scenario = $n; Status = $status; Seconds = $seconds; Logs = $logs; Note = $note })
        Write-Host "  scenario ${n}: $status  ($($logs.Passed) passed, $($logs.FailLines.Count) failed, $seconds seconds; $note)"

        if ($first -and -not $logs.HasUserLog) {
            # The chain (enter by itself, start by itself) does not work: no point in repeating it.
            $stoppedEarly = "Scenario ${n} did not start by itself, so the remaining scenarios were not run."
            break
        }
        $first = $false
    }
} catch {
    Say ''
    Say "UNEXPECTED ERROR in Run-Scenarios.ps1: $($_.Exception.Message)"
    foreach ($line in ("$($_.ScriptStackTrace)" -split "`r?`n")) { Say "    $line" }
} finally {
    # Put back what the run changed, whatever happened.
    try {
        [void](Set-PluginGlobal -Path $installedPlugin -EditorId $globalName -Value $valueAtStart)
        $restoreNotes.Add("Scenario number in the installed plugin: back to $(Get-PluginGlobal -Path $installedPlugin -EditorId $globalName)")
    } catch { $restoreNotes.Add("COULD NOT restore the scenario number in the installed plugin: $($_.Exception.Message). Run the install again to replace it.") }
    try {
        Set-IniValue $customIni 'General' 'sStartingConsoleCommand' ''
        $restoreNotes.Add("Start-up console command in the test profile: emptied (now '$(Get-IniValue $customIni 'General' 'sStartingConsoleCommand')')")
    } catch { $restoreNotes.Add("COULD NOT empty the start-up console command in ${customIni}: $($_.Exception.Message)") }
    try {
        # 0 is the game's own default, so "not set before" and 0 mean the same.
        $back = if ($null -eq $alwaysActiveBefore -or $alwaysActiveBefore -eq '') { '0' } else { $alwaysActiveBefore }
        Set-IniValue $customIni 'General' 'bAlwaysActive' $back
        $restoreNotes.Add("Keep-running-without-focus setting in the test profile: back to $(Get-IniValue $customIni 'General' 'bAlwaysActive')")
    } catch { $restoreNotes.Add("COULD NOT restore bAlwaysActive in ${customIni}: $($_.Exception.Message)") }
    $builtPlugin = Join-Path $build $pluginName
    if (Test-Path -LiteralPath $builtPlugin) {
        $same = (Get-FileHash -LiteralPath $builtPlugin).Hash -eq (Get-FileHash -LiteralPath $installedPlugin).Hash
        $restoreNotes.Add("Installed plugin identical to the build again: $(if ($same) { 'yes' } else { 'NO' })")
    }
}

# ------------------------------------------------------------- report
$out = New-Object System.Collections.Generic.List[string]
$out.Add("The Last Meridian: unattended scenario run   $(Get-Date -Format 'yyyy-MM-dd HH:mm')")
try {
    $head = Invoke-Native -Exe 'git' -Arguments @('-C', $repo, 'log', '--oneline', '-1')
    if ($head.Found -and $head.ExitCode -eq 0) { $out.Add("Repository commit: $($head.Output | Select-Object -First 1)") }
} catch { }
$out.Add("Run began: $($runStarted.ToString('yyyy-MM-dd HH:mm:ss')); took $([int]((Get-Date) - $runStarted).TotalSeconds) seconds")
$out.Add('')
foreach ($l in $ev) { $out.Add($l) }

$out.Add('')
$out.Add('== Scenarios ==')
$totalPassed = 0; $totalFailed = 0
foreach ($r in $results) { if ($r.Logs) { $totalPassed += $r.Logs.Passed; $totalFailed += $r.Logs.FailLines.Count } }
$okCount = @($results | Where-Object { $_.Status -eq 'PASSED' }).Count
$out.Add("  $($results.Count) of $($list.Count) run: $okCount passed, $($results.Count - $okCount) did not. Checks: $totalPassed passed, $totalFailed failed.")
$out.Add(('  {0,3}  {1,-11} {2,6} {3,6} {4,7}  {5}' -f '#', 'result', 'passed', 'failed', 'seconds', 'what it is'))
foreach ($r in $results) {
    $p = if ($r.Logs) { $r.Logs.Passed } else { 0 }
    $f = if ($r.Logs) { $r.Logs.FailLines.Count } else { 0 }
    $what = if ($caseTitles.ContainsKey([int]$r.Scenario)) { $caseTitles[[int]$r.Scenario] } else { '' }
    if ($r.Note -ne 'the game closed itself') { $what = "$what  [$($r.Note)]" }
    $out.Add(('  {0,3}  {1,-11} {2,6} {3,6} {4,7}  {5}' -f $r.Scenario, $r.Status, $p, $f, $r.Seconds, $what))
}
$notRun = @($list | Where-Object { $n = $_; -not @($results | Where-Object { $_.Scenario -eq $n }).Count })
if ($notRun.Count) { $out.Add("  not run: $($notRun -join ', ')") }
if ($stoppedEarly) {
    $out.Add('')
    $out.Add("STOPPED EARLY: $stoppedEarly")
    $out.Add('To run a scenario by hand instead: powershell -ExecutionPolicy Bypass -File tools\win\Start-TestGame.ps1')
    $out.Add('and in the game:  coc qasmoke   then   cqf TLM_Core RunSelfTest <number>   (one fresh session per scenario).')
}

foreach ($r in $results) {
    if (-not $r.Logs) { continue }
    # A matrix case that passed with a clean script log has nothing more to say than its row in the table.
    if ([int]$r.Scenario -ge 100 -and $r.Status -eq 'PASSED' -and -not $r.Logs.Problems.Count) { continue }
    $out.Add('')
    $out.Add("== Scenario $($r.Scenario): $($r.Status) ==")
    if ($r.Logs.Header) { $out.Add("  $($r.Logs.Header)") }
    $out.Add("  script log: $(if ($r.Logs.HasScriptLog) { "$($r.Logs.ScriptLogLines) lines" } else { 'none for this session' }); core quest started: $($r.Logs.CoreStarted); stage events: $($r.Logs.MqEvents) main quest, $($r.Logs.SqEvents) side quest")
    foreach ($l in $r.Logs.FailLines) { $out.Add("  $l") }
    foreach ($l in $r.Logs.InfoLines) { $out.Add("  $l") }
    if ($r.Logs.ResultLine) { $out.Add("  $($r.Logs.ResultLine)") }
    if ($r.Status -ne 'PASSED' -and $r.Logs.HasUserLog) {
        $out.Add("  last step named in the self-test's log: $(if ($r.Logs.LastStep) { $r.Logs.LastStep } else { '(none)' })")
        if (-not $r.Logs.ResultLine -and $r.Logs.LastLine) { $out.Add("  last line of the self-test's log      : $($r.Logs.LastLine)") }
    }
    if ($r.Logs.Problems.Count) {
        $out.Add("  errors and warnings in the game's script log that name this project ($($r.Logs.Problems.Count)$(if ($r.Logs.Problems.Count -gt 25) { ', first 25 shown' })):")
        foreach ($l in ($r.Logs.Problems | Select-Object -First 25)) { $out.Add("    $l") }
    } else {
        $out.Add("  errors and warnings in the game's script log that name this project: none")
    }
}

$out.Add('')
$out.Add('== Put back after the run ==')
foreach ($l in $restoreNotes) { $out.Add("  $l") }
$out.Add("  Mod Organizer now has profile '$ProfileName' selected. Switch back to your own profile before you play.")
$out.Add('')
$out.Add('A pass means the scripted rules behaved as predicted in the game for that scenario. It is not a test of the')
$out.Add('quest as a player would meet it.')

$text = Hide-UserFolder ($out -join [Environment]::NewLine)
$resultPath = Join-Path $build 'scenario-results.txt'
Set-Content -LiteralPath $resultPath -Value $text -Encoding utf8
Write-Host ''
Write-Host $text
Write-Host ''
Write-Host "Written to: $resultPath"
$copied = $false
if (-not $NoClipboard -and (Get-Command Set-Clipboard -ErrorAction SilentlyContinue)) {
    try { Set-Clipboard -Value $text; $copied = $true } catch { }
}
if ($copied) { Write-Host 'It is also on your clipboard. Click in the chat and press Ctrl+V to send it.' }

$bad = @($results | Where-Object { $_.Status -ne 'PASSED' }).Count
if ($bad -or $stoppedEarly -or $results.Count -lt $list.Count) { exit 1 }
