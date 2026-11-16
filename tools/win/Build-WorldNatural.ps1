<# Build a verified workspace package only. Never writes to a game or manager. #>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$VanillaMaster,
    [Parameter(Mandatory)][string]$PapyrusCompiler,
    [Parameter(Mandatory)][string]$BaseSources,
    [Parameter(Mandatory)][string]$ReviewedRuntime,
    [Parameter(Mandatory)][string]$OutputDirectory
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$buildRoot=[IO.Path]::GetFullPath((Join-Path $repo 'build'))+[IO.Path]::DirectorySeparatorChar
$output=[IO.Path]::GetFullPath($OutputDirectory)
if (-not $output.StartsWith($buildRoot,[StringComparison]::OrdinalIgnoreCase)) { throw 'Package output must be a new directory under this checkout build folder.' }
if ((Test-Path -LiteralPath $output) -and ((Get-Item -LiteralPath $output) -isnot [IO.DirectoryInfo] -or @(Get-ChildItem -LiteralPath $output -Force).Count)) { throw 'Package output must be new or empty; existing content was left unchanged.' }
foreach ($file in @($VanillaMaster,$PapyrusCompiler)) { if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Required input absent: $file" } }
if (-not (Test-Path -LiteralPath (Join-Path $BaseSources 'Quest.psc') -PathType Leaf)) { throw 'Base Papyrus sources are missing.' }
$pins=Get-Content (Join-Path $PSScriptRoot 'world-natural-artifact.json') -Raw | ConvertFrom-Json
# These source digests describe normalized logical text (UTF8/LF, final newline
# retained), not compiler byte identity. Refuse mixing reviewed PEX with edits.
$sources=Join-Path $repo 'scripts/Source/User'
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
& dotnet run --project (Join-Path $repo 'tools/WorldSliceBuilder') -- $VanillaMaster $world --story-source (Join-Path $bundle 'TheLastMeridian.esp') --natural *> (Join-Path $output 'world-build.txt')
if ($LASTEXITCODE -ne 0) { throw 'Natural world source build failed; inspect world-build.txt.' }
Copy-Item -LiteralPath (Join-Path $world 'TLMWorldSlice.esp') -Destination $bundle
$scripts=Join-Path $output 'fresh-compile';[void](New-Item -ItemType Directory -Force $scripts)
$names=@(Get-ChildItem -LiteralPath (Join-Path $sources 'TLM') -Filter '*.psc' -File | Sort-Object Name)
if ($names.Count -ne 19) { throw 'Expected exactly19 source scripts.' }
function XmlEscape([string]$s) { [Security.SecurityElement]::Escape($s) }
$entries=($names | ForEach-Object { '<Script>TLM\'+$_.BaseName+'</Script>' }) -join ''
$xml='<PapyrusProject xmlns="PapyrusProject.xsd" Flags="Institute_Papyrus_Flags.flg" Output="'+(XmlEscape $scripts)+'" Optimize="false" Release="false"><Imports><Import>'+(XmlEscape $sources)+'</Import><Import>'+(XmlEscape $BaseSources)+'</Import></Imports><Scripts>'+$entries+'</Scripts></PapyrusProject>'
$project=Join-Path $output 'runtime.ppj';[IO.File]::WriteAllText($project,$xml)
& $PapyrusCompiler $project *> (Join-Path $output 'compile.txt')
if ($LASTEXITCODE -ne 0 -or (Get-Content (Join-Path $output 'compile.txt') -Raw) -notmatch '19 succeeded, 0 failed') { throw 'Actual19-script compilation failed; inspect compile.txt.' }
foreach ($pair in @(@((Join-Path $bundle 'TheLastMeridian.esp'),$pins.masterSha256),@((Join-Path $bundle 'TLMWorldSlice.esp'),$pins.worldSha256))) {
    if ((Get-FileHash -LiteralPath $pair[0]).Hash -cne $pair[1]) { throw "Built plugin differs from reviewed pin: $($pair[0])" }
}
$present=@(Get-ChildItem -LiteralPath (Join-Path $scripts 'TLM') -Filter '*.pex' -File)
if ($present.Count -ne 19) { throw 'Compiled bundle must contain exactly19 scripts.' }
$packaged=Join-Path $bundle 'Scripts/TLM';[void](New-Item -ItemType Directory -Force $packaged)
foreach ($item in $pins.runtime.PSObject.Properties) {
    # Compiler output embeds paths/time and may reorder string tables. Preserve
    # already reviewed exact PEX rather than pretend a new compile has its hash.
    Copy-Item -LiteralPath (Join-Path $ReviewedRuntime $item.Name) -Destination $packaged
    if ((Get-FileHash -LiteralPath (Join-Path $packaged $item.Name)).Hash -cne $item.Value) { throw "Packaged reviewed runtime differs: $($item.Name)" }
}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'world-natural-artifact.json') -Destination (Join-Path $output 'verified-manifest.json')
Write-Host "Workspace package verified: $bundle. No installed files changed; native composed acceptance remains pending."
