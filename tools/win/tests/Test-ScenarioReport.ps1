<#
.SYNOPSIS
  Tests how Run-Scenarios.ps1 reads a game session's logs, names its outcome
  and adds a run up. No game, no Mod Organizer, nothing installed.

.DESCRIPTION
  Run-Scenarios.ps1 takes three things from Tlm.psm1: the reading of the two
  logs a game session writes (Read-ScenarioSessionLogs), the one word for a
  session (Get-ScenarioSessionStatus) and the totals and table of a run
  (Get-ScenarioRunSummary). This script writes stand-in logs, shaped like the
  ones the game wrote on 2026-11-14, into a folder of its own under the
  system's temporary folder, puts them through those same functions, and
  compares what comes out. It removes the folder afterwards.

  What it is for: on 2026-11-14 a session in which the first section of Act I
  was only set up for a person (number 900) was reported as PLAYED and counted
  into "1 of 1 run: 1 passed", with no checks at all. A play session is now
  SET UP or NOT SET UP, is counted apart from the scored scenarios, and is
  never a pass. The cases here: a set-up alone; a scored scenario and a
  set-up in one run; a set-up that did not happen; a scored scenario that
  failed, did not finish or was refused; a run that stopped early.

  It reads and writes nothing outside its own temporary folder. It starts no
  program. It works under Windows PowerShell 5.1 and PowerShell 7.

  Status: passes on Linux PowerShell 7.4. NOT YET RUN under Windows
  PowerShell 5.1, which is what the PC uses; it can be, without the game.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\win\tests\Test-ScenarioReport.ps1
.EXAMPLE
  pwsh -NoProfile -File tools/win/tests/Test-ScenarioReport.ps1
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$winDir = Split-Path -Parent $PSScriptRoot
Import-Module (Join-Path $winDir 'Tlm.psm1') -Force

$script:Checks = 0
$script:Failures = New-Object System.Collections.Generic.List[string]
function Check([string]$What, [bool]$Holds, [string]$Detail = '') {
    $script:Checks++
    if (-not $Holds) {
        $script:Failures.Add($(if ($Detail) { "$What  ($Detail)" } else { $What }))
        Write-Host "  FAILED  $What$(if ($Detail) { "  ($Detail)" })"
    }
}
function Check-Equal([string]$What, $Expected, $Actual) {
    Check $What ("$Expected" -eq "$Actual") "expected '$Expected', was '$Actual'"
}

$PlayNumber = 900
$Titles = @{ 2 = 'actors made at run time, in the aliases, killed'; 11 = 'people placed by the plugin'; 12 = 'Act I, first section: checked'; 900 = 'Act I, first section, set up for a person to play (nothing is scored)' }
$stamp = '[11/14/2026 - 11:44:19AM]'

$root = Join-Path ([System.IO.Path]::GetTempPath()) ("tlm-scenario-report-" + [guid]::NewGuid().ToString('N'))
[void](New-Item -ItemType Directory -Path $root)

function New-Session {
    # One game session's logs, in a folder of its own. Returns what the runner would hold for it.
    param(
        [int]$Scenario,
        [string[]]$ScriptLog,        # lines of Papyrus.0.log; $null: the game wrote none
        [string[]]$SelfTestLog,      # lines of User\TLM.0.log; $null: none
        [string]$ClosedBy = 'the game closed itself',
        [int]$Seconds = 40
    )
    $dir = Join-Path $root ("session-" + [guid]::NewGuid().ToString('N'))
    [void](New-Item -ItemType Directory -Path (Join-Path $dir 'User'))
    $userLog = Join-Path (Join-Path $dir 'User') 'TLM.0.log'
    $papyrusLog = Join-Path $dir 'Papyrus.0.log'
    $since = (Get-Date).AddSeconds(-5)
    if ($null -ne $ScriptLog) { Set-Content -LiteralPath $papyrusLog -Value $ScriptLog -Encoding utf8 }
    if ($null -ne $SelfTestLog) { Set-Content -LiteralPath $userLog -Value $SelfTestLog -Encoding utf8 }
    $logs = Read-ScenarioSessionLogs -UserLog $userLog -PapyrusLog $papyrusLog -Since $since
    $verdict = Get-ScenarioSessionStatus -Logs $logs -Playing ($Scenario -eq $PlayNumber) -ClosedBy $ClosedBy
    return [pscustomobject]@{ Scenario = $Scenario; Status = $verdict.Status; Seconds = $Seconds; Logs = $logs; Note = $verdict.Note }
}

function Lines-PassedScenario([int]$n, [int]$passes) {
    $l = @("$stamp TLM log opened (PC-64)", "$stamp ==== The Last Meridian self-test: scenario $n ====", "$stamp STEP  the first step")
    for ($i = 1; $i -le $passes; $i++) { $l += "$stamp PASS  check $i" }
    $l += "$stamp INFO  stage handlers already finished when SetStage returned: 5 of 5"
    $l += "$stamp ==== RESULT: $passes passed, 0 failed ===="
    return $l
}
$coreStarted = @("$stamp Papyrus log opened (PC-64)", "$stamp TLM_Core: started, data version 1")
$setUpLog = $coreStarted + @(
    "$stamp TLM_A1: setting up the first section",
    "$stamp TLM_MQ01: stage 10 item 0", "$stamp TLM_SQ01: stage 5 item 0",
    "$stamp TLM_A1: the first section is set up; aliases left empty: 0, people not there: 0")
$scoredLog = $coreStarted + @("$stamp TLM_MQ01: stage 10 item 0", "$stamp TLM_MQ01: stage 20 item 0")

function Summarize($results, [int[]]$requested, [string]$stoppedEarly) {
    return (Get-ScenarioRunSummary -Results @($results) -Requested $requested -PlayNumber $PlayNumber -Titles $Titles -StoppedEarly $stoppedEarly)
}
function Text($summary) { return ($summary.Lines -join "`n") }

try {
    # ------------------------------------------------------------ 1. a set-up alone
    Write-Host '1. a play session alone: set up, nothing scored'
    $play = New-Session -Scenario 900 -ScriptLog $setUpLog -SelfTestLog $null -ClosedBy 'the game was closed' -Seconds 106
    Check-Equal 'a session whose script log says the section was set up is SET UP' 'SET UP' $play.Status
    Check 'the stages the game set are read from the script log' (($play.Logs.MqStages -join ',') -eq '10' -and ($play.Logs.SqStages -join ',') -eq '5')
    $s = Summarize @($play) @(900) $null
    Check-Equal 'no scored scenario was asked for' 0 $s.ScoredAsked
    Check-Equal 'no scored scenario passed' 0 $s.ScoredPassed
    Check-Equal 'no check passed' 0 $s.ChecksPassed
    Check-Equal 'no check failed' 0 $s.ChecksFailed
    Check-Equal 'one play session was started' 1 $s.PlayStarted
    Check-Equal 'one play session was set up' 1 $s.PlaySetUp
    Check-Equal 'a set-up with nothing else wrong ends the run in order' 0 $s.ExitCode
    Check 'the totals say that nothing was scored' ((Text $s) -match 'Scored scenarios: none were asked for\. Checks: 0 passed, 0 failed\. Nothing was scored in this run\.')
    Check 'the totals count the play session apart, and say a set-up is not a pass' ((Text $s) -match 'Play sessions, in which nothing is scored: 1 of 1 started: 1 set up, 0 not set up\. A set-up is not a pass\.')
    Check 'no line says that anything passed' (-not ((Text $s) -match '\b[1-9]\d* passed'))
    Check 'the word PLAYED is not used' (-not ((Text $s) -match 'PLAYED'))
    $row = @($s.Lines | Where-Object { $_ -match '^\s+900\s' })
    Check 'the play session has one row in the table' ($row.Count -eq 1)
    Check 'its row shows no numbers of checks' ($row[0] -match '^\s+900\s+SET UP\s+-\s+-\s+106\s')
    Check-Equal 'its part of the report is headed as a play session' '== Play session 900: SET UP (nothing is scored) ==' $s.Rows[0].SectionTitle

    # A self-test log written during a play session (somebody ran a scenario from the console) is not the session's score.
    $playWithLog = New-Session -Scenario 900 -ScriptLog $setUpLog -SelfTestLog (Lines-PassedScenario 1 60) -ClosedBy 'the game was closed'
    Check-Equal 'a play session stays SET UP whatever a self-test log of that session holds' 'SET UP' $playWithLog.Status
    $s = Summarize @($playWithLog) @(900) $null
    Check-Equal 'checks written during a play session are not counted' 0 $s.ChecksPassed
    Check 'and no line says that anything passed' (-not ((Text $s) -match '\b[1-9]\d* passed'))

    # ------------------------------------------------------------ 2. a scored scenario and a set-up in one run
    Write-Host '2. a scored scenario and a play session in one run'
    $twelve = New-Session -Scenario 12 -ScriptLog $scoredLog -SelfTestLog (Lines-PassedScenario 12 42) -Seconds 76
    Check-Equal 'a scenario with a RESULT line and no FAIL line is PASSED' 'PASSED' $twelve.Status
    Check-Equal 'its PASS lines are counted' 42 $twelve.Logs.Passed
    $s = Summarize @($twelve, $play) @(12, 900) $null
    Check 'the scored total holds the scored scenario only' ((Text $s) -match 'Scored scenarios: 1 of 1 run: 1 passed, 0 did not\. Checks: 42 passed, 0 failed\.')
    Check 'the play session is on its own line' ((Text $s) -match 'Play sessions, in which nothing is scored: 1 of 1 started: 1 set up, 0 not set up\.')
    Check-Equal 'one scored scenario passed, not two' 1 $s.ScoredPassed
    Check-Equal 'the checks are those of the scored scenario' 42 $s.ChecksPassed
    Check-Equal 'the run is in order' 0 $s.ExitCode
    Check 'the scored row shows its numbers' (@($s.Lines | Where-Object { $_ -match '^\s+12\s+PASSED\s+42\s+0\s+76\s' }).Count -eq 1)
    Check-Equal 'the scored part of the report is headed as a scenario' '== Scenario 12: PASSED ==' $s.Rows[0].SectionTitle
    # the same in the other order
    $s = Summarize @($play, $twelve) @(900, 12) $null
    Check 'the order of the sessions does not change the totals' ($s.ScoredPassed -eq 1 -and $s.ChecksPassed -eq 42 -and $s.PlaySetUp -eq 1 -and $s.ExitCode -eq 0)

    # ------------------------------------------------------------ 3. a set-up that did not happen
    Write-Host '3. a play session that was not set up'
    $noLine = New-Session -Scenario 900 -ScriptLog ($coreStarted + @("$stamp TLM_A1: setting up the first section")) -SelfTestLog $null -ClosedBy 'the game was closed'
    Check-Equal 'the core quest started but no line says the section was set up: NOT SET UP' 'NOT SET UP' $noLine.Status
    Check 'the note says which line is missing' ($noLine.Note -match 'no line saying the first section was set up')
    $noCore = New-Session -Scenario 900 -ScriptLog @("$stamp Papyrus log opened (PC-64)") -SelfTestLog $null -ClosedBy 'the game was closed'
    Check-Equal 'the core quest never started: NOT SET UP' 'NOT SET UP' $noCore.Status
    Check 'the note says the game did not enter the test room' ($noCore.Note -match 'did not enter the test room')
    $noLog = New-Session -Scenario 900 -ScriptLog $null -SelfTestLog $null -ClosedBy 'the game was closed'
    Check-Equal 'no script log at all: NOT SET UP' 'NOT SET UP' $noLog.Status
    foreach ($bad in @($noLine, $noCore, $noLog)) {
        $s = Summarize @($bad) @(900) $null
        Check 'a play session that was not set up is counted as that' ($s.PlaySetUp -eq 0 -and $s.PlayNotSetUp -eq 1)
        Check-Equal 'and the run is not in order' 1 $s.ExitCode
        Check 'and the totals say so' ((Text $s) -match '1 of 1 started: 0 set up, 1 not set up')
        Check 'and its row gives the reason' (@($s.Lines | Where-Object { $_ -match '^\s+900\s+NOT SET UP\s+-\s+-\s' -and $_ -match '\[.+\]' }).Count -eq 1)
    }
    $s = Summarize @($twelve, $noLine) @(12, 900) $null
    Check 'a scored pass stays a pass beside a set-up that failed' ($s.ScoredPassed -eq 1 -and $s.ChecksPassed -eq 42)
    Check-Equal 'but the run is not in order' 1 $s.ExitCode

    # ------------------------------------------------------------ 4. scored scenarios that did not pass
    Write-Host '4. scored scenarios that did not pass'
    $failLog = @("$stamp ==== The Last Meridian self-test: scenario 2 ====", "$stamp STEP  the probe")
    for ($i = 1; $i -le 9; $i++) { $failLog += "$stamp PASS  probe: check $i" }
    $failLog += "$stamp FAIL  probe: a timer on a quest script fires: expected true, was false"
    $failLog += "$stamp ==== RESULT: 9 passed, 1 failed ===="
    $failed = New-Session -Scenario 2 -ScriptLog $scoredLog -SelfTestLog $failLog
    Check-Equal 'a RESULT line with a FAIL line is FAILED' 'FAILED' $failed.Status
    $s = Summarize @($failed) @(2) $null
    Check 'the totals count the failure' ((Text $s) -match 'Scored scenarios: 1 of 1 run: 0 passed, 1 did not\. Checks: 9 passed, 1 failed\.')
    Check-Equal 'the run is not in order' 1 $s.ExitCode
    Check 'no play line is printed when no play session was asked for' (-not ((Text $s) -match 'Play sessions'))
    $s = Summarize @($failed, $play) @(2, 900) $null
    Check 'a set-up beside a failed scenario does not make it pass' ($s.ScoredPassed -eq 0 -and $s.ScoredNotPassed -eq 1 -and $s.PlaySetUp -eq 1 -and $s.ExitCode -eq 1)

    $unfinished = New-Session -Scenario 2 -ScriptLog $scoredLog -SelfTestLog @("$stamp ==== The Last Meridian self-test: scenario 2 ====", "$stamp STEP  moving the marker", "$stamp PASS  check 1") -ClosedBy 'not finished after 900 seconds; this script asked its window to close'
    Check-Equal 'a self-test log with no RESULT line is UNFINISHED' 'UNFINISHED' $unfinished.Status
    Check 'the note carries how the game was closed' ($unfinished.Note -match 'not finished after 900 seconds')
    $refused = New-Session -Scenario 2 -ScriptLog $scoredLog -SelfTestLog @("$stamp ABORTED: the quests were already started in this session")
    Check-Equal 'a self-test that refused to run is REFUSED' 'REFUSED' $refused.Status
    $nothing = New-Session -Scenario 2 -ScriptLog $coreStarted -SelfTestLog $null
    Check-Equal 'the core quest started and no scenario did: NO RESULT' 'NO RESULT' $nothing.Status
    $s = Summarize @($unfinished, $refused, $nothing, $twelve) @(2, 3, 4, 12) $null
    Check 'only the scenario that passed is counted as passed' ($s.ScoredPassed -eq 1 -and $s.ScoredNotPassed -eq 3 -and $s.ExitCode -eq 1)
    Check-Equal 'the checks of an unfinished scenario are still counted as what they are' 43 $s.ChecksPassed

    # A scored scenario is never SET UP, even if the script log holds the set-up line (scenario 12 sets the section up too).
    $twelveWithLine = New-Session -Scenario 12 -ScriptLog $setUpLog -SelfTestLog (Lines-PassedScenario 12 42)
    Check-Equal 'a scored scenario is PASSED, not SET UP' 'PASSED' $twelveWithLine.Status
    $twelveNoResult = New-Session -Scenario 12 -ScriptLog $setUpLog -SelfTestLog $null
    Check-Equal 'the set-up line does not stand in for a RESULT line' 'NO RESULT' $twelveNoResult.Status

    # ------------------------------------------------------------ 5. a run that stopped early
    Write-Host '5. a run that stopped early'
    $notStarted = [pscustomobject]@{ Scenario = 12; Status = 'NOT STARTED'; Seconds = 180; Logs = $null; Note = 'the game did not appear' }
    $s = Summarize @($notStarted) @(12, 11, 900) 'Scenario 12: the game did not start. Nothing further was run.'
    Check 'the scored total counts what was started and what was asked for' ((Text $s) -match 'Scored scenarios: 1 of 2 run: 0 passed, 1 did not\. Checks: 0 passed, 0 failed\.')
    Check 'the play session that was never started is counted as not started' ((Text $s) -match 'Play sessions, in which nothing is scored: 0 of 1 started: 0 set up, 0 not set up\.')
    Check 'what was not run is listed' ((Text $s) -match '(?m)^\s+not run: 11, 900$')
    Check-Equal 'the run is not in order' 1 $s.ExitCode
    $s = Summarize @($twelve) @(12, 900) $null
    Check 'a run that ended before the play session is not in order, though all that ran passed' ($s.ScoredPassed -eq 1 -and $s.PlayStarted -eq 0 -and $s.ExitCode -eq 1 -and ((Text $s) -match 'not run: 900'))
    $s = Summarize @($twelve, $play) @(12, 900) 'something stopped the run'
    Check-Equal 'a run marked as stopped early is not in order whatever its sessions say' 1 $s.ExitCode
    $wrongGame = [pscustomobject]@{ Scenario = 900; Status = 'WRONG GAME'; Seconds = 30; Logs = $null; Note = 'started from somewhere else' }
    $s = Summarize @($wrongGame) @(900) 'The wrong copy of the game started.'
    Check 'a play session in which the wrong game started is not a set-up' ($s.PlayStarted -eq 1 -and $s.PlaySetUp -eq 0 -and $s.PlayNotSetUp -eq 1 -and $s.ExitCode -eq 1)
    $s = Summarize @() @(900) 'nothing ran'
    Check 'a run in which nothing was started' ($s.PlayStarted -eq 0 -and $s.ScoredRun -eq 0 -and $s.ExitCode -eq 1 -and ((Text $s) -match 'not run: 900'))

    # ------------------------------------------------------------ 6. an ordinary run, as before
    Write-Host '6. scored scenarios only'
    $eleven = New-Session -Scenario 11 -ScriptLog $scoredLog -SelfTestLog (Lines-PassedScenario 11 8)
    $s = Summarize @($twelve, $eleven) @(12, 11) $null
    Check 'the totals of a run with no play session' ((Text $s) -match 'Scored scenarios: 2 of 2 run: 2 passed, 0 did not\. Checks: 50 passed, 0 failed\.')
    Check 'such a run has no play line' (-not ((Text $s) -match 'Play sessions'))
    Check-Equal 'and is in order' 0 $s.ExitCode

    # ------------------------------------------------------------ 7. logs of an earlier session
    Write-Host '7. logs left by an earlier session are not read'
    $dir = Join-Path $root 'earlier'
    [void](New-Item -ItemType Directory -Path (Join-Path $dir 'User'))
    $u = Join-Path (Join-Path $dir 'User') 'TLM.0.log'; $p = Join-Path $dir 'Papyrus.0.log'
    Set-Content -LiteralPath $u -Value (Lines-PassedScenario 12 42) -Encoding utf8
    Set-Content -LiteralPath $p -Value $setUpLog -Encoding utf8
    $logs = Read-ScenarioSessionLogs -UserLog $u -PapyrusLog $p -Since (Get-Date).AddMinutes(5)
    Check 'neither log is taken for this session' (-not $logs.HasUserLog -and -not $logs.HasScriptLog -and -not $logs.Act1SetUp -and $logs.Passed -eq 0)
    Check-Equal 'a play session with only old logs is NOT SET UP' 'NOT SET UP' (Get-ScenarioSessionStatus -Logs $logs -Playing $true -ClosedBy 'the game was closed').Status
    Check-Equal 'a scored scenario with only old logs has NO RESULT' 'NO RESULT' (Get-ScenarioSessionStatus -Logs $logs -Playing $false -ClosedBy 'the game closed itself').Status

    # ------------------------------------------------------------ 8. the runner uses these, and nothing of its own
    Write-Host '8. Run-Scenarios.ps1 takes its words and its totals from the module'
    $runner = Get-Content -LiteralPath (Join-Path $winDir 'Run-Scenarios.ps1') -Raw
    # Its description says what the word used to be; its code must not use it.
    $runner = $runner -replace '(?s)<#.*?#>', ''
    Check 'the runner''s code does not use the word PLAYED' (-not ($runner -cmatch 'PLAYED'))
    Check 'the runner reads a session''s logs through the module' ($runner -match 'Read-ScenarioSessionLogs -UserLog \$userLog -PapyrusLog \$papyrusLog -Since \$since')
    Check 'the runner names a session through the module' ($runner -match 'Get-ScenarioSessionStatus -Logs \$logs -Playing \$playing -ClosedBy \$closedBy')
    Check 'the runner adds the run up through the module' ($runner -match 'Get-ScenarioRunSummary -Results')
    Check 'the runner ends with the summary''s verdict' ($runner -match 'exit \$summary\.ExitCode')
    Check 'the runner counts no status as passed by itself' (-not ($runner -match "Status -eq 'PASSED' -or"))
} finally {
    try { Remove-Item -LiteralPath $root -Recurse -Force } catch { }
}

Write-Host ''
if ($script:Failures.Count) {
    Write-Host "Test-ScenarioReport: $($script:Failures.Count) of $($script:Checks) checks FAILED"
    exit 1
}
Write-Host "Test-ScenarioReport: $($script:Checks) checks passed (stand-in logs; not the game)"
exit 0
