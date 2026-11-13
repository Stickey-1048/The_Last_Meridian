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

  Nothing else is pushed, no tracked file is changed, and no branch is touched.
  The tag carries the name and e-mail git is configured with on this PC; both
  are published with it.

  Whatever happens, the whole message is written to build\milestone-tag.txt
  and copied to the clipboard, like the other scripts' reports.

  Status: tested on Linux PowerShell 7 against scratch clones (new tag, tag
  already pushed, tag pointing elsewhere here and on the remote, missing or
  empty text, unknown commit, no identity, -NoPush, and started through
  Update-And-Run.ps1 -Tag). RAN ON THE OWNER'S PC under Windows PowerShell
  5.1: on 2026-11-12 as far as creating the tag, where it stopped as it
  should (git there had no name and e-mail), and on 2026-11-13 all the way:
  it created mq01-logic-proof on c1e6d48 and pushed it.

.PARAMETER Name
  The tag. Default: mq01-logic-proof.

.PARAMETER Commit
  The commit the tag goes on. Default: c1e6d48, the commit whose run of
  2026-11-12 passed all 62 scenarios (docs\design\VERIFY_LOG.md).

.PARAMETER NoPush
  Create the tag here and stop.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\win\Update-And-Run.ps1 -Tag
  The usual way: brings the folder up to date first, then runs this script.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\win\Push-MilestoneTag.ps1
#>
param(
    [string]$Name = 'mq01-logic-proof',
    [string]$Commit = 'c1e6d48',
    [switch]$NoPush,
    # Do not copy the message to the clipboard at the end.
    [switch]$NoClipboard
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Tlm.psm1') -Force

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

# Whatever happens, the whole message ends up in build\milestone-tag.txt and on
# the clipboard, as with the other scripts: run it, then paste.
$said = New-Object System.Collections.Generic.List[string]
function Say([string]$s = '') { $said.Add($s); Write-Host $s }
function Finish([int]$code) {
    $text = Hide-UserFolder ($said -join [Environment]::NewLine)
    try {
        $build = Join-Path $repo 'build'
        New-Item -ItemType Directory -Force -Path $build | Out-Null
        Set-Content -LiteralPath (Join-Path $build 'milestone-tag.txt') -Value $text -Encoding utf8
    } catch { }
    $copied = $false
    if (-not $NoClipboard -and (Get-Command Set-Clipboard -ErrorAction SilentlyContinue)) {
        try { Set-Clipboard -Value $text; $copied = $true } catch { }
    }
    Write-Host ''
    if ($copied) { Write-Host 'This message is on your clipboard. Click in the chat and press Ctrl+V to send it.' }
    else { Write-Host 'This message is also in build\milestone-tag.txt.' }
    exit $code
}
function Invoke-Git([string[]]$arguments) { return Invoke-Native -Exe 'git' -Arguments (@('-C', $repo) + $arguments) }
function Stop-Here([string]$why, [string]$then = 'Nothing was pushed. Send this message back.') {
    Say ''
    Say "STOPPED: $why"
    Say $then
    Finish 1
}
function Get-FirstLine($result) { return "$(@($result.Output) | Select-Object -First 1)".Trim() }
function Show-Lines($lines) {
    # What git wrote. An empty line on its error stream comes through PowerShell as the name of a type.
    # When git cannot work out who is tagging it names the Windows account and the PC; that is
    # left out, like the user folder everywhere else: this message is meant to be pasted.
    foreach ($l in @($lines)) {
        if ("$l" -eq 'System.Management.Automation.RemoteException') { continue }
        Say ("  $l" -replace "\(got '[^']*'\)", "(got the Windows account's name and the PC's)")
    }
}
function Get-RepositoryIdentity {
    # The name and GitHub no-reply address that most of this repository's own commits already
    # carry, if there is one: nothing new is published by tagging under it.
    $r = Invoke-Git @('log', '-n', '300', '--format=%an|%ae')
    if ($r.ExitCode -ne 0) { return $null }
    $best = @($r.Output | Where-Object { "$_" -match '\|[^|]+@users\.noreply\.github\.com$' } |
        Group-Object | Sort-Object Count -Descending | Select-Object -First 1)
    if (-not $best.Count) { return $null }
    $parts = "$($best[0].Name)".Split('|')
    if ($parts.Count -ne 2 -or -not $parts[0] -or -not $parts[1]) { return $null }
    return [pscustomobject]@{ Name = $parts[0]; Email = $parts[1] }
}

if ($Name -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]*$') { Stop-Here "'$Name' is not a tag name this script will use." }

$at = Invoke-Git @('log', '--oneline', '-1')
if (-not $at.Found) { Stop-Here 'git was not found. Install Git for Windows, then run this again.' }
if ($at.ExitCode -ne 0) { Stop-Here "this is not a git folder: $(Hide-UserFolder $repo)" }
Say "The Last Meridian: milestone tag   $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
Say "Folder : $(Hide-UserFolder $repo)"
Say "Tag    : $Name"

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
Say "Commit : $subject"

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
        Say ''
        Say "Already on GitHub: $Name -> $($sha.Substring(0, 7)). Nothing to do."
        Finish 0
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
    Say "The tag is already in this folder and points at the right commit; it is used as it is."
} else {
    $made = Invoke-Git @('tag', '-a', $Name, $sha, '-F', $textPath)
    if ($made.ExitCode -ne 0) {
        Show-Lines $made.Output
        if (("$($made.Output -join ' ')") -match '(?i)tell me who you are|identity|user\.email|user\.name') {
            Say ''
            Say 'git does not know who is tagging. Give this folder a name and an e-mail, then run this again.'
            Say 'Both are published with the tag. They are set for this folder only.'
            $known = Get-RepositoryIdentity
            if ($known) {
                Say 'These are the name and the GitHub no-reply address most of this repository''s commits already carry:'
                Say "    git config user.name  `"$($known.Name)`""
                Say "    git config user.email `"$($known.Email)`""
            } else {
                Say 'The no-reply address GitHub shows under Settings, Emails will do:'
                Say '    git config user.name  "Your name on GitHub"'
                Say '    git config user.email "12345678+yourname@users.noreply.github.com"'
            }
        }
        Stop-Here 'the tag could not be created (the lines above are what git said).'
    }
    Say 'Created the tag in this folder.'
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
Say "Its text: $($wanted[0])"
Say "          ($($wanted.Count) lines, the same as docs\design\tags\$Name.txt)"

if ($NoPush) {
    Say ''
    Say "-NoPush: the tag is in this folder only. To push it later:  git push origin refs/tags/$Name"
    Finish 0
}

# ---- 5. push that one tag
Say ''
Say "Pushing the tag (the first push from this PC may open a GitHub sign-in window) ..."
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
Say ''
Say "DONE. On GitHub: $Name -> $subject"
Say 'Send this message back, so that the record can say the tag is there.'
Finish 0
