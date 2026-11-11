# Shared helpers for the Windows-side scripts in tools/win.
#
# Everything in this module only READS the machine. Nothing here changes the
# game folder, the registry, saves or load order.
#
# Status: first ran on a real Windows PC (Windows PowerShell 5.1) on 2026-11-11
# through Run-FirstBuild.ps1; the installs, the Mod Organizer instance and the
# Creation Kit were found. Functions added after that run (Vortex, GOG product
# names, settings folders, user-folder redaction) have only been exercised on
# Linux PowerShell 7 against stand-in folder trees.

Set-StrictMode -Version Latest

# Windows PowerShell 5.1 has no $IsWindows variable; it only runs on Windows.
$script:OnWindows = if ($PSVersionTable.PSEdition -eq 'Desktop') { $true } else { [bool](Get-Variable -Name IsWindows -ValueOnly -ErrorAction SilentlyContinue) }

$script:Fallout4SteamAppId = '377160'
$script:DlcMasters = @(
    'DLCRobot.esm', 'DLCworkshop01.esm', 'DLCCoast.esm', 'DLCworkshop02.esm',
    'DLCworkshop03.esm', 'DLCNukaWorld.esm', 'DLCUltraHighResolution.esm'
)

function Hide-UserFolder {
    <#
      Replaces the Windows user folder (C:\Users\<name>) with %USERPROFILE%, in
      either slash style. The folder name identifies the account, and scan
      output may be pasted into a chat or committed to a public repository.
    #>
    param([string]$Text)
    $home_ = $env:USERPROFILE
    if (-not $home_ -or -not $Text) { return $Text }
    $ignoreCase = [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
    foreach ($form in @($home_, ($home_ -replace '\\', '/'), ($home_ -replace '\\', '\\'))) {
        $Text = [regex]::Replace($Text, [regex]::Escape($form), '%USERPROFILE%', $ignoreCase)
    }
    return $Text
}

function Invoke-Native {
    <#
      Runs a program and returns its exit code and all output lines.
      Windows PowerShell 5.1 turns anything a program writes to its error
      stream into a terminating error when $ErrorActionPreference is 'Stop',
      so the preference is relaxed for the duration of the call.
    #>
    param([Parameter(Mandatory)][string]$Exe, [string[]]$Arguments = @())
    $ErrorActionPreference = 'Continue'
    try {
        $out = & $Exe @Arguments 2>&1 | ForEach-Object { "$_" }
        return [pscustomobject]@{ ExitCode = $LASTEXITCODE; Output = @($out); Found = $true }
    } catch [System.Management.Automation.CommandNotFoundException] {
        return [pscustomobject]@{ ExitCode = -1; Output = @("$Exe was not found"); Found = $false }
    }
}

function Get-SteamAppState {
    <#
      Reads Steam's own record of an app (appmanifest_<id>.acf) from every
      library. StateFlags 4 means fully installed. Read-only.
    #>
    param([Parameter(Mandatory)][string]$AppId, [string]$SteamRoot, [string[]]$ExtraLibrary = @())
    $libs = @(Get-SteamLibraryRoots -SteamRoot $SteamRoot) + @($ExtraLibrary | Where-Object { $_ -and (Test-Path -LiteralPath $_) })
    foreach ($lib in ($libs | Select-Object -Unique)) {
        $manifest = Join-Path (Join-Path $lib 'steamapps') "appmanifest_$AppId.acf"
        if (-not (Test-Path -LiteralPath $manifest)) { continue }
        $v = @{}
        foreach ($line in Get-Content -LiteralPath $manifest) {
            if ($line -match '^\s*"(\w+)"\s+"(.*)"\s*$') { if (-not $v.ContainsKey($Matches[1])) { $v[$Matches[1]] = $Matches[2] } }
        }
        $total = 0L; $done = 0L
        if ($v.ContainsKey('BytesToDownload')) { [void][long]::TryParse($v['BytesToDownload'], [ref]$total) }
        if ($v.ContainsKey('BytesDownloaded')) { [void][long]::TryParse($v['BytesDownloaded'], [ref]$done) }
        $flags = if ($v.ContainsKey('StateFlags')) { $v['StateFlags'] } else { '' }
        $dir = if ($v.ContainsKey('installdir')) { $v['installdir'] } else { '' }
        $percent = $null
        if ($total -gt 0) { $percent = [int][math]::Floor(100.0 * $done / $total) }
        return [pscustomobject]@{
            AppId      = $AppId
            Name       = if ($v.ContainsKey('name')) { $v['name'] } else { '' }
            Library    = $lib
            Folder     = Join-Path (Join-Path (Join-Path $lib 'steamapps') 'common') $dir
            StateFlags = $flags
            Installed  = ($flags -eq '4')
            Percent    = $percent
        }
    }
    return $null
}

function Find-CreationKitFolders {
    <#
      Folders that contain CreationKit.exe. Steam installs the Creation Kit
      into its "Fallout 4" folder whether or not the game is there, so this
      looks at Steam libraries directly as well as at known installs.
    #>
    param([string]$SteamRoot, [string[]]$Extra = @())
    $found = New-Object System.Collections.Generic.List[string]
    $candidates = @()
    foreach ($lib in Get-SteamLibraryRoots -SteamRoot $SteamRoot) {
        $candidates += (Join-Path (Join-Path (Join-Path $lib 'steamapps') 'common') 'Fallout 4')
    }
    $candidates += @($Extra | Where-Object { $_ })
    foreach ($c in $candidates) {
        if ((Test-Path -LiteralPath $c) -and (Test-Path -LiteralPath (Join-Path $c 'CreationKit.exe'))) {
            $p = (Resolve-Path -LiteralPath $c).Path.TrimEnd('\', '/')
            if (-not ($found -contains $p)) { $found.Add($p) }
        }
    }
    return $found.ToArray()
}

function Get-RegistryValueSafe {
    param([string]$Path, [string]$Name)
    if (-not $script:OnWindows) { return $null }
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

    if ($script:OnWindows) {
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
        GogProducts        = @(Get-GogProductNames $Root)
        VortexDeployment   = Get-VortexDeployment $data
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

function Get-GogProductNames {
    <# GOG writes goggame-<id>.info into each game folder it installs. Returns the product names in it. #>
    param([string]$Root)
    $names = @()
    foreach ($f in @(Get-ChildItem -LiteralPath $Root -Filter 'goggame-*.info' -File -ErrorAction SilentlyContinue)) {
        $raw = Get-Content -LiteralPath $f.FullName -Raw
        if ($raw -match '"name"\s*:\s*"((?:[^"\\]|\\.)*)"') { $names += $Matches[1] }
    }
    return @($names | Sort-Object -Unique)
}

function Get-VortexDeployment {
    <#
      Vortex leaves vortex.deployment.json in a folder it deploys mods into.
      Returns counts and the staging folder only, never file or mod names.
      Read as text, not parsed as JSON: Windows PowerShell 5.1 refuses JSON
      over about 2 MB, and a large mod list is bigger than that.
    #>
    param([string]$DataFolder)
    $f = Join-Path $DataFolder 'vortex.deployment.json'
    if (-not (Test-Path -LiteralPath $f)) { return $null }
    $raw = Get-Content -LiteralPath $f -Raw
    $staging = $null; $method = $null
    if ($raw -match '"stagingPath"\s*:\s*"((?:[^"\\]|\\.)*)"') { $staging = $Matches[1] -replace '\\\\', '\' }
    if ($raw -match '"deploymentMethod"\s*:\s*"((?:[^"\\]|\\.)*)"') { $method = $Matches[1] }
    $sources = @([regex]::Matches($raw, '"source"\s*:\s*"((?:[^"\\]|\\.)*)"') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
    [pscustomobject]@{
        Files   = [regex]::Matches($raw, '"relPath"\s*:').Count
        Mods    = $sources.Count
        Method  = $method
        Staging = $staging
    }
}

function Get-VortexInfo {
    <# Vortex's own data folder (%APPDATA%\Vortex): which games it manages. Names and counts only. #>
    param([string]$AppDataRoot)
    if (-not $AppDataRoot) { $AppDataRoot = [Environment]::GetFolderPath('ApplicationData') }
    if (-not $AppDataRoot) { return $null }
    $root = Join-Path $AppDataRoot 'Vortex'
    if (-not (Test-Path -LiteralPath $root)) { return $null }
    $games = @()
    foreach ($d in @(Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue)) {
        $mods = Join-Path $d.FullName 'mods'
        $profiles = Join-Path $d.FullName 'profiles'
        if ((Test-Path -LiteralPath $mods) -or (Test-Path -LiteralPath $profiles)) {
            $staged = 0; $profileCount = 0
            if (Test-Path -LiteralPath $mods) { $staged = @(Get-ChildItem -LiteralPath $mods -Directory -ErrorAction SilentlyContinue).Count }
            if (Test-Path -LiteralPath $profiles) { $profileCount = @(Get-ChildItem -LiteralPath $profiles -Directory -ErrorAction SilentlyContinue).Count }
            $games += [pscustomobject]@{ Name = $d.Name; StagedMods = $staged; Profiles = $profileCount }
        }
    }
    [pscustomobject]@{ Root = $root; Games = $games }
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

    # Every Fallout-named settings folder, in case a total conversion keeps its own.
    $myGamesFolders = @()
    $myGamesRoot = Join-Path $DocumentsRoot 'My Games'
    if (Test-Path -LiteralPath $myGamesRoot) {
        foreach ($d in @(Get-ChildItem -LiteralPath $myGamesRoot -Directory -Filter 'Fallout*' -ErrorAction SilentlyContinue)) {
            $s = Join-Path $d.FullName 'Saves'
            $n = 0
            if (Test-Path -LiteralPath $s) { $n = @(Get-ChildItem -LiteralPath $s -Filter '*.fos' -File -ErrorAction SilentlyContinue).Count }
            $myGamesFolders += [pscustomobject]@{
                Name     = $d.Name
                Saves    = $n
                IniFiles = @(Get-ChildItem -LiteralPath $d.FullName -Filter '*.ini' -File -ErrorAction SilentlyContinue | ForEach-Object Name)
            }
        }
    }

    $appDirs = @()
    if ($LocalAppDataRoot -and (Test-Path -LiteralPath $LocalAppDataRoot)) {
        $appDirs = @(Get-ChildItem -LiteralPath $LocalAppDataRoot -Directory -Filter 'Fallout*' -ErrorAction SilentlyContinue | ForEach-Object FullName)
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
                MentionsLondon = [bool](@($lines | Where-Object { $_ -match 'LondonWorldSpace' }).Count)
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
        MyGamesFolders       = $myGamesFolders
        AppDataFolders       = @($appDirs | ForEach-Object { Split-Path -Leaf $_ })
    }
}

function Select-DevInstall {
    <#
      Picks the install to build against: the one given, else the only Steam
      install that has the Creation Kit and is not a Fallout London install.
      Throws with an explanation when the choice is not obvious.
    #>
    param([string]$GameRoot, [string]$SteamRoot, [string]$ModOrganizerRoot)
    if (-not $GameRoot -and $ModOrganizerRoot) {
        $mo = Get-ModOrganizerInfo -Root $ModOrganizerRoot
        if (-not $mo) { throw "No ModOrganizer.ini in $ModOrganizerRoot" }
        if (-not $mo.GamePath) { throw "ModOrganizer.ini in $ModOrganizerRoot has no gamePath" }
        $GameRoot = $mo.GamePath
    }
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

function ConvertFrom-MoValue {
    <# Mod Organizer writes paths as @ByteArray(C:\\Games\\Fallout 4) or with forward slashes. #>
    param([string]$Value)
    if ($null -eq $Value) { return $null }
    $v = $Value.Trim()
    if ($v -match '^@ByteArray\((.*)\)$') { $v = $Matches[1] }
    $v = $v -replace '\\\\', '\'
    return $v.Trim('"')
}

function Resolve-IfExists {
    param([string]$Path)
    if ($Path -and (Test-Path -LiteralPath $Path)) { return (Resolve-Path -LiteralPath $Path).Path.TrimEnd('\', '/') }
    return $Path
}

function Get-ModOrganizerInfo {
    <#
      Describes a Mod Organizer 2 instance (the folder holding ModOrganizer.ini).
      Read-only. Returns $null if the folder is not an instance.
    #>
    param([Parameter(Mandatory)][string]$Root)
    $ini = Join-Path $Root 'ModOrganizer.ini'
    if (-not (Test-Path -LiteralPath $ini)) { return $null }
    $rootPath = (Resolve-Path -LiteralPath $Root).Path

    $base = ConvertFrom-MoValue (Get-IniValue $ini 'Settings' 'base_directory')
    if (-not $base) { $base = $rootPath }
    function Resolve-MoDir([string]$key, [string]$default) {
        $v = ConvertFrom-MoValue (Get-IniValue $ini 'Settings' $key)
        if (-not $v) { return (Join-Path $base $default) }
        return $v.Replace('%BASE_DIR%', $base)
    }
    $mods = Resolve-MoDir 'mod_directory' 'mods'
    $profilesDir = Resolve-MoDir 'profiles_directory' 'profiles'
    $selected = ConvertFrom-MoValue (Get-IniValue $ini 'General' 'selected_profile')

    $profiles = @()
    if (Test-Path -LiteralPath $profilesDir) {
        foreach ($d in Get-ChildItem -LiteralPath $profilesDir -Directory -ErrorAction SilentlyContinue) {
            $modlist = Join-Path $d.FullName 'modlist.txt'
            $plugins = Join-Path $d.FullName 'plugins.txt'
            $settings = Join-Path $d.FullName 'settings.ini'
            $custom = Join-Path $d.FullName 'fallout4custom.ini'
            $modLines = @(); if (Test-Path -LiteralPath $modlist) { $modLines = @(Get-Content -LiteralPath $modlist) }
            $plugLines = @(); if (Test-Path -LiteralPath $plugins) { $plugLines = @(Get-Content -LiteralPath $plugins) }
            $profiles += [pscustomobject]@{
                Name                 = $d.Name
                Selected             = ($d.Name -eq $selected)
                ModsEnabled          = @($modLines | Where-Object { $_.StartsWith('+') }).Count
                PluginsActive        = @($plugLines | Where-Object { $_.StartsWith('*') }).Count
                LocalSettings        = (Get-IniValue $settings 'General' 'LocalSettings')
                LocalSaves           = (Get-IniValue $settings 'General' 'LocalSaves')
                CustomIniExists      = Test-Path -LiteralPath $custom
                InvalidateOlderFiles = Get-IniValue $custom 'Archive' 'bInvalidateOlderFiles'
                PapyrusLogging       = Get-IniValue $custom 'Papyrus' 'bEnableLogging'
                TlmModEnabled        = [bool](@($modLines | Where-Object { $_ -match '^\+TheLastMeridian' }).Count)
                TlmPluginActive      = [bool](@($plugLines | Where-Object { $_ -match '^\*TheLastMeridian\.esp' }).Count)
            }
        }
    }

    # Tools registered in Mod Organizer (they must be started through it to see the mods).
    $tools = @()
    $inExe = $false
    foreach ($line in Get-Content -LiteralPath $ini) {
        $t = $line.Trim()
        if ($t -match '^\[(.+)\]$') { $inExe = ($Matches[1] -ieq 'customExecutables'); continue }
        if ($inExe -and $t -match '^\d+\\binary=(.*)$') {
            $bin = ConvertFrom-MoValue $Matches[1]
            if ($bin -match '(CreationKit|f4se_loader|Fallout4Launcher|Fallout4|FO4Edit|xEdit)[^\\/]*\.exe$') { $tools += (Split-Path -Leaf $bin) }
        }
    }

    $modCount = 0
    if (Test-Path -LiteralPath $mods) { $modCount = @(Get-ChildItem -LiteralPath $mods -Directory -ErrorAction SilentlyContinue).Count }
    $baseSourceMods = @()
    if (Test-Path -LiteralPath $mods) {
        foreach ($d in Get-ChildItem -LiteralPath $mods -Directory -ErrorAction SilentlyContinue) {
            $q = Join-Path (Join-Path (Join-Path (Join-Path $d.FullName 'Scripts') 'Source') 'Base') 'Quest.psc'
            if (Test-Path -LiteralPath $q) { $baseSourceMods += (Split-Path -Parent $q) }
        }
    }

    [pscustomobject]@{
        Root             = $rootPath
        Version          = ConvertFrom-MoValue (Get-IniValue $ini 'General' 'version')
        GameName         = ConvertFrom-MoValue (Get-IniValue $ini 'General' 'gameName')
        GamePath         = Resolve-IfExists (ConvertFrom-MoValue (Get-IniValue $ini 'General' 'gamePath'))
        SelectedProfile  = $selected
        ModsDirectory    = $mods
        ProfilesDirectory = $profilesDir
        ModCount         = $modCount
        Profiles         = $profiles
        Tools            = @($tools | Sort-Object -Unique)
        BaseSourceDirs   = $baseSourceMods
        TlmModFolder     = Join-Path $mods 'TheLastMeridian-Dev'
        TlmModInstalled  = Test-Path -LiteralPath (Join-Path $mods 'TheLastMeridian-Dev')
        ExePresent       = Test-Path -LiteralPath (Join-Path $rootPath 'ModOrganizer.exe')
    }
}

function Find-BaseScriptSource {
    <#
      Where the game's own Papyrus sources are: an explicit folder, the game's
      Data\Scripts\Source\Base, or a Mod Organizer mod that carries them.
      Returns $null if none has any .psc in it.
    #>
    param([string]$Explicit, [string]$GameRoot, [string]$ModOrganizerRoot)
    $candidates = @()
    if ($Explicit) { $candidates += $Explicit }
    if ($GameRoot) { $candidates += (Join-Path (Join-Path (Join-Path (Join-Path $GameRoot 'Data') 'Scripts') 'Source') 'Base') }
    if ($ModOrganizerRoot) {
        $mo = Get-ModOrganizerInfo -Root $ModOrganizerRoot
        if ($mo) { $candidates += $mo.BaseSourceDirs }
    }
    foreach ($c in $candidates) {
        if ($c -and (Test-Path -LiteralPath $c) -and @(Get-ChildItem -LiteralPath $c -Filter '*.psc' -File -ErrorAction SilentlyContinue).Count -gt 0) {
            return (Resolve-Path -LiteralPath $c).Path
        }
    }
    return $null
}

Export-ModuleMember -Function Find-Fallout4Installs, Get-Fallout4InstallInfo, Get-Fallout4UserState,
    Select-DevInstall, Get-SteamLibraryRoots, Get-IniValue, Get-ExeVersion, Get-GameGeneration,
    Get-ModOrganizerInfo, Find-BaseScriptSource, ConvertFrom-MoValue, Invoke-Native, Get-SteamAppState,
    Find-CreationKitFolders, Get-VortexInfo, Get-VortexDeployment, Get-GogProductNames, Hide-UserFolder
