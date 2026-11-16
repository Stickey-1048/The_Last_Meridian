<# Fresh exterior story entry only. No installation, saved-character reset or private probe. #>
[CmdletBinding()]
param([string]$ModOrganizerRoot = 'C:\Modlists\TMR', [switch]$UseF4SE, [switch]$ValidateOnly, [switch]$Expanded, [switch]$Natural, [switch]$Details)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Tlm.psm1') -Force
Import-Module (Join-Path $PSScriptRoot 'World-Story.psm1') -Force
Assert-WorldStoryProcessesClear
$variant = Get-WorldStoryVariant -Expanded:$Expanded -Natural:$Natural -Details:$Details
$context = Get-WorldStoryContext -ModOrganizerRoot $ModOrganizerRoot -Expanded:$Expanded -Natural:$Natural -Details:$Details
if ((Get-ExeVersion $context.GameExe) -ne '1.10.163.0') { throw 'Story preview is reviewed for the managed Fallout 4 1.10.163 runtime only.' }
if ($context.RequiresF4SE -and -not $UseF4SE) { throw 'This story profile enables F4SE-dependent mods. Use -UseF4SE or the story .cmd launcher.' }
$launcher = Get-ScenarioLaunchExecutable -GameExe $context.GameExe -UseF4SE:$UseF4SE
$manager = Join-Path $context.Mo.Root 'ModOrganizer.exe'
if (-not (Test-Path -LiteralPath $manager -PathType Leaf)) { throw 'Mod Organizer executable is missing.' }
$build = Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'build'
$journal = Join-Path $build $variant.JournalName
$ini = Join-Path $context.Profile 'fallout4custom.ini'
if (Test-Path -LiteralPath $journal) {
    if ($ValidateOnly) { throw 'An unfinished story startup note needs recovery; validation made no changes.' }
    $old = Get-Content -LiteralPath $journal -Raw | ConvertFrom-Json
    Assert-WorldStoryRecoveryNote -Note $old -Ini $ini -GameFolder $context.Mo.GamePath -Variant $variant.Id
    Restore-WorldStoryState -Note $old
    Remove-Item -LiteralPath $journal -Force
}
$state = Get-WorldStoryStartupState -Ini $ini
$startup = $state.Startup; $active = $state.Active
if ($ValidateOnly) { Write-Host "Story preflight passed; launcher: $launcher; nothing changed or started. Native startup not tested."; exit 0 }
[void](New-Item -ItemType Directory -Force -Path $build)
Assert-WorldStoryProcessesClear
$plan = Get-WorldStoryStartupPlan -GameFolder $context.Mo.GamePath -Expanded:$Expanded -Natural:$Natural -Details:$Details
$note = [pscustomobject]@{ Variant=$variant.Id; ProfileName=$variant.ProfileName; Ini = $ini; GameFolder = $context.Mo.GamePath; StartupBefore = $startup; ActiveBefore = "$active"; Batch = $plan }
Set-Content -LiteralPath $journal -Value ($note | ConvertTo-Json -Depth 4) -Encoding utf8
$startedGame = $null
try {
    Write-FreshDemoStartupBatch -Plan $plan -OnStateChanged ({ param($p) Set-Content -LiteralPath $journal -Value ($note | ConvertTo-Json -Depth 4) -Encoding utf8 }.GetNewClosure())
    Set-IniValue $ini 'General' 'sStartingConsoleCommand' $plan.Command
    Set-IniValue $ini 'General' 'bAlwaysActive' '1'
    if ((Get-IniValue $ini 'General' 'sStartingConsoleCommand') -cne $plan.Command -or
        (Get-IniValue $ini 'General' 'bAlwaysActive') -ne '1') { throw 'Temporary world startup settings failed read-back.' }
    Write-Host 'MERIDIAN EXTERIOR STORY PROTOTYPE - fresh disposable character, balanced SPECIAL 4 each.'
    if ($Details) { Write-Host 'Shelter Details variant selected: six storage props are scenery, with no new crafting or storage functions. Native preview acceptance remains pending.' }
    if ($Natural) { Write-Host 'Natural layout and repaired handover variant selected. Composed native acceptance remains pending.' }
    if ($Expanded) { Write-Host 'Expanded world variant selected. Native rendering, routes and full quest acceptance remain pending.' }
    Write-Host 'Fresh story setup is queued after the exterior loads. This prototype reuses the first-section quest rules.'
    Write-Host 'Wait for setup, use the Directions objects, search the wreck and take the dispatch to Sheriff Pritchard. Quit normally WITHOUT SAVING.'
    Write-Host 'Close Mod Organizer too if it stays open (check the taskbar). Keep this window open until it confirms settings restored.'
    Write-Host "Verified world: $($context.World); launch: $launcher; profile: $($variant.ProfileName)"
    $argsLine = '-p "{0}" run "{1}"' -f $variant.ProfileName,$launcher
    $process = Start-Process -FilePath $manager -ArgumentList $argsLine -WorkingDirectory $context.Mo.Root -WindowStyle Hidden -PassThru
    $deadline = (Get-Date).AddSeconds(180)
    while ((Get-Date) -lt $deadline) {
        # A failed Windows inventory must not be mistaken for an absent game.
        [void](Get-WorldStoryProcessInventory)
        $running = @(Get-RunningGame)
        if ($running.Count) { $startedGame = $running[0]; break }
        Start-Sleep -Milliseconds 500
    }
    if (-not $startedGame) { throw 'The game did not appear. Close any Mod Organizer prompt/process before retrying; no preview pass is claimed.' }
    $path = $startedGame.Path
    if (-not $path -or -not (Test-SamePath $path $context.GameExe)) { throw 'The running game is not the expected managed Fallout4.exe. Close it; no preview pass is claimed.' }
    while (-not (Get-WorldStoryProcessInventory).Clear) { Start-Sleep -Seconds 1 }
} finally {
    # Restore checks both inventories again before its first write. Any live,
    # residual or unreadable inventory throws and leaves note/batch/settings.
    Assert-WorldStoryRecoveryNote -Note $note -Ini $ini -GameFolder $context.Mo.GamePath -Variant $variant.Id
    Restore-WorldStoryState -Note $note
    Remove-Item -LiteralPath $journal -Force
    Write-Host 'World preview settings restored and owned startup batch removed. No gameplay completion is inferred.'
}
