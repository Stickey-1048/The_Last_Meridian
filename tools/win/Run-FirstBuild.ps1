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

  What it changes: files inside this repository folder, plus one thing outside
  it: the Creation Kit's own Base.zip is unpacked beside itself in the Creation
  Kit folder if the script sources are still zipped (pass -NoExtractBase to
  skip; then step 5 cannot run).

  What it never touches: the game folder Mod Organizer manages, the Mod
  Organizer instance, profiles, load order, saves. Nothing is installed into
  the game. That is a separate, deliberate step (Install-Dev.ps1).

  Status: tested on Linux PowerShell 7 against a stand-in folder tree, a
  stand-in compiler and a stand-in master file. Not yet run on Windows.

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
    [string]$LocalAppDataRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Tlm.psm1') -Force

# For this run only: no .NET first-run banner, and no usage data sent to Microsoft.
$env:DOTNET_NOLOGO = '1'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$build = Join-Path $repo 'build'
New-Item -ItemType Directory -Force -Path $build | Out-Null
$logPath = Join-Path $build 'first-build-log.txt'
$log = New-Object System.Collections.Generic.List[string]
$results = New-Object System.Collections.Generic.List[object]

function Say([string]$s = '') { $log.Add($s); Write-Host $s }
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
            $how = if ($null -ne $st.Percent) { "$($st.Percent)% downloaded" } else { "state $($st.StateFlags)" }
            Result $app.Label 'NOT READY' "$how; wait for Steam to finish, then run this again"
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
        if ($pb.ExitCode -eq 0) {
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
        if ($c.ExitCode -eq 0) { Result 'Papyrus compile' 'PASSED' 'build\Scripts\TLM\*.pex' }
        else { Result 'Papyrus compile' 'FAILED' "exit code $($c.ExitCode); compiler messages are above" }
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
    Say 'Nothing was installed into the game or Mod Organizer.'
    Set-Content -LiteralPath $logPath -Value ($log -join [Environment]::NewLine) -Encoding utf8
    Write-Host ''
    Write-Host "Log written to: $logPath"
    Write-Host 'Send that file (or its contents) back.'
}
