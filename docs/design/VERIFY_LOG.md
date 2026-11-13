# Verification log

**Dates:** 2026-11-11 to 2026-11-13. **Sources:** the Fallout 4 Creation Kit wiki (falloutck.uesp.net), read through its API; the build runs on the owner's PC; the owner's report of the first attempt in the game; and Mod Organizer's source on GitHub.
**Not checked:** anything inside the Creation Kit editor. In the running game (all on 2026-11-12): the plugin loads, its scripts run, and 62 scripted scenarios pass all 1,560 of their checks with nobody at the keyboard. 49 of them are the rows of the two quests' test matrices, played with actors and markers made at run time and compared with the logic model after every event; four more do two things at once. The commit that did this, `c1e6d48`, carries the tag `mq01-logic-proof`. Nothing is placed in the world, so nothing that needs a built place, dialogue, a save or a player has been tested: triggers, pickups and conversations are stood in for by stage numbers, and ten rows of the matrices cannot be played this way at all.

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

What the game was seen to do in these runs is now also written down as rules in `tools/papyrus_sim`, a stand-in for the game that runs the project's real scripts on a machine without Fallout 4. Replaying the four recorded runs in it, with the scripts as they were at each commit, gives what the game gave each time (`tools/papyrus_sim/game_runs.json`, checked by `tools/run_checks.sh`). That makes it a fair rehearsal for a script change before it goes to the PC. It is not evidence about the game: where a rule in it is marked "assumed", only the game can say.

### Prepared for the next run: the test matrix as cases

Written after the ninth run, before any of it had been compiled or run. It has since run: see "The test matrix passes in the game" below.

The rows of the two test matrices are now cases the game can play with nobody at the keyboard: 49 cases, 309 events, 1,236 checks (self-test scenarios 101 to 128 for the main quest, 201 to 221 for the side quest). A case is a list of the logic model's events. For each event `TLM:CaseDriver` does what stands for it in the game, then compares everything it can see of both quests with the state the model reaches after that event: every stage of both quests, the outcome, method and reputation, the debrief variant and answer, both pairs of objectives, the four counters, who is alive, who is in the town aliases, whether the Cutters are disabled, the cargo, the three quest items, the evidence count and level, the side quest's outcome and its three flags, Haskell, and the caps from a sale. The cases themselves (`TLM:MatrixCases`) are written by `tools/gen_matrix_cases.py` from the model, so no expected value is typed by hand. `tools/matrix_cases.json` lists each case, the rows it stands for and its events.

Three kinds of step: an event the model allows; an *attempt* at an event the model does not allow, where the guard is in the quest script and nothing may change (a second debrief answer, the evade timer during a fight, killing a caravan hand in town, a decision without evidence, a second decision, recovery with nothing to recover); and one place where the script turns a request into another one (naming Haskell when he is dead posts the pages with no name).

What stands for what, as before: a trigger, a pickup or a line of dialogue is its stage number; picking up the dispatch, the ledger or the journal also gives the item; a kill by the player is `Kill` with the player named; leaving the ambush is moving its centre marker away; the timer running out is a direct call. Eight settlers and two markers are made for every case.

Rows no case stands for, and why:

| Row | Why not |
|---|---|
| T13 | ownership and theft: needs a placed container |
| T15, T16, S16 | need a save and a load |
| T20 | the sheriff's Essential flag: needs the placed actor |
| T22 | arrival at night: packages and time of day |
| T27 | clean plugin load: seen in every run, not a case |
| T28 | unrelated saves |
| S14, S20 | Pike dead, Vane dead: the guards are dialogue conditions, and there is no dialogue yet |
| T29, T29b | added 2026-11-13 (amendment A25): the timer during the conversation with the Cutter lead. There is no dialogue yet, and nothing else makes the game say he is talking to the player |

Also left out: the one attempt in T08 whose only guard is a dialogue condition (the deal after a fight has started).

Two places where the logic model and the scripts disagreed came out of this, and the model was the one that was wrong both times (DESIGN_AMENDMENTS_v0.2.md, test matrix changes): the hand-over does not set stage 900 when the dispatch is missing, and deciding with a lost ledger does not give the ledger back.

All 49 cases, and the nine older scenarios, pass when the real scripts are run in the stand-in engine. Its tests also show the checks bite: a changed rule in either quest script, a stage the model does not expect, and each single expected value changed in turn (46 of them) are all reported. One hole was found that way and closed: the first version of the driver read any expected value below zero as "not looked at", and the counters do go below zero.

What only the game can say, and the next run will: whether eight settlers at once behave; whether stage 37 (the Cutters turning on the player) puts the player in combat; whether `StopCombat` on the Cutters and `StopCombatAlarm` on the player end it (case 121; the stand-in engine simply assumes so); and everything else the stand-in engine marks as assumed.

One thing the stand-in engine could not show, found by an independent read of the driver before it went to the PC: in the stand-in nothing takes time, so two script threads never overlap. In the game they do. When the player leaves a live ambush, the quest sets stage 32 on a thread of its own, and the stage reads as done while its handler is still at work; the handler kills the drover last. The driver waited only for the stage, so its next step, the town stage, could arrive first, find the drover alive and put him in the town alias, where he cannot be killed. Four cases would have failed for that reason and not for anything in the rules. The driver now waits for the handler to have finished. With an engine copy that charges time for every call into the game, those cases failed before the change at some timings and none fail after it.

**Open, in the quest itself** (closed since: see "After the matrix: time" below): the same overlap is possible in play if the town stage follows a distance-triggered "evaded" within a fraction of a second, which needs something like fast travel from a live ambush to a spot inside the town gate's trigger. The result would be a drover alive in town who should be dead; no counter or outcome depends on it.

### The test matrix passes in the game, 2026-11-12

Tenth run, 14:07 to 14:42 by the PC's clock, commit `499104e`, started with `tools\win\Update-And-Run.ps1 -Install -Unattended`. Reported as the pasted results. Nobody touched the game. 58 game sessions took 2,097 seconds, 36 seconds each on average.

| What | Result |
|---|---|
| Scripts compile | Passed: `TLM:CaseDriver`, the generated `TLM:MatrixCases` (2,665 lines) and the changed `TLM:SelfTest` on their first compile |
| **All 58 scenarios** | **Passed: 1,456 checks, 0 failed.** Every session closed itself |
| The nine earlier scenarios | The same passes, the same reported lines and the same stage-event counts as in the ninth run |
| The 49 matrix cases | Each passed exactly as many checks as the generator wrote for it (four per event) |
| The game's script log | No error or warning naming this project in any of the 58 sessions (the report lists them for every session that has any) |
| Afterwards | Everything put back; the installed plugin identical to the build |

So for every row of the two matrices that can be played without a built place, a save or dialogue, the quest scripts did in the game what the logic model says, at every step, in everything the driver can see. That is 28 cases for the main quest (rows T01 to T12d, T14 to T14c, T17 to T19c, T21, T23 to T26c) and 21 for the side quest (S01 to S13, S15, S17 to S19, S21 to S24).

What the game showed that had only been assumed:

| What | Result |
|---|---|
| Eight settlers made at once and forced into aliases | Behaved; no case was disturbed by them |
| Stage 37, the Cutters turning on the player | The player was in combat afterwards, and survived four attackers for the seconds the case lasts (case 106). Whether that was `Debug.SetGodMode` or luck is not known |
| Ending a fight by script | After `StopCombat` on the four Cutters and `StopCombatAlarm` on the player, the player was out of combat, and the evade timer's function then resolved the ambush (case 121). Which of the two calls did it is not known |
| The evade timer during a fight | Did not resolve the ambush (case 119) |
| An objective completed without ever having been shown | Reads as completed (case 213, the side quest's second objective after "destroy") |
| A caravan hand in the town alias | Neither could be killed with the player named as killer (case 118) |
| The three unnamed Cutters | Their deaths alone did not resolve the ambush; the lead's then did (case 103) |
| Recovery | Stage 900 gave back a lost dispatch and a lost ledger once, and gave nothing unearned (cases 124, 125, 218) |
| The hand-over without the dispatch | Stood, and did not set stage 900 (case 126) |
| Naming Haskell when he is dead | Posted the pages with no name (case 217) |
| The sale | Took the ledger and the journal and gave 120 caps (case 212) |
| Leaving a live ambush with the caravan there, then the town stage | The drover was dead and out of the town alias in all four cases that do this (110, 120, 122, 123), with the driver waiting for the evade handler to finish first |

The stand-in engine (`tools/papyrus_sim`) had given the same 58 results beforehand, check for check. This run is now the fifth recorded in `tools/papyrus_sim/game_runs.json`.

What this is not. No trigger was walked into, nothing was picked up from the world, no line was spoken, nothing was saved or loaded, no AI package ran, and there is no place. A stage number stood for each of those. The ten rows listed above remain unplayed. And one fault is known in the quest script that no case provokes yet: the overlap described under "Prepared for the next run".

### After the matrix: time

Written after the tenth run and before the eleventh, when none of it had been compiled or run in the game; what the game then did with it is in the next section but one ("The guards in the game"). Everything in this section was found and checked in the stand-in engine, which is not the game.

The logic model has no time in it: an event is over before the next begins, and the 49 cases that passed play it that way, waiting after each step. The game does not keep to that, in two ways already seen in it. A death is announced about a second after it happens (`OnDeath` comes "when the actor has finished dying", while `IsDead` is true at once). And every handler runs on a thread of its own and gives other threads a turn at each call it makes into the game.

Looking for what that does to the quest script found three faults in the version that passed the matrix (amendment A24):

| What happens | What the script as tested does | What it should do |
|---|---|---|
| The player kills the Cutter lead, and within the next second the evade timer runs out, the player gets beyond the evade distance, or the town stage is set | Records "evaded": the drover is killed by script and the wagon looted, though the player has just saved them | A rescue |
| The town stage is set while "evaded" is still being handled on another thread | Puts the still-living drover into the town alias, where the kill that follows cannot touch him | The drover dead and not in town |
| Two resolutions are being handled at once | Can leave a mixture (the outcome of one, the bodies of the other), or let "evaded" overwrite a betrayal | One of them whole; a betrayal always stands |

None of these needs more than ordinary play: the first needs a quiet kill of the lead near the end of the timer, or leaving at once; the second something like fast travel from the ambush to the gate.

Three guards were added to `TLM:MQ01Quest`; no rule changed. How they were checked, without the game:

- The stand-in engine got a second mode in which every call out of a script takes a frame, so that threads overlap where the game lets them. It is a way of provoking overlaps, not a measurement.
- Four cases were added that do two things with no time between them (scenarios 129 to 132). With the quest script as it was at `499104e`, the first three fail in the ordinary mode and the fourth fails when calls take time, each with the fault in the table above. With the guards all four pass in both modes, and so do all 62 scenarios at 30, 60 and 144 calls a second.
- Two more tests set two resolutions going a few frames apart, 100 and 100 ways. With the guards the result is always one of them whole, and a betrayal always stands; with the old script it is not.

**The guards as first written were not enough.** They were given to an independent reader (a second session with no part in writing them, working from the code and the stand-in engine). It found nothing that should fail to compile and no change to ordinary play, and three gaps, each of which still let a fault from the table above through under some timing:

| Gap | What could still happen | Closed by |
|---|---|---|
| `WaitForResolutions` read the number of handlers at work first and then called into the game to count the stages. A handler could begin during those calls: no longer "set and yet to begin", and not counted as at work | The town stage goes ahead beside an "evaded" that has just begun: the drover alive in town | Reading the number of handlers at work last, with no call after it |
| The town stage waited before the resolution it asks for itself, but not after it | When the distance watch resolves the ambush at the same moment, the town stage's own request stands aside, and it moves the hands while the other handler is still killing and looting | A second wait after its own resolution |
| A betrayal that saw no outcome yet, and then lost the claim to a resolution that began in that instant, wrote at once | The other resolution writes its outcome afterwards: a betrayal lost | A betrayal that is not the first resolution waits again before it writes |

The same reading showed two weaknesses in the tests: nothing in them could tell the first or the third gap from a sound script, and cases 129 and 130 would pass without the guard having done anything if the death happened to be announced first. So:

- The guards now write a line to the game's script log when they change what happens (`TLM_MQ01: A24 ...`). The runner's report lists those lines under "Timing", with what case 132 notes about the overlap. A pass with no such line means the game's timing never asked the guard to act; it does not mean the guard works.
- The stand-in engine got a third mode, in which the timing is shaken: every call into the game takes 0 to 3 frames, a stage's handler begins 0 to 3 frames after the stage reads as set, events arrive up to 3 frames late, and threads that are ready in the same instant run in any order; differently for each of any number of seeds. This is harsher than the game is documented to be (there a call on the script's own quest gives no other thread a turn). `python3 tools/papyrus_sim --shake 5 all` runs scenarios this way.

Four pairs of things happening at once were then run under that shaking (`tools/papyrus_sim/test_overlap.py`, class `Shaken`). The number of runs that ended in a state the logic model does not allow (measured again on 2026-11-13, after the later changes to the script and to the stand-in; one figure moved, from 7 to 11, which is all a different shaking means):

| The quest script | Leaving, and the gate (760 runs) | Saved, and evaded (240) | A betrayal, and the timer (2,600) | The lead dead, and the gate (120) |
|---|---|---|---|---|
| Before the guards (`499104e`, the version that passed the matrix in the game) | 626 | 10 | 223 | 120 |
| The guards as first written (`8b94566`) | 522 | 0 | 95 | 0 |
| As it is now, with the first gap opened again | 8 | 0 | 0 | 0 |
| As it is now, with the second gap opened again | 191 | 0 | 0 | 0 |
| As it is now, with the third gap opened again | 0 | 0 | 11 | 0 |
| **As it is now** | **0** | **0** | **0** | **0** |

These numbers say nothing about how often any of it would happen in the game, where the timing is far gentler. They show that each of the three corrections is needed, and that the tests now notice when one is missing: each row but the last is a test that must find at least one wrong ending. All 62 scenarios also pass under the shaking, each three ways.

**Any two things at once.** Those four pairs were chosen by hand, and the reading had just shown what hand-picked pairs miss. So every ordered pair out of twelve things that can happen at a live ambush was run as well: the lead, another Cutter or either caravan hand killed by the player; Nell dead by nobody's hand; the timer; leaving; the gate; the three ways the conversation with the lead can end; a fight beginning. The second was fired zero to seven frames after the first, each 40 shakings: 42,240 runs. Asked of each: is the end one that the logic model gives for those two events in one order or the other? With the script as it is, every time. With the script before the guards, and with the guards as first written, not. The test suite keeps a smaller sweep for the script as it is, and two smaller still that must catch the older versions (`test_overlap.py`, class `AnyTwoThingsAtOnce`); since 2026-11-13 it has a thirteenth thing in it, the conversation with the lead being open (3,120 runs). This does not say which of two near-simultaneous things ought to win. It says the result is never a mixture of both, and a betrayal is never lost.

One thing the sweep does not look at, on purpose: when two resolution stages are set in the same instant, both read as set afterwards though only one was applied. Nothing reads those flags today; amendment A24 records what that means for the log entries still to be written.

What the next run can show: that the changed quest script compiles and still passes everything it passed, and cases 129 to 131. Whether the guard acted in those three, and whether the overlap of case 132 happened at all in the game, is in the "Timing" part of the report; a case that passes without its guard having acted has shown nothing about the guard, and the report now says which it was.

### The guards in the game, 2026-11-12

Eleventh run, 20:06 to 20:45 by the PC's clock, commit `c1e6d48`, started with `tools\win\Update-And-Run.ps1 -Install -Unattended`. Reported as the pasted results. Nobody touched the game. 62 game sessions took 2,344 seconds, 38 seconds each on average.

| What | Result |
|---|---|
| Scripts compile | Passed: the changed `TLM:MQ01Quest` (the guards of A24 with the three corrections), `TLM:CaseDriver` with its four new actions, and the regenerated `TLM:MatrixCases`, on their first compile |
| **All 62 scenarios** | **Passed: 1,560 checks, 0 failed.** Every session closed itself |
| The 58 scenarios of the tenth run | Each the same number of passes as then; for the nine older ones the same reported lines and stage-event counts as well. So the guards changed nothing where one thing happens at a time |
| Cases 129 to 132 | Passed: 28, 28, 24 and 24 checks |
| The game's script log | No error or warning naming this project in any of the 62 sessions |
| Afterwards | Everything put back; the installed plugin identical to the build |

What the "Timing" part of the report showed, which is the part that says whether a guard did anything:

| Case | In the game |
|---|---|
| 130: the lead killed, and the player gone before his death is announced | The guard acted: "the Cutter lead is already dead: a rescue, not an evasion" |
| 131: the lead killed, and the town stage before his death is announced | The guard acted, with the same line |
| 132: leaving a live ambush and reaching the gate in the same breath | The overlap happened: the town stage was set while the evade stage's handler was still at work. The town stage waited "3 tenths of a second for another resolution to finish", and the drover was dead and out of the town alias, as the model says |
| 129: the lead killed, and the timer runs out before his death is announced | Passed, with no line from the guard. Only one path through the script gives that: the timer's function found the player in combat straight after `Kill(player)` and started the timer over, and the death, announced a second later, made it a rescue. So the game takes a kill by the player for a fight, and on the timer's path the fight rule (A2) got there before the guard could |

So, of what amendment A24 lists: the town stage arriving beside a half-finished "evaded" was provoked in the game and the guard held; a rescue mistaken for an evasion was provoked on two of its three paths and the guard made it a rescue; on the third path, the timer, the case as written showed nothing about the guard.

What follows from case 129:

- A fact about the game, seen indirectly: straight after `Kill` with the player named as the killer, the player is in combat. How long, and whether it needs the three other Cutters standing by, is not known. Two seconds after such a kill the player was out of combat again (scenario 5, every run).
- The stand-in engine had it wrong. It gave the same 62 results beforehand, check for check, and the same lines for 130, 131 and 132 (132 only in its mode where calls take a frame, and there the same three tenths, which is a coincidence and not a prediction: that mode is for provoking overlaps). For 129 it had the guard acting. Its rule now says a kill by the player counts as a fight with the player until the death is announced, marked as seen indirectly and assumed in its details. The run is the sixth recorded in `tools/papyrus_sim/game_runs.json`, with the lines the guards wrote, so the replay fails if the stand-in gives 129 any other way.
- Case 129 is changed so that the next run can show the guard on the timer's path: the kill is made a quiet one (the three Cutters still standing are told to stand down and the alarm against the player is ended, as after "break_combat") before the timer's function is called. Whether that is enough to end the fight in the game is reported in two INFO lines; the case passes either way. Scenario 2 reports the same question with nobody standing by. Not yet compiled.
- From now on the quest script also says in the script log when the evade timer was held back and by what: `TLM_MQ01: A2 ...` for a fight, `TLM_MQ01: A25 ...` for the conversation. With that line in the eleventh run, case 129 would have explained itself.

### The tag `mq01-logic-proof`

Owner decision, 2026-11-13: the commit that passed the eleventh run is to carry the tag `mq01-logic-proof`. That also settles what was left of decision D8. The runbook had called this milestone the test matrix played in a built test cell; the tag now stands for the scripted proof with actors and markers made at run time, and playing the matrix in a built cell is still to do.

What the tag says, in full, is in [`tags/mq01-logic-proof.txt`](tags/mq01-logic-proof.txt): what passed, what that covers, and what it does not (ten rows of the matrices, anything in a built place, dialogue, saving and loading, the Creation Kit, the quest as a player would meet it).

State of the tag itself: **on GitHub since 2026-11-13.** The owner created and pushed it from the PC with `tools\win\Push-MilestoneTag.ps1` (08:32 by the PC's clock; the script's message came back by the clipboard). Checked from the session that wrote this record: it is an annotated tag, it points at `c1e6d48`, and its text is the text of `tags/mq01-logic-proof.txt` to the letter.

How it got there. The session that wrote this record is allowed to push the branch but not tags: the push of the tag was refused three times, the last after the owner had reconnected GitHub to it, while a push of the branch went through each time. So the tag had to come from the PC. (After the first version of that script was handed over, the owner's next paste was the eleventh run's report again: the script printed its message but did not copy it to the clipboard, as every other script here does. It does now, and it can be started through the usual command.)

First run of the script on the PC, 2026-11-12 22:06 by its clock: it read the text, found the commit, asked GitHub (no tag there), and stopped when git refused to create the tag, because git on that PC had no name and e-mail to put on it. Nothing was created and nothing was pushed, and the message came back by the clipboard. The script now proposes the name and GitHub no-reply address that most of the repository's own commits already carry, and leaves out of its message the Windows account and PC name that git prints in that error. With that identity set for the folder, the second run created the tag and pushed it.

### The timer and the conversation, 2026-11-13

Not yet compiled and not yet run in the game. Owner decision D9: the evade timer is to be held while the player is talking to the Cutter lead (amendment A25).

The fault it removes was in the design, not in the script: 90 seconds after the ambush goes live the timer resolved it as "evaded" unless the player was fighting, and a hold-up conversation is not a fight. A player still choosing a line in the 91st second had the drover killed and the wagon looted under the conversation, and the line then chosen was silently refused.

What was done, in the order the project asks for:

| Where | What |
|---|---|
| Logic model | A state "the conversation is open", two events (it opens; it is left without a line being chosen), and the rule: the timer does nothing while it is open. The conversation closes by itself whenever the lead can no longer be talked to. Two matrix rows, T29 and T29b. The exhaustive search finds no violation under the amended rules, and finds the fault under the v0.1 rules |
| `TLM:MQ01Quest` | One condition in `EvadeTimerElapsed`: if the lead `IsInDialogueWithPlayer`, the timer starts over, as it does during a fight. No flag is kept; the game is asked each time. When the timer is held back the script writes which rule did it to the script log (`TLM_MQ01: A2 ...` for a fight, `TLM_MQ01: A25 ...` for the conversation) |
| Plugin | Nothing: no record changes |
| Stand-in engine | A switch on an actor, "is talking to the player", that only a test flips. Nine tests (`tools/papyrus_sim/test_conversation.py`) with the real 90-second timer: it does not run out on a conversation of any length, and the script says so; a deal taken afterwards is a deal; after the conversation it runs out on its next turn; a fight holds it back and is reported as a fight; leaving, each line and a killing are not held back; an empty alias is not asked; and with the script as it was before the rule the deal is lost. The conversation is also one of the thirteen things in the sweep of pairs, which cannot see the rule itself (either order of "talks" and "the timer runs out" is allowed there) but would see anything else being held back |

What "held" means here. It is not a stopwatch that stops and goes on. The timer is looked at when it runs out: if the conversation is open at that moment it starts over with its whole 90 seconds, as it does for a fight. A conversation that is over before the 90 seconds are up does not lengthen them; one that is open when they run out buys a whole new 90. What is guaranteed is only that the ambush is never resolved under an open conversation. The logic model has no time in it and cannot tell the two readings apart; if the owner wants a true pause, that is a change to the script alone.

An independent read of this change found no fault in the rule or the script, and three in my tests of it, all corrected before any run. The model's test for row T29 had slipped under another row's "skip" mark and never ran. One stand-in test did not happen when it said it did, because the engine's clock stayed where the last event had left it, so it tested nothing; the engine's `run` now leaves the clock where it was told to, and that test fails if the guard of A24 is taken out. And a third compared nothing that the failed speech check changes. The same read asked for the line the script now writes when it holds the timer back, without which a held timer in the game could not be told from a fight.

What the game can say today, and what it cannot. The plugin has no dialogue, so nothing can make the game answer "yes, he is talking to the player". The next run shows only that the question compiles and is answered "no" when nobody is talking: scenario 2 asks it outright (one check more, 15), and every case in which the timer resolves the ambush depends on that answer (if the game counted a settler's greeting as a conversation, those cases would fail, and the `A25` line would say why). Rows T29 and T29b stay unplayed in the game until the hold-up conversation exists. Whether the game's answer is "yes" for the whole of a conversation, the player's turn to choose included, is checklist item 10a.

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
| The player "in combat" after `Kill(player)` | Seen in the game, indirectly | Not on the wiki. In the eleventh run (2026-11-12, case 129) the evade timer's function, called straight after `Kill` with the player named as killer, did not resolve the ambush and wrote no guard line: it can only have found the player in combat. Two seconds after such a kill the player is out of combat (scenario 5). *Needs the game:* asked outright from the next run on, with and without bystanders, and whether `StopCombatAlarm` ends it. |
| `OnCombatStateChanged` | Seen in the game | `Event OnCombatStateChanged(Actor akTarget, int aeCombatState)`. On 2026-11-12 an alias script received it, with the player as target, when `StartCombat(player)` was called on its actor. |
| `IsInDialogueWithPlayer` | Documented | `bool Function IsInDialogueWithPlayer() native`, a member of ObjectReference: "Is this actor or talking activator currently talking to the player?" Used by A25 on the Cutter lead's actor. *Needs the game twice over:* that it answers "no" when nobody is talking (asked in self-test scenario 2 from the next run on), and that it answers "yes" for the whole of a conversation, which cannot be seen until there is one. |
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
3d. The rows of the two test matrices that need no built place, save or dialogue, played in the game and compared with the logic model after every event. **Done 2026-11-12: 49 cases, 1,236 checks, 0 failed**, and again in the eleventh run.
3e. The guards against late deaths and overlapping handlers (A24) in the game. **Done 2026-11-12 for three of the four cases** (130, 131, 132: the guard was seen to act; in 132 the overlap itself was seen). Case 129, the timer's path: still to do, with the kill made a quiet one.
4. The generated plugin opens in the Creation Kit without errors, and the quest, stages, aliases and script properties look as intended.
5. Vanilla EditorIDs: `Caps001` **done**; `PlayerRef` **done** (as record `000014`, vouched for by the game's own quests); the .44 revolver and its ammo still to do.
6. Alias behaviour: Create Reference to Object — In (still to do); the Essential flag and the Protected flag (**done 2026-11-12** for kills by script, see the Papyrus table); alias on the player receiving `OnPlayerLoadGame` (**done 2026-11-12**).
7. `Kill` on a Protected actor (**done 2026-11-12**); `Disable` on an aliased actor (**done 2026-11-12**).
8. Message box with a hidden button: which index comes back.
9. Distance events (**done 2026-11-12**). Timers and distance registrations across a save and load (still to do).
10. Dialogue: option count, speech checks, unvoiced lines, and whether an actor in a hold-up will talk (A11).
10a. Once the hold-up conversation exists: does `IsInDialogueWithPlayer` on the Cutter lead read true from the first line to the last, the player's turn to choose included (A25)? Stand in the conversation past the 90th second and look in the script log for `TLM_MQ01: A25 the evade timer ran out during the conversation`. The ambush still being live is not enough by itself: a fight gives the same (the log then says `A2`), and so would a timer that does not count while a conversation is open. Rows T29 and T29b.
11. The remaining console commands.
