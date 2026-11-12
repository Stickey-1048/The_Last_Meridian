# Verification log

**Dates:** 2026-11-11 and 2026-11-12. **Sources:** the Fallout 4 Creation Kit wiki (falloutck.uesp.net), read through its API; the build runs on the owner's PC; the owner's report of the first attempt in the game; and Mod Organizer's source on GitHub.
**Not checked:** anything inside the Creation Kit editor. In the running game, only that the test room loads; the plugin has not been seen to load.

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
- `TLM:Core` writes `TLM_Core: started` to the game's script log when its quest starts, and shows "The Last Meridian test build is loaded." on screen a few seconds later (development only). That script change is not yet compiled.

Still not done anywhere: opening the plugin in the Creation Kit, loading the plugin in the game, any quest test.

Each `[VERIFY]` tag in the v0.1 designs ends up in one of three states:

- **Documented** — the wiki states it. Good enough to write code against; behaviour still has to be seen in the game.
- **Corrected** — the wiki contradicts or improves on the v0.1 assumption. The amendment is in [DESIGN_AMENDMENTS_v0.2.md](DESIGN_AMENDMENTS_v0.2.md).
- **Needs the game** — the wiki is silent, or the item is a fact about the installed build. Listed again at the end as the checklist for the game PC.

Native signatures used by the scripts are recorded in [`tools/papyrus_natives.json`](../../tools/papyrus_natives.json) with the page each came from, and are enforced by `tools/check_consistency.py`.

## Papyrus

| Item | State | What the wiki says |
|---|---|---|
| `StartTimer` / `OnTimer` on a quest script | Documented | `Function StartTimer(float afInterval, int aiTimerID = 0)`, `Event OnTimer(int aiTimerID)`, members of ScriptObject. Starting a timer whose ID is already running resets it. Time only counts outside menus and follows the global time modifier (VATS, Jet). Quests and aliases cancel their timers when the quest stops. |
| Do timers survive a save and load? | Needs the game | Not stated. The scripts do not rely on it: the evade timer and distance watch are re-armed on every load. |
| `GlobalVariable.SetValue` | Documented | `SetValue(float)`, plus `SetValueInt(int)`, `GetValueInt()`, and `Mod(float)` which is thread-safe. The scripts use `Mod` for all increments. |
| Quest stage fragments are unavoidable | Corrected | `Event OnStageSet(int auiStageID, int auiItemID)` exists on Quest and runs alongside any fragment. The scripts use it for everything, so there are no fragments (A12). |
| Setting a stage twice | Corrected | "SetStage has no effect after it is called the first time for any stage on a running quest" unless Allow Repeated Stages is on. v0.1's repeatable stage 15 (SQ01) and stage 900 could not work as written (A12, A15). |
| Alias scripts before the quest starts | Corrected | Aliases receive their reference's events as part of a running quest. SQ01 must already be running for clue scripts to fire (A8). |
| `OnContainerChanged` | Documented | `Event OnContainerChanged(ObjectReference akNewContainer, ObjectReference akOldContainer)`. Once an object is in a container it "ceases to exist in most cases". |
| `OnTriggerEnter` | Documented | `Event OnTriggerEnter(ObjectReference akActionRef)`. Can arrive out of order with `OnTriggerLeave`; the trigger's collision layer decides what fires it. |
| `OnDeath` | Documented | `Event OnDeath(Actor akKiller)`, "when the actor finishes dying". `OnDying` fires at the start. |
| `OnPlayerLoadGame` | Documented | Sent only to the player actor; fires "for the first time on the next load". An alias pointing at the player should receive it, since aliases get their reference's events. *That last step needs the game.* |
| `OnCombatStateChanged` | Documented | `Event OnCombatStateChanged(Actor akTarget, int aeCombatState)`. |
| `OnHit` | Documented | Needs `RegisterForHitEvent` first and fires once per registration. The scripts use `OnCombatStateChanged` instead. |
| Distance polling | Corrected | `RegisterForDistanceGreaterThanEvent(ScriptObject, ScriptObject, float)` and `Event OnDistanceGreaterThan(...)` exist and the wiki recommends them over polling `GetDistance`. |
| `Message.Show` return value | Documented | "If the message displays a message box to the user, it returns the button the user hit. If it doesn't, it will return -1 immediately." |
| Does a hidden button shift the returned index? | Needs the game | Not stated. |
| `RemoveItem` | Documented | `RemoveItem(Form akItemToRemove, int aiCount = 1, bool abSilent = false, ObjectReference akOtherContainer = None)`. |
| `Kill`, protection | Documented | `Kill(Actor akKiller = None)`; `SetProtected(bool abProtected = true)`; `SetEssential` then overrides alias flags. Protected: "The Player is the only one allowed to kill a Protected Actor." |
| Does `Kill` work on a Protected actor? | Needs the game | Not stated. The scripts clear the flag first. |
| Removing an NPC without a dangling alias | Needs the game | `Disable()` is documented; the alias stays filled. |
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
| `cqf` (CallQuestFunction) | Documented | `CQF <quest> <function> [params]`. Missing parameters are filled with zero or None, not with the script's defaults. |
| `sqv` (ShowQuestVars) | Documented | `SQV <QuestID> [filter]` shows variables, aliases and quest state. |
| `coc` | Seen in the game | `coc qasmoke` typed at the main menu loaded the test room (2026-11-12). |
| `startquest`, `setstage`, `getstage`, `sqs`, `sqt`, `prid`, `kill`, `tgm`, `player.additem` | Needs the game | No page on the wiki. |

## Checklist for the game PC

1. Game build, Creation Kit build, install paths → `BUILD_ENV.md` (`tools/win/Get-BuildEnv.ps1`). **Done 2026-11-11.** The file stays on the PC (git-ignored); the facts the build depends on are in the tables above.
2. Base script sources: where they are and how they unpack. **Done:** `Data\Scripts\Source\Base` in the Creation Kit folder.
3. All scripts compile with the real compiler (`tools/win/Build-Scripts.ps1`). **Done 2026-11-11: 8 of 8** (`TLM:Core` has changed since and awaits a recompile).
3a. The plugin loads in the game and the core quest starts (`tools/win/Start-TestGame.ps1`). **First attempt failed 2026-11-12:** see above.
4. The generated plugin opens in the Creation Kit without errors, and the quest, stages, aliases and script properties look as intended.
5. Vanilla EditorIDs: `Caps001` **done**; `PlayerRef` **done** (as record `000014`, vouched for by the game's own quests); the .44 revolver and its ammo still to do.
6. Alias behaviour: Create Reference to Object — In; Essential and Protected flags; alias on the player receiving `OnPlayerLoadGame`.
7. `Kill` on a Protected actor; `Disable` on an aliased actor.
8. Message box with a hidden button: which index comes back.
9. Timers and distance registrations across a save and load.
10. Dialogue: option count, speech checks, unvoiced lines, and whether an actor in a hold-up will talk (A11).
11. The remaining console commands.
