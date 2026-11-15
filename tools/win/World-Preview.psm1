Set-StrictMode -Version Latest
Import-Module (Join-Path $PSScriptRoot 'Tlm.psm1')

function Get-WorldPreviewContext {
    param([string]$ModOrganizerRoot, [string]$ProfileName = 'TLM-World-Preview')
    if ($ProfileName -cne 'TLM-World-Preview') { throw 'Use the dedicated TLM-World-Preview profile only.' }
    $mo = Get-ModOrganizerInfo -Root $ModOrganizerRoot
    if (-not $mo -or -not $mo.GamePath -or (Test-FalloutLondonFolder $mo.GamePath)) { throw 'A managed base-game installation is required.' }
    $profile = Join-Path $mo.ProfilesDirectory $ProfileName
    if (-not (Test-Path -LiteralPath $profile -PathType Container)) { throw 'TLM-World-Preview is not prepared. This launcher does not create/install profiles or mods.' }
    foreach ($key in @('LocalSaves', 'LocalSettings')) {
        if ((Get-IniValue (Join-Path $profile 'settings.ini') 'General' $key) -ine 'true') { throw "Dedicated profile requires $key=true." }
    }
    $allowed = @('TheLastMeridian-Dev', 'TheLastMeridian-WorldSliceQA', 'F4SE Scripts 0.6.23', 'FallUI - Workbench', 'Mod Configuration Menu')
    $enabled = @(Read-RawLines (Join-Path $profile 'modlist.txt') | Where-Object { $_.StartsWith('+') } | ForEach-Object { $_.Substring(1) })
    foreach ($name in $enabled) { if ($name -notin $allowed) { throw "Unreviewed/private mod enabled in world preview: $name" } }
    foreach ($required in @('TheLastMeridian-Dev', 'TheLastMeridian-WorldSliceQA')) { if ($required -notin $enabled) { throw "Required installed mod is not enabled: $required" } }
    $plugins = @(Read-RawLines (Join-Path $profile 'plugins.txt') | Where-Object { $_.StartsWith('*') } | ForEach-Object { $_.Substring(1) })
    foreach ($required in @('TheLastMeridian.esp', 'TLMWorldSlice.esp')) { if ($required -notin $plugins) { throw "Required plugin is not active: $required" } }
    foreach ($name in $plugins) { if ($name -notin @('TheLastMeridian.esp', 'TLMWorldSlice.esp')) { throw "Unreviewed plugin active: $name" } }
    $world = Join-Path (Join-Path $mo.ModsDirectory 'TheLastMeridian-WorldSliceQA') 'TLMWorldSlice.esp'
    $expected = '661E501331B40269B8A14DAD818D646BFCF0F4EB14D0A78F39CA522A2B6C0A3C'
    if (-not (Test-Path -LiteralPath $world) -or (Get-FileHash -LiteralPath $world -Algorithm SHA256).Hash -ne $expected) { throw 'World build is absent or differs from the reviewed 1583 couch-facing artifact.' }
    $core = Join-Path (Join-Path $mo.ModsDirectory 'TheLastMeridian-Dev') 'TheLastMeridian.esp'
    if ((Get-PluginGlobal -Path $core -EditorId 'TLM_G_DevScenario') -ne 0) { throw 'TLM scenario must already be zero; the world launcher never changes the plugin.' }
    $roots = @($enabled | ForEach-Object { Join-Path $mo.ModsDirectory $_ }) + @((Join-Path $mo.Root 'overwrite'), (Join-Path $mo.GamePath 'Data'))
    foreach ($folder in $roots) {
        $otherWorld = Join-Path $folder 'TLMWorldSlice.esp'
        if ((Test-Path -LiteralPath $otherWorld -PathType Leaf) -and (Get-FileHash -LiteralPath $otherWorld).Hash -ne $expected) { throw "Conflicting world plugin: $otherWorld" }
        $otherCore = Join-Path $folder 'TheLastMeridian.esp'
        if ((Test-Path -LiteralPath $otherCore -PathType Leaf) -and (Get-PluginGlobal -Path $otherCore -EditorId 'TLM_G_DevScenario') -ne 0) { throw "Nonzero scenario in plugin override: $otherCore" }
        foreach ($script in @('Core.pex', 'Act1Walk.pex')) {
            $file = Join-Path $folder (Join-Path 'Scripts\TLM' $script)
            if (Test-Path -LiteralPath $file -PathType Leaf) {
                $text = [System.Text.Encoding]::UTF8.GetString([System.IO.File]::ReadAllBytes($file))
                if ($text -match 'TLM_WorldNative|CaptureBaseline|CraftSmoke|WorldProbeTimer') { throw "Private probe script detected: $file" }
            }
        }
    }
    return [pscustomobject]@{ Mo = $mo; Profile = $profile; World = $world; GameExe = (Join-Path $mo.GamePath 'Fallout4.exe') }
}

function Get-WorldStartupPlan {
    param([string]$GameFolder)
    $plan = Get-FreshDemoStartupPlan -GameFolder $GameFolder
    if (-not $plan.Content.StartsWith("coc qasmoke`r`n")) { throw 'Unexpected fresh startup template.' }
    $plan.Content = $plan.Content.Replace("coc qasmoke`r`n", "coc TLM_WS_Clearing`r`n")
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { $plan.Hash = [System.BitConverter]::ToString($sha.ComputeHash([System.Text.Encoding]::ASCII.GetBytes($plan.Content))).Replace('-', '') }
    finally { $sha.Dispose() }
    return $plan
}

function Restore-WorldPreviewState {
    param($Note)
    $errors = @()
    foreach ($pair in @(@('sStartingConsoleCommand', 'StartupBefore'), @('bAlwaysActive', 'ActiveBefore'))) {
        try {
            $value = [string]$Note.($pair[1])
            Set-IniValue $Note.Ini 'General' $pair[0] $value
            if ([string](Get-IniValue $Note.Ini 'General' $pair[0]) -cne $value) { throw 'read-back mismatch' }
        } catch { $errors += "$($pair[0]): $($_.Exception.Message)" }
    }
    try { [void](Remove-FreshDemoStartupBatch -Plan $Note.Batch -GameFolder $Note.GameFolder) } catch { $errors += $_.Exception.Message }
    if ($errors.Count) { throw ('World preview cleanup incomplete; keep its ownership note: ' + ($errors -join '; ')) }
}
Export-ModuleMember -Function Get-WorldPreviewContext, Get-WorldStartupPlan, Restore-WorldPreviewState


