# Shared helpers for the Windows-side scripts in tools/win.
#
# Everything in this module only READS the machine. Nothing here changes the
# game folder, the registry, saves or load order.
#
# Status: the discovery logic was exercised on Linux PowerShell against a fake
# folder tree. It has NOT been run on a real Windows install yet; registry
# lookups in particular are untested.

Set-StrictMode -Version Latest

$script:Fallout4SteamAppId = '377160'
$script:DlcMasters = @(
    'DLCRobot.esm', 'DLCworkshop01.esm', 'DLCCoast.esm', 'DLCworkshop02.esm',
    'DLCworkshop03.esm', 'DLCNukaWorld.esm', 'DLCUltraHighResolution.esm'
)

function Get-RegistryValueSafe {
    param([string]$Path, [string]$Name)
    if (-not $IsWindows) { return $null }
    try {
        $item = Get-ItemProperty -Path $Path -ErrorAction Stop
        if ($item.PSObject.Properties.Name -contains $Name) { return $item.$Name }
    } catch { }
    return $null
}

function Get-SteamLibraryRoots {
    <# Steam's install folder plus every extra library listed in libraryfolders.vdf. #>
    param([string]$SteamRoot)
    $roots = New-Object System.Collections.Generic.List[string]
    if (-not $SteamRoot) {
        $SteamRoot = Get-RegistryValueSafe 'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam' 'InstallPath'
        if (-not $SteamRoot) { $SteamRoot = Get-RegistryValueSafe 'HKCU:\SOFTWARE\Valve\Steam' 'SteamPath' }
    }
    if (-not $SteamRoot -or -not (Test-Path -LiteralPath $SteamRoot)) { return @() }
    $roots.Add((Resolve-Path -LiteralPath $SteamRoot).Path)
    $vdf = Join-Path (Join-Path $SteamRoot 'steamapps') 'libraryfolders.vdf'
    if (Test-Path -LiteralPath $vdf) {
        foreach ($line in Get-Content -LiteralPath $vdf) {
            if ($line -match '^\s*"path"\s+"(.+)"\s*$') {
                $p = $Matches[1] -replace '\\\\', '\'
                if ((Test-Path -LiteralPath $p) -and -not ($roots -contains $p)) { $roots.Add($p) }
            }
        }
    }
    return $roots.ToArray()
}

function Find-Fallout4Installs {
    <#
      Returns one object per Fallout 4 install found: Store (Steam/GOG/Other),
      Root, and how it was found. Pass -ExtraRoot to add folders to check
      (also how this is tested off Windows).
    #>
    param([string]$SteamRoot, [string[]]$ExtraRoot = @())
    $found = [ordered]@{}

    function Add-Install([string]$Root, [string]$Store, [string]$How) {
        if (-not $Root) { return }
        if (-not (Test-Path -LiteralPath (Join-Path $Root 'Fallout4.exe'))) { return }
        $key = (Resolve-Path -LiteralPath $Root).Path.TrimEnd('\', '/')
        if (-not $found.Contains($key)) {
            $found[$key] = [pscustomobject]@{ Store = $Store; Root = $key; FoundBy = $How }
        }
    }

    foreach ($lib in Get-SteamLibraryRoots -SteamRoot $SteamRoot) {
        $apps = Join-Path $lib 'steamapps'
        $manifest = Join-Path $apps "appmanifest_$($script:Fallout4SteamAppId).acf"
        $dir = 'Fallout 4'
        if (Test-Path -LiteralPath $manifest) {
            foreach ($line in Get-Content -LiteralPath $manifest) {
                if ($line -match '^\s*"installdir"\s+"(.+)"\s*$') { $dir = $Matches[1] }
            }
        }
        Add-Install (Join-Path (Join-Path $apps 'common') $dir) 'Steam' "Steam library $lib"
    }

    if ($IsWindows) {
        foreach ($base in 'HKLM:\SOFTWARE\WOW6432Node\GOG.com\Games', 'HKLM:\SOFTWARE\GOG.com\Games') {
            if (Test-Path $base) {
                foreach ($k in Get-ChildItem $base -ErrorAction SilentlyContinue) {
                    $name = Get-RegistryValueSafe $k.PSPath 'gameName'
                    if ($name -and $name -like 'Fallout 4*') {
                        Add-Install (Get-RegistryValueSafe $k.PSPath 'path') 'GOG' "GOG registry ($name)"
                    }
                }
            }
        }
        Add-Install (Get-RegistryValueSafe 'HKLM:\SOFTWARE\WOW6432Node\Bethesda Softworks\Fallout4' 'Installed Path') 'Other' 'Bethesda registry key'
    }

    foreach ($r in $ExtraRoot) {
        $store = 'Other'
        if (Test-Path -LiteralPath (Join-Path $r 'Galaxy64.dll')) { $store = 'GOG' }
        elseif (Test-Path -LiteralPath (Join-Path $r 'steam_api64.dll')) { $store = 'Steam' }
        Add-Install $r $store 'given on the command line'
    }

    # An install found only through the Bethesda key still gets a store guess.
    foreach ($i in $found.Values) {
        if ($i.Store -eq 'Other') {
            if (Test-Path -LiteralPath (Join-Path $i.Root 'Galaxy64.dll')) { $i.Store = 'GOG' }
            elseif (Test-Path -LiteralPath (Join-Path $i.Root 'steam_api64.dll')) { $i.Store = 'Steam' }
        }
    }
    return @($found.Values)
}

function Get-ExeVersion {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    try {
        $v = (Get-Item -LiteralPath $Path).VersionInfo
        if ($v.FileVersion) { return ($v.FileVersion -replace ',\s*', '.').Trim() }
        if ($v.ProductVersion) { return $v.ProductVersion.Trim() }
    } catch { }
    return 'present (version unreadable)'
}

function Get-Fallout4InstallInfo {
    <# Everything the build needs to know about one install folder. Read-only. #>
    param([Parameter(Mandatory)][string]$Root)
    $data = Join-Path $Root 'Data'
    $src = Join-Path (Join-Path $data 'Scripts') 'Source'
    $base = Join-Path $src 'Base'
    $compilerDir = Join-Path $Root 'Papyrus Compiler'

    $basePsc = 0
    if (Test-Path -LiteralPath $base) {
        $basePsc = @(Get-ChildItem -LiteralPath $base -Filter '*.psc' -File -ErrorAction SilentlyContinue).Count
    }
    $plugins = @()
    if (Test-Path -LiteralPath $data) {
        $plugins = @(Get-ChildItem -LiteralPath $data -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Extension -in '.esp', '.esl', '.esm' } | ForEach-Object Name)
    }
    $vanilla = @('Fallout4.esm') + $script:DlcMasters
    $gameVersion = Get-ExeVersion (Join-Path $Root 'Fallout4.exe')

    [pscustomobject]@{
        Root               = $Root
        GameVersion        = $gameVersion
        GameGeneration     = Get-GameGeneration $gameVersion
        CreationKitVersion = Get-ExeVersion (Join-Path $Root 'CreationKit.exe')
        PapyrusCompiler    = Test-Path -LiteralPath (Join-Path $compilerDir 'PapyrusCompiler.exe')
        FlagsFile          = Test-Path -LiteralPath (Join-Path $base 'Institute_Papyrus_Flags.flg')
        BaseSourceZip      = Test-Path -LiteralPath (Join-Path $base 'Base.zip')
        BaseSourceCount    = $basePsc
        F4SEVersion        = Get-ExeVersion (Join-Path $Root 'f4se_loader.exe')
        DlcPresent         = @($script:DlcMasters | Where-Object { Test-Path -LiteralPath (Join-Path $data $_) })
        FalloutLondon      = Test-Path -LiteralPath (Join-Path $data 'LondonWorldSpace.esm')
        CreationClubCount  = @($plugins | Where-Object { $_ -like 'cc*' }).Count
        OtherPlugins       = @($plugins | Where-Object { ($vanilla -notcontains $_) -and ($_ -notlike 'cc*') })
        TlmInstalled       = Test-Path -LiteralPath (Join-Path $data 'TheLastMeridian.esp')
        ModManagerHint     = Get-ModManagerHint $Root
    }
}

function Get-GameGeneration {
    param([string]$Version)
    if (-not $Version -or $Version -notmatch '^(\d+)\.(\d+)\.(\d+)') { return 'unknown' }
    $major = [int]$Matches[1]; $minor = [int]$Matches[2]; $build = [int]$Matches[3]
    if ($major -eq 1 -and $minor -eq 10 -and $build -le 163) { return 'pre-next-gen (1.10.163 or earlier)' }
    if ($major -eq 1 -and $minor -eq 10) { return 'next-gen update (1.10.9xx)' }
    return 'later than 1.10 (check the Creation Kit build matches)'
}

function Get-ModManagerHint {
    param([string]$Root)
    $hints = @()
    if (Test-Path -LiteralPath (Join-Path $Root 'ModOrganizer.ini')) { $hints += 'Mod Organizer 2 (portable, in the game folder)' }
    if (Test-Path -LiteralPath (Join-Path (Join-Path $Root 'Data') '__vortex_staging_folder')) { $hints += 'Vortex staging folder in Data' }
    if (Test-Path -LiteralPath (Join-Path (Join-Path $Root 'Data') 'vortex.deployment.json')) { $hints += 'Vortex deployment' }
    if ($hints.Count -eq 0) { return 'none detected in the game folder' }
    return ($hints -join '; ')
}

function Get-IniValue {
    param([string]$Path, [string]$Section, [string]$Key)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    $in = $false
    foreach ($line in Get-Content -LiteralPath $Path) {
        $t = $line.Trim()
        if ($t -match '^\[(.+)\]$') { $in = ($Matches[1] -ieq $Section); continue }
        if ($in -and $t -match '^([^=;]+?)\s*=\s*(.*)$' -and ($Matches[1].Trim() -ieq $Key)) { return $Matches[2].Trim() }
    }
    return $null
}

function Get-Fallout4UserState {
    <#
      Settings, saves and load order live outside the game folder and are, as
      far as we know, SHARED by every Fallout 4 install on the machine.
      Reports counts and dates only; no save names or contents.
    #>
    param([string]$DocumentsRoot, [string]$LocalAppDataRoot)
    if (-not $DocumentsRoot) { $DocumentsRoot = [Environment]::GetFolderPath('MyDocuments') }
    if (-not $LocalAppDataRoot) { $LocalAppDataRoot = [Environment]::GetFolderPath('LocalApplicationData') }
    $my = Join-Path (Join-Path $DocumentsRoot 'My Games') 'Fallout4'
    $custom = Join-Path $my 'Fallout4Custom.ini'
    $saves = Join-Path $my 'Saves'
    $saveFiles = @()
    if (Test-Path -LiteralPath $saves) { $saveFiles = @(Get-ChildItem -LiteralPath $saves -Filter '*.fos' -File -ErrorAction SilentlyContinue) }
    $newest = $null
    if ($saveFiles.Count -gt 0) { $newest = ($saveFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime.ToString('yyyy-MM-dd') }

    $appDirs = @()
    if ($LocalAppDataRoot -and (Test-Path -LiteralPath $LocalAppDataRoot)) {
        $appDirs = @(Get-ChildItem -LiteralPath $LocalAppDataRoot -Directory -Filter 'Fallout4*' -ErrorAction SilentlyContinue | ForEach-Object FullName)
    }
    $pluginLists = @()
    foreach ($d in $appDirs) {
        $f = Join-Path $d 'plugins.txt'
        if (Test-Path -LiteralPath $f) {
            $lines = @(Get-Content -LiteralPath $f | Where-Object { $_ -and -not $_.StartsWith('#') })
            $pluginLists += [pscustomobject]@{
                Path       = $f
                Active     = @($lines | Where-Object { $_.StartsWith('*') }).Count
                Listed     = $lines.Count
                TlmListed  = [bool](@($lines | Where-Object { $_ -match 'TheLastMeridian\.esp' }).Count)
                TlmActive  = [bool](@($lines | Where-Object { $_ -match '^\*TheLastMeridian\.esp' }).Count)
            }
        }
    }

    [pscustomobject]@{
        MyGamesFolder        = $my
        MyGamesExists        = Test-Path -LiteralPath $my
        CustomIniExists      = Test-Path -LiteralPath $custom
        InvalidateOlderFiles = Get-IniValue $custom 'Archive' 'bInvalidateOlderFiles'
        ResourceDataDirs     = Get-IniValue $custom 'Archive' 'sResourceDataDirsFinal'
        PapyrusLogging       = Get-IniValue $custom 'Papyrus' 'bEnableLogging'
        SaveCount            = $saveFiles.Count
        NewestSave           = $newest
        PapyrusLogExists     = Test-Path -LiteralPath (Join-Path (Join-Path (Join-Path $my 'Logs') 'Script') 'Papyrus.0.log')
        PluginLists          = $pluginLists
    }
}

function Select-DevInstall {
    <#
      Picks the install to build against: the one given, else the only Steam
      install that has the Creation Kit and is not a Fallout London install.
      Throws with an explanation when the choice is not obvious.
    #>
    param([string]$GameRoot, [string]$SteamRoot)
    if ($GameRoot) {
        if (-not (Test-Path -LiteralPath (Join-Path $GameRoot 'Fallout4.exe'))) { throw "No Fallout4.exe in $GameRoot" }
        return (Resolve-Path -LiteralPath $GameRoot).Path
    }
    $all = @(Find-Fallout4Installs -SteamRoot $SteamRoot)
    if ($all.Count -eq 0) { throw 'No Fallout 4 install found. Pass -GameRoot <folder containing Fallout4.exe>.' }
    $good = @($all | Where-Object {
            (Test-Path -LiteralPath (Join-Path $_.Root 'CreationKit.exe')) -and
            -not (Test-Path -LiteralPath (Join-Path (Join-Path $_.Root 'Data') 'LondonWorldSpace.esm'))
        })
    if ($good.Count -eq 1) { return $good[0].Root }
    $list = ($all | ForEach-Object { "  $($_.Store): $($_.Root)" }) -join "`n"
    throw "Cannot choose an install automatically. Pass -GameRoot. Found:`n$list"
}

Export-ModuleMember -Function Find-Fallout4Installs, Get-Fallout4InstallInfo, Get-Fallout4UserState,
    Select-DevInstall, Get-SteamLibraryRoots, Get-IniValue, Get-ExeVersion, Get-GameGeneration
