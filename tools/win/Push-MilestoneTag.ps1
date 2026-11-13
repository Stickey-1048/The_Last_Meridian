<#
.SYNOPSIS
  Creates the annotated git tag for a milestone on the commit that passed, with
  the text kept in docs\design\tags\<name>.txt, and pushes that one tag to
  GitHub.

.DESCRIPTION
  Why this exists: the cloud session that does the day-to-day work is allowed
  to push the branch but not tags, so a tag has to come from the owner's PC.

  What it does, in this order, stopping at the first thing that is not as
  expected:
    1. reads docs\design\tags\<name>.txt, which must exist and not be empty;
    2. checks that the commit is in this folder;
    3. asks GitHub whether the tag is already there. If it is and points at
       that commit, there is nothing to do. If it points anywhere else, it is
       left alone and the script stops;
    4. creates the tag here, with that text, unless a tag of that name is
       already here and points at that commit. A tag of that name that points
       anywhere else is left alone and the script stops;
    5. pushes that one tag (not with -NoPush);
    6. asks GitHub again what the tag points at, and prints it.

  Nothing else is pushed, no file is changed, and no branch is touched. The
  tag carries the name and e-mail git is configured with on this PC; both are
  published with it.

  Status: tested on Linux PowerShell 7 against scratch clones (new tag, tag
  already pushed, tag pointing elsewhere here and on the remote, missing or
  empty text, unknown commit, no identity, -NoPush). NOT YET RUN ON A REAL PC.

.PARAMETER Name
  The tag. Default: mq01-logic-proof.

.PARAMETER Commit
  The commit the tag goes on. Default: c1e6d48, the commit whose run of
  2026-11-12 passed all 62 scenarios (docs\design\VERIFY_LOG.md).

.PARAMETER NoPush
  Create the tag here and stop.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\win\Push-MilestoneTag.ps1
#>
param(
    [string]$Name = 'mq01-logic-proof',
    [string]$Commit = 'c1e6d48',
    [switch]$NoPush
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Tlm.psm1') -Force

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
function Invoke-Git([string[]]$arguments) { return Invoke-Native -Exe 'git' -Arguments (@('-C', $repo) + $arguments) }
function Stop-Here([string]$why, [string]$then = 'Nothing was pushed. Send this message back.') {
    Write-Host ''
    Write-Host "STOPPED: $why"
    Write-Host $then
    exit 1
}
function Get-FirstLine($result) { return "$(@($result.Output) | Select-Object -First 1)".Trim() }
function Show-Lines($lines) {
    # What git wrote. An empty line on its error stream comes through PowerShell as the name of a type.
    foreach ($l in @($lines)) { if ("$l" -ne 'System.Management.Automation.RemoteException') { Write-Host "  $l" } }
}

if ($Name -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]*$') { Stop-Here "'$Name' is not a tag name this script will use." }

$at = Invoke-Git @('log', '--oneline', '-1')
if (-not $at.Found) { Stop-Here 'git was not found. Install Git for Windows, then run this again.' }
if ($at.ExitCode -ne 0) { Stop-Here "this is not a git folder: $(Hide-UserFolder $repo)" }
Write-Host "Folder : $(Hide-UserFolder $repo)"
Write-Host "Tag    : $Name"

# ---- 1. the text
$textPath = Join-Path (Join-Path (Join-Path (Join-Path $repo 'docs') 'design') 'tags') "$Name.txt"
if (-not (Test-Path -LiteralPath $textPath)) {
    Stop-Here "the tag's text is not here: docs\design\tags\$Name.txt. Bring the folder up to date first (git pull --ff-only)."
}
$text = @(Get-Content -LiteralPath $textPath)
$wanted = @($text | ForEach-Object { "$_".TrimEnd() })
while ($wanted.Count -and $wanted[-1] -eq '') { $wanted = @($wanted | Select-Object -First ($wanted.Count - 1)) }
if (-not $wanted.Count -or $wanted[0] -eq '') { Stop-Here "docs\design\tags\$Name.txt is empty, or its first line is." }

# ---- 2. the commit
$full = Invoke-Git @('rev-parse', '--verify', '--quiet', "$Commit^{commit}")
if ($full.ExitCode -ne 0) {
    Stop-Here "commit $Commit is not in this folder. Bring the folder up to date first (git pull --ff-only)."
}
$sha = Get-FirstLine $full
$subject = Get-FirstLine (Invoke-Git @('log', '-1', '--format=%h %s', $sha))
Write-Host "Commit : $subject"

# ---- 3. what GitHub has
function Get-RemoteTag {
    $r = Invoke-Git @('ls-remote', '--tags', 'origin', "refs/tags/$Name", "refs/tags/$Name^{}")
    if ($r.ExitCode -ne 0) { return [pscustomobject]@{ Ok = $false; Lines = @($r.Output); Commit = $null; Exists = $false; Annotated = $false } }
    $object = $null; $peeled = $null
    foreach ($line in @($r.Output)) {
        if ("$line" -match '^([0-9a-f]{40})\s+refs/tags/(.+)$') {
            if ($Matches[2] -eq "$Name^{}") { $peeled = $Matches[1] }
            elseif ($Matches[2] -eq $Name) { $object = $Matches[1] }
        }
    }
    # An annotated tag is listed twice: the tag itself, and the commit it points at (the ^{} line).
    $commitOnRemote = if ($peeled) { $peeled } else { $object }
    return [pscustomobject]@{ Ok = $true; Lines = @($r.Output); Commit = $commitOnRemote; Exists = [bool]$object; Annotated = [bool]$peeled }
}
$remote = Get-RemoteTag
if (-not $remote.Ok) {
    Show-Lines $remote.Lines
    Stop-Here 'GitHub could not be asked about the tag (the lines above are what git said).'
}
if ($remote.Exists) {
    if ($remote.Commit -eq $sha) {
        Write-Host ''
        Write-Host "Already on GitHub: $Name -> $($sha.Substring(0, 7)). Nothing to do."
        exit 0
    }
    Stop-Here "GitHub already has a tag $Name, and it points at $($remote.Commit.Substring(0, 7)), not at $($sha.Substring(0, 7)). It was left alone."
}

# ---- 4. the tag here
$local = Invoke-Git @('rev-parse', '--verify', '--quiet', "refs/tags/$Name^{commit}")
if ($local.ExitCode -eq 0) {
    $localSha = Get-FirstLine $local
    if ($localSha -ne $sha) {
        Stop-Here "a tag $Name is already in this folder and points at $($localSha.Substring(0, 7)), not at $($sha.Substring(0, 7)). It was left alone. If it is a leftover, remove it with:  git tag -d $Name"
    }
    Write-Host "The tag is already in this folder and points at the right commit; it is used as it is."
} else {
    $made = Invoke-Git @('tag', '-a', $Name, $sha, '-F', $textPath)
    if ($made.ExitCode -ne 0) {
        Show-Lines $made.Output
        if (("$($made.Output -join ' ')") -match '(?i)tell me who you are|identity|user\.email|user\.name') {
            Write-Host ''
            Write-Host 'git does not know who is tagging. Give this folder a name and an e-mail, then run this again.'
            Write-Host 'Both are published with the tag; the no-reply address GitHub shows under Settings, Emails will do:'
            Write-Host '    git config user.name  "Your name on GitHub"'
            Write-Host '    git config user.email "12345678+yourname@users.noreply.github.com"'
        }
        Stop-Here 'the tag could not be created (the lines above are what git said).'
    }
    Write-Host 'Created the tag in this folder.'
}

# What the tag says, read back from git, must be the text in the file.
$body = Invoke-Git @('cat-file', '-p', "refs/tags/$Name")
$lines = @($body.Output)
$blank = -1
for ($i = 0; $i -lt $lines.Count; $i++) { if ("$($lines[$i])" -eq '') { $blank = $i; break } }
$got = @()
if ($blank -ge 0 -and $blank + 1 -lt $lines.Count) { $got = @($lines[($blank + 1)..($lines.Count - 1)] | ForEach-Object { "$_".TrimEnd() }) }
while ($got.Count -and $got[-1] -eq '') { $got = @($got | Select-Object -First ($got.Count - 1)) }
$annotated = [bool](@($lines | Where-Object { "$_" -match '^tagger ' }).Count)
if (-not $annotated) {
    Stop-Here "the tag $Name in this folder carries no text of its own (it is not an annotated tag). It was not pushed. If it is a leftover, remove it with:  git tag -d $Name"
}
if (($got -join "`n") -ne ($wanted -join "`n")) {
    Stop-Here "the tag $Name in this folder does not say what docs\design\tags\$Name.txt says. It was not pushed. If it is a leftover, remove it with:  git tag -d $Name"
}
Write-Host "Its text: $($wanted[0])"
Write-Host "          ($($wanted.Count) lines, the same as docs\design\tags\$Name.txt)"

if ($NoPush) {
    Write-Host ''
    Write-Host "-NoPush: the tag is in this folder only. To push it later:  git push origin refs/tags/$Name"
    exit 0
}

# ---- 5. push that one tag
Write-Host ''
Write-Host "Pushing the tag (the first push from this PC may open a GitHub sign-in window) ..."
$push = Invoke-Git @('push', 'origin', "refs/tags/$Name")
Show-Lines $push.Output
if ($push.ExitCode -ne 0) {
    Stop-Here 'the push did not succeed (the lines above are what git said). The tag is still in this folder; running this again will try the push again.'
}

# ---- 6. what GitHub has now
$remote = Get-RemoteTag
if (-not $remote.Ok -or -not $remote.Exists -or $remote.Commit -ne $sha) {
    Show-Lines $remote.Lines
    Stop-Here 'the push reported success, but GitHub does not show the tag on that commit.' 'Send this message back.'
}
Write-Host ''
Write-Host "DONE. On GitHub: $Name -> $subject"
Write-Host 'Send this message back, so that the record can say the tag is there.'
exit 0
