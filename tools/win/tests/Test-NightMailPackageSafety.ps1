<# Source-package refusal checks. Uses dummy inputs; no licensed data, build, install or compiler.
   Copies only the verifier's declared inputs into a new workspace folder. #>
[CmdletBinding()]
param([Parameter(Mandatory)][string]$Python)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$fixture=Join-Path $repo ('build/night-mail-package-safety-'+[Guid]::NewGuid().ToString('N'))
$copy=Join-Path $fixture 'source'
[void](New-Item -ItemType Directory -Path $copy)
$manifest=Get-Content -LiteralPath (Join-Path $repo 'tools/win/night-mail-story-candidate.json') -Raw | ConvertFrom-Json
$names=@($manifest.sourceFilesTextSha256.PSObject.Properties.Name)+@($manifest.frozenTextSha256.PSObject.Properties.Name)+@('tools/win/night-mail-story-candidate.json','.gitattributes','tools/greenwater_story_candidate.py')
foreach($name in ($names | Sort-Object -Unique)) {
    $target=Join-Path $copy $name
    [void](New-Item -ItemType Directory -Force ([IO.Path]::GetDirectoryName($target)))
    Copy-Item -LiteralPath (Join-Path $repo $name) -Destination $target
}
$master=Join-Path $fixture 'dummy.esm';$compileLog=Join-Path $fixture 'dummy-compile.txt'
[IO.File]::WriteAllText($master,'not a game master')
[IO.File]::WriteAllText($compileLog,'not a compile')
$reviewed=Join-Path $fixture 'reviewed';$fresh=Join-Path $fixture 'fresh'
[void](New-Item -ItemType Directory -Path $reviewed,$fresh)
$packager=Join-Path $copy 'tools/win/Build-NightMail.ps1'
function Refused([string]$Output,[string]$Expected,[string]$Interpreter=$Python) {
    $reason=''
    try { & $packager -VanillaMaster $master -ReviewedRuntime $reviewed -FreshCompile $fresh -CompileLog $compileLog -OutputDirectory $Output -Python $Interpreter }
    catch { $reason=$_.Exception.Message }
    if ($reason -notlike $Expected) { throw "Wrong refusal: $reason; expected $Expected" }
    if (Test-Path -LiteralPath $Output) { throw "Refused packager created output: $Output" }
}
Refused (Join-Path $fixture 'outside') '*must be a new directory under this checkout build folder*'
Refused (Join-Path $copy 'build/missing-python') '*Python interpreter not found*' 'no-such-night-mail-python'
Refused (Join-Path $copy 'build/reviewed-absent') '*Reviewed runtime input absent:*'
$occupied=Join-Path $copy 'build/occupied'
[void](New-Item -ItemType Directory -Force $occupied)
$keep=Join-Path $occupied 'keep.txt';[IO.File]::WriteAllText($keep,'owner content')
$reason=''
try { & $packager -VanillaMaster $master -ReviewedRuntime $reviewed -FreshCompile $fresh -CompileLog $compileLog -OutputDirectory $occupied -Python $Python }
catch { $reason=$_.Exception.Message }
if ($reason -notlike '*must be wholly new*' -or [IO.File]::ReadAllText($keep) -cne 'owner content') { throw "Occupied output refusal failed: $reason" }
$changed=Join-Path $copy 'tools/PluginBuilder/SpecNightMail.cs'
[IO.File]::AppendAllText($changed,"`n// refusal mutation`n")
Refused (Join-Path $copy 'build/damaged-source') '*candidate source verifier refused this checkout*sourceFilesTextSha256*'
Write-Host 'Night Mail package safety: five exact refusals passed; no package output created, existing content preserved, no build, no licensed inputs.'
