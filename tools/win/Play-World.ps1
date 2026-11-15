<# Fresh exterior shell only. No installation, quest start, saved-character reset or private probe. #>
[CmdletBinding()]
param([string]$ModOrganizerRoot = 'C:\Modlists\TMR', [switch]$UseF4SE, [switch]$ValidateOnly)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Tlm.psm1') -Force
Import-Module (Join-Path $PSScriptRoot 'World-Preview.psm1') -Force
if (@(Get-RunningGame).Count -or (Test-ModOrganizerRunning)) { throw 'Close Fallout 4 and Mod Organizer before starting the world preview.' }
$context = Get-WorldPreviewContext -ModOrganizerRoot $ModOrganizerRoot
$launcher = Get-ScenarioLaunchExecutable -GameExe $context.GameExe -UseF4SE:$UseF4SE
$manager = Join-Path $context.Mo.Root 'ModOrganizer.exe'
if (-not (Test-Path -LiteralPath $manager -PathType Leaf)) { throw 'Mod Organizer executable is missing.' }
if ($ValidateOnly) { Write-Host "World preview preflight passed; launcher: $launcher; nothing changed or started."; exit 0 }
$build = Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'build'
[void](New-Item -ItemType Directory -Force -Path $build)
$journal = Join-Path $build 'world-preview.unfinished.json'
$ini = Join-Path $context.Profile 'fallout4custom.ini'
if (Test-Path -LiteralPath $journal) {
    $old = Get-Content -LiteralPath $journal -Raw | ConvertFrom-Json
    if (-not (Test-SamePath $old.Ini $ini) -or -not (Test-SamePath $old.GameFolder $context.Mo.GamePath)) { throw 'Unfinished note belongs to another profile/install; left untouched.' }
    Restore-WorldPreviewState -Note $old
    Remove-Item -LiteralPath $journal -Force
}
$startup = [string](Get-IniValue $ini 'General' 'sStartingConsoleCommand')
if ($startup.Trim()) { throw 'Dedicated world profile still has a startup command; finish its prior QA cleanup first.' }
$active = Get-IniValue $ini 'General' 'bAlwaysActive'
if ($null -eq $active -or "$active" -eq '') { $active = '0' }
$plan = Get-WorldStartupPlan -GameFolder $context.Mo.GamePath
$note = [pscustomobject]@{ Ini = $ini; GameFolder = $context.Mo.GamePath; StartupBefore = $startup; ActiveBefore = "$active"; Batch = $plan }
Set-Content -LiteralPath $journal -Value ($note | ConvertTo-Json -Depth 4) -Encoding utf8
$startedGame = $null
try {
    Write-FreshDemoStartupBatch -Plan $plan -OnStateChanged ({ param($p) Set-Content -LiteralPath $journal -Value ($note | ConvertTo-Json -Depth 4) -Encoding utf8 }.GetNewClosure())
    Set-IniValue $ini 'General' 'sStartingConsoleCommand' $plan.Command
    Set-IniValue $ini 'General' 'bAlwaysActive' '1'
    if ((Get-IniValue $ini 'General' 'sStartingConsoleCommand') -cne $plan.Command -or
        (Get-IniValue $ini 'General' 'bAlwaysActive') -ne '1') { throw 'Temporary world startup settings failed read-back.' }
    Write-Host 'MERIDIAN EXTERIOR PREVIEW - fresh disposable character, balanced SPECIAL 4 each.'
    Write-Host 'This is the exterior shell: terrain, cabin, furniture and fences. Story quests/guides are not connected here yet.'
    Write-Host 'Look around, try the cabin bed and couch, then quit normally WITHOUT SAVING. This window restores the two temporary settings.'
    Write-Host "Verified world: $($context.World); launch: $launcher; profile: TLM-World-Preview"
    $argsLine = '-p "TLM-World-Preview" run "{0}"' -f $launcher
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
        Restore-WorldPreviewState -Note $note
        Remove-Item -LiteralPath $journal -Force
        Write-Host 'World preview settings restored and owned startup batch removed. No gameplay completion is inferred.'
    }
}
