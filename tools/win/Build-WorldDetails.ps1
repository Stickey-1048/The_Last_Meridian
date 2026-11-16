<# Build a verified workspace package only. Never writes to a game or manager. #>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$VanillaMaster,
    [Parameter(Mandatory)][string]$ReviewedRuntime,
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
$pins=Get-Content (Join-Path $PSScriptRoot 'world-details-artifact.json') -Raw | ConvertFrom-Json
if ($pins.schema -ne 1 -or @($pins.runtime.PSObject.Properties).Count -ne 19 -or @($pins.sourceTextSha256.PSObject.Properties).Count -ne 19) { throw 'Details requires the complete reviewed19 runtime/source manifest.' }
# These source digests describe normalized logical text (UTF8/LF, final newline
# retained), not compiler byte identity. Refuse mixing reviewed PEX with edits.
$sources=Join-Path $repo 'scripts/Source/User'
$names=@(Get-ChildItem -LiteralPath (Join-Path $sources 'TLM') -File -Filter '*.psc' | ForEach-Object {$_.Name})
if ($names.Count -ne 19 -or @(Compare-Object ($names | Sort-Object) ($pins.sourceTextSha256.PSObject.Properties.Name | Sort-Object) -CaseSensitive).Count) { throw 'Current source names differ from the reviewed19 scripts.' }
foreach ($item in $pins.sourceTextSha256.PSObject.Properties) {
    $text=[IO.File]::ReadAllText((Join-Path $sources ('TLM/'+$item.Name))).Replace("`r`n","`n").Replace("`r","`n")
    $sha=[Security.Cryptography.SHA256]::Create()
    try { $actual=[BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($text))).Replace('-','') } finally { $sha.Dispose() }
    if ($actual -cne $item.Value) { throw "Current source differs from reviewed logical source: $($item.Name)" }
}
if (@(Get-ChildItem -LiteralPath $ReviewedRuntime -File -Filter '*.pex').Count -ne 19) { throw 'Reviewed runtime input must have exactly19 PEX files.' }
foreach ($item in $pins.runtime.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $ReviewedRuntime $item.Name)).Hash -cne $item.Value) { throw "Reviewed runtime input pin mismatch: $($item.Name)" }
}
[void](New-Item -ItemType Directory -Force $output)
$plugin=Join-Path $output 'plugin';$world=Join-Path $output 'world';$bundle=Join-Path $output 'bundle'
[void](New-Item -ItemType Directory -Force $plugin,$bundle)
& dotnet run --project (Join-Path $repo 'tools/PluginBuilder') -- --out $plugin --fallout4-esm $VanillaMaster *> (Join-Path $output 'plugin-build.txt')
if ($LASTEXITCODE -ne 0) { throw 'Plugin source build failed; inspect plugin-build.txt.' }
Copy-Item -LiteralPath (Join-Path $plugin 'TheLastMeridian.esp') -Destination $bundle
& dotnet run --project (Join-Path $repo 'tools/WorldSliceBuilder') -- $VanillaMaster $world --story-source (Join-Path $bundle 'TheLastMeridian.esp') --natural --private-shelter-detail *> (Join-Path $output 'world-build.txt')
if ($LASTEXITCODE -ne 0) { throw 'Details world source build failed; inspect world-build.txt.' }
Copy-Item -LiteralPath (Join-Path $world 'TLMWorldSlice.esp') -Destination $bundle
foreach ($pair in @(@((Join-Path $bundle 'TheLastMeridian.esp'),$pins.masterSha256),@((Join-Path $bundle 'TLMWorldSlice.esp'),$pins.worldSha256))) {
    if ((Get-FileHash -LiteralPath $pair[0]).Hash -cne $pair[1]) { throw "Built plugin differs from reviewed pin: $($pair[0])" }
}
$packaged=Join-Path $bundle 'Scripts/TLM';[void](New-Item -ItemType Directory -Force $packaged)
foreach ($item in $pins.runtime.PSObject.Properties) {
    # No script changes: copy exact reviewed PEX; no Papyrus compiler is invoked.
    Copy-Item -LiteralPath (Join-Path $ReviewedRuntime $item.Name) -Destination $packaged
    if ((Get-FileHash -LiteralPath (Join-Path $packaged $item.Name)).Hash -cne $item.Value) { throw "Packaged reviewed runtime differs: $($item.Name)" }
}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'world-details-artifact.json') -Destination (Join-Path $output 'verified-manifest.json')
Write-Host "Workspace package verified: $bundle. No installed files changed; no Papyrus compile performed; Details native acceptance remains pending."
