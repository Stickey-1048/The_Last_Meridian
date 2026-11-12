<#
.SYNOPSIS
  Collects what the game wrote during an in-game test and puts it on the clipboard.

.DESCRIPTION
  READ-ONLY. After running the self-test in the game (console:
  cqf TLM_Core RunSelfTest), this gathers:
    - the self-test's own log   Documents\My Games\Fallout4\Logs\Script\User\TLM.0.log
    - from the game's script log (Papyrus.0.log): its first lines, and every
      line that mentions this project's scripts
  into build\test-results.txt, and copies that text to the clipboard.

  Both logs only exist if Papyrus logging was on for the session; the test
  profile made by Install-Dev.ps1 -CreateProfile turns it on.
  The Windows user folder name is replaced with %USERPROFILE%.

  Status: tested on Linux PowerShell 7 against stand-in log files only.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\win\Get-TestResults.ps1
#>
[CmdletBinding()]
param(
    [string]$DocumentsRoot,
    [switch]$NoClipboard
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Tlm.psm1') -Force

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$build = Join-Path $repo 'build'
New-Item -ItemType Directory -Force -Path $build | Out-Null
if (-not $DocumentsRoot) { $DocumentsRoot = [Environment]::GetFolderPath('MyDocuments') }
$scriptLogs = Join-Path (Join-Path (Join-Path (Join-Path $DocumentsRoot 'My Games') 'Fallout4') 'Logs') 'Script'
$userLog = Join-Path (Join-Path $scriptLogs 'User') 'TLM.0.log'
$papyrusLog = Join-Path $scriptLogs 'Papyrus.0.log'

$out = New-Object System.Collections.Generic.List[string]
function Say([string]$s = '') { $out.Add($s) }
function Get-FileNote([string]$path) {
    $f = Get-Item -LiteralPath $path
    $age = [int]((Get-Date) - $f.LastWriteTime).TotalMinutes
    return "$path  (written $($f.LastWriteTime.ToString('yyyy-MM-dd HH:mm')), $age minute(s) ago, $($f.Length) bytes)"
}

Say "The Last Meridian: in-game test results   $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
$head = Invoke-Native -Exe 'git' -Arguments @('-C', $repo, 'log', '--oneline', '-1')
if ($head.Found -and $head.ExitCode -eq 0) { Say "Repository commit: $($head.Output | Select-Object -First 1)" }
$manifestPath = Join-Path $build 'install-manifest.json'
if (Test-Path -LiteralPath $manifestPath) {
    $m = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    Say "Installed build  : $($m.Root)  ($($m.Installed))"
} else {
    Say 'Installed build  : no install manifest (Install-Dev.ps1 has not been run from this folder)'
}

Say ''
Say '== Self-test log (TLM.0.log) =='
if (Test-Path -LiteralPath $userLog) {
    Say (Get-FileNote $userLog)
    foreach ($l in Get-Content -LiteralPath $userLog) { Say "  $l" }
} else {
    Say "Not found: $userLog"
    Say 'Either the self-test did not run, or Papyrus logging was off for that session.'
}

Say ''
Say '== Game script log (Papyrus.0.log) =='
if (Test-Path -LiteralPath $papyrusLog) {
    Say (Get-FileNote $papyrusLog)
    $lines = @(Get-Content -LiteralPath $papyrusLog)
    Say "Lines in all: $($lines.Count)"
    Say '-- first 12 lines --'
    foreach ($l in ($lines | Select-Object -First 12)) { Say "  $l" }
    $ours = @($lines | Where-Object { $_ -match 'TLM' })
    Say "-- lines mentioning this project: $($ours.Count)$(if ($ours.Count -gt 250) { ' (first 250 shown)' }) --"
    foreach ($l in ($ours | Select-Object -First 250)) { Say "  $l" }
} else {
    Say "Not found: $papyrusLog"
    Say 'Papyrus logging was off, or the game has not been run with it on.'
}

$text = Hide-UserFolder ($out -join [Environment]::NewLine)
$resultPath = Join-Path $build 'test-results.txt'
Set-Content -LiteralPath $resultPath -Value $text -Encoding utf8
Write-Host $text
Write-Host ''
Write-Host "Written to: $resultPath"
$copied = $false
if (-not $NoClipboard -and (Get-Command Set-Clipboard -ErrorAction SilentlyContinue)) {
    try { Set-Clipboard -Value $text; $copied = $true } catch { }
}
if ($copied) { Write-Host 'It is also on your clipboard. Click in the chat and press Ctrl+V to send it.' }
