# ACT1-RUNTIME-001: receipt

16 November 2026. Written and committed **before any source was changed**. It says what was received, what was read, what was found as it stands, and which files the implementation intends to touch. What was actually done is added at the end of this file when the work is finished (section 8), and in the ledger beside it.

Nothing here is a Papyrus compile, a load in Fallout 4 or a play session. No licensed input is in this checkout or was asked for.

## 1. What was received

| Input | Exact identity | How it was verified |
|---|---|---|
| Composition commit | `2efe2dbbaba543f7976a3df86bb81a96463aaa90`, tip of `feat/mercy-briefing-runtime` (draft PR 31) | fetched by branch name; `git rev-parse` of the fetched tip equals the given hash |
| Design contract | `docs/design/ACT1_RUNTIME_001.md`, SHA-256 `35fe9ee3bbb23b5d6f785c5c4167fad59afb71a067ea2be85291376d57d03047`, 122 lines | read in full, twice |
| Details line | `b280847ef14bfd03eea102d7845675506f51c3fe` | an ancestor of the composition commit |
| Common ancestor | `14d841b0c9b7b267d2e3e562b7c3b65fbc9b3fd1` | an ancestor of the composition commit |
| Accepted writing | `d142104fdc6f72ae556f285a0166c1122893b991` | not an ancestor (the composition applied its delta without a merge, as the contract says); the tree of `assets/incoming/act1/story` is the same object in both: `eb40d971bc2c295991064c74e986d2d123f6d0c3` |
| Entry contract | `docs/design/ACT1_ENTRY_SELECTION_CONTRACT.md`, SHA-256 `924ed1c3...7148` | unchanged |

This work is on a new branch, `feat/act1-runtime-001-mercy-briefing`, made from that exact commit. No branch was reset, rebased, merged or force-pushed, and no pull request is opened by this work.

## 2. What was read

In full: the design contract; `scripts/Source/User/TLM/Act1Talk.psc`; `tools/PluginBuilder/SpecAct1.cs`; `tools/WorldSliceBuilder/WorldStory.cs`; `tools/PluginBuilder/Program.cs`; `tools/check_consistency.py`; `tools/run_checks.sh`; `.github/workflows/portable-checks.yml` (read only; not changed); `tools/win/world-details-artifact.json`; `tools/win/Build-WorldDetails.ps1`; `tools/test_world_story_launcher.py`.

In the parts that bear on this task:

- `scripts/Source/User/TLM/Act1Walk.psc`: properties, state, `Begin`, `Spoken`, `ShowLine`, `CanDecide`, `TalkPritchard`, `Debrief`, `Report`.
- `scripts/Source/User/TLM/MQ01Quest.psc`: `OnStageSet`, `ConsequencesAcknowledged`, `LegacyDeliveryAcknowledged`, `DeliveryAcknowledged`, `ResumeCaravanConsequences`, `WaitForDeliveryAcknowledgment`, `RegisterDemoPresentation`, `ApplyDelivered`, `ApplyDebriefAnswer`, `ApplyDebriefDone`, `OnGameLoaded`, `Recover`.
- `tools/PluginBuilder/Spec.cs` (record types, books, messages, the list of quests), `Builder.cs` (books, messages, `Fill` for a quest, the id allocator in `Create`), `formkeys.txt`.
- `tools/papyrus_sim/sim.py`: the session, quests and objectives, `Message.Show` and how a test answers a box, `ForceRefTo`, `AddItem`, `RemoveItem`, `GetItemCount`, `press_activate`, `invoke`; the outline of `test_act1.py`.
- `tools/win/Build-WorldNatural.ps1` and the two package-safety fixtures, for what they do when a script source changes.
- From the accepted writing, the five talk nodes and the one document the contract names (section 4).

## 3. What was found, before any change

**The composed source describes the old runtime.** `scripts/Source/User/TLM` holds 19 scripts. Each one's text, with line ends made LF, has the SHA-256 that `tools/win/world-details-artifact.json` pins under `sourceTextSha256`: 19 of 19, no mismatch. (That is source provenance. No PEX is in this checkout and none was compared.)

**The gates the contract names are as it says.** `TalkPritchard` sets 50, waits on `WaitForDeliveryAcknowledgment`, shows the debrief and the handoff and sets 60; `MQ01Quest.OnStageSet(60)` runs `ApplyDebriefDone`, which, only when `DeliveryAcknowledged()`, sets `TLM_G_MQ01_Done` to 1 and stage 100. After 60 the last branch shows `SayPritchardAfter`, or `SayPritchardAfterAndMore` whose second button is the side quest's report.

**The baseline is green here, with one step that cannot run here.** `tools/run_checks.sh` on the untouched commit stops at `tools/test_world_story_launcher.py`, which needs PowerShell; this container has none, and adding it was refused. With only that one line left out of a scratch copy of the script (the tracked script is unchanged):

| Step | Result on the untouched commit |
|---|---|
| Logic model | 94 tests, OK (8 skipped, as before) |
| Plugin build, skeleton | 5 quests, 55 messages, 43 stages, 77 aliases; self-check passed; report equals the committed one |
| Consistency, matrix generator, intake checks | passed; strict intake fits (227 lines); 74 fixture tests OK; focused check passed (33 histories) |
| Eight stand-in masters | passed; the id file came out the same with and without a master |
| The scripts in the stand-in engine | 260 tests OK; 65 of 65 scenarios, 1628 checks; the same with 60 calls a second |

**One consequence is known in advance.** `tools/win/tests/Test-WorldNaturalPackageSafety.ps1` and `Test-WorldDetailsPackageSafety.ps1` each expect the old packager, given good new output ancestry, to get as far as "Reviewed runtime input must have exactly19 PEX files". Both packagers check the frozen source first. Once `Act1Walk.psc` changes and a twentieth script exists, they will refuse earlier, with "Current source differs from reviewed logical source: Act1Walk.psc" and "Current source names differ from the reviewed19 scripts." That is the guard doing what the contract says it should; but those two fixtures run inside `tools/run_checks.sh` on GitHub, so as they stand they would turn the remote check red. See section 5.

**The exterior builder cannot run here.** `tools/WorldSliceBuilder` against a generated stand-in master stops at `Program.cs` line 44: it looks up records only the game's own master has. So the exterior clone's read-back of the new binding is one of the local gates (section 7), unless a stand-in for just the cloning step proves practical; if it does, it will be reported as a stand-in and nothing more.

## 4. The approved text this increment uses

All from `assets/incoming/act1/story` as accepted at `d142104`; none of it is changed.

| Use | Source field | Length |
|---|---|---|
| The hub's question | `talk/tlm_mq02.json` `pritchard_report_open_roads.text` | 84 |
| The hub's four labels | the same node's four button labels | |
| The rail, the river, the pike | `pritchard_road_rail.text`, `pritchard_road_river.text`, `pritchard_road_pike.text` | 173, 177, 181 |
| The pike's follow-on | `pritchard_road_pike` button `What should I ask Quill?`; `pritchard_docket_context.text` and its two labels | 203 |
| The review copy | `documents.json` `docket_2298` title and text | 629 |

The speaker prefix the first section uses (`Owen Pritchard: "..."`) adds 19 characters; the longest spoken box is then 222 characters, under the 255 at which the game was seen to cut a box short. The availability text is not fiction and is kept apart from the quoted speech.

Deliberately **not** imported: the `mq02 done 100` condition on the hub's source node, its three `then` targets, `mq02c set 16` on the Take button, every other node, and any flag.

## 5. Files this work intends to touch

New:

- `scripts/Source/User/TLM/MercyBriefing.psc` (the twentieth script).
- `tools/PluginBuilder/SpecMercyBriefing.cs`: the quest `TLM_MercyBriefing`, the book `TLM_BOOK_Docket2298`, the messages.
- `tools/logic_model/mercy_briefing_model.py` and its test: the briefing's state, apart from the MQ01 and SQ01 rules.
- `tools/papyrus_sim/test_mercy_briefing.py`: the real scripts driven through `Spoken`, the buttons by index, the inventory.
- A mapping file for the projected text and a check that every projected string equals its source field.
- A manifest and recipe for this candidate under a new name, with the 20 source digests; no compiled or built hash is put in it until somebody has measured one.
- `docs/design/ACT1_RUNTIME_001_LEDGER.md`: changed files, forms as read back, properties, provenance, test results, open mechanics.

Changed:

- `scripts/Source/User/TLM/Act1Walk.psc`: one optional property, the activated actor passed on from `Spoken`, and the hand-off after the chapter is complete. Nothing before stage 60 changes.
- `tools/PluginBuilder/Spec.cs`: registration of the new book, messages and quest.
- `tools/PluginBuilder/SpecAct1.cs`: **one line**, the new property in `TLM:Act1Walk`'s binding. The contract lists "minimal Spec registration/message/property binding"; this file is where that binding is written, so it is named here as an extra.
- `tools/PluginBuilder/formkeys.txt`: lines appended by the builder's allocator; the existing 316 lines must stay byte for byte.
- `tools/PluginBuilder/last-build.report.txt`: regenerated, as `tools/run_checks.sh` requires after a spec change.
- `tools/README.md`: rows for the new files.
- `tools/papyrus_sim/sim.py` and `tools/papyrus_natives.json`: only if a call the new script makes has no rule yet, and then marked seen, documented or assumed.
- **Extra, to be justified in the ledger:** the one expectation in each of the two package-safety fixtures named in section 3, changed to require the frozen-source refusal on this candidate. The packagers and their guards are not touched. This cannot be run here (no PowerShell) and will be marked so.

Not touched: `MQ01Quest.psc`, `SQ01Quest.psc`, `Act1Talk.psc`, `WorldEntry.psc`, `Core.psc`, the scenario defaults, `tools/logic_model/tlm_model.py`, the matrix cases, `tools/papyrus_sim/game_runs.json`, the old artifact manifests, the launchers and stagers, the workflow, the accepted writing and its four packets, `CANON.md` and every narrative file. `WorldStory.cs` only if a check of the new binding is needed and can be exercised.

## 6. Bounds

One implementation and at most one consolidated repair. No destination, fair, later quest, generic adapter for the 227 lines, new speech, exterior placement, install, game launch, owner profile or save, workflow or authorisation change. `MQ02`, `MQ02c` stage 16 and every silver flag stay unset.

## 7. Gates that stay pending whatever this work finds

Maya's, after source review: the build and read-back against the real master, including the exterior clone; the Windows compile of all 20 scripts; the candidate's measured hashes. Root's, after that: private native QA. This work will report them as pending.

## 8. What was done

To be completed when the work is finished.
