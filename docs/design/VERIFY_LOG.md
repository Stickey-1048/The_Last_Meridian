# Verification log

**Date:** 2026-11-11. **Sources:** the Fallout 4 Creation Kit wiki (falloutck.uesp.net), read through its API; and, from the same day, the first build run on the owner's PC.
**Not checked:** anything inside the Creation Kit editor or the running game.

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

Still not done anywhere: opening the plugin in the Creation Kit, loading it in the game, any quest test.

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
| `coc`, `startquest`, `setstage`, `getstage`, `sqs`, `sqt`, `prid`, `kill`, `tgm`, `player.additem` | Needs the game | No page on the wiki. |

## Checklist for the game PC

1. Game build, Creation Kit build, install paths → `BUILD_ENV.md` (`tools/win/Get-BuildEnv.ps1`). **Done 2026-11-11** (the file is on the PC, not yet in the repository).
2. Base script sources: where they are and how they unpack. **Done:** `Data\Scripts\Source\Base` in the Creation Kit folder.
3. All seven scripts compile with the real compiler (`tools/win/Build-Scripts.ps1`). **Done 2026-11-11: 7 of 7.**
4. The generated plugin opens in the Creation Kit without errors, and the quest, stages, aliases and script properties look as intended.
5. Vanilla EditorIDs: `Caps001` **done**; `PlayerRef` fix awaiting a re-run; the .44 revolver and its ammo still to do.
6. Alias behaviour: Create Reference to Object — In; Essential and Protected flags; alias on the player receiving `OnPlayerLoadGame`.
7. `Kill` on a Protected actor; `Disable` on an aliased actor.
8. Message box with a hidden button: which index comes back.
9. Timers and distance registrations across a save and load.
10. Dialogue: option count, speech checks, unvoiced lines, and whether an actor in a hold-up will talk (A11).
11. The remaining console commands.
