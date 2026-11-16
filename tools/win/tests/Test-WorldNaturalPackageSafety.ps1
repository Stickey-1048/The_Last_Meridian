<# Refusal fixtures only: no compiler, game, manager or installed writes. #>
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$builder=Join-Path $PSScriptRoot '../Build-WorldNatural.ps1'
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
    $args=@{VanillaMaster=$master;PapyrusCompiler=$compiler;BaseSources=$base;ReviewedRuntime=$runtime}
    $outside=Join-Path ([IO.Path]::GetTempPath()) ('must-not-exist-'+[guid]::NewGuid().ToString('N'))
    Refuses { & $builder @args -OutputDirectory $outside } 'outside workspace output accepted'
    if (Test-Path $outside) { throw 'Outside directory was created.' };$checks++
    $occupied=Join-Path $root 'occupied';[void](New-Item -ItemType Directory $occupied);$sentinel=Join-Path $occupied 'keep.txt';Set-Content $sentinel 'owner content';$hash=(Get-FileHash $sentinel).Hash
    Refuses { & $builder @args -OutputDirectory $occupied } 'occupied output accepted'
    if ((Get-FileHash $sentinel).Hash -ne $hash) { throw 'Existing file changed.' };$checks++
    $new=Join-Path $root 'new-package'
    $reason=''
    try { & $builder @args -OutputDirectory $new } catch { $reason=$_.Exception.Message }
    if ($reason -notlike '*Reviewed runtime input must have exactly19 PEX files*') { throw "Normal new ancestry failed before intended input validation: $reason" };$checks++
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
} finally { Remove-Item -LiteralPath $root -Recurse -Force }
