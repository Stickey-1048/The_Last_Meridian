# GREENWATER-STORY-001: repair receipt

17 November 2026. Written and committed **before any source was changed** on this branch. It names what was received, where each finding was located in the reviewed source, the repair planned for each, the intended files and the branch. What was actually done is added at the end (section 6) when the work is finished.

Nothing here is a Papyrus compile, a build against the game's master, a load in Fallout 4 or a play session. No licensed input is in this checkout or was asked for.

## 1. What was received

| Input | Exact identity | How it was verified |
|---|---|---|
| Reviewed commit | `7e05c6b879e21940786c008f9dcdef4d5404654c`, tip of `feat/greenwater-story-001` | fetched by branch name; the fetched tip is that hash; the working tree was clean |
| The consolidated repair request | eight numbered findings from independent review (Sam, Nora, root), in the coordinator's message of 17 November | read in full |
| Root's diagnostics at `7e05c6b` | 23 of 23 scripts compiled with the licensed Papyrus compiler 2.8.0.4; built and read back against the owned master and exterior; 17 reviewed + 6 fresh selected | **reported to me, not seen by me.** They prove compiling and building of `7e05c6b` only. The source is not accepted, and they say nothing about the repaired source, which must be compiled and built again |
| Remote CI run 44006976340 and local Windows PowerShell 5.1 | both fail at `tools/win/tests/Test-WorldNaturalPackageSafety.ps1:40` | reported to me; the cause was confirmed here by arithmetic (section 2, finding 4), not by running PowerShell, which this environment does not have |

**Repair branch:** `feat/greenwater-story-001-repair`, made from the exact reviewed commit. No reset, rebase, merge or force-push; no pull request opened by this work.

This is a repair of the one road. No new scope, scenery, speech or story decision. The accepted writing under `assets/incoming/act1/story`, the four earlier package manifests, the a8 manifest and its check, and every earlier packager, launcher and workflow stay as they are.

## 2. The findings, located

Each was read in the source of `7e05c6b` before this receipt was written. Line numbers are that commit's.

| # | Finding | Where it is | Confirmed by reading |
|---|---|---|---|
| 1 | Scene boxes ignored | `GreenwaterWalk.psc` `TakeSkiff` (795 to 797): `ShowBox(NoteSkiffScene)` result unused, then both moves. `AtPilot` (1036 to 1046): `BeginReturn()` sets `ReturnPending` **before** the box, the box's result is unused, and `player.MoveTo(chute)` follows with no check of the player | yes |
| 2 | Hanging without a seen place | `MQ02BQuest.psc` `Hang` (714 to 717): `If ring` guards only the move; `Kill()` runs with no ring and after a move nobody checked. `IsDead()` is read once, straight after `Kill()`; `HatcherDied` returns at once while `Judging`, so a death that arrives late is recorded as 4 by `HatcherState` and stage 60 is never set | yes |
| 3 | Fire retry unreachable | `GreenwaterWalk.psc` `StageFire` (1107) calls `Refresh`, which switches `FireControl` off whenever `IsBurning()` (394 to 400); the failure text then says to use the firebox | yes |
| 4 | Fixture expects the wrong script | `Test-WorldNaturalPackageSafety.ps1:40` expects `…reviewed logical source: Act1Walk.psc`. `Build-WorldNatural.ps1` walks `world-natural-artifact.json`'s `sourceTextSha256` in file order and throws at the first difference. Computed here from that file and this checkout's sources: the differing scripts, in that order, are `Act1Guide.psc`, then `Act1Walk.psc`. So the unchanged packager correctly refuses at `Act1Guide.psc` | yes, by arithmetic |
| 4b | The Details fixture | `Build-WorldDetails.ps1` compares the count and names of the scripts (19) before any text, and this checkout has 23. Its fixture expects `Current source names differ from the reviewed19 scripts`, which is still what that order of checks gives. Not changed | yes, by reading |
| 5 | Post-modal guards incomplete | `TableTalk` (871 to 878): nothing is asked of Hatcher between `HatcherPaidA` and `HatcherPaidB`, nor before `LearnHire`. `AfterShare` (747 to 748): `LieWasHeard` after her box with no recheck of her, and `LieWasHeard` (543) asks only `RoadOpen` and `LieTold`. `JudgeAtTable` (961 to 963) passes straight to `Judge`; `Hang`, `Custody` and `Release` use `HatcherToJudge`, which is `IsThere` (a man in a fight passes). `grain_sold` is written only in `LieWasHeard`, so a lie told and her answer cancelled leaves it 0 | yes |
| 6 | Report cancel falls through | `OfferReport` (1193 to 1199) returns `false` for "left for later", for a box that gave no answer and for a stale conversation alike; `Act1Walk.AfterTheChapter` then opens the briefing | yes |
| 7 | Cargo recorded unseen | `MQ02BQuest.CompleteReturn` (622 to 647) writes cargo, `grain_home`, stage 42 from the pending return alone; `ReachedDock` switches the pieces afterwards by `Refresh` and never looks at them | yes |
| 8 | `MercyReturn` under the cabin floor | `WorldStory.GreenwaterSites["MercyReturn"]` = (3150, 2700, 0). The cabin's floor tiles (`Program.cs` 121 to 124) are 256-unit `workshop_ShackMidFloor01B` at x 2792, 3048, 3304 and y 2800, 3056, placed at Z 16: a footprint of x 2664 to 3432, y 2672 to 3184 (the builder's own furniture check uses 2668 to 3428 and 2676 to 3180). (3150, 2700) is inside it, 16 units below the surface the builder calls the native-tested support. `MercyTravel` (3150, 2620) is outside it | yes, from the builder's source. The tile's real bounds are in the game's master, which is not here |

## 3. The repair planned

**1. Scene confirmation.** A scene notice's answer is read. Only button 0 goes on. After it, before any move or any change of a pending fact: the player alive and the road open; the road's exclusive state (claim, escape pending, return pending, burning, outcome, cargo, completion) the same as before the box; the target marker still there. `BeginReturn` is split: a read of which return the lever can begin, and the commit, made after the confirmation and only for that same return. A cancelled, unsupported, stale or dead action leaves every fact as it was and moves nobody. A return already pending stays pending and can be begun again. The fire's closing notice gets the same treatment for its move to the landing.

**2. Hanging.** Fails closed with no ring, a ring switched off, or anybody it needs not alive, present and in no fight. Then: an execution intent is written; Hatcher is moved; he is seen at the ring (same cell, within a declared 256 units), and Opal, Hatcher, the player and the road are asked for again, **before** `Kill`. `Kill` is issued once and never again for that order. His death is waited for over a declared bound (3 seconds); whichever sees it first, the wait or his alias's death event, records the hanging, through one function, once. A death after the intent has lapsed, or with no intent, is a death otherwise. A refused kill records nothing and leaves him alive. Custody and release also ask for Hatcher in no fight. The dead-Opal behaviour is untouched.

**3. Fire.** The firebox stays on while a fire is ordered and not yet recorded; the deck is cleared only once it is. Before the order is taken: the burned marker must exist, else no order and a plain statement. After a failed showing the firebox is seen to be usable before the text says to use it; if it or the marker cannot be had, a different, exact text says so and gives no retry instruction. `FireDone` is given the marker and the lashed cargo and records only if it sees the one on and the other off. The pending fire stays exclusive throughout.

**4. Fixture.** The one expectation and its comment in `Test-WorldNaturalPackageSafety.ps1` are changed to the script the unchanged packager actually refuses first, `Act1Guide.psc`. Still an exact message, still followed by the no-output, sentinel and ancestry checks. The packager, its pins, the Details fixture and the workflow are not touched. **PowerShell cannot be run here; both shells remain root's to run.**

**5. Guards between pages and before commitments.** After every box whose answer leads on: the player alive and the road open, the speaker still alive, present and in no fight, and the action still the eligible one. `HatcherPaidB` is not shown, and stage 50 is not set by the admission, unless Hatcher is at his table before and after each page; the letter route is independent and unchanged. A judgment is not carried out on a man who is dead, gone or fighting. `grain_sold` moves to the acknowledged telling of the lie to a living Opal (`TellLie`); `LieHeard`, native stage 46 and the cup wait for her valid, living answer, which can be heard on a later visit. Nothing already earned is cleared. No rule asks for more of the cast than its action needs.

**6. Report.** `OfferReport` says which of four things happened: nothing was offered; the report was given; it was explicitly left for later (the documented `[Later]` button, which still leads on to the briefing so that the briefing stays reachable); or a shown report came back cancelled, unsupported or stale. The last closes Pritchard's conversation: no briefing and no other line in that activation.

**7. Cargo.** At the return dock the home cargo piece is switched on and the lashed one off, and both are looked at, before anything is recorded. `CompleteReturn` is given the two pieces and writes nothing unless it sees them so. On failure the pieces are put back as the facts stand, the pending return and the chain lock stay, stage 42 and completion stay unavailable, and the lever and the dock can be used again. A missing piece gets an exact text and no retry instruction.

**8. Marker.** `MercyReturn` goes to Z 32 in `SpecGreenwater.Parts` and `WorldStory.GreenwaterSites`: the floor's Z 16 plus 16 units to settle, the height the builder's own exterior arrival marker uses. A test will hold it inside the footprint computed from the builder's source and above that surface. No other placement moves. Whether the player lands and stands there in the game stays a gate for root; no grounding is claimed, and nothing is said about the earlier a8 saved state.

## 4. Files this work intends to touch

Scripts: `MQ02BQuest.psc`, `GreenwaterWalk.psc`, `Act1Walk.psc` (the report's four answers). Not `GreenwaterTalk.psc` unless a guard requires it.

Records and exterior: `SpecGreenwater.cs` (the marker's height; new and reworded technical notices, none of them speech), `WorldStory.cs` (the same height), `formkeys.txt` (appended only, for new notices), `last-build.report.txt`.

Model and tests: `greenwater_model.py` and its test (`grain_sold` at the lie); `sim.py` (seeded refusals and delays for a test, marked as such); `greenwater_player.py`; `test_greenwater.py`, `test_greenwater_projection.py`, `test_greenwater_world_clone.py`, `test_greenwater_candidate.py`.

Fixture: `tools/win/tests/Test-WorldNaturalPackageSafety.ps1`, one expectation and its comment.

Provenance and documents: `tools/win/greenwater-story-candidate.json` (new source digests; every measured field still pending), `tools/greenwater_story_candidate.py` only if a pinned path or count requires it, `GREENWATER_STORY_001_MAPPING.json`, `GREENWATER_STORY_001_LEDGER.md`, `tools/README.md`, this receipt.

Not touched: the accepted writing; `MQ01Quest`, `SQ01Quest`, `MercyBriefing`, `Core` and the other reviewed scripts; the four earlier manifests; `mercy-briefing-candidate.json` and its check; `Build-WorldDetails.ps1`, `Build-WorldNatural.ps1`, the stagers and launchers; `Test-WorldDetailsPackageSafety.ps1`; `.gitattributes`; `.github`; `game_runs.json`; `MatrixCases.psc`; `VERIFY_LOG.md`. The earlier receipt and its section 9 stay as committed.

## 5. Known in advance

- The candidate test pins `tools/win/tests` to the contract commit. With finding 4 it will pin every file there but the one fixture, and that fixture to exactly the one changed expectation.
- The stand-in engine has no way yet to refuse `Enable`, `Disable`, `MoveTo` or `Kill`, or to delay a death. Those will be added as seeds a test sets, off by default, and marked as seeds: they are not rules about the game.
- The number of freshly compiled scripts stays 6 and the reviewed 17 stay the same 17: no reviewed script's source is to change.
- A simulated press is not a native pass. Every regression added here runs the real scripts on the stand-in engine and proves nothing about the game.

## 6. Addendum received while the work was under way

Sections 1 to 5 are as they were committed in `07d4ae0`; nothing in them was edited. This section and the next were added afterwards.

**Finding 9, from the coordinator, 17 November, for this same repair** (an independent cloud QA comment on company issue 5, checked by the coordinator against `7e05c6b`): `tools/win/Build-Greenwater.ps1` checks only the script sources and the reviewed compiled scripts before it creates its output folder and runs the two builds from the checkout's C#. It never checks the builder's own sources, the id file, the documents or the frozen earlier files, and never runs `tools/greenwater_story_candidate.py verify`, which does. A changed builder, document or id file would pass the packager's check though the verifier refuses it. A finding by reading; no unsafe package was built, and root's diagnostic build was preceded by the full verifier.

Confirmed by reading `7e05c6b`: the packager's source check walks `sourceTextSha256` (the 23 scripts) and nothing else; its first write is the `New-Item` of the output folder; `dotnet run` follows.

**Planned for it:** the packager runs the full verifier after the output folder's own rules and before anything is created or built, and stops unless it exits 0 and makes its own statement; an interpreter that is absent or cannot be run stops it; `-Python` names the interpreter (nothing is installed, no path or policy is changed). Its existing checks stay. A new fixture, `tools/win/tests/Test-GreenwaterPackageSafety.ps1`, runs the packager on a copy of the files (never the checkout) with a builder source, the exterior builder, the id file, a document, a frozen packager and an earlier manifest changed in turn, and requires the verifier's refusal, its reason, no output and no build each time. **Neither file can be run here.** What can be: each of the fixture's six changes is made in Python on a copy of the tree and the real verifier must refuse it in the words the fixture expects.

Fresh compiled file names do not prove which source they were compiled from. The packager says so; the compile log and root's review of it stay required.

## 7. What was done

Added when the work was finished, 17 November 2026.

All nine findings were repaired as planned in sections 3 and 6. The account, finding by finding, with what was run, is `GREENWATER_STORY_001_LEDGER.md`, section 13.

**Found here, beyond the nine, and repaired in the same commit:**

- `GreenwaterWalk.psc` used `RV_RETURN_NONE`, which only `MQ02BQuest.psc` declared. My own mistake in this repair, caught by the stand-in engine on the first run: a compile error in the game. Declared. A test now requires every constant, alias and message a road script uses to be one that script declares; it fails with the line removed.
- **The crew's retaliation fed on itself.** `FightBack` called `StartCombat` for everybody who lives, and it is called from every one of their combat events; on the stand-in every `StartCombat` raises such an event, so the calls multiplied without end. It was in `7e05c6b`, where the tests ended before it showed. Whether the game raises a combat event for a fight already under way is not known. `FightBack` now leaves alone anybody already fighting, so each of the crew is set on the player once whichever way the game answers that.

**Where the work differs from this receipt:**

- Section 4 named `sim.py` for the seeded refusals and delays. They went into the test harness (`greenwater_player.py`) instead, which wraps the engine's calls for one test at a time; the engine is unchanged.
- `tools/greenwater_story_candidate.py` was not changed. `tools/win/tests/Test-GreenwaterPackageSafety.ps1` and `tools/papyrus_sim/test_greenwater_repair.py` are new.
- `NoteJudgmentFailed` now ends "Nothing is recorded." where it said "Nothing was changed.": after a hanging that stops at the ring, Hatcher has been moved.
- The declared bound on a hanging: a death more than 3 seconds after the one `Kill` is recorded as a death otherwise, not as a hanging. Both the wait and the death event agree on that. It is a declared number, not a measured one.

**Not done, and not claimed:** a Papyrus compile of the repaired source; a build against the game's master; any PowerShell run (the corrected Natural fixture, the new Greenwater fixture, the packager); the launcher test; anything in the game. Root's diagnostics were of `7e05c6b` and are not this source's.
