<# Optional actual-master reproduction check. No installation or game launch. #>
param([Parameter(Mandatory)][string]$VanillaMaster,[Parameter(Mandatory)][string]$StorySource)
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$root=Join-Path $repo ('build/variant-check-'+[guid]::NewGuid().ToString('N'))
[void](New-Item -ItemType Directory $root)
$cases=@(
    @{Name='story';Flag=@();Manifest=(Join-Path $PSScriptRoot '../world-story-artifact.json')},
    @{Name='expanded';Flag=@('--expand');Manifest=(Join-Path $PSScriptRoot '../../WorldSliceBuilder/expanded-artifact.json')},
    @{Name='natural';Flag=@('--natural');Manifest=(Join-Path $PSScriptRoot '../world-natural-artifact.json')}
)
$results=@()
foreach ($case in $cases) {
    $dir=Join-Path $root $case.Name
    $argv=@('run','--project',(Join-Path $repo 'tools/WorldSliceBuilder'),'--',$VanillaMaster,$dir,'--story-source',$StorySource)+$case.Flag
    & dotnet @argv *> (Join-Path $root ($case.Name+'.txt'))
    if ($LASTEXITCODE -ne 0) { throw "World build failed: $($case.Name); inspect $root" }
    $pins=Get-Content $case.Manifest -Raw | ConvertFrom-Json
    $hash=(Get-FileHash -LiteralPath (Join-Path $dir 'TLMWorldSlice.esp')).Hash
    if ($hash -cne $pins.worldSha256) { throw "World build hash differs for $($case.Name): $hash" }
    $results += [pscustomobject]@{Variant=$case.Name;Hash=$hash;MatchesFixedManifest=$true}
}
$results | ConvertTo-Json | Set-Content (Join-Path $root 'results.json')
Write-Host "All3 actual-master world builds match fixed pins. Workspace receipt: $root. No runtime/native play acceptance."
