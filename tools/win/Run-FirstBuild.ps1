<#
.SYNOPSIS
  One command for the first session on the game PC: scan, build the plugin,
  compile the scripts, and write one log file to send back.

.DESCRIPTION
  Runs, in order, and keeps going where it sensibly can:
    1. checks git and the .NET SDK are installed
    2. reads Steam's records for Fallout 4 and the Creation Kit (installed, or how far along)
    3. scans the PC and writes docs\design\BUILD_ENV.md          (Get-BuildEnv.ps1)
    4. builds build\TheLastMeridian.esp against the real Fallout4.esm (tools\PluginBuilder)
    5. compiles the Papyrus scripts into build\Scripts            (Build-Scripts.ps1)
  and writes everything it saw to build\first-build-log.txt.

  What it changes: files inside this repository folder, plus two things
  outside it:
    - the Creation Kit's own Base.zip is unpacked beside itself in the Creation
      Kit folder if the script sources are still zipped (pass -NoExtractBase to
      skip; then step 5 cannot run);
    - .NET downloads the plugin builder's libraries into its own cache in the
      Windows user folder (.nuget\packages) the first time it builds.

  On the first real run (2026-11-11), before the settings at the top of this
  script existed, .NET's first use on that PC also created a development HTTPS
  certificate in the user's certificate store and had its usage telemetry on.
  The certificate is untrusted and unused; `dotnet dev-certs https --clean`
  removes it.

  What it never touches: any game folder, existing Mod Organizer profiles,
  the shared load order, saves. By default nothing is installed anywhere.

  With -Install, and only if the build and the compile both passed, it also
  runs Install-Dev.ps1 -CreateProfile: the build is copied into a Mod
  Organizer mod folder and a separate test profile is created. Mod Organizer
  must be closed for that step.

  With -Install -Play, and only if the install passed, it then runs
  Start-TestGame.ps1: the base game is started through Mod Organizer in the
  test profile, and when the game closes the test results (with this build's
  summary on top) replace the build log on the clipboard.

  With -Install -Unattended it runs Run-Scenarios.ps1 instead: the game is
  started once per self-test scenario, enters the test room, runs the scenario
  and closes by itself. Read that script's description first: it closes the
  game it started if a scenario does not finish in time.

  Status: ran on the owner's PC under Windows PowerShell 5.1 on 2026-11-11 and
  every step passed. Additions since then (clipboard copy, wider scan) have
  only run on Linux PowerShell 7 against stand-ins.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\win\Run-FirstBuild.ps1
#>
[CmdletBinding()]
param(
    [string]$ModOrganizerRoot = 'C:\Modlists\TMR',
    # Folder the Creation Kit is installed in. Found through Steam if omitted.
    [string]$CreationKitRoot,
    [switch]$NoExtractBase,
    # Overrides for testing off Windows.
    [string]$SteamRoot,
    [string[]]$SteamLibrary = @('F:\SteamLibrary'),
    [string]$DocumentsRoot,
    [string]$LocalAppDataRoot,
    [string]$AppDataRoot,
    # Do not copy the log to the clipboard at the end.
    [switch]$NoClipboard,
    # After a successful build, install it as a Mod Organizer mod and set up
    # the test profile (Install-Dev.ps1 -ModOrganizerRoot ... -CreateProfile).
    [switch]$Install,
    # After a successful install, start the base game in the test profile and
    # collect the results when it closes (Start-TestGame.ps1). Needs -Install.
    [switch]$Play,
    # After a successful install, run the self-test scenarios with nobody at
    # the keyboard (Run-Scenarios.ps1): the game is started once per scenario,
    # enters the test room, runs the scenario and closes by itself. Needs
    # -Install. If both are given, this wins over -Play.
    [switch]$Unattended,
    # For -Unattended: scenario numbers, ranges (101-128) and set names (all,
    # basic, matrix, main, side), separated by commas. Default: all.
    [string]$Scenarios,
    # Run even though this folder is behind GitHub (see the check below).
    [switch]$AllowStale
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Tlm.psm1') -Force

# For this run only: no .NET first-run banner, no usage data sent to Microsoft,
# and none of the extras .NET sets up the first time it is ever used on a PC
# (a development HTTPS certificate in the user's certificate store, a PATH entry).
$env:DOTNET_NOLOGO = '1'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
$env:DOTNET_GENERATE_ASPNET_CERTIFICATE = 'false'
$env:DOTNET_ADD_GLOBAL_TOOLS_TO_PATH = 'false'

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$build = Join-Path $repo 'build'
New-Item -ItemType Directory -Force -Path $build | Out-Null
$logPath = Join-Path $build 'first-build-log.txt'
$log = New-Object System.Collections.Generic.List[string]
$results = New-Object System.Collections.Generic.List[object]
$pluginOk = $false
$compileOk = $false
$installed = $false
$installTried = $false
$head = $null
$layoutLines = @()
$lookupLines = @()

function Say([string]$s = '') { $log.Add($s); Write-Host $s }

# Is this folder behind GitHub? "git pull; powershell ... this script" runs this
# script even when the pull was refused, and then it is the older scripts that
# run: an old build would be tested while looking like a new one. Better to
# stop. If GitHub cannot be reached the check is skipped.
if (-not $AllowStale) {
    $fetch = Invoke-Native -Exe 'git' -Arguments @('-C', $repo, 'fetch', '--quiet')
    if ($fetch.Found -and $fetch.ExitCode -eq 0) {
        $behind = Invoke-Native -Exe 'git' -Arguments @('-C', $repo, 'rev-list', '--count', 'HEAD..@{u}')
        $count = 0
        if ($behind.ExitCode -eq 0 -and [int]::TryParse("$($behind.Output | Select-Object -First 1)".Trim(), [ref]$count) -and $count -gt 0) {
            Write-Host "This folder is $count commit(s) behind GitHub, so it was not brought up to date before this script started"
            Write-Host '(a "git pull" that was refused leaves the older scripts in place). Nothing was built or run.'
            Write-Host ''
            Write-Host 'Run this instead, with the same options. It updates the folder first and stops if it cannot:'
            Write-Host '    powershell -ExecutionPolicy Bypass -File tools\win\Update-And-Run.ps1 <options>'
            exit 1
        }
    }
}

# The install step needs Mod Organizer closed, and the test must not mistake a
# game that is already running for the one it starts. Ask before the long build.
if (($Install -or $Play -or $Unattended) -and -not (Wait-GameAndManagerClosed)) {
    Write-Host 'Still open after ten minutes. Nothing was built or installed. Close them and run the command again.'
    exit 1
}
function Result([string]$step, [string]$status, [string]$detail = '') {
    $results.Add([pscustomobject]@{ Step = $step; Status = $status; Detail = $detail })
    Say ("  -> {0}: {1}{2}" -f $step, $status, $(if ($detail) { " ($detail)" } else { '' }))
}
function Section([string]$title) { Say ''; Say "== $title =="; }

# Runs one of the sibling scripts in this session. Its output is collected
# line by line, so what it printed before a failure is kept. A script that
# throws, or ends with a non-zero exit code, counts as failed.
function Invoke-Sibling([string]$name, [hashtable]$scriptParams) {
    $path = Join-Path $PSScriptRoot $name
    $lines = New-Object System.Collections.Generic.List[string]
    $global:LASTEXITCODE = 0
    $code = 0
    try {
        & $path @scriptParams *>&1 | ForEach-Object { $lines.Add("$_") }
        if ($LASTEXITCODE) { $code = $LASTEXITCODE }
    } catch {
        $lines.Add("ERROR: $($_.Exception.Message)")
        $code = 1
    }
    # The sibling re-imports the shared module; make sure this script still has it.
    Import-Module (Join-Path $PSScriptRoot 'Tlm.psm1') -Force
    return [pscustomobject]@{ ExitCode = $code; Output = $lines.ToArray() }
}

try {
    Say "The Last Meridian: first build   $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    Say "Repository: $repo"
    $head = Invoke-Native -Exe 'git' -Arguments @('-C', $repo, 'log', '--oneline', '-1')
    if ($head.Found -and $head.ExitCode -eq 0) { Say "Commit    : $($head.Output | Select-Object -First 1)" }
    Say "PowerShell: $($PSVersionTable.PSVersion)"

    # ---------------------------------------------------------- 1. tools
    Section '1. Tools'
    $git = Invoke-Native -Exe 'git' -Arguments @('--version')
    if ($git.Found -and $git.ExitCode -eq 0) { Result 'git' 'PASSED' ($git.Output | Select-Object -First 1) } else { Result 'git' 'MISSING' 'install Git for Windows' }
    $dotnet = Invoke-Native -Exe 'dotnet' -Arguments @('--list-sdks')
    $haveSdk8 = $dotnet.Found -and $dotnet.ExitCode -eq 0 -and [bool](@($dotnet.Output | Where-Object { $_ -match '^8\.' }).Count)
    if ($haveSdk8) { Result '.NET 8 SDK' 'PASSED' (@($dotnet.Output | Where-Object { $_ -match '^8\.' })[0]) }
    else { Result '.NET 8 SDK' 'MISSING' 'install the .NET 8 SDK; the plugin cannot be built without it' }

    # ---------------------------------------------------------- 2. Steam
    Section '2. Steam installs'
    $ckFolder = $CreationKitRoot
    foreach ($app in @(@{ Id = '377160'; Label = 'Fallout 4 (Steam)' }, @{ Id = '1946160'; Label = 'Creation Kit' })) {
        $st = Get-SteamAppState -AppId $app.Id -SteamRoot $SteamRoot -ExtraLibrary $SteamLibrary
        if (-not $st) { Result $app.Label 'NOT FOUND' 'Steam has no record of it in any library'; continue }
        if ($st.Installed) { Result $app.Label 'PASSED' "installed in $($st.Folder)" }
        else {
            $how = if ($null -ne $st.Percent) { "Steam's record says $($st.Percent)%, which lags behind its progress bar" } else { "state $($st.StateFlags)" }
            Result $app.Label 'NOT READY' "still downloading; $how"
        }
        if ($app.Id -eq '1946160' -and -not $ckFolder -and $st.Installed) { $ckFolder = $st.Folder }
    }
    if (-not $ckFolder) {
        # Steam's record may be missing while the files are there.
        foreach ($lib in $SteamLibrary) {
            $guess = Join-Path (Join-Path (Join-Path $lib 'steamapps') 'common') 'Fallout 4'
            if (Test-Path -LiteralPath (Join-Path $guess 'CreationKit.exe')) { $ckFolder = $guess }
        }
    }
    if ($ckFolder -and (Test-Path -LiteralPath (Join-Path $ckFolder 'CreationKit.exe'))) {
        Say "Creation Kit folder: $ckFolder"
        Say "  CreationKit.exe     : $(Get-ExeVersion (Join-Path $ckFolder 'CreationKit.exe'))"
        Say "  Fallout4.exe (Steam): $(Get-ExeVersion (Join-Path $ckFolder 'Fallout4.exe'))"
        Say "  PapyrusCompiler.exe : $(if (Test-Path -LiteralPath (Join-Path (Join-Path $ckFolder 'Papyrus Compiler') 'PapyrusCompiler.exe')) { 'present' } else { 'MISSING' })"
    } else {
        $ckFolder = $null
        Say 'Creation Kit folder: not found'
    }

    # ---------------------------------------------------------- 3. scan
    Section '3. Environment scan'
    $moOk = $ModOrganizerRoot -and (Test-Path -LiteralPath (Join-Path $ModOrganizerRoot 'ModOrganizer.ini'))
    $scanArgs = @{}
    if ($moOk) { $scanArgs['ModOrganizerRoot'] = $ModOrganizerRoot } else { Say "No ModOrganizer.ini in '$ModOrganizerRoot'; scanning without it." }
    if ($ckFolder) { $scanArgs['CreationKitRoot'] = $ckFolder }
    if ($SteamRoot) { $scanArgs['SteamRoot'] = $SteamRoot }
    if ($DocumentsRoot) { $scanArgs['DocumentsRoot'] = $DocumentsRoot }
    if ($LocalAppDataRoot) { $scanArgs['LocalAppDataRoot'] = $LocalAppDataRoot }
    if ($AppDataRoot) { $scanArgs['AppDataRoot'] = $AppDataRoot }
    $scan = Invoke-Sibling 'Get-BuildEnv.ps1' $scanArgs
    $scan.Output | ForEach-Object { Say "  $_" }
    if ($scan.ExitCode -eq 0) { Result 'Environment scan' 'PASSED' 'docs\design\BUILD_ENV.md written' } else { Result 'Environment scan' 'FAILED' "exit code $($scan.ExitCode)" }

    # ---------------------------------------------------------- 4. plugin
    Section '4. Plugin build against the real Fallout4.esm'
    $esm = $null
    if ($moOk) {
        $mo = Get-ModOrganizerInfo -Root $ModOrganizerRoot
        if ($mo.GamePath) { $esm = Join-Path (Join-Path $mo.GamePath 'Data') 'Fallout4.esm' }
    }
    if (-not $haveSdk8) { Result 'Plugin build' 'SKIPPED' 'no .NET 8 SDK' }
    elseif (-not $esm -or -not (Test-Path -LiteralPath $esm)) { Result 'Plugin build' 'SKIPPED' "Fallout4.esm not found ($esm)" }
    else {
        Say "Master file: $esm ($([math]::Round((Get-Item -LiteralPath $esm).Length / 1MB)) MB)"
        Say '  Working. The first run downloads the builder''s libraries and then reads the whole master file;'
        Say '  this can take several minutes and prints nothing until it is done.'
        $pb = Invoke-Native -Exe 'dotnet' -Arguments @('run', '--project', (Join-Path (Join-Path $repo 'tools') 'PluginBuilder'), '--', '--out', $build, '--fallout4-esm', $esm)
        $pb.Output | Where-Object { $_ -notmatch 'warning (NU|CS)' } | ForEach-Object { Say "  $_" }
        # How this plugin's quests are laid out beside the game's own: kept for the test results.
        $layoutLines = @($pb.Output | Where-Object { $_ -match '^\s*layout:' } | ForEach-Object { "$_".Trim() })
        # What the builder found in the game's master file: the self-test's stand-ins depend on it.
        $lookupLines = @($pb.Output | Where-Object { $_ -match '^\s*lookup:' } | ForEach-Object { "$_".Trim() } | Select-Object -Unique)
        if ($pb.ExitCode -eq 0) {
            $pluginOk = $true
            Result 'Plugin build' 'PASSED' 'build\TheLastMeridian.esp'
            $report = Join-Path $build 'TheLastMeridian.report.txt'
            if (Test-Path -LiteralPath $report) {
                Say '  Lines of the report that depend on the real master:'
                Get-Content -LiteralPath $report | Where-Object { $_ -match 'alias\s+0 Player|Caps = |^Not wired yet' } | ForEach-Object { Say "    $_" }
            }
        } else { Result 'Plugin build' 'FAILED' "exit code $($pb.ExitCode)" }
    }

    # ---------------------------------------------------------- 5. compile
    Section '5. Papyrus compile'
    if (-not $ckFolder) { Result 'Papyrus compile' 'SKIPPED' 'Creation Kit not installed yet' }
    else {
        $compileArgs = @{ CreationKitRoot = $ckFolder }
        if (-not $NoExtractBase) { $compileArgs['ExtractBase'] = $true }
        $c = Invoke-Sibling 'Build-Scripts.ps1' $compileArgs
        $c.Output | ForEach-Object { Say "  $_" }
        if ($c.ExitCode -eq 0) { $compileOk = $true; Result 'Papyrus compile' 'PASSED' 'build\Scripts\TLM\*.pex' }
        else { Result 'Papyrus compile' 'FAILED' "exit code $($c.ExitCode); compiler messages are above" }
    }

    # ---------------------------------------------------------- 6. install
    if ($Install) {
        Section '6. Install for testing (Mod Organizer mod and test profile)'
        if (-not ($pluginOk -and $compileOk)) { Result 'Install for testing' 'SKIPPED' 'the plugin build and the compile must both pass first' }
        elseif (-not $moOk) { Result 'Install for testing' 'SKIPPED' "no Mod Organizer instance at '$ModOrganizerRoot'" }
        else {
            $installTried = $true
            $inst = Invoke-Sibling 'Install-Dev.ps1' @{ ModOrganizerRoot = $ModOrganizerRoot; CreateProfile = $true }
            $inst.Output | ForEach-Object { Say "  $_" }
            if ($inst.ExitCode -eq 0) { $installed = $true; Result 'Install for testing' 'PASSED' 'Mod Organizer mod and test profile' }
            else { Result 'Install for testing' 'FAILED' 'see the message above' }
        }
    }
} catch {
    Say ''
    Say "STOPPED by an unexpected error: $($_.Exception.Message)"
    Say ($_.ScriptStackTrace)
    Result 'Run-FirstBuild' 'FAILED' 'unexpected error; see above'
} finally {
    Say ''
    Say '== Summary =='
    foreach ($r in $results) { Say ("  {0,-18} {1}{2}" -f $r.Step, $r.Status, $(if ($r.Detail) { "  ($($r.Detail))" } else { '' })) }
    Say ''
    if ($installed) {
        Say 'Installed as a Mod Organizer mod with its own test profile. The game folders were not touched.'
        if ($Unattended) { Say 'The self-test scenarios are run next, unattended.' }
        elseif ($Play) { Say 'The game is started next, for the in-game test.' }
        else { Say 'The NEXT STEP is given under step 6 above.' }
    } elseif ($installTried) {
        # The install copies the build into the mod folder first and sets up the profile second.
        Say 'The install step did not finish. It copies the build into the Mod Organizer mod folder before it sets up'
        Say 'the test profile, so that mod folder may already hold this build. No game folder was touched.'
    } else {
        Say 'Nothing was installed into the game or a mod manager.'
    }

    # The scan's full findings go into the same log, so one paste carries everything.
    $envFile = Join-Path (Join-Path (Join-Path $repo 'docs') 'design') 'BUILD_ENV.md'
    if (Test-Path -LiteralPath $envFile) {
        $log.Add('')
        $log.Add('== docs\design\BUILD_ENV.md ==')
        foreach ($line in Get-Content -LiteralPath $envFile) { $log.Add($line) }
    }

    # Keep the Windows user folder name out of the log.
    $text = Hide-UserFolder ($log -join [Environment]::NewLine)
    Set-Content -LiteralPath $logPath -Value $text -Encoding utf8
    Write-Host ''
    Write-Host "Log written to: $logPath"

    $copied = $false
    if (-not $NoClipboard -and (Get-Command Set-Clipboard -ErrorAction SilentlyContinue)) {
        try { Set-Clipboard -Value $text; $copied = $true } catch { }
    }
    if (($Play -or $Unattended) -and $installed) {
        Write-Host 'Nothing to send yet: the game is started next, and when it closes the test results'
        Write-Host '(with this build''s summary on top) go on the clipboard instead.'
    } elseif ($copied) {
        Write-Host ''
        Write-Host 'The whole log is on your clipboard. Click in the chat and press Ctrl+V to send it.'
    } else {
        Write-Host 'Send that file (or its contents) back.'
    }

    if ($Play -or $Unattended) {
        Write-Host ''
        if (-not $installed) {
            Write-Host 'The game was not started: the install step did not pass (see the summary above).'
        } else {
            Write-Host $(if ($Unattended) { '== Running the self-test scenarios unattended ==' } else { '== Starting the game for the in-game test ==' })
            $preface = New-Object System.Collections.Generic.List[string]
            $preface.Add('== Build that was installed ==')
            if ($head -and $head.Found -and $head.ExitCode -eq 0) { $preface.Add("Commit: $($head.Output | Select-Object -First 1)") }
            foreach ($r in $results) { $preface.Add(("  {0,-18} {1}{2}" -f $r.Step, $r.Status, $(if ($r.Detail) { "  ($($r.Detail))" } else { '' }))) }
            foreach ($l in $lookupLines) { $preface.Add("  $l") }
            foreach ($l in $layoutLines) { $preface.Add("  $l") }
            $preface.Add('')
            $playArgs = @{ ModOrganizerRoot = $ModOrganizerRoot; Preface = $preface.ToArray() }
            if ($DocumentsRoot) { $playArgs['DocumentsRoot'] = $DocumentsRoot }
            if ($LocalAppDataRoot) { $playArgs['LocalAppDataRoot'] = $LocalAppDataRoot }
            if ($NoClipboard) { $playArgs['NoClipboard'] = $true }
            $playScript = 'Start-TestGame.ps1'
            if ($Unattended) {
                $playScript = 'Run-Scenarios.ps1'
                if ($Scenarios) { $playArgs['Scenarios'] = $Scenarios }
            }
            try { & (Join-Path $PSScriptRoot $playScript) @playArgs }
            catch {
                # Nothing was collected, so the build log carries the reason instead.
                $why = "The game was not started: $($_.Exception.Message)"
                Write-Host $why
                $text = $text + [Environment]::NewLine + [Environment]::NewLine + '== In-game test ==' + [Environment]::NewLine + (Hide-UserFolder $why)
                try { Set-Content -LiteralPath $logPath -Value $text -Encoding utf8 } catch { }
                if (-not $NoClipboard -and (Get-Command Set-Clipboard -ErrorAction SilentlyContinue)) {
                    try { Set-Clipboard -Value $text; Write-Host 'The build log, with that message added, is on your clipboard. Click in the chat and press Ctrl+V to send it.' } catch { }
                }
            }
        }
    }
}
