# NIGHT-MAIL-STORY-001: read and architecture receipt

17 November 2026. Written and committed **before any source was changed** on this branch. It names what was received and read, the native shape planned, the records, aliases and ids, how each scene and each piece of evidence is to be projected, the intended files, and the provenance plan. What was actually done is added at the end (section 10) when the work is finished, and in the ledger.

Nothing here is a Papyrus compile, a build against the game's master, a load in Fallout 4 or a play session. No licensed input is in this checkout or was asked for.

## 1. What was received

| Input | Exact identity | How it was verified |
|---|---|---|
| Contract commit | `d0756204ef9e79d67860422b21298d3b7807f9da`, tip of `feat/night-mail-story-contract` (draft PR 37) | fetched by branch name; the fetched tip is that hash |
| Its parent | `016b2b4005203ba180b908fb310a1653a95f934f` (the repaired Greenwater source) | the contract commit adds four documents and one `.gitattributes` line to it and nothing else (`git diff --stat`) |
| `docs/design/NIGHT_MAIL_STORY_001.md` | SHA-256 `6DDE040554712CBCEB060BA985FD8777A3F2F335A8BF2C74ADDE1E0E9E4F41CF`, 176 lines | read in full; the digest is the one the dispatch gives |
| `docs/design/NIGHT_MAIL_STORY_001_ORDER.md` | SHA-256 `8386699BF40AB9EE38282D5895CDC67CAA0AE932AB4E5F8D3A1BC73C98A18874`, 48 lines | read in full; the digest is the one the dispatch gives |
| `…_NORA_REVIEW.md`, `…_SAM_REVIEW.md` | `1A1FB6A3…6C3B`, `AD3EB8EA…BA15` | read in full |
| Accepted writing | `assets/incoming/act1/story`, as at `016b2b4` (narrative identity `d142104`) | unchanged; not to be changed |

**Implementation branch:** `feat/night-mail-story-001`, made from the exact contract commit. No reset, rebase, merge or force-push; no pull request opened by this work.

Where the outline and the order differ, the order is followed. Greenwater's source is reported clear at source, compile and artifact, with native play pending; nothing here assumes its stand-in tests say anything about the game.

## 2. Writing read for projection

From `assets/incoming/act1/story`, unchanged:

- `quests/tlm_mq02a.json`, whole: 15 stages, 4 objectives, both choice sets, 4 evidence entries, `cannot_break`, 9 flags.
- `talk/tlm_mq02a.json`, all 25 lines: `lockridge_default`, `_gate`, `_gate_alerted`, `_gate_sold`, `_dole`, `_rails`, `_hired`, `_after_ran`, `_after_dole`, `_after_sold`, `_hymnal`, `_stamp`; `tarrow_default`, `_footplate`, `_cut_before`, `_in_cut`, `_ran`, `_backed`, `_walking`; `dole_default`, `_sermon`, `_name`, `_silver`, `_share`, `_face`.
- `documents.json`: `yard_rules` (533 characters), `hymn_chalk` (135), `hymnal_flyleaf` (301), whole.
- `characters.json`: `lockridge` Augusta Lockridge, `tarrow` Wilhelmina Tupper, `dole` Ezekiel Dole.
- `talk/tlm_mq02.json`: the text only of `pritchard_hears_rail_after_fair` and `_unknown`.

One line is too long for one box with its speaker's name: `lockridge_gate` is 222 characters, 243 with `Augusta Lockridge: "…"`, over this project's 240. It will be shown as two boxes, cut between two of its own sentences (before ` Tonight I send`), with the buttons on the second. Every other line fits whole.

## 3. Native shape

Two quests, as Greenwater has, and one new cell.

- **`TLM_MQ02A`** (script `TLM:MQ02AQuest`): the road. The accepted stages and objectives, every fact later chapters read, every guard and every commit. It shows no box. Its aliases are filled by script. `tools/PluginBuilder/formkeys.txt` (670 lines, last id 2382) has no such name.
- **`TLM_NM`** (script `TLM:NightMailWalk`; alias script `TLM:NightMailTalk`): the greybox. The placed pieces in aliases of its own, the lines, the boxes, the staged scenes. Development only.
- **`TLM_CELL_NightMail`**: an interior cell **of this plugin's own**, holding the five zones. Nothing of the kind exists: the builder only overrides one of the game's cells today. Making a cell, filing it under its block and sub-block, flooring it, placing into it by its own coordinates and reading all of that back is new builder work and is planned as such (section 6).

The exterior builder will clone `TLM_NM` as it clones `TLM_GW`, giving the owner's world its own two Mercy pieces (the travel point and the return marker) and leaving every other alias on the story master's references in the new cell. `TLM_MQ02A` stays one record in the story master. Pritchard is read through `TLM_MQ01`'s own alias, as Greenwater reads him; no actor of the test room is bound.

Routing: every piece reports to `TLM:NightMailWalk` through `TLM:NightMailTalk` (activation, entering a box, death, combat). Pritchard keeps his one listener: the rail report, the stamp's receipt and its aftermath are offered from inside `TLM:Act1Walk`'s existing conversation, after the river report and before the briefing, each answering one of the four words Greenwater's report already answers (nothing offered / given / explicitly later / closed).

### Stages of `TLM_MQ02A`

The fifteen accepted stages, and native-only stages that carry the contract's neutral journal text where the accepted log would claim something that did not happen. A stage here is never read as "everything below it happened".

| Stage | Journal | Set when |
|---|---|---|
| 10 | accepted | arrival at the yard seen (player in the cell, at the gate marker) |
| 20 | accepted | Lockridge's assignment delivered and acknowledged, Lockridge alive, present, in no fight |
| 21 native | `You agreed to ride the Night Mail with the payroll and fever medicine.` | the labelled `Board the Night Mail` action, when no living Lockridge can assign |
| 30 | accepted | the departure confirmed on the footplate with Billie alive and present to drive |
| 31 native | `You boarded Old Contrary. The regulator is ready.` | the same without her |
| 40 | accepted | arrival at the Cut seen and the encounter's pieces seen on |
| 41 | accepted | the run's scene finished and seen (arrival, cargo delivered, engine damaged), Billie driving |
| 46 native | `The Night Mail got through. The medicine and payroll arrived; the engine is damaged.` | the same with the player at the regulator |
| 42 | accepted | Dole dead by the player's hand in the unresolved encounter, and each opponent dead or seen at its retreat marker out of the fight |
| 47 native | `Preacher Dole is dead. His death does not erase the yard's inspection records.` | Dole dead otherwise (in the encounter, or later) |
| 43 | accepted | the sale finished: 150 caps seen arrived, Billie alive and seen released, the cargo seen seized |
| 48 native | `You accepted Dole's share. The payroll and medicine were taken from the train.` | the same with no living Billie released |
| 44 | accepted | the reverse finished and seen (back at the yard, cargo retained), Billie driving |
| 49 native | `The train returned with its cargo undelivered. The obstruction at Sawtooth Cut remains.` | the same without her |
| 50 | accepted | the collection plate actually inspected |
| 51 native | `Dole described square-marked silver paying for pulled rails.` | his `dole_silver` delivered and answered |
| 55 | accepted | the flyleaf read through |
| 56 native | `Preacher Dole identified himself as Ostrander, Inspector of Way.` | his `dole_name` delivered and answered |
| 60 | accepted | the drawer actually opened, or a living Lockridge shown the real book opening it |
| 61 | accepted | `Keep stamping`, Lockridge alive, present, in no fight, the stamp seen still in the drawer |
| 62 | `Lockridge countersigned the reviewed entries in her own name. Suspect stock is held from dispatch.` | the countersigning scene finished and its board and held stock seen. The accepted log ("until morning") is not imported: no overnight clock is represented |
| 63 | accepted | the stamp seen in the player's inventory and gone from the drawer, with a living Lockridge there to watch |
| 64 native | `You took the inspector's stamp as evidence. It has not yet been delivered to Pritchard.` | the same without her |
| 100 | none; completes | the explicit departure for Mercy, seen arrived, with an encounter outcome recorded |

Objectives: the accepted 10, 20, 40, 55; and this build's own 70 (carry the mail forward or back, after Dole's defeat with the mail still aboard), 80 (leave for Mercy) and 90 (the stamp to Pritchard).

### Facts kept

Globals of the plugin, so that later quests and conditions can read them: `TLM_G_MQ02A_Outcome` (0, 41 run, 42 Dole defeated, 43 sold, 44 backed out), `_Mail` (0 aboard, 1 delivered, 2 retained at the yard, 3 seized), `_Engine` (0 sound, 1 run-damaged), `_Train` (0 yard, 1 Cut, 2 platform, 3 left to Dole), `_Dole` (0 not known dead, 1 dead by the player in the encounter, 2 dead otherwise), `_Stamp` (0, 61, 62, 63), `_StampDelivered`, `_YardAuthority` (0 held, 1 withdrawn, 2 vacant: she is dead), `_Reported`; and one each for the nine accepted flags `mail_through`, `mail_sold`, `line_closed`, `dole_lives`, `silver_rail`, `ostrander_known`, `lockridge_stamping`, `lockridge_signed`, `lockridge_reported`. Eighteen.

Script state, kept by a save: the exclusive claim, which scene is pending, the payment's and each one-time item's intent and acknowledgment, how each thing was learned, whether Dole was met, whether Billie's return and report were shown.

Projection decisions made here, for review:

- **`dole_lives`** is set when an outcome is recorded with Dole alive and he has seen the player (he was spoken to, or the train ran the gap past him), and cleared if he is later seen dead.
- **`lockridge_reported`** is `StampDelivered` and a yard with no master, acknowledged. With Lockridge alive that is the withdrawal scene (`_YardAuthority` 1). With Lockridge already dead no withdrawal is staged: the board is closed and the fact is recorded as `_YardAuthority` 2, a different number, and the flag is then set too, since both halves of its meaning are true. If review wants the flag held back in that case, it is one line.
- **Dole's coat** as a second place to find silver is not built. The collection plate is always reachable, before and after any death, so nothing waits on a body.

## 4. Scenes: requested is not done

Every staged scene is: a labelled notice with one button; then, only on that button, the player, the road's exclusive state and every marker and participant the scene needs asked for again; then the intent written; then the moves and the switched pieces; then a look at each (the player in the cell at the marker, each actor where it was sent, each piece on or off); and only then the record. A scene that is not seen stays pending under its own claim, excludes every other course, moves nobody back, pays nothing twice, and is finished from a control that is still usable. Nothing is rolled back by narration.

| Scene | Begun from | What is looked at before it is recorded |
|---|---|---|
| Travel to the yard | Mercy travel point | the destination marker is the placed marker of the Night Mail cell (identity, before the move; its 3D is not asked for); afterwards the player in that cell within reach of it |
| Departure | the footplate's departure control | player at the Cut's footplate marker; Billie there if she drives; the Cut's pieces on |
| Run | the regulator, or Billie's line | player at the platform; cargo delivered on, cargo aboard off, damaged engine on |
| Forward after defeat | the regulator | the same with the sound engine |
| Reverse / return | the reverser, or Billie's line | player at the yard footplate; cargo retained on |
| Sale | Dole's `Done.` | 150 caps counted in; Billie at her walking marker if she lives; cargo seized on, cargo aboard off |
| Defeat | Dole's death | each opponent dead, or out of the fight at its retreat marker |
| Billie's return and report | Lockridge, after a sale | a notice that it is the next morning by this scene's clock and no game time passes; Billie alive at the yard marker |
| Countersigning | `Sign your own name from now on.` | the countersigned board on, the stamped board off, the held stock on |
| Authority withdrawn | after Pritchard has the stamp | the closed board on and both other boards off; Lockridge's dispatch actions (the job, the stamp menu, the countersigning) stopped by that fact |
| Return to Mercy | an exit at the yard or the platform | player at the Mercy marker |

No moving train, no jump, no rotating office, no timer and no thirty riflemen are built or claimed. Three opponents with no names stand for them. Refusing the job, leaving unboarded, declining Dole or cancelling anything starts no fight and loses nothing.

## 5. Evidence: what is touched, what hears it, what is learned

Declared now, as the order asks, and not inferred from model flags.

| Evidence | The piece | The hook | What is learned | What is held |
|---|---|---|---|---|
| `yard_rules` | an activator at the gate | `NightMailTalk.OnActivate` → `NightMailWalk.Used` → its pages | nothing | nothing |
| `hymn_chalk` | an activator on the siding | the same | nothing | nothing |
| Silver, seen | the collection plate, an activator on the siding | the same → an inspection notice → on its button `LearnSilver(plate)` | `silver_rail`, stage 50 | nothing: the writing gives a label, not an item |
| Silver, told | Dole | `dole_silver` shown and answered with a button, Dole alive, present and in no fight after it → `LearnSilver(told)` | `silver_rail`, stage 51 | nothing |
| Identity, read | the hymnal, an activator on the siding | `OnActivate` → every page shown and answered → `LearnName(flyleaf)` | `ostrander_known`, stage 55 | the book `TLM_BOOK_HymnalFlyleaf`, asked for once and counted in |
| Identity, told | Dole | `dole_name` shown and answered → `LearnName(told)` | `ostrander_known`, stage 56 | **no book** |
| The book shown | Lockridge | used with the book counted in the player's inventory at that moment, Lockridge and Dole both alive, an explicit button | her `lockridge_hymnal`; then the drawer | the book stays with the player |
| The stamp, found | the drawer, an activator at her desk | `OnActivate` → a notice → on its button `FindStamp` | stage 60 | the stamp is in the drawer: the piece `StampInDrawer` is on |
| The stamp, taken | the explicit choice | `AddItem` once; acknowledged by the count rising **and** `StampInDrawer` seen off | decision 63 | `GetItemCount` of the stamp on the player, read whenever it matters |
| The stamp, delivered | Pritchard, an explicit button | `RemoveItem` to Pritchard; acknowledged by the player's count falling **and** his rising | `StampDelivered` | his inventory |

`OnRead`, `OnItemAdded` and `OnContainerChanged` are not used. Reading is page boxes, as the Greenwater letter is; custody is a count read at the moment of use, so a stamp dropped is not in custody and a stamp picked up again is, by the game's own pick-up, with no hook to miss. Knowledge does not depend on carrying anything. Only showing the book and handing over the stamp ask for the thing itself.

The surprised line (`He's ALIVE?`) is shown only for the real book, a living Lockridge and a living Dole, the first time. Hearing his name gives no book and shows no such line. With Dole dead the drawer and `lockridge_stamp` remain.

## 6. Records planned

Ids are given by the builder's allocator from 2383 upward and will be read back, not chosen. Editor ids:

- Quests `TLM_MQ02A`, `TLM_NM`. Cell `TLM_CELL_NightMail`.
- Actors, each a copy of the game's settler with no packages (development builds only): `TLM_NPC_YARDMASTER_IRONJUNCTION` (Augusta Lockridge), `TLM_NPC_DRIVER_NIGHTMAIL` (Wilhelmina Tupper), `TLM_NPC_PREACHER_BLACKRAIL` (Ezekiel Dole; one actor, one name on screen throughout), `TLM_NPC_BLACKRAIL_01` to `_03` (shown as "Black Rail rifle"; no names).
- Factions `TLM_Fac_IronJunction`, `TLM_Fac_BlackRail`.
- Book `TLM_BOOK_HymnalFlyleaf`. Item `TLM_MISC_OstranderStamp`.
- Activators and triggers `TLM_ACTI_NM_*`, `TLM_TRIG_NM_*`; messages `TLM_MSG_NM_*`; globals `TLM_G_MQ02A_*`.
- Placed references `TLM_REF_NM_*`: the two Mercy pieces in the game's test room for the development build; everything else, and the floor (`TLM_REF_NM_Floor_*`), in the new cell.

Aliases of `TLM_NM`: one for each placed piece. Aliases of `TLM_MQ02A`, filled by script: Lockridge, Billie, Dole, the three opponents, and the pieces objectives point at. Both lists will be given with their numbers from the build's read-back.

### The cell and its floor

Five labelled zones on three floors of the game's 256-unit floor tile (`workshop_ShackMidFloor01B`, the tile the exterior builder already stands a cabin on), laid at Z 0:

| Floor | Zones | Tiles (centres) |
|---|---|---|
| A | 1 the yard (gate, desk, drawer, boards); 2 the footplate as it stands in the yard | x 0 to 1024, y 0 to 512 |
| B | 3 Sawtooth Cut (the footplate as it stands there, the parley ground, Dole, the retreat path); 4 the boxcar tabernacle siding | x 3072 to 4608, y 0 to 512 |
| C | 5 the valley platform | x 6144 to 6656, y 0 to 512 |

Within a floor the zones are joined and walked between. Between floors there is nothing: the journey is a staged scene. A wide trigger box under all three sets a player who steps off an edge back at the zone's marker. People and markers stand 16 units above the tiles, activators 12, as the exterior's do above its ground. The exact coordinates of every piece will be in the ledger from the read-back. **Whether the tile's bounds are 256 square about its middle, whether a person stands on it in a cell of this plugin's, and that the cell has no navigation mesh (so nobody in it walks or takes cover of their own accord) are native unknowns, declared.**

## 7. Candidate text that changes

Availability text only; no speech. In this candidate's source: the Mercy briefing's hub, journal and footer, the first section's ending footer, Greenwater's travel and completion notices, the Night Mail's own, and the completed text of `TLM:Act1Guide`, to the strings the contract and the order give. The tests and the mapping that pin Greenwater's one-road strings will say why they changed.

## 8. Files this work intends to touch

New: `scripts/Source/User/TLM/MQ02AQuest.psc`, `NightMailWalk.psc`, `NightMailTalk.psc`; `tools/PluginBuilder/SpecNightMail.cs`; `tools/logic_model/night_mail_model.py` and its test; `tools/papyrus_sim/night_mail_player.py`, `test_night_mail*.py`; `tools/night_mail_story_candidate.py`, `tools/win/night-mail-story-candidate.json`, `tools/win/Build-NightMail.ps1`, `tools/win/tests/Test-NightMailPackageSafety.ps1`; `docs/design/NIGHT_MAIL_STORY_001_MAPPING.json` and `…_LEDGER.md`.

Changed: `Act1Walk.psc` (opens the travel point; routes the rail report), `Act1Guide.psc` (one string); `Spec.cs`, `SpecAct1.cs`, `SpecMercyBriefing.cs`, `SpecGreenwater.cs` (availability strings only), `Builder.cs` and its report and self-check (the own cell), `formkeys.txt` (appended), `last-build.report.txt`; `tools/StandInMaster/Program.cs` (the floor tile); `tools/WorldSliceBuilder/WorldStory.cs`, `StoryCloneCheck.cs`; the stand-in engine only if the new cell needs it; the earlier tests and mappings that pin the changed strings; `test_greenwater_candidate.py` (the 016b manifest becomes a frozen earlier one, checked on the 016b tree taken from Git, as a8's is); `tools/win/tests/Test-GreenwaterPackageSafety.ps1` (its expectation for this checkout: the frozen packager's exact refusal); `tools/README.md`.

Not touched: `MQ01Quest`, `SQ01Quest`, `MercyBriefing`, `MQ02BQuest`, `GreenwaterWalk`, `GreenwaterTalk`, `Core` and the other reviewed scripts; the accepted writing; the four earlier package manifests, the a8 manifest and its check, `greenwater-story-candidate.json`, `greenwater_story_candidate.py`, `Build-Greenwater.ps1`; the earlier packagers, stagers and launchers; the workflow; `game_runs.json`; `MatrixCases.psc`; `VERIFY_LOG.md`. `TLM_Core`'s scenario stays 0 and no QA helper is added.

## 9. Runtime provenance plan

- `016b2b4` is the immutable baseline. Its manifest, verifier, packager and their pins are not edited; their checks must refuse this checkout, and the tests will require that refusal and its reason.
- The composed candidate gets `tools/win/night-mail-story-candidate.json`, read by `tools/night_mail_story_candidate.py` (`verify`, `describe`, `measure`), and its own packager `tools/win/Build-NightMail.ps1`, which runs the full verifier before it creates or builds anything and fails closed, as the repaired Greenwater packager does. The number of scripts is counted from the checkout, not declared in advance.
- Selection: a compiled script is reused only where its source is still the reviewed text **and** its reviewed bytes are pinned in this repository; that is the Details runtime's. Every script changed or new since `016b2b4` is compiled afresh. The four scripts that `016b2b4` compiled afresh and that this work does not change (`MQ02BQuest`, `GreenwaterWalk`, `GreenwaterTalk`, `MercyBriefing`) have reviewed compiled files at root, but no digest of them is recorded here, so this manifest selects them from the fresh compile too and says that a later one may pin them.
- Every measured field stays empty until somebody builds on a licensed PC and measures. Nothing is compiled, built against the game's master or run here, and **no PowerShell can be run here**: the packager and its fixture will be written and their text checked, and said to be unrun.

## 10. What was done

To be completed when the work is finished.
