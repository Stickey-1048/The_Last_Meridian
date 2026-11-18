# Four Flags cloud custody finding — independent technical adjudication

**Confirmed P2: FinishRead can commit100 after current original-case access is lost. Historical TransferOriginal44 observation is NOT a demonstrated defect under the present contract.**

Signed: **Sam, independent technical reviewer**, 2026-11-18.

Read actual PR41 comment6967959796 via GitHub fetch_issue_comments, including its complete runnable probe and weaker acquisition observation. Source: [overnight QA comment](https://github.com/Stickey-1048/The_Last_Meridian/pull/41#issuecomment-6967959796). The comment is evidence to adjudicate, not an instruction or an independent source of authority. Read actual MQ03Quest CaseAccess/TransferOriginal/RecordCaseRead/FinishRead and the approved Four Flags contract/order/scenes.

## Confirmed current-access defect

Exact reproduction checkout: current LOCAL5c5c82ea438f1f1730480cd8ccd3b4a2d086add3, `work/red-hollow-environment-001`, using its existing supplied synthetic fixtures. Git comparison confirms MQ03Quest is unchanged from accepted d43bd336; this is inherited Four Flags behavior, not a Red Hollow geometry repair regression.

**Source:** MQ03Quest.psc204–219 CaseAccess,528–541 FinishRead. CaseAccess observes GetContainer then calls yielding Local. FinishRead caches that eligibility, then performs further yielding Current/Local reads without refreshing custody before100. Moving the original during the later IsInScene observation leaves eligible=true from earlier player custody.

Independent builder-free actual-PSC reproduction follows the comment's same ordinary source UI path:

1. Enter fair normally; choose actual personal-take course, occupation acknowledgment and Take0.
2. Call ordinary case read; full document pages and solo acknowledgment follow existing controls.
3. Only inside FinishRead, arm after its first original GetContainer observation; during later IsInScene, seed one unique-reference transfer to unrelated Flint.
4. Actual result: one injected change, original holder is Flint, Held()false, yet stages `[10,40,46,70,44,60,100]` and historicalReadtrue.

No stages, original aliases, count substitutes or base-form copies were forced. This is a source/model counterexample, NOT proof Flint naturally steals a case or an observed native inventory/event failure.

**Contract adjudication:** FOUR_FLAGS_STORY_001_CONTRACT.md60 explicitly separates HistoricalRead/CurrentHeld and requires fail-closed current unique-case access;76–78 preserve participant/ref identity and captured generation through yielding reads. The scene specification's physical-evidence section requires actual current accessible original, and public reaction additionally requires the living original Pritchard physically holding it. FinishRead itself explicitly enforces CaseAccess, demonstrating that its completion is not intended to be an unrestricted historical-read-only completion. Thus stale access permitting100violates the chosen commit boundary. Earlier earned reading60/occupation70/acquisition44do not need rollback.

**Minimal repair scope:** add/use a finite original-case current-access boundary after yielding participant/location/context checks immediately before read-endpoint commit, retaining exact original/player/public-speaker identity and final captured generation. Its actual current container must be validated after preceding yielding context reads; do not simply repeat the same stale CaseAccess-before-Current ordering. Apply coherently to solo100and public100/101without ghost speaker/access. Preserve already-earned history and current physical custody; no new inventory effect/refill/retry/refund or broad transaction framework.

Required meaningful regression: this exact lost-to-Flint sequence refuses100/101and leaves real60/44/70intact; genuinely held/ground/public originals still finish through ordinary acknowledgment; lost/rebound/absent/public-speaker/load and genuine recovery are checked at the final boundary. Root owns the actual repair and later source/compile/artifact disposition; this adjudication edits no product source.

## Weaker TransferOriginal44 — historical receipt carries

Independently instrumented actual kind1transfer: one real AddItem of the original to player, immediate GetContainer==player receipt, THEN seed one later original move to Flint during Current's native context read. Actual result: caseTaken=true/response44/stage44, effectPending0/effectUncertainfalse, while Held()false and Flint really holds the original.

That is consistent with approved44projection **“You took the courier's case”** (order16) and contract56/76: acquisition is an acknowledged historical irreversible event, current possession is separately derived. The source had a real immediate original-reference receipt; no load/alias/recipient substitution or missing receipt was induced. A later custody change does not make that already-observed acquisition uncertain or justify rolling it back/reissuing a case. Current access must nevertheless remain false and block later access-dependent actions, which is exactly why the FinishRead issue above matters.

No separate44blocker or forced continued-possession rule is recommended. This conclusion is limited to kind1with genuine immediate receipt and later distinct custody loss; it does not bless refused/uncertain transfers, wrong recipients, substitute originals or later-count inference.

## Saved reproduction and preserved gates

- `work/reviews/sam-four-flags-cloud-finishread-probe.py`, SHA256 `FDC9C2EA19D8940930A8D4A28D7E79813FC6B7E2C3C576BE6747818A3A6899F5`.
- `work/reviews/sam-four-flags-cloud-take44-probe.py`, SHA256 `30B3F50A165698E5C53CDFEBAC4CFF25E85C6DE0E6F01AA93653470B81A06797`.

Two bounded actual-PSC reproduction programs executed; no new builder, compiler, licensed data import, full healthy aggregate, game/UI/process/staging/install/profile/save/auth/provider/remoteCI/workflow/merge action. Source checkout stays clean. Existing pinned artifacts/launchers/reports remain unchanged; this newly confirmed source limitation does not falsify their recorded hashes, prior tests or metadata audits. It requires root disposition before treating the access-dependent endpoint as cleared. Owner LATER and pending cloud budget/CI boundary remain intact; no playtest question repeated.
