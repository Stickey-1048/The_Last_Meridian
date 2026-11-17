<#
  Refusal fixtures for tools/win/Build-Greenwater.ps1 only: no compiler, no game, no manager, no build and no
  installed writes.

  UNRUN WHERE IT WAS WRITTEN. No PowerShell exists in the environment this file was written in. It has not been
  run or parsed. Running it in Windows PowerShell 5.1 and in PowerShell 7 is root's, and until then nothing here
  counts as a pass.

  What it tries: the packager, run on a COPY of the files its source check reads (under this checkout's build
  folder, removed afterwards; the checkout itself is never edited), must
    - go past its source checks on the unchanged copy and stop at the first missing reviewed compiled script;
    - refuse, by the candidate's full source verifier and for the stated reason, a copy in which a builder source,
      the id file, a document's text or a frozen earlier packager was changed;
    - refuse when no Python interpreter can be found;
    - still refuse an output folder outside the build folder, one that exists with content, and one that exists
      empty;
  and in every case create no output folder and never reach dotnet. A refusal for any other reason is a failure
  of this fixture: no exception is accepted without its text.

  -Python: the interpreter to hand to the packager (a command name or a full path). Needs Python 3.
#>
param([string]$Python='python')
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$root=Join-Path $repo ('build/greenwater-package-safety-'+[guid]::NewGuid().ToString('N'))
[void](New-Item -ItemType Directory $root)
$checks=0
$reached=@{Dotnet=0}
# A stand-in for dotnet in this scope only: the packager's own call resolves to it, as a function comes before
# a program of the same name. Reaching it at all is a failure.
function dotnet { $reached.Dotnet++; throw 'fixture: the packager reached dotnet' }
Set-Item Function:\dotnet -Value ${function:dotnet}.GetNewClosure()
# Every file the candidate's source verifier and the packager's own source check read, besides the 23 scripts.
$files=@(
    'tools/win/Build-Greenwater.ps1',
    'tools/win/greenwater-story-candidate.json',
    'tools/greenwater_story_candidate.py',
    'tools/win/world-details-artifact.json',
    'tools/win/world-natural-artifact.json',
    'tools/win/world-story-artifact.json',
    'tools/WorldSliceBuilder/expanded-artifact.json',
    'tools/win/mercy-briefing-candidate.json',
    'tools/mercy_briefing_candidate.py',
    'tools/win/World-Story.psm1',
    'tools/win/Play-WorldStory.ps1',
    'tools/win/Build-WorldDetails.ps1',
    'tools/win/Build-WorldNatural.ps1',
    'tools/win/Stage-WorldDetails.ps1',
    'tools/PluginBuilder/Spec.cs',
    'tools/PluginBuilder/SpecAct1.cs',
    'tools/PluginBuilder/SpecMercyBriefing.cs',
    'tools/PluginBuilder/SpecGreenwater.cs',
    'tools/PluginBuilder/SpecGuide.cs',
    'tools/PluginBuilder/SpecOrientation.cs',
    'tools/PluginBuilder/Builder.cs',
    'tools/PluginBuilder/formkeys.txt',
    'tools/WorldSliceBuilder/WorldStory.cs',
    'tools/WorldSliceBuilder/Program.cs',
    'assets/incoming/act1/story/documents.json'
)
function Copy-FromCheckout([string]$name,[string]$copy) {
    $target=Join-Path $copy $name
    [void](New-Item -ItemType Directory -Force (Split-Path -Parent $target))
    Copy-Item -LiteralPath (Join-Path $repo $name) -Destination $target -Force
}
function Add-Text([string]$path,[string]$text) {
    # Appended as bytes, so that nothing else in the file changes.
    $bytes=[Text.Encoding]::UTF8.GetBytes($text)
    $stream=[IO.File]::Open($path,[IO.FileMode]::Append)
    try { $stream.Write($bytes,0,$bytes.Length) } finally { $stream.Dispose() }
}
try {
    $copy=Join-Path $root 'checkout'
    foreach ($name in $files) { Copy-FromCheckout $name $copy }
    $scripts=Join-Path $copy 'scripts/Source/User/TLM';[void](New-Item -ItemType Directory -Force $scripts)
    foreach ($script in @(Get-ChildItem -LiteralPath (Join-Path $repo 'scripts/Source/User/TLM') -File -Filter '*.psc')) { Copy-Item -LiteralPath $script.FullName -Destination $scripts }
    $builder=Join-Path $copy 'tools/win/Build-Greenwater.ps1'
    $master=Join-Path $root 'Fallout4.esm';$runtime=Join-Path $root 'runtime';$fresh=Join-Path $root 'fresh'
    [void](New-Item -ItemType Directory $runtime,$fresh)
    Set-Content $master 'input sentinel'
    $new=Join-Path $copy 'build/new-package'
    $common=@{VanillaMaster=$master;ReviewedRuntime=$runtime;FreshCompile=$fresh}

    function Get-Refusal([hashtable]$arguments) {
        $reason=''
        try { & $builder @arguments } catch { $reason=$_.Exception.Message }
        if (-not $reason) { throw 'The packager did not refuse.' }
        return $reason
    }
    function Assert-NothingMade([string]$what) {
        if (Test-Path -LiteralPath $new) { throw "Output was created: $what" }
        if (Test-Path -LiteralPath (Join-Path $copy 'build')) { throw "A build folder was created in the copy: $what" }
        if ($reached.Dotnet -ne 0) { throw "dotnet was reached: $what" }
        if ((Get-Content $master -Raw).Trim() -ne 'input sentinel') { throw "The input master changed: $what" }
    }

    # 1. The unchanged copy passes the full verifier and the packager's own source check, and is stopped by the
    #    next check: the first of the 17 reviewed compiled scripts is not in the empty runtime folder.
    $reason=Get-Refusal ($common + @{OutputDirectory=$new;Python=$Python})
    if ($reason -notlike '*Reviewed runtime input absent:*') { throw "The unchanged copy was not stopped at the reviewed runtime check: $reason" };$checks++
    Assert-NothingMade 'the unchanged copy';$checks++

    # 2. Provenance the packager's own source check does not read. Each must be refused by the full verifier,
    #    for its own reason, before anything is created.
    $document=Join-Path $copy 'assets/incoming/act1/story/documents.json'
    $changes=@(
        @{What='a builder source';File='tools/PluginBuilder/SpecGreenwater.cs';Expect='*builderSourceTextSha256 is not as the manifest describes*';Do={ param($path) Add-Text $path "`n// fixture`n" }},
        @{What='the exterior builder';File='tools/WorldSliceBuilder/WorldStory.cs';Expect='*builderSourceTextSha256 is not as the manifest describes*';Do={ param($path) Add-Text $path "`n// fixture`n" }},
        @{What='the id file';File='tools/PluginBuilder/formkeys.txt';Expect='*idFile is not as the manifest describes*';Do={ param($path) Add-Text $path "TLM_FIXTURE`n9999`n" }},
        @{What='a document';File='assets/incoming/act1/story/documents.json';Expect='*documents is not as the manifest describes*';Do={ param($path)
            $text=[IO.File]::ReadAllText($path)
            if (-not $text.Contains('Enclosed, forty. Count them.')) { throw 'fixture: the letter of hire is not worded as this fixture expects' }
            [IO.File]::WriteAllText($path,$text.Replace('Enclosed, forty. Count them.','Enclosed, fifty. Count them.'),(New-Object Text.UTF8Encoding $false)) }},
        @{What='a frozen earlier packager';File='tools/win/Build-WorldDetails.ps1';Expect='*frozenTextSha256: tools/win/Build-WorldDetails.ps1 is not the frozen text*';Do={ param($path) Add-Text $path "`n# fixture`n" }},
        @{What='an earlier manifest';File='tools/win/world-natural-artifact.json';Expect='*earlierManifestsSha256: tools/win/world-natural-artifact.json is not the pinned*';Do={ param($path) Add-Text $path " " }}
    )
    foreach ($change in $changes) {
        & $change.Do (Join-Path $copy $change.File)
        $reason=Get-Refusal ($common + @{OutputDirectory=$new;Python=$Python})
        if ($reason -notlike '*candidate source verifier refused this checkout*') { throw "Not refused by the full verifier ($($change.What)): $reason" };$checks++
        if ($reason -notlike $change.Expect) { throw "Refused for another reason ($($change.What)): $reason" };$checks++
        Assert-NothingMade $change.What;$checks++
        Copy-FromCheckout $change.File $copy
    }
    # Put back, the copy passes the verifier again: the refusals above were for the changes and nothing else.
    $reason=Get-Refusal ($common + @{OutputDirectory=$new;Python=$Python})
    if ($reason -notlike '*Reviewed runtime input absent:*') { throw "The restored copy was not stopped at the reviewed runtime check: $reason" };$checks++

    # 3. No interpreter: fails closed.
    $reason=Get-Refusal ($common + @{OutputDirectory=$new;Python='tlm-no-such-python-interpreter'})
    if ($reason -notlike '*Python interpreter not found*') { throw "A missing interpreter was not refused as such: $reason" };$checks++
    Assert-NothingMade 'no interpreter';$checks++

    # 4. The output folder's own rules still come first.
    $outside=Join-Path ([IO.Path]::GetTempPath()) ('must-not-exist-'+[guid]::NewGuid().ToString('N'))
    $reason=Get-Refusal ($common + @{OutputDirectory=$outside;Python=$Python})
    if ($reason -notlike '*must be a new directory under this checkout build folder*') { throw "An outside output was not refused as such: $reason" };$checks++
    if (Test-Path -LiteralPath $outside) { throw 'The outside folder was created.' };$checks++
    $occupied=Join-Path $root 'occupied-checkout';foreach ($name in $files) { Copy-FromCheckout $name $occupied }
    $occupiedOutput=Join-Path $occupied 'build/occupied';[void](New-Item -ItemType Directory -Force $occupiedOutput)
    $sentinel=Join-Path $occupiedOutput 'keep.txt';Set-Content $sentinel 'owner content';$hash=(Get-FileHash $sentinel).Hash
    $occupiedBuilder=Join-Path $occupied 'tools/win/Build-Greenwater.ps1'
    foreach ($case in @('occupied','empty')) {
        $target=$occupiedOutput
        if ($case -eq 'empty') { $target=Join-Path $occupied 'build/empty';[void](New-Item -ItemType Directory -Force $target) }
        $reason=''
        try { & $occupiedBuilder @common -OutputDirectory $target -Python $Python } catch { $reason=$_.Exception.Message }
        if ($reason -notlike '*must be wholly new*') { throw "An existing $case output was not refused as such: $reason" };$checks++
        if ((Get-FileHash $sentinel).Hash -ne $hash) { throw 'An existing file changed.' };$checks++
        if ($case -eq 'empty' -and @(Get-ChildItem -LiteralPath $target -Force).Count) { throw 'An existing empty folder changed.' }
    }
    if ($reached.Dotnet -ne 0) { throw 'dotnet was reached.' };$checks++
    Write-Host "$checks Greenwater package refusal checks passed; no compiler, build, game or install execution."
} finally { $target=[IO.Path]::GetFullPath($root);if (-not $target.StartsWith(([IO.Path]::GetFullPath($repo)+[IO.Path]::DirectorySeparatorChar),[StringComparison]::OrdinalIgnoreCase)) { throw 'Fixture cleanup escaped checkout.' };Remove-Item -LiteralPath $target -Recurse -Force }
