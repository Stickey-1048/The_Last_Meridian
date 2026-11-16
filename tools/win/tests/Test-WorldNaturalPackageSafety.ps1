<# Refusal fixtures only: no compiler, game, manager or installed writes. #>
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$builder=Join-Path $PSScriptRoot '../Build-WorldNatural.ps1'
$root=Join-Path $repo ('build/package-safety-'+[guid]::NewGuid().ToString('N'))
[void](New-Item -ItemType Directory $root)
$checks=0
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
    Refuses { & $builder @args -OutputDirectory $new } 'missing reviewed runtime accepted'
    if (Test-Path $new) { throw 'Refused package created output before validating runtime.' };$checks++
    if ((Get-Content $master -Raw).Trim() -ne 'input sentinel') { throw 'Input master changed.' };$checks++
    Write-Host "$checks package refusal checks passed; no compiler/game/install execution."
} finally { Remove-Item -LiteralPath $root -Recurse -Force }
