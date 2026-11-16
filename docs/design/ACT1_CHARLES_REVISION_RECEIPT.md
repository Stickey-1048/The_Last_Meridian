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

## 6. Next action

Apply the above, validate, then complete sections 7 to 9 of this file and add the node-by-node change record. Handoff after that is Charles to Maya, Iris and Nora.
