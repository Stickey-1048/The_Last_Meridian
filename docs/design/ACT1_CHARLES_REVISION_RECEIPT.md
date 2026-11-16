# Act I revision: receipt from Claude Code ("Charles")

16 November 2026. Written before any revision was made, then completed with results (section 6 onward). This is a record of what was read and what is intended. **Nothing here is a compile, a game test or a claim that any chapter is playable.**

## 1. What was received and read

| Item | Value | How it was checked |
|---|---|---|
| Decision commit | `4234ff2aa04caf6e671724ea894058e4dd6aad13` on `feat/act1-creative-decisions` (draft PR 27) | Fetched. It is the tip of that branch |
| Source proposal | `6f21643ec36c1e0511dadd59e28e5ea3b4552a82` on `claude/gracious-lamport-ggrwzp` | It is the direct parent of the decision commit |
| What the decision commit changes | Nine files, 387 lines added, none removed | `git diff --stat 6f21643 4234ff2` |
| Primary packet | `docs/design/ACT1_APPROVED_TEXT_REVISIONS_2026-11-16.json` | SHA-256 computed here: `364bdaa09fab8658cb99d0ff4eeffcf5db98767d465a0e427b1957ba5f4f2c5a`. Matches the hash given |
| Ballad and Flint addendum | `docs/design/ACT1_BALLAD_ADDENDUM_2026-11-16.json` | SHA-256 computed here: `50eeb71025b8cceac6d9d6e5f79656239406fd7a856f2343c94ee83953202cff`. Matches the hash given |

Read in full at that commit: `docs/design/ACT1_CHARLES_CREATIVE_HANDOFF.md`; `docs/design/ACT1_CREATIVE_DECISIONS_2026-11-16.md` (the five governing decisions, all 24 answers, the agency, naming and handoff sections); both packets; the additions to `CANON.md` and `docs/naming-registry.md`; and the three notes added to `assets/incoming/act1/story/` (`OVERVIEW.md`, `QUESTIONS_FOR_OWNER.md`, `README.md`).

The decision commit left the story JSON itself untouched: `characters.json`, `documents.json`, `quests/` and `talk/` are byte-for-byte the proposal's.

## 2. Branch

`feat/act1-charles-intake-revision`, created from the decision commit. Nothing was reset, discarded or force-pushed. The proposal branch and the decision branch are not changed by this work.

## 3. What I understand the work to be

A revision of the writing intake under `assets/incoming/act1/story/` and its review records. Not six gameplay quests, not Chapter 5, not the player's family, not the installed demo, not any script, logic model, plugin record or world package.

I do not re-decide any creative question. Where the packets supply wording I use it exactly. Where a change needs prose the packets do not supply, I do not write it: the node is listed in section 8 for Iris.

## 4. Rules I am applying to myself

1. **Supplied text is applied verbatim**, with the addendum overriding the primary packet for the ballads and `flint_who` only.
2. **Machine IDs do not change**: character ids, line ids, evidence ids, document ids, flag names, stage numbers. Stage 30 of `mq03` and stage 70 of `mq02` are removed as instructed; nothing is renumbered.
3. **Derived wording** is allowed only in fields that describe mechanics or design intent to a reader of the file (`set_by`, `now`, `later`, flag meanings, `cannot_break`, `ways_through`, `open_questions`, a character's `role`), and only by restating words the decisions or packets already use. Every such field is marked DERIVED in the change record so that it can be checked or replaced.
4. **Subtractive edits** (deleting a clause, a list entry or a name the decisions retire) are treated as mechanical.
5. **Player-facing text the decisions contradict but the packets do not replace** is handled one of two ways, and each case is listed:
   - a leaf line nothing links to is removed, pending replacement text;
   - a structural node that cannot be removed without breaking the quest is left as written and flagged as UNREVISED.
6. **The format is not extended.** Conditions stay AND-only; an "or" is two lines.

## 5. Intended changes, by file

| File | Intended change |
|---|---|
| `characters.json` | Four display names (Tupper, Blevins, Rafferty, Beckett); the twelve field replacements in the packet; Pike's secret; the 2298 date; removal of recognition and foreknowledge entries in Grey, Voss, Flint and Quill metadata; surname propagation in ties and notes |
| `talk/tlm_mq02.json` | `pritchard_sends_talbot` and its incoming button; removal of the Talbot-injury lines; the three roads kept available after a refusal |
| `talk/tlm_mq02a.json` | Surname propagation only |
| `talk/tlm_mq02b.json` | `pruitt_chain` (text and button) and `pruitt_burned`; surname propagation |
| `talk/tlm_mq02c.json` | `dunmore_tells`, `cutter_rope`, the three Dorn lines and their buttons; the 2298 challenge made conditional on evidence, with Quill's supplied response; the seal order relabelled and offered only once the knocking has been heard; Roark's two distinct aftermath lines; surname propagation |
| `talk/tlm_mq03.json` | Removal of the four Voss nodes; the Grey, Flint, Belden and Brigg replacements; `flint_who` from the addendum; button relabel into `flint_hat` |
| `talk/tlm_mq04.json` | Surname propagation only |
| `talk/town.json` | Removal of the Talbot-injury aside; ballad cries routed by actual Chapter 1 outcome; surname propagation |
| `documents.json` | The ballad replaced whole by the three supplied sheets, with routing; H.G. to H.B.; the incidental named fiddler and widow reduced to roles |
| `quests/tlm_mq02.json` | Stage 50 as the fair-without-report path; stage 70 and `talbot_shot` removed; `cannot_break` from the supplied contract |
| `quests/tlm_mq02a.json`, `tlm_mq02b.json` | No automatic bad outcome for a road left alone; the honest burn label and flag meaning; surname propagation |
| `quests/tlm_mq02c.json` | Supplied stage 15 and stage 51 logs; `hollow_line` meaning; the seal label; a separate fact for an expired, warned local deadline; a fact for holding the 2298 docket |
| `quests/tlm_mq03.json` | Supplied premise, stage 41 log, choice and flag meaning; stage 30 removed; courier scene armed only with the player present |
| `quests/tlm_mq04.json` | Surname propagation; removal of the claim that all four payments ran every month for six years |
| `OVERVIEW.md`, `QUESTIONS_FOR_OWNER.md`, `README.md`, `../PROVENANCE.md` | Brought into line with the adopted decisions; the proposal's own text stays in Git history |

Sections 1 to 5 above were committed as `b3bf874` before any story file was changed. What follows was added afterwards.

## 6. What was done

196 nodes changed. Every one is listed with its text before and after in [ACT1_CHARLES_REVISION_CHANGES.md](ACT1_CHARLES_REVISION_CHANGES.md).

| Kind | Changes | What it means |
|---|---|---|
| SUPPLIED | 64 | The new value is, character for character, a string from a packet |
| WIRING | 42 | A condition, a button's effect or link, a `reads` or `set_by` entry, or a node added to carry one |
| NAME | 38 | Only an approved surname or initial differs |
| DERIVED | 22 | Wording not in a packet, in a field no player reads, restating the decisions. **Each needs a second reader** |
| REMOVED | 15 | 13 nodes gone; 2 journal entries blanked |
| SUBTRACTIVE | 6 | Words taken out, none put in |
| RECORD | 6 | Each quest file's own list of open questions, brought up to date |
| DATE | 3 | The year written as 2298 |

Removed, 13 nodes:

- The four face-to-face lines at the fair (`voss_default`, `voss_line`, `voss_know`, `voss_beef`) and stage 30 of `mq03`.
- The refusal punishment: stage 70 and objective 70 of `mq02`, the flag `talbot_shot`, and the lines `pritchard_talbot_back`, `talbot_sent` and `keene_talbot_aside`.
- `quill_unmoved`: it was the failed-check reply to a check that no longer exists.
- `pritchard_quill_aside`: it said Quill sent Pritchard a line that the player carried. Under the supplied reply she sends none. No replacement was supplied.

Added to carry the approved contracts, with no new story text:

| Node | Why |
|---|---|
| `pritchard_three_tokens_later` | "The roads are still there if you change your mind" has to be true after the fair is called. Reuses the existing text of `pritchard_three_tokens` |
| `quill_court_docket` | The 2298 challenge is offered only with the docket in hand. The format has no condition on a single button, so the line exists twice |
| `greer_first_heard` | The seal order is offered only after the knocking has been heard. Same reason |
| `dunmore_freed_fine` | The debt line now plays only for a man actually freed (rope shot, or fine paid), not for one held for the adjourned hearing |
| `roark_after_deadline`, stage 56 of `mq02c` | The warned deadline running out is a different fact from an order to seal, and Roark says a different supplied line for each |
| `granger_ballad_missed` | The addendum routes "missed" to the same sheet as "evaded", by a separate binding |
| Flag `docket_2298_held`, evidence `docket_2298` | A place for the evidence the challenge needs. Marked NOT YET AUTHORED |
| Three ballad documents | One complete sheet per variant, and the common body for when no outcome is recorded |

Three conditions were tightened for outcome fidelity, beyond what the packets list:

- `vane_two_books_kind` now also needs `method is deal`. Its follow-on says the player "took a share", which is false when the caravan was shot at instead.
- `dunmore_rope` and `cutter_rope` now need `outcome isnot missed`. Both address the player as somebody met on the Tellico road.

No change was needed in `talk/tlm_mq02a.json`: the four surnames appear there only inside ids.

## 7. What was run

All on the final files, in the cloud session. **None of it is a compile or a game test.**

| Check | Result |
|---|---|
| SHA-256 of both packets | Match the hashes in the handoff |
| `python3 tools/check_story_intake.py --strict assets/incoming/act1/story` | Pass: 16 files, 30 characters known, 6 quest files, 161 lines of talk, 9 sources |
| `python3 docs/design/ACT1_CHARLES_REVISION_CHECKS.py` | Pass. It checks the folder against both packets: supplied wording exact at every keyed node; retired buttons, nodes, stages and the flag gone and unreferenced; stage numbers not renumbered; twelve character fields and Pike's secret exact; eleven display names; no old surname, initial or retired word left in any story JSON; supplied quest wording exact; the four ballad sheets exact and each outcome bound to its sheet; the docket gate, the knocking gate, the two Roark facts, and the fair opening on a refusal |
| The same script's reading list | Read by me: five places carry the inspector's legal name, all at or after the reveal; no recognition cue remains in what it flags |
| `python3 tools/check_story_intake.py --self-test docs/design/story_intake_example` | Pass, as before: 132 kinds of damage caught. The checker itself was not changed |
| `python3 tools/check_consistency.py` | No problems found |

Not run: `tools/run_checks.sh` to the end (this machine has no PowerShell; nothing it covers besides the story folder was touched); the Papyrus compiler; the game.

The checker's `--self-test` mode, pointed at this folder instead of at its worked example, reports one failure. That is how the self-test is built, not a fault in the folder: one of its deliberate damages assumes the first quest file is one the plugin already has.

## 8. Missing writing, returned to Iris

I wrote none of these. Each names the node and the field.

**Needed before a path can be reached or reads correctly**

1. **The 2298 docket.** `quests/tlm_mq02c.json`, evidence `docket_2298`, field `found`: where the player learns of the spring 2298 hanging and gets the docket. A `documents.json` entry for the docket itself. Which event sets the flag `docket_2298_held`. Until these exist `quill_court_docket` cannot play and stage 13 cannot be set.
2. **Three journal entries** (a stage's `log`, at most 240 characters): `mq02` stage 50 (the fair called without a report); `mq02c` stage 13 (the adjournment); `mq02c` stage 56 (the deadline ran out). The first two were blanked because the old text is now false.
3. **Standing in front of the rifles.** `quests/tlm_mq03.json` stage 43 (`log`, and the choice's `label`, `now`, `later`) and `talk/tlm_mq03.json` `brigg_rifles` (`text`) are UNREVISED and contradict decision 18. They cannot be removed without losing one of the four courses at the shot.
4. **Brigg's visible demand.** The supplied rule says his demand and the chance to intervene must be shown before stage 70. No line makes the demand.
5. **A road reported after the fair is called.** `pritchard_hears_rail`, `_river` and `_pike` now play only before the fair, because their follow-on calls it. Nothing is said for a road finished afterwards.
6. **The condemned man when the player never met the Cutters.** `dunmore_rope` and `cutter_rope` need a variant for `outcome is missed`. Without one he has nothing to say in that case; the clerk's paper still gives stage 15.

**To confirm or replace**

7. **The ballad cries.** `granger_ballad_saved`, `_walked`, `_missed`, `_deal` now each speak the first two lines of their sheet's ending. That is supplied text put to a use the addendum does not spell out. The hawker's own patter was dropped.
8. **The exploited sheet after a betrayal.** The addendum sends every exploited outcome to the sheet about counting and trading. When `method is betrayal` there was no trade.
9. **The deadline's warning.** Stage 30's journal entry and Blevins both say the charges fire at dawn. Is that the "clearly warned" wording, or is more wanted?
10. **`dorn_terms`, middle button**: "I can't swear for a whole town." is unchanged. In the new text she no longer asks for that.
11. **`belden_default`**: "You'll take a bowl. We insist." sits beside the new "Take a bowl if you want; supper isn't a signature."
12. **`pike_mould_aside`**: "a mould I ought never to have cut", said about the silver case. Decision 9 separates the mould from the case.
13. **`mq04`**: whether "(Step aside)" is explicit enough for a choice that allows an execution; and that the town hangs Vane if the player never comes to the porch. No contract for this chapter was supplied and both are as first written.
14. **`gantt_dispatch`**: Gantt writes "I have a name". Decision 6 says the dispatch proves no payer. It does not prove one, but it claims one.

**Character notes the packet did not replace, which may be out of step**

15. `belden`: `secret` (the stores are a third of what he says; "the soup is the offer"), `wants`, `wrong_about`, against decision 17.
16. `voss`: `role` is DERIVED. `fears` ("asked to do it again, to somebody he liked") and the tie to Flint ("leaves her a cartridge case each time, out of respect") are unchanged; the first may read as a cue, the second sits oddly with the new `flint_roof`.
17. `pike`: the first entry of `knows` is DERIVED from the supplied secret. Her tie to Voss ("Made his mould") is unchanged.
18. Two list entries were deleted as cues without replacement: Flint's "Whether the stranger is on his side or hers" and Quill's "That the stranger at her wagon is the one the Cutters were waiting for".

**Asked for by the decisions, with nothing supplied to apply**

19. Decision 15: a human purpose and voice for Juno. She still has two lines.
20. The registry's "Captain Blevins" and "Delegate Belden" on first return in a crowded scene. No supplied line uses either.
21. Decision 19: internal disagreement inside each faction. Each speaker now names a cost; none voices a dissenter.
22. `mq02b`: the sale of the grain still ends with Greenwater signing "whatever he puts in front of it" (`later` of the fourth choice, `hatcher_share`, `nell_soup_aside`), against decision 17's reading of the relief as real.

## 9. Engineering gaps

None of these is solved by this revision.

1. **No condition on a single button.** Three lines exist twice for that reason. A person editing one copy must edit the other.
2. **Lines that tie.** A follow-on line has no condition and priority 0, and so does a speaker's default. Nineteen speakers have more than one such line and the format gives no order between them. The worked example has the same shape. `STORY_INTAKE.md` needs a rule, for instance that a line reached only by `then` is never a greeting.
3. **Flags have no setter the check can read.** 23 of the 40 flags are declared and never read in this folder. `docket_2298_held` has nothing that sets it.
4. **`pritchard_three_tokens_later`** is offered after the fair even when all three roads are done. Saying "at least one is not done" needs an "or".
5. **The local deadline** (stage 56) is described in prose only: armed at stage 30, not counted in menus or while unloaded, never set by the fair. It needs a design and a native test.
6. **Feasibility gates** from decisions 20 to 22 are untouched: the duel, the moving engine and the jump, the rope shot, a crowd.
7. **A delegate attacked or killed at the fair** has no fallback. The supplied rule rules out blanket immunity.
8. **Ids carry retired spellings** by instruction (`greer_first`, `pruitt_chain`, `vickers_door`, `ballad_six_rounds`). Anyone searching for a retired surname will find them.
9. **The research rows** are unverified search summaries (decision 14).

## 10. Files

Changed: `assets/incoming/act1/PROVENANCE.md`; under `assets/incoming/act1/story/`: `OVERVIEW.md`, `QUESTIONS_FOR_OWNER.md`, `README.md`, `characters.json`, `documents.json`, `quests/tlm_mq02.json`, `tlm_mq02a.json`, `tlm_mq02b.json`, `tlm_mq02c.json`, `tlm_mq03.json`, `tlm_mq04.json`, `talk/tlm_mq02.json`, `tlm_mq02b.json`, `tlm_mq02c.json`, `tlm_mq03.json`, `tlm_mq04.json`, `town.json`.

Added: `docs/design/ACT1_CHARLES_REVISION_RECEIPT.md` (this file), `docs/design/ACT1_CHARLES_REVISION_CHANGES.md`, `docs/design/ACT1_CHARLES_REVISION_CHECKS.py`.

Not changed: `CANON.md`, `docs/naming-registry.md`, both packets, the decision amendment, the handoff, `RESEARCH.md`, `talk/tlm_mq02a.json`, every script, the logic model, the plugin builder, the world packages, and anything installed.

## 11. Handoff

Charles to Maya, Iris and Nora. The package is a revised proposal. It is not accepted, and it is not a playable chapter. The branch and commit are in the delivery message and in `git log`.
