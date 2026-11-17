# Red Hollow: one complete playable story contract

Iris, 17 November 2026. **Design preparation only.** This workspace contract does not authorize another implementation while Night Mail runs. No accepted narrative/runtime/canon, cloud job, installation, save or game UI is changed. It prepares the remaining Chapter2 road, not a broader roadmap or a measured playtime promise.

## Accepted inputs and bounded deliverable

Read the actual accepted narrative in `work/greenwater-repair-review`, HEAD `016b2b4005203ba180b908fb310a1653a95f934f`, whose story content remains accepted d142104: `quests/tlm_mq02c.json`, all `talk/tlm_mq02c.json`, relevant hub talk, documents and character entries, together with `ACT1_CREATIVE_DECISIONS_2026-11-16.md`. Settled decisions govern over obsolete owner questions. Existing Greenwater repairs and the published Night Mail design provide patterns for acknowledged scenes, real physical effect verification, custody and truthful context-dependent journals; neither provides a working rope, hoist or safe deadline by assumption.

Deliver **TLM_MQ02C, What Knocks in Red Hollow** as one road: optional gallows intervention/evidence, mine warning, actual descent and eleven-person rescue or an informed fatal sealing, a limited optional Dorn meeting, visible aftermath and a truthful Mercy report. A readable briefing or narration that miners were rescued is insufficient.

Use one isolated greybox test cell with five labelled zones: (1) toll/gallows wagon and a real walk-around bypass, (2) Mouth/hoist-house and vigil, (3) cage/lift staging, (4) Nine-level miners/break and (5) sealed gallery/stone door. Short supported paths connect nearby zones; a confirmed fade/relocation may represent the four-hundred-foot hoist. No real vertical lift physics, four-minute wait, red-clay settlement landscape, custom art, voiced cast or further underground culture is a prerequisite. Label represented travel rather than claiming a simulated lift. Add only reviewed Mercy travel/report/copy integration outside this cell.

Mercy departure is explicit after the actual opening completion, independent of Greenwater/Night Mail completion. Decline/cancel leaves the player/state untouched. Do not require a brass tag that an earlier information-only briefing never actually granted. Document this commissioning/travel projection. Root selects a separate composed candidate only after the currently running work is reviewed; do not replace its source or predeclare runtime counts/hashes here.

## Exact narrative sources and roles

Paths below are relative to accepted `assets/incoming/act1/story/`.

| Source | Exact IDs / use |
|---|---|
| `quests/tlm_mq02c.json` | `key=mq02c`, `id=TLM_MQ02C`; stages/objectives/evidence/flags and `cannot_break` |
| `talk/tlm_mq02c.json`, court | `quill_court`, `quill_court_docket`, `quill_fine`, `quill_shamed`, `quill_after_shot`, `quill_after_drop`; ordinary default only in truthful context |
| Same, prisoner | `dunmore_rope`, `dunmore_rope_missed`, `dunmore_tells`, `cutter_rope`, `cutter_rope_missed`, `dunmore_freed`, `dunmore_freed_fine` |
| Same, mine surface | `roark_mouth`, `roark_deadline_warning`, `roark_why`, `roark_back`, `roark_cage`; `greer_first`, `greer_first_heard`, `greer_knock`, `greer_lamp` |
| Same, gallery | `dorn_door`, `dorn_terms`, `dorn_who`, `dorn_no_head`, `dorn_sworn`, `dorn_lamp`, relevant default |
| Same, aftermath | `roark_after_line`, `roark_after_break`, `roark_after_fire`, `roark_after_deadline` |
| `documents.json` | Whole `toll_board`, `quill_docket`, `docket_2298`, `chalk_message` |
| `characters.json` | `quill` Esther Quill; `greer` Hobart Blevins; `roark` Dinah Roark; `dorn` Helga Dorn. Keep retired machine IDs, corrected display names |
| `talk/tlm_mq02.json` | `pritchard_road_pike`, `pritchard_docket_context`; exact speech of `pritchard_hears_pike_after_fair` / `_unknown` for explicitly documented report projection |

The current prisoner uses the **actual surviving** Reese Dunmore, otherwise a surviving existing Tellico Cutter. Never resurrect Dunmore or create a newly named gang member. If both existing Cutter roles and Dunmore are dead/unavailable, omit that prisoner scene with technical availability text; leave the bypass and main mine story playable. Do not conjure a fresh prisoner or grant testimony from a record never established. Import the actual MQ01 outcome: missed introductions cannot imply the player met them. Brigg's authority appears in the toll document; his physical presence/new dialogue is not required.

Pell remains only Dinah's already established husband, one of the night shift. No surname, genealogy, separate backstory or new speaking character is added. The eleven miners are existing authored roles represented physically, not eleven newly authored personalities.

## Proposed native bindings and physical controls

| Alias/reference group | Required actual binding or object |
|---|---|
| Quill, Blevins, Roark, Dorn | Four canonical named actors in this road; correct source/display identities; actual life/presence/combat eligibility per action |
| CondemnedActor | Same real surviving MQ01 Dunmore, otherwise one existing surviving Cutter reference; bind only after the opening encounter is finished. A deliberately staged court relocation of an actually living departed actor is distinct from resurrection; verify enable/move and do not reset the old encounter or duplicate its actor |
| Miners01 through Miners11 | Eleven distinct persistent generic night-shift actors; explicitly allocate one unnamed role for the established reference-only Pell relationship. No already placed physical Pell actor is assumed. No new speaking identities |
| Toll/court controls | Toll board, court docket, actual gate/bypass, hit-capable rope attachment, unbroken/broken displays, supported condemned/release/custody/execution markers, local scene control and established transcript |
| Docket2298 | Existing actual book base/item from Mercy helper, dynamically counted; no second identity/duplicate-for-proof or automatic refill |
| Mouth/hoist controls | Actual mouth door/blocked rubble, distinct firing control/key, functioning cage access, surface/below player markers and eleven supported miner arrival markers |
| Inner break/gallery | Separate inner-break barrier/charge control, miner muster/cage markers, closed stone door and eligible Dorn position; no target beyond the sealed door |
| Evidence | Existing shovel-message text, desk silver/instruction inspection, separately tracked gallery lamp and cot lamp origins; actual readable/custody behavior |
| Mercy/episode boundary | Explicit entry/return, local loaded-area detection, report target on the existing Pritchard reference and optional briefing/copy integration |

Resolve real engine-supported record types/events and audited base forms during implementation; this table does not invent a Papyrus hit/timer/lift API. Independent readback must prove each binding and supported coordinate. No original Mercy/story alias is reset to make a new role convenient.

## Ordinary actions and consequential sequence

| Player action | Discovery/response | Actual result |
|---|---|---|
| Arrive at the gap, read the toll/court boards, talk or take the walk-around path | Dominion toll/court claim; `Plea: not asked` remains visibly challengeable, not proof of justice | Optional court encounter may be bypassed without a remote execution; main route remains open |
| Speak to the prisoner, shoot the real rope attachment, pay sixty caps, or show the currently held docket | Accepted testimony; `quill_fine` or `quill_shamed` | Actual release, adjourned living custody, or a separately witnessed execution; no pardon from the old docket |
| Reach the Mouth, inspect the shovel message, hear the knocking, ask Roark/Blevins | Eleven are below; Blevins's assertion they are dead is his belief, not narrator truth | Merely asking questions does not arm a timer |
| Read the actual local warning and explicitly confirm rescue/talking to Blevins | `roark_deadline_warning` | A visible, locally active deadline is armed only after acknowledgment, with its remaining time understandable |
| Use the hoist; physically find the eleven, then approach the sealed gallery if desired | Actual miners; optional `dorn_door` and terms; physical evidence/lamp | Rescue remains possible without allegiance, a personal oath, lamp theft or optional proof |
| Choose personal undertaking / rescue then blast the break / rescue without either / informed seal order / knowingly fail the locally warned deadline | Accepted choices and context-dependent aftermath | Verified surface survivors, separately blocked inner break, or observed sealed Mouth with people entombed; timeout never becomes a player order |
| Return to the surface and then Mercy | Actual cage, rubble, survivors and evidence; truthful report | Road complete with separate court/mine/evidence facts. No fair, next chapter or hidden origin is opened |

## Two independent outcome machines

**CourtOutcome:** none / bypassed / rope-released / fine-released / adjourned-under-review / executed. These are exclusive; testimony and the prior2298 case are independent evidence. The current accused may be guilty even when the old hanging was wrongful. An adjournment keeps the current person alive to answer the charge; it does not pardon, recruit or owe a rescue favor automatically.

**MineOutcome:** none / saved-with-personal-line / saved-and-break-blown / saved-without-pledge-or-blast / explicit-order-sealed / deadline-sealed, plus the native adverse-state adapter `observed-casualties-resolved` described below. Exclusive terminal outcomes are committed after the actual physical result, not a choice click. A separate `PactMade` or `PlanBlowBreak` can precede rescue, but neither proves a miner reached the surface. Taking the optional lamp is orthogonal and cannot stand in for rescuing or sealing the mine.

Persist court/prisoner identity and actual life/custody, fee/receipt/fine facts, testimony source, actual docket possession, `ReferralPending` and acknowledged actual referral of both dockets, knocking encountered, warning acknowledged, timer state/remaining active seconds, current local area, pending hoist/rescue/fire scene, `PactMade`, `TermsDeliveryPending`, `BreakPlan`, `MinersBelow`, `MinersAtCage`, `MinersAtSurface`, `EntombedCount`, actual deaths/cause, `LampOrigin`/acquisition/current possession, actual silver evidence, return/report history and explicit cause of any Mouth firing. Never derive every earlier stage from a higher number.

## Stage proposal and actual observation

| Accepted stage | Native trigger / fidelity condition |
|---|---|
| 10 | Actual arrival at the gap, not merely confirming travel |
| 11 | Real player projectile breaks the rope attachment and the actual living prisoner reaches a safe supported release position. Quill's separate recording/fine is tracked only if actually delivered |
| 12 | Sixty caps actually transferred once and living prisoner actually released; real receipt item/status provided, not an unsupported promise |
| 13 | Actual living Quill hears the challenge while the current2298 copy is held, then acknowledges adjournment and keeps the prisoner alive in reviewed custody |
| 14 | Actual witnessed local execution, not area departure or global noon. Actual death observed after a valid pending execution intent |
| 15 | Accepted testimony actually delivered, or its declared physical transcript projection actually read; distinguish source and prisoner identity |
| 16 | Actual acquisition/history of the existing review copy, even if this precedes road start. Do not reset/refill the earlier helper; `docket_2298_held` is current possession at use time |
| 20 | Actual mine/Mouth arrival; do not imply a full settlement crowd was simulated |
| 30 | Actual knocking encountered, warning acknowledged, explicit valid confirming action; timer additionally requires living functional Blevins. Do not display a final call before it occurred |
| 40 | Successful staged descent and observed player arrival at supported Nine-level floor |
| 45 | The actual living cohort found below, counted individually; no inferred feeding testimony from the counter alone |
| 50 | Actual arrival at the sealed gallery. Living Dorn speaks only when present and eligible; do not imply deeper access |
| 51 | Personal undertaking mutually acknowledged **and all eleven actually safe at surface**; town ratification remains absent |
| 52 | All eleven safe first, then actual represented inner-break collapse observed. This is not the Mouth firing control |
| 53 | Explicit informed player order, all eleven still below, living functional Blevins, and actual Mouth sealing observed. Record `PlayerOrdered=true` only here |
| 56 | Locally armed, visibly warned deadline expires under eligible conditions, Blevins actually fires and the Mouth closes with the shift below. `PlayerOrdered=false` |
| 54 | Actual gallery/cot lamp acquisition; origin tracked, actual possession distinct from history; no assumed hostile Dorn speech for the cot item |
| 60 | Actual hoist-house silver/instruction inspection. No claim that Blevins's private motive was proved |
| 100 | Explicit departure after one observed terminal mine outcome; court, evidence and lamp remain optional |

**A real source-mapping gap needs a native-only projection:** `ways_through` permits bringing the shift up and leaving the break; `cannot_break` says attacking Dorn cannot prevent rescue. Yet source terminal51 requires a pledge and52 requires blasting. Do not falsely set either to complete an unpledged/unblasted rescue. Propose native-only stage**57**, documented in the ledger, for `saved-without-pledge-or-blast`, with journal `The eleven miners reached the surface. You made no gallery undertaking and did not blast the break.` **Do not commit57 automatically on surface arrival.** Preserve rescued-person facts and any pending break plan so actual52 remains available after rescue. Commit57 only after an explicit decision to leave without blasting or abandon the pending break plan, with no undertaking or blast falsely claimed. Permit100 after57 too. This encodes an existing authored route, not a new canon outcome or a JSON amendment.

For actual adverse gameplay deaths, propose native-only stage**58** rather than falsely setting an all-eleven stage or leaving a permanent impossible objective. It is available only after at least one **observed actual death**, all eleven distinct cohort references have a known physical fate, and every surviving miner is verified safe at the surface. If all eleven actually died, the surviving count is zero and every death must still be observed/tracked. Use a technical counted journal reporting actual survivors and observed deaths/cause; no all-eleven rescue speech/flag or fabricated player-order blame. Permit100 after58. A missing alias, failed movement, disabled miner, unobserved fate or incomplete rescue batch cannot qualify as a death or pass58: these remain recoverable engineering failures. `PactMade` and any later safe inner-break action remain separately tracked;58 does not claim a full rescue or rewrite the existing five primary story outcomes. This is an adverse-state truthfulness adapter, not newly authored people or backstory.

## The eleven: physical proof, not an offscreen counter

Use **eleven actual persistent unnamed miner roles/aliases**, each with its own real actor reference and supported below/cage/surface locations. One corresponds to the existing reference-only Pell relationship; it receives no new personality, surname or speech. Keep all eleven inspectable at the rescue staging/surface area. A counter or two representative actors plus nine invisible successes does not establish `shift_saved` or justify `All eleven`.

Record each person's actual life and successful arrival. Do not grant salvation on a MoveTo request alone, disabled reference, missing alias, duplicate actor, an actor still below, or a spawned replacement for someone killed. `shift_saved` requires eleven distinct assigned people alive, enabled and observed within their supported surface rescue area. If engineering intentionally represents fewer people, it must label that limit and cannot claim full eleven-person native acceptance; that is an unmet rescue gate, not scope permission to fake the count.

The rescue lift is one bounded batch scene: **all surviving unresolved assigned miners** must be ready, the hoist/control/arrival markers present, and the player explicitly confirms. Separately observed dead miners retain their actual tracked fate and are not transport-roster members; this permits the narrowly eligible58 path without pretending dead people must board. A missing reference, unobserved fate or failed movement is neither a death nor readiness. A rescue-transit pending state pauses the deadline while movement/arrival is verified. If only some moves succeed, retain individual facts and retry only unfinished arrivals with usable controls. Do not return moved miners below, duplicate them, or allow a timeout/seal to claim all eleven were still trapped. No irreversible mine outcome can interleave with the in-progress rescue batch. The engineering ledger must show the exclusive scene owner and real failure recovery.

If the Mouth is sealed, represent the actual blocked entrance/cage and track the below cohort as **entombed**, not automatically eleven observed corpses. Knocking stopping and fatal future implications do not prove an individually witnessed death count. Do not kill/disable miners merely to manufacture a desired counter. Actual separately observed casualties retain their real cause; they are not credited to the player's order unless that action actually caused them.

## Gallows: rope, money, review and refusal

- Provide a real walk-around bypass and an ordinary paid toll control from the accepted `toll_board` rates; a person on foot pays two caps, not sixty. The sixty-cap mercy fine is a separate action. No mandatory payment, perk or threatened prisoner is needed to reach the mine.
- Rope rescue is an actual supported hit/destruction interaction on a visible rope attachment target, not a menu choice setting11. Use an actual eligible player shot, show the rope broken and safely free the living prisoner; verify arrival. No real ragdoll fall or new animation system is required. Do not stage a fall onto unsupported geometry.
- `quill_after_shot` claims a forty-yard shot and a recorded four-cap fine. Gate the whole line on actually represented range/context and a real recording action; otherwise omit it and use technical status `The rope is broken. The prisoner is alive and free.` No global Dominion war or instant attack follows merely from talking/refusal. Fine incurred and fine paid are separate facts; never remove nonexistent caps or repeat it.
- Payment verifies funds, actual once-only deduction, actual release and receipt before12. Failed/stale payment never releases a corpse or completes a purchase.
- Docket challenge checks current exact copy possession both before and after the modal exchange, living eligible Quill and actual living prisoner. Actual adjournment/custody follows before13. **Stage13 alone does not earn the full `quill_shamed` flag:** its canonical meaning also requires both the current and2298 dockets actually sent for review. Keep `ReferralPending` separate, represent the actual referral and acknowledge it before setting the conjunction flag. Failed/pending referral does not undo the earned adjournment or living custody and retries only that unfinished referral; it cannot duplicate/remove another held copy as a substitute. The old case proves a wrongful2298 hanging and both officials' culpability, not this prisoner's innocence. Pritchard's prior acquisition record cannot substitute for held evidence.
- The source `(Watch)` option can start a short clearly labelled **local execution scene** with a readable imminent-drop indication and opportunity to intervene. No silent wall-clock death at noon. Leaving the scene area, opening a menu, unloading or cancelling pauses/prevents its progress; bypassing never sets14. Use a persistent pending intent, safe gallows position and actual death acknowledgment before execution status. Quill/prisoner absent/dead or an invalid target fails closed. It is not a player seal order, and it never starts the mine timer.
- SourceQuill after-drop/stage14 assumes noon and steady witnessing. Without an explicitly represented temporal/witness scene, omit that compound line and use `The court carried out the sentence while you remained at the wagon.` Actual prisoner paper/evidence remains independent where established.

No new rescue-assistance feature is promised. `dunmore_freed` records his authored future favor; any later whistle/call/fair/porch service remains a later implementation, clearly outside this road. The flag `neck_owed` requires actual freedom and the eligible survivor, not an adjourned prisoner still in custody. `rope_shot`'s full Dominion-record meaning requires the actual recording context; track a shot separately if Quill cannot record it.

## A real local warning and safe active-time deadline

Use the exact `roark_deadline_warning` before an explicit accepted confirming button. Merely opening it, asking questions, hearing Blevins argue, looking at a note or choosing `Not yet. I need to prepare.` does not arm anything. A native displayed countdown/final-call UI is a mandatory prerequisite before any56 path. Its finite budget is an explicit test tuning value, not canon dawn or a duration inferred from the four-minute hoist speech. Validate sufficient ordinary play opportunity and disclose the actual active-time rule.

Count only eligible **active gameplay time while the player is physically in this road's locally loaded Mouth/Nine/gallery zones**. Pause in all menus/modal dialogue, during acknowledged scripted transit/rescue scenes, when outside this local episode, unloaded, travelling to Mercy/another road, and across save/reload downtime. Resume remaining time without adding absent elapsed time. If menu/load/local-state detection is uncertain, fail closed and pause. Never derive expiry from game-hour/global calendar or the fair being called. Leaving the warned road does not run it to destruction elsewhere.

At expiry recheck Blevins alive, enabled, present, noncombat and actually able to operate the real firing control; charges/targets still available; all eleven still below; no rescue/other resolution/pending scene. A functional final-call acknowledgment is required, not a ghost turning a key after death. If those conditions fail, do not set56 or catch up a hidden detonation later; retain an explicit paused/blocked state and give renewed visible warning before any eligible resumed firing.

The explicit53 path requires locally heard knocking, acknowledged warning, an exact informed order, all eleven below and the same functional firing scene. Recheck after the confirmation. Blevins's death removes both his order-execution and deadline firing paths; no invented player detonation route substitutes for a dead operator. His authored body key and player/Roark hoist fallback still permit rescue. If Roark is dead but Blevins lives, present the exact accepted warning as clearly labelled action UI without attributing speech to her. If Blevins is dead, do not quote him preparing to fire or arm a nonexistent deadline; use a separate rescue-accepted fact and permit descent without falsely claiming30's warning occurred.

## Hoist, rescue, break and Dorn

Use real controls for descent, call cage and return, with explicit acknowledgment and safe supported target positions. A short staged transition may represent `roark_cage`'s four minutes; do not require eight minutes of inactivity or claim continuous physical lift simulation. With Roark unavailable, the player uses the same physical controls; no corpse lowers a cage. Missing key/control/marker or failed movement is a recoverable actual obstacle, not a stage advancement.

At the break the player can find/retrieve the eleven without entering Dorn's sealed door. Main rescue does not require a pledge, optional lamp theft, attacking her or joining an ancillary faction. Dorn attacked may close/withdraw behind her door; keep the shift/cage accessible and track her actual life rather than invulnerably resurrecting her. No passage beyond the sealed door is built.

Dorn's promise covers her gallery/House and the player's **own** passage/carrying terms. It does not bind Red Hollow, establish universal first contact, answer ancestry/origins or erase broader memory. No Deep access, Rider identity, hidden-player recognition, main-faction allegiance or new culture exposition is authorized. Exact `dorn_terms`, `dorn_no_head`, `dorn_sworn` supply the necessary bounded exchange. Record actual acknowledged `PactMade` and terms pending delivery separately;51 waits for all-eleven rescue. Saying the oath does not teleport survivors or ratify a town agreement.

For52, choosing `They come up. Then I blow the break.` sets a **plan**, not the source's immediate completed stage. Rescue the eleven first, then return to a safe inner-break control and observe the represented rubble barrier. This closes the break between mine and gallery, not the Mouth with people inside. Keep the two firing controls, targets and outcome locks distinct. Anyone still in the blast area, unresolved miner arrival, failed barrier display or missing charge scene blocks52. No spring-time mine reopening, deeper collapse physics or actual hundred-ton measurement is claimed.

The lamp has two accepted possible origins: gallery or Blevins's cot. A cot acquisition cannot trigger `dorn_lamp` as if Dorn watched theft. That reply requires actual living Dorn witnessing the gallery act. Acquisition/current inventory/origin and optional emitted-light representation are separate. A lit world stand-in plus inventory item is not proof of a working carried light; disclose the actual implementation. Lamp54 never completes the mine, sets `shift_saved` or auto-starts a future sale to Brigg/Grey/the fair.

## Evidence without invented documents or omniscient proof

The accepted full documents are the four listed above. `condemned_paper`, `greer_silver` and `smokeless_lamp` are **quest evidence descriptors**, not fully authored documents in `documents.json`. Do not invent a signed letter, paymaster identity, quantity or new witness to fill them.

For the paper path after a real prisoner statement exists, project a clearly labelled transcript using an exact accepted excerpt: Dunmore's `dunmore_tells`; for a replacement Cutter, the relevant `cutter_rope`/`_missed` excerpt beginning `We were paid` and ending at the accepted statement's end, omitting encounter-recognition preamble. Register the native transcript projection, prisoner/context and original node; reading it actually grants15. Do not portray the unrelated `quill_docket` as that testimony: it proves charge/procedure, not the silver payment. If no eligible prisoner/statement existed, do not create this evidence from nothing; the optional15 path can be unavailable without blocking the mine.

The desk inspection may show stamped silver and the already authored instruction `keep the Mouth shut through winter` from stage60. Use technical status `You found stamped silver and an instruction to keep the Mouth shut through winter.` Do not project `He would have done it for nothing` as discovered objective proof, name Vane from an unsigned mark or replace seeing silver with merely asking Blevins about the lamp. The shovel's PELL signature remains the accepted reference, not a new actor biography.

## Truthful journals and aftermath

Original logs/spoken aftermath contain facts that need actual context. Native technical projections, separate from NPC quotations:

- Stage10 without represented noon: `You reached the Dominion toll-gate. A prisoner is on the gallows wagon.` Use only if the actual prisoner exists; otherwise report the gate alone.
- Stage15 from oral testimony: `You heard how the Cutters were paid to watch for Gantt's delayed freight and seize his pouch.` A read transcript records that source, not a conversation never heard.
- Stage20 without a whole staged town/crowd: `You reached the chained Mouth at Red Hollow.`
- Stage30 before any final call has actually played: `You accepted the warned local rescue deadline. The shift is still below.`
- Stage40 represented hoist: `You reached the Nine level by the cage.` Do not assert a measured physical four-hundred-foot travel.
- Stage45 actual count: `You found eleven miners alive at the break in the rock.` Only after eleven are actually found; no feeding/hidden motive inferred from count.
- Stage50 without eligible Dorn present: `You reached the cut gallery and its sealed stone door.`
- Stage51 only after physical rescue: retain the accepted personal-undertaking journal, without a ratified-town claim.
- Stage52 without measured tonnage/roof event: `The eleven miners reached the surface. You then blasted the break closed.` Only after both facts are observed.
- Stage53 without represented dawn/morning: `You ordered the Mouth sealed with the shift below. Blevins carried out the order.` Both true or neither claimed.
- Stage56: `The warned local deadline expired. Blevins sealed the Mouth with the shift below. You gave no order.` Never replace this with53's blame.

`roark_after_line` claims an actual code sent/reply received and Pell asleep in her kitchen. Eleven arrivals alone prove none of those later scenes. Show the whole line only if those contexts are represented and acknowledged. Otherwise its exact accepted ending beginning `I don't know what you did down there.` may be used after the living Roark actually receives the personal-line/rescue account; no kitchen/sleep/code claim is smuggled in. Without that delivery use technical saved/pact status, not invented speech.

`roark_after_break` attributes a later report to Pell; show it only after that actual survivor/report context, otherwise use the neutral52 status. Roark's53/56 aftermath additionally claims near-noon listening, a long aftermath and differing responsibility. Without represented time/witness context omit the compound quote and use the distinct technical53/56 logs. Never attribute an order to an expired timer, or speak through dead Roark. Captive death/partial rescue cannot play an `all eleven` response.

## Mercy report, integration and release boundary

After an observed mine terminal outcome, explicit return completes100. Reuse exact `pritchard_hears_pike_after_fair` speech if mine payment evidence is actually known, `_unknown` otherwise, under a declared road-completion projection rather than its original post-fair guard. No fair has occurred. Court testimony `silver_road` is not mine desk evidence `silver_mine`; report these, survivor fate, personal undertaking and lamp separately. Carrying a lamp never proves a paymaster, town agreement or player origin.

Preserve actual SQ01, Greenwater, Night Mail, briefing and optional2298-copy behavior in the eventual composed candidate. Use an explicit at-most-four-choice report selector as needed. Cancelled, unsupported or stale modal results close that activation; they cannot fall through into another report/briefing or commit a transfer. Current copy possession is checked dynamically; stage16/history must survive without pretending the copy is still held after drop/removal. Never mutate an earlier helper's accepted acquisition merely to start this road.

Once this road is actually built in a separately approved future candidate, all candidate-only Mercy hub/journal/Act1Guide/travel/completion availability labels must agree that all three roads are available and the fair remains unavailable. Do not update current Night Mail/016b/a8/b280 labels or manifests now, or infer any native pass from this design. No Chapter2-wide completion, fair scene, later epilogue, spring repair, Dorn cultural chapter or main-faction commitment is included.

## Acceptance gates for the future single implementation

1. Independent narrative/engineering review checks the explicit native57/58 adapters and their narrow eligibility; then root alone decides when to dispatch. The contract supplies the proposed handling rather than leaving those cases to invented NPC speech. No parallel Charles job is authorized here.
2. Engineering supplies exact allocation/alias/physical-effect/text-projection/state/timer ledger and actual supported floor/marker geometry. Full candidate verifier runs before output writes; unchanged earlier manifests/refusal tests remain frozen. Changed/new runtime gets real fresh compilation later, with no assumed script count.
3. Actual-controller tests cover court bypass/shot/payment/review/watch; real earlier-prisoner outcomes/deaths; current-possession docket; transcript versus oral evidence; every mine outcome and lamp origin; no-Dorn/no-Roark/no-Blevins rescue; delayed/refused moves, partial batch arrival, death before/after acknowledgment, cancelled/stale menu, payment/item failure, custody and save/reload. No dialogue click alone proves rope, rescue, collapse or death.
4. Timer adversarial tests explicitly cover every relevant menu/modal, leaving/unloading/other road, scripted transit, save/load downtime, global-time change/fair call, blocked/incombat/dead operator and interrupted final warning. None can silently become a timeout or an explicit order. Recheck an acknowledged finite final call before actual sealing.
5. Only after source/build/compile/readback acceptance does separately authorized native QA walk a real bypass/nonviolent rescue, physical rope intervention, docket adjournment and each mining consequence with normal stats. Count all eleven actual aliases on the surface for full rescue acceptance; distinguish entombment from observed deaths. Capture actionable markers, countdown, evidence rendering, actual control effects, aftermath, Mercy report and persistence.

**Done for this road:** an ordinary player can pass or intervene at the court, confront the mine crisis, physically rescue the shift or knowingly suffer/choose its loss, meet Dorn within the approved bounds if desired, see the consequences and return a truthful report. This document prepares that work; it neither builds it nor starts another engineering run.
