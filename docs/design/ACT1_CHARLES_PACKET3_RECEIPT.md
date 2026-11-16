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

Sections 1 to 6 above were committed as `0f8d5d2` before any source or story file was changed. What follows was added afterwards.

## 7. What was done

Packet 3 is applied in full. No supplied line is withheld and none is altered.

| Part of the packet | Applied as |
|---|---|
| 23 text replacements | All 23, character for character: 17 lines of talk, 5 quest fields, 1 character note |
| 12 new lines | All 12, whole: speaker, `entry`, conditions, text and buttons exactly as supplied. I added only a priority |
| Routing: open-road reports | The link "Discuss a road account." appended to all seven open-roads lines, after their road buttons. The eight evidence-split menus and their six leaves are kept |
| Routing: the truce | `pritchard_truce` and `talbot_truce` now lead, with no effect, to Brigg's concession for that officer. **Stage 43 is recorded in two places only, both Brigg's: the Continue under each concession** |
| Routing: Brigg dead | Six fallback menus, Pritchard, then Talbot, then Flint by who is alive, each in a living-courier and a dead-courier form |
| Routing: the courier | Brigg's six existing menus now ask for a living courier. Six copies ask for a dead one and have no button to stay with her. `threefords_dying` needs her alive |
| Routing: completion | `mq03 notdone 100` on all twelve of Brigg's menus and all eight lines of the two truce chains. The supplied concessions and fallbacks already carry it |
| Routing: fidelity | `pruitt_ran` only from a living Rafferty; `pritchard_after_rope` only from a living Pritchard after the chosen hanging |
| Routing: dissent order | On `belden_offer`, `brigg_offer` and `grey_offer` the dissent question is third and "(Move on)" last |

Talk is now 227 lines: 129 entries, 86 continuations, 12 asides. It was 209. Seventy-four nodes changed: 23 supplied values, 18 lines added, 29 changes of conditions or buttons, 4 lists of open questions. Each is in [the change ledger](ACT1_CHARLES_PACKET3_CHANGES.md). Every line's `entry`, priority and conditions are in [the complete entry ledger](ACT1_CHARLES_PACKET3_ENTRY_LEDGER.md), which replaces the packet 2 ledger as the current one.

**Priorities.** No existing number was changed. Twelve are new:

| Lines | Priority | Why |
|---|---|---|
| Pritchard's two fallbacks | 75, 74 | Above anything else he would say while the courier's fate is open (66 at most), below the porch at 85 |
| Talbot's two | 75, 74 | Above his only other conditional greeting (30) |
| Flint's two | 75, 74 | Above her lines at the shooting match (50, 60), below the roof at 80 |
| Brigg's six dead-courier menus | 59 to 54 | Directly under his six living-courier menus at 65 to 60, which keep their numbers |

**Sam's three repairs are kept as they were**: the selector's implicit Continue and index check, the bounded walks in the focused check with their two messages, and the full guards on the truce. His seven tests are kept; one had its expected result updated, because the officer's button now leads to the concession and no longer records 43.

**Checks and tests brought up to packet 3**

- `docs/design/ACT1_CHARLES_REVISION_CHECKS.py`: packet 3's hash; packet 3 last in the order of precedence; each of the 12 new lines compared whole with the packet; a check that every one of the 23 replacements is looked at by something; the open-roads link; the chain through the concession; the twelve menus and six fallbacks; completion; the living only. The exception that held `whitcomb_rates` back is removed, and the line is now expected to be packet 3's. Ten more histories.
- `tools/test_story_intake_v2.py`: 20 tests added, 74 in all.

**A defect of my own, found and fixed before returning.** While trying the focused check against damaged copies of the folder, one copy made it crash instead of report: a walk I had just extended read the next line's name without asking whether there was a next line. That is the same kind of fault Sam found last time. It is fixed, and the same damaged copy now produces a report.

## 8. Packet 3, item by item

| # | Disposition | What I did |
|---|---|---|
| 1 | REPLACE `whitcomb_rates` | APPLIED. The line no longer says "yonder" and the check fails if it does |
| 2 | ADD the report link | APPLIED to all seven, with the dispatcher and three leaves. None has an effect or asks for evidence |
| 3 | REPLACE six report texts | APPLIED |
| 4 | REPLACE the open-roads header | APPLIED to all seven |
| 5 | KEEP the full-quorum truce | KEPT. Not returned as a question. The quest file records it as a decision |
| 6 | ADD fallbacks, with a return gate | APPLIED. The gate is in section 10 |
| 7 | REPLACE the fraction | APPLIED: Rafferty's line and the consequence text. The pilot rule stays in `cannot_break` as the packet says |
| 8 | REPLACE the rope reply | APPLIED, with the living-Pritchard guard |
| 9 | REPLACE Roark's warning, with a runtime gate | APPLIED. Stage 30 is still set only by her two confirming buttons |
| 10 | REORDER dissent | APPLIED |
| 11 | REPLACE Pritchard's note | APPLIED |
| 12 | KEEP the `Continue` labels and repair the flow | KEPT and APPLIED. Eleven such buttons now: the nine, and the two under the concessions |

## 9. What was run

On the final files, in the cloud session. **Source checks and a stand-in selector. Not a compile, not a game test, and no proof of a playable quest, an inventory, a scene or a timer.**

| Check | Result |
|---|---|
| SHA-256 of the four packets and the contract (line endings as LF) | All five match |
| `python3 tools/check_story_intake.py --strict assets/incoming/act1/story` | Pass: 16 files, 6 quest files, 227 lines of talk |
| `python3 tools/check_story_intake.py --self-test docs/design/story_intake_example` | Pass, unchanged: 132 kinds of damage caught, 21 sound folders passed |
| `python3 tools/check_story_intake.py --strict --self-test docs/design/story_intake_example_v2` | Pass: 92 kinds of damage caught, 21 sound folders passed |
| `python3 tools/test_story_intake_v2.py` | 74 tests, all pass |
| `python3 docs/design/ACT1_CHARLES_REVISION_CHECKS.py` | Pass. 33 histories through the selector |
| `python3 tools/check_consistency.py`, `python3 tools/gen_matrix_cases.py --check` | No problems; 53 matrix cases as before |
| The focused check and the two story test classes against 20 damaged copies of the folder | The focused check refused all 20, each for its own reason, without crashing. The tests failed on 19; the twentieth, a character note put back, is a value only the focused check compares. The undamaged copy passes both. Done by hand in this session; the copies are not committed |

The four commands `tools/run_checks.sh` uses as hard gates for this source (its lines 46 and 49 to 51) were run exactly as written there and pass. **The script as a whole was not run here**: it stops earlier on this machine for want of PowerShell. The remote run on the pushed commit is the place it runs entire, and I have not seen that result.

What the 20 new tests cover, against the order:

- Both truce paths, with the courier alive and dead, reach Brigg's concession with stage 43 unset, show his supplied words, and record 43 only on the Continue beneath.
- At the concession: each of the five required people killed in turn, and each of 41, 42, 43, 44, 70 and 100 set in turn. No effect, no reply, no false acknowledgement afterwards.
- The same for every one of the ten lines of the two chains, and for every one of the eighteen course menus, each tried in a state built from its own conditions. A menu written for somebody dead is also tried with them alive.
- Every course menu does record its course while its conditions hold, and none records 43 or 70.
- Completion blocks every one of the 28 active courier and truce sources.
- A dead courier: no menu offers to stay; her last words cannot be said; exactly one carrier offers the courses in each cast tried.
- Brigg dead: Pritchard, then Talbot, then Flint; nobody else; no truce. All four dead: nobody, and nothing recorded.
- All seven open-road contexts, reached both by a refusal and by a report, with and without evidence flags: the right road buttons, the link, the dispatcher, three leaves, and no change to stages, flags or caps.
- Learned payment evidence against the review copy in hand; `whitcomb_rates`; no fraction and no dead pilot; the rope reply; the dissent order.

## 10. Runtime gates that remain

This source cannot express these. None is implemented or claimed, and none is a request for writing.

1. **The case when every carrier is dead.** With Brigg, Pritchard, Talbot and Flint dead, no line offers a course and none is taken. In source, stage 100 of the fair is then set only by Pritchard's reading of the case, and stage 60 has no source setter at all. How the player gets at the case is for the game.
2. **Presence.** A condition asks whether someone is alive, never whether they are there. Every fallback, every voice in the truce, Belden's wagon and Nell's aside are wired on life alone.
3. **Putting a line on the screen.** Brigg's order and each fallback menu are greetings: they are said when their speaker is spoken to. Showing one after the shot, before anything else can be chosen, needs a scene.
4. **Order and atomicity in the game.** In source the concession is read before its Continue records 43, and a failed target does not undo an effect. Whether the game shows the words before committing is not shown by anything here.
5. **Flags.** Nothing in the format sets one. Twenty are read. `docket_2298_held` must follow what is carried; the `silver_` flags mean something learned; `courier_heard` must follow the courier's words being delivered, not the choice to stay.
6. **The review copy.** Stage 16 is set from the hub's talk for a quest that may not have begun, and handing over a document is not something the format does.
7. **The mine.** A visible warning, the timer, its behaviour in menus and when unloaded, and a living Captain. No number of minutes exists.
8. **The occupation.** Stage 70 has no source setter.
9. **The Chute.** What is lost depends on the route and the pilot. Only the living-or-dead rule exists, in prose.
10. **Asides** have no rule for when they are shown. **Food, caps and cargo** are words. **The duel, the engine, the rope shot and the crowd** are untested ideas.

## 11. For the reviewers

Things I decided that the packet did not spell out:

1. **The six dead-courier menus** are copies named `<line>_courier_dead`. The six existing ids keep the living-courier form. Both forms of `brigg_demand` and `brigg_demand_talbot` keep the truce button.
2. **`brigg_rifles` does not ask `mq03 notdone 100`.** It has no button, so it is not a source, and the order says to keep its guards those of the committed state.
3. **`threefords_default` is unchanged.** Only `threefords_dying` was named for the living-courier guard.
4. **`talk/tlm_mq03.json` is written back in the layout of the other talk files**, so its diff is larger than its changes.
5. **One state the source cannot reach but does not exclude**: if stage 100 of the hub were ever set without 50 or 60, Pritchard would offer the first, pre-fair choice of roads again. No button here does that. I found it by setting a test up wrongly and did not add a guard nobody asked for.
6. **The flag `courier_heard`** still means "heard the courier's last words". Packet 3 says choosing to stay is not hearing; the flag's meaning already fits, and what sets it is gate 5.

## 12. Files

Changed: `docs/design/ACT1_CHARLES_REVISION_CHECKS.py`, `tools/test_story_intake_v2.py`, `tools/README.md`, `assets/incoming/act1/PROVENANCE.md`; under `assets/incoming/act1/story/`: `OVERVIEW.md`, `QUESTIONS_FOR_OWNER.md`, `README.md`, `characters.json`, four quest files (`tlm_mq02.json`, `tlm_mq02b.json`, `tlm_mq03.json`, `tlm_mq04.json`) and five talk files (`tlm_mq02.json`, `tlm_mq02b.json`, `tlm_mq02c.json`, `tlm_mq03.json`, `tlm_mq04.json`).

Added: `docs/design/ACT1_CHARLES_PACKET3_RECEIPT.md` (this file), `ACT1_CHARLES_PACKET3_ENTRY_LEDGER.md`, `ACT1_CHARLES_PACKET3_CHANGES.md`.

Not changed: the four packets, the contract, the orders, the repair review, the canonical decisions, `CANON.md`, the naming registry, both worked examples, `tools/check_story_intake.py`, `tools/story_intake_select.py`, `tools/run_checks.sh`, the workflow, `.gitattributes`, the earlier receipts and ledgers, `documents.json`, `RESEARCH.md`, every Papyrus script, the logic model, the builders, and anything installed.

## 13. Handoff

Charles to Maya, Iris, Nora and Sam. A revised proposal in source. Not accepted, not built, not playable. The branch and commit are in the delivery message and in `git log`.
