<# Fresh exterior story entry only. No installation, saved-character reset or private probe. #>
[CmdletBinding()]
param([string]$ModOrganizerRoot = 'C:\Modlists\TMR', [switch]$UseF4SE, [switch]$ValidateOnly)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Tlm.psm1') -Force
Import-Module (Join-Path $PSScriptRoot 'World-Story.psm1') -Force
if (@(Get-RunningGame).Count -or (Test-ModOrganizerRunning)) { throw 'Close Fallout 4 and Mod Organizer before starting the world preview.' }
$context = Get-WorldStoryContext -ModOrganizerRoot $ModOrganizerRoot
if ((Get-ExeVersion $context.GameExe) -ne '1.10.163.0') { throw 'Story preview is reviewed for the managed Fallout 4 1.10.163 runtime only.' }
if ($context.RequiresF4SE -and -not $UseF4SE) { throw 'This story profile enables F4SE-dependent mods. Use -UseF4SE or the story .cmd launcher.' }
$launcher = Get-ScenarioLaunchExecutable -GameExe $context.GameExe -UseF4SE:$UseF4SE
$manager = Join-Path $context.Mo.Root 'ModOrganizer.exe'
if (-not (Test-Path -LiteralPath $manager -PathType Leaf)) { throw 'Mod Organizer executable is missing.' }
$build = Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'build'
$journal = Join-Path $build 'world-story.unfinished.json'
$ini = Join-Path $context.Profile 'fallout4custom.ini'
if (Test-Path -LiteralPath $journal) {
    if ($ValidateOnly) { throw 'An unfinished story startup note needs recovery; validation made no changes.' }
    $old = Get-Content -LiteralPath $journal -Raw | ConvertFrom-Json
    if (-not (Test-SamePath $old.Ini $ini) -or -not (Test-SamePath $old.GameFolder $context.Mo.GamePath)) { throw 'Unfinished note belongs to another profile/install; left untouched.' }
    Restore-WorldStoryState -Note $old
    Remove-Item -LiteralPath $journal -Force
}
$state = Get-WorldStoryStartupState -Ini $ini
$startup = $state.Startup; $active = $state.Active
if ($ValidateOnly) { Write-Host "Story preflight passed; launcher: $launcher; nothing changed or started. Native startup not tested."; exit 0 }
[void](New-Item -ItemType Directory -Force -Path $build)
$plan = Get-WorldStoryStartupPlan -GameFolder $context.Mo.GamePath
$note = [pscustomobject]@{ Ini = $ini; GameFolder = $context.Mo.GamePath; StartupBefore = $startup; ActiveBefore = "$active"; Batch = $plan }
Set-Content -LiteralPath $journal -Value ($note | ConvertTo-Json -Depth 4) -Encoding utf8
$startedGame = $null
try {
    Write-FreshDemoStartupBatch -Plan $plan -OnStateChanged ({ param($p) Set-Content -LiteralPath $journal -Value ($note | ConvertTo-Json -Depth 4) -Encoding utf8 }.GetNewClosure())
    Set-IniValue $ini 'General' 'sStartingConsoleCommand' $plan.Command
    Set-IniValue $ini 'General' 'bAlwaysActive' '1'
    if ((Get-IniValue $ini 'General' 'sStartingConsoleCommand') -cne $plan.Command -or
        (Get-IniValue $ini 'General' 'bAlwaysActive') -ne '1') { throw 'Temporary world startup settings failed read-back.' }
    Write-Host 'MERIDIAN EXTERIOR STORY PROTOTYPE - fresh disposable character, balanced SPECIAL 4 each.'
    Write-Host 'Fresh story setup is queued after the exterior loads. This prototype reuses the first-section quest rules.'
    Write-Host 'Wait for setup, use the Directions objects, search the wreck and take the dispatch to Sheriff Pritchard. Quit normally WITHOUT SAVING.'
    Write-Host 'Close Mod Organizer too if it stays open (check the taskbar). Keep this window open until it confirms settings restored.'
    Write-Host "Verified world: $($context.World); launch: $launcher; profile: TLM-World-Story-Preview"
    $argsLine = '-p "TLM-World-Story-Preview" run "{0}"' -f $launcher
    $process = Start-Process -FilePath $manager -ArgumentList $argsLine -WorkingDirectory $context.Mo.Root -WindowStyle Hidden -PassThru
    $deadline = (Get-Date).AddSeconds(180)
    while ((Get-Date) -lt $deadline) {
        $running = @(Get-RunningGame)
        if ($running.Count) { $startedGame = $running[0]; break }
        Start-Sleep -Milliseconds 500
    }
    if (-not $startedGame) { throw 'The game did not appear. Close any Mod Organizer prompt/process before retrying; no preview pass is claimed.' }
    $path = $startedGame.Path
    if (-not $path -or -not (Test-SamePath $path $context.GameExe)) { throw 'The running game is not the expected managed Fallout4.exe. Close it; no preview pass is claimed.' }
    while (@(Get-RunningGame).Count -or (Test-ModOrganizerRunning)) { Start-Sleep -Seconds 1 }
} finally {
    # Do not remove a live startup batch or change settings under a running game/manager.
    if (@(Get-RunningGame).Count -or (Test-ModOrganizerRunning)) {
        Write-Warning 'Game/manager still open: ownership note and startup state retained. Close both; the next launch retries cleanup.'
    } else {
        Restore-WorldStoryState -Note $note
        Remove-Item -LiteralPath $journal -Force
        Write-Host 'World preview settings restored and owned startup batch removed. No gameplay completion is inferred.'
    }
}
