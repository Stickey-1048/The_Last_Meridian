<#
.SYNOPSIS
  Brings this folder up to date with GitHub, then runs Run-FirstBuild.ps1 with
  the options given. If the folder cannot be brought up to date it stops and
  runs nothing.

.DESCRIPTION
  Why this exists: the one-line command used so far,
      git pull; powershell ... Run-FirstBuild.ps1 ...
  runs its second half even when the first half failed. On 2026-11-12 a pull
  was refused, the older scripts then ran, and the only visible sign was an
  error about an option they did not know. With an option they did know, an
  old build would have been tested while looking like a new one.

  What it does:
    1. Looks at the tracked files git reports as changed on this PC.
       - A file whose content is the same as git's copy (only its line endings
         or its size on disk differ) is refreshed in git's index. Nothing is
         staged and nothing is discarded; git simply stops reporting it.
       - A file whose content really differs stops the script. The file is
         listed, nothing is pulled, nothing is discarded.
    2. Runs  git pull --ff-only.  If that fails, it stops.
    3. Starts Run-FirstBuild.ps1 in a new PowerShell with the options given,
       so the scripts that run are the ones just received.

  Every option on the command line is passed on to Run-FirstBuild.ps1.

  Status: tested on Linux PowerShell 7 against scratch clones of this
  repository (up to date, behind, behind with a file git wrongly thinks
  changed, behind with a file really changed). NOT YET RUN ON A REAL PC.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\win\Update-And-Run.ps1 -Install -Unattended
#>

# No param block on purpose: everything on the command line is for Run-FirstBuild.ps1.
$passThrough = @($args)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Tlm.psm1') -Force

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
function Invoke-Git([string[]]$arguments) { return Invoke-Native -Exe 'git' -Arguments (@('-C', $repo) + $arguments) }

$at = Invoke-Git @('log', '--oneline', '-1')
if (-not $at.Found) { Write-Host 'git was not found. Install Git for Windows, then run this again.'; exit 1 }
if ($at.ExitCode -ne 0) { Write-Host "This is not a git folder: $repo"; exit 1 }
Write-Host "Folder : $repo"
Write-Host "Now at : $($at.Output | Select-Object -First 1)"

# ---- 1. files git reports as changed on this PC
$status = Invoke-Git @('status', '--porcelain', '--untracked-files=no')
$changed = New-Object System.Collections.Generic.List[string]
foreach ($line in @($status.Output | Where-Object { $_ -and $_.Length -gt 3 })) {
    $code = $line.Substring(0, 2)
    $file = $line.Substring(3).Trim('"')
    if ($code -eq ' M') {
        # Changed in the folder, not staged. Is the content really different?
        $diff = Invoke-Git @('diff', '--quiet', '--', $file)
        if ($diff.ExitCode -eq 0) {
            [void](Invoke-Git @('add', '--', $file))
            Write-Host "Refreshed: $file  (git reported it as changed, but its content is the same as git's copy)"
            continue
        }
    }
    $changed.Add("$code  $file")
}
if ($changed.Count) {
    Write-Host ''
    Write-Host 'These files were changed on this PC:'
    foreach ($c in $changed) { Write-Host "    $c" }
    Write-Host 'The folder was NOT updated and nothing was run. Nothing has been discarded.'
    Write-Host 'Send this message back.'
    exit 1
}

# ---- 2. update
$pull = Invoke-Git @('pull', '--ff-only')
foreach ($l in $pull.Output) { Write-Host "  $l" }
if ($pull.ExitCode -ne 0) {
    Write-Host ''
    Write-Host 'git pull did not succeed, so nothing was run. Send the lines above back.'
    exit 1
}
$now = Invoke-Git @('log', '--oneline', '-1')
Write-Host "Updated to: $($now.Output | Select-Object -First 1)"
Write-Host ''

# ---- 3. run, in a new PowerShell so that the scripts just received are the ones that run
$shell = if ($PSVersionTable.PSEdition -eq 'Desktop') { (Get-Process -Id $PID).Path } else { 'pwsh' }
& $shell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'Run-FirstBuild.ps1') @passThrough
exit $LASTEXITCODE
