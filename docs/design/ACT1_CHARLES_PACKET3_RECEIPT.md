# Act I, packet 3: receipt from Claude Code ("Charles")

16 November 2026. Sections 1 to 6 were written and committed before any source or story file was changed. Results are added from section 7 on. **Nothing here is a compile, a game test or a claim that any quest is playable.**

## 1. What was received and read

| Item | Value | How it was checked |
|---|---|---|
| Integration commit | `4b77df4afb69680a24add28aebf52f96373cfd89` on `feat/act1-packet2-remote-checks` (draft PR 29) | Fetched. It is the tip of that branch |
| My packet 2 revision | `f1b045e917abe37d6c2b34efe0f7da22601434a8` | An ancestor, two commits back |
| Remote-check hook | `2b81cf1fe06f68dc3a480125b21eda520af57d66` | Between the two. Adds three lines to `tools/run_checks.sh` that run the v2 example, the fixtures and the focused check |
| Order | `docs/design/ACT1_CHARLES_PACKET3_ORDER.md` | Read in full |
| Repair review | `docs/design/ACT1_SOURCE_REPAIR_REVIEW.md` | Read in full |
| Packet 3 | `docs/design/ACT1_WRITING_CLOSURE_PACKET_3.json` | Read in full: 23 text replacements, 12 new lines, 6 routing instructions, 12 dispositions. SHA-256 computed here: `2955092d985afd5586f2eab9200d909fd5940a0e96a2a8a9533d6b1643a6f5d2`. Matches |
| Earlier packets and the contract | Primary packet `364bdaa0...`, addendum `50eeb710...`, packet 2 `f8166ead...`, contract `924ed1c3...` | All four unchanged |

What the integration commit changes since `f1b045e`, read as a diff:

- **`tools/story_intake_select.py`**: a line with no buttons now closes on its one implicit Continue instead of raising; a button index that is not a real index in range is refused.
- **`docs/design/ACT1_CHARLES_REVISION_CHECKS.py`**: both walks along the truce stop on a repeated line or after as many steps as there are lines; Brigg's reply is expected to carry the full resolved-context guard.
- **`assets/incoming/act1/story/talk/tlm_mq03.json`**: nine `when` lists only. The eight lines of the two truce chains and `brigg_rifles` now carry the whole context, not just their own speaker being alive. No id and no word changed.
- **`tools/test_story_intake_v2.py`**: seven tests added, 54 in all.
- `tools/run_checks.sh`, `.gitattributes`, the packet 2 entry ledger, and the three new documents.

**These were three real defects in what I returned at `f1b045e`.** A box with no buttons crashed the selector. The focused check could loop for ever on a chain that was legal but circular. And the truce could record stage 43 after one of its speakers had died or another course had been taken, because each line asked only whether its own speaker was alive. I had not tested any of the three.

Run here on the integration commit before changing anything: `python3 tools/test_story_intake_v2.py`, 54 tests, all pass; `python3 docs/design/ACT1_CHARLES_REVISION_CHECKS.py`, pass.

## 2. Branch

`feat/act1-charles-packet3-application`, created from the integration commit. Nothing is reset, discarded, force-pushed or merged. No other branch is changed.

## 3. Scope as I understand it

Apply packet 3 completely to the story folder, with exactly the routing it gives, and bring the source checks and tests up to it. Keep Sam's three repairs and their regressions.

Not in scope and not touched: the game, its scripts, the logic model, the builders, anything installed, saves, Chapter 5, the player's past or family, auth, providers, security settings, workers, the workflow, `tools/run_checks.sh`. The four earlier packets, the contract and the canonical decisions are not edited.

## 4. Precedence I am applying

Canonical decisions govern. For wording: the primary packet; the ballad addendum for its two subjects; packet 2 for what it names; packet 3 for exactly the fields and routing it names. The focused check will expect the latest supplier's value for each node and print every pair where one packet replaces another.

## 5. Rules I am applying to myself

1. Supplied prose is applied character for character. No story text is written by me.
2. The full-quorum truce is a KEEP. I will not return it as missing writing.
3. No new action, flag setter, "or" or condition on a single button. Where a button must be absent in some states, the whole line is copied.
4. Stage 43 is recorded in one place only: the Continue under Brigg's own concession. The two local officers' buttons carry no effect.
5. Every line that offers a courier course or carries the truce asks that the fair's quest is not complete (stage 100), as well as the guards it already has.
6. `entry` and priority for each new line are assigned by me, written into the ledger with a reason, and no unrelated number is moved.
7. Sam's three repairs stay as they are. Tests are added, and expected chains and words updated; none is removed or loosened.
8. Where the format cannot express something, it is returned as a runtime gate. Nothing is invented to cover it.

## 6. Found before starting

- All 57 strings in packet 3 pass the checker's rules for text (length, ASCII, the six words Act I may not use). The reworded `whitcomb_rates` is among them, so the line withheld at `f1b045e` can now be applied and its exception in the focused check removed.
- `talk/tlm_mq03.json` at the integration commit is no longer laid out the way the other talk files are (the repair wrote it with different spacing). It will be written back in the common layout, so its diff will show formatting as well as content. The node-by-node ledger compares parsed content and is not affected.

Intended changes, by area:

| Area | Intended change |
|---|---|
| `talk/tlm_mq02.json` | The common open-roads text on seven lines, each with the new report link; the dispatcher and three neutral leaves; six replaced report texts |
| `talk/tlm_mq02b.json`, `tlm_mq02c.json`, `tlm_mq04.json` | `pruitt_ran`, `roark_deadline_warning`, `pritchard_after_rope`: supplied text; a living-speaker guard on the first and third |
| `talk/tlm_mq03.json` | `whitcomb_rates`; Brigg's two concession lines, with stage 43 moved onto them; `mq03 notdone 100` on every courier and truce source; the living and dead courier split on Brigg's six menus; six fallback menus for a dead Brigg; the dissent buttons moved before "(Move on)"; `threefords_dying` only while she lives |
| `quests/tlm_mq02b.json`, `tlm_mq03.json` | Five supplied consequence and journal texts |
| `characters.json` | Pritchard's first `knows` entry |
| `docs/design/ACT1_CHARLES_REVISION_CHECKS.py` | Packet 3 in the order of precedence; the new chain; the new guards; the withheld exception removed |
| `tools/test_story_intake_v2.py` | The histories the order lists, added to the 54 |
| Ledgers | A complete final entry ledger and a node-by-node change ledger against the integration commit |
