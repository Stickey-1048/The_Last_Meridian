Set-StrictMode -Version Latest
Import-Module (Join-Path $PSScriptRoot 'Tlm.psm1')

function Get-WorldStoryContext {
    param([string]$ModOrganizerRoot, [string]$ProfileName = 'TLM-World-Story-Preview',
        [string]$ManifestPath = (Join-Path $PSScriptRoot 'world-story-artifact.json'))
    # ManifestPath permits isolated fixture testing; the launcher exposes no override.
    if ($ProfileName -cne 'TLM-World-Story-Preview') { throw 'Use the dedicated TLM-World-Story-Preview profile only.' }
    $manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
    $runtime = @($manifest.runtime.PSObject.Properties)
    if ($manifest.schema -ne 1 -or $runtime.Count -ne 19 -or
        $manifest.worldSha256 -notmatch '^[A-Fa-f0-9]{64}$' -or $manifest.masterSha256 -notmatch '^[A-Fa-f0-9]{64}$') { throw 'Story artifact manifest is incomplete.' }
    foreach ($item in $runtime) {
        if ($item.Name -notmatch '^[A-Za-z0-9_]+\.pex$' -or "$($item.Value)" -notmatch '^[A-Fa-f0-9]{64}$') { throw 'Unsafe runtime manifest entry.' }
    }
    foreach ($name in @('Core.pex','Act1Walk.pex','MQ01Quest.pex','Act1Guide.pex','WorldEntry.pex','WorldEntryPlayer.pex')) {
        if ($name -notin $runtime.Name) { throw "Missing required runtime pin: $name" }
    }
    $mo = Get-ModOrganizerInfo -Root $ModOrganizerRoot
    if (-not $mo -or -not $mo.GamePath -or (Test-FalloutLondonFolder $mo.GamePath)) { throw 'A managed base-game installation is required.' }
    $profile = Join-Path $mo.ProfilesDirectory $ProfileName
    if (-not (Test-Path -LiteralPath $profile -PathType Container)) { throw 'Dedicated story profile is not prepared. No installation is performed.' }
    foreach ($key in @('LocalSaves','LocalSettings')) {
        if ((Get-IniValue (Join-Path $profile 'settings.ini') General $key) -ine 'true') { throw "Dedicated profile requires $key=true." }
    }
    $allowed = @('TheLastMeridian-WorldStoryPreview','F4SE Scripts 0.6.23','FallUI - Workbench','Mod Configuration Menu')
    $enabled = @(Read-RawLines (Join-Path $profile 'modlist.txt') | Where-Object { $_.StartsWith('+') } | ForEach-Object { $_.Substring(1) })
    if (@($enabled | Select-Object -Unique).Count -ne $enabled.Count) { throw 'Duplicate enabled mod entries.' }
    foreach ($name in $enabled) { if ($name -notin $allowed) { throw "Unreviewed/private mod enabled in story profile: $name" } }
    if ('TheLastMeridian-WorldStoryPreview' -notin $enabled) { throw 'The isolated story mod is not enabled.' }
    $plugins = @(Read-RawLines (Join-Path $profile 'plugins.txt') | Where-Object { $_.StartsWith('*') } | ForEach-Object { $_.Substring(1) })
    if ($plugins.Count -ne 2 -or $plugins[0] -cne 'TheLastMeridian.esp' -or $plugins[1] -cne 'TLMWorldSlice.esp') { throw 'Story profile must activate only the master then the world addon.' }
    $story = Join-Path $mo.ModsDirectory 'TheLastMeridian-WorldStoryPreview'
    $world = Join-Path $story 'TLMWorldSlice.esp'; $core = Join-Path $story 'TheLastMeridian.esp'
    foreach ($pair in @(@($world,$manifest.worldSha256),@($core,$manifest.masterSha256))) {
        if (-not (Test-Path -LiteralPath $pair[0] -PathType Leaf) -or (Get-FileHash -LiteralPath $pair[0] -Algorithm SHA256).Hash -ne $pair[1]) { throw "Story plugin absent or differs from reviewed artifact: $($pair[0])" }
    }
    if ((Get-PluginGlobal -Path $core -EditorId TLM_G_DevScenario) -ne 0) { throw 'Scenario must already be zero; launcher never changes a plugin.' }
    $runtimeRoot = Join-Path $story 'Scripts/TLM'
    $present = @(Get-ChildItem -LiteralPath $runtimeRoot -File -Filter '*.pex')
    if ($present.Count -ne 19) { throw 'Story runtime must contain exactly the 19 reviewed scripts.' }
    foreach ($item in $runtime) {
        $file = Join-Path $runtimeRoot $item.Name
        if (-not (Test-Path -LiteralPath $file -PathType Leaf) -or (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash -ne $item.Value) { throw "Story runtime differs from reviewed bundle: $file" }
    }
    # One private mod owns all mutable Meridian files, removing priority ambiguity.
    $otherRoots = @($enabled | Where-Object { $_ -ne 'TheLastMeridian-WorldStoryPreview' } | ForEach-Object { Join-Path $mo.ModsDirectory $_ }) + @((Join-Path $mo.Root 'overwrite'),(Join-Path $mo.GamePath 'Data'))
    foreach ($folder in @($story) + $otherRoots) {
        if (-not (Test-Path -LiteralPath $folder)) { continue }
        if (@(Get-ChildItem -LiteralPath $folder -File -Filter '*.ba2' | Where-Object { $_.Name -match '^(TLM|TheLastMeridian)' }).Count) { throw "Unreviewed Meridian archive may override scripts: $folder" }
        if (Test-SamePath $folder $story) { continue }
        foreach ($name in @('TLMWorldSlice.esp','TheLastMeridian.esp')) {
            if (Test-Path -LiteralPath (Join-Path $folder $name)) { throw "Conflicting Meridian plugin outside isolated story mod: $folder" }
        }
        $scripts = Join-Path $folder 'Scripts/TLM'
        if ((Test-Path -LiteralPath $scripts) -and @(Get-ChildItem -LiteralPath $scripts -File -Filter '*.pex').Count) { throw "Conflicting/private Meridian scripts outside isolated story mod: $scripts" }
    }
    $gameExe = Join-Path $mo.GamePath 'Fallout4.exe'
    if (-not (Test-Path -LiteralPath $gameExe -PathType Leaf)) { throw 'Managed game executable missing.' }
    return [pscustomobject]@{Mo=$mo; Profile=$profile; World=$world; GameExe=$gameExe; RequiresF4SE=(@($enabled | Where-Object { $_ -in @('FallUI - Workbench','Mod Configuration Menu') }).Count -gt 0)}
}

function Get-WorldStoryStartupPlan {
    param([string]$GameFolder)
    $plan = Get-FreshDemoStartupPlan -GameFolder $GameFolder
    if (-not $plan.Content.StartsWith("coc qasmoke`r`n")) { throw 'Unexpected fresh startup template.' }
    $plan.Content = $plan.Content.Replace("coc qasmoke`r`n", "coc TLM_WS_Clearing`r`n") + "cqf TLM_WS_Entry QueueFreshEntry`r`n"
    $sha = [Security.Cryptography.SHA256]::Create()
    try { $plan.Hash = [BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::ASCII.GetBytes($plan.Content))).Replace('-','') }
    finally { $sha.Dispose() }
    return $plan
}

function Restore-WorldStoryState {
    param($Note)
    $errors = @()
    foreach ($pair in @(@('sStartingConsoleCommand','StartupBefore'),@('bAlwaysActive','ActiveBefore'))) {
        try {
            $value = [string]$Note.($pair[1]); Set-IniValue $Note.Ini General $pair[0] $value
            if ([string](Get-IniValue $Note.Ini General $pair[0]) -cne $value) { throw 'read-back mismatch' }
        } catch { $errors += "$($pair[0]): $($_.Exception.Message)" }
    }
    try { [void](Remove-FreshDemoStartupBatch -Plan $Note.Batch -GameFolder $Note.GameFolder) } catch { $errors += $_.Exception.Message }
    if ($errors.Count) { throw ('Story startup cleanup incomplete; keep ownership note: ' + ($errors -join '; ')) }
}
function Get-WorldStoryStartupState {
    param([string]$Ini)
    $startup=[string](Get-IniValue $Ini General sStartingConsoleCommand)
    if ($startup.Trim()) { throw 'Dedicated story profile has an existing startup command; it was left unchanged.' }
    $active=Get-IniValue $Ini General bAlwaysActive
    if ($null -eq $active -or "$active" -eq '') { $active='0' }
    return [pscustomobject]@{Startup=$startup;Active="$active"}
}
Export-ModuleMember -Function Get-WorldStoryContext, Get-WorldStoryStartupPlan, Restore-WorldStoryState, Get-WorldStoryStartupState
