param([string]$WorldArtifact, [string]$CoreArtifact)
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot '../Tlm.psm1') -Force
Import-Module (Join-Path $PSScriptRoot '../World-Preview.psm1') -Force
$root = Join-Path ([IO.Path]::GetTempPath()) ('TlmWorldTest_' + [guid]::NewGuid().ToString('N'))
[void](New-Item -ItemType Directory -Path $root)
$checks = 0
function Assert($condition, $label) { if (-not $condition) { throw $label }; $script:checks++ }
function Refuses([scriptblock]$action, $label) { $failed = $false; try { & $action } catch { $failed = $true }; Assert $failed $label }
try {
    $p = Get-WorldStartupPlan $root
    $lines = @($p.Content.TrimEnd().Split("`n") | ForEach-Object { $_.TrimEnd("`r") })
    Assert ($lines.Count -eq 8 -and $lines[0] -ceq 'coc TLM_WS_Clearing') 'world entry plus exactly seven writes'
    $i = 1
    foreach ($av in @('Strength','Perception','Endurance','Charisma','Intelligence','Agility','Luck')) {
        Assert ($lines[$i] -ceq "player.setav $av 4") "balanced $av"; $i++
    }
    $ini = Join-Path $root 'fallout4custom.ini'
    Set-Content $ini "[General]`r`nsStartingConsoleCommand=`r`nbAlwaysActive=0`r`nUnrelated=keep"
    $note = [pscustomobject]@{ Ini=$ini; GameFolder=$root; StartupBefore=''; ActiveBefore='0'; Batch=$p }
    Write-FreshDemoStartupBatch $p
    Assert ((Get-FileHash $p.Path).Hash -eq $p.Hash) 'world content hash recomputed'
    Set-IniValue $ini General sStartingConsoleCommand $p.Command
    Set-IniValue $ini General bAlwaysActive 1
    # Recovery uses serialized ownership, as the next invocation would.
    Restore-WorldPreviewState ($note | ConvertTo-Json -Depth 4 | ConvertFrom-Json)
    Assert (-not (Test-Path $p.Path)) 'owned batch removed'
    Assert ((Get-IniValue $ini General sStartingConsoleCommand) -eq '') 'startup restored'
    Assert ((Get-IniValue $ini General bAlwaysActive) -eq '0') 'activity restored'
    Assert ((Get-IniValue $ini General Unrelated) -eq 'keep') 'unrelated settings preserved'
    $p = Get-WorldStartupPlan $root; $note.Batch=$p
    [IO.File]::WriteAllText($p.Path, $p.Content, [Text.Encoding]::ASCII)
    Refuses { Write-FreshDemoStartupBatch $p } 'existing identical collision refuses'
    Restore-WorldPreviewState ($note | ConvertTo-Json -Depth 4 | ConvertFrom-Json)
    Assert (Test-Path $p.Path) 'rejected existing file survives integrated finally/recovery'
    Remove-Item -LiteralPath $p.Path
    $p = Get-WorldStartupPlan $root; $note.Batch=$p
    Write-FreshDemoStartupBatch $p
    Add-Content $p.Path 'owner changed'
    Refuses { Restore-WorldPreviewState $note } 'changed owned batch refuses deletion'
    Assert (Test-Path $p.Path) 'changed batch preserved'
    Remove-Item -LiteralPath $p.Path
    $p = Get-WorldStartupPlan $root; $note.Batch=$p
    Set-Content $p.Path 'ambiguous interrupted file'
    Refuses { Restore-WorldPreviewState $note } 'planned present ambiguous interrupted ownership refuses'
    Assert (Test-Path $p.Path) 'ambiguous file preserved'
    Refuses { Get-WorldPreviewContext -ModOrganizerRoot $root -ProfileName 'Default' } 'owner profile refused'
    Refuses { Get-WorldPreviewContext -ModOrganizerRoot $root } 'absent manager/profile refused'
    if ($WorldArtifact -and $CoreArtifact) {
        $mo = Join-Path $root 'manager'; $game = Join-Path $root 'game'
        $profile = Join-Path $mo 'profiles/TLM-World-Preview'
        $world = Join-Path $mo 'mods/TheLastMeridian-WorldSliceQA/TLMWorldSlice.esp'
        $core = Join-Path $mo 'mods/TheLastMeridian-Dev/TheLastMeridian.esp'
        foreach ($folder in @($game,$profile,(Split-Path $world),(Split-Path $core))) { [void](New-Item -ItemType Directory -Force $folder) }
        Copy-Item -LiteralPath $WorldArtifact -Destination $world
        Copy-Item -LiteralPath $CoreArtifact -Destination $core
        Set-Content (Join-Path $mo 'ModOrganizer.ini') "[General]`ngamePath=$game"
        $settings = Join-Path $profile 'settings.ini'; $mods = Join-Path $profile 'modlist.txt'
        Set-Content $settings "[General]`nLocalSaves=true`nLocalSettings=true"
        Set-Content $mods "+TheLastMeridian-Dev`n+TheLastMeridian-WorldSliceQA"
        Set-Content (Join-Path $profile 'plugins.txt') "*TheLastMeridian.esp`n*TLMWorldSlice.esp"
        $ctx = Get-WorldPreviewContext $mo
        Assert ($ctx.World -eq $world) 'actual artifact/context fixture accepted'
        Set-IniValue $settings General LocalSaves false
        Refuses { Get-WorldPreviewContext $mo } 'shared saves refused'
        Set-IniValue $settings General LocalSaves true
        Add-Content $mods '+TheLastMeridian-WorldProbe'
        Refuses { Get-WorldPreviewContext $mo } 'private probe mod refused'
        Set-Content $mods "+TheLastMeridian-Dev`n+TheLastMeridian-WorldSliceQA"
        $probe = Join-Path (Split-Path $core) 'Scripts/TLM/Core.pex'
        [void](New-Item -ItemType Directory -Force (Split-Path $probe))
        Set-Content $probe 'TLM_WorldNative'
        Refuses { Get-WorldPreviewContext $mo } 'private script override refused'
        Remove-Item $probe
        Set-PluginGlobal $core TLM_G_DevScenario 12
        Refuses { Get-WorldPreviewContext $mo } 'nonzero scenario refused'
        Set-PluginGlobal $core TLM_G_DevScenario 0
        Add-Content $world 'changed'
        Refuses { Get-WorldPreviewContext $mo } 'changed world artifact refused'
    }
    foreach ($file in @('../Play-World.ps1','../World-Preview.psm1')) {
        $tokens=$null; $errors=$null
        [void][Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot $file),[ref]$tokens,[ref]$errors)
        Assert ($errors.Count -eq 0) "parser $file"
    }
    Write-Host "$checks world launcher checks passed"
} finally { Remove-Item -LiteralPath $root -Recurse -Force }
