<#
.SYNOPSIS
  Compiles the project's Papyrus sources with the game's own compiler.

.DESCRIPTION
  Writes build\TLM.ppj (a Papyrus project) and runs
  "<game>\Papyrus Compiler\PapyrusCompiler.exe" on it. Output goes to
  build\Scripts inside the repository, NOT into the game folder; use
  Install-Dev.ps1 to copy it in.

  The only thing this script can change in the game folder is extracting
  Base.zip (the game's own script sources) in place, and only with -ExtractBase.

  Status: the wiring was tested with a stand-in compiler. It has not yet been
  run against the real PapyrusCompiler.exe.

.EXAMPLE
  pwsh tools/win/Build-Scripts.ps1
  pwsh tools/win/Build-Scripts.ps1 -GameRoot 'C:\Program Files (x86)\Steam\steamapps\common\Fallout 4' -ExtractBase
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$GameRoot,
    [switch]$ExtractBase,
    [switch]$Release,
    [string]$SteamRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Tlm.psm1') -Force

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$root = Select-DevInstall -GameRoot $GameRoot -SteamRoot $SteamRoot
$compiler = Join-Path (Join-Path $root 'Papyrus Compiler') 'PapyrusCompiler.exe'
if (-not (Test-Path -LiteralPath $compiler)) { throw "Papyrus compiler not found: $compiler (install the Creation Kit)" }

$gameSource = Join-Path (Join-Path (Join-Path $root 'Data') 'Scripts') 'Source'
$base = Join-Path $gameSource 'Base'
$zip = Join-Path $base 'Base.zip'
$havePsc = (Test-Path -LiteralPath $base) -and @(Get-ChildItem -LiteralPath $base -Filter '*.psc' -File).Count -gt 0
if (-not $havePsc) {
    if ($ExtractBase -and (Test-Path -LiteralPath $zip)) {
        if ($PSCmdlet.ShouldProcess($base, 'Extract Base.zip (the game''s script sources) in place')) {
            Expand-Archive -LiteralPath $zip -DestinationPath $base -Force
        }
    } elseif (Test-Path -LiteralPath $zip) {
        throw "Base script sources are still zipped at $zip. Re-run with -ExtractBase to extract them in place."
    } else {
        throw "Base script sources not found under $base. They ship with the Creation Kit."
    }
}

$srcRoot = Join-Path (Join-Path (Join-Path $repo 'scripts') 'Source') 'User'
$scripts = @(Get-ChildItem -LiteralPath (Join-Path $srcRoot 'TLM') -Filter '*.psc' -File | Sort-Object Name)
if ($scripts.Count -eq 0) { throw "No .psc files under $srcRoot\TLM" }

$outDir = Join-Path (Join-Path $repo 'build') 'Scripts'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$imports = @($srcRoot)
$gameUser = Join-Path $gameSource 'User'
if (Test-Path -LiteralPath $gameUser) { $imports += $gameUser }
$imports += $base

function Xml([string]$s) { [System.Security.SecurityElement]::Escape($s) }
$rel = if ($Release) { 'true' } else { 'false' }
$ppj = New-Object System.Text.StringBuilder
[void]$ppj.AppendLine("<?xml version='1.0'?>")
[void]$ppj.AppendLine("<PapyrusProject xmlns=`"PapyrusProject.xsd`" Flags=`"Institute_Papyrus_Flags.flg`" Output=`"$(Xml $outDir)`" Optimize=`"$rel`" Release=`"$rel`">")
[void]$ppj.AppendLine('  <Imports>')
foreach ($i in $imports) { [void]$ppj.AppendLine("    <Import>$(Xml $i)</Import>") }
[void]$ppj.AppendLine('  </Imports>')
[void]$ppj.AppendLine('  <Scripts>')
foreach ($s in $scripts) { [void]$ppj.AppendLine("    <Script>TLM\$($s.BaseName)</Script>") }
[void]$ppj.AppendLine('  </Scripts>')
[void]$ppj.AppendLine('</PapyrusProject>')
$ppjPath = Join-Path (Join-Path $repo 'build') 'TLM.ppj'
Set-Content -LiteralPath $ppjPath -Value $ppj.ToString() -Encoding utf8

Write-Host "Compiler : $compiler"
Write-Host "Project  : $ppjPath ($($scripts.Count) scripts)"
$log = Join-Path (Join-Path $repo 'build') 'papyrus-compile.log'
& $compiler $ppjPath 2>&1 | Tee-Object -FilePath $log
$code = $LASTEXITCODE

$pex = @(Get-ChildItem -LiteralPath $outDir -Recurse -Filter '*.pex' -File -ErrorAction SilentlyContinue)
Write-Host ''
Write-Host "Compiler exit code: $code; .pex files produced: $($pex.Count) of $($scripts.Count); log: $log"
if ($code -ne 0 -or $pex.Count -lt $scripts.Count) {
    Write-Error 'Compilation FAILED. Fix the errors in the log; do not install.'
    exit 1
}
Write-Host 'Compilation succeeded. This proves the scripts compile, not that they behave correctly in the game.'
