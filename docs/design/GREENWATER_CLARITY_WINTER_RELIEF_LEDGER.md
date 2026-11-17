# Greenwater clarity and winter relief implementation ledger

Baseline is exact `1cdd4666b12e3b40f0c3bf5a3e877f561c7b8d83`. Authority is the frozen owner-choice clarity packet37F98343, Winter Relief contractDA8164F2, Sam feasibility532668DD and the coordinator's final engineering order. Full packets accompany this candidate. All additions are technical prototype UI and the owner-approved derived relief rules; accepted NPC speech, canon, player past and all three roads' earlier outcomes remain intact.

## Scene and choice flow

Successful first outward travel verifies the actual arrival within256units before showing the role brief. It neither enters the landing trigger nor sets a quest stage. The acknowledgement is not movement. A claim owns the message; an activation cannot start another conversation beneath it. Revisit after a resolved result never asserts the grain is still an unresolved initial task.

The landing, occupied Queen, separate grain barge, card table, lashing and pilot retain their actual IDs/positions. Their technical labels explain those roles. Current landing/cargo pages select actual paid, whole, partial or destroyed history; unavailable cast receives neutral layout directions. Original cargo-delivery counts remain historical counts, separately identified from the new current relief reserves.

Opal's eligible first completed goal conversation earns its original20, then the informational goal/stakes pages. They choose no route. Card play has a local stake confirmation. Accepted Hatcher Done now leads to the explicit200-cap/grain-retained confirmation; only exact button0 plus captured living/current participant, road stamp and unclaimed offer reaches the old once-only payment. Cancel, invalid answer or stale context closes. The later [Lie] to Opal stays a separate commit, and her acknowledged reply alone earns46. Payment/lie/reply flags and once-only meals remain distinct.

Hanging, living custody and release each have their own explicit local precommit confirmation. The original speaker, prisoner, required recipient/object and road stamp are captured before the first choice, passed through confirmation and checked at the rules effect/receipt boundaries against authoritative aliases. Rebinding does not select a replacement. Hanging's observed-death receipt uses the persisted actual execution actor; genuine issued effects remain facts rather than being rolled back. The fire warning distinguishes the occupied Queen's people from its separate grain cargo and reports risk/cargo effects without inventing30deaths. No dialogue, refusal or technical note attacks the player or grants a moral label.

## One ledger, two controls

There are30 source scripts: the accepted29 plus `GreenwaterRelief.psc`. Of the accepted29, only GreenwaterWalk, GreenwaterTalk and MQ02BQuest change. Core and every unrelated accepted script stay exact. The selected runtime is17 source-identical measured Details PEX plus13 fresh PEX; a separate fresh compile of all 30 is required. Source verification is not compilation.

`TLM_GW_Relief` is one master-owned quest. Its Stores/Supply aliases are script-filled; its real Player alias forwards OnPlayerLoadGame through the existing GreenwaterTalk script. It is never copied into the world. Greenwater controller aliases31/32 append ReliefStores/ReliefSupply after the accepted0..30prefix. The actual opened controller binds both references once, only after successful Start AND IsRunning; another controller cannot replace that owner. A failed startup is retried on ordinary later controller refresh/travel.

The new landing control is at(2180,850,12), separate from the preserved historical ration board. The Mercy control is at(3050,3620,12), in front of the existing supply shelter. Neither is a new NPC, duplicate document, container, workshop or teleport. Actual reference placements are deferred until AFTER every accepted story/scenery allocation. All accepted world IDs and payloads therefore retain their allocation positions; the source cloner verifies the old story payloads against an actual baseline Git export. No additional static stock art is required.

The full world builder must audit each actual borrowed control model, reject missing/oversized paper bounds and sample continuous 192-unit approaches from the east at the landing and the existing rear supply street at Mercy against actual transformed upright scenery bounds. Both points lie over generated flat LAND atZ0; controls stand atZ12. The supply point is outside the shelter floor, so no unsupported floor elevation is claimed. This is a source/build gate, not Havok, navmesh, reach or legibility proof.

## Cargo snapshot and accounting

The read-only MQ02B helper accepts only completed100, coherent exclusive claimed/outcome/stage/cargo/GrainHome/recovered/payment tuples, with no return/escape/fire still pending. It returns900 for actual whole 12,630 for actual 8,495 for actual 6, or90 for actual completed paid/fire zero recovery. Unknown/inconsistent combinations return-1and do not initialize. Enum Cargo is never treated as a count. Snapshot initialization happens once; travel, report and load cannot refill it.

Balance is `StartingReserve + DonatedUnits -150*StepIndex`. Reserve=max(balance,0), shortfall=max(-balance,0), remaining demand=150*(6-StepIndex). Thus donations clear debt first. Ten relief units are one deliberately simplified town-provisioning day; these are not population/calorie facts. The six explicit steps represent90local days, with no global clock, passive/offline consumption, inferred death or punishment for leaving.

Actual Corn1/5/10 is removed once and credits10units each only after the immediate active-request receipt. Donation total is checked at100000 units before effects. The strict typed Corn EDID/name and Caps001/Bottlecap bindings have no permissive Meal/name fallback. The coordinator's prior owned-master evidence identifies Corn0330F8 and Caps00000F; this author's synthetic tests do not measure those owned-master keys.

Mercy offers10Corn for20 actual caps, finite30Corn per period. Buying credits no town reserve. Initial period is0; only successful steps1..5reset stock. Step6retains the final period's remaining stock so unresolved shortfall can still receive help; there is no seventh reset. Scavenged/grown Corn is equally accepted. Corn inventory has a checked100000item ceiling for a purchase, preventing addition overflow. Stage90occurs once after six steps and zero debt; the covered season then offers inspection only. Earlier hunger and all original river facts remain recorded.

## Finite inventory and load protocol

Donation, purchase and advance share one persisted pending owner and monotonic request nonce. Testing/claiming that owner has no native call between them. Intent stores kind, activation epoch, actor/control identity, step, quantity, baseline counts and removal/delivery-issued flags before any effect.

| Operation | Issued phases | Commit |
| --- | --- | --- |
|Donation|One Corn RemoveItem call|Immediate exact decrease, then current owner/epoch/context read after native calls, one credit and committed nonce|
|Purchase|One20-cap RemoveItem; only after its receipt, one10-Corn AddItem|Both immediate receipts/current context, then stock charged once; no donation credit|
|Local step|No inventory effect; one persisted operation owner|One150-unit step and applicable stock-period change|

Native inventory APIs return no transaction ID/success value. Immediate count acknowledgement within the active request is a finite observational gate, not universal exactly-once proof. There is no polling window, automatic refund, retry, reissue or later unrelated-count inference. A refused/delayed/uncertain effect or in-flight load remains blocked, preserving the request for diagnosis; status still works. An already issued native call may eventually change inventory even though credit/delivery continuation is withheld. This limitation is intentional and must not be advertised as seamless recovery.

Load invalidates the epoch and holds pending operations. A relief-only controller generation releases its interrupted outer claim without releasing ordinary Greenwater story conversations; resumed old activations cannot clear a newer claim. Epoch/owner facts are read after native count/context reads, including paced-call tests. Each later UI page retains its originating activation epoch and checks it after native context reads; a newer requestEpoch cannot authorize an older result, status, forecast or completion frame. Healthy committed data and stock survive the simulated player-load event. Actual latent-stack/save behavior still requires the coordinator's native healthy-load test.

## Provenance and gates

The candidate has its own manifest, full-before-output verifier, opt-in workspace packager and PowerShell refusal fixture. All earlier verifiers/manifests/packagers/workflows remain exact. Historical Greenwater and Red Hollow candidate/repair tests use actual immutable Git exports; the old63Greenwater repair/mutation cases also execute unchanged, alongside the current adapted probes. New independent context guards make some old single-guard mutants redundant; current probes remove both relevant guards while historical probes preserve their original meaning.

The mapping records23new relief UI messages and the precise39record-ID append, source ownership, aliases, stages and qualification of coordinator-provided master facts. It records no fabricated compiler, artifact or native measurements. Final source checks, remote CI and independent Sam/Nora source review are separate gates. Only the coordinator runs licensed compilation/build/audit, installation, ordinary controller comprehension/inventory sequences and healthy reload before owner handoff. This candidate is fresh-game/fresh-save only and promises no migration.
