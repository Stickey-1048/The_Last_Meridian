# TLM_MQ01 — Six Rounds to Mercy: Technical Design Document

**Status:** DESIGN DRAFT v0.1, 2026-11-11. Not implemented. Not tested. Awaiting owner review.
**Companion doc:** [TLM_SQ01 — Signed Clean](TLM_SQ01_signed-clean.md) (the evidence-based secondary objective).
**Scope:** Chapter 01 of [three-act-story.md](../three-act-story.md) plus the minimum Mercy Crossing hub needed to finish it.

> **Amended 2026-11-11.** [DESIGN_AMENDMENTS_v0.2.md](DESIGN_AMENDMENTS_v0.2.md) changes parts of this document (stage numbers, outcome rules, script layout) and is what the model, scripts and plugin builder implement. The amendments are proposed, pending owner review. `[VERIFY]` items are resolved or carried forward in [VERIFY_LOG.md](VERIFY_LOG.md).

> ### Verification status — read first
> - Written without Fallout 4 or the Creation Kit available. **Nothing here has been built, compiled or run.**
> - Creation Kit (CK) tab names, flag labels, console commands and Papyrus function names come from the author's general knowledge of the Fallout 4 CK, not from this repo's tooling. Items marked **[VERIFY]** must be checked against the installed CK (and the CK wiki) before relying on them.
> - Papyrus in §11 is **untested scaffolding**. It has not been compiled.
> - No FormIDs are assumed anywhere. Reference records by EditorID in the CK, and by script property or alias in Papyrus.

---

## 1. Canon constraints this design must obey

| # | Constraint | Source |
|---|---|---|
| C1 | Southern Appalachia (eastern TN), 2317. No desert or Wild-West visuals. | CANON.md, Creation identity |
| C2 | Player is a **surface-born** descendant of Deep exiles, **unaware** of it in Chapter 01. Do not reveal the Deep, the Open Ledger or the exile in MQ01. | three-act-story.md Ch01; child-of-the-deep.md |
| C3 | Do not define the player's sex, ethnicity, appearance, personality, parents or childhood. Dialogue must stay role-play neutral. | child-of-the-deep.md Rules |
| C4 | Ch01 beats: wrecked train, scavenge revolver and dispatch, help/evade/exploit a threatened caravan, reach Mercy Crossing and Sheriff Owen Pritchard. Tutorial for combat, dialogue and scavenging. | three-act-story.md Ch01 |
| C5 | Ideology is expressed through **consequences**, not speeches. The player is held to the same accountability standard as opponents. | doctrine-of-the-open-ledger.md; CLAUDE.md |
| C6 | No ancillary quest gates main progress. MQ01 must be completable by the shortest path, and no NPC death or skipped optional may soft-lock it. | CANON.md Side-content principle; three-act-story.md invariants |
| C7 | Use names from [naming-registry.md](../naming-registry.md). New minor names must pass its family/homophone policy (see §13). | naming-registry.md |
| C8 | Exactly four principal factions. MQ01 introduces none as a joinable power. | CANON.md |
| C9 | Original assets only. No proprietary assets in the repo. | README.md; CLAUDE.md |

**Dev-plan success criteria (from development-plan.md):** a 30–60 minute slice with one persistent binary choice, one reputation increment, basic save/load, completion and fallback testing.

---

## 2. Prerequisites and plugin setup

### 2.1 Tooling
- Fallout 4 (Steam/GOG/Microsoft Store build to be recorded) and the **Creation Kit** from Bethesda's tools. Record exact versions in `docs/design/BUILD_ENV.md` once installed. **[VERIFY]** version compatibility with the current game build.
- A Papyrus compiler (the CK's built-in one) with the base game's Papyrus source extracted to the location the CK expects. **[VERIFY]** the expected source folders for the installed CK version.
- No script extenders (F4SE) for the slice. Everything must run on the vanilla Papyrus VM.

### 2.2 Plugin decisions

| Decision | Recommendation | Why |
|---|---|---|
| File name | `TheLastMeridian.esp` | Simple for dev. ESL-flagging is a later optimization, not a slice concern. |
| Masters | **`Fallout4.esm` only.** No DLC for v0.1. | Fewer dependencies means fewer test configurations. Revisit for Far Harbor (Appalachian-adjacent assets are tempting). |
| Prefix | `TLM_` on **every** new EditorID. | development-plan.md |
| EditorID scheme | `TLM_<TYPE>_<Name>`, e.g. `TLM_NPC_SHERIFF_MERCY`, `TLM_G_CaravanOutcome`. NPC IDs follow the stable-ID rule in naming-registry.md. | Display names can change without breaking references. |
| FormID policy | Let the CK assign. **Never** hardcode a FormID in Papyrus. Use properties and aliases. | Survives load-order changes. |
| Editing existing records | **Do not edit vanilla records.** Only add new ones. | Compatibility, rollback, and the IP rule. |
| Version global | `TLM_G_DataVersion` (int), set by `TLM_Core`. | Lets later builds migrate saves. |

### 2.3 Repository layout (proposed)

```
plugin/TheLastMeridian.esp          # binary; tag every milestone (see §16)
scripts/Source/User/...             # .psc only (never .pex of vanilla, never vanilla .psc)
docs/design/                        # these documents
```
Add `*.esp binary` to `.gitattributes`. Never commit extracted game assets, vanilla scripts, or voice files you don't own.

### 2.4 Open technical decisions (need an owner call before building)

| ID | Question | Options | Recommendation |
|---|---|---|---|
| **T1** | **How does a new game begin at the wreck?** Vanilla starts with the pre-war intro and character creation. | (a) Dev-only: start in the CK/console at the wreck (`coc`) and `startquest`. (b) A start-quest that runs after vanilla character creation and moves the player. (c) Full replacement of the intro flow. | Build and test the slice with **(a)**. Defer (b)/(c) to a separate issue. It is a known-hard area and must not block MQ01 logic. **[VERIFY]** |
| **T2** | **Where does the geography live?** | (a) A new small custom worldspace (`TLM_BrokenValleys`). (b) Interiors/test cells only. (c) A corner of the Commonwealth worldspace. | **Prototype logic in (b)**, using a temporary test cell and aliases/markers only. Then port to **(a)**. Reject (c): it pollutes vanilla space. Exterior terrain and navmesh are the biggest schedule risk in the slice. |
| **T3** | **Pack animals.** Fallout 4 has no horses. | Placeholder brahmin; later custom mule/horse assets. | Brahmin placeholder; do not block on assets. |
| **T4** | **Player's first-wake state.** Character creation gives the player a body and clothes. | Strip inventory at start vs. keep clothes. | Strip weapons/ammo/aid only; keep clothing. Add the one fixed heirloom item (§5.3). |

---

## 3. Record inventory (what must exist in the plugin)

| Type | EditorID | Purpose |
|---|---|---|
| Quest | `TLM_Core` | Start-game-enabled utility quest: version global, defaults for the four metrics, dev helpers. **No story logic.** |
| Quest | `TLM_MQ01` | This quest. |
| Quest | `TLM_SQ01` | Secondary objective (separate doc). |
| Location | `TLM_Loc_RailWreck`, `TLM_Loc_TellicoRoad`, `TLM_Loc_MercyCrossing` | Map markers, objective targets. |
| Globals | `TLM_G_CaravanOutcome` (short), `TLM_G_CaravanAliveAtMercy` (short 0/1), `TLM_G_Rep_MercyCrossing` (short), `TLM_G_MQ01_Done` (short) | Persisted, condition-friendly state. |
| Globals (hidden metrics) | `TLM_Truth`, `TLM_Competence`, `TLM_Accountability`, `TLM_MutualTrust` (all short, default 0) | Names fixed by doctrine-of-the-open-ledger.md. Not shown to the player. |
| Actors | See §5 | Cast. |
| Items | `TLM_WEAP_MarshalRevolver` *(see note)*, `TLM_MISC_Dispatch`, `TLM_MISC_TornTransitPass`, `TLM_BOOK_MarshalLog` | Quest and tutorial items. |
| Containers/Activators | `TLM_CONT_WagonCargo`, `TLM_ACTI_NoticeBoard` | Cargo, notice board (SQ01). |
| Triggers/Markers | `TLM_TRIG_AmbushSight`, `TLM_TRIG_TownGate`, `TLM_MARK_AmbushCenter`, `TLM_MARK_CaravanYard`, `TLM_MARK_WreckStart` | Encounter and town hooks. |
| Factions | `TLM_Fac_Cutters` (hostile to player and caravan), `TLM_Fac_Caravan`, `TLM_Fac_MercyCrossing` | AI/crime behavior. Reputation itself lives in a global. |
| Messages | `TLM_MSG_Tut_*`, `TLM_MSG_PublishChoice` (SQ01) | Tutorial hints, board choice. |
| Packages | See §10 | NPC behavior. |
| Dialogue | See §8 | Branches/topics. |

> **Note on the revolver:** prefer reusing a vanilla `.44` revolver-class weapon with a new, renamed *copy* record (`TLM_WEAP_MarshalRevolver`) over editing the vanilla one. Confirm the vanilla weapon and ammo EditorIDs in the CK **[VERIFY]**.

---

## 4. Design intent

1. **"Six Rounds" is a scarcity rule.** The player's revolver holds six rounds and there is almost no reserve. Every shot on the road is a decision, which makes the caravan choice real rather than a free fight.
2. **The road is the tutorial.** Combat, dialogue, scavenging and barter are each taught by something the player must do to get to Mercy Crossing. Hints appear as short messages, not a lecture.
3. **The caravan choice is the persistent consequence.** Help, evade or exploit each leave a different mark in the world and in dialogue.
4. **Accountability is mechanical.** If the player lies about what happened on the road, the world can contradict them, because a witness exists.
5. **Nothing is lost on a skipped path.** The slice finishes whether the player fights, sneaks past, skips the wreck loot, or arrives in town empty-handed.

---

## 5. Cast

### 5.1 Mercy Crossing (five named NPCs from the dev plan, plus one minor)

| Stable ID | Name | Role in slice | Dialogue weight |
|---|---|---|---|
| `TLM_NPC_SHERIFF_MERCY` | Owen Pritchard | Dispatch recipient, debrief, MQ02 hook. Old Warden. | **Full tree (§8.3)** |
| `TLM_NPC_GUNSMITH_MERCY` | Ada Pike | Sells ammo, owns the independent parts book (SQ01 evidence). | Barter + 1 SQ01 topic |
| `TLM_NPC_MERCHANT_MERCY` | Silas Vane | Trading post; SQ01 buyer option. **Do not imply guilt**; Chapter 04 owns his arc. | Barter + 1 SQ01 topic |
| `TLM_NPC_PHYSICIAN_MERCY` | Miriam Keene | Treats the caravan survivor; stimpak-equivalent barter. | Barks only |
| `TLM_NPC_DEPUTY_MERCY` | Jonah Talbot | Town gate patrol; first greeting. | 2–3 barks |
| `TLM_NPC_FREIGHT_MERCY` | Corwin Haskell *(minor, **proposed**)* | Freight agent; the SQ01 scapegoat risk. | Barks only |

### 5.2 Road and wreck (all **PROVISIONAL** names, pending registry approval)

| Stable ID | Name | Role |
|---|---|---|
| `TLM_NPC_MARSHAL_DEAD` | Rail Marshal Tobias Gantt | Dead at spawn ("starts dead"). Carries dispatch, revolver, journal. No dialogue. |
| `TLM_NPC_CARAVAN_MASTER` | Nell Fenwick | Caravan owner. Protected. Reward-giver, and the witness in the Exploit path. |
| `TLM_NPC_CARAVAN_DROVER` | Abel Rudd | Her hand. Protected during the fight; his death is the cost of Evade/Exploit. |
| `TLM_NPC_CUTTER_LEAD` | Reese Dunmore | Leader of the Tellico Cutters; the deal-maker. |
| `TLM_NPC_CUTTER_01..03` | (unnamed) | Three raiders. |

### 5.3 Items with story weight
- **`TLM_MISC_TornTransitPass`**: a half-torn pass with an unfamiliar emblem, in the player's starting inventory. **No dialogue, no explanation, no quest effect in MQ01.** It plants the "lost family marks" symptom from doctrine-of-the-open-ledger.md (Act I). *Optional; owner may cut it.*
- **`TLM_MISC_Dispatch`**: the sealed rail dispatch. Content is provisional (see §13, Q4).

---

## 6. Quest `TLM_MQ01`

### 6.1 Quest data **[VERIFY all labels in CK]**
| Setting | Value |
|---|---|
| Quest type | Main |
| Start Game Enabled | **No**. Started by `TLM_Core` (new game) or by console during dev. |
| Run Once | Yes |
| Allow Repeat Stages | No |
| Story Manager event | None. Explicit start. |
| Priority | Highest in slice |

### 6.2 Stage table

Stage numbers are milestones. **Objectives, not stage order, direct the player**, because the player can reach the town before the dispatch.

| Stage | Name | Trigger | Effects | Log entry (draft) |
|---|---|---|---|---|
| 0 | Unstarted | default | none | none |
| 10 | Awake at the wreck | `TLM_Core` / dev start | Place player at `TLM_MARK_WreckStart`; strip weapons/ammo; add `TornTransitPass`; **enable** ambush actors (state ARMED); display **O10**; show tutorial message 1 | *The train is a ruin and you're alive. Whoever carried the line's mail didn't make it.* |
| 15 | Armed (optional) | Revolver picked up (alias script) | Show "six rounds" hint message | *Six rounds in the cylinder. Count them.* |
| 20 | Dispatch acquired | Dispatch picked up (alias script) | Complete **O10**; display **O20** (target: Pritchard / Mercy Crossing) | *The marshal's dispatch is sealed to the Sheriff of Mercy Crossing.* |
| 30 | Ambush live | Player enters `TLM_TRIG_AmbushSight`, **or** any combat with a Cutter, **or** hits a Cutter | Caravan state → LIVE; start evade timer + distance poll | *(none; emergent)* |
| 31 | Caravan saved | LIVE → Cutters dead/broken | `TLM_G_CaravanOutcome = 1`; remove protection | *You turned the Cutters off the wagon.* |
| 32 | Caravan evaded | LIVE → timer/distance rule (§7) | `Outcome = 2`; scripted fallout (§7.3) | *You kept walking.* |
| 33 | Caravan exploited | Deal accepted (§8.1) or player kills caravan hands | `Outcome = 3`; scripted fallout; set method flag | *You took a share.* |
| 40 | Arrived at Mercy Crossing | `TLM_TRIG_TownGate` | **Failsafe:** if Nell is alive and not in town, move her to `TLM_MARK_CaravanYard`; set `CaravanAliveAtMercy` | *Mercy Crossing.* |
| 50 | Dispatch delivered | Pritchard handoff topic (§8.3) | Complete **O20**; apply rep (§9); queue Pritchard follow-up topics by outcome | *Delivered to Sheriff Pritchard.* |
| 60 | Debrief complete | End of Pritchard debrief | Set `TLM_G_MQ01_Done = 1`; hand off to the MQ02 stub | *Pritchard has more for you.* |
| 100 | Completed | 60 reached | Complete quest | |
| **900** | **Recovery** | Any failsafe in §12 | Repair state; add a replacement dispatch if lost; re-display the right objective | *(silent)* |

**Order rules:** 31/32/33 only after 30; 50 requires 20 (else the Pritchard topic for "no dispatch" applies, §8.3); 60 requires 50; 100 requires 60. Each stage is guarded in script with `GetStageDone` so repeated triggers are harmless.

### 6.3 Objectives

| ID | Text | Displayed at | Completed at | Target |
|---|---|---|---|---|
| O10 | Find the marshal's dispatch case | 10 | 20 | `Alias_Marshal` |
| O20 | Take the dispatch to Sheriff Owen Pritchard in Mercy Crossing | 20 | 50 | `Alias_SheriffPritchard` |

Two objectives only. The caravan encounter deliberately has **no objective**: it is emergent, which is what makes ignoring it a legitimate choice.
**If the player reaches town without the dispatch**, O10 stays displayed and Pritchard sends them back (§8.3). O20 is never shown until the dispatch is held.

### 6.4 Aliases

| Alias | Kind | Fill | Flags **[VERIFY]** | Notes |
|---|---|---|---|---|
| `Alias_Marshal` | Reference | Specific ref: dead Gantt | Allow Dead, Protected | O10 target. |
| `Alias_Dispatch` | Reference | Specific ref: placed `TLM_MISC_Dispatch` | Quest Object | Alias script P1. |
| `Alias_Revolver` | Reference | Specific ref: placed revolver | Quest Object | Alias script P1b (hint only). |
| `Alias_SheriffPritchard` | Reference | **Unique Actor** | **Essential** (slice only) | O20 target. Must always be reachable. |
| `Alias_CaravanMaster` | Reference | Specific ref: Nell | Protected | Script P5. |
| `Alias_CaravanDrover` | Reference | Specific ref: Abel | Protected | Script P5. |
| `Alias_CutterLead` | Reference | Specific ref: Dunmore | Allow Dead | Script P4. |
| `Alias_CutterA/B/C` | Reference ×3 | Specific refs | Allow Dead | Script P4. (Single aliases are easier to debug than a collection alias.) |
| `Alias_Wagon` | Reference | Specific ref: wagon + `TLM_CONT_WagonCargo` | | Owned by `TLM_Fac_Caravan`, so taking cargo is theft. |
| `Alias_AmbushTrigger` | Reference | Specific ref: trigger volume | | Script P2. |
| `Alias_TownGate` | Reference | Specific ref: trigger volume | | Script P6. |
| `Alias_MercyCrossingLoc` | Location | Specific location | | Map marker target. |

---

## 7. The caravan encounter

### 7.1 State machine
State lives in the quest script (`CaravanState`). **The stage numbers and `TLM_G_CaravanOutcome` are the persisted source of truth; `CaravanState` is derived and re-derivable after a load** (§12).

```
DORMANT(0) --stage 10--> ARMED(1) --player enters trigger / combat--> LIVE(2)
LIVE --all Cutters dead OR lead dead (rest break)--------------> SAVED(3)   stage 31
LIVE --no hostile act AND timer expires, OR player leaves-----> EVADED(4)   stage 32
LIVE --deal accepted OR player kills a caravan hand-----------> EXPLOITED(5) stage 33
```
First resolution wins. Later events (e.g. someone kills a Cutter after EVADED) are ignored for outcome purposes.

### 7.2 Scene setup
- Raiders (Dunmore + 3) are **already in combat with the wagon crew** when the player arrives, with Nell and Abel under a "Protected" alias so the player can't accidentally lose the SAVED path to bad AI.
- Placement: on the road, in line of sight from a high point, so Evade is a visible, deliberate choice (walk past, not fail to notice).
- Ammo tuning: **six** revolver rounds are not enough to kill all three Cutters by shooting alone. The fight must be possible with melee, stealth, headshots/criticals, the reserve in the marshal's satchel, or a speech result. **Tune in playtest; do not hardcode numbers from this doc.**

### 7.3 Outcomes and their world effects

| Outcome | Condition | Nell | Abel | Wagon cargo | Player gets | Mark left |
|---|---|---|---|---|---|---|
| **1 Saved** | Lead dead / Cutters dead or broken | Alive, walks to town | Alive | Intact | Reward topic from Nell (reserve ammo + caps, one time) | `CaravanAliveAtMercy = 1` |
| **2 Evaded** | Timer expires with no hostile act, or player moves out of range | Alive, wounded, walks to town | **Killed** by Cutters | Looted by Cutters (gone) | Nothing | `CaravanAliveAtMercy = 1` |
| **3 Exploited** | Deal accepted in §8.1, or player kills a caravan hand | **Deal:** alive, robbed, witness. **Betrayal:** dead. | Killed | Split with Cutters; player gets a share | Share of cargo | Deal: `CaravanAliveAtMercy = 1` with witness. Betrayal: `0`, no witness. |

Evade timing: **T_EVADE** (starting suggestion 90 s, tuned in playtest) and a distance rule (starting suggestion: beyond roughly 3,500–5,000 game units from `TLM_MARK_AmbushCenter`). Both are tunables, not facts.

### 7.4 What makes it a *persistent binary choice* (dev-plan item 4)
`TLM_G_CaravanAliveAtMercy` (0/1) is the clean binary that later content reads. `TLM_G_CaravanOutcome` (1/2/3) carries the nuance for dialogue. Later chapters should condition on the binary first and the enum second.

### 7.5 Exploit path: how a lie gets caught
If Outcome = 3 by **Deal**, Nell survives and arrives at the clinic. At the Pritchard debrief (§8.3) the player may confess, deny, or blame the Cutters. Pritchard's lines are conditioned on Nell being alive. **There is no combat punishment**, only reputation and trust (§9). If the player took the **Betrayal** route (both dead), no witness exists, so no one can contradict a denial. That is deliberately a *worse moral outcome with a better practical one*, and the design does not hide that.

---

## 8. Dialogue tree

Rules: ≤ 4 player options per node (the vanilla wheel limit **[VERIFY]**), role-play neutral, short. Protagonist lines are **text-only** in the slice (no voice assets). **[VERIFY]** how the CK handles unvoiced player topics. Speech-challenge difficulty is a CK setting, not hardcoded here.

### 8.1 Reese Dunmore (greeting while state = LIVE and no shot fired)
```
DUNMORE: "Keep walking. Or stay and pick up a share."
 ├─ [Intimidate/Persuade, speech check] "Pritchard hangs road-takers. Leave." ── success → Cutters break → SAVED(31)
 │                                                                        └─ fail → combat → fight
 ├─ [Attack] "Let them go." ── combat → fight (outcome decided by §7.1)
 ├─ "What kind of share?" → DUNMORE: "Half the cargo. The drover won't be a problem."
 │     ├─ "Done." ── EXPLOITED/Deal (33)
 │     └─ "No." ── combat → fight
 └─ [Leave] "Not my business." ── no stage; EVADE rules apply (§7.3)
```
Dunmore's greeting is gated by `GetStage TLM_MQ01 == 30`-equivalent state and "not in combat with player". Once combat or a deal starts, this branch ends.

### 8.2 Nell Fenwick (after outcome, in town or on road)
| Outcome | Opening | Player options | Effect |
|---|---|---|---|
| Saved | Thanks; offers reward | "Take it." / "Keep it." / "Who hit you?" | One-time reward; `TLM_MutualTrust +1` on first thanks |
| Evaded | "You watched. You kept walking." | "I couldn't." / "Not my fight." / (nothing) | No reward; she won't barter. No script effects. |
| Exploited (Deal) | Cold, tells the truth to anyone who asks | (none; she refuses to talk) | She is the Pritchard witness. |

### 8.3 Sheriff Owen Pritchard
**Entry condition:** player speaks to him in the office or yard. He is on a 24-hour office sandbox in the slice so he is never unreachable (§10).

```
NODE P0 — greeting  (variants by state)
 A. Has dispatch (stage ≥ 20):
    PRITCHARD: "Off the Tellico wreck. That's Tobias Gantt's case you're carrying."
     ├─ [Hand over the dispatch] → P1
     ├─ "Not yet." → exit (case stays; O20 remains)
     └─ (SQ01) "There's something else from that train." → see SQ01 doc, §6
 B. No dispatch (stage < 20):
    PRITCHARD: "Gantt's train never reached us. Where's his case?"
     ├─ "I haven't looked." / "Lost it." → PRITCHARD: "Six hours east at the wreck. I'll mark it."
     │       → re-display O10 with map marker; **no stage change; no fail state**
     └─ "I'll go back for it." → same
NODE P1 — delivery (sets stage 50)
 PRITCHARD reads, grim: "The line keeps losing marshals." 
 Then, conditioned on caravan state:
    Saved(1):    "Word is Nell Fenwick's wagon got through. Obliged."                              → rep (§9)
    Evaded(2):   "Abel Rudd's dead on the Tellico road. Nell Fenwick says someone watched it happen."  [no accusation]
                  ├─ "I watched." (admit: Accountability +1, Truth +1)
                  ├─ "I never saw it." (deny: Truth −1; Nell is alive and can contradict)
                  └─ exit (say nothing; no change)
    Exploited(3), Nell alive:
                  "Nell Fenwick's at Miriam Keene's clinic. Her account is different from the one you'll give me."
                  ├─ "I took a share." (confess: Accountability +1, Truth +1)
                  ├─ "The Cutters forced it." (blame: Truth −1; Pritchard notes the discrepancy)
                  └─ "She's lying." (deny: Truth −1, MutualTrust −1)
    Exploited(3), Nell dead: "Two dead on the Tellico road and no one to say how." (No contradiction possible.)
NODE P2 — hand-off (sets stage 60)
 PRITCHARD: "Greenwater's food has gone short. Red Hollow's sealed the mine. Iron Junction's rails are being cut.
             Pick one. I don't have the people for all three."   → Chapter 02 hook; stage 60 → 100
```
**Design intent:** none of these lines need the player to argue a philosophy. The only "moral" input is a short answer to a question a person would actually ask.

---

## 9. Rewards, reputation and hidden metrics

### 9.1 Reputation (dev-plan item 4: one faction-reputation increment)
`TLM_G_Rep_MercyCrossing`, applied once at stage 50:

| Condition | Δ |
|---|---|
| Dispatch delivered | +1 |
| Caravan **Saved** | +1 |
| Caravan **Exploited (Deal)** and Nell alive | −1 |
| Otherwise | 0 |

Resulting range 0–2 for honest paths, 0 for the Exploit-with-witness path. Reputation is a number the *town* acts on later (prices, barks). It is **not** a moral meter shown to the player.

### 9.2 Hidden metrics (names from doctrine-of-the-open-ledger.md)
Not displayed. Only adjusted by explicit player *choices*, never by combat statistics. **Do not gate any MQ01/Act I content on them.** They exist for later evaluation.

| Event | Truth | Competence | Accountability | MutualTrust |
|---|---|---|---|---|
| Caravan saved | | | | +1 |
| Confess or admit (P1, Evaded or Exploited-Deal) | +1 | | +1 | |
| Deny or blame while Nell is alive (P1) | −1 | | | −1 (Exploited "She's lying" only) |
| Other MQ01 events | 0 | 0 | 0 | 0 |

(SQ01 adds more; see its doc.)

---

## 10. Mercy Crossing minimum hub

**Interiors (3):** `TLM_Int_WardenOffice`, `TLM_Int_TradingPost` (Vane + Pike's corner), `TLM_Int_Clinic`. **Exterior:** a short street with a gate trigger and a notice board.
**No** crafting, settlement building, faction offices or extra vendors in the slice.

| NPC | Package (slice) | Notes |
|---|---|---|
| Pritchard | 24-hour sandbox at office marker | **No sleep package** in the slice, so he is always reachable. Add sleep later with a wake-for-dialogue test. |
| Pike | Sandbox at stall, 06–20 | Barter container with limited `.44` stock. |
| Vane | Sandbox at counter, 06–20 | Barter container. |
| Keene | Sandbox at clinic, 06–20 | Nell recovers here in Outcomes 2 and 3-Deal. |
| Talbot | Patrol/sandbox at gate, 06–20 | One greeting bark on first approach. |
| Haskell | Sandbox at freight shed, 06–20 | Barks only (see SQ01). |

**Night rule:** any NPC the quest *needs* (Pritchard) must be reachable at any hour. NPCs that are optional can sleep or be off schedule.
**Navmesh:** required for every cell where an NPC moves. Do not ship an exterior without it.

---

## 11. Papyrus: responsibilities and scaffolding (**UNTESTED**)

### 11.1 What Papyrus must do, and nothing else
| ID | Attached to | Responsibility |
|---|---|---|
| P1 | `Alias_Dispatch` | On `OnContainerChanged` to the player: `SetStage(20)` (once). |
| P1b | `Alias_Revolver` | Same pattern → stage 15 (hint only). |
| P2 | `Alias_AmbushTrigger` | `OnTriggerEnter` by player → `EnterLive()`. |
| P3 | `TLM_MQ01` quest script | Owns state and outcome functions; timers; recovery. |
| P4 | `Alias_CutterLead/A/B/C` | `OnDeath` → `CutterDown(self)`. |
| P5 | `Alias_CaravanMaster/Drover` | `OnDeath` → `CaravanHandDied(self, killer)`. |
| P6 | `Alias_TownGate` | `OnTriggerEnter` by player → `SetStage(40)`. |
| P7 | Topic Info end-fragments | Dunmore deal → `SetStage(33)`; Pritchard handoff → `SetStage(50)`, `SetStage(60)`. |
| P8 | Player alias or `TLM_Core` | `OnPlayerLoadGame`: re-derive state (§12). |

Everything else (conditions, packages, barter, objective *targets*, markers) is data, not script.
Quest-stage fragments set objectives, so a small amount of CK-generated fragment code is unavoidable. **[VERIFY]** whether a no-code path exists for objective display in this CK version.

### 11.2 Scaffolding: `TLM_MQ01_QuestScript` (**NOT COMPILED, NOT RUN**)

```papyrus
Scriptname TLM_MQ01_QuestScript extends Quest
;; UNTESTED SCAFFOLDING. Function names marked ;;VERIFY must be checked against the CK/Papyrus reference.

GlobalVariable Property TLM_G_CaravanOutcome Auto Const Mandatory
GlobalVariable Property TLM_G_CaravanAliveAtMercy Auto Const Mandatory
ReferenceAlias Property Alias_CaravanMaster Auto Const Mandatory
ReferenceAlias Property Alias_CaravanDrover Auto Const Mandatory
ReferenceAlias Property Alias_CutterLead Auto Const Mandatory
ReferenceAlias Property Alias_CutterA Auto Const Mandatory
ReferenceAlias Property Alias_CutterB Auto Const Mandatory
ReferenceAlias Property Alias_CutterC Auto Const Mandatory

int Property CaravanState = 0 Auto Hidden     ;; derived; stage/global are the truth
int cuttersDown = 0

int Property TIMER_EVADE = 1 Auto Const
float Property EvadeSeconds = 90.0 Auto Const ;; tune in playtest

Function EnterLive()
    If CaravanState >= 2 || !IsRunning()
        Return
    EndIf
    CaravanState = 2
    SetStage(30)
    StartTimer(EvadeSeconds, TIMER_EVADE)       ;;VERIFY StartTimer on Quest
EndFunction

Event OnTimer(int aiTimerID)                    ;;VERIFY OnTimer on Quest
    If aiTimerID == TIMER_EVADE && CaravanState == 2
        ResolveEvaded()
    EndIf
EndEvent

Function CutterDown(ReferenceAlias akWhich)
    If CaravanState < 2
        EnterLive()
    EndIf
    cuttersDown += 1
    If CaravanState == 2 && (cuttersDown >= 4 || akWhich == Alias_CutterLead)
        ResolveSaved()
    EndIf
EndFunction

Function ResolveSaved()
    If CaravanState != 2
        Return
    EndIf
    CaravanState = 3
    TLM_G_CaravanOutcome.SetValue(1)            ;;VERIFY GlobalVariable.SetValue
    SetStage(31)
EndFunction

Function ResolveEvaded()
    If CaravanState != 2
        Return
    EndIf
    CaravanState = 4
    TLM_G_CaravanOutcome.SetValue(2)
    ;; Abel is killed by Cutters; Nell survives wounded; cargo looted.
    ;; Kill(...) and un-protecting are VERIFY items.
    SetStage(32)
EndFunction

Function ResolveExploited(bool abBetrayal)
    If CaravanState != 2
        Return
    EndIf
    CaravanState = 5
    TLM_G_CaravanOutcome.SetValue(3)
    SetStage(33)
EndFunction
```
Deliberately omitted until built in the CK: distance polling, kill/protection toggling, town failsafe, recovery. Each needs real alias references to test against.

---

## 12. Persistence, failure and reload cases

**Principle:** the **stage** and the **globals** are authoritative. Script variables are caches. After any load, state must be re-derivable from stage and globals.

| Case | Risk | Mitigation |
|---|---|---|
| Save/load mid-encounter (state LIVE) | Timer lost, state variable reset | P8 on `OnPlayerLoadGame`: if stage ≥ 30 and no outcome stage set, restart the evade timer. **[VERIFY]** whether timers persist across saves. |
| Reload from each stage (10/20/30/31/32/33/40/50/60) | Alias unfilled; script not attached | Re-test every stage in the matrix (§14). |
| Player dies in the fight | State half-applied | Death reloads; no persistent effect until an outcome stage sets. |
| Player never loots the dispatch | Quest can't progress | Pritchard "no dispatch" branch (§8.3 B); stage 900 re-adds a replacement dispatch if the original is destroyed. |
| Dispatch dropped/stolen/destroyed | O10/O20 dead | Quest-object flag prevents destruction; stage 900 fallback. |
| Pritchard killed | Dead end | `Essential` for the slice. |
| Nell or Abel killed by the player | Wrong outcome | `OnDeath` P5 → Exploited/Betrayal. |
| Nell dies elsewhere (not by player) | Witness assumption | Re-check `IsDead` at stage 50 before choosing the Pritchard variant. |
| Player reaches town first | Out-of-order | O10 remains; no soft-lock. |
| Player leaves the area then returns | Evade fires prematurely | Evade only resolves from LIVE; later returns are cosmetic. |
| Caravan never reaches town | Nell not in clinic | Stage 40 failsafe moves her. |
| Cutters stuck/unreachable | SAVED never fires | Stage 900 "force-resolve after N minutes of idle LIVE". **[VERIFY design in test]** |
| Plugin updated mid-playthrough | Orphaned script instances/aliases | Treat structural alias changes as save-breaking; new game for slice tests. |
| Mod removed | Orphaned scripts | Not supported in slice; document it. |

**Recovery (stage 900) must:** restore a valid dispatch, re-display the correct objective, set `CaravanState` to match the outcome global, and log silently. It must never grant anything beyond restoring what the player already earned.

---

## 13. Naming hygiene (flags for owner; nothing changed in the registry)

**New names proposed for MQ01** (all pass exact-name check against the registry; checked for first-letter/voice-tag clustering): Tobias Gantt, Nell Fenwick, Abel Rudd, Reese Dunmore, Corwin Haskell, R. Ostrander (SQ01 inspector, off-screen).

**Existing near-collisions I noticed while checking** (not fixed here; the registry belongs to the owner):
| Pair | Issue |
|---|---|
| Irena **Sable** / **Sable** Echo | Same word, different characters |
| Marcus **Thorne** / Elara **Thorn** | Near-homophones |
| Marcus Thorne / Marius Haldane | Near-identical given names |
| Tomas Arden / Tomas Belden | Same given name |
| Evelyn **Harrow** / Elise **Marrow** | Rhyme |
| Mara Vale / Celia Marr / Elise Marrow | Similar syllables |
| **Miriam** Keene / **Miriam** Kade | Same given name (the surnames were changed, the first name was not) |
| Seren Ash**fall** / Malcolm **Ash** / Ashen Brotherhood | "Ash" overload |

Not blockers for MQ01 except that Keene appears here; consider renaming one Miriam before voice-script work.

---

## 14. Test matrix

All commands in this table are the author's recollection of the Fallout 4 console and are **[VERIFY]**: `coc <cell>`, `startquest`, `setstage <quest> <n>`, `getstage`, `sqs` (show quest stages), `sqt` (show targets), `prid`, `kill`, `tgm`, `player.additem`.

| # | Scenario | Steps | Expected | Result |
|---|---|---|---|---|
| T01 | Clean dev start | `coc` to wreck; `startquest TLM_MQ01` | Stage 10; O10 shown; player at start marker; no ammo | ☐ |
| T02 | Dispatch pickup | Loot case | Stage 20; O10 complete; O20 shown | ☐ |
| T03 | Revolver hint | Pick up revolver | Stage 15; hint once | ☐ |
| T04 | Skip revolver | Never take it | Quest still completable | ☐ |
| T05 | Saved by fight | Kill all Cutters | Stage 31; Outcome 1; Abel and Nell alive | ☐ |
| T06 | Saved by lead kill | Kill Dunmore only | Rest break; Outcome 1 | ☐ |
| T07 | Saved by speech | Pass speech check | Cutters withdraw; Outcome 1 | ☐ |
| T08 | Speech fail | Fail check | Combat starts; still reachable | ☐ |
| T09 | Evade by walking | Walk past, no shots | Timer/distance → Outcome 2; Abel dead; Nell alive | ☐ |
| T10 | Evade by stealth | Sneak around | Outcome 2 | ☐ |
| T11 | Deal | Accept deal | Stage 33; Outcome 3; cargo share; Nell alive | ☐ |
| T12 | Betrayal | Kill Abel/Nell | Outcome 3 Betrayal; no witness | ☐ |
| T13 | Take cargo after SAVED | Loot wagon | Counts as theft (faction-owned); no outcome change | ☐ |
| T14 | Fight then leave | Start combat, walk away mid-fight | No premature Evade after combat engaged | ☐ |
| T15 | Reload mid-encounter | Save in LIVE, quit, load | Timer/state restored (P8) | ☐ |
| T16 | Reload at each stage | 10/20/30/31/32/33/40/50/60 | Objectives and aliases correct | ☐ |
| T17 | Town first | Go to Pritchard without dispatch | Branch B; O10 stays; no soft-lock | ☐ |
| T18 | Skip wreck loot, take dispatch late | Return to wreck | Completes normally | ☐ |
| T19 | Dispatch dropped | Drop/transfer case | Quest-object protection; 900 repair | ☐ |
| T20 | Pritchard essential | Attack him | Falls, not dies; reachable | ☐ |
| T21 | Nell dead (non-player) before stage 50 | Kill via console | Correct Pritchard variant | ☐ |
| T22 | Night arrival | Arrive 02:00 | Pritchard reachable | ☐ |
| T23 | Reputation | Complete each outcome | §9.1 values exact | ☐ |
| T24 | Metrics | Each P1 branch | §9.2 values exact; nothing gated | ☐ |
| T25 | Confess vs deny | Exploit-Deal; each answer | Dialogue variants; no combat punishment | ☐ |
| T26 | Completion | Reach 100 | `MQ01_Done = 1`; MQ02 hook text | ☐ |
| T27 | Clean plugin load | Fresh profile, plugin only | No missing-master/script errors in logs | ☐ |
| T28 | Unrelated saves | Load a vanilla save with plugin disabled/enabled | No corruption | ☐ |

---

## 15. Creation Kit click-path checklist (build order)

Steps are order-of-work, not exact menu paths. **[VERIFY]** menu and tab names against the installed CK.

- [ ] **0 Environment.** Install CK; extract base Papyrus source; create `TheLastMeridian.esp` with `Fallout4.esm` master only; save immediately.
- [ ] **1 Globals.** Create the §3 globals (short, default 0). Create `TLM_G_DataVersion`.
- [ ] **2 Factions.** `TLM_Fac_Cutters`, `TLM_Fac_Caravan`, `TLM_Fac_MercyCrossing`; set Cutters hostile to player/caravan.
- [ ] **3 Items.** Copy the chosen revolver and ammo into `TLM_` records; create `Dispatch`, `TornTransitPass`, `MarshalLog`; place a note/book form for the dispatch.
- [ ] **4 Test cell.** Build the temporary logic cell (T2-b): wreck area, road stretch, ambush area, mini-town gate. Add the markers/triggers in §3.
- [ ] **5 Actors.** Create all §5 NPCs; set aliases-to-be flags (Essential/Protected) in *aliases*, not on base actors where possible. Attach packages.
- [ ] **6 Quest shell.** Create `TLM_MQ01`; set Quest Data per §6.1.
- [ ] **7 Stages.** Create stages from §6.2, with log entries.
- [ ] **8 Objectives.** O10 and O20 with alias targets.
- [ ] **9 Aliases.** Create aliases per §6.4, fill types and flags. Attach alias scripts P1–P6.
- [ ] **10 Quest script.** Create `TLM_MQ01_QuestScript`, fill properties; compile; fix errors.
- [ ] **11 Fragments.** Stage fragments to display/complete objectives; topic end-fragments for P7.
- [ ] **12 Dialogue.** Create branches for §8: Dunmore (greeting + deal), Nell (3 states), Pritchard (P0–P2). Set conditions per §8. Add the speech-check infos.
- [ ] **13 Barter.** Ada/Vane/Keene vendor containers (small).
- [ ] **14 Navmesh and AI.** Navmesh test cell; verify NPCs path.
- [ ] **15 Run T01–T28.** Log results in the matrix; file issues for failures.
- [ ] **16 Port to the real worldspace** (T2-a) only after logic passes; repoint aliases/markers; re-run T01–T28.
- [ ] **17 Tag** the `.esp` (§16).

---

## 16. Rollback

- **Branch:** one feature branch per milestone. Merge only after the matrix passes.
- **Binary plugin:** tag the `.esp` at each green milestone (`mq01-logic-proof`, `mq01-worldspace`, …). Rollback = restore the previous tagged `.esp` and its `.psc`.
- **Saves:** quest and alias structure changes can orphan script instances in existing saves. **Test saves are disposable.** Do not promise save compatibility before a release candidate.
- **Feature toggles:** the encounter's actors are enabled by stage 10 only, so disabling that single step reverts MQ01 to a no-ambush version without touching the rest.
- **Docs:** this design is versioned in git; do not edit canon files to "match" an implementation without a documented decision (CLAUDE.md).

---

## 17. Open questions for the owner

| ID | Question | Proposal |
|---|---|---|
| Q1 | T1/T2/T3 (§2.4): start technique, geography, pack animals. | As recommended in §2.4. |
| Q2 | Is `Rail Marshal Tobias Gantt` + a dispatch the right opening artifact? | Yes; ties to Chapter 05 (Blackstone Station) via "Corridor line keeps losing marshals." |
| Q3 | Does Pritchard know the player? | **No.** Ch01 treats the player as a stranger off the wreck. |
| Q4 | What is in the dispatch? | Provisional: a sealed request to audit freight and maintenance records on the line, plus Gantt's note that his inspector's reports "don't add up." This sets up SQ01 and the Chapter 02 rail thread without invoking the Deep. |
| Q5 | Does "six rounds" have an in-story meaning? | Optional callback: Pritchard asks how many rounds are left. No mechanical effect. |
| Q6 | Keep `TornTransitPass`? | Yes, as a silent seed; cut if the owner wants zero Deep hints before Chapter 05. |
| Q7 | Do SQ01 outcomes map onto the doctrine's flags (`TLM_OpenLedgerDiscovered`, etc.)? | **No** for Act I. Keep them reserved for Act II. |
| Q8 | Name approvals (§13) and the Miriam collision. | Owner decision. |
| Q9 | DLC dependency. | None for v0.1. |

---

## 18. Definition of done for MQ01 v0.1
All of §14 passes in the CK test cell **and** after porting; stage 100 reached on at least the Saved, Evaded and Exploited paths; no soft-lock found in the T17–T22 cases; no vanilla record edited; no vanilla asset committed; this document updated with whatever the CK walkthrough corrected.
