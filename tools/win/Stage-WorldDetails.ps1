<# ROOT-ONLY six-prop Details owner staging. SOURCE CANDIDATE, not executed; targeted native acceptance pending.
Creates only NEW dedicated targets; no launch, save copy or fallback overwrite.
On failure preserve partial targets and unfinished receipt for inspection. #>
[CmdletBinding()]
param([Parameter(Mandatory)][ValidatePattern('^[a-fA-F0-9]{40}$')][string]$ReviewedSourceCommit)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$workspace=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$launcher=$workspace
$expectedHead=$ReviewedSourceCommit
$manifestHash='E384CF4988BAD9B38D07990A0AD214A3F52D264E43D7CF447B3398059544F89B'
$head=@(& git -C $launcher rev-parse HEAD)
if ($LASTEXITCODE -ne 0 -or $head.Count -ne 1 -or $head[0] -cne $expectedHead) { throw 'Details staging requires the exact independently inspected Details source.' }
& git -C $launcher diff --quiet HEAD --
if ($LASTEXITCODE -ne 0) { throw 'Inspected Details source has tracked modifications.' }
Import-Module (Join-Path $launcher 'tools/win/Tlm.psm1') -Force
Import-Module (Join-Path $launcher 'tools/win/World-Story.psm1') -Force

function Assert-DetailsStageClear {
    Assert-WorldStoryProcessesClear
    $hostEditor=@(Get-Process -ErrorAction Stop | Where-Object { $_.ProcessName -eq 'CreationKit' })
    $cimEditor=@(Get-CimInstance -ClassName Win32_Process -Filter "Name='CreationKit.exe'" -ErrorAction Stop)
    if ($hostEditor.Count -or $cimEditor.Count) { throw 'Creation Kit remains; no staging writes permitted.' }
}
function Assert-DetailsStageHash([string]$Path,[string]$Expected) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf) -or (Get-FileHash -LiteralPath $Path).Hash -cne $Expected) { throw "Staging hash mismatch: $Path" }
}
function Assert-DetailsStagePath([string]$Path,[switch]$New) {
    $full=[IO.Path]::GetFullPath($Path);$cursor=$full
    while ($cursor) {
        $entry=$null
        try { $entry=Get-Item -LiteralPath $cursor -Force -ErrorAction Stop }
        catch [System.Management.Automation.ItemNotFoundException] { $entry=$null }
        catch { throw "Cannot inspect staging ancestry: $cursor" }
        if ($null -ne $entry) {
            if (($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse staging ancestry refused: $cursor" }
            if ($New -and $cursor -ceq $full) { throw "Target or partial staging already exists; left untouched: $full" }
            if ($cursor -cne $full -and -not $entry.PSIsContainer) { throw "Staging ancestor is not a directory: $cursor" }
        }
        $parent=[IO.Path]::GetDirectoryName($cursor.TrimEnd([IO.Path]::DirectorySeparatorChar))
        if (-not $parent -or $parent -ceq $cursor) { break };$cursor=$parent
    }
}
function Copy-DetailsStageNewFile([string]$Source,[string]$Destination) {
    Assert-DetailsStageClear
    Assert-DetailsStagePath $Destination -New
    $inputStream=$null;$outputStream=$null
    try {
        $inputStream=[IO.File]::Open($Source,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read)
        $outputStream=[IO.File]::Open($Destination,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
        $inputStream.CopyTo($outputStream)
    } finally { if ($outputStream) { $outputStream.Dispose() };if ($inputStream) { $inputStream.Dispose() } }
}
function Write-DetailsStageLines([string]$Path,[string[]]$Lines) { Assert-DetailsStageClear;Assert-DetailsStagePath $Path;Write-RawLines $Path $Lines }
function Set-DetailsStageIni([string]$Path,[string]$Section,[string]$Key,[string]$Value) { Assert-DetailsStageClear;Assert-DetailsStagePath $Path;Set-IniValue $Path $Section $Key $Value }
function Get-DetailsOtherPrefs([string]$Path) {
    $general=$false
    foreach ($line in @(Read-RawLines $Path)) {
        if ($line -match '^\s*\[([^\]]+)\]') { $general=($Matches[1] -ieq 'General') }
        if ($general -and $line -match '^\s*bGamepadEnable\s*=') { continue }
        $line
    }
}
Assert-DetailsStageClear
$manifestPath=Join-Path $launcher 'tools/win/world-details-artifact.json'
Assert-DetailsStageHash $manifestPath $manifestHash
$manifest=Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$pins=@($manifest.runtime.PSObject.Properties)
if ($manifest.schema -ne 1 -or $pins.Count -ne 19 -or
    $manifest.worldSha256 -cne 'E1279E42DAA19D94A628F1270D285EB8A175EE21579924C0DE51B017C25F5965' -or
    $manifest.masterSha256 -cne 'AA52CBC3A6153BF83BB99EF22D8CC385DA2254052B49E4A78252494003250F3F') { throw 'Wrong frozen Details manifest.' }
foreach ($pin in $pins) { if ($pin.Name -notmatch '^[A-Za-z0-9_]+\.pex$' -or "$($pin.Value)" -notmatch '^[A-F0-9]{64}$') { throw 'Unsafe runtime pin.' } }
$bundle=Join-Path $launcher 'build/details-verified/bundle'
$world=Join-Path $bundle 'TLMWorldSlice.esp';$master=Join-Path $bundle 'TheLastMeridian.esp';$runtime=Join-Path $bundle 'Scripts/TLM'
$expectedFiles=@('TheLastMeridian.esp','TLMWorldSlice.esp')+@($pins | ForEach-Object { 'Scripts/TLM/'+$_.Name })
function Assert-DetailsBundle([string]$Root,[switch]$WithManifest) {
    Assert-DetailsStagePath $Root
    $items=@(Get-ChildItem -LiteralPath $Root -Force -Recurse)
    if (@($items | Where-Object { ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 }).Count) { throw 'Bundle contains a reparse point.' }
    $expected=@($expectedFiles);if ($WithManifest) { $expected+=@('reviewed-artifact.json') }
    $actual=@($items | Where-Object { -not $_.PSIsContainer } | ForEach-Object { $_.FullName.Substring($Root.Length+1).Replace('\','/') })
    if ($actual.Count -ne $expected.Count -or @(Compare-Object ($actual | Sort-Object) ($expected | Sort-Object) -CaseSensitive).Count) { throw 'Bundle has missing/extra files; partial staging retained.' }
    $dirs=@($items | Where-Object { $_.PSIsContainer } | ForEach-Object { $_.FullName.Substring($Root.Length+1).Replace('\','/') })
    if ($dirs.Count -ne 2 -or @($dirs | Where-Object { $_ -cnotin @('Scripts','Scripts/TLM') }).Count) { throw 'Unexpected bundle directories.' }
    Assert-DetailsStageHash (Join-Path $Root 'TLMWorldSlice.esp') $manifest.worldSha256
    Assert-DetailsStageHash (Join-Path $Root 'TheLastMeridian.esp') $manifest.masterSha256
    foreach ($pin in $pins) { Assert-DetailsStageHash (Join-Path $Root ('Scripts/TLM/'+$pin.Name)) $pin.Value }
    if ((Get-PluginGlobal -Path (Join-Path $Root 'TheLastMeridian.esp') -EditorId TLM_G_DevScenario) -ne 0) { throw 'Scenario is not zero.' }
    if ($WithManifest) { Assert-DetailsStageHash (Join-Path $Root 'reviewed-artifact.json') $manifestHash }
}
Assert-DetailsBundle $bundle
# Verify current source text corresponds to the selected reviewed runtime.
$sourcePins=@($manifest.sourceTextSha256.PSObject.Properties)
$sourceNames=@(Get-ChildItem -LiteralPath (Join-Path $launcher 'scripts/Source/User/TLM') -File -Filter '*.psc' | ForEach-Object { $_.Name })
if ($sourcePins.Count -ne 19 -or $sourceNames.Count -ne 19 -or @(Compare-Object ($sourceNames | Sort-Object) ($sourcePins.Name | Sort-Object) -CaseSensitive).Count) { throw 'Expected exactly19 source scripts matching source provenance.' }
foreach ($pin in $sourcePins) {
    $text=[IO.File]::ReadAllText((Join-Path $launcher ('scripts/Source/User/TLM/'+$pin.Name))).Replace("`r`n","`n").Replace("`r","`n")
    $sha=[Security.Cryptography.SHA256]::Create()
    try { $hash=[BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($text))).Replace('-','') } finally { $sha.Dispose() }
    if ($hash -cne $pin.Value) { throw "Source digest mismatch: $($pin.Name)" }
}
$moRoot='C:\Modlists\TMR';$variant=Get-WorldStoryVariant -Details
$mod=Join-Path $moRoot ('mods/'+$variant.ModName);$profile=Join-Path $moRoot ('profiles/'+$variant.ProfileName)
$sourceProfile=Join-Path $moRoot 'profiles/TLM-World-Natural-Preview'
$mo=Get-ModOrganizerInfo -Root $moRoot
if (-not $mo -or -not (Test-SamePath $mo.ModsDirectory (Join-Path $moRoot 'mods')) -or -not (Test-SamePath $mo.ProfilesDirectory (Join-Path $moRoot 'profiles'))) { throw 'Unexpected manager staging paths.' }
Assert-DetailsStagePath $mod -New;Assert-DetailsStagePath $profile -New;Assert-DetailsStagePath $sourceProfile
if (-not (Test-Path -LiteralPath $sourceProfile -PathType Container)) { throw 'Reviewed source profile absent.' }
$profileNames=@('archives.txt','fallout4.ini','fallout4custom.ini','fallout4prefs.ini','initweaks.ini','loadorder.txt','lockedorder.txt','modlist.txt','plugins.txt','settings.ini')
$sourceFiles=@($profileNames | ForEach-Object { Get-Item -LiteralPath (Join-Path $sourceProfile $_) -Force -ErrorAction Stop })
foreach ($f in $sourceFiles) { if ($f.PSIsContainer -or ($f.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Source profile input is not an ordinary file.' } }
$sourcePrefs=Join-Path $sourceProfile 'fallout4prefs.ini'
$otherPrefsBefore=@(Get-DetailsOtherPrefs $sourcePrefs)
$controllerBefore=[string](Get-IniValue $sourcePrefs General bGamepadEnable)
# Hash existing fallbacks; never write to any path in this set. No saves copied.
$protected=@(Join-Path $moRoot 'ModOrganizer.ini')
foreach ($relative in @('profiles/TLM-World-Preview','profiles/TLM-World-Story-Preview','profiles/TLM-World-Expanded-Preview','mods/TheLastMeridian-WorldSliceQA','mods/TheLastMeridian-WorldStoryPreview','mods/TheLastMeridian-WorldExpandedPreview','profiles/TLM-World-Natural-Preview','mods/TheLastMeridian-WorldNaturalPreview','mods/TheLastMeridian-Dev')) {
    $folder=Join-Path $moRoot $relative
    if (-not (Test-Path -LiteralPath $folder -PathType Container)) { throw "Fallback absent: $folder" }
    $protected+=@(Get-ChildItem -LiteralPath $folder -File -Force -Recurse | ForEach-Object { $_.FullName })
}
$before=@{};foreach ($path in $protected) { $before[$path]=(Get-FileHash -LiteralPath $path).Hash }
$receiptPath=Join-Path (Join-Path $launcher 'build') ('details-stage-receipt-'+[guid]::NewGuid().ToString('N')+'.json')
$receipt=[pscustomobject]@{Status='STARTING; NOT COMPLETE';LauncherHead=$expectedHead;ManifestSha256=$manifestHash;Bundle=$bundle;Profile=$profile;Mod=$mod;WorldSha256=$manifest.worldSha256;MasterSha256=$manifest.masterSha256;Runtime=$manifest.runtime;FallbackHashes=$before;NoGameLaunched=$true;NoSavesCopied=$true;ControlPreference='owner controller enabled in NEW target only; all other prefs preserved';ControllerBefore=$controllerBefore;ControllerAfter='1'}
Assert-DetailsStageClear;Assert-DetailsStagePath $receiptPath -New
$bytes=[Text.Encoding]::UTF8.GetBytes(($receipt | ConvertTo-Json -Depth 6))
$stream=[IO.File]::Open($receiptPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try { $stream.Write($bytes,0,$bytes.Length) } finally { $stream.Dispose() }
Write-Output "Starting new-only Details staging. On any failure preserve partial targets and receipt: $receiptPath"
Assert-DetailsStageClear;Assert-DetailsStagePath $mod -New
[void](New-Item -ItemType Directory -Path $mod)
Assert-DetailsStageClear
[void](New-Item -ItemType Directory -Path (Join-Path $mod 'Scripts/TLM'))
Copy-DetailsStageNewFile $world (Join-Path $mod 'TLMWorldSlice.esp');Copy-DetailsStageNewFile $master (Join-Path $mod 'TheLastMeridian.esp')
foreach ($pin in $pins) { Copy-DetailsStageNewFile (Join-Path $runtime $pin.Name) (Join-Path $mod ('Scripts/TLM/'+$pin.Name)) }
Copy-DetailsStageNewFile $manifestPath (Join-Path $mod 'reviewed-artifact.json')
Assert-DetailsBundle $mod -WithManifest
Assert-DetailsStageClear;Assert-DetailsStagePath $profile -New
[void](New-Item -ItemType Directory -Path $profile)
foreach ($f in $sourceFiles) { Copy-DetailsStageNewFile $f.FullName (Join-Path $profile $f.Name) }
if (@(Get-ChildItem -LiteralPath $profile -Force).Count -ne $profileNames.Count) { throw 'New profile has extra entries; partial staging retained.' }
Write-DetailsStageLines (Join-Path $profile 'modlist.txt') @('# Reviewed Details only; optional personal UI not auto-enabled',('+'+$variant.ModName))
Write-DetailsStageLines (Join-Path $profile 'plugins.txt') @('# Native acceptance pending','*TheLastMeridian.esp','*TLMWorldSlice.esp')
$order=@(Read-RawLines (Join-Path $profile 'loadorder.txt') | Where-Object { $_ -notin @('TheLastMeridian.esp','TLMWorldSlice.esp') })+@('TheLastMeridian.esp','TLMWorldSlice.esp')
Write-DetailsStageLines (Join-Path $profile 'loadorder.txt') $order
$custom=Join-Path $profile 'fallout4custom.ini';$settings=Join-Path $profile 'settings.ini'
foreach ($pair in @(@('General','sStartingConsoleCommand',''),@('General','bAlwaysActive','0'),@('Papyrus','bEnableLogging','1'),@('Papyrus','bEnableTrace','1'),@('Papyrus','bLoadDebugInformation','1'),@('Archive','bInvalidateOlderFiles','1'),@('Archive','sResourceDataDirsFinal',''))) { Set-DetailsStageIni $custom $pair[0] $pair[1] $pair[2] }
Set-DetailsStageIni $settings General LocalSaves true;Set-DetailsStageIni $settings General LocalSettings true
$prefs=Join-Path $profile 'fallout4prefs.ini'
Set-DetailsStageIni $prefs General bGamepadEnable '1'
Assert-DetailsStageClear
[void](Get-WorldStoryContext -ModOrganizerRoot $moRoot -Details)
[void](Get-WorldStoryStartupState -Ini $custom)
if ((Get-IniValue $custom General bAlwaysActive) -ne '0') { throw 'Temporary startup baseline readback failed.' }
if ((Get-IniValue $prefs General bGamepadEnable) -ne '1' -or [string]::Join("`n",@(Get-DetailsOtherPrefs $prefs)) -cne [string]::Join("`n",$otherPrefsBefore)) { throw 'Owner controller preference or preserved-other-prefs readback failed.' }
Assert-DetailsBundle $mod -WithManifest
foreach ($path in $before.Keys) { Assert-DetailsStageHash $path $before[$path] }
$receipt.Status='STAGED; NATIVE ACCEPTANCE PENDING'
Assert-DetailsStageClear;Assert-DetailsStagePath $receiptPath
$receipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $receiptPath -Encoding utf8
Write-Output "Details owner files staged separately. No game launched; no native readiness/pass claimed. Receipt: $receiptPath"
