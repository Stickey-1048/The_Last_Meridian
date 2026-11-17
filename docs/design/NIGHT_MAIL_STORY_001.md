# Next playable road contract: The Night Mail

Iris, 17 November 2026. **Workspace design contract for one further playable Act I road. No implementation, native pass, canon amendment, installation or dispatch is performed here.** Story progress takes priority over the stopped landscape proposal.

## Decision and actual dependencies inspected

Choose **Iron Junction / MQ02A / The Night Mail** next. It has three named actors, four meaningful main resolutions, optional evidence and a second consequential inspection decision. Its forgery investigation pays off the opening's unsafe equipment and false certification directly. A bounded rail-yard/Cut greybox can reuse the accepted Greenwater pattern of acknowledged staged travel, separate physical action and observed consequence; it does not require completed train physics.

Red Hollow remains important but brings a linked hanging/rope action, warned local deadline, hoist, eleven miners and the narrowly permitted Dorn encounter. Its optional docket is already authored, but that does not make all those mechanics ready. Iron Junction is the stronger next dependency set now that one complete staged road framework exists. Approved creative decisions20/22 explicitly retain grounded/station alternatives when duel/vehicle spectacle is unsupported; no new canon decision is needed to bound this prototype.

Read actual accepted files in `work/greenwater-repair-review`, exact HEAD **016b2b4005203ba180b908fb310a1653a95f934f**: the unchanged d142104 Act I quest/talk/character/documents, `ACT1_CREATIVE_DECISIONS_2026-11-16.md`, actual Greenwater contract, mapping, independent narrative review, repair receipt, candidate UI and SQ01 state definitions. The current plan already implements only Greenwater; there is no native Night Mail contract to duplicate. Do not use the stale pre-decision question list to reopen Dole's identity, Lockridge's authorship or the opening wreck's cause.

The coordinator reports Greenwater016b source/build/artifact clear, **native pending**. Reuse its repaired design patterns after code review, not an assumption that its stand-in tests prove native behavior. Do not revise or re-dispatch Greenwater under this contract. Engineering starts a new composed candidate from the coordinator-selected accepted baseline and preserves every frozen earlier fallback and verifier.

## Concrete deliverable and bounded footprint

One separately accessible **Night Mail story greybox**: (1) Iron Junction gate/office/desk, (2) a stationary Old Contrary footplate with ordinary controls, (3) Sawtooth Cut stop/parley/combat space, (4) a short accessible boxcar-tabernacle evidence siding and (5) an arrival/return platform with visible mail/medicine cargo configurations. Simple existing floor pieces, barriers, crates, engine stand-ins and labels are sufficient. Three canonical actors plus at most three anonymous Black Rail opponents represent the encounter; dialogue's thirty rifles is not a claim that thirty AI actors have been built. No polished scenery, voice acting, rotating office, moving-engine actor attachment, full transport system or new landscape is a release prerequisite.

Keep those five zones in one new isolated test cell, with actual short walkable connections where appropriate and explicit staged scene transitions for the journey. Add only the Mercy entry/return/report integration outside it. No regional railway, second settlement exterior, added cells for future chapters or rearrangement of the owner town is part of this footprint. Engineering returns the exact reference/marker list and collision-supported coordinates; this narrative brief does not pretend an unaudited coordinate sketch is usable geometry.

At Mercy, an explicit `Iron Junction story test` activation becomes available after the actual opening dispatch/debrief gates, independently of completing Greenwater or acquiring a Red Hollow copy. A confirmed trip brings the player to the yard gate; declining/cancelling does nothing. Returning unresolved is always possible and does not complete the quest. Never require an inventory spike that the existing briefing never actually issued: document this technical travel projection of the accepted commissioned rail trip rather than pretending the source's token precondition is implemented.

Target a complete story playthrough rather than a fixed duration. Measure the actual first-run time. Do not pad a three-actor story with long walks, forced waits or repeated boxes to advertise thirty minutes.

## Accepted sources: stable IDs and text paths

All narrative paths below are under `assets/incoming/act1/story/` in the accepted016b tree; narrative identity remains d142104.

| Input | Exact accepted IDs |
|---|---|
| `quests/tlm_mq02a.json` | `key=mq02a`, `id=TLM_MQ02A`, title `The Night Mail`; all stages, objectives, choices, evidence, flags and `cannot_break` |
| `talk/tlm_mq02a.json`, gate/assignment | `lockridge_default`, `lockridge_gate`, `lockridge_gate_alerted`, `lockridge_gate_sold`, `lockridge_dole`, `lockridge_rails`, `lockridge_hired` |
| Same, train | `tarrow_default`, `tarrow_footplate`, `tarrow_cut_before`, `tarrow_in_cut`, `tarrow_ran`, `tarrow_backed`, `tarrow_walking` |
| Same, preacher | `dole_default`, `dole_sermon`, `dole_name`, `dole_silver`, `dole_share`, `dole_face` |
| Same, aftermath/forgery | `lockridge_after_ran`, `lockridge_after_dole`, `lockridge_after_sold`, `lockridge_hymnal`, `lockridge_stamp` |
| `documents.json` | Whole `yard_rules`, `hymn_chalk`, `hymnal_flyleaf` text; physical stamp/collection silver are evidence references specified by the quest, not missing long documents |
| `characters.json` | `lockridge`: Augusta Lockridge, Gussie; `tarrow`: Wilhelmina Tupper, Billie; `dole`: Ezekiel Dole, Preacher Dole. Reuben Ostrander is the same actor's legal identity, never a second actor |
| `talk/tlm_mq02.json` | `pritchard_road_rail`; exact text of `pritchard_hears_rail_after_fair` and `_unknown` for explicitly documented native completion-report projection |

Preserve character speech/documents exactly, splitting boxes where actual rendered speaker-prefix length requires it. No automatic import of the Python selector, source priorities or source button effects is claimed. Native projection must recheck real conditions and commit facts after their action succeeds. Every intentional context split/excerpt or neutral technical substitute below is recorded in the mapping ledger; accepted JSON remains unchanged.

## The playable sequence

| Player action | Response/discovery | Real consequence or next action |
|---|---|---|
| Arrive and read the gate rules | `yard_rules`; Lockridge's appropriate gate greeting | A named yardmaster has a specific mail/medicine job. The player can refuse without automatic combat or a missed-train disaster |
| Ask about hymn marks/inspections; accept `I'll ride your mail.` | `lockridge_dole`, `lockridge_rails`, then acknowledged `lockridge_hired` | Objective targets the actual footplate. No quest completion or time limit yet |
| Walk onto the footplate; speak to Billie; use the departure control | `tarrow_footplate` / optional `tarrow_cut_before` | Confirmed staged travel reaches the Cut, with lanterns, visible rail obstruction, Dole and a safe parley route |
| Stop/get down, question Dole or inspect the nearby evidence siding | `dole_sermon`, optional `dole_name` / `dole_silver`; physical flyleaf/silver | The player may discover who was presumed dead and that a square-mark payment chain exists. Identity and paymaster knowledge are separate |
| Choose run / fight / sell / back out | Exact accepted options and proper warnings; relevant living participants only | Actual staged transit/cargo configuration, physical combat death/retreat, one-time paid seizure, or safe reverse/withheld delivery |
| Return to yard and inspect the real desk drawer, optionally show the hymnal | `lockridge_stamp` in a truthful living context | The player finds the actual stamp and can preserve forgery, obtain Lockridge's own signatures or carry proof to Pritchard |
| Leave after a resolved mail encounter; return/report | Actual cargo/engine/cast state; knowledge-sensitive Pritchard report | Night Mail complete with a persistent result and optional forgery consequences; no fair or Red Hollow becomes playable |

## State and stage proposal

Create the actual native `TLM_MQ02A` only after confirming no FormKey/editor-ID conflict. Use own fresh aliases/globals/scripts, with an explicit tested adapter to the existing MQ01/SQ01/Mercy flows. Do not write SQ01's prior evidence or outcome to make a preferred greeting appear.

**Independent persisted facts:** `EncounterOutcome` = none / run / Dole-defeated / sold / backed-out; `MailState` = on-train / delivered / retained-at-yard / seized; `EngineState` = sound-prototype / run-damaged; `DoleDeathObserved` and actual killer/context; `DoleNameKnown`; `SilverRailKnown`; `ForgeryFound`; `StampDecision` = none / continued / countersigned / taken-for-report; `StampInPlayerCustody`; `StampDelivered`; `YardAuthorityWithdrawn`; `SharePaid`; `DeparturePending`; `ScenePending`; `RoadReported`. Actual actor life and possession are checked at use time, not inferred from an old stage. Pending scenes are persistent and exclusive, but not completed outcomes.

| Accepted stage | Native trigger and required observation |
|---|---|
| 10 | Actual confirmed arrival at the yard; objective10. A failed move does not claim arrival |
| 20 | Assignment response delivered/acknowledged with living Lockridge. If she is dead, source explicitly permits Billie to take the train out on her own word: a clearly labelled `Board the Night Mail` action starts that existing fallback without a fabricated dead-yardmaster conversation |
| 30 | Player physically reaches the real footplate and begins the acknowledged departure; boarding alone does not resolve a journey |
| 40 | Confirmed player arrival at the Cut and encounter pieces observed available. No timer or forced QUICK response |
| 41 | Approved run/jump represented by a confirmed, bounded staged scene; real arrival/cargo delivery and damaged-engine display both observed. Never just the original choice click |
| 42 | Actual Dole death defeats the encounter, with credit/context recorded. Opponents are actually defeated or visibly staged to retreat; this stage alone does not assert medicine delivery |
| 43 | Explicit accepted share bargain, actual one-time150-cap payment, safe Billie release if alive and actual transfer/seizure of mail/medicine shown. Do not pay or seize on cancellation/stale target |
| 44 | Confirmed reverse/return outcome with cargo safely retained and delivery withheld. `line_closed` reflects this chosen unresolved obstruction; no unearned deaths |
| 50 | Actual inspection of collection silver/body evidence or delivered `dole_silver` admission; square-mark evidence learned, not identity of its ultimate funder |
| 55 | Actual flyleaf read or Dole's delivered name revelation. Show public/legal identity distinction; do not rename all interfaces before the discovery |
| 60 | Actual desk-drawer inspection/stamp discovery, or the acknowledged living Lockridge showing it. No proof merely from possessing an unrelated letter |
| 61 | Explicit choice to leave the stamp in continued use, physically still in yard custody; it does not promise a safe fleet |
| 62 | Actual represented countersigning/record-review scene finishes; visible inspection-status change and suspect stock held from dispatch. Do not assert a year of signatures appeared on a cancelled box |
| 63 | Stamp actually transferred into player custody after the explicit report choice. Stage63 alone is **not** `lockridge_reported`; that flag requires actual living-Pritchard receipt |
| 100 | Explicit departure after one completed encounter outcome41/42/43/44, with its current mail/cast consequences visible. Optional silver/identity/forgery work cannot block completion |

Stages41/42/43/44 are exclusive main encounter resolutions. Stage50/55/60 may occur in any physically possible order, before or after resolution; optional inspection decisions61/62/63 are exclusive and independent of the mail choice. A later ordinary death must not overwrite a completed run/sale/back-out with42. A failed/cancelled scene or half-finished payment/transit is not an outcome. Test save/load while pending without duplicating caps, transfers or scene effects.

After defeating Dole, actual forward transit can deliver the mail; a physical return action can retain it at the yard instead. Both retain `EncounterOutcome=Dole-defeated`, not a second41/44. Show the player's choice and the cargo fact plainly. This separates authored Dole defeat from an unearned `mail_through` flag; neither incidental death nor leaving the area silently delivers medicine. Completion after42 is allowed by source and does not require the optional investigation. A retained-at-yard result remains a real withheld delivery, not a narrated rescue.

Accepted flags map explicitly: `mail_through` only on observed delivery, `mail_sold` only on the completed paid seizure, `line_closed` on the backed-out obstruction, `dole_lives` as actual living Dole plus this encounter's recognition (not the player's childhood), `silver_rail`/`ostrander_known` as earned knowledge, `lockridge_stamping`/`lockridge_signed` after those actual decisions. `lockridge_reported` requires **both actual Pritchard receipt (`StampDelivered`) and acknowledged visible yard-without-master aftermath (`YardAuthorityWithdrawn`)**. Preserve the taken-but-not-delivered state across travel/save/drop; inventory acquisition is not delivery. Prevent repeat stamp decisions even if the stamp is later dropped.

## Alias and physical reference inventory

- **Named cast:** Lockridge, Billie, Dole; public Dole display remains Preacher/Ezekiel Dole until identity is actually learned. His legal and assumed names never produce duplicate living actors.
- **Optional anonymous opponents:** up to three Black Rail actors in a bounded combat group, with no new names or faction identity. Calibrate a winnable ordinary Fallout fight for normal initial characters. They do not attack because the player refused Lockridge or left parley. Their retaliation handler must not recursively restart its own combat events.
- **Yard:** arrival/return marker on audited support, rules notice, Lockridge's actual accessible drawer, stamp, represented inspection stock/status. No rotating-office physics needed.
- **Train/Cut:** footplate entry, departure, forward/run and reverse controls; Cut arrival marker; safe step-down route; Dole position; escape/retreat markers; cargo and run-damaged engine configurations. Real target availability/distance/support must be observed before moving a player/actor or committing a state.
- **Evidence siding:** actually walkable chapel/tabernacle stand-in with collection plate, readable flyleaf access and a chalked-boiler notice. Evidence remains accessible after the relevant death; no lockpicking/perk gate or required optional kill.
- **Delivery/report:** arrival platform with visibly delivered medicine/mail; Mercy return marker and actual Pritchard receipt. Keep Pritchard's existing exterior reference, MQ01/SQ01 and Greenwater aliases intact.

## Main routes and native feasibility boundary

**Run the gap, nonviolent:** player can return to the footplate from parley, use the stoke/run control and explicitly confirm. The greybox may stage the authored leap with a short fade/relocation and before/after engine/cargo display. Clearly label that it represents a scene; it is not a tested moving-engine ride or simulated airborne locomotive. Only successful arrival and delivered cargo can set41/`mail_through`. If Billie lives, her actual delivered `tarrow_ran` and Lockridge's appropriate aftermath may reflect the authored leap. With dead Billie, the accepted player-operated-regulator fallback remains usable without Billie's voice or a journal claiming she drove. If a safe staged run cannot be made, keep the backed-out/grounded progression usable and return the exact feasibility failure; do not silently invent repaired rails, a different rescue, or claim all four outcomes passed.

**Get down and fight:** Dole talks before aggression on his parley route; `Stand aside`/`dole_face` makes the confrontation legible. No quick-time duel or invulnerable antagonist is needed. Standard player-initiated shooting from the footplate is allowed and counts as facing him in this encounter, as source says. Stage42 follows real death/defeat, never a speech choice or disabled living actor. Combat/retreat must actually leave the line traversable. Preserve physical evidence on the corpse/siding; his death does not erase the stamp, hymnal or Lockridge's testimony. A later murder after another resolution cannot retroactively replace that resolution.

**Sell the mail:** after hearing Dole's actual share terms, `Done.` can commit the once-only150 caps and seizure. Billie, if alive, is visibly moved to a safe return/walking position before reporting she walked home; do not kill her to clear the scene. Show withheld medicine and stolen payroll. Dole's offer is a third of the pay-chest; the accepted native grant is150 caps, with no invented wider economy value. No false delivery flag, simultaneous run/back-out, or repeat payment. `lockridge_after_sold` requires a separately acknowledged Billie return and report **and** explicitly represented temporal context for its claim that she arrived at four this morning. A safe successful MoveTo alone proves neither. Otherwise omit that quote and use the neutral sale status below; no global clock advance or new character speech is required.

**Back out, nonviolent/refusal:** player can decline at the yard, leave before boarding or choose reverse at the Cut. Only the explicit completed reverse commits44 and closes the obstructed line. Declining/unboarded departure remains unresolved, with no offscreen wreck, timer or automatic medicine loss. The held cargo remains visibly safe but undelivered. Do not read `Not tonight` as choosing a different later chapter or consenting to a fight.

## Optional forgery decision and genuine source fidelity hazards

These are actual conditional hazards in accepted prose/metadata, not permission to decide new canon. Keep them explicit in the native mapping and independent review:

1. **Opening neglect versus later sabotage.** Canon is settled: Lockridge forged unsafe clearances; Chapter1's wreck is neglected equipment/fraud, while Dole's later pulled rails are intentional crimes. Hymn marks on later wrecks do not prove he sabotaged the opening or that every accident was coordinated. Identity, forgery and payment are separate discoveries.
2. **`lockridge_hymnal` says `He's ALIVE?`.** It cannot play after actual Dole death, or merely because55 came from oral admission without a current shown hymnal. Use that exact response only with the real book shown, living Lockridge and living Dole in its first discovery context. Otherwise the physically accessible drawer/stamp and `lockridge_stamp` can advance the optional decision without inventing a replacement surprised speech. No ghost dialogue is required.
3. **The kill choice's `later` field says nobody is left to say what the yard signed.** Taken as an objective fact it conflicts with surviving records and testimony. Do not project it as a universal journal/report claim. Report only the tracked loss of Dole and preserve other proof. This is a known context restriction for review, not a new explanation of the plot.
4. **Compound survivor claims.** `tarrow_ran`, `tarrow_backed`, `tarrow_walking`, `lockridge_after_sold` and stage41/43/44/63 logs assume particular people alive and actions witnessed. Filter truthfully. Technical journal alternatives when those assumptions fail are supplied below; do not resurrect someone or have a corpse take payment/speak.
5. **Stamp custody versus report.** Accepted stage63 text describes taking the stamp, but `lockridge_reported` describes it in Pritchard's hands and a leaderless yard. Delay that conjunction flag until actual receipt **and** acknowledged authority withdrawal. Possession alone cannot claim delivery; receipt alone cannot claim the yard lacks a master. No Brigg/fair scene is included.

Two exact dead-Billie context projections avoid another missing-writing loop. Do not play `lockridge_hired` when Billie is already dead: acknowledge the accepted assignment with technical UI `Assignment accepted. Board the Night Mail.` and preserve the player-operated-regulator fallback. For `dole_share` with dead Billie, omit its first sentence promising her safe walk; use the exact accepted remainder beginning `The physic goes up the hill:` and ending `step off the footplate.` Display the existing150-cap offer separately as technical UI `Offer: 150 caps.` No new NPC speech is authored. The source's ordinary whole-line version remains when Billie is alive and a safe release can be delivered. Every such excerpt is explicit in the mapping ledger and independently checked.

`Keep stamping` is a knowingly compromised choice, not a free repair; show unchanged suspect dispatch status. **Both Keep stamping61 and Countersign62 require living, eligible Lockridge.** `Sign your own name` represents a countersigning/review scene and held suspect stock, not instant magical track repair. `Pritchard gets the stamp` transfers real evidence and permits an actual later handoff. Optional drawer proof remains obtainable if Lockridge is dead or hostile; omit unavailable continued-use/countersigning choices. Without her, taking evidence for report or leaving it undecided remains possible without her spoken menu. No new legal acquittal, automatic replacement clerk, resurrected yardmaster or replacement named envoy is authorized.

The report aftermath must be concrete: for example, an actual changed yard-dispatch status with Lockridge no longer performing dispatch-role actions, or a safely represented withdrawal. The mapping names the exact observed physical pieces and stopped role actions that establish `YardAuthorityWithdrawn`; record it only after checking those changes and acknowledgment. Do not kill her, silently disable her, falsely narrate departure, or conjure Brigg/a replacement to obtain the flag. If this aftermath fails after a real stamp receipt, retain `StampDelivered`, leave `lockridge_reported` pending and retry only the unfinished aftermath. Never reverse or duplicate the transfer. A pre-existing death is tracked as such, not an observed withdrawal scene fabricated after the fact.

Technical journal/status text for conditional projections, kept separate from character quotations:

- Stage20 fallback without a living Lockridge assignment: `You agreed to ride the Night Mail with the payroll and fever medicine.`
- Stage30 with dead Billie: `You boarded Old Contrary. The regulator is ready.`
- Stage50 from spoken admission rather than actual plate inspection: `Dole described square-marked silver paying for pulled rails.`
- Stage55 from oral identification rather than a read flyleaf: `Preacher Dole identified himself as Ostrander, Inspector of Way.`
- Dead-Billie run: `The Night Mail got through. The medicine and payroll arrived; the engine is damaged.`
- Dole otherwise dead: `Preacher Dole is dead. His death does not erase the yard's inspection records.` Do not assign the player a kill they did not make.
- Sale before any living-Billie report: `You accepted Dole's share. The payroll and medicine were taken from the train.`
- Reverse with prior casualties: `The train returned with its cargo undelivered. The obstruction at Sawtooth Cut remains.` Do not use `Nobody's dead` after a real casualty.
- Stamp taken: `You took the inspector's stamp as evidence. It has not yet been delivered to Pritchard.`
- Countersigning scene completed without a represented overnight clock: `Lockridge countersigned the reviewed entries in her own name. Suspect stock is held from dispatch.`

These neutral state descriptions avoid unsupported witness/timing/kill claims. They do not alter the accepted documents or add a player's past. No global time advance is required to show an ellipsis; never progress an unrelated unresolved road through a staged review scene.

The20/30/50/55 variants are gated by the actual source/context, not automatically substituted for physical evidence. Hearing Dole does not prove the player opened a hymnal, saw handwriting or inspected a full collection plate. Keep those discovery paths and their logs distinct.

## Death, custody, cancellation and persistence rules

Only the relevant participants gate an action. Lockridge dead does not block Billie/player boarding; Billie dead leaves actual regulator controls; Dole dead leaves forward/reverse travel and physical evidence; Pritchard unavailable delays receipt/report but not road completion. For a Dole death not credited to the player, record the real cause/context and use the neutral dead-state log, not `by the player's hand`. Do not globally require all three actors alive.

After every modal return, recheck player alive, road/current exclusive phase, participant alive/present/noncombat and actual target/reference availability before transfer, payment, combat, movement or outcome. Continue must mean only its documented button, with cancelled/unsupported returns closing without effects. A failed scene stays honestly pending/retryable only while its real controls remain usable. Verify arrival, actor transfer, cargo display and payment before recording completion; a destination failing after effects is not rollback.

Evidence knowledge is learned, not tied to continuing inventory ownership, except the stamp's actual physical custody for handoff. Readable flyleaf, observed silver and current stamp location must survive ordinary saving/loading and taking/dropping where allowed. Optional evidence never blocks an authored main route. No repeated caps, duplicate stamps, restarted encounter, rewritten earlier outcome or disposal of other-road evidence on re-entry.

## Mercy return, availability and end boundary

Return report reuses the exact text of `pritchard_hears_rail_after_fair` when silver evidence is known, or `_unknown` otherwise. As in the accepted Greenwater projection, document that the original post-fair condition is **not** imported: no fair has occurred. Report the actual mail outcome, Dole knowledge and stamp facts independently. Set this road's `RoadReported` and true stamp-receipt fact when earned; set the separate canonical report conjunction only after its acknowledged authority aftermath as specified above. Do not mark the other roads, fair, Chapter2 or ActI complete.

Pritchard's new report must coexist with SQ01, Greenwater report and briefing. Any report-selector/menu cancellation closes that activation with no subsequent automatic report or briefing. An explicit Later may lead to the documented next option; a cancelled/stale answer may not. Keep at most four visible choices per box and use an explicit selector if needed rather than hiding an older available report behind an unfinishable new one.

**Candidate-only technical availability must change consistently once both roads are built.** Current016b strings correctly say only Greenwater is playable; they would be false in the combined candidate. Update the new candidate's `SpecMercyBriefing.UiBriefingOnly`, `UiJournalComplete`, relevant footer in `SpecAct1`, Greenwater travel/completion availability and the new Night Mail controls/status together. Frozen016b/a8/b280 packages stay byte-for-byte unchanged. Suggested exact UI values:

- Hub: `Mercy briefing. Greenwater and Iron Junction are playable. Red Hollow and the fair are not.`
- Opening footer: `Opening complete. Greenwater and Iron Junction are playable.`
- Briefing journal: `Mercy briefing complete. Greenwater and Iron Junction are playable; Red Hollow and the fair are not.`
- Greenwater completion: `Greenwater road complete. Iron Junction is also playable; Red Hollow and the fair are not.`
- Night Mail completion: `Night Mail road complete. Greenwater remains playable; Red Hollow and the fair are not.`

These are future candidate availability labels, not a current claim that Iron Junction or Greenwater has passed native testing. Preserve all character speech and old fallback manifests. New candidate checks must explain intentional UI/source changes without weakening any earlier frozen verifier.

Also update the actual completed-road guide in the new candidate: `scripts/Source/User/TLM/Act1Guide.psc` must say `Greenwater and Iron Junction are available at their story test points. Red Hollow and the fair are not playable. Optional Mercy evidence and briefs remain available.` Declare that changed source for fresh compilation and candidate pins; immutable016b keeps its existing one-road guide.

Snapshot016b as the immutable baseline. The composed Night Mail candidate needs its own manifest, full verifier and explicit opt-in package/build path. Every changed/new script requires fresh compilation later; retain earlier PEX only where the actual reviewed source remains unchanged. Do not predeclare a script count, reuse old hashes for changed bytes, change frozen manifests, weaken old refusal fixtures or make preservation tests vacuous. Run the full new verifier before output writes/build. Native compile/build/artifact evidence belongs to the new candidate, never retroactively to016b.

## Narrow independent review corrections incorporated

This revision retains the original fidelity findings above and incorporates the accepted Nora/Sam corrections: conditional20/30/50/55 journals, living eligible Lockridge for61/62, actual Act1Guide availability, conjunctive receipt/authority aftermath, and separately observed Billie report/temporal context. These are context/provenance corrections to this contract, not new canon decisions or a revision of accepted016b source. Root has accepted these narrow edits; no additional broad review or owner decision is required before its separate engineering dispatch.

## Independent acceptance, not another information-only milestone

1. Engineering returns a concrete mapping/alias/stage/scene ledger and implements this one full road. Stop and return only genuinely missing canon/physical dependencies; do not ask again whether Ostrander lives or who forged the clearances. No further landscape scope joins this task.
2. Source tests use actual runtime/controller paths for all four outcomes, early refusal, dead key actors, boarding without the optional evidence, evidence before/after each resolution, greeting variants from real SQ01 state, all stamp decisions, taken-versus-received stamp, both knowledge-sensitive reports and regression of current Greenwater/SQ01 cancel behavior.
3. Adversarial checks interrupt every pending scene and modal step: stale branch, combat/death, missing/disabled destination, refused/delayed movement, failed payment/transfer, failed enable/disable and save/reload. Every outcome/display/caps/custody claim must match observed facts. No model-only pass or console-set stage is native evidence.
4. Licensed compile/build, exact VMAD/reference/property readback, artifact/runtime selection and preservation gates precede any separately authorized staging. All older fallback pins and packaging refusal tests remain valid for their own immutable inputs.
5. Native QA walks a complete nonviolent run and a backed-out route, then separately exercises actual Dole defeat, paid seizure, identity/silver discovery and forgery outcomes with normal character stats. Observe cargo/engine changes, usable controls, actual payments/receipt, readable evidence, actual return/report and reload persistence. Scene abstraction and absent moving-train physics are disclosed. A failed branch is repaired before promising that all four work.

**Done means:** the player takes a real job, investigates the rail crimes, chooses a consequential way through the Cut, sees the mail/cast/yard outcome, optionally confronts the forged inspections and can return a truthful report. It does not mean the rest of ActI is built, and a second briefing or a narrated train result alone does not satisfy this contract.
