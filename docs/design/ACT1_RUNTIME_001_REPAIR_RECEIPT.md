# ACT1-RUNTIME-001: repair receipt

16 November 2026. Written and committed **before any repair was made**. It records the findings of the independent review of the implementation commit, as Maya delivered them, and what the one consolidated repair intends to change. What was actually done is added at the end (section 5) when the repair is finished.

Nothing here is a Papyrus compile, a build against the game's master or a game test. No licensed input is in this checkout or was asked for.

## 1. What is being repaired

| | |
|---|---|
| Reviewed commit | `f649f9b24f6105ac83ab0e0c2ecc7860259a28ed`, tip of `feat/act1-runtime-001-mercy-briefing`; fetched and compared with the given hash |
| This branch | `feat/act1-runtime-001-repair`, made from that exact commit. Nothing reset, rebased, merged or force-pushed; no pull request opened by this work |
| Scope | The approved ACT1-RUNTIME-001 scope, unchanged. One consolidated repair, no new feature, no new speech, no destination work |

## 2. The findings, as delivered

**1. Explicit Continue only (found by Nora and Sam).** In `TLM:Act1Walk`, after the chapter, the box with the side quest's report has two buttons. Return 1 is the report; return 0 alone may go on to the briefing. My code used a plain `Else`, so a return of −1 or of any unsupported value opened the briefing and started its quest. Sam reproduced it through the real `Spoken` with −1 and with 9. That is a defect in what I wrote: before my change, anything but 1 did nothing.

**2. Starting the quest must fail closed (found by Sam).** `TLM:MercyBriefing.Offer` called `Start()` and ignored both its result and whether the quest was then running. With `Start` returning false and the quest still stopped, the script went on to the alias and raised in the stand-in instead of falling back to the first section's own ending. That is a defect in what I wrote. The `Briefer` alias is already Optional (the builder makes every script-filled alias so); it is not the problem and is not to be changed.

**3. Raw digests and Windows line ends (found in review).** `tools/mercy_briefing_candidate.py` hashes the four earlier manifests byte for byte. They have no end-of-line rule, so a fresh Windows checkout writes them with CRLF while the committed blobs, and the digests my manifest records, are LF: `verify` and 10 of the 98 new tests fail there. I ran everything on Linux and did not see it. The committed bytes and every old pin are right and must stay.

**4. Which compiled scripts go into the bundle (found in review).** My recipe said every one of the 20 scripts is taken from a fresh compile and no earlier PEX is reused. The contract says otherwise: a full fresh compile of all 20 is the *proof that they compile*; the *runtime selected for the bundle* is the 18 unchanged reviewed PEX of the earlier runtime (manifest `F8649EE3…`), each after its source text and its bytes have been checked against the pins, together with the freshly compiled `Act1Walk` and `MercyBriefing`. The freshly compiled 18 are not substituted, and nothing assumes the compiler reproduces the old bytes. I misread that paragraph of the contract.

**Wording (ledger, unresolved mechanics, item 4).** I wrote that no box of this project has been answered by hand in a recorded run. That is wrong as a statement about the project: earlier choices have their own independent game receipts. Only the **new** Mercy briefing boxes have not been answered in a recorded game run. A correction of wording, not a new result.

Also delivered, and not mine to change: root ran the two changed package-safety fixtures under Windows PowerShell 5.1, 15 checks each, all passing. Those expectations and the guards they protect stay as they are.

## 3. What the repair intends to change

| File | Change |
|---|---|
| `scripts/Source/User/TLM/Act1Walk.psc` | The report box's return read once: 1 the report, 0 the briefing, anything else nothing |
| `scripts/Source/User/TLM/MercyBriefing.psc` | `Start`'s result and the running state both required before anything else; otherwise false, with a diagnostic naming both, before `busy` is claimed and before any alias, stage, objective or item is touched. While there, the same strictness for its own boxes: a brief counts as shown only on a return that is one of its buttons, since finding 1 is the same mistake |
| `tools/logic_model/mercy_briefing_model.py` and its test | The gate "its quest can be started", so the model keeps step |
| `tools/papyrus_sim/test_mercy_briefing.py` | Regressions: −1, an unsupported value, explicit 0 and the report's 1 through the real `Spoken`, with the side quest and every reward compared; `Start` failing, and the two inconsistent results, on first access and on a completed briefing; normal first and repeat access beside them |
| `.gitattributes` | Four exact rules, `text eol=lf`, for `tools/win/world-details-artifact.json`, `world-natural-artifact.json`, `world-story-artifact.json` and `tools/WorldSliceBuilder/expanded-artifact.json`. Their committed bytes are not changed |
| `tools/mercy_briefing_candidate.py`, `tools/win/mercy-briefing-candidate.json`, `tools/papyrus_sim/test_mercy_briefing_candidate.py` | The selection policy recorded and checked: 18 reused reviewed PEX by name and pinned digest, 2 freshly compiled; the full compile as separate proof; `measure` says which is which in a built bundle. A check that the four manifests' committed blobs are the pinned bytes whatever the working copy's line ends. Measured digests stay empty |
| `docs/design/ACT1_RUNTIME_001_LEDGER.md`, `tools/README.md`, this file | The corrections above, the wording of item 4, what a working copy made before the rules needs, and results |

Not to be touched: the four earlier manifests' contents, their packagers, stagers and pins; the two package-safety fixtures; `MQ01Quest`, `SQ01Quest`, `Act1Talk`, `WorldEntry`, `Core`; `tools/run_checks.sh`; the workflow; any Git setting outside this repository's own tracked `.gitattributes`; the accepted writing and its packets; `SpecMercyBriefing.cs` (no text changes).

## 4. What stays pending whatever the repair finds

Root's, after independent acceptance of the repaired source: the fresh Windows checkout, the build and read-back against the game's master, the compile of the 20 scripts, the candidate's measured digests. Then private native QA. None is claimed here.

## 5. What was done

To be completed when the repair is finished.
