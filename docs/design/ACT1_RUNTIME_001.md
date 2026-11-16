# ACT1-RUNTIME-001: Mercy briefing and the optional review copy

Status: **DESIGN APPROVED FOR BOUNDED SOURCE IMPLEMENTATION**,16 November2026. Sam authored the candidate; Maya and Nora independently accepted its bounded design. Maya clarified cloud/local build responsibilities and composition without a merge below. Source implementation and native acceptance remain pending. Accepted writing is not reopened; the installed owner Details demo and the separate Green physical gate remain independent.

## One concrete playable increment

After the player actually delivers Gantt's dispatch and finishes the existing MQ01 debrief, Pritchard can give repeatable, selectable information about the three future roads. The Red Hollow briefing offers the approved optional2298 review copy as a real readable inventory book. The preview can observe whether that exact copy is currently carried. A small **Mercy briefing** journal task records receipt of a briefing and ends honestly at the build boundary.

This adds actual interaction, an authored evidence document and persistent, testable acquisition/current-possession behavior. It does **not** open Iron Junction, Greenwater, Red Hollow, the fair or any later chapter. No button says a route has started; no objective points toward an unbuilt destination; no canonical MQ02 road-completion or MQ02c acquisition stage is falsely set. The first playable addition is preparation in the already-rendered Mercy location, not a claim that the three journeys exist.

## Exact baselines and composition

| Input | Exact revision/artifact |
|---|---|
| Accepted227-line writing/entry contract | `d142104fdc6f72ae556f285a0166c1122893b991`; exact remote CI43928319207 success supplied by Maya |
| Tested owner Details source | `b280847ef14bfd03eea102d7845675506f51c3fe`, immutable `work/world-details-preview` |
| Common ancestor | `14d841b0c9b7b267d2e3e562b7c3b65fbc9b3fd1` |
| Current Details master | `AA52CBC3A6153BF83BB99EF22D8CC385DA2254052B49E4A78252494003250F3F` |
| Current Details exterior | `E1279E42DAA19D94A628F1270D285EB8A175EE21579924C0DE51B017C25F5965` |
| Current runtime | Normal19, manifest `F8649EE3E35DB1711089C6A7B21283E385DC31A2729802748A43491681478412`; Act1Walk `B5CE46D3FF83F08A1BA5820A85CD058C7A30B78F842BC10DB40E3EFD0482995F`, MQ01Quest `70E44BA8D1BC673AAFBA2BF74201A27D2A2B9675E70424BD882F37AF738404B5`, normal Core `BD7A9CBB30F5DCB3858EFA9556BE14B875332056A86B6B7816838E1577A8E4E3` |

**Do not replace Details with the writing checkout.** Actual inspection shows d142 does not contain the Details builder/packager/launcher additions. A direct b280→d142 tree diff removes14 runtime-tool/world paths. However, ancestor14d→d142 changes none of `scripts`, PluginBuilder, WorldSliceBuilder, `tools/win` or the logic model; ancestor14d→b280 changes none of the incoming writing or its selector/checker. They are distinct, compatible lines of work, not a verified precomposed runtime branch.

Maya prepared a **new isolated feature worktree/branch from b280**, applying the exact reviewed writing delta from common ancestor14d to accepted d142. The patch passed git apply --check and applied without conflict. This is a normal source-composition commit, not a merge commit or PR merge; both original branches/checkouts remain untouched. Before runtime edits, verify the composed source still describes the old runtime and that the normal19 approved source provenance matches. No control build or native result is claimed by this composition. The copied source README retains its earlier trailing-blank-line whitespace warning; do not confuse that documentation warning with a failed content application.

Preserve the original b280/E127 owner package, profile, controller1, fixed manifests, launchers and fallbacks. A new candidate gets **new hashes and its own manifest**; it must never be put under the old Details pins. Once runtime source changes, the old Details packager in the feature checkout may correctly fail its frozen-source guard. Do not weaken that guard or claim it rebuilds the new variant. The immutable b280 checkout remains the reproducible old fallback.

## Current native integration facts inspected

- `Act1Talk.OnActivate` already routes real player activation through `Act1Walk.Spoken(Who,Actor)`. Pritchard is Who5. There is no generic v2 native dialogue adapter; the accepted Python selector is a source reference only.
- `Act1Walk.TalkPritchard` handles delivery50, waits for `WaitForDeliveryAcknowledgment`, shows the debrief/handoff, then records60. `MQ01Quest.ApplyDebriefDone` sets Done1 and100 after the acknowledged delivery. Use these actual gates; do not mistake dispatch possession, stage50 alone or one menu click for completion.
- After60 the existing Pritchard After/AfterAndMore messages retain the SQ01 report path. Preserve that path and its effects; the new briefing must not hide an available ledger report.
- Current handoff/After messages explicitly say later routes are not playable. `SpecAct1.DemoEnd` notes a real native failure near255 displayed characters; avoid concatenating long new footers onto every spoken line. Test full native rendered strings, not only the intake240-character field limit.
- PluginBuilder already constructs native BOOK records through `BookSpec`/`Builder.Build` using the owned master's note model/inventory presentation. It does not generate native forms from the incoming documents automatically.
- The exterior builder clones `TLM_A1` to `TLM_WS_A1`, remaps its own alias links and preserves **29 exterior aliases/references**. It copies ordinary non-alias script object properties. A new master-quest property can be preserved without moving/recasting any actor, but actual VMAD readback is still required.
- Current native rules/model implement MQ01 and SQ01 only. No TLM_MQ02 or MQ02c runtime quest, silver-flag setter,2298 inventory item or destination navigation exists. This increment must not pretend otherwise.

## Runtime projection and exact source mappings

Use a **small explicit projection**, not an adapter for all227 lines. Keep accepted intake/packets unchanged. An accompanying mapping file identifies the exact d142 field used for each native message/book and the source-only semantics deliberately not imported.

| Proposed runtime record/state | Approved source / meaning |
|---|---|
| `TLM_MercyBriefing` quest; script `TLM:MercyBriefing` | New clearly labelled preview utility task, not `TLM_MQ02`. StartGameEnabled=false. No timers, cast setup or load reset. |
| Local stages10/20; objective10 | Technical preview progress only:10 briefing begun,20 at least one route briefing presented and the utility task complete. They are not MQ02/MQ02c stages with the same numbers. |
| Objective10 text | UI-only: `Ask Pritchard about the three roads.` Target the actual actor activated, if the alias is bound; journal availability is acceptance, HUD tracking is separately observed. |
| Native hub question | Exact `pritchard_report_open_roads.text`: `Which road do you want to ask about? Tell me what you know, or ask what to look for.` This generic prose is reused as a new preview message, **not** as an executable import of that postfair node's MQ02done100 guard. Record this projection distinction explicitly. |
| Hub labels | Existing approved `The rail.`, `The river.`, `Red Hollow.`, `Not now.` These ask for information, not the canonical promise-to-travel buttons or fair-without-report action. |
| Three native briefing leaves | Exact `pritchard_road_rail`, `pritchard_road_river`, `pritchard_road_pike` text. No new narrative wording, token transfer or destination quest is implied. |
| Pike follow-on | Exact `What should I ask Quill?` and `pritchard_docket_context` with its approved `Take the review copy.` / `Leave the copy.` options, subject to the idempotent handover below. |
| `TLM_BOOK_Docket2298` | Exact `documents.json:docket_2298` title/body (629characters). Native BOOK form, no new NPC/witness/family or invented historical claim. Not a paymaster proof or a pardon. |
| `CopyIssued`, `CopyGrantPending` | Private preview handover bookkeeping, not knowledge flags. Persist on the helper; no initialization/reset on load. |
| `HasReviewCopy()` | Read-only `player.GetItemCount(TLM_BOOK_Docket2298)>0` **at use time**. This is the precursor mapping for future `docket_2298_held`, not a latched acquisition boolean. |
| Canonical MQ02c16 / silver flags | **Not set here.** MQ02c is not built. Record local issuance history for a future explicit migration contract; do not create half a later quest merely to set16. All silver evidence remains unearned unless its actual existing source says otherwise; no new silver flag is granted by a briefing. |

Technical UI outside the quoted character speech must state, at the hub and final journal boundary: **`Mercy briefing only. The three destinations are not playable in this build.`** A short handoff footer may say **`Opening complete. Ask again for Mercy briefs; roads unbuilt.`** Both are product-availability text, not new fiction. Audit the complete actual message strings for length; split availability into a short separate UI message/title if necessary. Do not silently truncate approved prose. No missing creative line is required for this increment.

## Native flow and persistent-state rules

1. Preserve the existing dispatch/debrief path through60/100 exactly. On **subsequent explicit Pritchard activation**, after MQ01's delivery acknowledgement,60,100 and Done1 are all true, offer the new briefing. A missing optional binding falls back to the existing ending rather than breaking MQ01.
2. Pass the actual activated Pritchard into the helper; do not assume a test-room actor or force the old quest aliases to refill. A small optional actor parameter/internal handoff from `Spoken` is acceptable. Preserve existing public behavior/call sites and the `talking/quiet` guard. Recheck the live, noncombat actor and player after every modal return before state/item effects. Dead/stale actors do not give a copy or complete a task.
3. Keep the existing SQ01 `More`/Report choice reachable through the current AfterAndMore branch. Continue may open the briefing; Report does its existing work and returns. The new hub has at most4choices and does not steal a report-button index.
4. First explicit briefing access starts the preview utility task and displays objective10 once. `Not now` closes without finishing a road, setting evidence or starting a timer. Selecting a route shows only that leaf (plus the optional Pike subtree), then closes; reactivation permits other briefs. Do not build an unbounded modal-menu loop.
5. After a valid presented briefing, complete the utility objective/task once with UI journal text **`Mercy briefing complete. Destinations are not playable in this build.`** This is not MQ02 completion. Repeated explicit information access must remain possible without restarting/resetting the finished utility task. Compile/test the stopped-quest/helper call behavior rather than assume it; the existing MQ01 postcompletion helper calls provide a pattern, not proof for the new helper.
6. A copy is supplied only on the explicit approved Take choice. Before native AddItem, persist a private handover intent and claim the helper's short no-reentry guard; then give **one** new book and acknowledge from actual current inventory count. Current count>0 never awards another copy. `CopyIssued` prevents regeneration after dropping/storing/removing it. Dropping the book makes `HasReviewCopy` false; retrieving that actual item makes it true. Do not remove other inventory, mark the optional book a compulsory QuestObject, change caps/perks or respawn lost copies.
7. If a save/load interrupts native handover, inspect current count to acknowledge an already delivered book. A pending intent with count0 must fail closed with an actionable test diagnostic, not automatically replay AddItem or claim a successful handover. The optional main briefing still works. No new general transaction framework or retry timer is requested. After issuance, omit Take from subsequent whole-message contexts; retain the supplied speech and a neutral Continue/Leave so no button falsely promises a second copy. Explain availability through UI, not invented NPC dialogue.
8. No owner-save migration is promised. Initially test the new variant only in a separate fresh disposable profile. Loading/reentering its own saved candidate must preserve utility state and must not reset MQ01, replay its rewards, or duplicate the optional copy. Current owner Details saves/packages remain untouched.

The copy handover is the smallest new **actual evidence mechanism** in this increment. It proves acquisition/current possession only, not that a person read/understood it, that Quill received it or that the earlier hanging establishes any present prisoner's innocence. A physical desk placement/drop animation is outside this first projection and must not be claimed as built.

## Bounded author surface

Expected files, with any extra justified in the handoff:

- New small `scripts/Source/User/TLM/MercyBriefing.psc`; `Act1Walk.psc` only the postcompletion handoff/actor forwarding/property. No edits to MQ01Quest, SQ01Quest, Act1Talk alias behavior, WorldEntry startup, AI, globals for earlier outcomes, Core or scenario defaults.
- New focused native spec file such as `tools/PluginBuilder/SpecMercyBriefing.cs`; minimal Spec registration/message/property binding and new BOOK/quest. Append own FormKeys, preserving the complete existing `formkeys.txt` prefix and numeric identities. Do not preinvent numeric IDs; read back the actual allocation.
- `WorldStory.cs` only if explicit new-property verification/remapping is needed. No exterior placements, LAND, meshes, furniture, fences, navmesh,29-alias prefix or actors move. Actual world VMAD may change for the new binding and its source master changes hash; identify that exact expected raw delta.
- One small briefing-state model/test module separate from the established MQ01/SQ01 rules. Existing simulator fixtures drive actual `Spoken`, returned message indices and inventory API effects; no whole-v2 native dispatcher or six-quest adapter. Add missing simulated API support only from inspected base SDK behavior and label assumptions.
- New fixed **source/workspace package recipe and manifest** for this candidate, not changed old Details pins. Record proposed source fields/stages/property-to-form mappings, document text hash and all20 runtime hashes. A new owner launcher/stager is **not** part of Charles's first code task; root commissions a new-only private QA wrapper after source acceptance.
- Developer design/handoff/provenance plus exact supplied-text projection checks. No creative packet or accepted intake rewrites. Existing remote checks may run under their already authorized configuration; no workflow/auth/provider changes are part of this increment.

Normal runtime grows from19 to20 scripts: modified Act1Walk plus new MercyBriefing, the other18 original script sources/approved bytes unchanged. Actual full compile must succeed for20. Preserve original pinned bytes for unchanged18 only after source-provenance comparison; record fresh-compile success separately from selected-package provenance. No blind PEX normalization or assumption that compiler timestamps reproduce old bytes. The new master/world get new measured hashes, not invented future pins.

## Acceptance and stage gates

### 1 — Design approval (before Charles)

Maya reviews this exact candidate; Nora independently checks scope/prose/boundary honesty. Approve the preview utility projection and its deliberate nonmapping of canonical MQ02/MQ02c stages. If either reviewer wants an actual built destination instead, change the task before dispatch; do not call a briefing a completed journey.

### 2 — Author source/build handoff

Charles uses the exact published composition commit in an isolated follow-up branch; first commits an actual receipt, then one bounded implementation candidate plus at most one consolidated repair. In the existing cloud session, produce exact changed-file inventory, source-text mapping, generated stand-in-master build/readback and applicable source/simulator tests. If the cloud lacks the Papyrus compiler or real GOG master, report those gates as pending rather than claiming success or requesting an upload. After independent code/source review, Maya performs the workspace-only owned-GOG-master build/readback,20-script Windows compile and candidate package hash receipt locally. Licensed masters/compiler inputs are not uploaded or committed. No install/game/owner profile or save writes occur in this author/source stage. No new author-defined gameplay chapter or narration. Return draft/unmerged for review.

### 3 — Independent code/source checks

Review before execution; then run appropriate checks once per changed candidate:

- Existing strict/four-packet/74entry checks stay green; accepted writing/legacy v1/runtime baseline unchanged. Existing runtime aggregate including65scenarios/53matrix cases remains required because Act1Walk and builder wiring change, even though MQ01/SQ01 rules do not. Preserve scenario12's no unsolicited boxes/42checks.
- Native projection tests match each used d142 text/title/button exactly; availability UI is separately identified and full displayed strings stay below the known truncation case. No unused227-node adapter or swallowed check failure.
- Gate matrix: no dispatch; dispatch carried;50pending;50acknowledged but60absent;60event still finishing; final100/Done1; actor dead/combat; player death; interrupted/stale menu. Only the final acknowledged state opens the addition, with source rechecks before effects.
- Native menu-index tests cover all3briefs, Not now, Pike's optional context, existing SQ01 report availability and repeated visits. No MQ02/road/fair stage, silver flag, reward, actor state or destination objective changes.
- Objective starts once on explicit access, completes only after an actually shown leaf, remains completed on repeats/reentry; no canonical chapter completion is synthesized.
- Item count0→1 only after explicit Take; repeat/reentrant activation no second copy; save/load before/after intent and acknowledgment; dropped/stored/removed copy count0; retrieve→1; injected native AddItem failure/pending count0 fails closed without another item grant. Current possession is never inferred from utility progress or issuance history. Main briefing never requires taking the optional copy.
- Real-master binary/readback: preserve old FormKey prefix, all old actor/ref/alias placements and LAND; new quest/BOOK/messages have correct script/property types; both QASmoke source and exterior clone resolve the intended helper rather than the wrong quest/test-room actor. Missing new binding is diagnosed; old fixed manifest rejects the new bundle.

### 4 — Root's private native QA, after independent source clearance

Root creates a separately reviewed new-only profile/mod/journal for the new pins; protects owner Details/Natural/QA files, uses dual process guards and established startup ownership/cleanup. New fresh player only, normal Core/scenario0/F4SE route as already validated; no loaded owner save, no quest resets or invulnerability. Native runs must keep their artifact/runtime pins exact.

At least two short fresh paths: a real Leave/bypass completion of existing MQ01 followed by the new Mercy menu, and another outcome/SQ01-report-present case demonstrating that the old report stays accessible. Actual player/normal actor activation and dispatch handover, not forced SetStage to manufacture endpoint acceptance. Fixtures may separately seed source preconditions for negative tests, labelled as such; they do not replace the measured first-section route.

Capture actual menu returns as numeric indices and the shown text; a cursor hovering over a label is not proof of choice. Observe native objective/journal and the short honest boundary. Verify the real book appears once and opens as the exact readable document; independently count the exact new book. Save/reload only this disposable candidate save, reactivate and confirm no duplicate/reward replay; optional drop/retrieve shows current count, with actual normal input where available. Log closure and exact protected-file/startup restoration. Positioning fixtures are not walking/navmesh proof. If menu input is uncertain, stop at that gate and request the smallest physical confirmation rather than report an imagined selection.

### 5 — Candidate acceptance and owner delivery (separate approval)

Only after source/remote checks and the specific native gates pass may Maya approve a new fixed owner variant/launcher and publish its exact receipt. Preserve the existing b280/E127 fallback. The final user-facing statement is **Mercy briefing plus optional evidence copy**, with three destinations still unbuilt—not Chapter2 delivered, not all227 lines implemented, not a new walkable region. Neither this design nor a cloud green check changes the installed game.

## Precise next Charles scope if approved

“Start from Maya's exact published composition commit in a new isolated branch. Implement ACT1-RUNTIME-001 only: existing Pritchard postacknowledged-MQ01 activation -> repeatable three-road information hub -> optional native2298 review copy/current-possession proof -> truthful completed Mercy briefing boundary. Preserve old MQ01/SQ01 behavior, nineteen-script fallback and fixed pins; new candidate20-script package/source checks only. No destinations/fair, generic v2 game adapter, scene/navmesh expansion, install/game/auth/workflow or owner-save change. Return exact source/stand-in-build/test/provenance handoff for independent review. Maya owns the later licensed-master build and Windows compiler gates. The design has Maya and Nora's bounded clearance; the delivery message supplies the exact approved composition commit.”

Signed **Sam**, design author; **Maya**, coordinator and composition author. Nora independently cleared the bounded design with the cloud/local gate clarification. No implementation acceptance or native result is claimed.
