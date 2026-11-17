<#
.SYNOPSIS
  Builds a workspace package of the GREENWATER-STORY-001 candidate and measures it.
  Never writes to a game or a mod manager.

.DESCRIPTION
  UNTESTED SCAFFOLDING. This script was written where no PowerShell and no
  game master exist. It has not been run, not even parsed by PowerShell. Read
  it before running it. Its checks of the output folder are the lines of
  Build-WorldDetails.ps1, which root has run; the rest is new.

  It is the opt-in build of this candidate and of nothing else. The Details,
  Natural and story packagers and launchers are unchanged and refuse this
  checkout's source, as they should; this script reads none of their pins as
  a pin of its own output.

  What it takes:
    -VanillaMaster    the game's own Fallout4.esm (read only);
    -ReviewedRuntime  a folder holding the reviewed compiled scripts of the
                      Details runtime (the 19 that world-details-artifact.json
                      pins). 17 of them are used, each after its bytes have
                      been checked against that pin;
    -FreshCompile     a folder holding all 23 scripts of THIS checkout compiled
                      afresh by the game's Papyrus compiler (for example the
                      output of tools\win\Build-Scripts.ps1). Keep the
                      compiler's log with the build receipt. This script does
                      not run the compiler;
    -OutputDirectory  a folder that does not exist yet, under this checkout's
                      build folder.

  What it does: checks that the checkout is the source of
  greenwater-story-candidate.json (23 scripts by text); builds the plugin and
  the exterior from source against the master; puts into bundle\Scripts\TLM
  exactly 23 files: the 17 reviewed ones byte for byte, and the 6 that the
  manifest lists under runtimeSelection.freshlyCompiled from -FreshCompile;
  writes measured.json.

  What it does NOT do: compare anything it built with a pin. No pin of this
  candidate's plugin, exterior or six fresh scripts exists. measured.json is a
  measurement for a build receipt. It verifies nothing, and nothing built by
  this script is accepted by being built.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$VanillaMaster,
    [Parameter(Mandatory)][string]$ReviewedRuntime,
    [Parameter(Mandatory)][string]$FreshCompile,
    [Parameter(Mandatory)][string]$OutputDirectory
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$buildRoot=[IO.Path]::GetFullPath((Join-Path $repo 'build'))+[IO.Path]::DirectorySeparatorChar
$output=[IO.Path]::GetFullPath($OutputDirectory)
if (-not $output.StartsWith($buildRoot,[StringComparison]::OrdinalIgnoreCase)) { throw 'Package output must be a new directory under this checkout build folder.' }
# Inspect every existing component without creating anything. A lexical prefix
# alone does not contain writes when an ancestor is a junction/symlink. Refuse
# all reparse points, including inside the checkout and above it; no resolution
# or redirection is authorized. An existing empty output is also not ours.
$cursor=$output
while ($cursor) {
    $entry=$null
    try { $entry=Get-Item -LiteralPath $cursor -Force -ErrorAction Stop }
    catch [System.Management.Automation.ItemNotFoundException] { $entry=$null }
    catch { throw "Cannot inspect package output ancestry; no writes allowed: $cursor. $($_.Exception.Message)" }
    if ($null -ne $entry) {
        if (($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Package output ancestry contains a reparse point; left unchanged: $cursor" }
        if ($cursor -ceq $output) { throw 'Package output must be wholly new; even an existing empty directory is left unchanged.' }
        if (-not $entry.PSIsContainer) { throw "Package output ancestor is not a directory: $cursor" }
    }
    $parent=[IO.Path]::GetDirectoryName($cursor.TrimEnd([IO.Path]::DirectorySeparatorChar))
    if (-not $parent -or $parent -ceq $cursor) { break }
    $cursor=$parent
}
foreach ($file in @($VanillaMaster)) { if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Required input absent: $file" } }
foreach ($folder in @($ReviewedRuntime,$FreshCompile)) { if (-not (Test-Path -LiteralPath $folder -PathType Container)) { throw "Required input folder absent: $folder" } }

function Get-TextSha256([string]$Path) {
    # A source's digest: its UTF-8 text with every line end made LF. Not a digest of anything compiled.
    $text=[IO.File]::ReadAllText($Path).Replace("`r`n","`n").Replace("`r","`n")
    $sha=[Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($text))).Replace('-','') } finally { $sha.Dispose() }
}

# This candidate's own manifest, and no other.
$manifestPath=Join-Path $PSScriptRoot 'greenwater-story-candidate.json'
$candidate=Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$reviewed=@($candidate.runtimeSelection.reusedReviewedPex.PSObject.Properties)
$fresh=@($candidate.runtimeSelection.freshlyCompiled)
$sourcePins=@($candidate.sourceTextSha256.PSObject.Properties)
if ($candidate.schema -ne 1 -or $candidate.scripts -ne 23 -or $sourcePins.Count -ne 23 -or $reviewed.Count -ne 17 -or $fresh.Count -ne 6) { throw 'The Greenwater candidate manifest is not 23 scripts: 17 reviewed and 6 fresh.' }
$expected=@($reviewed | ForEach-Object {$_.Name}) + $fresh
if (@($expected | Sort-Object -Unique).Count -ne 23) { throw 'The manifest names a compiled script twice.' }
foreach ($name in $expected) { if (-not ($candidate.sourceTextSha256.PSObject.Properties.Name -ccontains ($name -replace '\.pex$','.psc'))) { throw "The manifest selects a compiled script it names no source for: $name" } }

# The checkout is the manifest's source: the same 23 names, the same text.
$sources=Join-Path $repo 'scripts/Source/User'
$names=@(Get-ChildItem -LiteralPath (Join-Path $sources 'TLM') -File -Filter '*.psc' | ForEach-Object {$_.Name})
if ($names.Count -ne 23 -or @(Compare-Object ($names | Sort-Object) ($sourcePins | ForEach-Object {$_.Name} | Sort-Object) -CaseSensitive).Count) { throw 'Current source names differ from the 23 scripts of the Greenwater candidate.' }
foreach ($item in $sourcePins) {
    if ((Get-TextSha256 (Join-Path $sources ('TLM/'+$item.Name))) -cne $item.Value) { throw "Current source differs from the Greenwater candidate's source: $($item.Name)" }
}

# The 17 reviewed compiled scripts: each one's source is still the reviewed text, and its bytes are the reviewed bytes.
$details=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'world-details-artifact.json') -Raw | ConvertFrom-Json
foreach ($item in $reviewed) {
    $source=$item.Name -replace '\.pex$','.psc'
    if ($details.runtime.($item.Name) -cne $item.Value) { throw "Not the Details runtime's reviewed file: $($item.Name)" }
    if ($details.sourceTextSha256.$source -cne $candidate.sourceTextSha256.$source) { throw "A reviewed compiled script is selected for a source that is not the reviewed text: $source" }
    $file=Join-Path $ReviewedRuntime $item.Name
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Reviewed runtime input absent: $($item.Name)" }
    if ((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash -cne $item.Value) { throw "Reviewed runtime input pin mismatch: $($item.Name)" }
}
# The fresh compile: all 23 of this checkout, and nothing else. It is the proof that the source compiles.
$compiled=@(Get-ChildItem -LiteralPath $FreshCompile -File -Filter '*.pex' | ForEach-Object {$_.Name})
if ($compiled.Count -ne 23 -or @(Compare-Object ($compiled | Sort-Object) ($expected | Sort-Object) -CaseSensitive).Count) { throw 'The fresh compile must hold exactly the 23 compiled scripts of this checkout.' }

[void](New-Item -ItemType Directory -Force $output)
$plugin=Join-Path $output 'plugin';$world=Join-Path $output 'world';$bundle=Join-Path $output 'bundle'
[void](New-Item -ItemType Directory -Force $plugin,$bundle)
& dotnet run --project (Join-Path $repo 'tools/PluginBuilder') -- --out $plugin --fallout4-esm $VanillaMaster *> (Join-Path $output 'plugin-build.txt')
if ($LASTEXITCODE -ne 0) { throw 'Plugin source build failed; inspect plugin-build.txt.' }
Copy-Item -LiteralPath (Join-Path $plugin 'TheLastMeridian.esp') -Destination $bundle
& dotnet run --project (Join-Path $repo 'tools/WorldSliceBuilder') -- $VanillaMaster $world --story-source (Join-Path $bundle 'TheLastMeridian.esp') --natural --private-shelter-detail *> (Join-Path $output 'world-build.txt')
if ($LASTEXITCODE -ne 0) { throw 'World source build failed; inspect world-build.txt.' }
Copy-Item -LiteralPath (Join-Path $world 'TLMWorldSlice.esp') -Destination $bundle

$packaged=Join-Path $bundle 'Scripts/TLM';[void](New-Item -ItemType Directory -Force $packaged)
foreach ($item in $reviewed) {
    # Unchanged reviewed source: the exact reviewed file, never the fresh compile's.
    Copy-Item -LiteralPath (Join-Path $ReviewedRuntime $item.Name) -Destination $packaged
    if ((Get-FileHash -LiteralPath (Join-Path $packaged $item.Name) -Algorithm SHA256).Hash -cne $item.Value) { throw "Packaged reviewed runtime differs: $($item.Name)" }
}
foreach ($name in $fresh) {
    # Changed or new source, and MercyBriefing: from the fresh compile, never an earlier compiled file.
    Copy-Item -LiteralPath (Join-Path $FreshCompile $name) -Destination $packaged
    if ((Get-FileHash -LiteralPath (Join-Path $packaged $name) -Algorithm SHA256).Hash -cne (Get-FileHash -LiteralPath (Join-Path $FreshCompile $name) -Algorithm SHA256).Hash) { throw "Packaged fresh script differs from the fresh compile: $name" }
}
if (@(Get-ChildItem -LiteralPath $packaged -File).Count -ne 23) { throw 'The bundle does not hold exactly 23 compiled scripts.' }

# Measured, not verified: there is no pin of this candidate's plugin, exterior or fresh scripts to verify against.
$runtime=[ordered]@{}
foreach ($name in ($expected | Sort-Object)) { $runtime[$name]=(Get-FileHash -LiteralPath (Join-Path $packaged $name) -Algorithm SHA256).Hash }
$compiledDigests=[ordered]@{}
foreach ($name in ($expected | Sort-Object)) { $compiledDigests[$name]=(Get-FileHash -LiteralPath (Join-Path $FreshCompile $name) -Algorithm SHA256).Hash }
$measured=[ordered]@{
    what='MEASURED, NOT VERIFIED. Digests of what this run built and bundled, for a build receipt. No pin of this candidate exists, and none is created here. For the runtime manifest digest in the manifest''s own formula, and the check of the selection, run: python tools/greenwater_story_candidate.py measure <bundle> --fresh-compile <folder>'
    candidate=$candidate.candidate
    masterSha256=(Get-FileHash -LiteralPath (Join-Path $bundle 'TheLastMeridian.esp') -Algorithm SHA256).Hash
    worldSha256=(Get-FileHash -LiteralPath (Join-Path $bundle 'TLMWorldSlice.esp') -Algorithm SHA256).Hash
    runtime=$runtime
    reusedAsReviewed=@($reviewed | ForEach-Object {$_.Name})
    freshlyCompiled=$fresh
    freshCompile=$compiledDigests
}
[IO.File]::WriteAllText((Join-Path $output 'measured.json'),($measured | ConvertTo-Json -Depth 5),(New-Object Text.UTF8Encoding $false))
Copy-Item -LiteralPath $manifestPath -Destination (Join-Path $output 'candidate-manifest.json')
Write-Host "Greenwater candidate workspace package built and MEASURED (not verified against any pin; none exists): $bundle. No installed files changed; no Papyrus compile performed by this script; the build read-back, the compile log and native acceptance of every branch remain pending."
