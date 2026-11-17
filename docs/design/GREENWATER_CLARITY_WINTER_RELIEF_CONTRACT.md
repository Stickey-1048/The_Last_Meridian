# GREENWATER-WINTER-RELIEF-001: owner-approved follow-up contract

Nora, creative/player UX contract,17 November2026. **DERIVED NEW owner-approved follow-up**, not previously accepted NPC prose or canon history. Source design only; independent technical feasibility and implementation review remain required. No code, live game, input, profile/save/install or cloud action is authorized by this document itself.

The owner wants the food risk clear and the ability to return and help feed Greenwater through winter: a light survival concept, not an automatic death sentence. Preserve frozen clarity packet `37F98343B56482F223D623CC658E1A6402172C933FEBD5DE0435C2FA5D713905` and implement that separate clarity work as already authorized. This follow-up must not delay or substitute for it.

## Playable scope and immutable history

Unlock after the actual Greenwater road reaches100, regardless of chosen cargo outcome. The player may revisit Greenwater's existing stores board and Mercy's existing supply area to contribute real inventory or optionally buy a small, finite legitimate food batch. They can inspect the reserve, contribute partially/repeatedly and explicitly advance a warned local provisioning step. The board then displays the real updated count and whether the forecast improved. This is repeatable relief work, not only a promise of future help.

Never reset or rewrite MQ02B outcome44/42/43/41, cargo quantities, Hatcher judgment, paid200caps, TellLie/grain_sold/46, evidence, prior report, meal grants or other roads. Later relief does not turn a lie into truth, return a burned barge or erase earlier hunger. No new faction/player-past revelation, named merchant, Hatcher redemption or mandatory allegiance. No morality score, guaranteed starvation death, mandatory payment, punishment for leaving, automatic offscreen atrocity or real-time famine.

## New record ownership and controls

Proposed new quest `TLM_GW_Relief`, script `TLM:GreenwaterRelief`; keep its lifecycle/state separate from MQ02B. Stage meanings below are NEW technical stages, not extensions with invented old-road journals:

| Stage | Exact earned meaning |
| --- | --- |
|10|Relief ledger initialized once from an actual completed Greenwater cargo snapshot.|
|20|At least one actual food contribution was consumed and credited once.|
|30|First explicit warned provisioning step completed. Repeat counters carry later steps; do not replay stage30 for credit.|
|90|All six local winter steps accounted for and outstanding shortfall cleared. This means this bounded relief ledger is covered, not universal town prosperity.|

Fields: `Initialized`, `CargoUnitsAtStart`, `ReserveUnits`, `ShortfallUnits`, `StepIndex`0..6, `EverShortfall`, `DonatedUnits`, `PurchasedThisStep`, `PendingOperation`, unique pending request number, item/caps count snapshots, and once-only initialization/completion latches. Integer arithmetic and a reasonable checked upper cap prevent overflow. No global calendar, game-time timer or `Utility.GetCurrentRealTime` consumption.

Aliases reference existing true objects/actors through reviewed binding, not new personalities: actual `TLM_WS_GW`/`TLM_GW` RationBoard at(2180,620,12), Opal at(2100,560,0) for optional availability/context only; Pritchard is not needed to accept a donation. Do not place another interactive object over RationBoard or silently replace its accepted historical document. Add at most two new clearly labelled technical controls: `TLM_ACTI_GW_ReliefStores` near the landing board and `TLM_ACTI_Mercy_ReliefSupply` near the existing Mercy supply shelter. Exact new REFR positions must be chosen from the actual current exterior/readback with transformed bounds and192-unit approach/activation clearance, not invented in this prose. Preserve all old IDs/coordinates; new base/REFR/message/quest IDs require explicit own allocation. No terrain/navmesh/actor/AI/weather/landscaping changes.

Existing ration-board document remains the historical arrival account, not a dynamic prediction. Display `[Current relief stores]` separately; do not leave “grain barge is not lost” as the sole current state after actual fire. Relief controls can operate a technical store ledger if Opal has died; no dead speaker/ghost gratitude, invented replacement warden or resurrection. This needs no new voiced dialogue.

## Grounded food bindings and real material cost

Current licensed1cdd lookup receipt `build/licensed-red-hollow-1cdd466-001/plugin-build.txt:1047` resolves the existing GW Meal to **Ingestible Corn, `0330F8:Fallout4.esm`**; Caps001 resolves **MiscItem `00000F:Fallout4.esm`**. These are observed record keys, not assumed runtime load-order IDs. Builder must use typed lookup and verify EDID/display name/record type against the owner's master, pin/read back the chosen actual FormKey and fail the feature closed if unavailable. Never silently fall back from food to a cap/model stand-in. Optional additional edible forms require actual typed lookups and an explicit per-item unit table reviewed before implementation; minimum viable contract supports Corn only.

One accepted Corn item contributes ten **relief units**, an explicit simplified gameplay accounting unit, not a claim about calories, population or one ear literally feeding a town for a day. Donation choices:1,5,10 or cancel, filtered to real current item count. Revalidate count and current player/state after the exact confirmation. Remove the exact chosen quantity once; credit only its acknowledged actual inventory decrease. Insufficient inventory, cancel/invalid answer, death/combat/context loss before transfer commits nothing. Contribute again later using genuinely different remaining inventory; no credit merely for selecting a menu or carrying a stack. No withdraw-and-redonate loop or duplicated credits on repeated activation/load.

Alternative legitimate help: a NEW clearly technical Mercy relief-supply purchase offers **10 Corn for20 caps**, at most30 Corn per current local winter step. It is a small finite aid supply, not a boundless market or new faction service. Show price/stock before confirmation; remove20 real caps once and deliver10 actual verified Corn once. **Buying food does not credit the town**; the player must carry it back and donate it. Normal scavenged/grown/owned Corn is equally accepted, so this is not a paywall. Stage/visit/reload never replenishes shop stock. Only a successful explicit step increments the stock period; no free cap/item grants, repeat-after-cancel purchases or changed owner stats.

Both inventory operations need a persisted single-operation intent/nonce before the first effect, observed bounded acknowledgement and a once-only completion latch. No automatic retry of a RemoveItem/AddItem after an uncertain response or load; no inferred receipt from a later unrelated inventory change. Preserve an uncertain request, show a practical nontechnical unavailable message and log the exact count/identity for diagnosis. If safe idempotent load reconciliation cannot be proved with the existing engine primitives, document the finite limitation and keep that operation blocked rather than invent success/refunds. Sam must assess this implementation edge explicitly; it does not authorize a general transaction framework.

## Simplified reserve and explicit local time model

These numbers are **DERIVED gameplay tuning**, not new population/calorie lore. Show the unit convention on the status page. Use six explicit15-day local steps to represent the remaining90-day winter horizon. Ten relief units represent one town-provisioning day in this deliberately simplified ledger, so each step costs150 units.

Initialize once from the actual completed road's delivered cargo and current outcome, never from visiting/revisiting:

| Actual cargo delivered home | Starting reserve units | Meaning |
| --- | --- | --- |
|12/12|900|Existing9-day reserve90 + full winter cargo810. No relief debt is manufactured for a successful whole-cargo recovery.|
|8/12|630|90 +540 from the actually returned fraction.|
|6/12|495|90 +405 from the actually returned fraction.|
|0/12 (paid share/fire/no recovery)|90|Only the initially documented9-day reserve; payment to the player is not town food.|

No claim that these remain historically untouched if a future feature actually consumes reserves; this new isolated ledger starts at the completed-road follow-up and moves only by its own disclosed local steps. Snapshot source cargo count and never reinitialize on load, repeat report or a later relief donation. Unknown/inconsistent cargo state blocks initialization with no substituted outcome. Store full/partial/free/paid/grain-lie history independently.

Status shows current step, reserve, pending shortfall, next demand150, total remaining demand, total donated, and historical shortage occurrence. Forecast wording: `Covered for the remaining planned steps` only if reserve covers all remaining demand plus shortfall; otherwise `More food is needed before winter is covered`. This is a forecast, not deaths already observed.

No passive consumption. Only the owner choosing `[Advance the relief ledger by15 days]` at the local landing control, after a second explicit summary confirmation, advances one step. It is a local chapter accounting step, NOT advancing Fallout's global clock or other quests; say so. Explain exact projected reserve/shortfall first. Insufficient reserve must show the risk and permit `Keep gathering; do not advance` without cost. The player may still explicitly accept a shortage step; unprovided demand becomes `ShortfallUnits`, historical `EverShortfall=true`, never a forced Kill/Disable or invented casualty. Six steps maximum; no seventh winter or repeated final cost. No spending time/caps/items just to inspect or refuse.

Each step consumes existing reserve toward that step's150 demand; any deficit is recorded, not negative inventory or an automatic death. Later contributions first clear outstanding accounting shortfall, then add reserve. Explicitly say that aid now cannot undo earlier hunger: the historical shortage marker remains. Stage90 requires six steps and zero outstanding shortfall, not a claim of no past hardship. No arbitrary visit deadline, offline clock, save/load catchup, faster running penalty or punitive failure for pursuing Iron Junction/Red Hollow.

## Technical UI and visible aftermath

All NEW text is technical prototype UI, not invented Opal/Pritchard speech. Minimal examples ready for engineering interpolation:

- `[Winter relief] Greenwater still needs food. Your earlier river decision remains unchanged. You can bring real Corn here, inspect the reserve or return later. Nothing runs down while you are away.`
- `[Donate food?] Give %g Corn from your inventory to the town stores. Each credited item is consumed once. This will clear %g shortfall and add %g reserve units. You keep the rest.` Buttons `Donate this food` / `Cancel`.
- `[Relief supply] Buy10 Corn for20caps. %g of this step's30 remain in stock. Buying is not a donation; bring the food to Greenwater.` Buttons `Buy one batch` / `Cancel`.
- `[Advance local relief step?] This accounts for15days of town provisions only. It does not move the game's clock. Demand:150units. Projected reserve:%g; shortfall:%g. No time passes unless you confirm.` Buttons `Advance one relief step` / `Keep gathering`.
- `[Food still needed] The ledger records a shortage of%g relief units. This is unmet need, not a recorded death toll. You can return with more food. Earlier hunger remains part of the record.`

Implement with readable normal spaces and bounded per-page text/buttons. A compact live count on the stores control, plus at most three new vanilla STATIC crate/sack visual states (low/partial/covered) if audited models support safe placement, makes aid tangible. Visuals follow actual persisted numbers; no fake full store after only menu selection. Model/placement missing must not falsely claim successful physical stock rendering. The dynamic status page and actual inventory transfer are the minimum playable aftermath; new scenery is optional and separately audited. No full settlement simulation or voice/audio prerequisite.

Mercy hub may offer `Food relief for Greenwater` only once the completed-road relief is actually available, routed without exceeding the existing four-button page limit or hiding reports/copy/other roads. It directs to the existing landing or opens the actual current relief summary; it does not teleport/advance/donate automatically. Keep stage44 payment and the separate lie explanation explicit if displaying the old result alongside later relief.

## Finite acceptance cases

1. Actual whole/8/6/zero delivered cargo initializes exactly900/630/495/90 once; repeat travel/report/load changes none. Unknown cargo refuses safely. No old outcome/payment/lie/report/faction changes.
2. Real donations1/5/10 remove exactly that count once, credit exactly ten relief units per item once, retain all other items; insufficient/cancel/invalid/stale/death/current-context loss yields no phantom credit. Repeat/load/double activation cannot replay a pending effect. Persisted ambiguity blocks rather than guessing.
3. Real20cap purchase yields10 actual Corn, stock10less, no town reserve change until donation. Two/three batches work within available caps/stock; fourth refuses. Same-period reload/visit cannot refill; no-money player can still gather/donate ordinary Corn.
4. Inspect/refuse/leave/wait/other road/save/reload/offline time never consumes reserves or adds deaths. One explicitly confirmed step consumes150, advances once and renews only the finite stock period. Sixth cannot repeat; seventh absent.
5. Partial support, advance-with-shortfall and later return help are playable. Donation clears current shortfall but keeps historical hunger; no retroactive erasure or guaranteed death. Zero-reserve status clearly reports need, not a dead town.
6. After all six accounted steps and zero shortfall, stage90 occurs once; no duplicated reward or unrelated reputation adjustment. Full-cargo route can cover winter without buying/donating, while still allowing voluntary stores help before completion.
7. Ordinary controller menus are readable and explicit about who receives food/money, the separate earlier lie, remaining demand and local-only time. Missing/dead Opal causes no ghost speech or service lock; no automatic punishment for visiting later. Dynamic low/partial/covered display reflects actual state.
8. New-only source/IDs/aliases/bounds are verified; accepted writing and all old quest/runtime/fallback packages remain preserved. Synthetic delayed/refused inventory responses and save/reentry cases are labelled model evidence. Actual compiler/licensed readback, inventory acknowledgement, controller sequence, persistence/one ordinary healthy reload and tangible stock display remain native gates before owner handoff.

## Requested feasibility handoff

Sam: bounded read-only review of this exact contract, actual typed Corn/Caps lookup and minimal state/control integration. Confirm whether the once-only inventory/load edges, explicit local model and existing shared hub routing are implementable within one small follow-up. Identify concrete safety/engine blockers and the smallest adjustment; do not redesign the story or start implementation. Root owns authorization of the final source order and independent/native gates. No author claim of working automation or completed relief feature is made.
