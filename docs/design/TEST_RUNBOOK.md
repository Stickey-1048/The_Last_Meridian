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
| Steam copy of the game | build 1.11.240.0, in the same Steam folder as the Creation Kit |
| Fallout London | separate install: `C:\Program Files (x86)\GOG Galaxy\Games\Fallout London\Fallout London` |
| Mod Organizer 2 | instance at `C:\Modlists\TMR`, pointing at the GOG game; selected profile "The Midnight Ride Extended" |
| Vortex | installed, with a staged mod library that is not deployed into any of the three game folders; not used by this project |
| How the owner starts the game | through GOG Galaxy; the owner believes that starts Fallout London (owner's report) |
| Settings, saves, active plugins | one shared Fallout 4 settings folder and one active-plugin list, currently holding Fallout London's plugins |
| PowerShell | Windows PowerShell 5.1 |

What follows from that:

- **Building needs no game launch.** The plugin is built from the GOG game's `Fallout4.esm`, and the scripts are compiled with the Creation Kit's compiler. Both already work.
- **Fallout London is not used and not touched.** The install script refuses it.
- **The test runs through a separate Mod Organizer profile.** Three copies of the game exist (GOG base, Fallout London, Steam) and they share one settings folder and one active-plugin list, which is Fallout London's. A Mod Organizer profile with its own settings, saves and plugin list keeps the test away from all of that, and Mod Organizer is already pointed at the clean GOG base game. **Do not start the Steam copy or the GOG base game directly**, and do not deploy anything from Vortex while testing.
- **Two builds are in play.** The game under test is 1.10.163.0 and the compiler comes from Creation Kit 1.11.246.0. The plugin is written with header version 0.95 and FormIDs from 0x800, which every build reads. Whether scripts compiled by the newer compiler run on 1.10.163 is expected but **unverified**; the first in-game check answers it. If the Creation Kit editor is later used on the plugin, match it to the game first.
- Use a **disposable save**, or none: from the main menu the console command `coc qasmoke` should load the game's test cell with a default character (the cell name is on the Creation Kit wiki; the command is unverified here). Quest and alias changes orphan script data in old saves.

## Shortcut: build, compile and install in one command

```powershell
git pull; powershell -ExecutionPolicy Bypass -File tools\win\Run-FirstBuild.ps1 -Install
```

Close Mod Organizer first. The script checks the tools, reads Steam's install state, runs the scan, builds the plugin against the real `Fallout4.esm`, compiles the scripts and, if both of those passed, installs the build as a Mod Organizer mod and creates the test profile (step 5). It writes everything, including the scan's findings, to `build\first-build-log.txt` and copies that log to the clipboard so it can be pasted into a chat (`-NoClipboard` turns that off). Without `-Install` it stops after the compile and installs nothing.

Outside the repository it changes: the Mod Organizer mod folder and test profile (with `-Install`); the Creation Kit's own `Base.zip`, unpacked beside itself if the script sources are still zipped (`-NoExtractBase` skips that, and the compile with it); and .NET's library cache in the Windows user folder (`.nuget\packages`) the first time it builds. The very first use of .NET on a PC can also create a development HTTPS certificate and send usage telemetry to Microsoft; the script now switches both off, but the first run on the owner's PC predates that (`dotnet dev-certs https --clean` removes the certificate).

Defaults assume Mod Organizer at `C:\Modlists\TMR` and a Steam library at `F:\SteamLibrary`; `-ModOrganizerRoot`, `-SteamLibrary` and `-CreationKitRoot` override them. The Windows user folder name is replaced with `%USERPROFILE%` in everything it writes.

The numbered steps below are what it runs, for doing them one at a time.

## 1. Record the environment (read-only)

```powershell
powershell -ExecutionPolicy Bypass -File tools\win\Get-BuildEnv.ps1 -ModOrganizerRoot 'C:\Modlists\TMR'
```

Writes `docs/design/BUILD_ENV.md`: game and Creation Kit versions, install paths, compiler and script sources, DLC, Fallout London, mod managers, and the settings folders. The file is an inventory of one person's PC, so it is git-ignored and stays there; the facts the build depends on are summarised in [VERIFY_LOG.md](VERIFY_LOG.md).

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

## 4. Install for testing

```powershell
powershell -ExecutionPolicy Bypass -File tools\win\Install-Dev.ps1 -ModOrganizerRoot 'C:\Modlists\TMR' -CreateProfile
```

Mod Organizer must be closed. This does two things, and touches no game folder:

- copies the plugin, the compiled scripts and their sources into `C:\Modlists\TMR\mods\TheLastMeridian-Dev`;
- creates the Mod Organizer profile `TLM-Dev` as a copy of the selected profile's files, with every other mod and plugin switched off, its own settings and saves, Papyrus logging on and loose files on. Existing profiles are only read. If `TLM-Dev` already exists, only this project's lines in it are refreshed.

Why Mod Organizer: on the owner's PC, Fallout London shares the one Fallout 4 settings folder and the one active-plugin list with any copy of the game started directly. A Mod Organizer profile with its own settings, saves and plugin list is what keeps a test from touching them.

`Uninstall-Dev.ps1` removes exactly the files that were copied, and the mod folder with them; add `-RemoveProfile` to delete the test profile too (with any saves made in it).

A profile made this way has not yet been opened by a real Mod Organizer. If `TLM-Dev` does not appear in its profile list, or the mod is not ticked in it, that is a finding to report, and the fallback is to make the profile by hand: Profiles, select one, Copy, name it `TLM-Dev`, untick every mod except `TheLastMeridian-Dev`, tick `TheLastMeridian.esp`.

### Other ways to install

`Package-Dev.ps1` writes `build\TheLastMeridian-Dev.zip`, laid out like a Data folder, for installing with any mod manager. `Install-Dev.ps1 -GameRoot <folder>` copies straight into a game's Data folder. Neither isolates the test from the shared settings and plugin list; do not use them on this PC without a reason.

## 5. First in-game test: the self-test

With only the generated records, every alias is empty and flagged Optional, so this tests the **stage logic and globals**, not the world.

1. Start Mod Organizer (`C:\Modlists\TMR\ModOrganizer.exe`).
2. In the Profile list at the top, choose `TLM-Dev`.
3. In the list next to the Run button, choose the entry that starts `Fallout4.exe` (the install script prints its title).
4. Run. At the game's main menu, press the `~` key and type `coc qasmoke`. When the room has loaded, open the console again and type `cqf TLM_Core RunSelfTest`. Close the console and wait for a message box.
5. Quit the game and run:

```powershell
powershell -ExecutionPolicy Bypass -File tools\win\Get-TestResults.ps1
```

It gathers the self-test's log and the relevant lines of the game's script log into `build\test-results.txt` and the clipboard.

The self-test (`scripts/Source/User/TLM/SelfTest.psc`, attached to `TLM_Core`, development only) starts `TLM_MQ01`, walks it through dispatch, ambush, saved, delivery and hand-off, then walks `TLM_SQ01` through a clue found before the ledger, the ledger, the journal and a public posting. It makes 60 checks of stages, objectives and globals. Every expected number is the logic model's prediction: `tools/logic_model/test_selftest_expectations.py` fails if the two differ. It can run once per game session, because the quests run once.

Everything in this step is unverified: that the plugin loads, that `coc qasmoke` works from the main menu, that the scripts bind, and that scripts compiled with the Creation Kit 1.11 compiler run on game build 1.10.163. Whatever fails first is the finding.

Switch Mod Organizer back to your own profile afterwards.

### Checking by hand

The same things can be checked one at a time in the console. The `setstage` and `sqv` commands themselves are unverified.

| Check | Console | Expect |
|---|---|---|
| Plugin and core quest loaded | `sqv TLM_Core` | quest running; `TLM_G_DataVersion` is 1 |
| Start | `cqf TLM_Core DevStart` then `sqv TLM_MQ01` | stage 10 done; objective 10 shown; `TLM_SQ01` stage 5 done |
| Dispatch | `setstage TLM_MQ01 20` | objective 10 complete, 20 shown |
| Saved | `setstage TLM_MQ01 30` then `setstage TLM_MQ01 31` | `TLM_G_CaravanOutcome` = 1 |
| Deliver | `setstage TLM_MQ01 50` | stage 40 also set; `TLM_G_Rep_MercyCrossing` = 2; `TLM_G_MQ01_DebriefVariant` = 6 here (no Nell exists yet, so "lost") |
| Finish | `setstage TLM_MQ01 60` | stage 100; quest completed; `TLM_G_MQ01_Done` = 1 |
| SQ01 evidence | `setstage TLM_SQ01 10`, `11`, `13` | stage 20 then 25 set by the script; `TLM_G_SQ01_EvidenceLevel` = 2 |

Other outcomes (Evaded `30`, `32`; Deal `30`, `33`; Missed `40` straight after `20`) each need a fresh session; compare the globals with `tools/logic_model/test_mq01_matrix.py`.

## 6. Open the plugin in the Creation Kit

Not attempted yet, and not needed for step 5. The Creation Kit on this PC (1.11.246.0) sits beside the Steam copy of the game (1.11.240.0), while the game under test is the GOG copy (1.10.163.0); how to open the plugin in the editor without mixing those up has to be worked out first. When it is, check that the plugin loads with no errors beyond the usual vanilla warnings, that the three quests show the stages, objectives and aliases in `tools/PluginBuilder/last-build.report.txt`, and that each quest's Scripts tab shows its scripts with their properties filled. If the Creation Kit rejects or rewrites anything, record it in `VERIFY_LOG.md` and fix the builder, not the `.esp` by hand.

## 7. Then, and only then

Build the temporary test cell (wreck, road, ambush, gate), place the actors and markers, fill the aliases, remove the Optional flags, and run T01–T28 and S01–S24 for real. That is the `mq01-logic-proof` milestone.

## What to report back

For each step: passed, failed (with the exact message), or not attempted and why. Do not mark a case passed from the model's result; the model already passes all of them.
