# Verification log

**Dates:** 2026-11-11 and 2026-11-12. **Sources:** the Fallout 4 Creation Kit wiki (falloutck.uesp.net), read through its API; the build runs on the owner's PC; the owner's report of the first attempt in the game; and Mod Organizer's source on GitHub.
**Not checked:** anything inside the Creation Kit editor. In the running game (all on 2026-11-12): the plugin loads, its scripts run, and nine scripted scenarios pass all 220 of their checks with nobody at the keyboard. Six of them play the main quest from start to hand-off with actors and markers made at run time, one for each way the caravan encounter can end. Nothing is placed in the world, so nothing that needs a built place, dialogue or a player has been tested; triggers, pickups and conversations are stood in for by stage numbers; and the side quest has been through one path only.

## Results from the game PC

First run of `tools/win/Run-FirstBuild.ps1` on the owner's PC, 2026-11-11, commit `f9ec406`, Windows PowerShell 5.1. Reported by screenshot of its output.

| What | Result |
|---|---|
| Game under test | GOG Fallout 4 GOTY, `Fallout4.exe` 1.10.163.0 |
| Creation Kit | 1.11.246.0, in the Steam library's `Fallout 4` folder (installed without the Steam copy of the game, which was still downloading) |
| Fallout London | found as a separate install; the scripts refuse to copy into it |
| Mod Organizer | an instance at `C:\Modlists\TMR` manages the GOG game; selected profile "The Midnight Ride Extended" with its own settings |
| **Scripts compile** | **Yes: 7 succeeded, 0 failed**, Papyrus Compiler 2.8.0.4, against the Creation Kit's own script sources in `Data\Scripts\Source\Base`. This is a compile only; nothing has run in the game |
| Plugin build against the real `Fallout4.esm` | Passed: 10,053 bytes, header version 0.95, lowest FormID 0x800, file read back matches the spec |
| `Caps001` looked up by EditorID | Resolved to `00000F:Fallout4.esm` |
| `PlayerRef` looked up by EditorID | **Not found.** Cause reproduced off the PC: the untyped lookup is case-sensitive, and the master evidently spells it differently. Fixed (typed, case-insensitive lookup, with a fallback to id 0x14 that is only accepted if it places the actor `Player`). The fix is tested on stand-in masters and awaits a re-run on the PC |
| Scan bug | It reported that no Creation Kit was found, because it only counted folders containing `Fallout4.exe`. Fixed |

Second run, same day, commit `59b917c`, after the Steam copy of the game finished installing. Reported as the pasted log.

| What | Result |
|---|---|
| Steam copy of the game | `Fallout4.exe` 1.11.240.0, beside Creation Kit 1.11.246.0; base game only, no story DLC |
| GOG base game folder | clean: no mods in `Data`, no F4SE, all six DLC masters |
| Scripts compile | Again 7 of 7 |
| `PlayerRef` | **Still not found.** The typed, case-insensitive lookup finds no placed actor with that EditorID in the 1.10.163 master, and record `000014` is not visible to the library as a placed actor placing `Player`. The builder now also accepts `000014` when at least ten vanilla quest aliases named like "Player" force that reference; tested on stand-in masters, awaiting a third run |
| Settings and load order | One Fallout 4 settings folder and one active-plugin list on the PC, and that list holds Fallout London's plugins. Any copy of the game started directly shares them |
| Mod Organizer | 2.5.2 at `C:\Modlists\TMR`, two profiles, each with its own settings and saves |
| Vortex | installed, with a staged mod library that is not deployed into any of the three game folders. Not used by this project |

What follows: the first in-game test goes through a separate Mod Organizer profile, so that nothing shared with Fallout London is read or written (TEST_RUNBOOK.md, steps 4 and 5).

Third run, same day, commit `859f468`, with `-Install`. Reported as the pasted log.

| What | Result |
|---|---|
| `PlayerRef` | **Resolved.** Record `000014` is still not visible to the library as a placed actor, but 13 vanilla quest aliases force that reference and all 13 are named like "Player" (for example quest `RESceneKMK02`, alias `Player`), which meets the builder's threshold of ten. The player alias is now filled with `000014:Fallout4.esm` |
| Scripts compile | 8 of 8, including the new self-test script, on its first compile |
| Plugin | 10,692 bytes; 31 items still not wired (all of them placed references and the location, which need the test cell) |
| Install as a Mod Organizer mod | Passed: 17 files in `C:\Modlists\TMR\mods\TheLastMeridian-Dev` |
| Test profile | Created as `TLM-Dev` from the selected profile, with that profile's 109 enabled mods switched off in the copy. Not yet opened by Mod Organizer |

Checklist item 5 below is now done for `Caps001` and `PlayerRef`.

### First attempt in the game, 2026-11-12

Build of the third run, started by the owner from Mod Organizer's window. Reported by screenshots and in the owner's words. Which entry of the Run list was used is not known; "Fallout Launcher" was the one selected in the screenshots taken just before.

| What | Result |
|---|---|
| Mod Organizer and the script-made profile | **Works.** Mod Organizer 2.5.2 listed the profile `TLM-Dev` and showed `TheLastMeridian.esp` active beside the base game's seven master files (8 active) |
| What the game showed | The **Fallout London** main menu, in a small window. Then a loading screen in a layout that is not the base game's, carrying base-game text, and the base game's test room after `coc qasmoke` |
| `cqf TLM_Core RunSelfTest` | The console answered "Compiled script not saved!"; in the owner's words it said the quest was not found. The quest was therefore not among the data the running game had loaded |
| Reading | The game that ran was using Fallout London's files, so it was not the base game with Mod Organizer's files in view. **Not established:** which copy of the game ran and why, and whether the plugin loads when the right copy runs |
| `coc qasmoke` from the main menu | Works (in whichever copy that was) |

Read afterwards in Mod Organizer's own source, release 2.5.2 unless marked (this is reading, not a test):

| Fact | Where |
|---|---|
| The enabled mods are mapped onto the Data folder of the managed game only. Another copy of the game started from Mod Organizer does not see them | `src/organizercore.cpp`, `fileMapping` |
| The profile's `plugins.txt` is mapped onto the shared `%LOCALAPPDATA%\Fallout4\plugins.txt`, and the game's own master files are left out of it | game plugin `gamefallout4.cpp`, `mappings`; `creationgameplugins.cpp`, `writePluginList` (both read from the current development branch, not the 2.5.2 tag) |
| When an instance is created, the game folder is taken from the registry value `Bethesda Softworks\Fallout4\Installed Path`. On this PC that value names the Fallout London folder | `gamegamebryo.cpp`, `identifyGamePath` (development branch); the scan of 2026-11-11 |
| Entries of the Run list are kept as stored and only missing ones are added, so an entry can point at a different folder from the managed one | `src/executableslist.cpp`, `load` |
| `ModOrganizer.exe -p <profile> run <program>` runs one program inside the virtual file system, in that profile, waits for it and exits. If Mod Organizer is already open with a different profile it refuses | `src/commandline.cpp`, `RunCommand`; `src/main.cpp`; `src/moapplication.cpp` |
| Which file was started is written to Mod Organizer's log only at log level Debug | `src/spawn.cpp`, `logSpawning` |

Not verified at all: forum reports that the game's launcher starts the copy named in the registry rather than the one in its own folder. That would explain both the owner's impression that the GOG game "just runs London" and this attempt, if the launcher entry was the one used.

What was changed in response (tested against stand-ins only; not yet run on the PC):

- `tools/win/Start-TestGame.ps1` starts `Fallout4.exe` in the managed folder by its full path through Mod Organizer's `run` command, then reads from the running process which file it is and whether Mod Organizer's file-system library is loaded in it.
- `tools/win/Get-TestResults.ps1` now also reports which file each Run-list entry starts, the registry's game folder, whether either game folder holds Fallout London files, the settings the test profile hands the game, and marks logs older than the session.
- `TLM:Core` writes `TLM_Core: started` to the game's script log when its quest starts, and shows "The Last Meridian test build is loaded." on screen a few seconds later (development only).

Fourth run, 2026-11-11 21:41 by the PC's clock, commit `c2bfd36`, with `-Install -Play`. Reported as the pasted log.

| What | Result |
|---|---|
| Scripts compile | 8 of 8, including the changed `TLM:Core` (timer and on-screen line) |
| Plugin | Unchanged: 10,692 bytes, player alias forced to `000014:Fallout4.esm` |
| Install | **Failed, through a fault in this project's script:** "The source profile and the new profile are the same." The test profile was by then the one selected in Mod Organizer, and the script took the selected profile as the one to copy from even though the test profile already existed and only needed refreshing. The stand-in tests had never put the stand-in Mod Organizer in that state. The build had already been copied into the mod folder when the step stopped, although the summary said nothing was installed; no profile and no game folder was changed |
| In-game test | Not started, because the install did not pass |
| Scan | The test profile shows 1 mod and 1 plugin switched on, with its own settings and saves and script logging on. A game script log now exists in the shared settings folder, where there was none before the first attempt in the game |

Reading of that last line: script logging is off in the shared settings and on in the test profile only, so the session that showed the Fallout London menu ran with the test profile's settings in effect. That fits a Fallout London copy of the game started inside Mod Organizer's file system. It is an inference; the log itself has not been read yet.

Fixed after the fourth run (tested against stand-ins only): an existing test profile is refreshed without any source profile; a new one is copied from the selected profile or, if that cannot serve, the first other profile; the record of copied files is written before the profile step; the summary no longer claims nothing was installed when the install stopped part-way; the stand-in Mod Organizer now remembers the profile it was started with, as the real one does; and every part of the results report is collected on its own, so a failure in one part cannot keep the rest from the clipboard.

### First run in the right game, 2026-11-12

Fifth run, 06:57 to 08:17 by the PC's clock, commit `87d04d5`, with `-Install -Play`. Reported as the pasted results and a screenshot of the self-test's message box.

| What | Result |
|---|---|
| Install | Passed: the existing test profile was refreshed |
| Starting the game by command | **Works.** `ModOrganizer.exe -p "TLM-Dev" run "<game folder>\Fallout4.exe"` started the base game. Read from the running process: started from `...\Fallout 4 GOTY\Fallout4.exe`, by Mod Organizer, with `usvfs_x64.dll` loaded and no F4SE |
| The plugin loads (game 1.10.163, GOG) | **Yes.** `TLM_Core` started and its script wrote `TLM_Core: started, data version 1` to the game's script log |
| The scripts bind and run | **Yes.** No error or warning in the game's log names this project's scripts. Scripts compiled by the 1.11 Creation Kit's compiler run on game 1.10.163 |
| `cqf TLM_Core RunSelfTest` | Works, including finding the function on the second of two scripts attached to the quest |
| `coc qasmoke` from the main menu | Works in the base game |
| `SetStage`, `GetStageDone`, `IsRunning`, `IsObjectiveDisplayed`, `GetItemCount`, `GetValueInt` | Behave as the wiki says. `SetStage` on a quest that is not running starts it |
| Self-test | **26 passed, 34 failed.** Exactly the checks that depend on a stage handler failed; every other check passed |
| Cause | No `OnStageSet` event reached the quest scripts. The stages were set, silently. In the plugin as built, no stage had an item (a "log entry") as the game reads the file: the subrecord that starts an item (QSDT) was only written when its flags were not zero, which was true of one stage per quest |
| Why the checks did not catch it | The library that writes the plugin also reads it back, and it reads a stage's text without that subrecord as an item. The read-back self-check therefore passed. Nothing in the repository looked at the bytes |

What supports that reading, besides the result itself (none of it is a test; the next run is):

- xEdit's record definitions for Fallout 4 (`wbDefinitionsFO4.pas`, record QUST): a log entry is a group that begins with QSDT; the NEXT marker between the quest's two condition lists is marked required.
- UESP's description of the same record in Skyrim: "Each QSDT field marks the start of a log entry."
- The wiki's own signature, `OnStageSet(int auiStageID, int auiItemID)`: the event names an item.
- A modders' forum report found by search: OnStageSet does not fire for a stage that has no log entry.

Also settled by this run: why the first attempt showed Fallout London.

| Fact | Source |
|---|---|
| In this Mod Organizer the entry "Fallout 4" is hidden from the Run list. Of the entries shown, only "F4SE" and "Fallout Launcher" start a game, and the F4SE loader does not exist in the managed folder | `ModOrganizer.ini`, read by the results script |
| The Windows registry names the Fallout London folder as the Fallout 4 install | the results script |
| A preloader that exists only in the Fallout London folder wrote its log at 20:42 on 2026-11-11, during that attempt, and the game's script logs of that evening exist although script logging is on in the test profile only | file times in the shared settings folder |

So the launcher, the only usable entry, was started inside Mod Organizer with the test profile's settings, and the game that came up was the Fallout London copy. That the launcher picks its game from the registry is still an inference from these facts, not something read in its code.

**Correction to the second run's table:** the base game folder is not clean. The scans counted plugin files only. Its Data folder holds loose files in more than 24 folders: F4SE plugins, MCM settings, 362 files under Scripts, meshes, materials, sounds, interface files. They are left from mods installed straight into the game, without their plugins. The game loads loose files in every Mod Organizer profile that has loose files switched on, the test profile included, because Mod Organizer can add files to Data but cannot hide files that are really there. Nothing in this run points at them, but a test in that folder is not a test of the plain game. The scan now reports them.

Fixed after the fifth run (checks pass; not yet re-tested in the game):

- The builder writes exactly one item, with its flags subrecord, for every stage; the NEXT marker for every quest; flags for every objective; and the display time for messages that are not boxes. The plugin is 10,989 bytes in skeleton mode (10,692 with the real master before the change).
- The builder's self-check now fails if a stage has no item or an item lacks its flags.
- `tools/check_plugin_layout.py` reads the plugin's raw records without the library and checks the same things. Run on the plugin as it was tested in the game it reports 77 problems. `tools/run_checks.sh` runs it, with four kinds of deliberate damage that must each be caught.
- With the real master supplied, the builder prints how the game's own quests are laid out (how many stages have no item, how many items lack flags) beside this plugin's, so the claim "the Creation Kit always writes this" is checked against the game's data on the PC.
- `TLM:MQ01Quest` and `TLM:SQ01Quest` write one line to the script log for every stage event they receive, and the results script counts them.
- The results script reports a finished self-test even when a second attempt in the same session was refused.
- The self-test also reports, without scoring it, how often a stage's handler had already finished when `SetStage` returned. The wiki says `SetStage` waits for the stage's fragment "and event if any"; the quest scripts depend on that wherever a handler sets another stage and then reads what it changed (for example the delivery forcing the town stage), so the next run measures it.

### The self-test passes, 2026-11-12

Sixth run, 08:58 to 09:16 by the PC's clock, commit `63b31d1`, with `-Install -Play`. Reported as the pasted results.

| What | Result |
|---|---|
| Scripts compile | 8 of 8, with the changes |
| How the game's own quests are laid out (`Fallout4.esm`, build 1.10.163) | 1,336 quests, every one with the condition marker. 8,680 stages, 63 of them (0.73%) with no item. 9,058 stage items, every one with its flags subrecord. 1,198 objectives, every one with flags. So the Creation Kit always writes the three things this plugin had left out, and the comparison now reads "present in all" for this plugin on each line |
| Stage events | **Arrive.** During the self-test 10 reached the main quest's script and 10 the side quest's, each logged as "item 0" |
| `SetStage` and the handler | **In 13 of 13 cases the stage's handler had finished when `SetStage` returned.** That includes stages set from inside a handler: the log shows stage 50's event, then stage 40's, before the checks that follow the delivery; likewise 60 then 100, and in the side quest 10 then 20, 13 then 25, 43 then 50 then 100 |
| Self-test | **60 passed, 0 failed**, in a fresh session entered with `coc qasmoke` |

What the 60 checks cover: one scenario. In the main quest the start, the dispatch, the ambush going live, "saved", a second outcome being ignored, the delivery forcing the town stage, a debrief answer the variant does not offer being ignored, the hand-off and completion. In the side quest a clue examined before the ledger, the ledger, the journal, the posting that names the Yard Office, and a second decision being ignored. They read stages, objectives, globals and one item given to the player. Every alias was empty.

What they do not cover: anything with an actor or an object in the world, the evade timer and distance watch, dialogue, the message boxes, the four other caravan outcomes, the five other side-quest outcomes, and saving and loading.

Seen by accident in the same session, before the self-test: the owner first loaded a save made during the fifth run, in which the faulty plugin had left the quests with stages set and nothing applied.

| What | Result |
|---|---|
| The alias on the player | The script on the main quest's player alias received `OnPlayerLoadGame`. So the alias forced to record `000014` is filled with the player, and an alias receives its reference's events (checklist item 6, the last part) |
| Recovery on load | The side quest's `OnGameLoaded` ran: it logged "ledger was missing; replaced", gave the ledger, recomputed the evidence and set stages 20 and 25, whose events arrived. That is the designed recovery path running on a state only the old fault could produce. Whether what it did was right for a player has not been judged |
| The self-test in that session | Refused to run, as designed, because the quests had already been started |

Also read from the fifth run's log after the fact: that session too began by loading a save, not with `coc`. Three seconds before `TLM_Core` started, the game warned about a Fallout London variable "loaded from save". The test profile's own saves folder holds saves the Fallout London copy made during the first attempt, and "Continue" loads the newest. It does not change the cause of that run's 34 failures. **For testing, always enter with `coc qasmoke` from the main menu; never "Continue" or "Load" in the test profile.**

The managed game's Data folder has one loose compiled script directly under `Scripts`, and it is not one of the game's own base scripts; the several hundred other files under `Scripts` are in subfolders. So the leftovers there do not replace the game's base scripts.

Prepared for the next run, and unverified until it has happened (it has: see "The first unattended run" below):

- `tools/win/Run-Scenarios.ps1` runs scenarios one game session each, unattended. It depends on three things not yet seen in the game: `sStartingConsoleCommand=coc qasmoke` in the profile's settings entering the test room at start-up (forum reports say the setting works, some that it is ignored under a mod manager); `TLM:Core` then starting the scenario by itself from its timer; and `Debug.QuitGame()` closing the game. The last is listed on the wiki as a debug-only function; the other debug-only functions the scripts use (`Trace`, `TraceUser`, `OpenUserLog`) do work in this game when the scripts are compiled as they are now.
- Self-test scenario 2, `TLM:FixtureProbe`, spawns the game's generic settler (`WorkshopNPC`, looked up when the plugin is built; if the name is not in `Fallout4.esm` the probe says so and stops), forces the actors into three of the quest's aliases and kills them. It answers checklist items 6 and 7 as far as they can be answered without a placed world, and decides whether the test matrix can be run with actors made at run time (owner decision D8).

### A refused pull, 2026-11-12

The seventh run did not happen. Reported by screenshot: `git pull` stopped with "Your local changes to the following files would be overwritten by merge: tools/PluginBuilder/formkeys.txt", and the command that followed it on the same line then ran the older `Run-FirstBuild.ps1`, which stopped at an option it did not know. Nothing was built or run.

Cause, reproduced in a scratch clone: the PC's copy of the repository was cloned before `.gitattributes` pinned `formkeys.txt` to LF line endings, so its working copy had Windows line endings. Since commit `1eeca6b` the plugin builder rewrote that file with LF "whenever it differed", and a difference in line endings counted. The rewrite changed the file's size and nothing else. Git compares sizes before contents, so it reported the file as modified although `git diff` showed no difference, and it refused the first pull that had to update the file. The change that was meant to keep builds from marking the file as changed is what marked it. It never showed on Linux, where the file has LF to begin with.

Fixed (reproduced and tested in scratch clones; not yet run on the PC):

- The builder compares the file without regard to line endings and leaves it alone unless its content really differs.
- `tools/win/Update-And-Run.ps1` updates the folder and then runs the build, and stops if it cannot update. A file git reports as changed whose content is identical is refreshed in git's index (nothing is staged, nothing discarded); a file whose content really differs is listed and left alone.
- `Run-FirstBuild.ps1` stops at once if the folder is behind GitHub, instead of running older scripts.

The one-time remedy on the PC is `git add tools/PluginBuilder/formkeys.txt`, which makes git look at the content again, followed by `git pull`. It worked: the next run was at the current commit.

### The first unattended run, 2026-11-12

Eighth run, 10:18 to 10:22 by the PC's clock, commit `1b832da`. The command given was the one-time remedy above followed by `tools\win\Update-And-Run.ps1 -Install -Unattended`; only the results of the scenario run were sent back, as pasted text. Nobody touched the game.

| What | Result |
|---|---|
| Scripts compile | 9 of 9, the new `TLM:FixtureProbe` on its first compile |
| Entering the test room by itself | **Works.** With `sStartingConsoleCommand=coc qasmoke` in the test profile's `fallout4custom.ini`, the game started through Mod Organizer went into the room without a key being pressed |
| Starting the scenario by itself | **Works.** `TLM:Core` read the scenario number from the plugin and started the scenario from its timer |
| The game closing itself | **Works.** `Debug.QuitGame()` ended the game; the results were complete on disk |
| Scenario 1 (both quests by stages alone) | **60 passed, 0 failed, 32 seconds** from starting Mod Organizer to the game being gone. The same result as the run by hand |
| Scenario 2 (actors made at run time) | **Did not finish: 15 passed, 0 failed, no result line.** The script stopped in its last part. The runner closed the game after its limit of 240 seconds by asking the window to close, which the game obeyed |
| Afterwards | The scenario number, the start-up command and the keep-running setting were put back; the installed plugin was again identical to the build |
| The game's script log | No error or warning naming this project in either session |

What scenario 2 showed before it stopped. The settler is the game's `WorkshopNPC`, found in `Fallout4.esm` when the plugin was built, and spawned next to the player with `PlaceAtMe`.

| What | Result |
|---|---|
| An actor made at run time, put into an alias with `ForceRefTo` | The alias holds it, and the quest script's own test for "alive" sees it |
| An actor in an alias flagged Protected | `IsEssential()` is false. `Kill()` with no killer **does not kill it**. `Kill(player)` kills it. `SetProtected(false)` and then `Kill()` kills it |
| The Cutter alias script | Heard the death of the actor forced into the lead's alias (`OnDeath`), and the quest set stage 31 and the outcome "saved" |
| The caravan hand alias script | Heard the death of the actor forced into the caravan master's alias with the player as killer; the quest set stage 35, and "exploited" replaced "saved" (amendment A3) |
| A hand's death with no player as killer | Not treated as a betrayal: stage 35 stayed unset |
| A timer on a quest script | Fired |
| `PlaceAtMe` of this plugin's item, which has no model | Returned a reference |

So the quest's rules that hang on an alias and a death can be tested with actors made at run time. The quest's `KillByCutters` clears the protection before it kills; the second row shows that it has to whenever the Cutter lead is not there to be named as the killer.

Where it stopped. After the fifteenth check the script registered for a distance event between the player and the placed item, called `MoveTo` on the item to put it 3000 units away, and waited three seconds; the line that follows the wait was never written. Which of those calls did not come back is not established. `MoveTo` is the likeliest: the wiki lists it among the functions that suspend the script until the game has done the work, and the item has no model, so nothing of it is ever loaded.

What was changed because of it (not yet compiled, not yet run):

- The self-test has a watchdog. Every step of a scenario is named and given a number of seconds; if the step does not come back in time, the self-test writes where it stopped, writes the result and closes the game. The runner's own limit stays as the second line of defence, and its report now shows the last step named in the log.
- Scenario 2 keeps the 14 checks about actors and loses the distance part.
- Scenario 3 is new: distance events between the player and one of the game's plain markers (`XMarker`, looked up when the plugin is built), registering while already apart, and the main quest's own "the player has left" watch with the marker as the centre of the ambush. It ends with two experiments that repeat what stopped scenario 2, apart and in order; if one does not come back, the watchdog reports that as a fact and the scenario still counts.
- Scenarios 4 to 9 are new (`TLM:WorldCases`): the main quest played from start to hand-off with a caravan made at run time, one case for each way the encounter can end. Every expected number comes from the logic model; `tools/logic_model/test_worldcases_expectations.py` replays the six sequences and fails if a number, a yes/no check or a stage in the script differs.

| Scenario | Case | Events in the logic model | Matrix rows it stands for |
|---|---|---|---|
| 4 | evaded | start, take_dispatch, goto_ambush, evade_timer, goto_town, pritchard_handover, debrief_admit, pritchard_handoff | T09, and the "evaded" debrief with "admit" |
| 5 | saved after a fight | start, take_dispatch, goto_ambush, attack_cutter, player_kills_lead, goto_town, pritchard_handover, pritchard_handoff | T06, and the "saved" debrief |
| 6 | missed | start, take_dispatch, goto_town, pritchard_handover, pritchard_handoff | T10b |
| 7 | betrayal on the road | start, take_dispatch, goto_ambush, player_kills_nell, goto_town, pritchard_handover, pritchard_handoff | T12 |
| 8 | murder after saving | start, take_dispatch, goto_ambush, player_kills_lead, player_kills_nell, goto_town, pritchard_handover, debrief_confess, pritchard_handoff | T12c, and the "witness" debrief with "confess" |
| 9 | the deal | start, take_dispatch, goto_ambush, dunmore_deal, goto_town, pritchard_handover, debrief_blame, pritchard_handoff | T11, and the "witness" debrief with "blame" |

With scenario 1 (the debrief for a caravan master lost to something other than the player) these reach all four caravan outcomes and all six debrief variants. They are six paths through the rules, not the matrix: T01 to T28 has other rows, and the side quest's S01 to S24 are untouched.

What scenarios 4 to 9 stand in for, and what they leave out: the dispatch, the triggers and the conversation with the sheriff are stage numbers set by the test; the function the evade timer calls when it runs out is called directly, the 90 seconds are not waited for; the deal is its stage number, set as the conversation would set it; the wagon's cargo is three items in a fourth settler's pockets. The stand-ins are settlers with their own AI and guns, so the player is made invulnerable for the length of the case.

### All nine scenarios pass, 2026-11-12

Ninth run, 11:51 to 11:56 by the PC's clock, commit `3b73468`, started with `tools\win\Update-And-Run.ps1 -Install -Unattended`. Reported as the pasted results. Nobody touched the game. Nine game sessions took 335 seconds.

| What | Result |
|---|---|
| Scripts compile | Passed, the new `TLM:WorldCases` and the changed `TLM:SelfTest`, `TLM:FixtureProbe` and `TLM:MQ01Quest` on their first compile |
| Looked up in `Fallout4.esm` | `WorkshopNPC` is `020593` (the settler the stand-ins are made from); `XMarker` is `00003B` |
| **The nine scenarios** | **All passed: 220 checks, 0 failed** |
| The game's script log | No error or warning naming this project in any of the nine sessions |
| `SetStage` and the handler | The handler had finished when `SetStage` returned in 61 of 61 cases across the nine sessions |
| Afterwards | Everything put back; the installed plugin identical to the build |

| # | Scenario | Passed | Seconds |
|---|---|---|---|
| 1 | both quests by stages alone | 60 | 32 |
| 2 | actors made at run time, in the aliases, killed | 14 | 61 |
| 3 | distance events and the quest's "the player has left" watch | 8 | 46 |
| 4 | evaded | 27 | 33 |
| 5 | saved after a fight | 24 | 35 |
| 6 | missed | 22 | 31 |
| 7 | betrayal on the road | 22 | 31 |
| 8 | murder after saving | 22 | 36 |
| 9 | the deal | 21 | 31 |

The seconds run from starting Mod Organizer to Mod Organizer being gone again. Scenario 2 took about half a minute longer than the others after its result was written; why is not known.

What the game showed, beyond the numbers the logic model predicted:

| What | Result |
|---|---|
| **The cause of the eighth run's stop** | **`MoveTo` on a placed reference that has no model does not come back.** Scenario 3 placed a copy of this plugin's item (`Is3DLoaded` = false), called `MoveTo` to put it 300 units away, and the call had not returned when the watchdog ended the scenario. No distance event and no long distance were involved this time, so it was the `MoveTo`. The two experiments that were to follow could not run |
| The watchdog | Worked. It fired 17 seconds after the step began (its limit was 20, counted by the game's timer), wrote where the scenario was, wrote the result and closed the game. So a timer event on a script does get in while another call into that script is suspended |
| `MoveTo` on the game's plain marker | Returns. The marker was 2000 units away afterwards, and 5000 in the second test |
| Distance events | None while the two references were together; one event after the marker was moved away, reporting 2000 units; and one at once when registering while already apart |
| The main quest's "the player has left" watch | With a marker as the centre of a live ambush moved 5000 units away (the evade distance is 4000), the quest set stage 32 and the outcome "evaded" |
| An alias flagged Essential | The actor forced into it reports `IsEssential()` = true, and `Kill(player)` did not kill it (scenario 4, the caravan master in the town alias). Amendment A10 holds for a kill by script; a player's weapon has not been tried |
| A Cutter who turns on the player | `StartCombat(player)` on the actor in the Cutter lead's alias: the alias script received `OnCombatStateChanged` with the player as target and the quest set stage 30 by itself. The lead and the player were both in combat. After the lead's death and stage 31 the player was out of combat |
| `IsDead()` straight after `Kill` | True. In the town stage the quest kills the drover and in the same breath decides who goes to the caravan yard; the drover was dead by then and stayed out of the town alias (scenario 6) |
| `TryToDisable` on an aliased actor | The actor is disabled afterwards, alive (scenarios 4, 6, 7) or dead (scenario 5) |
| `RemoveAllItems` through the wagon alias | Emptied the stand-in's pockets |
| The evade timer running out with no fight | With the player not in combat, `EvadeTimerElapsed` set stage 32; the drover, killed by script with the Cutter lead named as killer, was dead and his death was not counted as a betrayal |

Which rows of the main quest's matrix this stands for, with stage numbers in place of triggers, pickups and talk: T06 (saved by killing the lead), T09 (evaded when the timer runs out), T09b (evaded by leaving, without a caravan), T10b (missed), T11 (the deal), T12 (betrayal with no witness), T12c (murder after saving), T12d (no killing in town, by script), T21 (the caravan master lost to something else, in scenario 1), T26 (completion), five of the six reputation cases of T23, and three of the seven metric cases of T24 (saved; evaded and admitted; the deal and blaming the Cutters), with "confess" seen on a different route to the same debrief.

Not run in the game: T05 and T05b (the three unnamed Cutters), T07 and T08 (the speech check), T10a, T12b, T14 to T14c (no early "evaded" during a fight), T17 to T19c (the dispatch taken late, lost, repaired), T25, T26b and T26c; the rows the model cannot express (T13, T15, T16, T20, T22, T27, T28); and every row of the side quest's matrix except the one path of scenario 1.

Still not done anywhere: opening the plugin in the Creation Kit, anything in a built place, any test of the quest as a player would meet it.

Each `[VERIFY]` tag in the v0.1 designs ends up in one of three states:

- **Documented** — the wiki states it. Good enough to write code against; behaviour still has to be seen in the game.
- **Corrected** — the wiki contradicts or improves on the v0.1 assumption. The amendment is in [DESIGN_AMENDMENTS_v0.2.md](DESIGN_AMENDMENTS_v0.2.md).
- **Needs the game** — the wiki is silent, or the item is a fact about the installed build. Listed again at the end as the checklist for the game PC.

Native signatures used by the scripts are recorded in [`tools/papyrus_natives.json`](../../tools/papyrus_natives.json) with the page each came from, and are enforced by `tools/check_consistency.py`.

## Papyrus

| Item | State | What the wiki says |
|---|---|---|
| `StartTimer` / `OnTimer` on a quest script | Seen in the game | `Function StartTimer(float afInterval, int aiTimerID = 0)`, `Event OnTimer(int aiTimerID)`, members of ScriptObject. Starting a timer whose ID is already running resets it. Time only counts outside menus and follows the global time modifier (VATS, Jet). Quests and aliases cancel their timers when the quest stops. On 2026-11-12 a one-second timer fired, and a timer event was handled while another call into the same script was suspended. |
| Do timers survive a save and load? | Needs the game | Not stated. The scripts do not rely on it: the evade timer and distance watch are re-armed on every load. |
| `GlobalVariable.SetValue` | Documented | `SetValue(float)`, plus `SetValueInt(int)`, `GetValueInt()`, and `Mod(float)` which is thread-safe. The scripts use `Mod` for all increments. |
| Quest stage fragments are unavoidable | Corrected | `Event OnStageSet(int auiStageID, int auiItemID)` exists on Quest and runs alongside any fragment. The scripts use it for everything, so there are no fragments (A12). |
| `OnStageSet` for a stage with no item | Seen in the game | The wiki does not say. In the game on 2026-11-12, stages without an item were set and no event arrived (A22). With one item on every stage the event arrives, as item 0. |
| `SetStage` waits for the stage's handler | Seen in the game | The wiki says it waits for the fragment "and event if any". In the game the handler had finished in 13 of 13 cases when `SetStage` returned, including stages set from inside a handler. |
| An alias on the player receives `OnPlayerLoadGame` | Seen in the game | Once, on 2026-11-12, when a save was loaded. |
| Setting a stage twice | Corrected | "SetStage has no effect after it is called the first time for any stage on a running quest" unless Allow Repeated Stages is on. v0.1's repeatable stage 15 (SQ01) and stage 900 could not work as written (A12, A15). |
| Alias scripts before the quest starts | Corrected | Aliases receive their reference's events as part of a running quest. SQ01 must already be running for clue scripts to fire (A8). |
| `OnContainerChanged` | Documented | `Event OnContainerChanged(ObjectReference akNewContainer, ObjectReference akOldContainer)`. Once an object is in a container it "ceases to exist in most cases". |
| `OnTriggerEnter` | Documented | `Event OnTriggerEnter(ObjectReference akActionRef)`. Can arrive out of order with `OnTriggerLeave`; the trigger's collision layer decides what fires it. |
| `OnDeath` | Seen in the game | `Event OnDeath(Actor akKiller)`, "when the actor finishes dying". `OnDying` fires at the start. On 2026-11-12 the scripts on two aliases received it for actors forced into them, with the killer passed to `Kill`. |
| `OnPlayerLoadGame` | Documented | Sent only to the player actor; fires "for the first time on the next load". An alias pointing at the player should receive it, since aliases get their reference's events. *That last step needs the game.* |
| `OnCombatStateChanged` | Seen in the game | `Event OnCombatStateChanged(Actor akTarget, int aeCombatState)`. On 2026-11-12 an alias script received it, with the player as target, when `StartCombat(player)` was called on its actor. |
| `OnHit` | Documented | Needs `RegisterForHitEvent` first and fires once per registration. The scripts use `OnCombatStateChanged` instead. |
| Distance polling | Corrected | `RegisterForDistanceGreaterThanEvent(ScriptObject, ScriptObject, float)` and `Event OnDistanceGreaterThan(...)` exist and the wiki recommends them over polling `GetDistance`. One event per registration; "if the objects are already that far apart, the event will be sent immediately". **Seen in the game** on 2026-11-12, all three statements. |
| Calling an event like a function | Documented, not used | "Calling events is identical to calling a function." Nothing in the project relies on it: the evade timer's handler is a function of its own (`EvadeTimerElapsed`), which the timer event and the self-test both call. |
| `Message.Show` return value | Documented | "If the message displays a message box to the user, it returns the button the user hit. If it doesn't, it will return -1 immediately." |
| Does a hidden button shift the returned index? | Needs the game | Not stated. |
| `RemoveItem` | Documented | `RemoveItem(Form akItemToRemove, int aiCount = 1, bool abSilent = false, ObjectReference akOtherContainer = None)`. |
| `Kill`, protection | Documented | `Kill(Actor akKiller = None)`; `SetProtected(bool abProtected = true)`; `SetEssential` then overrides alias flags. Protected: "The Player is the only one allowed to kill a Protected Actor." |
| Does `Kill` work on a Protected actor? | Seen in the game | Not stated on the wiki. In the game on 2026-11-12, for an actor in an alias flagged Protected: `Kill()` with no killer did nothing; `Kill(player)` killed; `SetProtected(false)` then `Kill()` killed. The scripts clear the flag first. |
| `ForceRefTo` with an actor made by `PlaceAtMe` | Seen in the game | The alias holds the actor and its script receives the actor's events (2026-11-12). |
| `MoveTo` | Seen in the game | Listed among the latent functions: the script is suspended until the game has moved the reference. On 2026-11-12, twice, a script that called it on a placed item with no model never continued; the second time nothing else was involved. On the game's plain marker it returns at once. **Nothing without a model may be moved by script** (A23). |
| An alias flagged Essential | Seen in the game | The wiki's alias page is empty. In the game on 2026-11-12 the actor forced into such an alias reported `IsEssential()` = true and `Kill(player)` did not kill it. |
| `IsDead()` straight after `Kill` | Seen in the game | True at once (2026-11-12), not only when the actor has finished dying. `OnDeath` still arrives later. |
| `Debug` functions in the game | Seen in the game | The wiki calls them debug-only. `Trace`, `TraceUser`, `OpenUserLog` and `QuitGame` have visibly worked in game build 1.10.163 with the scripts compiled as they are. `SetGodMode` compiles and is called without an error; its effect has not been looked at. |
| Removing an NPC without a dangling alias | Partly seen | `Disable()` is documented; the alias stays filled. In the game on 2026-11-12 `TryToDisable` left the aliased actor disabled, alive or dead. Whether anything is left dangling has not been looked at. |
| Property flags | Documented | `Auto Const`, `Mandatory`, `AutoReadOnly`, and `Const` variables are all valid Fallout 4 Papyrus. |
| Default scripts | Documented (new) | The base game ships `DefaultAliasOnContainerChangedTo`, `DefaultAliasOnTriggerEnter`, `DefaultAliasOnDeath`, `DefaultTopicInfoSetStage`, `DefaultShowMessageOnActivateAlias` and others, each taking a `StageToSet`. Pickups, triggers and dialogue can set stages with no project code. |

## Creation Kit

| Item | State | What the wiki says |
|---|---|---|
| Quest Data labels | Documented | Priority, Event, Start Game Enabled, Run Once, Warn on alias fill failure, Allow repeated stages, Type. "If aliases fail to fill, the entire quest will fail." |
| Quest type for SQ01 | Corrected | "Miscellaneous quests ... do not display objective descriptions and summaries" (A18). |
| Stage and objective fields | Documented | Stage index 0–65535, log entries with Complete Quest / Fail Quest; objectives have an index, display text and alias targets. |
| Alias flag labels and fill types | Needs the game | The wiki's alias page is empty. The flag names in the plugin come from the file format (Quest Object, Essential, Protected, Allow Dead, Allow Disabled, Optional). |
| Message form | Documented | Message Box checkbox; Menu Buttons, each with its own conditions. No button limit is stated. |
| Dialogue: four options, speech checks, unvoiced lines | Needs the game | The wiki has no usable dialogue pages. |
| Papyrus compiler | Documented | `<game>\Papyrus Compiler\PapyrusCompiler.exe`; flags file `Institute_Papyrus_Flags.flg`; project files (`.ppj`) with import folders `Data\Scripts\Source\User` and `...\Base`. |
| Unpacking the base script sources | Needs the game | Not described on the pages read. |
| Loose files | Documented | Compiled scripts are ignored unless `Fallout4Custom.ini` has `[Archive] bInvalidateOlderFiles=1` and `sResourceDataDirsFinal=` (empty). |
| Papyrus logging | Documented | `[Papyrus] bEnableLogging=1`, `bEnableTrace=1`, `bLoadDebugInformation=1`; log at `Documents\My Games\Fallout4\Logs\Script\Papyrus.0.log`. |
| Where to get the Creation Kit | Needs the game | The wiki still describes the retired Bethesda.net Launcher. |

## Console

| Item | State | What the wiki says |
|---|---|---|
| `cqf` (CallQuestFunction) | Seen in the game | `CQF <quest> <function> [params]`. Missing parameters are filled with zero or None, not with the script's defaults. Worked on 2026-11-12 for a function on the second of two scripts on the quest. |
| `sqv` (ShowQuestVars) | Documented | `SQV <QuestID> [filter]` shows variables, aliases and quest state. |
| `coc` | Seen in the game | `coc qasmoke` typed at the main menu loaded the test room (2026-11-12). The same command given as `[General] sStartingConsoleCommand` in the profile's settings entered the room at start-up, with no key pressed. |
| `startquest`, `setstage`, `getstage`, `sqs`, `sqt`, `prid`, `kill`, `tgm`, `player.additem` | Needs the game | No page on the wiki. |

## Checklist for the game PC

1. Game build, Creation Kit build, install paths → `BUILD_ENV.md` (`tools/win/Get-BuildEnv.ps1`). **Done 2026-11-11.** The file stays on the PC (git-ignored); the facts the build depends on are in the tables above.
2. Base script sources: where they are and how they unpack. **Done:** `Data\Scripts\Source\Base` in the Creation Kit folder.
3. All scripts compile with the real compiler (`tools/win/Build-Scripts.ps1`). **Done 2026-11-11: 8 of 8**, again after the change to `TLM:Core`.
3a. The plugin loads in the game and the core quest starts (`tools/win/Start-TestGame.ps1`). **Done 2026-11-12** on the second attempt.
3b. Stage events reach the quest scripts and the self-test passes. **Done 2026-11-12: 60 of 60**, after a first run failed 34 because the stages had no items.
3c. The self-test runs with nobody at the keyboard (`tools/win/Run-Scenarios.ps1`). **Done 2026-11-12: nine scenarios, 220 checks, 0 failed.**
4. The generated plugin opens in the Creation Kit without errors, and the quest, stages, aliases and script properties look as intended.
5. Vanilla EditorIDs: `Caps001` **done**; `PlayerRef` **done** (as record `000014`, vouched for by the game's own quests); the .44 revolver and its ammo still to do.
6. Alias behaviour: Create Reference to Object — In (still to do); the Essential flag and the Protected flag (**done 2026-11-12** for kills by script, see the Papyrus table); alias on the player receiving `OnPlayerLoadGame` (**done 2026-11-12**).
7. `Kill` on a Protected actor (**done 2026-11-12**); `Disable` on an aliased actor (**done 2026-11-12**).
8. Message box with a hidden button: which index comes back.
9. Distance events (**done 2026-11-12**). Timers and distance registrations across a save and load (still to do).
10. Dialogue: option count, speech checks, unvoiced lines, and whether an actor in a hold-up will talk (A11).
11. The remaining console commands.
