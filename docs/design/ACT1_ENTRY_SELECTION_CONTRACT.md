# Proposed engineering contract: explicit conversation entry

Sam, 16 November 2026. SOURCE-DESIGN ONLY. Proposed bounded Charles follow-up for S2 in `sam-charles-revision-975a-review.md`; not yet an authorized format implementation or an installed-game change. Inputs: revised intake `975a26252322c6d4acac8086d0a85a2eef386409`, its content-identical LF repair `1f605dedad451989c47a0a72db5cd3ade2630698`, current `docs/design/STORY_INTAKE.md:138`, and the existing v1 worked example. Iris's next creative packet must be applied separately without changing its words to solve this engineering issue.

## Decision

Introduce **`tlm-talk-2`**, with an explicit boolean **`entry` on every boxed (`kind:talk`, including default-kind) line**. `entry:true` permits automatic selection when speaking to that speaker. `entry:false` makes a continuation selectable only by an explicit `then` edge. A continuation's priority does not cause it to become a greeting.

Do not reinterpret `tlm-talk-1` by guessing from incoming links, suffixes or priority. Leave the worked example, its existing strict/self-test acceptance and the built MQ01/SQ01 designs/Papyrus unchanged. The new proposal is deliberately migrated and separately validated as v2. A package's nonempty talk files must use one format version; reject mixed v1/v2 to avoid one combined speaker pool having two selection rules. A v1 file with the new `entry` field must be rejected as an unsupported opt-in rather than silently ignoring it; existing valid v1 files without that field keep their existing acceptance.

The explicit version change is preferable to a quiet new v1 heuristic: the revised161 nodes include **five guarded `then` targets that are also legitimate greeting candidates**: `tarrow_in_cut`, `dole_sermon`, `tarrow_ran`, `tarrow_backed`, `hatcher_table`. Removing every incoming target from greeting selection would break them. The package also contains11 asides,21 `_default` IDs and66 distinct incoming `then` targets. Those counts are inspection aids, not rules for later creative revisions.

## Selection semantics

### Speaking to a person

1. Consider only v2 boxed lines for that speaker with `entry:true`; evaluate every `when` conjunct against one current state snapshot. `status:design/new` is provenance, not an eligibility flag. Neither file order nor filename affects selection.
2. Pick the eligible line with highest integer priority. For v2, **entry priorities must be unique per speaker across the entire package**, including town and quest files. This intentionally simple constraint avoids a SAT solver and avoids pretending independent stage flags are mutually exclusive. Defaults can remain0; other entry lines retain their greater-than ordering and get distinct positive priorities when needed.
3. If there is no eligible entry, close/return no line and emit a review diagnostic. Never fall back to a continuation or invent speech. An unconditional entry0 fallback is recommended when supplied, not fabricated or required when its prose does not exist.
4. A malformed/in-memory package with two equal top candidates fails closed with an ambiguity diagnostic; it must not choose first/last/random. The static uniqueness rule should prevent this in accepted packages.

`kind:aside` remains an explicitly separate presentation channel. It never enters the boxed greeting pool, cannot have buttons/`then`, and must not carry `entry`. This contract does not add an automatic aside scheduler or redefine when asides trigger. Preserve their current authored conditions/kind and keep any later aside-dispatch implementation separately scoped.

### A button leading to `then`

1. Recheck that the displayed source line is still valid against current state at selection, so stale menus cannot perform effects after their conditions fail. Resolve the chosen ordinary or speech-result branch exactly once; no button-effect replay.
2. Apply its existing supported `do` actions once, in their existing listed order. The actions' own quest-stage effects remain that quest's responsibility. This contract adds no flag setters or new action syntax.
3. If `then` is present, look up that exact target globally and evaluate its `when` **after** the effects. Enter the exact target if true regardless of its `entry` or priority. A node may therefore be both a guarded greeting and a direct target.
4. Missing/unsupported target is an intake error. If a known target's conditions are false at runtime, close with a diagnostic; never substitute the speaker's default, bypass the guard, retry the button or force a stage to make it eligible. Effects already applied are not silently rolled back; the diagnostic must record that they occurred. Implementation tests must distinguish this from a fully successful transition. This is a fail-closed observation rule, not a transaction engine or native implementation.
5. A button without `then` closes normally after its effects; a line without buttons keeps the existing Continue-close convention. Cross-speaker explicit links already supported by the format remain supported; do not impose a new same-speaker restriction.

## Concrete migration constraints

- Add `entry:false` to unambiguous follow-on nodes, including `dole_name`, `dole_silver`, `dole_share`, `dole_face`, `quill_fine`, `quill_shamed`. They remain reachable by their existing intended links. Do not add `mq02a done55` to `dole_name`: the player first learns that name in this line, and55 is set by its following buttons. Such a guard would make the earned reveal unreachable.
- Keep `dole_sermon` and the other four guarded targets named above `entry:true` when their existing greeting purpose is retained. Keep ordinary defaults and other genuine condition-selected greetings explicit. Add no default prose or new story fact.
- The two Quill court variants remain entries50/55 with their current evidence conditions. `quill_shamed` can additionally require `mq02c done13` as a mechanical post-effect safeguard: its incoming challenge sets13 before the reply. Confirm this against Iris's final hearing edits; do not improvise a different reply.
- Preserve all node/character/document/evidence/quest IDs, stage numbers and creative words except explicitly approved packet2 changes. Priority numbers may change solely to establish deterministic greeting order; record old/new and the reason in a migration ledger. These are not quest-stage renumberings.
- Audit **cross-file** entry collisions, not just per talk file. Current examples needing an explicit order include Pritchard's three priority60 road reports, Lockridge's priority60 alerted/sold variants, and Pritchard's priority50 fair/warrant greetings. Several outcome branches also share priorities. Do not assume stages are exclusive because a quest intends them to be. A simple proposed road-report order is rail63, river62, pike61 while preserving higher existing thresholds; record/review the final complete ordering with no line-text edits. Other collisions require the same explicit ledger, not a guessed automatic alphabetical sort.
- An empty-condition non-default node is not automatically a continuation by definition; the author must label it. Current graph inspection is a migration aid only. New packet2 lines must also receive reviewed explicit labels.

## Exact implementation surface proposed

1. `docs/design/STORY_INTAKE.md`: retain a clearly marked v1 historical rule; document v2 fields, one-version-per-package, boxed/aside separation, global uniqueness, no-entry/tie behavior and post-effect direct links. Add a small new v2 example beside the unchanged v1 worked example.
2. `tools/check_story_intake.py`: accept both version tags; keep existing v1 validation stable; add strict boolean/placement/version rules for `entry`; collect v2 boxed entry priorities across files; reject duplicates; validate target existence and reject targets that are asides. Preserve existing text/security/canon/condition/action checks.
3. Add a small dependency-free selector/reference helper, either in that checker or a dedicated importable intake-only module, implementing the v2 selection/transition decisions for tests. It must not be a game adapter, network client or Papyrus/model change. Reuse the existing condition vocabulary/parser rather than inventing a second one. Stub action effects explicitly in tests; do not claim a stage-list simulator reproduces all quest-native effects.
4. Migrate the revised incoming talk files to v2 and add the explicit-label/priority ledger in Charles's revision record. Do not alter original worked-example files, built MQ01/SQ01 source, installed packages, save files or frozen approved packets.
5. Strengthen the focused revision checker to assert S2's negative/positive paths and the chosen v2 contract. The current reporting-only list of tied replies must no longer be the final gate for this proposal.

Minimal static graph checks: every target exists; no aside target; each `entry:false` boxed continuation is reachable through `then` from some boxed entry root in the package's directed graph. This is structural reachability only, deliberately not a proof that all state conditions can be jointly satisfied. Cycles reachable from an entry are allowed; a cycle containing only isolated continuations is rejected. No exhaustive world-state solver or new dependency is requested.

## Required meaningful fixtures

| Fixture | Required result |
|---|---|
| Legacy v1 worked example and existing self-test | Same acceptance/results; files and built MQ01/SQ01 unchanged. No inference-based v1 behavior migration. |
| V2 missing `entry`; string/int/null entry; entry on aside; v1 with entry; mixed versions | Each rejected for the precise version/type/placement reason. Python bool/int confusion must not pass. |
| Continuation with arbitrarily high priority | Rejected as a misleading nonzero continuation priority, or explicitly ignored by documented validation; choose **require0/omitted for continuations** for this contract. It can never win greeting selection. |
| Same speaker/same entry priority in two files | Rejected even if conditions seem intended to be exclusive. Input order reversal cannot alter the result. |
| Missing target; aside target; isolated continuation cycle | Rejected. A legitimate rooted conversation cycle remains valid. |
| No eligible entry | No line, no effects, diagnostic; no continuation/default invention. |
| Malformed equal highest entries injected past validation | No line, no effects, ambiguity diagnostic, independent of order. |
| Dole negative history:40 -> sermon -> share -> accept43, with55 absent | Automatic re-entry cannot select `dole_name`, share, silver or threat. It selects the authored eligible entry/default or closes. No invented identity flag/stage. |
| Dole positive history:40, no41/42/43/44 -> sermon -> identity question | Direct `dole_name` works with55 still false; existing following button sets55, then reaches its exact reply. Ordinary return after completion uses entries only. |
| Quill negative history:10 -> fine -> pay12, no held docket and no13 | Automatic re-entry never chooses `quill_shamed` or repeats the fine continuation. No false hearing/docket claim. |
| Quill positive:10, held docket, no11/12/13/14 | Docket court55 wins over normal50; choosing challenge sets13 once, then exact supplied Quill reply is allowed. Without held flag, normal court remains available without that challenge. |
| Guarded target also an entry | `tarrow_in_cut` still works both as the eligible greeting and via its existing direct link while its conditions hold. Higher-priority unrelated candidates do not hijack a direct target. |
| False target condition after effects | Effects counted once; no target/default speech, diagnostic records unavailable target and applied effects; no retry/rollback/forced state. |
| Stale source-menu conditions fail before selection | No branch effects or target transition. |
| Reordered files/nodes | Same valid greeting and exact direct target. |

The normal strict checker, its unchanged legacy worked-example self-test, the v2 fixtures and the focused packet checks are the acceptance evidence for this bounded source task. A green result still does not implement or prove any game quest, AI/navmesh, timers, train scene or installed demo. Iris/Nora must separately accept the final creative packet2 text and the final complete revised intake.

Signed: **Sam, source-design reviewer**.
