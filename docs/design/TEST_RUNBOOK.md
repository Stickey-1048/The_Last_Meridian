# Test runbook — getting from the repository to a first in-game result

**Status:** steps 1 to 5 have run on the owner's PC and pass. On 2026-11-12 the base game was started by command through Mod Organizer, the plugin loaded, its scripts ran, and the self-test reported **60 passed, 0 failed** (details in [VERIFY_LOG.md](VERIFY_LOG.md); an earlier run that day failed 34 checks on a fault in the generated plugin). That is one scripted scenario of stages and globals with every alias empty. The same day 58 scenarios passed with nobody at the keyboard (1,456 checks, 0 failed); 49 of them are the rows of the two test matrices, played with actors and markers the test makes itself and compared with the logic model after every event. Steps 6 and 7 have not been started: nothing has been opened in the Creation Kit, and nothing in a built place or with a player has been tested.

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
- **The base game folder is not a clean install.** Its Data folder holds loose files left by mods that were once installed straight into it (F4SE plugins, MCM settings, several hundred scripts, meshes, sounds, interface files), without their plugins. The game loads them in every Mod Organizer profile that has loose files switched on, and the test profile must have them on for this project's own scripts. Nothing so far points at them, but if a result ever looks like someone else's script at work, look there first. A clean copy of the game for testing, or packing this project's scripts into an archive so that loose files can stay off, are the two ways out.
- **Fallout London is not used and not touched.** The install script refuses it.
- **The test runs through a separate Mod Organizer profile.** Three copies of the game exist (GOG base, Fallout London, Steam) and they share one settings folder and one active-plugin list, which is Fallout London's. A Mod Organizer profile with its own settings, saves and plugin list keeps the test away from all of that, and Mod Organizer is already pointed at the clean GOG base game. **Do not start the Steam copy or the GOG base game directly**, and do not deploy anything from Vortex while testing.
- **Which copy starts has to be checked, not assumed.** Mod Organizer puts this project's files only into the Data folder of the game it manages; a different copy of the game started from the same window does not see them. The Windows registry on this PC names the Fallout London folder as "the" Fallout 4 install, the game's launcher is reported to start whichever copy the registry names, and an entry in Mod Organizer's Run list keeps whatever path it was created with. So step 5 starts `Fallout4.exe` by its full path and reads from the running process which file it is.
- **Two builds are in play.** The game under test is 1.10.163.0 and the compiler comes from Creation Kit 1.11.246.0. The plugin is written with header version 0.95 and FormIDs from 0x800, which every build reads. Whether scripts compiled by the newer compiler run on 1.10.163 is expected but **unverified**; the first in-game check answers it. If the Creation Kit editor is later used on the plugin, match it to the game first.
- Use a **disposable save**, or none: from the main menu the console command `coc qasmoke` should load the game's test cell with a default character (the cell name is on the Creation Kit wiki; the command is unverified here). Quest and alias changes orphan script data in old saves.

## Shortcut: update, build, compile, install and start the test in one command

```powershell
powershell -ExecutionPolicy Bypass -File tools\win\Update-And-Run.ps1 -Install -Play
```

`Update-And-Run.ps1` brings the folder up to date with GitHub and then runs `Run-FirstBuild.ps1` with the same options; if it cannot update, it stops and runs nothing. Use it instead of typing `git pull; powershell ... Run-FirstBuild.ps1 ...`: in that form the second command runs even when the pull was refused, and then it is the older scripts that run. That happened on 2026-11-12 (see [VERIFY_LOG.md](VERIFY_LOG.md)). `Run-FirstBuild.ps1` now also refuses to start in a folder that is behind GitHub. If git reports a file as changed on the PC although its content is the same as git's copy, `Update-And-Run.ps1` tells git to look again and carries on; if a file's content really differs, it lists the file, discards nothing and stops.

If Mod Organizer or the game is open, the script says so and waits for them to be closed. It then checks the tools, reads Steam's install state, runs the scan, builds the plugin against the real `Fallout4.esm`, compiles the scripts and, if both of those passed, installs the build as a Mod Organizer mod and creates or refreshes the test profile (step 4). With `-Play`, and only if the install passed, it starts the game for the in-game test (step 5) and, when the game closes, puts the test results on the clipboard with the build's summary on top. Without `-Play` it stops after the install and copies the build log (`build\first-build-log.txt`, which includes the scan's findings) to the clipboard instead; without `-Install` it stops after the compile and installs nothing. `-NoClipboard` turns the clipboard off.

Outside the repository it changes: the Mod Organizer mod folder and test profile (with `-Install`); which profile Mod Organizer has selected (with `-Play`); the Creation Kit's own `Base.zip`, unpacked beside itself if the script sources are still zipped (`-NoExtractBase` skips that, and the compile with it); and .NET's library cache in the Windows user folder (`.nuget\packages`) the first time it builds. The very first use of .NET on a PC can also create a development HTTPS certificate and send usage telemetry to Microsoft; the script now switches both off, but the first run on the owner's PC predates that (`dotnet dev-certs https --clean` removes the certificate).

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

The real Mod Organizer (2.5.2) opened a profile made this way on 2026-11-12 and showed `TheLastMeridian.esp` active beside the game's own master files. If that ever stops working, the fallback is to make the profile by hand: Profiles, select one, Copy, name it `TLM-Dev`, untick every mod except `TheLastMeridian-Dev`, tick `TheLastMeridian.esp`.

### Other ways to install

`Package-Dev.ps1` writes `build\TheLastMeridian-Dev.zip`, laid out like a Data folder, for installing with any mod manager. `Install-Dev.ps1 -GameRoot <folder>` copies straight into a game's Data folder. Neither isolates the test from the shared settings and plugin list; do not use them on this PC without a reason.

## 5. First in-game test: the self-test

With only the generated records, every alias is empty and flagged Optional, so this tests the **stage logic and globals**, not the world.

```powershell
powershell -ExecutionPolicy Bypass -File tools\win\Start-TestGame.ps1
```

(`Run-FirstBuild.ps1 -Install -Play` runs this at its end.) The script:

1. checks that the test build is installed and switched on in the profile `TLM-Dev`, and waits for Mod Organizer and the game to be closed if either is open;
2. starts Mod Organizer with `ModOrganizer.exe -p "TLM-Dev" run "<managed game folder>\Fallout4.exe"`. That is Mod Organizer's own command for running one program inside its virtual file system in a named profile (read from the 2.5.2 source, `src/commandline.cpp`; not yet run against the real program). Neither the Run list nor the game's launcher is involved;
3. when `Fallout4.exe` appears, reads from the running process which file it was started from and whether Mod Organizer's file-system library (`usvfs`) is loaded in it, and says so. If the wrong copy started, it says that instead of the instructions;
4. prints what to do in the game:
   - at the main menu press the `~` key, type `coc qasmoke`, press Enter;
   - when the room has loaded, close the console. Within about ten seconds a line should appear in the top-left corner: "The Last Meridian test build is loaded." If it never appears, the plugin is not loaded;
   - open the console, type `cqf TLM_Core RunSelfTest`, press Enter, close the console and wait for a message box;
   - quit the game;
5. when the game closes, runs `Get-TestResults.ps1`, which writes `build\test-results.txt` and copies it to the clipboard: a verdict (did the plugin load, did the self-test run, what did it report), the self-test's log, the relevant lines of the game's script log, what the game was given to load, which copy of the game each entry in Mod Organizer's Run list starts, the game folder named in the registry, and whether the game folders hold Fallout London files. Logs written before the session began are marked as old.

If Mod Organizer opens but starts nothing, the script says how to start the game by hand from its window (profile `TLM-Dev`; **Fallout 4**, not **Fallout Launcher**, in the list next to Run) and keeps watching.

`Get-TestResults.ps1` can also be run by itself after any session.

The self-test (`scripts/Source/User/TLM/SelfTest.psc`, attached to `TLM_Core`, development only) starts `TLM_MQ01`, walks it through dispatch, ambush, saved, delivery and hand-off, then walks `TLM_SQ01` through a clue found before the ledger, the ledger, the journal and a public posting. It makes 60 checks of stages, objectives and globals. Every expected number is the logic model's prediction: `tools/logic_model/test_selftest_expectations.py` fails if the two differ. It can run once per game session, because the quests run once.

Seen in the game so far (2026-11-12): `coc qasmoke` typed at the main menu loads the test room; the plugin loads; the scripts bind without errors; scripts compiled with the Creation Kit 1.11 compiler run on game build 1.10.163; `cqf` runs the self-test; setting a stage starts a stopped quest; stage events reach the quest scripts; `SetStage` returns after the stage's handler has finished; the self-test passes 60 of 60.

**Always enter with `coc qasmoke` from the main menu.** Do not use "Continue" or "Load" in the test profile: its saves folder holds saves from earlier test sessions (and from the Fallout London copy that started by mistake on the first attempt), and a loaded save carries old quest state, in which the self-test refuses to run.

Switch Mod Organizer back to your own profile afterwards.

### Running scenarios with nobody at the keyboard

```powershell
powershell -ExecutionPolicy Bypass -File tools\win\Update-And-Run.ps1 -Install -Unattended
```

or, without rebuilding, `powershell -ExecutionPolicy Bypass -File tools\win\Run-Scenarios.ps1` (`-Scenarios 2` runs one of them, `-Scenarios basic` the first eleven).

Each scenario needs a fresh session, because the quests run once. For each scenario `Run-Scenarios.ps1` writes the scenario number into the installed copy of the plugin (the value of the global `TLM_G_DevScenario`: four bytes), starts the game as above, and waits. For the length of the run the test profile's `fallout4custom.ini` carries `sStartingConsoleCommand=coc qasmoke`, so the game enters the test room by itself, and `bAlwaysActive=1`, so it keeps running when its window is not in front. In the game `TLM:Core` sees the scenario number, runs that scenario a few seconds after the room has loaded, and closes the game. The script then reads the logs, moves on to the next scenario, and at the end puts the scenario number back to 0 and the two settings back, and copies a table of results to the clipboard.

| Scenario | What it is |
|---|---|
| 1 | The self-test described above: both quests by stages alone, 60 checks |
| 2 | The fixture probe (`TLM:FixtureProbe`): spawns the game's generic settler three times, forces the actors into the drover, Cutter lead and caravan master aliases, kills them, and checks that the alias scripts hear it (the Cutter lead's death by the player's hand sets stage 31, the caravan master's stage 35); a timer; and, since amendment A25, that an actor nobody is talking to is not "in dialogue with the player". 15 checks (14 in the runs up to 2026-11-12). Its INFO lines also report whether the game takes a kill by the player for a fight: with nobody standing by it does not, and with one of the quest's people standing by it does not either (2026-11-13, twice); an experiment at the end asks the same with four standing by |
| 3 | Distance events (`TLM:FixtureProbe`): one of the game's plain markers is placed at the player and moved away; registering while already apart; then the main quest's own watch, with a marker as the centre of a live ambush moved beyond the evade distance, which sets stage 32. It ends with experiments on a placed item that has no model; the first never comes back, so the watchdog ends the scenario there, 8 checks passed |
| 4 | The main quest played through with a caravan made at run time (`TLM:WorldCases`): the player meets the ambush and does nothing. The drover should die, the cargo go, the caravan master reach the town alias and be unkillable there, the debrief be the "evaded" one, and admitting it count for truth and accountability |
| 5 | The same, saved: the Cutter lead starts a fight and dies by the player's hand. Both hands should reach town, the cargo stay, the debrief be the "saved" one with its extra reputation and trust |
| 6 | The same, missed: the player goes to town without meeting the ambush. The town stage should resolve it (stage 34), kill the drover and keep him out of the town alias in the same breath |
| 7 | The same, betrayal on the road: the caravan master dies by the player's hand at the ambush. The Cutters should finish the drover, nobody reach town, and the debrief be the one with no witness |
| 8 | The same, murder after saving: the Cutter lead dies, then the caravan master, both by the player's hand. "Exploited" should replace "saved", the drover reach town as the witness, and confessing count for truth and accountability |
| 9 | The same, the deal: stage 33 is set as the talk with the Cutter lead would set it. The drover should die, the cargo go, the caravan master be the witness, and blaming the Cutters cost truth |
| 10 | The placed-content trial (`TLM:PlacedTrial`, on a quest of its own, `TLM_Trial`): a settler, a trigger and an object that the plugin itself places in the test room, with quest aliases pointing at them. The person should start disabled and be there once enabled; picking the object up and entering the trigger should each set a stage through the game's own script on the alias. 17 checks; its INFO lines say where everything is and what two comparison triggers did. **Ran in the game on 2026-11-13, twice: 17 of 17.** The second time the comparison triggers named no collision layer, as the game's own do, and both set their stages. The settler, once enabled, is not where it was placed: its sandbox package puts it on a seat of the room (scenario 11) |
| 11 | The same trial, part two (`TLM:PlacedPeople`, on the same quest): people the plugin places. A person on a base of the plugin's own, which is the game's settler with no packages and no script, should start disabled, be there once enabled and still be within 64 units of its spot six seconds later, height included; activating it should show a line and set a stage through the project's own script on its alias. 8 checks, all written before the rest. Its INFO lines then say, for that person, a second like it, and two copies of the game's settler, each enabled alone: where it is at once, after two seconds and after six, and what it is doing; what holds a person that did not stay; where the navigation mesh is under each spot; and whether the settler goes to a place in the room or to the player. **Ran in the game on 2026-11-13: 8 of 8**, in 163 seconds, and every experiment came back. The person of the plugin's own stood exactly where it was placed. It cannot follow scenario 10 in one session: both use the trial's quest |

| 101 to 128 | The rows of the main quest's test matrix, as cases generated from the logic model (`TLM:MatrixCases`, with `TLM:CaseDriver` doing the work). After every event the driver compares everything it can see of both quests with the model. `tools/matrix_cases.json` says which rows each case stands for |
| 129 to 132 | Not rows of the matrix: the main quest when the game does two things with no time between them (amendment A24). The Cutter lead killed and the timer, leaving, or the town stage before his death is announced; and the town stage set while "evaded" is still being handled. Case 132 says in an INFO line whether that overlap really happened. The report has a part headed "Timing" that lists, per scenario, that INFO line and each line the main quest wrote to the script log when a rule about timing decided something: `TLM_MQ01: A2 ...` (the evade timer held back by a fight), `TLM_MQ01: A24 ...` (a guard against a late death or an overlap) and `TLM_MQ01: A25 ...` (the timer held back by the conversation with the Cutter lead). A case here that passes with no `A24` line has passed because the game's timing never put the guard to the test. That was so for case 129 twice: on 2026-11-12 the game took the kill for a fight, and on 2026-11-13 the death was announced before the timer's function was reached. In case 129 the lead now dies with nobody named as his killer, and the timer's function is called in the next breath |
| 201 to 221 | The same for the side quest's matrix |

`-Scenarios` takes numbers, ranges and names, separated by commas: `all` (the default: 1 to 11 and every case from 101 up; a session took 36 seconds on 2026-11-12, 66 on the morning of 2026-11-13 and 30 to 37 that afternoon, so between 35 and 70 minutes), `basic` (1 to 11), `matrix`, `main`, `side`, or for example `4,104-110,side`. With that many scenarios the report shows one line each, and details only for the ones that did not pass.

Lines beginning INFO report what the game did without scoring it. Lines beginning STEP name what the scenario was about to do, so a run that stops shows where.

Scenarios 4 to 9 and the matrix cases make the player invulnerable while they run (the stand-ins are settlers with guns and their own minds) and take that back at the end. The expected numbers in scenarios 4 to 9 are the logic model's: `tools/logic_model/test_worldcases_expectations.py` fails if the script and the model disagree. The matrix cases are written by `tools/gen_matrix_cases.py` from the model; never edit `MatrixCases.psc` by hand.

Before any of this goes to the PC it can be rehearsed without the game: `python3 tools/papyrus_sim all` runs the real scripts against a stand-in for the game (see `tools/README.md`). That is a rehearsal, not a result.

**A scenario that stops is ended twice over.** The self-test gives every step a number of seconds; when a step does not come back in time, the self-test itself writes where it stopped and closes the game. Behind that, **the script closes the game it started** if a scenario has not finished after fifteen minutes (four at first; seven once a scenario that moves the player about had taken a minute and a half; fifteen since scenario 11, which has some twenty steps that may each wait two and a half minutes for the game): first by asking the window to close, then by ending the process. It only runs if no game and no Mod Organizer was open when it began. Nothing is saved by hand in these sessions.

**Steam has to be running, and the runner sees to it.** Mod Organizer asks about Steam before it starts a game whose folder holds `steam_api64.dll`, and waits for the answer: a window titled "Launch Steam". After a restart of the PC, Steam is usually not running. So before anything is started the runner looks; if Steam is needed and not running it starts Steam in the background and says so in the report's "Steam" line. `-NoSteamStart` makes it ask you to start Steam and wait instead. Steam is left running afterwards.

**If Mod Organizer stops on any other question**, the runner names the window on the screen after twenty seconds ("Mod Organizer has not started the game yet and is showing a window titled ..."). If you are there, answer it and the run carries on. If nobody is, the first scenario is given five minutes; then the report says which window it was and what was running, and the runner closes that Mod Organizer so that it cannot start the game later, when the run's settings have been taken away again.

**A run that is cut off is repaired by the next one.** If the PC shuts down or the window is closed in mid-run, the run cannot put back what it changed in the test profile: the start-up console command, the keep-running-without-focus setting and the scenario number in the installed plugin stay as the run set them. Nothing outside the test profile is touched, but until the next run do not start the game in that profile: it would walk into the test room by itself and might run a scenario and close. Before a run changes anything it writes down how things were (`build\scenario-run.unfinished.json`) and removes that note when it has put them back. The next run finds the note, says so in its report, and puts back what was there before the run that was cut off. A run cut off before these notes existed (before 2026-11-13) left none; its mark is the start-up command still being in the test profile, and the next run then puts back the game's own defaults.

Seen on the PC on 2026-11-12: the start-up console command enters the room, the scenario starts by itself, `Debug.QuitGame()` closes the game, a settler can be spawned in the test room, the watchdog ends a scenario that has stopped, and all 58 scenarios pass, in 35 minutes together. Scenario 3 always ends through the watchdog: its last part is an experiment known not to come back (moving a placed item that has no model), kept as a record of that fact. If the first scenario never starts by itself the script stops and says so, and the scenarios can still be run by hand: `Start-TestGame.ps1`, then in the game `coc qasmoke` and `cqf TLM_Core RunSelfTest 2`.

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

Build the temporary test cell (wreck, road, ambush, gate), place the actors and markers, fill the aliases, remove the Optional flags, and run T01–T29 and S01–S24 for real.

When this was written, that was to be the `mq01-logic-proof` milestone. By the owner's decision of 2026-11-13 the tag of that name marks the scripted proof of 2026-11-12 instead (commit `c1e6d48`, 62 scenarios with actors and markers made at run time); the built cell is still the next step.

## Tagging a milestone

Done for `mq01-logic-proof` on 2026-11-13. For the next milestone: a tag has to be pushed from the owner's PC, because the cloud session that does the day-to-day work may push the branch but not tags. One command, the usual one with `-Tag` in place of the other options:

```
cd C:\Dev\The_Last_Meridian
powershell -ExecutionPolicy Bypass -File tools\win\Update-And-Run.ps1 -Tag
```

It brings the folder up to date as always and then, instead of building anything, runs `tools\win\Push-MilestoneTag.ps1`. That script creates the tag `mq01-logic-proof` on commit `c1e6d48` with the text in `docs\design\tags\mq01-logic-proof.txt`, pushes that one tag and nothing else, and says what GitHub then shows. It stops without pushing if the tag already exists anywhere pointing at another commit, if the text is missing, or if git does not know who is tagging (the name and e-mail git is configured with are published with a tag). The first push from the PC may open a GitHub sign-in window. Whatever happens, its whole message is copied to the clipboard and written to `build\milestone-tag.txt`: paste it into the chat. The game and Mod Organizer do not have to be closed for this.

## What to report back

For each step: passed, failed (with the exact message), or not attempted and why. Do not mark a case passed from the model's result; the model already passes all of them.
