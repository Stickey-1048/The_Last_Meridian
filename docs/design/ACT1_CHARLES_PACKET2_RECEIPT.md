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
