# Test runbook — getting from the repository to a first in-game result

**Status:** steps 1 to 3 ran on the owner's PC on 2026-11-11 and passed: the scan, the plugin build against the real `Fallout4.esm`, and the compile of all seven scripts (details in [VERIFY_LOG.md](VERIFY_LOG.md)). Everything from step 4 on is untested.

Run the commands in PowerShell from the repository folder on the PC that has Fallout 4 and the Creation Kit.

Needed on the PC besides the game: **git**, the **.NET 8 SDK** (for the plugin builder), and the **Creation Kit**. All three are installed on the owner's PC. The commands use Windows PowerShell with `-ExecutionPolicy Bypass` so the scripts are allowed to run for that one call.

## 0. The setup on the owner's PC

From the scan and build run of 2026-11-11, unless marked as the owner's report.

| What | Where |
|---|---|
| Game under test | GOG Fallout 4 GOTY, build 1.10.163.0: `C:\Program Files (x86)\GOG Galaxy\Games\Fallout 4 GOTY` |
| Creation Kit | 1.11.246.0, with the Papyrus compiler and script sources: `F:\SteamLibrary\steamapps\common\Fallout 4` |
| Steam copy of the game | downloading into the same Steam folder at the time of the run |
| Fallout London | separate install: `C:\Program Files (x86)\GOG Galaxy\Games\Fallout London\Fallout London` |
| Mod Organizer 2 | instance at `C:\Modlists\TMR`, pointing at the GOG game; selected profile "The Midnight Ride Extended" |
| Vortex | the owner reports using it; what it manages is not yet known |
| How the owner starts the game | through GOG Galaxy; the owner believes that starts Fallout London (owner's report) |
| PowerShell | Windows PowerShell 5.1 |

What follows from that:

- **Building needs no game launch.** The plugin is built from the GOG game's `Fallout4.esm`, and the scripts are compiled with the Creation Kit's compiler. Both already work.
- **Fallout London is not used and not touched.** The install script refuses it.
- **How to start base Fallout 4 with the test mod is undecided.** Three copies of the game will exist (GOG base, Fallout London, Steam), and they may share settings, saves and the active plugin list. The next scan reports which mod manager deploys into which folder and which settings folders exist; the choice (a clean Mod Organizer profile, a Vortex install of the packaged zip, or a direct copy) follows from that. Until then, **do not start the Steam copy** and do not install the test build anywhere.
- **Two builds are in play.** The game under test is 1.10.163.0 and the compiler comes from Creation Kit 1.11.246.0. The plugin is written with header version 0.95 and FormIDs from 0x800, which every build reads. Whether scripts compiled by the newer compiler run on 1.10.163 is expected but **unverified**; the first in-game check answers it. If the Creation Kit editor is later used on the plugin, match it to the game first.
- Use a **disposable save**, or none: from the main menu the console command `coc qasmoke` should load the game's test cell with a default character (the cell name is on the Creation Kit wiki; the command is unverified here). Quest and alias changes orphan script data in old saves.

## Shortcut: steps 1 to 3 in one command

```powershell
powershell -ExecutionPolicy Bypass -File tools\win\Run-FirstBuild.ps1
```

It checks the tools, reads Steam's install state for Fallout 4 and the Creation Kit, runs the scan, builds the plugin against the real `Fallout4.esm`, compiles the scripts, and writes everything, including the scan's findings, to `build\first-build-log.txt`. It also copies that log to the clipboard, so it can be pasted straight into a chat (`-NoClipboard` turns that off). The Windows user folder name is replaced with `%USERPROFILE%` in the log and in `BUILD_ENV.md`. It keeps going where it can, so it is safe to run while Steam is still downloading.

It installs nothing into the game or a mod manager. Outside the repository it changes two things: it unpacks the Creation Kit's own `Base.zip` beside itself if the script sources are still zipped (`-NoExtractBase` skips that, and the compile with it), and .NET downloads the plugin builder's libraries into its cache in the Windows user folder (`.nuget\packages`) the first time it builds. The very first use of .NET on a PC can also create a development HTTPS certificate and send usage telemetry to Microsoft; the script now switches both off, but the first run on the owner's PC predates that (`dotnet dev-certs https --clean` removes the certificate). Defaults assume Mod Organizer at `C:\Modlists\TMR` and a Steam library at `F:\SteamLibrary`; `-ModOrganizerRoot`, `-SteamLibrary` and `-CreationKitRoot` override them.

Steps 1 to 3 below are what it runs, for doing them one at a time.

## 1. Record the environment (read-only)

```powershell
powershell -ExecutionPolicy Bypass -File tools\win\Get-BuildEnv.ps1 -ModOrganizerRoot 'C:\Modlists\TMR'
```

Writes `docs/design/BUILD_ENV.md`: game and Creation Kit versions, install paths, compiler and script sources, DLC, Fallout London, loose-file and logging settings. Commit it.

## 2. Build the plugin against the real master

```powershell
dotnet run --project tools/PluginBuilder -- --out build --fallout4-esm "C:\Program Files (x86)\GOG Galaxy\Games\Fallout 4 GOTY\Data\Fallout4.esm"
```

With `Fallout4.esm` supplied, vanilla records (`PlayerRef`, `Caps001`) are resolved by EditorID. On the first real run `Caps001` resolved and `PlayerRef` did not; the lookup has since been made independent of letter case and is awaiting a re-run. Read `build\TheLastMeridian.report.txt`; the "Not wired yet" list should shrink by two.

## 3. Compile the scripts

```powershell
powershell -ExecutionPolicy Bypass -File tools\win\Build-Scripts.ps1 -CreationKitRoot '<Steam library>\steamapps\common\Fallout 4' -ExtractBase
```

`-CreationKitRoot` is the folder the Creation Kit was installed into; the compiler and the game's script sources are taken from there. `-ExtractBase` unpacks `Data\Scripts\Source\Base\Base.zip` in that folder if the sources are still zipped. `-BaseSource <folder>` and `-CompilerPath <exe>` override either location.

Output goes to `build\Scripts\TLM\*.pex`, not into the game. The first real compile will probably find errors the documentation-level lint could not. Fix them in `scripts/Source/User/TLM/`, re-run `tools/run_checks.sh` (or `python tools/check_consistency.py`), and compile again.

## 4. Open the plugin in the Creation Kit

Install the build as a Mod Organizer mod (step 5), enable it in the test profile, start the Creation Kit **from Mod Organizer**, load `TheLastMeridian.esp` as the active file, and check:

- it loads with no errors beyond the usual vanilla warnings;
- quests `TLM_Core`, `TLM_MQ01`, `TLM_SQ01` show the stages, objectives and aliases in `tools/PluginBuilder/last-build.report.txt`;
- each quest's Scripts tab shows the script with its properties filled (no red mandatory properties except those listed as not wired).

If the Creation Kit rejects or rewrites anything, that is a finding: record it in `VERIFY_LOG.md` and fix the builder, not the `.esp` by hand.

## 5. Install for testing

```powershell
powershell -ExecutionPolicy Bypass -File tools\win\Install-Dev.ps1 -ModOrganizerRoot 'C:\Modlists\TMR' -WhatIf     # shows what would be copied
powershell -ExecutionPolicy Bypass -File tools\win\Install-Dev.ps1 -ModOrganizerRoot 'C:\Modlists\TMR'
```

This creates `C:\Modlists\TMR\mods\TheLastMeridian-Dev`. Then, in Mod Organizer, refresh, tick the mod in the left pane and `TheLastMeridian.esp` in the right pane, in the test profile only. The script never edits profiles, the mod list or the plugin list. `powershell -ExecutionPolicy Bypass -File tools\win\Uninstall-Dev.ps1` removes exactly what was copied, and the mod folder with it.

### If the game is started through Vortex, or you would rather install it yourself

```powershell
powershell -ExecutionPolicy Bypass -File tools\win\Package-Dev.ps1
```

This writes `build\TheLastMeridian-Dev.zip`, laid out like a Data folder. Install the zip with the mod manager that actually starts the game (Vortex: Install From File; Mod Organizer: install from archive), in a test profile, and enable `TheLastMeridian.esp`. Which manager starts the game under test is an open question on this PC: the scan found a Mod Organizer instance at `C:\Modlists\TMR`, and the owner reports using Vortex.

## 6. First in-game checks (before any test cell exists)

With only the generated records, every alias is empty and flagged Optional, so this stage tests the **stage logic and globals**, not the world. In the console:

| Check | Console | Expect |
|---|---|---|
| Plugin and core quest loaded | `sqv TLM_Core` | quest running; `TLM_G_DataVersion` is 1 |
| Start | `cqf TLM_Core DevStart` then `sqv TLM_MQ01` | stage 10 done; objective 10 shown; `TLM_SQ01` stage 5 done |
| Dispatch | `setstage TLM_MQ01 20` | objective 10 complete, 20 shown |
| Saved | `setstage TLM_MQ01 30` then `setstage TLM_MQ01 31` | `TLM_G_CaravanOutcome` = 1 |
| Deliver | `setstage TLM_MQ01 50` | stage 40 also set; `TLM_G_Rep_MercyCrossing` = 2; `TLM_G_MQ01_DebriefVariant` = 6 here (no Nell exists yet, so "lost") |
| Finish | `setstage TLM_MQ01 60` | stage 100; quest completed; `TLM_G_MQ01_Done` = 1 |
| SQ01 evidence | `setstage TLM_SQ01 10`, `11`, `13` | stage 20 then 25 set by the script; `TLM_G_SQ01_EvidenceLevel` = 2 |

Repeat from a fresh save for Evaded (`30`, `32`), Deal (`30`, `33`) and Missed (`40` straight after `20`), comparing each global with the values in `tools/logic_model/test_mq01_matrix.py`. The setstage commands themselves are unverified; check them first.

Papyrus errors appear in `Documents\My Games\Fallout4\Logs\Script\Papyrus.0.log` once logging is on.

## 7. Then, and only then

Build the temporary test cell (wreck, road, ambush, gate), place the actors and markers, fill the aliases, remove the Optional flags, and run T01–T28 and S01–S24 for real. That is the `mq01-logic-proof` milestone.

## What to report back

For each step: passed, failed (with the exact message), or not attempted and why. Do not mark a case passed from the model's result; the model already passes all of them.
