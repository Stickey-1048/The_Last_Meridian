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

  Two more faults, found in review on 2026-11-14, are covered as well. A
  scenario that wrote its RESULT line and then never closed the game, so that
  the runner had to close it, was called PASSED: it is now TIMED OUT. And a
  run whose scenarios passed ended as a success even when what it had changed
  (the scenario number in the installed plugin, two settings of the test
  profile) could not be put back, or the installed plugin was not the build:
  it now ends as failed and keeps its note of how things were. The putting
  back (Restore-ScenarioRunState) is tried here on a stand-in plugin file and
  a stand-in settings file.

  It reads and writes nothing outside its own temporary folder. It starts no
  program. It works under Windows PowerShell 5.1 and PowerShell 7.

  Status: passes on Linux PowerShell 7.4. Under Windows PowerShell 5.1,
  which is what the PC uses, it passed there twice on 2026-11-14 (version
  5.1.26100.9818, in a checkout of its own, no game started): its first 81
  checks, and then 130 with the forced close after RESULT and the putting
  back. The ten checks added since (results being exactly what was asked
  for) HAVE NOT YET RUN under 5.1; they can, without the game.

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
        [int]$Seconds = 40,
        [bool]$TimedOut = $false
    )
    $dir = Join-Path $root ("session-" + [guid]::NewGuid().ToString('N'))
    [void](New-Item -ItemType Directory -Path (Join-Path $dir 'User'))
    $userLog = Join-Path (Join-Path $dir 'User') 'TLM.0.log'
    $papyrusLog = Join-Path $dir 'Papyrus.0.log'
    $since = (Get-Date).AddSeconds(-5)
    if ($null -ne $ScriptLog) { Set-Content -LiteralPath $papyrusLog -Value $ScriptLog -Encoding utf8 }
    if ($null -ne $SelfTestLog) { Set-Content -LiteralPath $userLog -Value $SelfTestLog -Encoding utf8 }
    $logs = Read-ScenarioSessionLogs -UserLog $userLog -PapyrusLog $papyrusLog -Since $since
    $verdict = Get-ScenarioSessionStatus -Logs $logs -Playing ($Scenario -eq $PlayNumber) -ClosedBy $ClosedBy -TimedOut $TimedOut
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

    # ------------------------------------------------------------ 5b. the results are exactly what was asked for
    Write-Host '5b. the right number of results does not stand in for the right results'
    $elevenB = New-Session -Scenario 11 -ScriptLog $scoredLog -SelfTestLog (Lines-PassedScenario 11 8)
    # two results for 12 and none for 11: as many results as were asked for, and all passed
    $s = Summarize @($twelve, $twelve) @(12, 11) $null
    Check 'a scenario with two results does not hide one that never ran' ($s.ExitCode -eq 1 -and ($s.NotRun -join ',') -eq '11' -and ($s.MoreThanOnce -join ',') -eq '12')
    Check 'the totals name both' ((Text $s) -match '(?m)^\s+not run: 11$' -and (Text $s) -match 'MORE THAN ONE RESULT for: 12')
    # a result for a scenario nobody asked for, in place of one that was
    $thirteen = [pscustomobject]@{ Scenario = 13; Status = 'PASSED'; Seconds = 30; Logs = $twelve.Logs; Note = 'the game closed itself' }
    $s = Summarize @($twelve, $thirteen) @(12, 11) $null
    Check 'a result nobody asked for does not hide one that never ran' ($s.ExitCode -eq 1 -and ($s.NotRun -join ',') -eq '11' -and ($s.NotAskedFor -join ',') -eq '13')
    Check 'the totals name it' ((Text $s) -match 'A RESULT NOBODY ASKED FOR: 13')
    # everything asked for is there and passed, and one is there twice
    $s = Summarize @($twelve, $elevenB, $elevenB) @(12, 11) $null
    Check 'a scenario with two results is not in order even when nothing is missing' ($s.ExitCode -eq 1 -and -not $s.NotRun.Count -and ($s.MoreThanOnce -join ',') -eq '11')
    # everything asked for is there and passed, and there is one more
    $s = Summarize @($twelve, $elevenB, $thirteen) @(12, 11) $null
    Check 'a result too many is not in order even when nothing is missing' ($s.ExitCode -eq 1 -and -not $s.NotRun.Count -and ($s.NotAskedFor -join ',') -eq '13')
    # the same for play sessions
    $s = Summarize @($play, $play) @(12, 900) $null
    Check 'two set-ups do not hide a scored scenario that never ran' ($s.ExitCode -eq 1 -and ($s.NotRun -join ',') -eq '12' -and ($s.MoreThanOnce -join ',') -eq '900')
    # a list that asks for a scenario twice
    $s = Summarize @($twelve, $elevenB) @(12, 11, 11) $null
    Check 'a scenario asked for twice is not in order' ($s.ExitCode -eq 1 -and ($s.AskedTwice -join ',') -eq '11')
    # and the plain case still is
    $s = Summarize @($twelve, $elevenB) @(12, 11) $null
    Check 'exactly what was asked for, each once and passed, is in order' ($s.ExitCode -eq 0 -and -not $s.NotRun.Count -and -not $s.MoreThanOnce.Count -and -not $s.NotAskedFor.Count -and -not $s.AskedTwice.Count)
    $s = Summarize @($elevenB, $twelve) @(12, 11) $null
    Check 'in whatever order they ran' ($s.ExitCode -eq 0)

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

    # ------------------------------------------------------------ 9. a RESULT line, and then the game never closed
    Write-Host '9. a scenario that wrote RESULT and then had to be closed by the runner'
    $closedByRunner = 'not finished after 900 seconds; this script ended its process'
    $passLog = Lines-PassedScenario 4 27
    $hung = New-Session -Scenario 4 -ScriptLog $scoredLog -SelfTestLog $passLog -ClosedBy $closedByRunner -Seconds 900 -TimedOut $true
    Check-Equal 'a passing RESULT line and a forced close is TIMED OUT, not PASSED' 'TIMED OUT' $hung.Status
    Check 'the note says the result was written and the game did not close' ($hung.Note -match 'wrote its RESULT line, but the game did not close by itself' -and $hung.Note -match 'ended its process')
    Check-Equal 'the checks it reported are kept' 27 $hung.Logs.Passed
    $s = Summarize @($hung) @(4) $null
    Check 'it is counted among those that did not pass, with its checks' ((Text $s) -match 'Scored scenarios: 1 of 1 run: 0 passed, 1 did not\. Checks: 27 passed, 0 failed\.')
    Check-Equal 'and the run is not in order' 1 $s.ExitCode
    Check 'its row says TIMED OUT and why' (@($s.Lines | Where-Object { $_ -match '^\s+4\s+TIMED OUT\s+27\s+0\s+900\s' -and $_ -match 'did not close by itself' }).Count -eq 1)
    $graceful = New-Session -Scenario 4 -ScriptLog $scoredLog -SelfTestLog $passLog -ClosedBy 'the game closed itself' -Seconds 442
    Check-Equal 'the same log from a game that closed itself, however slowly, is PASSED' 'PASSED' $graceful.Status
    $s = Summarize @($graceful) @(4) $null
    Check-Equal 'and that run is in order' 0 $s.ExitCode
    $hungFailed = New-Session -Scenario 2 -ScriptLog $scoredLog -SelfTestLog $failLog -ClosedBy $closedByRunner -TimedOut $true
    Check-Equal 'a failing RESULT line and a forced close is TIMED OUT as well' 'TIMED OUT' $hungFailed.Status
    $s = Summarize @($hungFailed) @(2) $null
    Check 'and its failed check is still counted' ($s.ChecksPassed -eq 9 -and $s.ChecksFailed -eq 1 -and $s.ExitCode -eq 1)
    $hungNoResult = New-Session -Scenario 2 -ScriptLog $scoredLog -SelfTestLog @("$stamp ==== The Last Meridian self-test: scenario 2 ====", "$stamp PASS  check 1") -ClosedBy $closedByRunner -TimedOut $true
    Check-Equal 'a forced close with no RESULT line stays UNFINISHED' 'UNFINISHED' $hungNoResult.Status
    $s = Summarize @($twelve, $hung, $play) @(12, 4, 900) $null
    Check 'one timed-out scenario fails a run in which everything else is in order' ($s.ScoredPassed -eq 1 -and $s.ScoredNotPassed -eq 1 -and $s.PlaySetUp -eq 1 -and $s.ChecksPassed -eq 69 -and $s.ExitCode -eq 1)

    # ------------------------------------------------------------ 10. putting back what a run changed
    Write-Host '10. putting back what a run changed'
    $globalName = 'TLM_G_DevScenario'
    function New-StandInPlugin([string]$Path, [single]$Value) {
        # The least a plugin needs for the global to be found: a GLOB record with its EditorID and its value.
        $ascii = [System.Text.Encoding]::ASCII
        $b = New-Object System.Collections.Generic.List[byte]
        $b.AddRange($ascii.GetBytes('TES4')); $b.AddRange([byte[]](0) * 20)
        $b.AddRange($ascii.GetBytes('GLOB')); $b.AddRange([byte[]](0) * 20)
        $name = $ascii.GetBytes($globalName)
        $b.AddRange($ascii.GetBytes('EDID')); $b.AddRange([System.BitConverter]::GetBytes([uint16]($name.Length + 1))); $b.AddRange($name); $b.Add(0)
        $b.AddRange($ascii.GetBytes('FLTV')); $b.AddRange([System.BitConverter]::GetBytes([uint16]4)); $b.AddRange([System.BitConverter]::GetBytes([single]$Value))
        [System.IO.File]::WriteAllBytes($Path, $b.ToArray())
    }
    function New-RunState([string]$Name, [single]$During = 12, [single]$Built = 0) {
        # A PC in the middle of a run: the scenario number written into the installed plugin, the two
        # settings changed, and the run's note of how things were.
        $dir = Join-Path $root "state-$Name"
        [void](New-Item -ItemType Directory -Path $dir)
        $state = [pscustomobject]@{
            Installed = Join-Path $dir 'installed.esp'; Built = Join-Path $dir 'built.esp'
            Ini = Join-Path $dir 'fallout4custom.ini'; Note = Join-Path $dir 'scenario-run.unfinished.json'
        }
        New-StandInPlugin $state.Installed $During
        New-StandInPlugin $state.Built $Built
        Set-Content -LiteralPath $state.Ini -Value @('[General]', 'sStartingConsoleCommand=coc qasmoke', 'bAlwaysActive=1', '[Display]', 'iSize W=1920') -Encoding ascii
        Set-Content -LiteralPath $state.Note -Value '{ "Began": "2026-11-14 10:50:31", "ScenarioBefore": 0, "AlwaysActiveBefore": "0" }' -Encoding ascii
        return $state
    }
    function Restore($state, $alwaysActiveBefore = '0') {
        return (Restore-ScenarioRunState -InstalledPlugin $state.Installed -GlobalName $globalName -ValueAtStart 0 -CustomIni $state.Ini `
            -AlwaysActiveBefore $alwaysActiveBefore -BuiltPlugin $state.Built -UnfinishedPath $state.Note -Unfinished $null -CutOffWithoutNote $false)
    }
    function Notes($restore) { return ($restore.Notes -join "`n") }

    # everything goes back
    $st = New-RunState 'clean'
    $re = Restore $st
    Check 'a clean putting back is not a failure' (-not $re.Failed)
    Check-Equal 'the scenario number is back to 0' 0 (Get-PluginGlobal -Path $st.Installed -EditorId $globalName)
    Check-Equal 'the start-up command is empty' '' "$(Get-IniValue $st.Ini 'General' 'sStartingConsoleCommand')"
    Check-Equal 'the keep-running setting is back' '0' (Get-IniValue $st.Ini 'General' 'bAlwaysActive')
    Check-Equal 'another section of the settings file is untouched' '1920' (Get-IniValue $st.Ini 'Display' 'iSize W')
    Check 'the installed plugin is the build again, and the notes say so' ((Notes $re) -match 'Installed plugin identical to the build again: yes')
    Check 'the note of how things were is removed' (-not (Test-Path -LiteralPath $st.Note))
    Check 'no line says COULD NOT' (-not ((Notes $re) -match 'COULD NOT|NOT EVERYTHING'))
    $s = Get-ScenarioRunSummary -Results @($twelve) -Requested @(12) -PlayNumber $PlayNumber -Titles $Titles -RestoreFailed $re.Failed
    Check-Equal 'a passed run that was put back ends with 0' 0 $s.ExitCode
    # a setting that was something else before the run goes back to that
    $st = New-RunState 'was-on'
    $re = Restore $st '1'
    Check 'a setting that was 1 before the run is 1 again' ((-not $re.Failed) -and (Get-IniValue $st.Ini 'General' 'bAlwaysActive') -eq '1')

    # the scenario number cannot be put back: the installed plugin no longer holds the global
    $st = New-RunState 'no-global'
    Set-Content -LiteralPath $st.Installed -Value 'not a plugin any more' -Encoding ascii
    $re = Restore $st
    Check 'a scenario number that cannot be written is a failure' $re.Failed
    Check 'the notes say what could not be done, and what to do' ((Notes $re) -match 'COULD NOT restore the scenario number in the installed plugin' -and (Notes $re) -match 'Run the install again')
    Check 'the note of how things were is kept' (Test-Path -LiteralPath $st.Note)
    Check 'the notes say that it is kept' ((Notes $re) -match 'NOT EVERYTHING WAS PUT BACK' -and (Notes $re) -match 'scenario-run\.unfinished\.json')
    Check 'the settings were still put back' ("$(Get-IniValue $st.Ini 'General' 'sStartingConsoleCommand')" -eq '' -and (Get-IniValue $st.Ini 'General' 'bAlwaysActive') -eq '0')
    $s = Get-ScenarioRunSummary -Results @($twelve) -Requested @(12) -PlayNumber $PlayNumber -Titles $Titles -RestoreFailed $re.Failed
    Check-Equal 'a run whose scenarios all passed ends with 1 when the number was not put back' 1 $s.ExitCode
    Check 'the scenario still counts as passed' ($s.ScoredPassed -eq 1 -and $s.ChecksPassed -eq 42)
    Check 'and the totals say the run is not in order' ((Text $s) -match 'THE RUN IS NOT IN ORDER')

    # each thing that cannot be put back fails the run by itself: here nothing else is wrong, and there is no build to compare with
    $st = New-RunState 'only-the-number'
    Remove-Item -LiteralPath $st.Built -Force
    Set-Content -LiteralPath $st.Installed -Value 'not a plugin any more' -Encoding ascii
    $re = Restore $st
    Check 'the scenario number alone, not put back, is a failure' ($re.Failed -and @($re.Notes | Where-Object { $_ -match '^COULD NOT' }).Count -eq 1 -and (Test-Path -LiteralPath $st.Note))
    $st = New-RunState 'only-the-settings'
    Remove-Item -LiteralPath $st.Built -Force
    Remove-Item -LiteralPath $st.Ini -Force
    [void](New-Item -ItemType Directory -Path $st.Ini)
    $re = Restore $st
    Check 'the settings alone, not put back, are a failure' ($re.Failed -and @($re.Notes | Where-Object { $_ -match '^COULD NOT' }).Count -eq 2 -and (Test-Path -LiteralPath $st.Note))

    # the installed plugin is gone
    $st = New-RunState 'no-plugin'
    Remove-Item -LiteralPath $st.Installed -Force
    $re = Restore $st
    Check 'an installed plugin that is gone is a failure, and nothing is thrown' ($re.Failed -and (Notes $re) -match 'COULD NOT restore the scenario number' -and (Test-Path -LiteralPath $st.Note))

    # the settings file cannot be written: something else is in its place
    $st = New-RunState 'no-ini'
    Remove-Item -LiteralPath $st.Ini -Force
    [void](New-Item -ItemType Directory -Path $st.Ini)
    $re = Restore $st
    Check 'settings that cannot be written are a failure' $re.Failed
    Check 'the notes name the start-up command' ((Notes $re) -match 'COULD NOT empty the start-up console command')
    Check 'the notes name the keep-running setting' ((Notes $re) -match 'COULD NOT restore bAlwaysActive')
    Check 'the scenario number was still put back' ((Get-PluginGlobal -Path $st.Installed -EditorId $globalName) -eq 0)
    Check 'the note of how things were is kept' (Test-Path -LiteralPath $st.Note)
    $s = Get-ScenarioRunSummary -Results @($twelve, $play) -Requested @(12, 900) -PlayNumber $PlayNumber -Titles $Titles -RestoreFailed $re.Failed
    Check-Equal 'a run in order otherwise ends with 1 when the settings were not put back' 1 $s.ExitCode

    # the installed plugin is not the build
    $st = New-RunState 'mismatch'
    [System.IO.File]::AppendAllText($st.Built, 'x')
    $re = Restore $st
    Check 'an installed plugin that is not the build is a failure' $re.Failed
    Check 'the notes say NO, and what to do' ((Notes $re) -match 'Installed plugin identical to the build again: NO' -and (Notes $re) -match 'Run the install again')
    Check 'the notes say that this, and not a failed putting back, is why the run fails' ((Notes $re) -match 'THE INSTALLED PLUGIN IS NOT THE BUILD' -and -not ((Notes $re) -match 'COULD NOT|NOT EVERYTHING WAS PUT BACK') -and (Notes $re) -match 'scenario-run\.unfinished\.json')
    Check 'the scenario number and the settings were put back all the same' ((Get-PluginGlobal -Path $st.Installed -EditorId $globalName) -eq 0 -and "$(Get-IniValue $st.Ini 'General' 'sStartingConsoleCommand')" -eq '')
    Check 'the note of how things were is kept' (Test-Path -LiteralPath $st.Note)
    $s = Get-ScenarioRunSummary -Results @($twelve) -Requested @(12) -PlayNumber $PlayNumber -Titles $Titles -RestoreFailed $re.Failed
    Check-Equal 'a passed run ends with 1 when the installed plugin is not the build' 1 $s.ExitCode

    # no build to compare with: nothing to say about it, and no failure
    $st = New-RunState 'no-build'
    Remove-Item -LiteralPath $st.Built -Force
    $re = Restore $st
    Check 'with no build to compare with, a clean putting back is still clean' ((-not $re.Failed) -and -not ((Notes $re) -match 'identical to the build'))

    # ------------------------------------------------------------ 11. the runner uses these, and nothing of its own
    Write-Host '11. Run-Scenarios.ps1 takes its words and its totals from the module'
    $runner = Get-Content -LiteralPath (Join-Path $winDir 'Run-Scenarios.ps1') -Raw
    # Its description says what the word used to be; its code must not use it.
    $runner = $runner -replace '(?s)<#.*?#>', ''
    Check 'the runner''s code does not use the word PLAYED' (-not ($runner -cmatch 'PLAYED'))
    Check 'the runner reads a session''s logs through the module' ($runner -match 'Read-ScenarioSessionLogs -UserLog \$userLog -PapyrusLog \$papyrusLog -Since \$since')
    Check 'the runner names a session through the module, and tells it when the time ran out' ($runner -match 'Get-ScenarioSessionStatus -Logs \$logs -Playing \$playing -ClosedBy \$closedBy -TimedOut \$timedOut')
    Check 'the runner puts things back through the module' ($runner -match 'Restore-ScenarioRunState -InstalledPlugin \$installedPlugin')
    Check 'the runner tells the summary whether everything was put back' ($runner -match '-RestoreFailed \$restoreFailed')
    Check 'the runner takes the putting back for failed until it has been seen to work' ($runner -match '(?m)^\$restoreFailed = \$true\s*$')
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
