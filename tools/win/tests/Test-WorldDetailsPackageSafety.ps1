<# Refusal fixtures only: no compiler, game, manager or installed writes. #>
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$builder=Join-Path $PSScriptRoot '../Build-WorldDetails.ps1'
$root=Join-Path $repo ('build/package-safety-'+[guid]::NewGuid().ToString('N'))
[void](New-Item -ItemType Directory $root)
$checks=0
$packageFixture=@{Reparse='';Unreadable=''}
# Harmless metadata mocks only. No real junction/symlink creation is attempted.
# The actual builder's Get-Item calls resolve this parent-scope function.
function Get-Item {
    [CmdletBinding()]param([string]$LiteralPath,[switch]$Force)
    if ($LiteralPath -ceq $packageFixture.Unreadable) { throw 'fixture metadata unreadable' }
    $entry=Microsoft.PowerShell.Management\Get-Item -LiteralPath $LiteralPath -Force:$Force -ErrorAction Stop
    if ($LiteralPath -ceq $packageFixture.Reparse) {
        return [pscustomobject]@{Attributes=([IO.FileAttributes]::Directory -bor [IO.FileAttributes]::ReparsePoint);PSIsContainer=$true;FullName=$entry.FullName}
    }
    $entry
}
Set-Item Function:\Get-Item -Value ${function:Get-Item}.GetNewClosure()
function Refuses([scriptblock]$action,[string]$reason) { $failed=$false;try { & $action } catch { $failed=$true };if (-not $failed) { throw $reason };$script:checks++ }
try {
    $master=Join-Path $root 'Fallout4.esm';$compiler=Join-Path $root 'never-run.exe';$base=Join-Path $root 'base';$runtime=Join-Path $root 'runtime'
    [void](New-Item -ItemType Directory $base,$runtime)
    Set-Content $master 'input sentinel';Set-Content $compiler 'fixture only; never executable';Set-Content (Join-Path $base 'Quest.psc') 'fixture'
    $args=@{VanillaMaster=$master;ReviewedRuntime=$runtime}
    $outside=Join-Path ([IO.Path]::GetTempPath()) ('must-not-exist-'+[guid]::NewGuid().ToString('N'))
    Refuses { & $builder @args -OutputDirectory $outside } 'outside workspace output accepted'
    if (Test-Path $outside) { throw 'Outside directory was created.' };$checks++
    $occupied=Join-Path $root 'occupied';[void](New-Item -ItemType Directory $occupied);$sentinel=Join-Path $occupied 'keep.txt';Set-Content $sentinel 'owner content';$hash=(Get-FileHash $sentinel).Hash
    Refuses { & $builder @args -OutputDirectory $occupied } 'occupied output accepted'
    if ((Get-FileHash $sentinel).Hash -ne $hash) { throw 'Existing file changed.' };$checks++
    $new=Join-Path $root 'new-package'
    $reason=''
    try { & $builder @args -OutputDirectory $new } catch { $reason=$_.Exception.Message }
    # ACT1-RUNTIME-001 candidate checkout: the runtime source here is no longer the reviewed19 (Act1Walk changed,
    # MercyBriefing added). This pinned packager must refuse it at its own frozen-source guard, before it looks at
    # any runtime input and without creating output. The guard and the pins are unchanged; the immutable b280
    # checkout keeps the earlier expectation (the19-PEX check is reached) and still builds the old package.
    if ($reason -notlike '*Current source names differ from the reviewed19 scripts*') { throw "Pinned packager did not refuse the changed candidate source at its frozen-source guard: $reason" };$checks++
    if (Test-Path $new) { throw 'Refused package created output before validating runtime.' };$checks++
    if ((Get-Content $master -Raw).Trim() -ne 'input sentinel') { throw 'Input master changed.' };$checks++
    $empty=Join-Path $root 'empty';[void](New-Item -ItemType Directory $empty)
    Refuses { & $builder @args -OutputDirectory $empty } 'existing empty output accepted'
    if (@(Get-ChildItem -LiteralPath $empty -Force).Count) { throw 'Empty existing directory changed.' };$checks++
    foreach ($mode in @('ancestor-reparse','output-reparse','unreadable')) {
        $target=$new
        if ($mode -eq 'ancestor-reparse') { $packageFixture.Reparse=$root }
        if ($mode -eq 'output-reparse') { $packageFixture.Reparse=$empty;$target=$empty }
        if ($mode -eq 'unreadable') { $packageFixture.Unreadable=$root }
        $reason=''
        try { & $builder @args -OutputDirectory $target } catch { $reason=$_.Exception.Message }
        $expected=if ($mode -eq 'unreadable') { 'Cannot inspect package output ancestry' } else { 'contains a reparse point' }
        if ($reason -notlike "*$expected*") { throw "Wrong refusal for $mode : $reason" };$checks++
        if ((Test-Path $new) -or (Get-FileHash $sentinel).Hash -ne $hash -or @(Get-ChildItem -LiteralPath $empty -Force).Count) { throw "Refusal changed files: $mode" };$checks++
        $packageFixture.Reparse='';$packageFixture.Unreadable=''
    }
    Write-Host "$checks package refusal checks passed; no compiler/game/install execution."
} finally { $target=[IO.Path]::GetFullPath($root);if (-not $target.StartsWith(([IO.Path]::GetFullPath($repo)+[IO.Path]::DirectorySeparatorChar),[StringComparison]::OrdinalIgnoreCase)) { throw 'Fixture cleanup escaped checkout.' };Remove-Item -LiteralPath $target -Recurse -Force }
