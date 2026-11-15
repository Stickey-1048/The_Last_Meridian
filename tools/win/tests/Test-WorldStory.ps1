param([Parameter(Mandatory)][string]$CoreArtifact, [string]$WorldArtifact, [string]$ExpandedArtifact)
$ErrorActionPreference='Stop'
Import-Module (Join-Path $PSScriptRoot '../Tlm.psm1') -Force
Import-Module (Join-Path $PSScriptRoot '../World-Story.psm1') -Force
$storyModule=Get-Module World-Story
# Only this module's inventory cmdlets are mocked; tests never inspect or
# interrupt host processes, and can run on CI without Windows CIM support.
& $storyModule {
    $script:fixtureHost=@();$script:fixtureCim=@();$script:fixtureHostBroken=$false;$script:fixtureCimBroken=$false
    function script:Get-Process {
        [CmdletBinding()]param()
        if ($script:fixtureHostBroken) { throw 'fixture process query failed' }
        $script:fixtureHost
    }
    function script:Get-CimInstance {
        [CmdletBinding()]param([string]$ClassName,[string]$Filter)
        if ($ClassName -cne 'Win32_Process' -or $Filter -notmatch 'Fallout4.exe.*ModOrganizer.exe') { throw 'unexpected inventory query' }
        if ($script:fixtureCimBroken) { throw 'fixture CIM unavailable' }
        $script:fixtureCim
    }
}
function SetProcessFixture($HostRows=@(),$CimRows=@(),[bool]$HostBroken=$false,[bool]$CimBroken=$false) {
    & $storyModule {param($h,$c,$hb,$cb) $script:fixtureHost=@($h);$script:fixtureCim=@($c);$script:fixtureHostBroken=$hb;$script:fixtureCimBroken=$cb} $HostRows $CimRows $HostBroken $CimBroken
}
$root=Join-Path ([IO.Path]::GetTempPath()) ('TlmStoryTest_'+[guid]::NewGuid().ToString('N'))
[void](New-Item -ItemType Directory $root)
$checks=0
function Assert($condition,$label) { if (-not $condition) { throw $label }; $script:checks++ }
function Refuses([scriptblock]$action,$label) { $failed=$false;try { & $action } catch { $failed=$true };Assert $failed $label }
try {
    SetProcessFixture
    Assert ((Get-WorldStoryProcessInventory).Clear) 'both inventories absent permits lifecycle'
    SetProcessFixture -HostRows @([pscustomobject]@{Id=101;ProcessName='Fallout4'})
    Refuses { Assert-WorldStoryProcessesClear } 'ordinary Get-Process live game blocks launch'
    SetProcessFixture -CimRows @([pscustomobject]@{ProcessId=102;Name='ModOrganizer.exe'})
    $inventory=Get-WorldStoryProcessInventory
    Assert (-not $inventory.Clear -and $inventory.Processes.Count -eq 1 -and $inventory.Processes[0].Source -eq 'CIM') 'Get-Process empty CIM residual manager remains busy'
    Refuses { Assert-WorldStoryProcessesClear } 'residual manager blocks launch'
    SetProcessFixture -HostRows @([pscustomobject]@{Id=103;ProcessName='Fallout4'}) -CimRows @([pscustomobject]@{ProcessId=103;Name='Fallout4.exe'})
    $inventory=Get-WorldStoryProcessInventory
    Assert ($inventory.Processes.Count -eq 1 -and $inventory.Processes[0].Source -eq 'Get-Process+CIM') 'same PID deduplicated across providers'
    SetProcessFixture -CimBroken $true
    Refuses { Assert-WorldStoryProcessesClear } 'broken CIM fails closed even with empty process list'
    SetProcessFixture -HostBroken $true
    Refuses { Assert-WorldStoryProcessesClear } 'broken host inventory fails closed'
    SetProcessFixture -CimRows @([pscustomobject]@{ProcessId=0;Name='Fallout4.exe'})
    Refuses { Assert-WorldStoryProcessesClear } 'incomplete CIM record fails closed'
    SetProcessFixture
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
    # Execute the actual launcher's finally block against owned temporary files:
    # a residual process or broken inventory must prevent settings/batch/note edits.
    $parseTokens=$null;$parseErrors=$null
    $launcherAst=[Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot '../Play-WorldStory.ps1'),[ref]$parseTokens,[ref]$parseErrors)
    $tryAst=@($launcherAst.EndBlock.Statements | Where-Object { $_ -is [Management.Automation.Language.TryStatementAst] })[-1]
    $text=$tryAst.Finally.Extent.Text
    $actualFinally=[scriptblock]::Create($text.Substring(1,$text.Length-2))
    $variant=Get-WorldStoryVariant
    $context=[pscustomobject]@{Mo=[pscustomobject]@{GamePath=$root}}
    foreach ($mode in @('residual','broken','clear')) {
        SetProcessFixture
        $p=Get-WorldStoryStartupPlan $root;$note.Batch=$p;Write-FreshDemoStartupBatch $p
        Set-IniValue $ini General sStartingConsoleCommand $p.Command;Set-IniValue $ini General bAlwaysActive 1
        $journal=Join-Path $root 'owned-note.json';$note | ConvertTo-Json -Depth 4 | Set-Content $journal
        $iniHash=(Get-FileHash $ini).Hash;$batchHash=(Get-FileHash $p.Path).Hash;$noteHash=(Get-FileHash $journal).Hash
        if ($mode -eq 'residual') { SetProcessFixture -CimRows @([pscustomobject]@{ProcessId=104;Name='Fallout4.exe'}) }
        if ($mode -eq 'broken') { SetProcessFixture -CimBroken $true }
        if ($mode -eq 'clear') {
            & $actualFinally
            Assert (-not (Test-Path $p.Path) -and -not (Test-Path $journal)) 'actual finally removes owned batch/note only after both providers clear'
            Assert ((Get-IniValue $ini General sStartingConsoleCommand) -ceq '' -and (Get-IniValue $ini General bAlwaysActive) -eq '0') 'actual finally restores settings after full exit'
        } else {
            Refuses { & $actualFinally } "actual finally $mode inventory fails closed"
            Assert ((Get-FileHash $ini).Hash -eq $iniHash -and (Get-FileHash $p.Path).Hash -eq $batchHash -and (Get-FileHash $journal).Hash -eq $noteHash) "actual finally $mode preserves settings/batch/ownership note"
            SetProcessFixture
            Restore-WorldStoryState $note;Remove-Item $journal
        }
    }
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
    $defaultIni=$ini;$defaultIniHash=(Get-FileHash $ini).Hash
    $expandedVariant=Get-WorldStoryVariant -Expanded
    $expandedProfile=Join-Path $mo ('profiles/'+$expandedVariant.ProfileName)
    $expandedMod=Join-Path $mo ('mods/'+$expandedVariant.ModName)
    [void](New-Item -ItemType Directory -Force $expandedProfile,$expandedMod)
    [void](New-Item -ItemType Directory -Force (Join-Path $expandedMod 'Scripts/TLM'))
    Copy-Item (Join-Path $scripts '*.pex') (Join-Path $expandedMod 'Scripts/TLM')
    Copy-Item $core (Join-Path $expandedMod 'TheLastMeridian.esp')
    $expandedWorld=Join-Path $expandedMod 'TLMWorldSlice.esp'
    if ($ExpandedArtifact) { Copy-Item -LiteralPath $ExpandedArtifact -Destination $expandedWorld } else { Set-Content $expandedWorld 'distinct expanded fixture world' }
    Set-Content (Join-Path $expandedProfile 'settings.ini') "[General]`nLocalSaves=true`nLocalSettings=true"
    $expandedMods=Join-Path $expandedProfile 'modlist.txt';Set-Content $expandedMods ('+'+$expandedVariant.ModName)
    Copy-Item $plugins (Join-Path $expandedProfile 'plugins.txt')
    $expandedPins=Get-Content $expandedVariant.ManifestPath -Raw | ConvertFrom-Json
    $fixedDefault=Get-Content (Get-WorldStoryVariant).ManifestPath -Raw | ConvertFrom-Json
    Assert ($expandedPins.worldSha256 -cne $fixedDefault.worldSha256) 'fixed expanded manifest differs from preserved default world'
    Assert (($expandedPins.runtime | ConvertTo-Json -Compress) -ceq ($fixedDefault.runtime | ConvertTo-Json -Compress) -and $expandedPins.masterSha256 -ceq $fixedDefault.masterSha256) 'expanded reuses exactly the same fixed master and19 runtime pins'
    foreach ($item in $expandedPins.runtime.PSObject.Properties) { $item.Value=(Get-FileHash (Join-Path $expandedMod ('Scripts/TLM/'+$item.Name))).Hash }
    $expandedPins.masterSha256=(Get-FileHash $core).Hash;$expandedPins.worldSha256=(Get-FileHash $expandedWorld).Hash
    $expandedManifest=Join-Path $root 'expanded-fixture-manifest.json';$expandedPins | ConvertTo-Json -Depth 4 | Set-Content $expandedManifest
    function ExpandedContext { Get-WorldStoryContext -ModOrganizerRoot $mo -Expanded -ManifestPath $expandedManifest }
    Assert ((ExpandedContext).World -eq $expandedWorld -and (Context).World -eq $world) 'both variants independently accepted'
    Refuses { Get-WorldStoryContext -ModOrganizerRoot $mo -Expanded -ProfileName 'TLM-World-Story-Preview' -ManifestPath $expandedManifest } 'expanded cannot select default profile'
    Add-Content $expandedMods '+TheLastMeridian-WorldStoryPreview';Refuses { ExpandedContext } 'default mod rejected in expanded profile';Set-Content $expandedMods ('+'+$expandedVariant.ModName)
    $savedExpanded=[IO.File]::ReadAllBytes($expandedWorld);Copy-Item $world $expandedWorld -Force
    Refuses { ExpandedContext } 'default world cannot satisfy expanded pin';[IO.File]::WriteAllBytes($expandedWorld,$savedExpanded)
    $variant=$expandedVariant;$context=[pscustomobject]@{Mo=[pscustomobject]@{GamePath=$game}}
    $ini=Join-Path $expandedProfile 'fallout4custom.ini';Set-Content $ini "[General]`nsStartingConsoleCommand=`nbAlwaysActive=0"
    $p=Get-WorldStoryStartupPlan $game -Expanded;Write-FreshDemoStartupBatch $p
    $note=[pscustomobject]@{Variant=$variant.Id;ProfileName=$variant.ProfileName;Ini=$ini;GameFolder=$game;StartupBefore='';ActiveBefore='0';Batch=$p}
    $journal=Join-Path $root $variant.JournalName;$note | ConvertTo-Json -Depth 4 | Set-Content $journal
    $otherJournal=Join-Path $root 'world-story.unfinished.json';Set-Content $otherJournal 'unrelated default note'
    $otherHash=(Get-FileHash $otherJournal).Hash
    Set-IniValue $ini General sStartingConsoleCommand $p.Command;Set-IniValue $ini General bAlwaysActive 1
    $iniHash=(Get-FileHash $ini).Hash;$batchHash=(Get-FileHash $p.Path).Hash;$noteHash=(Get-FileHash $journal).Hash
    foreach ($cross in @('variant','profile','batch','ini')) {
        $good=$note;$note=$good | ConvertTo-Json -Depth 4 | ConvertFrom-Json
        switch ($cross) {
            variant { $note.Variant='story' }
            profile { $note.ProfileName='TLM-World-Story-Preview' }
            batch { $note.Batch.Variant='story' }
            ini { $note.Ini=$defaultIni }
        }
        Refuses { & $actualFinally } "cross-variant $cross note refuses actual cleanup"
        Assert ((Get-FileHash $ini).Hash -eq $iniHash -and (Get-FileHash $p.Path).Hash -eq $batchHash -and (Get-FileHash $journal).Hash -eq $noteHash -and (Get-FileHash $defaultIni).Hash -eq $defaultIniHash) "cross-variant $cross preserves both profiles/batch/note"
        $note=$good
    }
    $variant=Get-WorldStoryVariant;$ini=$defaultIni;$context=[pscustomobject]@{Mo=[pscustomobject]@{GamePath=$root}}
    Refuses { & $actualFinally } 'expanded note cannot run through default actual cleanup'
    Assert ((Get-FileHash $note.Ini).Hash -eq $iniHash -and (Get-FileHash $p.Path).Hash -eq $batchHash -and (Get-FileHash $defaultIni).Hash -eq $defaultIniHash) 'reverse cross-variant refusal preserves both profiles/batch'
    $variant=$expandedVariant;$ini=$note.Ini;$context=[pscustomobject]@{Mo=[pscustomobject]@{GamePath=$game}}
    SetProcessFixture -CimRows @([pscustomobject]@{ProcessId=105;Name='Fallout4.exe'})
    Refuses { & $actualFinally } 'expanded residual process blocks actual cleanup'
    Assert ((Get-FileHash $ini).Hash -eq $iniHash -and (Get-FileHash $p.Path).Hash -eq $batchHash) 'expanded process guard preserves state'
    SetProcessFixture
    & $actualFinally
    Assert (-not (Test-Path $p.Path) -and -not (Test-Path $journal) -and (Get-FileHash $otherJournal).Hash -eq $otherHash) 'expanded recovery removes only its own batch/note'
    Assert ((Get-IniValue $ini General sStartingConsoleCommand) -ceq '' -and (Get-IniValue $ini General bAlwaysActive) -eq '0' -and (Get-FileHash $defaultIni).Hash -eq $defaultIniHash) 'expanded recovery restores only expanded settings'
    $legacyBatch=Get-WorldStoryStartupPlan $root;$legacyBatch.PSObject.Properties.Remove('Variant')
    $legacy=[pscustomobject]@{Ini=$defaultIni;GameFolder=$root;StartupBefore='';ActiveBefore='0';Batch=$legacyBatch}
    Assert-WorldStoryRecoveryNote $legacy $defaultIni $root
    Refuses { Assert-WorldStoryRecoveryNote $legacy $ini $game -Variant expanded } 'legacy default note never recovers as expanded'
    $variant=Get-WorldStoryVariant;$ini=$defaultIni;$context=[pscustomobject]@{Mo=[pscustomobject]@{GamePath=$root}}
    $note=$legacy;Write-FreshDemoStartupBatch $legacyBatch
    Set-IniValue $ini General sStartingConsoleCommand $legacyBatch.Command;Set-IniValue $ini General bAlwaysActive 1
    $journal=$otherJournal;$note | ConvertTo-Json -Depth 4 | Set-Content $journal
    & $actualFinally
    Assert (-not (Test-Path $legacyBatch.Path) -and -not (Test-Path $journal) -and (Get-FileHash $ini).Hash -eq $defaultIniHash) 'legacy untagged default recovery remains functional'
    $defaultPlan=Get-WorldStoryStartupPlan $game;$expandedPlan=Get-WorldStoryStartupPlan $game -Expanded
    Assert ($defaultPlan.Content -ceq $expandedPlan.Content -and $defaultPlan.Hash -ceq $expandedPlan.Hash -and $defaultPlan.Path -cne $expandedPlan.Path -and $defaultPlan.Variant -ceq 'story' -and $expandedPlan.Variant -ceq 'expanded') 'same fresh startup behavior with unique independently identified batches'
    $parameterNames=@($launcherAst.ParamBlock.Parameters | ForEach-Object { $_.Name.VariablePath.UserPath })
    Assert ('Expanded' -in $parameterNames -and 'ManifestPath' -notin $parameterNames -and 'ProfileName' -notin $parameterNames) 'launcher exposes fixed opt-in but no arbitrary manifest/profile override'
    foreach ($name in @('Play-WorldStory.ps1','World-Story.psm1')) {
        $tokens=$null;$errors=$null;[void][Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot "../$name"),[ref]$tokens,[ref]$errors)
        Assert ($errors.Count -eq 0) "parser $name"
    }
    Write-Host "$checks story launcher checks passed (fixtures only; no game/manager execution)"
} finally { Remove-Item -LiteralPath $root -Recurse -Force;Remove-Module World-Story }
