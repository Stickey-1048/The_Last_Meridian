param([Parameter(Mandatory)][string]$CoreArtifact, [string]$WorldArtifact)
$ErrorActionPreference='Stop'
Import-Module (Join-Path $PSScriptRoot '../Tlm.psm1') -Force
Import-Module (Join-Path $PSScriptRoot '../World-Story.psm1') -Force
$root=Join-Path ([IO.Path]::GetTempPath()) ('TlmStoryTest_'+[guid]::NewGuid().ToString('N'))
[void](New-Item -ItemType Directory $root)
$checks=0
function Assert($condition,$label) { if (-not $condition) { throw $label }; $script:checks++ }
function Refuses([scriptblock]$action,$label) { $failed=$false;try { & $action } catch { $failed=$true };Assert $failed $label }
try {
    $p=Get-WorldStoryStartupPlan $root
    $lines=@($p.Content.TrimEnd().Split("`n") | ForEach-Object { $_.TrimEnd("`r") })
    Assert ($lines.Count -eq 9 -and $lines[0] -ceq 'coc TLM_WS_Clearing' -and $lines[8] -ceq 'cqf TLM_WS_Entry QueueFreshEntry') 'COC then seven stats then explicit queue'
    $i=1
    foreach ($av in @('Strength','Perception','Endurance','Charisma','Intelligence','Agility','Luck')) { Assert ($lines[$i] -ceq "player.setav $av 4") "fresh-only $av";$i++ }
    $ini=Join-Path $root 'fallout4custom.ini'
    Set-Content $ini "[General]`r`nsStartingConsoleCommand=`r`nbAlwaysActive=0`r`nUnrelated=keep`r`n[Controls]`r`nbGamepadEnable=1"
    $note=[pscustomobject]@{Ini=$ini;GameFolder=$root;StartupBefore='';ActiveBefore='0';Batch=$p}
    Write-FreshDemoStartupBatch $p
    Assert ((Get-FileHash $p.Path).Hash -eq $p.Hash) 'batch hash includes queue'
    Set-IniValue $ini General sStartingConsoleCommand $p.Command
    Set-IniValue $ini General bAlwaysActive 1
    Restore-WorldStoryState ($note | ConvertTo-Json -Depth 4 | ConvertFrom-Json)
    Assert (-not (Test-Path $p.Path)) 'owned batch removed'
    Assert ((Get-IniValue $ini General sStartingConsoleCommand) -ceq '') 'startup restored'
    Assert ((Get-IniValue $ini General bAlwaysActive) -eq '0') 'activity restored'
    Assert ((Get-IniValue $ini General Unrelated) -ceq 'keep') 'unrelated setting preserved'
    Assert ((Get-IniValue $ini Controls bGamepadEnable) -eq '1') 'controller preference preserved'
    $before=(Get-FileHash $ini).Hash
    $state=Get-WorldStoryStartupState $ini
    Assert ($state.Startup -ceq '' -and $state.Active -eq '0' -and (Get-FileHash $ini).Hash -eq $before) 'startup preflight is read-only'
    Set-IniValue $ini General sStartingConsoleCommand 'owner command'
    $before=(Get-FileHash $ini).Hash
    Refuses { Get-WorldStoryStartupState $ini } 'existing startup command refuses'
    Assert ((Get-FileHash $ini).Hash -eq $before) 'refused owner startup unchanged'
    Set-IniValue $ini General sStartingConsoleCommand ''
    $p=Get-WorldStoryStartupPlan $root;$note.Batch=$p
    [IO.File]::WriteAllText($p.Path,$p.Content,[Text.Encoding]::ASCII)
    Refuses { Write-FreshDemoStartupBatch $p } 'existing identical file collision refuses'
    Restore-WorldStoryState $note
    Assert (Test-Path $p.Path) 'collision never claims/deletes existing file'
    Remove-Item -LiteralPath $p.Path
    $p=Get-WorldStoryStartupPlan $root;$note.Batch=$p;Write-FreshDemoStartupBatch $p
    Add-Content $p.Path 'changed'
    Refuses { Restore-WorldStoryState $note } 'changed owned batch preserved'
    Assert (Test-Path $p.Path) 'changed batch survives recovery'
    Remove-Item -LiteralPath $p.Path
    $p=Get-WorldStoryStartupPlan $root;$note.Batch=$p;Set-Content $p.Path 'ambiguous'
    Refuses { Restore-WorldStoryState $note } 'ambiguous interrupted ownership refuses deletion'
    Assert (Test-Path $p.Path) 'ambiguous file preserved'
    $mo=Join-Path $root 'manager';$game=Join-Path $root 'game'
    $profile=Join-Path $mo 'profiles/TLM-World-Story-Preview';$mod=Join-Path $mo 'mods/TheLastMeridian-WorldStoryPreview'
    $scripts=Join-Path $mod 'Scripts/TLM'
    foreach ($folder in @($game,$profile,$scripts)) { [void](New-Item -ItemType Directory -Force $folder) }
    Copy-Item -LiteralPath $CoreArtifact -Destination (Join-Path $mod 'TheLastMeridian.esp')
    $core=Join-Path $mod 'TheLastMeridian.esp';$world=Join-Path $mod 'TLMWorldSlice.esp'
    if ($WorldArtifact) { Copy-Item -LiteralPath $WorldArtifact -Destination $world } else { Set-Content $world 'fixture-world-bytes; builder readback tested separately' }
    Set-Content (Join-Path $game 'Fallout4.exe') 'fixture only; never executed'
    Set-Content (Join-Path $mo 'ModOrganizer.ini') "[General]`ngamePath=$game"
    $settings=Join-Path $profile 'settings.ini';$mods=Join-Path $profile 'modlist.txt';$plugins=Join-Path $profile 'plugins.txt'
    Set-Content $settings "[General]`nLocalSaves=true`nLocalSettings=true"
    Set-Content $mods '+TheLastMeridian-WorldStoryPreview'
    Set-Content $plugins "*TheLastMeridian.esp`n*TLMWorldSlice.esp"
    $pins=Get-Content (Join-Path $PSScriptRoot '../world-story-artifact.json') -Raw | ConvertFrom-Json
    # Synthetic PEX bytes exercise integrity/refusal logic, never runtime behavior.
    foreach ($item in $pins.runtime.PSObject.Properties) { $file=Join-Path $scripts $item.Name;Set-Content $file ("fixture-"+$item.Name);$item.Value=(Get-FileHash $file).Hash }
    $pins.worldSha256=(Get-FileHash $world).Hash;$pins.masterSha256=(Get-FileHash $core).Hash
    $manifest=Join-Path $root 'fixture-manifest.json'
    function SavePins { $pins | ConvertTo-Json -Depth 4 | Set-Content $manifest }
    function Context { Get-WorldStoryContext -ModOrganizerRoot $mo -ManifestPath $manifest }
    SavePins
    Assert ((Context).World -eq $world) 'isolated positive context accepted'
    Refuses { Get-WorldStoryContext -ModOrganizerRoot $mo -ProfileName 'Default' -ManifestPath $manifest } 'owner profile rejected'
    Set-IniValue $settings General LocalSaves false;Refuses { Context } 'shared saves rejected';Set-IniValue $settings General LocalSaves true
    Set-IniValue $settings General LocalSettings false;Refuses { Context } 'shared settings rejected';Set-IniValue $settings General LocalSettings true
    Add-Content $mods '+TheLastMeridian-WorldProbe';Refuses { Context } 'private/unreviewed mod rejected';Set-Content $mods '+TheLastMeridian-WorldStoryPreview'
    Add-Content $mods '+TheLastMeridian-WorldStoryPreview';Refuses { Context } 'duplicate mod rejected';Set-Content $mods '+TheLastMeridian-WorldStoryPreview'
    Add-Content $mods '+FallUI - Workbench';Assert ((Context).RequiresF4SE) 'F4SE-dependent UI flagged';Set-Content $mods '+TheLastMeridian-WorldStoryPreview'
    Set-Content $plugins "*TLMWorldSlice.esp`n*TheLastMeridian.esp";Refuses { Context } 'incorrect plugin order rejected';Set-Content $plugins "*TheLastMeridian.esp`n*TLMWorldSlice.esp"
    Set-PluginGlobal $core TLM_G_DevScenario 12;$pins.masterSha256=(Get-FileHash $core).Hash;SavePins
    Refuses { Context } 'nonzero scenario rejected even with matching hash'
    Set-PluginGlobal $core TLM_G_DevScenario 0;$pins.masterSha256=(Get-FileHash $core).Hash;SavePins
    $scriptFile=Join-Path $scripts 'WorldEntry.pex';$original=[IO.File]::ReadAllBytes($scriptFile)
    Add-Content $scriptFile 'modified';Refuses { Context } 'altered runtime rejected';[IO.File]::WriteAllBytes($scriptFile,$original)
    Set-Content (Join-Path $scripts 'PrivateProbe.pex') 'probe';Refuses { Context } 'extra runtime script rejected';Remove-Item (Join-Path $scripts 'PrivateProbe.pex')
    $outside=Join-Path $mo 'overwrite/Scripts/TLM';[void](New-Item -ItemType Directory -Force $outside)
    Set-Content (Join-Path $outside 'Core.pex') 'private';Refuses { Context } 'overwrite probe rejected';Remove-Item (Join-Path $outside 'Core.pex')
    $data=Join-Path $game 'Data';[void](New-Item -ItemType Directory -Force $data)
    Copy-Item $world (Join-Path $data 'TLMWorldSlice.esp');Refuses { Context } 'duplicate world in game Data rejected';Remove-Item (Join-Path $data 'TLMWorldSlice.esp')
    Set-Content (Join-Path $mod 'TLMWorldSlice.ba2') 'unknown';Refuses { Context } 'shadowing archive rejected';Remove-Item (Join-Path $mod 'TLMWorldSlice.ba2')
    $originalWorld=[IO.File]::ReadAllBytes($world);Add-Content $world 'modified';Refuses { Context } 'altered world rejected';[IO.File]::WriteAllBytes($world,$originalWorld)
    Assert ((Context).World -eq $world) 'fixture accepted after repairs'
    foreach ($name in @('Play-WorldStory.ps1','World-Story.psm1')) {
        $tokens=$null;$errors=$null;[void][Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot "../$name"),[ref]$tokens,[ref]$errors)
        Assert ($errors.Count -eq 0) "parser $name"
    }
    Write-Host "$checks story launcher checks passed (fixtures only; no game/manager execution)"
} finally { Remove-Item -LiteralPath $root -Recurse -Force }
