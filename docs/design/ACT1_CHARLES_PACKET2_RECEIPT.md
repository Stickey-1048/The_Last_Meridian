# Act I, packet 2 and the conversation-entry format: receipt from Claude Code ("Charles")

16 November 2026. Sections 1 to 6 were written and committed before any source or story file was changed. Results are added from section 7 on. **Nothing here is a compile, a game test or a claim that any chapter is playable.**

## 1. What was received and read

| Item | Value | How it was checked |
|---|---|---|
| Follow-up commit | `495de2a6246e168672e738b5cd8dd2310f7cbb6f` on `feat/act1-charles-reviewed-revision` (draft PR 28) | Fetched. It is the tip of that branch |
| My earlier revision | `975a26252322c6d4acac8086d0a85a2eef386409` | An ancestor of the follow-up commit, two commits back |
| Line-ending repair | `1f605dedad451989c47a0a72db5cd3ade2630698` | Between the two; adds `.gitattributes` rules for the frozen packets |
| Canonical decisions | `4234ff2aa04caf6e671724ea894058e4dd6aad13` | An ancestor; `ACT1_CREATIVE_DECISIONS_2026-11-16.md` read again, with its one added paragraph |
| What the follow-up commit changes since `975a262` | Five files, 797 lines added, none removed: `.gitattributes`, the order, the contract, packet 2, one paragraph in the decisions | `git diff --stat 975a262 495de2a` |
| Order | `docs/design/ACT1_CHARLES_PACKET2_ORDER.md` | Read in full |
| Contract | `docs/design/ACT1_ENTRY_SELECTION_CONTRACT.md` | Read in full. SHA-256 computed here: `924ed1c382e13425800630c14d2cec8a002f8027996c63968478147bf5957148`. Matches |
| Packet 2 | `docs/design/ACT1_WRITING_CLOSURE_PACKET_2.json` | Read in full, every section. SHA-256 computed here: `f8166ead0b59050aec88a29b88be88244556cc3784c4c32189d503df0adb5a10`. Matches |
| Primary packet | `docs/design/ACT1_APPROVED_TEXT_REVISIONS_2026-11-16.json` | Unchanged: `364bdaa0...f2c5a` |
| Ballad addendum | `docs/design/ACT1_BALLAD_ADDENDUM_2026-11-16.json` | Unchanged: `50eeb710...2cff` |

The story folder at the follow-up commit is byte-for-byte my `975a262` revision.

## 2. Branch

`feat/act1-charles-packet2-entry-format`, created from the follow-up commit. Nothing is reset, discarded, force-pushed or merged. No other branch is changed.

## 3. Scope as I understand it

Two things, both source only:

1. **Apply packet 2's writing** to `assets/incoming/act1/story/`, exactly as supplied, with the wiring it asks for in the format as it actually is.
2. **Implement the contract**: the `tlm-talk-2` format with an explicit `entry` on every boxed line, the checker rules for it, a small reference selector, a separate v2 worked example, the fixtures the contract lists, and the migration of the revised talk files with a ledger.

Not in scope, and not touched: the game, its scripts, the logic model, the plugin and world builders, anything installed, saves, Chapter 5, the player's past or family, auth, providers, security settings, workers. The v1 worked example, the built `TLM_MQ01` and `TLM_SQ01` designs and the Papyrus stay as they are. The three frozen packets and the canonical decisions are not edited.

## 4. Precedence I am applying

Canonical decisions govern. Then, for wording: the primary packet; the ballad addendum for its two subjects; packet 2 for exactly the fields, choices and contracts it names. Everything packet 2 does not name is kept. Where packet 2 replaces a value an earlier packet supplied, the focused check will expect the successor and record the pair; no check is deleted and none is loosened to a substring search.

## 5. Rules I am applying to myself

1. Supplied prose is applied character for character.
2. No story text is written by me. Where the format forces a button with no supplied label, the only label used is the builder's own word, `Continue`, and each such button is listed.
3. No new action, no flag setter, no "or", no condition on a single button. Where a button must appear in some states and not others, the whole line is copied with AND-only conditions, and the copies are listed.
4. A new stage is defined only where packet 2 asks for one (stage 16 of `mq02c`). Nothing is renumbered.
5. `entry` is assigned to each line by me as the author of the migration and written into the ledger with its reason. It is not computed from links or names.
6. Priorities change only to make a speaker's greetings strictly ordered. Every old and new number is in the ledger.
7. Anything the supplied prose cannot express truthfully in this format goes back to Iris or Sam as a named gap. Nothing is invented to close it.

## 6. Found before starting

**One supplied line cannot be taken in as written.** `whitcomb_rates` in packet 2 reads "Signatory carriers vote on the charter rate." The intake rule for Act I refuses six words in every form, and "charter" is one of them (`docs/design/STORY_INTAKE.md`; `NOT_IN_ACT_ONE` in the checker). Packet 2's own validation covered length and ASCII only. I will not change Iris's words and I will not weaken the rule, so this line stays as it was at `975a262`, is recorded as WITHHELD, and is returned. Every other packet 2 string passes the checker's text rules (59 strings and the contract strings scanned).

Intended changes, by area:

| Area | Intended change |
|---|---|
| `tools/check_story_intake.py` | Accept `tlm-talk-2` beside `tlm-talk-1`; v1 behaviour unchanged; the v2 rules of the contract |
| `tools/story_intake_select.py` (new) | Dependency-free reference selector for greetings and button transitions |
| `tools/test_story_intake_v2.py` (new) | The contract's fixtures |
| `docs/design/STORY_INTAKE.md` | v1 rule kept and marked historical; v2 documented |
| `docs/design/story_intake_example_v2/` (new) | A small v2 worked example; the v1 example untouched |
| `assets/incoming/act1/story/talk/` | Migrated to v2; packet 2 lines, texts, buttons and conditions |
| `assets/incoming/act1/story/` other files | Packet 2 journals, documents, character fields, quest contracts |
| `docs/design/ACT1_CHARLES_REVISION_CHECKS.py` | Successor-aware expected values; the Dole and Quill histories; the v2 contract |
| Ledgers | Every node with its `entry`, priority and conditions; every changed value before and after; every KEEP |

Sections 1 to 6 above were committed as `f4f56d1` before any source or story file was changed. What follows was added afterwards.

## 7. What was done

**The format and its tools**

| File | What changed |
|---|---|
| `tools/check_story_intake.py` | Accepts `tlm-talk-2` beside `tlm-talk-1`. For the second format: `entry` is required on every boxed line and must be a real true or false; an aside may not carry it; a continuation has no priority; a speaker's entries have distinct priorities across the whole folder; a button may not lead to an aside; every continuation is reachable from an entry. A folder may not mix the two formats, and a first-format file with `entry` in it is refused. The checks of the first format, of text, of names, conditions and effects are as they were |
| `tools/story_intake_select.py` (new) | The reference selector: what a person says, and what a button does. It validates each condition with the check's own code before answering it. It refuses a first-format folder rather than guess |
| `tools/test_story_intake_v2.py` (new) | 47 tests: the contract's fixture table |
| `docs/design/STORY_INTAKE.md` | The first format's rule kept and marked as such; the second format documented |
| `docs/design/story_intake_example_v2/` (new) | The first example's talk in the second format. The first example is untouched |
| `tools/README.md` | Two rows for the two new files |

**The story folder**

- Talk is now `tlm-talk-2`: 209 lines, of which 117 are entries, 80 continuations and 12 asides. It was 161 lines.
- Every boxed line has an `entry` I assigned by hand from two written lists (21 defaults, 80 continuations; everything else boxed is an entry). 42 entries have a new or changed priority. All of it is in [the entry ledger](ACT1_CHARLES_PACKET2_ENTRY_LEDGER.md), speaker by speaker and line by line.
- 136 nodes changed besides: 57 supplied values, 51 nodes added, 16 changes of wiring, 6 derived fields, 5 lists of open questions, 1 removal. Each is in [the change ledger](ACT1_CHARLES_PACKET2_CHANGES.md) with its text before and after.
- The five guarded targets the contract names (`tarrow_in_cut`, `dole_sermon`, `tarrow_ran`, `tarrow_backed`, `hatcher_table`) are entries and still button targets. `brigg_rifles` is a sixth of the same kind.
- `dole_name` has no guard on stage 55. `quill_shamed` is a continuation guarded by `mq02c done 13`.

**Where one line became several**, because a button must be there in some states and not others and the format has no condition on a button and no "or":

| Lines | Copies | Split on |
|---|---|---|
| The three road reports before the fair | 2 each | Whether that road's payment evidence was learned. The claim button is on the known copy only |
| `pritchard_three_tokens_later` | 7 | Which roads are still open. Each copy offers only those |
| The report menu after the fair | 8 | The three evidence flags. Each button leads to the known or the unknown text |
| The six report texts after the fair | 1 each | Guarded by the evidence each speaks of |
| `brigg_demand` | 6 | Who is alive to speak for the truce |
| The truce as spoken | 2 chains | Pritchard, or Talbot when Pritchard is dead |
| `belden_greenwater_relief` | 2 | After the grain is sold; after the fire |

**Buttons with a label of mine.** Nine, all the single word `Continue`, which is what the builder shows on a box with nothing to choose: one on `pritchard_road_pike`, so that the new question about Quill is not the only way out of the box, and eight that carry the truce from one speaker to the next.

**Withheld.** `whitcomb_rates`: packet 2's text is not applied (section 6). The line is as it was at `975a262`.

## 8. Packet 2, item by item

| # | Request | What I did |
|---|---|---|
| 1 | The 2298 docket | APPLIED. The document, `pritchard_docket_context` reached by "What should I ask Quill?", stage 16, the evidence entry and the flag's meaning. The challenge still asks for the flag, not the stage. Two mappings open (section 11) |
| 2 | Journal entries | APPLIED. All eight supplied entries, exactly |
| 3 | The rifles | APPLIED. Label, both consequence texts, journal entry, `set_by`, Brigg's reply. The quest file no longer says the request itself sets stage 43 |
| 4 | Brigg's demand | APPLIED as a line of his that carries the four courses. Putting it on screen is open (section 11) |
| 5 | Reports after the fair | APPLIED: six texts, eight menus. One thing open: how the menu and the open roads share his greeting (section 10) |
| 6 | The condemned man, never met | APPLIED. Both lines, bound to `outcome is missed` |
| 7 | Granger's cries | APPLIED. The supplied patter replaces the lines I had quoted from the sheets |
| 8 | Betrayal | APPLIED. The sheet, the cry, and the trading sheet and cry bound to a deal |
| 9 | The mine's warning | APPLIED. Only the two confirming buttons on `roark_deadline_warning` set stage 30. Roark's other buttons no longer do |
| 10 | Dorn's middle button | APPLIED |
| 11 | `belden_default` | APPLIED |
| 12 | Pike's aside | APPLIED |
| 13 | The porch | APPLIED. Label, both texts, `set_by`, and the rule against a hanging by absence |
| 14 | The dispatch | APPLIED. Both paragraphs |
| 15 | Belden's notes | APPLIED |
| 16 | Voss's notes | APPLIED, with Flint's two |
| 17 | Pike's notes | APPLIED |
| 18 | The two deleted entries | KEPT deleted. The check now fails if either comes back |
| 19 | Juno | APPLIED: her default and her role. The staging is open |
| 20 | Captain Blevins, Delegate Belden | APPLIED through the supplied lines that use them. Nothing added |
| 21 | Dissent | APPLIED for the Commonwealth, the Dominion and the Directorate, and `whitcomb_big`. `whitcomb_rates` WITHHELD |
| 22 | The grain sale | APPLIED |

Nora's further corrections: road completion is not proof (APPLIED, the split reports); the dead pilot and the lost fraction (APPLIED in the journal and Starnes's reply; two places still say "a third", section 10); cut-then-burn (APPLIED: gone from every field); a hanging does not erase every witness (APPLIED); presence of the caravan (APPLIED for Starnes and Nell; the withheld Whitcomb line still says "Nell Fenwick yonder"); Vane's present-tense report of Reese (APPLIED).

The five KEEP decisions are kept: the quoted cries were acceptable and are now replaced by the supplied patter; Gantt's lead stays a lead; the two entries stay deleted; Voss's role is the supplied one; no family detail is added.

## 9. What was run

On the final files, in the cloud session. **None of it is a compile or a game test, and none of it shows a playable quest, an inventory, a timer or a scene.**

| Check | Result |
|---|---|
| SHA-256 of the three packets and the contract (line endings as LF) | All four match |
| `python3 tools/check_story_intake.py --strict assets/incoming/act1/story` | Pass: 16 files, 6 quest files, 209 lines of talk |
| `python3 tools/check_story_intake.py --self-test docs/design/story_intake_example` | Pass, word for word as before: 132 kinds of damage caught, 21 sound folders passed. The five files of that example hash as they did at `495de2a` |
| `python3 tools/check_story_intake.py --strict --self-test docs/design/story_intake_example_v2` | Pass: 92 kinds of damage caught, 21 sound folders passed |
| `python3 tools/test_story_intake_v2.py` | 47 tests, all pass |
| `python3 docs/design/ACT1_CHARLES_REVISION_CHECKS.py` | Pass. 23 histories through the selector |
| `python3 tools/check_consistency.py` | No problems found |
| The focused check, against 16 deliberately damaged copies of the folder | All 16 refused, each for its own reason; the undamaged copy passes. Done by hand in this session; the damaged copies are not committed |

What the fixtures cover, against the contract's table: the first format and its self-test unchanged; missing `entry`; `entry` as a string, a number, null; `entry` on an aside; the first format with `entry`; mixed formats; a continuation with a priority; one priority twice for a speaker across two files, in either order; a missing target; an aside as target; a ring of continuations with no way in, and a ring with one; no eligible entry; equal top entries forced past the check; Dole's two histories; Quill's two, and a third where the copy was once taken and is not in hand; a guarded target that is also a greeting; a target whose conditions fail after the effects; a stale menu; reordered files and lines.

The focused check keeps every exact comparison it had and adds packet 2's. Two values now expect a successor: `flint_who` (primary packet, then the addendum) and `pruitt_chain` (primary packet, then packet 2). The withheld line is checked as withheld: the check fails if it carries packet 2's text, and fails if packet 2's text stops containing the barred word.

Not run: `tools/run_checks.sh` to the end (no PowerShell on this machine); the logic model's tests (nothing they cover was touched); the Papyrus compiler; the game.

The check's `--self-test` mode pointed at the story folder itself still reports one failure, as at `975a262` and for the same reason: one of its damages assumes the folder's first quest file is one the plugin already has.

## 10. Open: writing, returned to Iris and Nora

1. **`whitcomb_rates` cannot be taken in.** "Signatory carriers vote on the charter rate." uses a word no line of Act I may use. Until it is reworded the line still says "Nell Fenwick yonder", which assumes she is alive and present, and the Compact's dissent over rates is not in the package.
2. **The report menu and the open roads.** After the fair Pritchard has one greeting. The open roads are ordered above the report menu, so the menu is reached only when no road is left to take. One supplied button, of 48 characters or fewer, on the open-roads line would join them; every copy of that line has a free place for it. Or say that reports come first.
3. **The report menu offers all three roads** whether or not each was travelled, as packet 2 specifies (eight contexts, on evidence only). The texts read as if the player had been there.
4. **"Spike, scoop or tag. Pick one up off my desk."** is still what Pritchard says when only one or two roads are open. The buttons are right; the sentence names all three.
5. **A truce with a voice missing.** It is offered only when Whitcomb, Belden and Grey are alive and either Pritchard or Talbot is. With one of them dead the other three courses remain and the truce is absent. What a smaller truce sounds like is not written.
6. **Brigg dead.** There is then no order and nothing carries the three remaining courses. No speaker was supplied for that case and I did not choose one.
7. **"A third"** of the grain: `pruitt_ran` and the `later` text of the Chute choice still say it. Packet 2 took the fraction out of the journal and of Starnes's reply.
8. **`pritchard_after_rope`** still says "You stepped aside", which was the old button.
9. **`roark_deadline_warning`** is reached from Roark's own button, "Lower the cage. I'll go down." Its words treat Blevins's final warning as just given. Whether it should instead follow an audible call from him is a staging question.
10. **The three dissent buttons** are each the fourth button, after "(Move on)", as the wiring note says. They may read better third.
11. **`pritchard.knows`** still has "Gantt was bringing him a name and would not put it on paper", beside the revised dispatch.
12. **The nine `Continue` buttons** (section 7) are mine to the extent of one word. Confirm or supply.

## 11. Open: runtime mappings and engineering, returned to Sam

Nothing below is implemented or claimed.

1. **Nothing in the format sets a flag.** Twenty flags are read by conditions in this folder. Each needs a mapping in the game. In particular `docket_2298_held` must follow what the player is carrying now, and the four `silver_` flags mean something learned, which may be spoken and need not be a paper.
2. **The review copy.** Stage 16 is set by a button at Pritchard's desk, in the hub's talk, for a quest that may not have begun. The copy "lies in the open on his desk": handing over a document is not something this format does.
3. **Presence.** A condition can ask whether a person is alive. It cannot ask whether they are on the camp-ground or in Greenwater. Every "living and present" in packet 2 is wired as living only.
4. **Brigg's order on the screen.** A boxed line is said when its speaker is spoken to. Putting `brigg_demand` up after the shot, before anything else can be chosen, needs a scene. Stage 70 has no setter in source at all.
5. **Stage 43** is set by the last `Continue` in the truce, on the way into Brigg's reply, because a line cannot do anything by being said. The reply is guarded by 43.
6. **The local deadline** (stage 56): when it starts counting, the visible final call, what a countdown looks like, that it stops in menus and when unloaded, and a living Captain. No number of minutes is given anywhere.
7. **Asides** have conditions and no rule for when they are shown, as the contract leaves it.
8. **A bowl of soup, caps, a share of cargo**: promises in dialogue. No inventory or supply effect exists.
9. **The feasibility gates** of the decisions are untouched: the duel, the engine and the jump, the rope shot, the crowd, the fair.
10. **The selector is a stand-in.** A stage a button sets is noted and nothing more. It cannot show what a quest does next.
11. **The fixtures are not in `tools/run_checks.sh`** or the GitHub workflow. That file is outside the surface the contract lists, so I left it. One line would add them.
12. **Copies must be kept in step by hand**: 28 lines exist only as a copy of another line for a different context (25 made here, 3 from the first revision).
13. **Ids keep retired spellings** by instruction.

## 12. Files

Changed: `tools/check_story_intake.py`, `tools/README.md`, `docs/design/STORY_INTAKE.md`, `docs/design/ACT1_CHARLES_REVISION_CHECKS.py`, `assets/incoming/act1/PROVENANCE.md`; under `assets/incoming/act1/story/`: `OVERVIEW.md`, `QUESTIONS_FOR_OWNER.md`, `README.md`, `characters.json`, `documents.json`, five of the six quest files (`tlm_mq02a.json` is untouched) and all seven talk files.

Added: `tools/story_intake_select.py`, `tools/test_story_intake_v2.py`, `docs/design/story_intake_example_v2/` (two files), `docs/design/ACT1_CHARLES_PACKET2_RECEIPT.md` (this file), `ACT1_CHARLES_PACKET2_ENTRY_LEDGER.md`, `ACT1_CHARLES_PACKET2_CHANGES.md`.

Not changed: the three packets, the contract, the order, the canonical decisions, `CANON.md`, the naming registry, the first worked example, the earlier receipt and its change record, `RESEARCH.md`, every Papyrus script, the logic model, the builders, `tools/run_checks.sh`, the workflow, and anything installed.

## 13. Handoff

Charles to Maya, Iris, Nora and Sam. A revised proposal in a new source format. Not accepted, not built, not playable. The branch and commit are in the delivery message and in `git log`.
