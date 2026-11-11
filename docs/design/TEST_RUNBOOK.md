# Test runbook — getting from the repository to a first in-game result

**Status:** written before any of it has been run on a real install. Steps 1–3 are scripted and the scripts were tested against a stand-in folder tree. Everything from step 4 on is untested.

Run the commands in PowerShell from the repository folder on the PC that has Fallout 4 and the Creation Kit.

## 0. The setup, as reported by the owner on 2026-11-11

Not yet confirmed by the scan in step 1.

| What | Where |
|---|---|
| Game in use | GOG Fallout 4 GOTY: `C:\Program Files (x86)\GOG Galaxy\Games\Fallout 4 GOTY` |
| Mod Organizer 2 instance | `C:\Modlists\TMR` (its `ModOrganizer.ini` points at the GOG install) |
| Fallout London | separate install: `C:\Program Files (x86)\GOG Galaxy\Games\Fallout London\Fallout London` |
| Steam copy | not installed (`F:\SteamLibrary` has no Fallout 4; the Steam registry entry is stale) |

What follows from that:

- **Everything goes through Mod Organizer.** The test build is installed as a mod folder under `C:\Modlists\TMR\mods`, never into the game folder. Tools that must see it (the game, the Creation Kit) are started from Mod Organizer.
- **Test in a copy of the profile.** Copy the current Mod Organizer profile, select the copy, and enable the test mod only there. The existing mod list stays as it is.
- **Fallout London is not used and not touched.** The install script refuses it.
- **The Creation Kit is the open question.** It supplies the Papyrus compiler and the game's script sources, and it is distributed through Steam. Step 1 reports whether `CreationKit.exe` is in the GOG folder. If it is not, nothing can be compiled until it is, and how to get it next to a GOG install has to be worked out on the PC.
- **Game build.** A curated mod list often pins an older game build. The plugin is written with header version 0.95 and FormIDs from 0x800, which every build reads, but the Creation Kit build has to suit the game build. Step 1 records both.
- Use a **disposable save**. Quest and alias changes orphan script data in old saves.

## 1. Record the environment (read-only)

```powershell
pwsh tools/win/Get-BuildEnv.ps1 -ModOrganizerRoot 'C:\Modlists\TMR'
```

Writes `docs/design/BUILD_ENV.md`: game and Creation Kit versions, install paths, compiler and script sources, DLC, Fallout London, loose-file and logging settings. Commit it.

## 2. Build the plugin against the real master

```powershell
dotnet run --project tools/PluginBuilder -- --out build --fallout4-esm "C:\Program Files (x86)\GOG Galaxy\Games\Fallout 4 GOTY\Data\Fallout4.esm"
```

With `Fallout4.esm` supplied, vanilla records (`PlayerRef`, `Caps001`) are resolved by EditorID. **This code path has never run.** Read `build\TheLastMeridian.report.txt`; the "Not wired yet" list should shrink by two.

## 3. Compile the scripts

```powershell
pwsh tools/win/Build-Scripts.ps1 -ModOrganizerRoot 'C:\Modlists\TMR'
```

The script looks for the game's script sources in the game's `Data\Scripts\Source\Base` and in any Mod Organizer mod that carries them. Add `-ExtractBase` if they are still zipped in the game folder, or `-BaseSource <folder>` and `-CompilerPath <exe>` if they are somewhere else.

Output goes to `build\Scripts\TLM\*.pex`, not into the game. The first real compile will probably find errors the documentation-level lint could not. Fix them in `scripts/Source/User/TLM/`, re-run `tools/run_checks.sh` (or `python tools/check_consistency.py`), and compile again.

## 4. Open the plugin in the Creation Kit

Install the build as a Mod Organizer mod (step 5), enable it in the test profile, start the Creation Kit **from Mod Organizer**, load `TheLastMeridian.esp` as the active file, and check:

- it loads with no errors beyond the usual vanilla warnings;
- quests `TLM_Core`, `TLM_MQ01`, `TLM_SQ01` show the stages, objectives and aliases in `tools/PluginBuilder/last-build.report.txt`;
- each quest's Scripts tab shows the script with its properties filled (no red mandatory properties except those listed as not wired).

If the Creation Kit rejects or rewrites anything, that is a finding: record it in `VERIFY_LOG.md` and fix the builder, not the `.esp` by hand.

## 5. Install for testing

```powershell
pwsh tools/win/Install-Dev.ps1 -ModOrganizerRoot 'C:\Modlists\TMR' -WhatIf     # shows what would be copied
pwsh tools/win/Install-Dev.ps1 -ModOrganizerRoot 'C:\Modlists\TMR'
```

This creates `C:\Modlists\TMR\mods\TheLastMeridian-Dev`. Then, in Mod Organizer, refresh, tick the mod in the left pane and `TheLastMeridian.esp` in the right pane, in the test profile only. The script never edits profiles, the mod list or the plugin list. `pwsh tools/win/Uninstall-Dev.ps1` removes exactly what was copied, and the mod folder with it.

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
