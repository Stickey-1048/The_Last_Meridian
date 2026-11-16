# Separate fresh exterior story launcher — source candidate

This adds a separate entry route to the reviewed36fa exterior story source. It does not replace the shell launcher/profile, install anything or certify native startup/playthrough. The source composes the reviewed7f3 departure runtime. Read the exact artifact/runtime pins in `tools/win/world-story-artifact.json`; rebuilding the PEX or plugin requires a newly reviewed manifest, not bypassing its checks.

## Root-controlled preparation

Create the separate `TLM-World-Story-Preview` MO2 profile with local settings and local saves. In a separate physical mod `TheLastMeridian-WorldStoryPreview`, stage the exact286B TheLastMeridian.esp master, this candidate's TLMWorldSlice.esp, and all19 candidate PEX under Scripts/TLM. Use copies, not edits to the owner Dev/WorldSliceQA mods. Enable this mod; disable other Meridian/probe/runtime mods. Optional approved mods are F4SE Scripts0.6.23, FallUI - Workbench and Mod Configuration Menu. Both plugins must be active in master-then-addon order, with no other non-vanilla plugin active. Keep the source development scenario0.

All Meridian files come from the single isolated mod, eliminating runtime priority ambiguity. Extra TLM scripts/plugins in overwrite, physical game Data or the other enabled roots are refused; extra Meridian BA2 archives are refused. The launcher pins the master, addon and all19 PEX, and refuses missing/extra runtime files. This is integrity checking of the known loose-file fixture, not an assertion that arbitrary compromised system configuration cannot interfere.

Use only the managed Fallout4.exe1.10.163.0. `tools/win/Play-WorldStory.cmd` opts into the supported existing F4SE0.6.23 loader. It installs nothing. Direct PowerShell use can omit -UseF4SE only when no F4SE-dependent UI mod is enabled. Existing gamepad preferences remain unchanged. Root's disposable mouse/keyboard QA profile is a separate concern.

```powershell
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File tools/win/Play-WorldStory.ps1 -UseF4SE -ValidateOnly
```

ValidateOnly starts nothing, writes nothing and refuses unfinished recovery notes or existing startup commands. Close the game and MO2 before validation/launch. After the actual native entry gates pass, the .cmd is the owner-facing shortcut. No owner should need to type COC/CQF manually for this route.

## Explicit delayed startup and safety boundary

The owned startup batch is fresh-main-menu COC to TLM_WS_Clearing, the existing seven SPECIAL4 writes, then `cqf TLM_WS_Entry QueueFreshEntry`. Stat writes are exclusively in that fresh-start batch; no quest/load handler changes a character's stats, levels, perks or inventory.

QueueFreshEntry is explicit only: neither OnQuestInit nor OnPlayerLoadGame starts it. It starts the wrapper quest so its forced player alias receives OnPlayerLoadGame. Readiness polls use a one-second Papyrus timer, at most30polls, requiring a player, loaded3D, the exact clearing cell and no menu mode. **These are30timer polls, not a guaranteed30seconds of wall time**: engine menus/loading can suspend timers. It rechecks original preview/main/side running and stage state and the section state before dispatching existing Begin. Duplicate requests cannot rebind/restart. Timeout or invalid quest state cancels that session's request. The entry never resets/stops an existing quest or enables controls/AI.

The player alias's saved-load event cancels a pending request and timer, without changing an already-started section. Native event delivery/order still needs actual testing. These guards do not establish the complete history of an arbitrary save; the launcher is for fresh disposable main-menu COC sessions only. Never use it as an existing-character migration tool. Quit without saving during prototype acceptance.

## Recovery and outcome

The launcher uses its own `build/world-story.unfinished.json` ownership note, separate from the shell. It records the previous startup/activity settings before creating the uniquely named batch. When both game and manager have closed, it restores those settings and removes only the matching owned batch. Changed/ambiguous/pre-existing batch files are preserved and reported; unrelated INI keys/controller settings are preserved. If game/manager is still running, the note is retained. Keep the launcher window open until restoration is confirmed. Never delete a recovery note to hide failed cleanup.

The separate story launcher checks both ordinary process enumeration and Windows CIM `Win32_Process` at preflight, while waiting, and again before recovery/cleanup writes. On 2026-11-15, an incompletely terminated game/manager disappeared from ordinary enumeration while CIM still listed a remaining thread. Either provider listing Fallout4/ModOrganizer now blocks launch and cleanup. A failed/incomplete inventory also fails closed: the launcher reports the error and retains its ownership note, batch and temporary settings. It does not kill a process, change permissions or repair Windows services. The old shell and other launchers are unchanged.

CIM is deliberately conservative. A lingering/stale process record can delay recovery after a window disappears; close both applications and wait for Windows to finish their exit. If incomplete shutdown persists, the coordinator must restore a clean Windows session before more native tests. Do not bypass this guard by deleting the note or launching again. This protects the lifecycle; it does not diagnose or fix the earlier black-load condition. Process checks are snapshots, not a global lock against another person launching a program between checks.

If preflight fails because the installed fixture changed, repair/revert that fixture before rerunning recovery, or have the coordinator inspect and use the saved ownership note. It is deliberately not a general automatic repair tool. Existing startup commands are not overwritten.

Launching a process or queueing setup is not a gameplay pass. Existing Act1Walk setup logs and native alias checks must confirm actual setup. This launcher does not automatically complete a quest, choose dialogue, close the game, copy reports to the clipboard or send messages.

## Acceptance gates

- Actual compiler:19PSC/PEX, no errors; C# builder/readback validates one correctly owned forced-player cancellation alias on the wrapper, while the section retains29story refs/guide bindings.
- Guard fixture executes real WorldEntry/WorldEntryPlayer scripts against a counting downstream stub: explicit-only behavior, delayed readiness, duplicate requests, timeout, existing/changed quest state, wrong timer and saved-load cancellation. This is source behavior under a model, not native saved-load timing proof.
- PowerShell fixtures exercise preflight integrity and refusal, owned-batch recovery, collision/changed-file preservation and untouched controller/unrelated settings. Existing CI invokes these through tools/run_checks.sh; no workflow permission changes.
- Process fixtures cover both providers absent, ordinary live processes, ordinary enumeration empty with a CIM-only residual, duplicate PID reporting, malformed records and provider failure. They execute the actual launcher's finally block on temporary owned files: busy/unknown inventory preserves all three artifacts/settings, while clear inventory restores settings and removes only owned files. The test mocks inventory cmdlets inside this module so CI does not inspect or change host processes.
- Root native: actual one-click main-menu entry, balanced fresh baseline, exactly one setup,29refs/13actors/26casts, readable3directions and existing quest interactions; repeat launch after clean exit; actual saved-load cancellation while pending without restart/reset; validate cleanup after ordinary exit and one interrupted-start recovery. Capture source/artifact/runtime hashes and distinguish request/setup/playthrough results.
- Independent source review and cloud checks must pass before owner handoff. Existing navmesh/pursuit limitations remain; the launcher does not solve them.
