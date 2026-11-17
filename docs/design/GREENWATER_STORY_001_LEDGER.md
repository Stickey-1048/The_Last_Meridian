# GREENWATER-STORY-001: change, mapping, record, allocation and provenance ledger

17 November 2026. What was built for the one playable road, *The Queen of Tellico* (`TLM_MQ02B`), on `feat/greenwater-story-001`, from the exact contract commit `637cbeda836c55b7c93bb45583b1ea2914f2d46d`. The receipt written before any change is `GREENWATER_STORY_001_RECEIPT.md` (commit `f475c9b`).

**Repaired after independent review of `7e05c6b`.** Nine findings and two more found on the way: section 13, and `GREENWATER_STORY_001_REPAIR_RECEIPT.md` (commit `07d4ae0`, before any change). The figures in sections 1 to 12 are the repaired source's.

**What this is and is not.** It is source: three new Papyrus scripts, two changed ones, a plugin spec the builder turns into records, an exterior-clone step, a model, and tests that play the real scripts on a stand-in for the game. Everything below that says "passes" passed here, on Linux, with Python 3 and the .NET 8 SDK. **None of it is a Papyrus compile, a build against the game's master, a load in Fallout 4 or a play session.** No licensed file was used, asked for or uploaded. Nobody has seen any of this in the game.

## 1. What a player is meant to get

After the first section is over and Pritchard has taken the dispatch, a **Greenwater story test** point stands in Mercy's yard. Using it asks once whether to go; declining does nothing.

Going sets the player down in three connected greybox zones, each with a label a player can read:

| Zone | What stands there |
|---|---|
| The landing | Opal Starnes, the ration board, the steeple's mooring ring, the skiff back to Mercy, the return dock; later the cargo (whole or reduced) and Tomas Belden |
| The Queen of Tellico | the gangway, the faro table, Lyle Hatcher, his strongbox, two of his crew, the boiler firebox |
| The barge and the Chute | Mose Rafferty and his skiff (at the landing end), the off side, the lashed cargo, the anchor chain, the pilot lever, the head of the Chute |

The road is then played by using those things. Four courses, each exclusive once it is taken:

- **41 cards.** Sit down, play. Current Charisma 5 or more wins; less loses, takes nothing and leaves every other course open. A win yields the cargo and nothing more: the barge has still to be brought home with the pilot lever, and only then is the grain home. Hatcher's fate is a separate, explicit choice: Opal (hanging, stage 60), Pritchard (custody, stage 61), or let him keep his boat.
- **42 cut and run.** Board by the off side or the gangway, cut the chain (which locks out cards, share and fire from that moment), take the pilot lever, walk the Chute to the return dock. Stage 42 is set at the dock, not at the lever. With a living Rafferty piloting more is recovered than without.
- **43 fire.** Use the firebox. Rafferty warns once if he can; the order is then given, staged, seen, and only then recorded.
- **44 the share.** Hatcher pays 200 caps, once. The interim status says the grain remains aboard. Telling Opal the barge was lost is a separate explicit choice, made to her alive: `grain_sold` is set when that lie is told. Her mistaken thanks, the journal's account of them (stage 46) and her cup follow only her actual answer.

Evidence: the ration board is read page by page and sets nothing. The letter of hire is read page by page from the strongbox (and kept as a book); Hatcher's admission is the other way to learn who hired him. Either sets stage 50.

Leaving by the skiff with nothing settled settles nothing; the road can be gone back to. With a course carried through, leaving completes the road (stage 100) and Pritchard, asked at Mercy, is offered the river report once, known or unknown hire.

Representation boundaries are stated to the player outside any character's speech: the Chute is a walk between two markers after a notice; the fire is a burned marker switched on and the deck's pieces switched off; a hanging is Hatcher moved to the steeple and killed; custody is Hatcher moved to Pritchard and restrained. Where one of those cannot be seen to have happened, the script records nothing and says so.

## 2. Changed paths

New:

| Path | What |
|---|---|
| `scripts/Source/User/TLM/MQ02BQuest.psc` | The road's rules (898 lines). Shows no box. Every setter of a stage, global or fact is here |
| `scripts/Source/User/TLM/GreenwaterWalk.psc` | The greybox: boxes, pieces, travel (1220 lines) |
| `scripts/Source/User/TLM/GreenwaterTalk.psc` | On each placed alias: passes use, entry, death and attack to the walk (49 lines) |
| `tools/PluginBuilder/SpecGreenwater.cs` | The records: two quests, 12 globals, 2 factions, 6 actors, 1 book, 21 base objects, 31 placed references, 91 messages |
| `tools/WorldSliceBuilder/StoryCloneCheck.cs` | Runs the exterior builder's story-cloning step alone on a stand-in build, with damage trials |
| `tools/logic_model/greenwater_model.py`, `test_greenwater_model.py` | The road as a state model, and its 27 tests |
| `tools/papyrus_sim/greenwater_player.py` | Plays the real scripts and compares every step with the model |
| `tools/papyrus_sim/test_greenwater.py` | 94 tests, 20 of them mutation trials |
| `tools/papyrus_sim/test_greenwater_repair.py` | 63 tests for the repair: 41 probes of the findings and 22 trials that take each repair out again |
| `tools/papyrus_sim/test_greenwater_projection.py` | 14 tests: every displayed string against the accepted writing |
| `tools/papyrus_sim/test_greenwater_world_clone.py` | 13 tests: the clone step, its refusals, the sites |
| `tools/papyrus_sim/test_greenwater_candidate.py` | 33 tests: the manifest, its check, the packager's and the two fixtures' text |
| `tools/win/tests/Test-GreenwaterPackageSafety.ps1` | The packager's refusal fixture. **Never run, never parsed** |
| `docs/design/GREENWATER_STORY_001_REPAIR_RECEIPT.md` | The repair's receipt |
| `tools/greenwater_story_candidate.py`, `tools/win/greenwater-story-candidate.json` | The candidate's own manifest of source and its check |
| `tools/win/Build-Greenwater.ps1` | The candidate's own packager. **Untested scaffolding: never run, never parsed** |
| `docs/design/GREENWATER_STORY_001_MAPPING.json` | Text and guard mapping, generated and checked |
| `docs/design/GREENWATER_STORY_001_LEDGER.md` | This file |

Changed:

| Path | What changed |
|---|---|
| `scripts/Source/User/TLM/Act1Walk.psc` | A `TLM_Greenwater` property; the greybox is set up when the first section begins; after the chapter Pritchard offers the river report before the briefing. +54 −3 lines. Scenario 12 meets none of it |
| `scripts/Source/User/TLM/Act1Guide.psc` | One string: the completed guide's availability text |
| `tools/PluginBuilder/Spec.cs` | Concatenates the Greenwater records; eight quests |
| `tools/PluginBuilder/SpecAct1.cs` | The ending footer; the `TLM_Greenwater` binding |
| `tools/PluginBuilder/SpecMercyBriefing.cs` | Three availability strings |
| `tools/PluginBuilder/Builder.cs` | `Ingestible` added to the kinds found by a player-visible name |
| `tools/PluginBuilder/formkeys.txt` | 162 ids appended; the first 338 lines are a8's, byte for byte |
| `tools/PluginBuilder/last-build.report.txt` | The skeleton build's report; of the earlier lines only counts and the changed strings differ |
| `tools/StandInMaster/Program.cs` | A Charisma actor value and a "Corn" ingestible in the default stand-in |
| `tools/WorldSliceBuilder/WorldStory.cs`, `Program.cs` | Clones `TLM_GW` into the exterior; `--story-clone-check` |
| `tools/papyrus_natives.json` | `GetValue`, `GetBaseValue`, `OnTriggerEnter`, **marked unverified** |
| `tools/papyrus_sim/sim.py` | The player's actor values (4.0 unless a test says otherwise) |
| `tools/papyrus_sim/test_act1.py`, `test_guide.py`, `test_mercy_briefing.py`, `test_mercy_briefing_projection.py` | Expect the candidate's availability text and eight quests |
| `tools/papyrus_sim/test_mercy_briefing_candidate.py` | The a8 manifest is now a frozen earlier one: tests that its check refuses this checkout and still passes, and still catches damage, on the a8 tree taken from Git |
| `docs/design/ACT1_RUNTIME_001_MAPPING.json` | The three changed strings, with the earlier wording recorded |
| `tools/win/tests/Test-WorldNaturalPackageSafety.ps1` | One expectation and its comment (repair, finding 4). Nothing else in `tools/win/tests` is changed |
| `tools/README.md` | Rows for the above |
| `docs/design/GREENWATER_STORY_001_RECEIPT.md` | Section 9 |

Not changed, and tested not to be: `MQ01Quest`, `SQ01Quest`, `MercyBriefing`, `Core` and the other 13 reviewed scripts; the accepted writing under `assets/incoming/act1/story`; the four earlier package manifests; `tools/win/mercy-briefing-candidate.json` and `tools/mercy_briefing_candidate.py`; every earlier packager, launcher and PowerShell test; `.gitattributes`; `.github`; `tools/papyrus_sim/game_runs.json`; `MatrixCases.psc`; `docs/design/VERIFY_LOG.md`.

## 3. Mapping and guards

`docs/design/GREENWATER_STORY_001_MAPPING.json` is the mapping ledger. It lists, for each of the 34 spoken records, the node of `talk/tlm_mq02b.json` (or `tlm_mq02.json`) it is word for word, the exact condition under which it is shown, and what each button then does; the 49 technical boxes and notes, which are this build's own words and are never inside quoted speech; the two documents and how they are paged; the quest's stages and objectives; and each accepted flag's one global and its single setter.

`test_greenwater_projection.py` checks that file against the plugin as built and the story JSON character by character. The longest displayed string is 236 characters (the project's margin is 240).

Two excerpts and no more, both from the order:

- `hatcher_lost` with Opal dead, absent or in a fight is shown only through `She's yours, friend, every sack.` (item 8). The full speech is kept when she can be given him. Records `HatcherLostNoOpal`, `HatcherLostAlone`.
- `hatcher_paid` is one speech over two boxes, cut before ` But a man sees`, because the whole line with his name is 255 characters, the length at which the game was seen to cut a box short.

Opal's reactions, as guarded (item 9):

| Line | Shown only when |
|---|---|
| `starnes_after_won` | outcome 41, cargo actually home whole, Hatcher alive, present and unjudged; Opal can speak |
| `starnes_denied` | outcome 41, cargo home whole, Hatcher released or in custody; not said before |
| `starnes_won_hatcher_dead` | outcome 41, cargo home whole, Hatcher dead otherwise than by stage 60 |
| `starnes_after_hanging` | outcome 41, cargo home whole, stage 60, Hatcher hanged |
| `starnes_after_chute` | outcome 42, stage 42, cargo home reduced, more than nothing recovered |
| `starnes_after_fire` | outcome 43, stage 43, cargo destroyed |
| `starnes_after_share` | stage 44, the share actually paid, the lie explicitly told to her alive (which sets `grain_sold`); stage 46 carries the full journal text only after her answer, given alive |

"Can speak" is one function, `MQ02BQuest.CanSpeak`: not dead, not disabled, not in combat. Each action checks only the people it needs, and checks them again after every box that leads to it: between the two halves of a speech, after a question before its answer is carried out, and after a notice before anybody is moved.

## 4. Records, as the stand-in build reads them back

From `build/sim/TheLastMeridian.json` (the plugin built against the default stand-in master). `tools/win/greenwater-story-candidate.json`, under `records`, holds the same and is tested against that build.

| Record | What |
|---|---|
| `TLM_MQ02B` | Main quest, priority 55, not start-game-enabled, script `TLM:MQ02BQuest` (26 properties). Stages 10, 20, 30, 40, 41, 42, 43, 44, 45, 46, 50, 60, 61, 100; 100 completes. Six objectives (10, 20, 40, 50 accepted; 60 and 80 this build's). Eleven optional aliases filled by script: Opal, Hatcher, Rafferty, Belden, Crew1, Crew2, Steeple, Table, Strongbox, Pilot, Exit |
| `TLM_GW` | Development greybox, no stages, script `TLM:GreenwaterWalk` (117 properties). 31 aliases, each a placed reference; 27 carry `TLM:GreenwaterTalk` |
| `TLM_WS_GW` | Made by the exterior builder: a clone of `TLM_GW` with 31 persistent references of its own. `TLM_MQ02B` is not cloned |
| 12 globals | `TLM_G_MQ02B_Outcome`, `Cargo`, `Recovered`, `Hatcher`, `GrainHome`, `GrainSold`, `QueenBurned`, `HatcherHanged`, `HatcherFriend`, `HatcherHunting`, `SilverRiver`, `Reported` |
| 2 factions | `TLM_Fac_Greenwater`, `TLM_Fac_QueenCrew` |
| 6 actors | `TLM_NPC_WARDEN_GREENWATER`, `TLM_NPC_PILOT_GREENWATER`, `TLM_NPC_DELEGATE_COMMONWEALTH`, `TLM_NPC_COMMODORE_QUEEN`, `TLM_NPC_QUEEN_CREW_01`, `_02`. Copies of the game's settler with no packages: **development builds only** |
| 1 book | `TLM_BOOK_LetterOfHire` |
| 17 activators, 4 triggers | the pieces |
| 31 placed references | `TLM_REF_GW_*`, in the test room |
| 91 messages | 34 speech, 49 technical, 8 document pages |

Four named people, as the registry has them. The two crew are anonymous ("one of the Queen's crew"); no thirty occupants are simulated or claimed.

One binding was added elsewhere: `TLM:Act1Walk` on `TLM_A1` has `TLM_Greenwater` → `TLM_GW`. In the exterior the builder re-points the clone `TLM_WS_A1` at `TLM_WS_GW`.

## 5. Allocation

`tools/PluginBuilder/formkeys.txt`: lines 1 to 338 are a8's, byte for byte (compared with `git show a8f6d64:…`). 166 names follow, numbered 2217 to 2382 without a gap and without reuse of an earlier number. The first 162 are the reviewed commit's, with their numbers; the last four are the repair's notices.

| Kind | Count |
|---|---|
| quests (`TLM_MQ02B`, `TLM_GW`) | 2 |
| globals | 12 |
| factions | 2 |
| actors | 6 |
| book | 1 |
| activators | 17 |
| triggers | 4 |
| placed references | 31 |
| messages | 91 |
| **total** | **166** |

The allocator reads that file, so the numbers are the same in every build. The exact names and numbers are in the manifest under `idFile.appended`.

## 6. Provenance

`tools/win/greenwater-story-candidate.json` is this candidate's own manifest. `python3 tools/greenwater_story_candidate.py verify` passes on this checkout.

**23 scripts.** Selected for a bundle:

- **17 reviewed compiled files**, byte for byte, of the Details runtime (`tools/win/world-details-artifact.json`): the scripts whose source is still that package's pinned text. Each is to be checked against its pinned digest before use.
- **6 from a fresh compile**: `Act1Walk.pex` and `Act1Guide.pex` (changed), `MQ02BQuest.pex`, `GreenwaterWalk.pex` and `GreenwaterTalk.pex` (new), and `MercyBriefing.pex`.

`MercyBriefing.psc` is a8's source, word for word. It is compiled afresh all the same: the repository records no measured digest of a compiled `MercyBriefing`, so there is no reviewed file here to check one against. If root records that digest, a later manifest may reuse the file; this one does not, and its check fails if anybody adds one.

A full fresh compile of all 23 is the proof that the source compiles; its 17 are never bundled. Every measured field (`masterSha256`, `worldSha256`, `runtime`, `runtimeManifestSha256`, `freshCompile`) is `null`, pending a real build, and the check fails if one is filled in without who measured it and from what.

Frozen, and checked to be: the four earlier package manifests byte for byte; the a8 manifest, its check, `World-Story.psm1`, `Play-WorldStory.ps1`, `Build-WorldDetails.ps1`, `Build-WorldNatural.ps1` and `Stage-WorldDetails.ps1` as text. None of them mentions this candidate. The a8 check **refuses this checkout**, naming `Act1Walk`, `Act1Guide` and the three new scripts, and still passes on the a8 tree. The Details and Natural packagers refuse it too by their own rule (19 names); that was not run here.

**Packager.** `tools/win/Build-Greenwater.ps1` is the opt-in build of this candidate only. It takes the master, the reviewed runtime, a fresh compile and a Python interpreter. Before it creates anything it checks the output folder, then **runs the full source verifier and stops unless it passes** (repair, finding 9), then checks the 23 scripts and the 17 pins itself. It bundles 17 + 6 and writes `measured.json`: a measurement, compared with no pin, because none exists. Its output-folder guard is `Build-WorldDetails.ps1`'s, line for line. It cannot tell which source the fresh compiled files were made from, and says so: the compile log and root's review of it are what do. **It and its fixture have never been run or parsed**; only their text was checked, and the fixture's six changes were carried out in Python against the real verifier.

**Launcher.** None was added. The frozen launchers stage only packages whose pins they hold. Staging a measured bundle into a disposable profile is root's.

**QA.** `TLM_Core`'s scenario stays 0; `Core.psc` is the reviewed text. No QA-only script, record or helper is in this source. Nothing sets a stat. The two starts of the order's item 5 are root's disposable characters.

## 7. The order's ten clarifications

| # | Where it is done | Tried by |
|---|---|---|
| 1 Availability | Hub, hand-off footer, briefing journal, first-section ending, completed guide, travel and completion text. The a8 package keeps its wording | `test_availability_text_tells_the_new_truth`, `test_the_availability_text_is_the_orders` |
| 2 Cargo and judgment | `Cargo` 1 (yielded) at the win, 2 only at `CompleteReturn`. `Hang`, `Custody`, `Release` are separate functions, each rechecked after its box. The menu is one of four whole messages by who can receive | `test_cards_then_the_barge_home_and_each_judgment`, `test_no_pritchard_no_custody`, mutations `the_card_win_taken_for_the_grain_at_home`, `a_hanging_nobody_chose`, `a_dead_opal_handed_a_prisoner` |
| 3 The lie | `TakeShare` pays once; `TellLie` is its own box and sets `grain_sold` (the paid deal and the lie delivered to her alive); `LieWasHeard` sets stage 46 on her answer | `test_the_share_the_lie_and_her_thanks`, `test_the_share_with_no_lie_told_still_finishes`, mutations `her_thanks_on_payment_alone`, `the_lie_told_for_the_player`, `paid_twice` |
| 4 Friend, hunting | `Release` alone sets `hatcher_friend`; `CompleteReturn` of an escape with Hatcher alive and free alone sets `hatcher_hunting` | mutations `a_friend_who_was_not_released`, `a_dead_hatcher_hunting` |
| 5 Stats | Threshold 5 on current Charisma; base and current are traced at each deal | `test_the_threshold_is_five_…`, `test_current_and_not_base_charisma_is_played` (stand-in values) |
| 6 Physical outcomes | Cargo pieces switched, caps and food counted in the inventory, cast moved, killed or restrained; a scene not seen records nothing | `test_the_fire`, `WhatTheGameDoesNotHonour` |
| 7 Provenance | Section 6 | `test_greenwater_candidate.py` |
| 8 Dead-Opal prefix | Section 3 | `test_the_two_excerpts_are_exactly_what_the_order_allows`, `test_opal_dead_and_the_other_three_courses` |
| 9 Guards, escape lock | Section 3; `EscapePending` from the chain cut to stage 42 | `test_an_escape_pending_goes_with_the_player_and_comes_back`, `test_the_run_interrupted_is_begun_again_and_done_once`, mutations `cut_then_burn`, `the_run_recorded_at_the_lever` |
| 10 Crew, dead-Opal access | Two crew in `TLM_Fac_QueenCrew`; `GreenwaterTalk` reports an attack or a killing and the walk starts combat for the crew and Hatcher only. The gangway, off side and every deck piece work with Opal dead and stage 20 never set | `TheQueensCrew`, `test_opal_dead_before_she_was_heard`, mutation `boarding_locked_behind_opal` |

## 8. What was run here, and what came out

On the repaired source.

| What | Result |
|---|---|
| `tools/run_checks.sh`, with the one line that needs PowerShell (`tools/test_world_story_launcher.py`) left out | exit 0. Logic model 142 tests; consistency clean for 23 scripts; 74 intake fixtures; strict intake 227 lines, 33 histories; stand-in build self-check passes; simulator 597 tests; **65 of 65 scenarios, 1628 checks**, also at 60 calls a second; scenario 12 still 42 checks |
| `test_greenwater_repair` | 63 pass: 41 probes of the findings through the real scripts, and 22 trials that take each repair out again, each caught |
| `test_greenwater` | 94 pass. Its 20 mutation trials each break the real script one way and are each caught for the stated reason |
| `test_greenwater_model` | 27 pass, including every sequence of seven actions in three worlds |
| `test_greenwater_projection` | 14 pass |
| `test_greenwater_world_clone` | 13 pass: stand-in master → plugin → clone step → read-back; 60 persistent references (29 + 31); `MercyReturn` read back at Z 32; seven kinds of damage each refused; a source from before the road clones as it did |
| `test_greenwater_candidate` (33) with `test_mercy_briefing_candidate` (22) | 55 pass |
| `greenwater_story_candidate.py verify` | passes |
| `mercy_briefing_candidate.py verify` | **refuses this checkout**, as it must |
| A lint of the four road scripts for reserved-word names, redeclared locals, locals named like a function of their own script, and non-Papyrus syntax | one found and renamed (a local `stamp` in `Stamp()`); nothing else. A text scan, not a compiler |

All of these are among the 597, or are the model's 142, except the two `verify` runs and the lint.

**Not run:** the Papyrus compiler on the repaired source; any build against the game's master; `tools/WorldSliceBuilder` as a whole; **anything in PowerShell**: `Build-Greenwater.ps1`, its fixture `Test-GreenwaterPackageSafety.ps1`, the corrected `Test-WorldNaturalPackageSafety.ps1`, `Test-WorldDetailsPackageSafety.ps1`, the launcher test, `Test-ScenarioReport.ps1`; the game.

Root reports having compiled 23 of 23 scripts of `7e05c6b` with the licensed compiler and built and read it back against the owned master. That was the unrepaired source. Three scripts have changed since (`MQ02BQuest`, `GreenwaterWalk`, `Act1Walk`), all three among the six that are compiled afresh anyway; the repaired source has not been compiled by anybody.

A stand-in pass means the scripts do what the model says on an engine written from this project's notes. A probe that presses a button there is not a press in the game. It is not a compile and not a game test.

## 9. Source against native: what is not known

1. **Whether the repaired scripts compile.** Root compiled `7e05c6b` (reported; not seen here). `MQ02BQuest`, `GreenwaterWalk` and `Act1Walk` have changed since by about 500 lines and have not met the compiler. One compile error of my own making in the repair was caught by the stand-in engine and fixed (an undeclared constant); a test now looks for that kind.
2. **Three natives written from memory**: `ObjectReference.GetValue(ActorValue)`, `GetBaseValue(ActorValue)`, the `OnTriggerEnter` event on an alias. Marked unverified in `tools/papyrus_natives.json`.
3. **What the builder finds in the real master** for `Charisma` (by editor id), for the meal (by the names a player sees: Corn, Vegetable Soup, Noodle Cup, Tato, Mutfruit) and for caps. If Charisma is not bound no card is dealt and the script says so; if no meal is found the bowl is not given and the build says so; if caps are not bound no share is offered. The builder's output is to be read.
4. **The six people.** Copies of the game's settler with no packages. Whether they stand where placed, can be spoken to, and take 1 to 30 seconds to appear as the first section's did, is not observed for these.
5. **Crew retaliation.** `StartCombat` from a script on a killing or an attack, for whoever of the three lives and is not already fighting. Whether the two crew and Hatcher actually fight, and nobody else does, is **pending until observed**; item 10's `cannot_break` is not claimed met. Whether the game raises a combat event for a fight already under way is not known; the script no longer depends on the answer.
6. **Hanging and custody.** `MoveTo`, a look at where he is, then one `Kill` and a wait of up to 3 seconds for his death; `MoveTo`, a look, then `SetRestrained`. Not observed. Whether `MoveTo` has put an actor in place by the time the next line reads his position, whether `Kill` is immediate, and whether 256 units and 3 seconds are sensible, are all unknown: if the game is slower than either number a real hanging is refused (and said to be), never invented. Custody needs Pritchard in the same cell within 1500 units after the move.
7. **Travel.** `MoveTo` between Mercy and the greybox, in the test room and in the exterior. No fade is played; the notices are message boxes.
8. **The ground.** `MercyReturn` stands at Z 32 over the cabin's floor tiles, whose surface the exterior builder gives as Z 16 (section 13, finding 8): arithmetic on that builder's source, **not a grounding pass**. Whether the player lands and stands there is a gate for root before staging. In the exterior the other sites are at least 600 units from every piece of the expansion's scenery and south of the bypass road, by arithmetic on the builder's source. Terrain height, collision and whether a spot can be stood on were not checked. In the test room, a spot is open floor only once somebody has stood on it.
9. **Persistence.** The escape lock, the execution intent, the ordered fire and the one-time grants are script variables, which the game saves. Tried here only as "the load event changes nothing". What becomes of a save made during the 3 seconds of a hanging's wait, or during any other wait in these scripts, was not tried and is not known here.
10. **The journal.** Objectives are flagged displayed. Nothing sets or has checked quest tracking.
11. **The exterior builder against the real master.** Only its cloning step ran, on a stand-in.

## 10. Unresolved mechanics

- No boat moves. The Chute, the tow and the fire are notices and switched pieces.
- "Recovered" (12, 8 or 6 of 12) is bookkeeping for the cargo piece shown; no sack count is canon and no speech states one.
- After the fire Hatcher, if he was alive aboard, is recorded as not accounted for (5), not dead: no death is counted that did not happen to an actor.
- `hatcher_hunting` and `hatcher_friend` are stored; no encounter, speech or price follows from them yet.
- Belden is switched on only by outcomes 43 and 44 and hands over one relief portion; nothing else of the Commonwealth's is built.
- A paid share with Opal dead, gone or fighting before the lie, or with the lie never told, completes the road without `grain_sold`. With the lie told and her answer never heard, it completes with `grain_sold` and without stage 46.
- A hanging that stops at the ring (Opal gone, a fight, a kill that does nothing) leaves Hatcher alive where he was taken, at the steeple. He still deals from there: the table and he are used, not a place. Nothing moves him back.
- A death more than 3 seconds after the one `Kill` is a death otherwise, not a hanging. Declared, not measured.
- A fire ordered and not shown, or a return whose cargo is not shown, keeps its course exclusive until it is shown. If a piece it needs is missing for good, the road cannot be finished by that course or any other, and the text says to report it. There is no way back from an order.
- The river report is offered only in Pritchard's own conversation after the first section; the fair is not built and nothing of it is implied.
- No launcher; the packager and its fixture are unrun.

## 11. Next operator actions (root's)

1. Independent source review.
2. `python tools/greenwater_story_candidate.py verify` on the review checkout.
3. Compile all 23 scripts; keep the log.
4. Run `tools\win\tests\Test-GreenwaterPackageSafety.ps1 -Python <interpreter>`, `Test-WorldNaturalPackageSafety.ps1` and `Test-WorldDetailsPackageSafety.ps1` in Windows PowerShell 5.1 and PowerShell 7. None has been run on this source.
5. Build with `tools\win\Build-Greenwater.ps1 -Python <interpreter>` (read it first), or by the manifest's recipe by hand; read both build outputs. Keep the compile log: it, not the packager, ties the six fresh files to this source.
6. `python tools/greenwater_story_candidate.py measure <bundle> --fresh-compile <folder>`; record the digests.
7. Before staging: see where `MercyReturn` puts the player.
8. Stage into a disposable profile; play each of the four courses, a card loss then another course, each judgment, both kinds of evidence, the dead-cast cases, leaving and coming back, and the crew.

## 12. Rollback

The implementation is `7e05c6b` on `feat/greenwater-story-001`, above `637cbed`; the repair is on `feat/greenwater-story-001-repair`, above `7e05c6b`. Dropping the repair branch restores the reviewed source; dropping both, or checking out `a8f6d64`, restores the Mercy briefing candidate exactly: its manifest and check were not edited. No installed file, save, profile, pin, workflow or setting was touched, so nothing outside the branch needs undoing.

## 13. The repair after independent review of `7e05c6b`

Receipt first (`07d4ae0`), then one commit. Nine findings from the review and the coordinator, and two more found on the way. Every probe named here runs the real scripts on the stand-in engine through the piece or the person, as the game would reach them; what is seeded (a box that gives no answer, a call that does nothing, a late death, an empty alias, somebody dying or fighting meanwhile) is a way a call could fail, not a claim about the game.

| # | What was wrong | What it is now | Probes (`test_greenwater_repair.py`) |
|---|---|---|---|
| 1 | The skiff's and the lever's notices were not read; the lever began its return before its notice | Only the notice's one button goes on. After it: player alive, road open, the road's exclusive state the same as before the box (`MQ02BQuest.Stamp`), the marker still there. `BeginReturn` is a read (`ReturnOffered`) and a commit made after the notice. A return already begun stays begun. The fire's closing notice moves nobody unless confirmed | `SceneNotices`, 8: -1 and 7 on each notice; the player dead, the marker gone or the road changed under it; begun again after a refusal; the claim released each time |
| 2 | `Hang` killed with no ring, or after a move nobody checked; a late death became "dead otherwise" | No ring or a ring switched off: nothing is done. An execution intent; the move; Hatcher **seen at the ring** (same cell, 256 units) and Opal, Hatcher, the player and the road asked for again, **before** one `Kill`; his death waited for up to 3 seconds; recorded by one function (`RecordHanging`) from the wait or from his death event, whichever is first. Custody and release also need him in no fight | `Hanging`, 10: carried out; no ring; a move that does nothing; Opal dead or Hatcher fighting before the kill; a fight under his question; a kill that does nothing, then an unrelated death; a death 0.5 s late (the hanging); a death 10 s late (not); the event and the wait writing the same record; the dead-Opal menu |
| 3 | A fire that was not seen switched its own firebox off and then said to use it | The deck is cleared by a recorded fire only. No marker: no order. Not seen: the marker off again, the cargo as the facts have it, the firebox seen on, then the instruction; if it cannot be had, a different text and no instruction. `FireDone` is handed the marker and the cargo and looks itself | `Fire`, 6: refused once then shown by using the firebox again; left for Mercy and come back to; no marker; cannot be shown; not confirmed or stale; the rule asked directly |
| 4 | The Natural fixture expected `Act1Walk.psc`; the frozen packager refuses at `Act1Guide.psc` | The one expectation and its comment. Worked out from the pins' order and this checkout; the Details fixture's expectation still follows from its packager's order of checks. **Not run: no PowerShell here** | `test_greenwater_candidate.py`: the fixture differs from the contract commit's by that one line outside its comment |
| 5 | Nothing was asked between a speech's halves or before some commitments; `grain_sold` waited for her answer | The speaker and the player are asked for after every box that leads on. No second half of the admission, and no stage 50 by it, without Hatcher at his table throughout. `grain_sold` is set by `TellLie`, the lie delivered to her alive, and kept; `LieHeard`, stage 46 and the cup wait for her answer, alive. Nothing earned is cleared | `BetweenPagesAndBeforeCommitments`, 6: Hatcher dead or fighting under either half, and the letter still works; evidence already earned kept; her answer cancelled, or she dies under it, then heard on a later visit; no lie to nobody; Opal's and Rafferty's own questions answered to them |
| 6 | A report that came back unanswered fell through into the briefing | `OfferReport` gives one of four answers. Shown and not validly answered, or stale: the conversation is over. `[Later]` still leads on to the briefing | `Report`, 5, through Pritchard himself: -1 and 7, known and unknown; Pritchard dead or fighting, the player dead; `[Later]` and `[Report]`; with the side quest's report still to make |
| 7 | The cargo was recorded home without being looked at | The home piece on and the lashed one off, looked at, before anything is written; `CompleteReturn` is handed both and looks itself. Not seen: pieces put back, the return and the chain lock kept, no stage 42, no completion; the lever and the dock work again | `Cargo`, 4: reduced and whole, each refused once then seen; no completion in between; a missing piece; the rule asked directly |
| 8 | `MercyReturn` at Z 0 inside the cabin floor's footprint, surface Z 16 | Z 32 in the spec and the exterior builder: the surface plus 16. The footprint is computed from the builder's source (x 2664 to 3432, y 2672 to 3184). No other site moved. **Not a grounding pass** | `test_greenwater_world_clone.py`: it is the one site over the floor; 16 above it; read back at 32; every other site as at `7e05c6b` |
| 9 | The packager checked the 23 scripts only before it built | It runs the full verifier first and stops unless that exits 0 and says so; `-Python` names the interpreter. A fixture changes a builder source, the exterior builder, the id file, a document, a frozen packager and an earlier manifest on a copy. **Neither is run** | `test_greenwater_candidate.py`: the order of the packager's steps; each of the fixture's six changes made in Python and refused by the real verifier in the words the fixture expects |
| + | `GreenwaterWalk` used a constant only `MQ02BQuest` declared (mine, in this repair) | Declared | `test_greenwater.py`: every such name a road script uses is one it declares |
| + | `FightBack` restarted fights already under way from every combat event; on the stand-in they multiplied without end (in `7e05c6b`) | Nobody already fighting is started again | `Crew`, 2 |

**Changed by the repair:** `MQ02BQuest.psc`, `GreenwaterWalk.psc`, `Act1Walk.psc`; `SpecGreenwater.cs` (the marker's height, four new notices, one reworded), `WorldStory.cs` (the height), `formkeys.txt` (four ids appended, 2379 to 2382), `last-build.report.txt`; `greenwater_model.py`; `greenwater_player.py`; `test_greenwater.py`, `test_greenwater_projection.py`, `test_greenwater_world_clone.py`, `test_greenwater_candidate.py`; `Build-Greenwater.ps1`; `Test-WorldNaturalPackageSafety.ps1`; `greenwater-story-candidate.json`; the mapping, this ledger, `tools/README.md`. **New:** `test_greenwater_repair.py`, `Test-GreenwaterPackageSafety.ps1`, the repair receipt.

**Not changed:** `GreenwaterTalk.psc`, `Act1Guide.psc`, `MercyBriefing.psc` and the 17 reviewed scripts; the accepted writing; the four earlier manifests; the a8 manifest and its check; the earlier packagers, stagers and launchers; `Test-WorldDetailsPackageSafety.ps1`; `.gitattributes`; `.github`; `sim.py`; `game_runs.json`. The selection is still 17 reviewed and 6 fresh, the same 17 and the same 6.

**The text mapping** was regenerated: the four new notices, the reworded one, and every guard the repair changed, in the words of the scripts.

