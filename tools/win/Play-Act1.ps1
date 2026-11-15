<#
.SYNOPSIS
  Starts the game with the first section of Act I set up to be played by hand.

.DESCRIPTION
  One command for the whole of it: brings this folder up to date with GitHub,
  compiles the scripts, builds and installs the test plugin, starts the base
  game through Mod Organizer in the test profile, and has the game enter its
  test room. A few seconds later the plugin sets the first section up there:
  the wreck to the left, the road ahead, Mercy Crossing to the right
  (docs\design\TLM_ACT1_first_section.md).

  Then the game is yours. Nothing is scored and nothing here ends the game:
  quit it from its own menu when you have seen enough. This window waits for
  that, puts back what the run changed, and collects what the game wrote
  (which stages were set, in what order, and anything the script log says of
  the section) into build\scenario-results.txt and onto the clipboard. The
  report says SET UP or NOT SET UP for the session, apart from any scored
  scenario: a set-up is not a pass, and the report cannot tell whether
  anybody played.

  It is Update-And-Run.ps1 with  -Install -Unattended -Scenarios 900 ;
  anything else on the command line is passed on with those. 900 is not a
  scenario of the self-test: it is the number that tells the plugin to set
  the section up and leave the game open.

  Its fresh main-menu COC entry uses a temporary startup batch that sets the
  seven base SPECIAL values to 4 (28 total). Native level 1 is left unchanged;
  health/AP are derived by the engine. It grants no perks, caps, gear or cheat
  protection. No quest/load function resets stats on an existing or resumed
  character. The runner removes its batch and startup command afterwards.

  DEVELOPMENT ONLY. The section stands in the game's own test room and its
  people are copies of the game's settler. Use the test profile only, and
  switch Mod Organizer back to your own profile afterwards.

  Status: tested on Linux PowerShell 7 with stand-ins for Mod Organizer and
  the game. THIS SCRIPT HAS NOT YET RUN ON A REAL PC. What it leads to,
  Run-Scenarios.ps1 with the number 900, ran there once on 2026-11-14 on a
  build already installed: the section was set up, and nobody played
  (docs\design\VERIFY_LOG.md).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\win\Play-Act1.ps1
#>

# No param block on purpose: everything on the command line is passed on.
$passThrough = @($args)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

& (Join-Path $PSScriptRoot 'Update-And-Run.ps1') -Install -Unattended -Scenarios 900 @passThrough
exit $LASTEXITCODE
