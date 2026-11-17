# GREENWATER-STORY-001: receipt

17 November 2026. Written and committed **before any source was changed**. It names what was received and read, the projection and guard plan, the planned records and aliases, the intended files and the branch. What was actually done is added at the end (section 9) when the work is finished, and in the ledger beside it.

Nothing here is a Papyrus compile, a build against the game's master, a load in Fallout 4 or a play session. No licensed input is in this checkout or was asked for.

## 1. What was received

| Input | Exact identity | How it was verified |
|---|---|---|
| Contract commit | `637cbeda836c55b7c93bb45583b1ea2914f2d46d`, tip of `feat/greenwater-story-contract` (draft PR 34) | fetched by branch name; the fetched tip is that hash |
| Its parent line | `a8f6d6482b4b5dc9d545e197ed4cf2c8f6324306` (the repaired Mercy briefing source) | an ancestor; the contract commit adds four documents and three `.gitattributes` lines and nothing else |
| `docs/design/GREENWATER_STORY_001.md` | SHA-256 `A20CFEC0F53A8FB4F84A9590D6D1BC163E331E586B4E20D80C00EAC213620203`, 121 lines | read in full; the digest is the one both reviews name |
| `docs/design/GREENWATER_STORY_001_ORDER.md` | SHA-256 `8D0175B28C7D597E7983CF270D358C65D629B728429834247CEDC73FD3A39961`, 33 lines | read in full; the digest is the one the dispatch gives |
| `GREENWATER_STORY_001_NORA_REVIEW.md`, `…_SAM_REVIEW.md` | `C45B5FD1…3CC9FF`, `B4E01820…51D0` | read in full |
| Accepted writing | tree `assets/incoming/act1/story` = `eb40d971bc2c295991064c74e986d2d123f6d0c3`, the same object as at `d142104` | unchanged; not to be changed |

**Implementation branch:** `feat/greenwater-story-001`, made from the exact contract commit. No reset, rebase, merge or force-push; no pull request opened by this work.

Where the outline and the order differ, the order is followed (its ten clarifications). Where the order gives a string and Nora's review gives another for the same place, the order's is used.

## 2. Writing read for projection

From `assets/incoming/act1/story`, unchanged:

- `quests/tlm_mq02b.json`, whole: 13 stages, 4 objectives, both choice sets, evidence, `cannot_break`, 7 flags.
- `talk/tlm_mq02b.json`, all 26 nodes. Projected: `starnes_default`, `starnes_first`, `starnes_wants`, `starnes_guns`, `starnes_bowl`, `pruitt_default`, `pruitt_skiff`, `pruitt_confess`, `hatcher_default`, `hatcher_table`, `hatcher_lost`, `hatcher_won`, `hatcher_share`, `hatcher_paid`, `pruitt_chain`, `pruitt_ran`, `pruitt_burned`, `starnes_after_won`, `starnes_won_hatcher_dead`, `starnes_denied`, `starnes_after_chute`, `starnes_after_fire`, `starnes_after_share`, `starnes_after_hanging`, `belden_greenwater_relief`, `belden_greenwater_relief_fire`.
- `documents.json`: `ration_board` (431 characters) and `letter_of_hire` (486 characters), whole.
- `characters.json`: `starnes` Opal Starnes, `hatcher` Lyle Hatcher, `pruitt` Mose Rafferty, `belden` Tomas Belden.
- `talk/tlm_mq02.json`: `pritchard_road_river` (already in the Mercy briefing), and the text only of `pritchard_hears_river_after_fair` and `pritchard_hears_river_after_fair_unknown`.

Speech is copied word for word. A spoken box is written as the first section writes one, `Name: "…"`. Two things need a split or an excerpt and both will be in the mapping:

- `hatcher_paid` is 239 characters; with its speaker it is 255, the length at which the game was seen to cut a box short. It is shown as two boxes, cut between two of its sentences, and the hire is learned only when the second has been answered.
- `hatcher_lost` when Opal is dead or not there: only the approved prefix ending `She's yours, friend, every sack.` (order, item 8).
- The two documents are longer than a box. Each is shown page by page, cut only at its own line breaks; the pages put together are the document, which a test compares. The letter is also a book in the inventory once read.

## 3. Native shape

Two quests, as the first section has two layers:

- **`TLM_MQ02B`** (script `TLM:MQ02BQuest`): the road. The accepted stages and objectives, the facts later chapters read, every guard and every commit. Its aliases are filled by script. No record of this name exists yet: `tools/PluginBuilder/formkeys.txt` (338 lines, last id 2216) has none.
- **`TLM_GW`** (script `TLM:GreenwaterWalk`; alias script `TLM:GreenwaterTalk`): the greybox. The placed pieces in aliases of its own, the lines, the boxes and the physical actions. Development only, like `TLM_A1`. The exterior builder clones it, as it clones `TLM_A1`, so that the owner's exterior has its own references and `TLM_MQ02B` stays one record in the story master.

Routing: the Mercy travel point and every Greenwater piece report to `TLM:GreenwaterWalk` through `TLM:GreenwaterTalk`. Pritchard keeps his one listener: the river report is offered from inside `TLM:Act1Walk`'s existing activation and its `talking` claim, after the side quest's report box and before the Mercy briefing. No second listener is put on him.

### Stages of `TLM_MQ02B`

The thirteen accepted stages with their accepted journal text, and one native stage: **46**, "the lie was told and heard", which carries the accepted compound text of stage 44. Stage 44 itself carries the contract's interim text `You accepted Hatcher's share. The grain remains aboard the Queen.` No stage is read as "everything below it happened".

### Facts kept, and where

Global variables of the plugin, so that later quests and conditions can read them: `TLM_G_MQ02B_Outcome` (0, 41, 42, 43, 44), `_Cargo` (0 lashed to the Queen, 1 yielded, 2 home whole, 3 home reduced, 4 destroyed), `_Recovered` (of 12 units: 12, 8 with a living pilot, 6 alone), `_Hatcher` (0 free, 1 released, 2 in custody, 3 hanged, 4 dead otherwise, 5 not accounted for after the fire), and one each for `grain_home`, `grain_sold`, `queen_burned`, `hatcher_hanged`, `hatcher_friend`, `hatcher_hunting`, `silver_river`, and `_Reported`. Script variables for what is in progress: the card result, the escape-pending lock, the pending return, payment intent, lie told and heard, each one-time grant.

### Guards, by action (the full ledger follows the implementation)

| Action | Needs, read again after every box and before any effect |
|---|---|
| Travel | `TLM_MQ01` 50, 60, 100, Done 1, delivery acknowledged; player alive. Explicit choice |
| Stage 10 | the player inside the landing's trigger, on this road |
| Stage 20 | Opal alive, there and in no fight; her problem speech delivered and its button pressed |
| Stage 30 | the player inside either boarding trigger (or first use of a deck piece: the greybox has no hull). Never locked by stage 20 or by anybody being alive |
| Stage 40, cards, share, admission | Hatcher alive, there, in no fight, free; road unresolved, no escape pending |
| Card win 41 | current Charisma at least 5, read from the game, base and current traced. Cargo becomes *yielded*, not delivered |
| Card loss 45 | otherwise. Nothing taken; another course stays open |
| Share 44 | "Done." pressed; intent written; 200 caps asked for once; the count seen to have risen by 200; then 44 with the interim text |
| Lie | 44, paid, Opal alive and there, the explicit lie action chosen; `LieTold`. Her line; then 46 and `grain_sold` |
| Chain cut | on the Queen, unresolved, nothing pending: sets the **escape-pending lock**, which excludes cards, share and fire from then on and is kept by a save |
| Pilot | escape pending (or cargo yielded by cards): the return begins; it can be begun again if interrupted |
| 42 | the player inside the return dock's trigger with an escape pending: cargo home reduced (8 of 12 with Rafferty alive, 6 without), `grain_home`; `hatcher_hunting` only if Hatcher is alive |
| Whole delivery | the same trigger with a yielded cargo: home whole, 12 of 12, `grain_home` |
| Fire 43 | unresolved, **no escape pending**, the occupancy warning delivered (Rafferty's line if he lives, labelled action text if not), then the explicit confirmation at the fire control |
| Hanging 60 | 41; Hatcher alive and free; Opal alive and there; the explicit button; Hatcher seen dead afterwards |
| Custody 61 | 41; Hatcher alive and free; Pritchard alive and there; the explicit button; Hatcher seen alive beside him afterwards |
| Release | 41; Hatcher alive and free; the explicit button; `hatcher_friend` |
| Opal's reactions | as the order's item 9, each with Opal alive, there and in no fight |
| Belden | 43 or 44; Belden alive and there; his line, then one real food item, once |
| Stage 100 | one of 42, 43, 44, or 41 with the cargo delivered; the explicit departure; the player seen to have arrived at Mercy |
| River report | 100; Pritchard alive (through `Act1Walk`); the explicit report button; `_Reported` |

No rule asks for all four of the cast to be alive.

## 4. Records planned

Ids are given by the builder's allocator from 2217 upward and will be read back, not chosen. Editor ids:

- Quests: `TLM_MQ02B`, `TLM_GW`.
- Actors, each a copy of the game's settler with no packages (as the first section's): `TLM_NPC_WARDEN_GREENWATER` (Opal Starnes), `TLM_NPC_COMMODORE_QUEEN` (Lyle Hatcher), `TLM_NPC_PILOT_GREENWATER` (Mose Rafferty), `TLM_NPC_DELEGATE_COMMONWEALTH` (Tomas Belden), `TLM_NPC_QUEEN_CREW_01`, `TLM_NPC_QUEEN_CREW_02` (both shown as "Queen's crew"; anonymous).
- Factions: `TLM_Fac_Greenwater`, `TLM_Fac_QueenCrew`.
- Book: `TLM_BOOK_LetterOfHire`.
- Activators and triggers `TLM_ACTI_GW_*` / `TLM_TRIG_GW_*`: the Mercy travel point ("Greenwater story test"), three area labels, ration board, Rafferty's skiff, exit skiff, steeple ring, two cargo configurations at the landing, lashed cargo, faro table, strongbox, anchor chain, pilot lever, boiler firebox, the burned Queen's marker; triggers for the landing, the gangway, the off side and the return dock.
- Messages `TLM_MSG_GW_*`: every projected line, the document pages, and the technical text.
- Globals `TLM_G_MQ02B_*` as above.
- From the game's master, by lookup: bottle caps (already used), the Charisma actor value, one food item found by the name a player sees. If either of the last two is not found the build says so, and the script refuses the card game or gives no meal and says that, rather than claim either.
- Placed references `TLM_REF_GW_*` in the game's test room for the development build, all switched off until used; the exterior builder gives the owner's world its own at ground it has free, south of the bypass road.

Aliases of `TLM_GW` (one for each placed piece) and of `TLM_MQ02B` (Opal, Hatcher, Rafferty, Belden, two crew, and the pieces objectives point at) will be listed with their numbers in the ledger from the build's read-back.

## 5. Candidate text that changes (order, item 1)

Product-availability text only; no speech. In this candidate's source: the Mercy briefing's hub and stage 10 (`Mercy briefing. Greenwater is playable; the other roads are not.`), its hand-off footer (`Opening complete. Ask for briefings or use Greenwater story test.`), its stage 20, the first section's own ending footer, and the completed text of `TLM:Act1Guide`. The earlier mapping and tests that pin the old strings change with them, and say why.

## 6. Files this work intends to touch

New: `scripts/Source/User/TLM/MQ02BQuest.psc`, `GreenwaterWalk.psc`, `GreenwaterTalk.psc`; `tools/PluginBuilder/SpecGreenwater.cs`; `tools/logic_model/greenwater_model.py` and its test; `tools/papyrus_sim/test_greenwater*.py`; `docs/design/GREENWATER_STORY_001_MAPPING.json` and `…_LEDGER.md`; the candidate's manifest and its check (`tools/win/greenwater-story-candidate.json`, `tools/greenwater_story_candidate.py`); a separately named packager, `tools/win/Build-Greenwater.ps1`.

Changed: `Act1Walk.psc` (opens the travel point at set-up; routes the river report), `Act1Guide.psc` and the first section's and the briefing's spec for the availability text; `Spec.cs` (registration), `SpecAct1.cs`, `SpecMercyBriefing.cs`; `formkeys.txt` (appended) and the build report; `tools/StandInMaster/Program.cs` (the two game records looked up); `tools/WorldSliceBuilder/WorldStory.cs` (the second clone and its checks) and `Program.cs` only as far as a check of that clone on a stand-in build needs; `tools/papyrus_sim/sim.py` and `tools/papyrus_natives.json` for natives the new scripts call that have no rule yet, each marked seen, documented or assumed; the Mercy briefing's mapping and tests where the availability text and the frozen manifest's meaning change; `tools/README.md`.

Not touched: `MQ01Quest.psc`, `SQ01Quest.psc`, `MercyBriefing.psc` unless a guard requires it, `Core.psc`, `WorldEntry.psc`, `tlm_model.py`, the matrix cases, `game_runs.json`, the earlier manifests, packagers, stagers and launchers, the workflow, the accepted writing and its packets.

## 7. Known in advance

- `tools/win/mercy-briefing-candidate.json` describes the a8 source. Once `Act1Walk` changes it no longer describes this checkout, and its own check must refuse it; the tests that said "this checkout is that source" will say that instead, and its damage trials will run on the a8 tree taken from Git.
- **No launcher variant will be added to `World-Story.psm1`.** That module is shared by the frozen launchers, needs pinned digests that only a licensed build can measure, and cannot be run here (no PowerShell). The candidate gets a separately named packager, which the order's item 7 allows; wiring a launcher to measured pins is left to root and said so.
- The exterior builder cannot run here (it needs the game's master). The clone step will be exercised on a stand-in build.
- A new script's runtime selection: every changed or new script is taken from a fresh compile; only scripts whose source is still the reviewed text keep a reviewed compiled file. The exact count will be declared from the final source.

## 8. Pending whatever this work finds

Root's: the build and read-back against the game's master, the compile, measured digests, staging, and native QA of each branch. None is claimed here.

## 9. What was done

To be completed when the work is finished.
