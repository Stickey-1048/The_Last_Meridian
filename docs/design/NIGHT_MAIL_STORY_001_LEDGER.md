# NIGHT-MAIL-STORY-001: change, mapping, record, allocation and provenance ledger

**Source candidate. Not compiled by the Papyrus compiler, not built against the game's master, not run in the game.** Every pass below is a stand-in pass: the real scripts, on an engine written from this project's notes, against a model; or a text check of built records against the accepted writing. It is not a compile and not a game test.

Contract `docs/design/NIGHT_MAIL_STORY_001.md` (SHA-256 `6DDE0405…41CF`) and its order `NIGHT_MAIL_STORY_001_ORDER.md` (`8386699B…8874`), published at `d0756204ef9e79d67860422b21298d3b7807f9da`. This work is on `feat/night-mail-story-001`, made from exactly that commit. The receipt is `NIGHT_MAIL_STORY_001_RECEIPT.md`.

## 1. What a player is meant to get

After the first section is over and Pritchard has taken the dispatch, an **Iron Junction story test** point stands in Mercy's yard beside Greenwater's. Using it asks once whether to go; declining does nothing. Going sets the player down in an interior cell of this plugin's own, in five labelled zones on three floors:

| Zone (floor) | What stands there |
|---|---|
| The yard (A) | the rules on the gate, Augusta Lockridge at her desk, her dispatch board, her top drawer (and the inspector's stamp in it), the way back to Mercy, the held stock once she countersigns |
| Old Contrary's footplate (A) | Billie Tupper, the departure control, the mail car |
| Sawtooth Cut (B) | the footplate at the lanterns, the regulator and the reverser, Ezekiel Dole and three opponents, the track back to the yard, the mail car (aboard, seized) |
| The siding (B) | the hymnal, the collection plate, the chalked boiler |
| The valley platform (C) | where the mail arrives, the engine (sound or damaged), the way back to Mercy and the line back to the yard |

**The job.** Lockridge's gate greeting offers it; "I'll ride your mail." takes it. Refusing, asking who chalks the hymns or who passes the trains, or leaving, loses nothing and harms nobody. With Lockridge dead or no longer dispatching the footplate is boarded unasked (stage 21); with Billie dead the player is at the regulator (stage 31).

**Four exclusive outcomes**, each carried out as a staged scene and recorded only when the pieces, the player and the people are seen as the scene needs:

- **41 run.** Billie (or the player) runs the spread rail. The mail is delivered, the engine damaged, the player set down at the platform. Dole, if alive, watched the engine go by.
- **42 Dole defeated.** Dole is killed in the unsettled encounter; the three opponents go up the hill (or are dead); the mail is still aboard. The train is then taken forward (delivered, engine sound) or back (retained, the line not shut) by the regulator, or left.
- **43 sale.** 150 caps, asked for once and counted. The mail is seized, Billie is put off to walk home unharmed, and the next time Lockridge is spoken to the scene of Billie's return and report is offered.
- **44 back-out.** The train goes back to the yard with its cargo retained; the line is shut.

**Evidence, never needed.** The collection plate (silver known), the hymnal's flyleaf (the name known; the book itself is given once), Dole's own account of either, and the drawer: the stamp may be left in use, countersigned over by Lockridge, or taken. A taken stamp is custody, not delivery: Pritchard has it only when it is seen with him, and only then does the yard's dispatch board close and `lockridge_reported` become true.

**Leaving** with nothing settled settles nothing; the road can be gone back to. With an outcome recorded and no scene pending, leaving completes the road (stage 100), and Pritchard, asked at Mercy, is offered the rail report, then the stamp, then the yard's change, in his one conversation.

Representation boundaries are stated to the player outside any character's speech: the eleven miles are not shown, no engine moves, nobody jumps, and no night passes.

## 2. Changed paths

New: `scripts/Source/User/TLM/MQ02AQuest.psc`, `NightMailWalk.psc`, `NightMailTalk.psc`; `tools/PluginBuilder/SpecNightMail.cs`; `tools/logic_model/night_mail_model.py`, `test_night_mail_model.py`; `tools/papyrus_sim/night_mail_player.py`, `test_night_mail.py`, `test_night_mail_scenes.py`, `test_night_mail_router.py`, `test_night_mail_projection.py`, `test_night_mail_source.py`, `test_night_mail_mutations.py`, `test_night_mail_world_clone.py`, `test_night_mail_candidate.py`; `tools/night_mail_story_candidate.py`; `tools/win/night-mail-story-candidate.json`, `Build-NightMail.ps1`, `tests/Test-NightMailPackageSafety.ps1`; `docs/design/NIGHT_MAIL_STORY_001_MAPPING.json`, `NIGHT_MAIL_STORY_001_LEDGER.md`.

Changed, for this road: `scripts/Source/User/TLM/Act1Walk.psc` (the rail travel point is opened with the first section; the rail report is offered in Pritchard's conversation after the river's, with the same four answers), `Act1Guide.psc` (its one availability text); `tools/PluginBuilder/Spec.cs` (the road's records join the lists; `OwnCells`), `Builder.cs` and `SelfCheck.cs` (the first cell this builder makes: see section 5), `SpecAct1.cs`, `SpecMercyBriefing.cs`, `SpecGreenwater.cs` (the availability strings only), `formkeys.txt` (283 lines appended); `tools/StandInMaster/Program.cs` (the floor tile, with bounds); `tools/check_plugin_layout.py` (an own cell is allowed only if the build says it made one, with the bytes it must have; four new kinds of damage); `tools/WorldSliceBuilder/WorldStory.cs` and `StoryCloneCheck.cs` (the third clone and seven kinds of damaged source (and a source from before the road, which must clone as it did)).

Changed, for the new availability text ("Greenwater and Iron Junction only"): `docs/design/ACT1_RUNTIME_001_MAPPING.json`, `GREENWATER_STORY_001_MAPPING.json` (the strings only, and why); `test_act1.py`, `test_guide.py`, `test_mercy_briefing.py`, `test_mercy_briefing_projection.py`, `test_greenwater.py`, `test_greenwater_projection.py`, `test_greenwater_world_clone.py`, `test_mercy_briefing_candidate.py`.

Changed so that the earlier candidates stay frozen and honest: `tools/papyrus_sim/test_greenwater_candidate.py` (now tests the Greenwater manifest as a frozen manifest of the 016b source: it refuses this checkout and passes and notices every damage on the 016b tree taken out of Git), `tools/win/tests/Test-GreenwaterPackageSafety.ps1` (its expectation of this checkout is now the frozen packager's refusal; unrun). `tools/win/greenwater-story-candidate.json`, `tools/greenwater_story_candidate.py`, `tools/win/Build-Greenwater.ps1`, every earlier packager, manifest, pin and workflow, and every accepted 016b artifact are **byte-unchanged** (compared with `git diff --quiet 016b2b4`).

Not touched: the main quest, the side quest, the Mercy briefing's rules, Greenwater's scripts, `.github`, any workflow, any launcher.

## 3. Incorporated from root: `381d631c2ba8bfe5cf5d9f55b36e721137aa69f3`

Root's single-file CI repair changes only `tools/papyrus_sim/test_greenwater_candidate.py`: its guard that the frozen `.gitattributes` rules are preserved and only the exact Night Mail docs rule may follow, with six negative cases (an altered frozen rule, a removed one, a broad override, a broadened approved rule, the approved rule prepended instead of appended, the approved rule twice). It was cherry-picked whole, cleanly, as `6dc299b`. The file at that commit is byte-identical to the one at `381d631`: SHA-256 `828ED796B7EA796D48100AA5D009C3BB5C565E88FC52D7309FF4DD4748D06CCC` with LF line ends; the digest quoted in the work order, `0D1AC65DD4A9448574B8E6AE0DD29435772F55AFB5F76B924321B58EBC7EAE9C`, is the same file with CRLF line ends (checked here by turning the LF file into CRLF). Nothing else of that commit exists to take.

Adapted only as the honest 016b snapshot required, and nothing dropped: `preserves_frozen_attributes` and the test of its six negative cases are as root wrote them; the exact-append comparison of `.gitattributes` with the contract commit's is kept; the file now carries the frozen-016b tests described in section 2. This checkout's own `.gitattributes` is the contract commit's, with no further change (`test_night_mail_candidate.py` compares them).

## 4. Mapping and guards

The text mapping is `NIGHT_MAIL_STORY_001_MAPPING.json`: for each of the 29 spoken boxes the node, the whole-or-excerpt rule, the buttons, who has to be alive, present and in no fight, and what follows an answer; for each of the 88 boxes this build speaks for itself its exact text and when it is shown; the three documents; the 24 stages and 7 objectives with what sets them; the 9 accepted flags with where each is written; the 9 facts; and what is deliberately not imported (the reward notice, stage 62's accepted log, Dole's coat as a second place for the silver, the conditions of the two Pritchard lines). `test_night_mail_projection.py` compares it with the plugin as built and with the accepted writing, character by character (15 tests).

Speech is imported whole except for exactly three excerpts: Lockridge's gate greeting in two boxes (it is 243 characters with her name, over the 240 this project holds every displayed string to; it is cut between two sentences and nothing is left out), Dole's offer without its promise about Billie when she is dead or gone (the rest of his line, from "The physic goes up the hill:"), and the two Pritchard lines (their text only; their condition, "after the fair", is not imported and no fair is implied). The build's own text is in square brackets and never in a character's mouth.

Guards, in the order's words:

- **Requested transit is not arrival.** Travel, departure, the run, the reverse, the delivery, the return to the yard and the leaving each ask for a move, then look: the player in the marker's cell within 512 units of it, for up to ten seconds. Nothing is recorded on a move that was asked for.
- **Killing Dole is not delivering medicine.** Outcome 42 leaves the mail aboard and `mail_through` 0; the mail goes through only by the regulator, seen at the platform.
- **A taken stamp is not delivered proof.** Stage 63/64 is custody. The stamp is delivered only when it is seen with Pritchard; the yard's board closes and `lockridge_reported` is written only then and only after the board was seen closed and its notice answered.
- **Oral identity is not holding or reading a book.** Dole naming himself is stage 56 and `ostrander_known`; the hymnal is shown to Lockridge only with the book itself in the inventory.
- **A cancelled menu is not a later fallback.** Every box is read by its button; a box that comes back with no button a person can press begins nothing, records nothing and closes the conversation it was in.
- **A dead or hostile participant cannot speak, countersign or receive an item.** Each line, and each effect of an answered box, is shown or done only if its speaker is alive, enabled and in no fight when asked and again after the box.
- **Refusal never harms.** The only fights are the ones the player chooses ("Stand aside", "No.", an attack), and the opponents already fighting are not set on the player again.
- **Pending scenes are exclusive, persisted and recoverable.** Section 6.

## 5. The cell, the builder, and what the stand-in showed

The builder made no cell before this work; it only overrode one of the game's. `Builder.PlaceReferences` now allocates an own cell's id before its references, makes it (`MakeOwnCell`: interior flag, lighting, filed under its block and sub-block by its id, with a note in the report), and places into it by the cell's own coordinates. Nothing is placed by hand: `Spec.Placed` lists every reference, floor tiles included. `SelfCheck` and `check_plugin_layout.py` read it back: an own cell is allowed only if the build says it made one, must have an editor id, a two-byte flag subrecord with the interior bit, and a lighting subrecord; the layout check notices 39 kinds of deliberate damage, four of them new.

Floors. The tile is the game's `workshop_ShackMidFloor01B`, the tile the exterior builder stands a cabin on, laid with its surface at Z 0 and **assumed 256 units square** (the stand-in master gives it those bounds; the game's was not read). Between the floors there is nothing; a trigger box 700 units below them catches a fall and sets the player back at the arrival marker of the zone a scene last put them in.

| Floor | Tiles | Tile centres, x | Tile centres, y | Surface z | Extent (256-unit tiles, assumed square) |
|---|---|---|---|---|---|
| A: the yard and the yard footplate | 5 x 3 = 15 | 0 to 1024 | 0 to 512 | 0 | x -128 to 1152, y -128 to 640 |
| B: the Cut, its retreat path and the siding | 7 x 3 = 21 | 3072 to 4608 | 0 to 512 | 0 | x 2944 to 4736, y -128 to 640 |
| C: the platform | 3 x 3 = 9 | 6144 to 6656 | 0 to 512 | 0 | x 6016 to 6784, y -128 to 640 |

### The pieces, as the plugin writes them

| Id | Alias of `TLM_NM` | Reference in `TLM_CELL_NightMail` | What it is | x | y | z | Disabled at start | Hears (`Who`) |
|---|---|---|---|---|---|---|---|---|
| 0 | `MercyTravel` | `TLM_REF_NM_MercyTravel` | at Mercy: forced 000A08:TheLastMeridian.esp | | | | yes | 1 |
| 1 | `MercyReturn` | `TLM_REF_NM_MercyReturn` | at Mercy: forced 000A09:TheLastMeridian.esp | | | | yes | - |
| 2 | `YardArrival` | `TLM_REF_NM_YardArrival` | PlacedObject | 256 | 160 | 16 | yes | - |
| 3 | `Rules` | `TLM_REF_NM_Rules` | PlacedObject | 400 | 60 | 12 | yes | 3 |
| 4 | `LabelYard` | `TLM_REF_NM_LabelYard` | PlacedObject | 120 | 60 | 12 | yes | 4 |
| 5 | `Exit` | `TLM_REF_NM_Exit` | PlacedObject | 20 | 300 | 12 | yes | 9 |
| 6 | `Lockridge` | `TLM_REF_NM_Lockridge` | PlacedNpc | 256 | 420 | 16 | yes | 5 |
| 7 | `Drawer` | `TLM_REF_NM_Drawer` | PlacedObject | 120 | 500 | 12 | yes | 6 |
| 8 | `StampInDrawer` | `TLM_REF_NM_StampInDrawer` | PlacedObject | 60 | 500 | 12 | yes | 6 |
| 9 | `BoardStamped` | `TLM_REF_NM_BoardStamped` | PlacedObject | 400 | 520 | 12 | yes | 7 |
| 10 | `BoardSigned` | `TLM_REF_NM_BoardSigned` | PlacedObject | 400 | 520 | 12 | yes | 7 |
| 11 | `BoardClosed` | `TLM_REF_NM_BoardClosed` | PlacedObject | 400 | 520 | 12 | yes | 7 |
| 12 | `HeldStock` | `TLM_REF_NM_HeldStock` | PlacedObject | 560 | 520 | 12 | yes | 8 |
| 13 | `CargoRetained` | `TLM_REF_NM_CargoRetained` | PlacedObject | 600 | 300 | 12 | yes | 10 |
| 14 | `BillieYard` | `TLM_REF_NM_BillieYard` | PlacedObject | 400 | 300 | 16 | yes | - |
| 15 | `BillieFootplate` | `TLM_REF_NM_BillieFootplate` | PlacedObject | 1040 | 400 | 16 | yes | - |
| 16 | `LabelFootplate` | `TLM_REF_NM_LabelFootplate` | PlacedObject | 760 | 60 | 12 | yes | 11 |
| 17 | `YardFootplate` | `TLM_REF_NM_YardFootplate` | PlacedObject | 880 | 256 | 16 | yes | - |
| 18 | `Billie` | `TLM_REF_NM_Billie` | PlacedNpc | 1040 | 400 | 16 | yes | 12 |
| 19 | `Depart` | `TLM_REF_NM_Depart` | PlacedObject | 1040 | 120 | 12 | yes | 13 |
| 20 | `CargoAboard` | `TLM_REF_NM_CargoAboard` | PlacedObject | 760 | 480 | 12 | yes | 10 |
| 21 | `CutArrival` | `TLM_REF_NM_CutArrival` | PlacedObject | 3200 | 256 | 16 | yes | - |
| 22 | `LabelCut` | `TLM_REF_NM_LabelCut` | PlacedObject | 3060 | 60 | 12 | yes | 14 |
| 23 | `BillieCut` | `TLM_REF_NM_BillieCut` | PlacedObject | 3340 | 400 | 16 | yes | - |
| 24 | `Regulator` | `TLM_REF_NM_Regulator` | PlacedObject | 3340 | 120 | 12 | yes | 15 |
| 25 | `Reverser` | `TLM_REF_NM_Reverser` | PlacedObject | 3200 | 120 | 12 | yes | 16 |
| 26 | `CargoAtCut` | `TLM_REF_NM_CargoAtCut` | PlacedObject | 3060 | 400 | 12 | yes | 10 |
| 27 | `BackFromCut` | `TLM_REF_NM_BackFromCut` | PlacedObject | 2990 | 256 | 12 | yes | 22 |
| 28 | `BillieWalk` | `TLM_REF_NM_BillieWalk` | PlacedObject | 3000 | 540 | 16 | yes | - |
| 29 | `Lanterns` | `TLM_REF_NM_Lanterns` | PlacedObject | 3560 | 256 | 12 | yes | 17 |
| 30 | `Dole` | `TLM_REF_NM_Dole` | PlacedNpc | 3800 | 256 | 16 | yes | 18 |
| 31 | `Rifle1` | `TLM_REF_NM_Rifle1` | PlacedNpc | 3940 | 120 | 16 | yes | 19 |
| 32 | `Rifle2` | `TLM_REF_NM_Rifle2` | PlacedNpc | 3940 | 400 | 16 | yes | 20 |
| 33 | `Rifle3` | `TLM_REF_NM_Rifle3` | PlacedNpc | 3980 | 256 | 16 | yes | 21 |
| 34 | `CargoSeized` | `TLM_REF_NM_CargoSeized` | PlacedObject | 3700 | 500 | 12 | yes | 10 |
| 35 | `Retreat1` | `TLM_REF_NM_Retreat1` | PlacedObject | 4640 | 40 | 16 | yes | - |
| 36 | `Retreat2` | `TLM_REF_NM_Retreat2` | PlacedObject | 4640 | 256 | 16 | yes | - |
| 37 | `Retreat3` | `TLM_REF_NM_Retreat3` | PlacedObject | 4640 | 480 | 16 | yes | - |
| 38 | `LabelSiding` | `TLM_REF_NM_LabelSiding` | PlacedObject | 4160 | 60 | 12 | yes | 23 |
| 39 | `Hymnal` | `TLM_REF_NM_Hymnal` | PlacedObject | 4200 | 520 | 12 | yes | 24 |
| 40 | `Plate` | `TLM_REF_NM_Plate` | PlacedObject | 4340 | 520 | 12 | yes | 25 |
| 41 | `Chalk` | `TLM_REF_NM_Chalk` | PlacedObject | 4400 | 120 | 12 | yes | 26 |
| 42 | `PlatformArrival` | `TLM_REF_NM_PlatformArrival` | PlacedObject | 6272 | 256 | 16 | yes | - |
| 43 | `LabelPlatform` | `TLM_REF_NM_LabelPlatform` | PlacedObject | 6130 | 60 | 12 | yes | 27 |
| 44 | `BilliePlatform` | `TLM_REF_NM_BilliePlatform` | PlacedObject | 6420 | 400 | 16 | yes | - |
| 45 | `CargoDelivered` | `TLM_REF_NM_CargoDelivered` | PlacedObject | 6560 | 500 | 12 | yes | 10 |
| 46 | `EngineSound` | `TLM_REF_NM_EngineSound` | PlacedObject | 6420 | 120 | 12 | yes | 28 |
| 47 | `EngineDamaged` | `TLM_REF_NM_EngineDamaged` | PlacedObject | 6420 | 120 | 12 | yes | 28 |
| 48 | `PlatformExit` | `TLM_REF_NM_PlatformExit` | PlacedObject | 6700 | 300 | 12 | yes | 9 |
| 49 | `BackFromPlatform` | `TLM_REF_NM_BackFromPlatform` | PlacedObject | 6130 | 480 | 12 | yes | 22 |
| 50 | `Fall` | `TLM_REF_NM_Fall` | PlacedObject (box) | 3328 | 256 | -700 | yes | 31 |

The two Mercy pieces are placed in the game's test room for the development build (travel `560, -60`, return `520, -100`, from its arrival point, beside Greenwater's) and in the owner's exterior by the exterior builder (travel `2950, 2640, 12`, return `2780, 2650, 0`; 128 units or more from everything else at Mercy, Greenwater's two included; clear of the cabin's floor tiles, which start at y 2672).

## 6. Scenes: begun, carried out, looked at, recorded

The rules script keeps a claim (`Claim`), one pending scene (`ScenePending`) and one pending yard scene (`YardPending`), as script variables the game saves. A scene is **begun** (an intent, after the player's confirmation and a fresh look at the road), **carried out** by the greybox (the moves and the switched pieces), **looked at** (the greybox waits up to two seconds for a piece to be seen on or off, and up to ten for the player to be seen at a marker), and only then **recorded** by the rules script, which is handed the references and looks itself. If it is not seen, nothing is recorded, the scene stays begun, the pieces are put back as the recorded facts stand, and the next control of the train (or, for the yard, of the drawer, the board or Pritchard) tries it again.

| Scene | Begun by | Looked at before it is recorded | Recorded as |
|---|---|---|---|
| Travel | the Mercy travel point | the player seen at the yard gate | stage 10 |
| Departure | `BeginDepart` | the player at the Cut's footplate marker and the lanterns on | train in the Cut, stage 40 |
| Run | `BeginRun` | the player at the platform, delivered cargo on, aboard cargo off, damaged engine on | outcome 41, 41/46 |
| Reverse | `BeginReverse` | the player at the yard footplate, retained cargo on, aboard off | outcome 44, 44/49 |
| Sale | `TakeShare` (the 150 caps counted in) | seized cargo on, aboard off, Billie (if she lives) at her walking marker in no fight | outcome 43, 43/48 |
| Defeat | Dole's death in the unsettled encounter | Dole dead; each opponent dead or in no fight at a retreat marker | outcome 42, 42/47 |
| Forward / carry back | `BeginForward`, `BeginCarryBack` | as the run, with the sound engine / as the reverse | mail delivered / retained |
| Billie's return and report | Lockridge, after a sale | Billie seen at the yard marker in no fight | `BillieReported` |
| Countersigning | `BeginCountersign` | signed board on, stamped board off, held stock on, Lockridge alive and there | stage 62 |
| The stamp taken | `TakeStamp` (asked for once) | the stamp in the inventory and the drawer's piece off | 63 / 64 |
| The stamp handed over | `HandOver` | the stamp gone from the player and with Pritchard | `stamp_delivered` |
| The yard's change | `BeginAuthority` | closed board on, both others off, and its notice answered | yard authority, `lockridge_reported` |
| Leaving | the exit | the player seen at the Mercy marker | stage 100 |

Billie is placed by the recorded facts, never ahead of them (`PlaceBillie`): on the footplate where the train is recorded to stand, at her walking marker after a sale until her return was shown, at the yard after it.

**Recovery without a rollback.** The way back along the line and the road to Mercy are never shut by a pending scene, so nobody is kept in the Cut by a scene that cannot be shown. A countersigning confirmed and never seen, with Lockridge no longer there to do it, is dropped (nothing was signed) and the drawer is open to whoever is left. A stamp asked for once and not seen to arrive is not asked for again; her other two answers stay open. Caps asked for once and not seen fail closed: the deal is off and the share is never offered or asked for again. A handover not seen is looked at again at Pritchard's next conversation. Nothing that was recorded is taken back.

## 7. Aliases

`TLM_MQ02A` (script-filled, all `Optional`): `0 Lockridge`, `1 Billie`, `2 Dole`, `3 Rifle1`, `4 Rifle2`, `5 Rifle3`, `6 Depart`, `7 Regulator`, `8 Exit`. They are filled by `TLM:NightMailWalk` at the first travel from the 51 aliases of `TLM_NM` (the `CastFrom` and `CastInto` lists, which the exterior clone remaps and the road's stay in the story master).

`TLM_NM` (51 aliases, ids 0 to 50, all `Optional` and `AllowDisabled`; 38 carry `TLM:NightMailTalk` with their `Who` number; the people are `Protected`): the table in section 5. The exterior clone `TLM_WS_NM` gives only `MercyTravel` and `MercyReturn` references of their own; the other 49 keep the story master's.

## 8. Allocation

`tools/PluginBuilder/formkeys.txt`: lines 1 to 670 are 016b's, byte for byte (compared with `git show 016b2b4:…`). 283 names follow, numbered 2383 to 2665 without a gap and without reuse of an earlier number.

| Kind | Count | Numbers |
|---|---|---|
| globals (`TLM_G_MQ02A_*`) | 18 | 2383 to 2400 |
| factions | 2 | 2401, 2402 |
| stamp (misc item) | 1 | 2403 |
| activators | 31 | 2404 to 2434 |
| trigger | 1 | 2435 |
| actors | 6 | 2436 to 2441 |
| book | 1 | 2442 |
| quests (`TLM_MQ02A`, `TLM_NM`) | 2 | 2443, 2444 |
| the cell (`TLM_CELL_NightMail`) | 1 | 2570 |
| placed references (51 pieces, 45 floor tiles) | 96 | between 2568 and 2665 |
| messages | 124 | between 2445 and 2664 |
| **total** | **283** | |

(The two last-numbered records are `TLM_MSG_NM_AskWalkToCut`, 2664, and `TLM_REF_NM_BillieFootplate`, 2665: added after the first allocation, so that nothing before them was renumbered.) The exact names and numbers are in the manifest under `idFile.appended`.

## 9. Pritchard's conversation and Lockridge's greetings

Pritchard keeps his one listener. After the first section, `TLM:Act1Walk` offers, in this order and inside its own claim on him: the river report (Greenwater's), then the rail report (this road's: the report, the stamp, the yard's change), then the Mercy briefing. Each of the first two returns one of four answers (none, given, later, closed); the same four in both scripts, and a test compares them. "Given" or "closed" ends that conversation; "later" goes on to the next; the side quest's own report keeps its own button in the first section's boxes.

Lockridge's three gate greetings read the side quest as it recorded itself and write nothing of it: `lockridge_gate_alerted` when `TLM_G_SQ01_YardAlerted` is 1 (only the side quest's report to Pritchard sets it), `lockridge_gate_sold` when `TLM_G_SQ01_Outcome` is 5 (Vane's purchase; a ledger merely not carried is not that), otherwise the plain greeting. A notice posted in public (outcome 3) is not the yard alerted. The tests play the side quest to each ending through its real boxes, not by setting its facts.

## 10. Provenance of the composed candidate

`tools/win/night-mail-story-candidate.json`, checked by `python3 tools/night_mail_story_candidate.py verify`: 26 script sources by digest; the builder's sources; the id file (670 earlier lines, 283 new); the three documents; the four earlier package manifests byte for byte; the a8 and Greenwater manifests, checks and packagers, and the earlier packagers and launcher, as text. Against the Details pins: 17 unchanged, 2 changed (`Act1Walk`, `Act1Guide`), 7 added. Against the Greenwater candidate (016b): 21 unchanged (the Greenwater road's own scripts word for word), 2 changed, 3 added (`MQ02AQuest`, `NightMailWalk`, `NightMailTalk`).

**Compiled scripts.** 17 are the reviewed compiled files of the Details runtime, taken by name and digest only after their source text matches that runtime's pins. **9 are compiled afresh** and are the only ones that can go into the bundle for a changed or added script: `Act1Guide`, `Act1Walk`, `MQ02AQuest`, `NightMailWalk`, `NightMailTalk`, and four whose source is unchanged since 016b but of which no compiled digest is recorded anywhere in the repository: `GreenwaterTalk`, `GreenwaterWalk`, `MQ02BQuest`, `MercyBriefing`. No pin of the Greenwater candidate is used for any of them, none of its 17 digests is taken from its manifest rather than the Details runtime's, and the verifier requires the two sets of 17 to be the same. A full fresh compile of all 26 is the compile proof. Every measured field in the manifest is null.

`tools/win/Build-NightMail.ps1` is its opt-in packager (untested scaffolding: no PowerShell here), and it runs the full source verifier, failing closed, before it creates or builds anything. Its refusal fixture's eight changes are carried out in Python in `test_night_mail_candidate.py`. The Greenwater packager and its manifest are unchanged and now refuse this checkout; `test_greenwater_candidate.py` shows that, and that they still pass and still notice damage on the 016b tree.

## 11. What was run here, and what came out

@@CHECKS@@

## 12. Source against native: what is not known

1. **Whether any of it compiles.** Nothing of this road has met the Papyrus compiler: three new scripts (about 3,500 lines) and a changed `Act1Walk`. The stand-in engine parses the subset this project uses and caught several errors of mine (an undeclared constant, a local named like a function), but it is not the compiler. `tools/check_consistency.py` is clean (documentation-level).
2. **Natives written from memory or the wiki**, marked in `tools/papyrus_natives.json`: `StopCombat`, `IsDisabled`, `RemoveItem` to another container, `GetDistance`, `GetParentCell`, `IsInCombat` as used here. Whether `MoveTo` into another interior cell puts the player there before the next look (the scripts look for up to ten seconds), and whether enabling or disabling a reference of a cell that is not loaded takes effect (the authority scene, run from Mercy, switches boards in the cell), are **pending until observed**.
3. **The cell.** The first one this builder makes: its interior flag, lighting values, filing and load are read back by the builder's own check and by byte-level layout checks against the stand-in master. Whether the game loads it, lights it and lets the player stand on the floor is not known. **No navmesh**: nobody paths; combat is standing and shooting, and nobody walks home (Billie is moved).
4. **The floor.** The tile's bounds are assumed 256 square; `workshop_ShackMidFloor01B` was not read from the game. Spots are 16 units above the floor (people and arrival markers) or 12 (pieces). "A spot is open floor only once somebody has stood on it": nobody has. The exact coordinates are in section 5.
5. **The three people and the three opponents** are copies of the game's settler with no packages (as the first section's and Greenwater's), made by the builder on the PC from that PC's master; development only. Whether they appear within the seconds the scripts allow (the first section's took 1 to 30) is not known for this cell.
6. **The opponents' difficulty and whether they fight.** `StartCombat` from a script on the player's choice, for whoever of Dole and the three lives and is not already fighting. Whether they actually fight, and nobody else does, and whether a killing in front of the others is taken as a crime, is pending until observed. Their strength is unmeasured: they are plain settlers.
7. **Quest tracking.** Objectives are flagged displayed. Nothing sets or has checked tracking.
8. **Persistence.** Every pending scene, the claim, the share and the one-time requests are script variables, which the game saves. Tried here only as "the load event changes nothing" and as a pending scene finished after a simulated load. What a save made during one of the waits (up to ten seconds) does is **not tried and not known**.
9. **The exterior builder against the real master.** Only its cloning step ran, on a stand-in; the two Mercy sites are read back and compared with the spec, and measured against what the expansion and the cabin place, from the sources. Nothing was seen.
10. **The writing.** The three excerpts are the only places the accepted text is shortened, and each is listed in the mapping.

## 13. Unresolved mechanics

- No engine moves, no rail is crossed, nobody jumps: the run, the reverse and the delivery are notices and switched pieces.
- No night passes. The next morning, in Lockridge's account, is a notice that says so.
- Thirty rifles are three; they are anonymous. Dole's congregation does not sing.
- The engine's damage is a switched piece; nothing of it is repaired or priced.
- `dole_lives`, `silver_rail`, `ostrander_known` and the yard's authority are stored; no later chapter reads them yet.
- A pending scene whose piece is missing for good cannot be finished by that scene or by another course, and the text says to report it; there is no way back from a scene except the way home, which is never shut.
- The "taken" and the "delivered" stamp are two facts; a stamp dropped and picked up again is the same one decision, and what is held, not what was once taken, is what Pritchard is offered.
- The report's lines for the outcome "Dole defeated" with the mail left aboard describe the mail where it is; no follow-up scene exists for a train left in the Cut.
- No launcher; the packager and its fixture are unrun.

## 14. Next operator actions (root's)

1. Independent source review of the three scripts, the spec and the builder's own-cell support.
2. `python tools/night_mail_story_candidate.py verify` on the review checkout.
3. Compile all 26 scripts; keep the log.
4. Run `tools\win\tests\Test-NightMailPackageSafety.ps1 -Python <interpreter>` and `Test-GreenwaterPackageSafety.ps1` in Windows PowerShell 5.1 and PowerShell 7; neither has been run.
5. Build with `tools\win\Build-NightMail.ps1 -Python <interpreter>` (read it first), or by the manifest's recipe by hand; read both build outputs, in particular the report's lines for the floor tile's bounds and the cell's lighting.
6. `python tools/night_mail_story_candidate.py measure <bundle> --fresh-compile <folder>`; record the digests.
7. Before staging: stand in the cell. Does it load, light, hold a player on each floor, and set the player back from the fall box?
8. Stage into a disposable profile; play the four outcomes, a refusal, each dead-cast case, the stamp's three decisions and the handover, the sale's morning, evidence either side of an outcome, leaving and coming back, both roads in either order, and the opponents.

## 15. Rollback

The implementation is on `feat/night-mail-story-001`, above the contract commit `d075620`, above `016b2b4`. Dropping the branch restores the Greenwater candidate exactly: its manifest, check, packager and 016b artifacts were not edited, and the one earlier fixture this work changed (`Test-GreenwaterPackageSafety.ps1`) is restored by checking out `016b2b4`. No installed file, profile, save, workflow, worker, provider or auth setting was touched.
