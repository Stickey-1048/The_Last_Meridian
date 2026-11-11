# TLM_SQ01 — Signed Clean: Evidence-Based Secondary Objective

**Status:** DESIGN DRAFT v0.1, 2026-11-11. Not implemented. Not tested. Awaiting owner review.
**Parent doc:** [TLM_MQ01 — Six Rounds to Mercy](TLM_MQ01_six-rounds-to-mercy.md). Read its verification-status box first; the same caveats apply. Items marked **[VERIFY]** are unchecked against the Creation Kit.

---

## 1. What this is

A short optional quest, triggered by something the player finds at the train wreck: **the train's maintenance ledger says the brakes and couplers were inspected and sound. The wreckage says otherwise.**

It exists to deliver the Open Ledger theme in the opening hours **without a speech**:
- Two ledgers disagree (the line's official one and an independent one), and the player has to decide what the gap proves.
- The player can publish, report, sell or bury the finding.
- If the player claims more than the evidence supports, an innocent person pays, and the player is accountable for that.

**It is a symptom, not a reveal.** It must not mention the Deep, the East Galleries, the Open Ledger Charter or the player's family. (CANON.md; doctrine-of-the-open-ledger.md, "Act I – Symptoms".) The only link is thematic: a record that claims everything is fine while something has quietly gone wrong, and the question of who answers for it.

### Canon fit
| Rule | How SQ01 complies |
|---|---|
| Optional content never gates the main quest | SQ01 is never required for MQ01 stage 100 or any later chapter. |
| No new principal faction | The accused institution is the **Iron Junction yard office**, an existing locale from Chapter 02, not a power bloc. |
| Silas Vane's arc belongs to Chapter 04 | Vane may *buy* the ledger but is **not** shown to be guilty or innocent. |
| Player is held to the same standard | The scapegoat branch (§6, option C) is the player's own error. |
| Consequences, not monologues | Choices are short options and a message box. |

---

## 2. Design thesis: "Signed clean"

An inspector's signature certifies an inspection took place. The story question is not *who is the villain* but **how much does this evidence actually prove, and what do I do with a partial answer?**

- A physical clue shows *something was missed* (neglect or fraud).
- A dead man's signature shows *fraud*, but not *who*.
- An independent parts book shows *the repair could not have happened*, still not *who*.
- No evidence in MQ01 names an individual. **The responsible party is deliberately unresolved**, left for Chapter 02 (Iron Junction), so any player who names a person in MQ01 is guessing.

---

## 3. Evidence

### 3.1 Items and sources

| ID | Evidence | Where found | What it shows | Level |
|---|---|---|---|---|
| **E0** | `TLM_BOOK_RailMaintLedger`: the line's maintenance ledger | Locomotive cab lockbox (`TLM_CONT_CabLockbox`) | The *claim*: brake shoes "renewed", draw-bar "inspected, sound", all signed by one inspector. **Picking this up starts SQ01.** | Claim only |
| **E1** | Worn brake-shoe pile | Wreck cell, examinable activator | Shoes worn to the rivets, not new. Contradicts the ledger's "renewed". | Physical |
| **E2** | Cracked draw-bar/coupler | Wreck cell, examinable activator | Old, rust-darkened fracture face: a crack that existed long before the wreck. Contradicts "sound". | Physical |
| **E3** | `TLM_BOOK_MarshalLog`: Rail Marshal Gantt's pocket journal | On the dead marshal (`TLM_NPC_MARSHAL_DEAD`) | Records that inspector **R. Ostrander** died of fever at Greenwater **before** the dates on the ledger's most recent signed entries. A dead man cannot have signed them. | Document: **falsification** |
| **E4** | Ada Pike's parts book | Dialogue with Ada Pike | The line stopped buying brake shoes from her several months ago. She keeps her own tally and shows it. The repairs could not have been made with her stock. | Independent ledger |

E1 and E2 are physical and can be examined **before** or **after** E0 is found. Evidence is counted whichever order the player finds it.

### 3.2 Evidence level (computed, hidden)
`TLM_G_SQ01_Evidence` counts distinct items among E1–E4 (E0 is the claim and doesn't count).

| Level | Rule | What the player can truthfully say |
|---|---|---|
| **0** | Has E0 only | "The ledger is odd." (No actionable claim.) |
| **1** | Any one of E1, E2, E3, E4 (E3 alone is level 1; it needs corroboration to reach 2) | "The ledger is wrong." Could be neglect. |
| **2** | **E3** plus at least one other, **or** any three of E1/E2/E4 | "The ledger was falsified." Fraud is established; **author is not.** |

**There is no level that names a person.** This is intentional (see §2).

### 3.3 Draft in-game text (original; not from any existing work)

**Ledger page (E0), excerpt**
```
LINE 14 — LOCO/CAR MAINTENANCE — IRON JUNCTION YARD
Entry  Item                   Action          Result      Signed
 41    Brake shoes, car 3     Renewed         Good        R. Ostrander
 42    Draw-bar, car 3        Inspected       Sound       R. Ostrander
 43    Brake shoes, car 5     Renewed         Good        R. Ostrander
 44    Journal box, car 5     Inspected       Sound       R. Ostrander
```
Show a short entry range; the full ledger text is cosmetic.

**Marshal's journal (E3), excerpt**
```
Greenwater. Ostrander took ill on the 9th. By the 14th he was gone. I carried
the line's word to the yard the same week. Last I saw, no one had been sent in his place.
Odd, then, that every car I rode on this trip came up on the list as "signed clean".
Pritchard will want to see this in person.
```
**Ada Pike (E4), dialogue core:** a short, practical exchange. "They used to buy shoes off me every season. Haven't taken a pair since spring. I kept the count. Here, look." No speech about honesty.

> Avoid any in-world phrase that echoes the Open Ledger Charter's language. The theme should be felt through the object, not the wording.

---

## 4. Quest `TLM_SQ01`

### 4.1 Quest data **[VERIFY labels]**
Quest type: Miscellaneous/side. Start Game Enabled: **No**. Run Once: Yes. Not displayed until started. Started by the **E0 pickup** (alias script) or by speaking to Pike/Pritchard about "something from that train" if the player somehow reaches them first.

### 4.2 Stages

| Stage | Name | Trigger | Effects |
|---|---|---|---|
| 0 | Unstarted | default | |
| 10 | Ledger found | E0 picked up | Start quest; display **O10**; set `Evidence` to count already-examined clues |
| 15 | Evidence updated | Any of E1–E4 acquired | Recompute level; if level ≥ 1 display **O20**; log entry reflects level |
| 20 | Case presentable | Level ≥ 1 | Enables the §6 options. (Level 2 enables the stronger framing.) |
| 50 | Resolved | A §6 option chosen | Apply outcome (§7); complete objectives |
| 100 | Completed | 50 reached | Complete quest |
| **900** | Recovery | Any failsafe, §9 | Re-grant the ledger if lost; recompute level from flags |

### 4.3 Objectives
| ID | Text | Displayed | Completed |
|---|---|---|---|
| O10 | Compare the ledger to the wreck | 10 | 15 (when level ≥ 1) |
| O20 | Decide what to do with the evidence | 15 (level ≥ 1) | 50 |

### 4.4 Aliases
| Alias | Kind | Fill | Notes |
|---|---|---|---|
| `Alias_Ledger` | Reference | Specific ref (placed ledger) | Quest Object; script: pickup → `SetStage(10)` |
| `Alias_Journal` | Reference | Specific ref (on the marshal) | Pickup → set `E3` flag, `RecomputeEvidence()` |
| `Alias_BrakeShoes` | Reference | Specific ref | Activate → set `E1` flag |
| `Alias_DrawBar` | Reference | Specific ref | Activate → set `E2` flag |
| `Alias_Pike` | Reference | Unique Actor | Dialogue topic sets `E4` flag |
| `Alias_Pritchard` | Reference | Unique Actor (shared with MQ01) | Option A |
| `Alias_Vane` | Reference | Unique Actor | Option C |
| `Alias_Haskell` | Reference | Unique Actor | Scapegoat risk (option B, name) |
| `Alias_NoticeBoard` | Reference | Specific ref | Option B |

Evidence flags are **globals or quest-script ints** (not stages) so they can arrive in any order and persist: `TLM_G_SQ01_E1..E4` (0/1), `TLM_G_SQ01_Evidence` (0–4 derived), `TLM_G_SQ01_Outcome` (0–6).

---

## 5. Why examine-and-compare instead of a minigame
Fallout 4 gives us activators, note forms, objectives and dialogue. A custom comparison UI would be new tech for a vertical slice and would be the first thing to break. "Walk to the wreck, read the page, look at the part, and compare" is **diegetic, cheap, and already teaches scavenging**.

Examinable parts should show a short **Message** (`TLM_MSG_E1`, `TLM_MSG_E2` **[VERIFY]**) with the observation, not a conclusion ("The shoes are ground to the rivets."). The *player* draws the contradiction with the ledger.

---

## 6. The decision (what the player does with it)

Available from stage 20. Four routes; all legitimate; each has a price.

### A. Report it to Sheriff Pritchard (formal)
Dialogue option in MQ01 node P0.A: *"There's something else from that train."* Pritchard asks to see the ledger and journal, takes copies, and sends word to the line. Requires level ≥ 1.
- Slow: no immediate payoff.
- Pritchard becomes an advocate: a flag later makes Iron Junction's yard hostile to the player until Chapter 02 sorts it out (`TLM_G_SQ01_YardAlerted = 1`).
- Safest for the player and for bystanders; also the least dramatic. **That is a legitimate design.**

### B. Post it publicly on the Mercy Crossing notice board
Activating `TLM_ACTI_NoticeBoard` opens `TLM_MSG_PublishChoice` **[VERIFY message-button limit]**. The choices are short text buttons. No NPC speech is needed.

| Button | Available when | Result |
|---|---|---|
| **Post the pages, no name** | Level ≥ 1 | Pages go up. Townsfolk gather and argue. No one is accused. |
| **Name the Yard Office** | Level **2** | As above, with the claim that the Iron Junction yard falsified it. Justified by the evidence. |
| **Name Corwin Haskell** | Level ≥ 1 | The freight agent who signs the *receiving* page at Mercy Crossing. **No evidence implicates him.** He is run off. See §7. |
| Cancel | always | Nothing happens. |

### C. Sell it to Silas Vane
Dialogue topic with Vane, available from level ≥ 1. He pays caps for the ledger and journal ("Paper like this makes trouble for everyone").
- The player loses the evidence (it is removed from inventory and the flags freeze).
- Flag for Chapter 04: `TLM_G_SQ01_VaneHasLedger = 1`.
- **Vane is not shown to be guilty or innocent.** He just takes it.

### D. Keep it, destroy it, or do nothing
No dialogue required. The ledger stays in inventory, or the player can drop/burn it. No outcome fires; SQ01 stays at stage 20 and the evidence remains usable later. Choosing to **destroy** records outcome 6 and changes nothing else.

---

## 7. Outcomes and consequences

`TLM_G_SQ01_Outcome`: 0 none, 1 reported, 2 posted (no name), 3 posted (Yard Office), 4 posted (**Haskell**), 5 sold, 6 destroyed.

| Outcome | World effect | Truth | Competence | Accountability | MutualTrust |
|---|---|---|---|---|---|
| 1 Reported | Pritchard has the copies; `YardAlerted = 1` | +1 | +1 | | |
| 2 Posted, no name | Town gathers, argument ensues, nothing escalates | +1 | | | |
| 3 Posted, Yard Office (level 2) | As 2; townsfolk direct anger at the yard | +1 | +1 | | +1 |
| **4 Posted, Haskell** | **Haskell is run out of town** (`HaskellScapegoated = 1`; he is disabled/moved off-map by script). Keene and Pike say so, plainly. | **−1** | **−1** | **−1** | **−1** |
| 5 Sold | Ledger gone; `VaneHasLedger = 1`; caps received | 0 | | | |
| 6 Destroyed | No effect | −1 | | | |

(Metric names from doctrine-of-the-open-ledger.md. Not shown to the player. **No Act I content may be gated on them.**)

### 7.1 The scapegoat branch is the point
Option **B-Haskell** is only reachable if the player chooses to name someone the evidence does not name. **The game never tells them it is wrong at the moment of choice.** Afterwards:
- Haskell is gone; Keene and Pike each have one line about it that **states the facts without moralizing** ("Corwin signed for freight. That's all he did").
- A **repair path** exists but is deferred: a later optional quest (not in the slice) lets the player clear his name once the real source is found at Iron Junction. Flag: `TLM_G_SQ01_HaskellScapegoated`.
- This is the design's direct expression of the doctrine's rule that **the player must meet the same accountability standard as their opponents** and that their judgment is not guaranteed flawless.

### 7.2 Hooks for later chapters (flags only; nothing built)
| Flag | Consumer |
|---|---|
| `YardAlerted` | Ch02 Iron Junction: the yard is wary of the player. |
| `VaneHasLedger` | Ch04 The Black Ledger: Vane already holds one ledger. |
| `HaskellScapegoated` | Optional repair quest; Mercy Crossing barks. |
| `SQ01_Outcome` | Act III evidence/legitimacy evaluation (owner to decide). |

---

## 8. Papyrus responsibilities (**UNTESTED**; keep minimal)

| ID | Attached to | Responsibility |
|---|---|---|
| S1 | `Alias_Ledger` | Pickup → `SetStage(10)`. |
| S2 | `Alias_Journal` | Pickup → set E3; recompute. |
| S3 | `Alias_BrakeShoes`, `Alias_DrawBar` | `OnActivate` → set E1/E2; show message; recompute. |
| S4 | Pike topic fragment | Set E4; recompute. |
| S5 | `TLM_SQ01_QuestScript` | `RecomputeEvidence()` (counts flags, sets level, advances 15/20); `ApplyOutcome(int)` applies §7 and sets stage 50. |
| S6 | `Alias_NoticeBoard` | `OnActivate` → show `TLM_MSG_PublishChoice`, branch on the returned index **[VERIFY Message.Show return value]**; call `ApplyOutcome`. |
| S7 | Vane topic fragment | Remove ledger/journal from the player **[VERIFY RemoveItem usage]**; `ApplyOutcome(5)`. |

`ApplyOutcome(4)` must `Disable()`/move Haskell and set the flag. **[VERIFY]** the right call to remove an NPC from the world without leaving a dangling alias.

**Scaffolding intentionally not provided here.** It depends on aliases and messages that don't exist yet. Write it once the records are built in the CK.

---

## 9. Persistence, failure and reload

| Case | Risk | Mitigation |
|---|---|---|
| Player never goes to the wreck's cab | SQ01 never starts | Fine; it is optional. |
| E1/E2/E3 examined **before** E0 is found | Evidence lost | Flags are globals; E0 pickup recomputes. |
| Ledger dropped or lost | Can't proceed | Quest object protection; stage 900 re-grants. |
| Player sells then tries to post | No evidence | After outcome 5, boards/options are disabled. |
| Haskell killed by the player or elsewhere | Alias/consequence conflict | Check `IsDead` before `ApplyOutcome(4)`; if dead, use "posted, no name" semantics and log. |
| Pike dead before E4 | E4 unreachable | Level 2 still reachable via E3 + E1/E2. |
| Marshal's journal destroyed | E3 lost | Quest-object flag. |
| Reload after outcome | Flags/outcome | Outcome is a global; stage 50 is authoritative. |
| Load order: board message before level ≥ 1 | Option misfire | Gate with conditions on `Evidence`. |

---

## 10. Test matrix

| # | Scenario | Expected | Result |
|---|---|---|---|
| S01 | Pick up E0 only | Stage 10; O10; level 0; no options | ☐ |
| S02 | Examine E1 first, then E0 | Level counts E1 on pickup | ☐ |
| S03 | E0 + E1 | Level 1; O20 shown | ☐ |
| S04 | E0 + E3 + E1 | Level 2 | ☐ |
| S05 | E0 + E1 + E2 + E4 (no E3) | Level 2 | ☐ |
| S06 | Option A (report) | Outcome 1; flags; Pritchard line | ☐ |
| S07 | Option B, no name | Outcome 2 | ☐ |
| S08 | Option B, Yard Office at level 1 | Button **not offered** | ☐ |
| S09 | Option B, Yard Office at level 2 | Outcome 3 | ☐ |
| S10 | Option B, Haskell | Outcome 4; Haskell gone; −1 across metrics; Keene/Pike barks | ☐ |
| S11 | Option C (sell) | Outcome 5; caps; items removed; `VaneHasLedger` | ☐ |
| S12 | Option D (destroy) | Outcome 6 | ☐ |
| S13 | Do nothing | Stage 20; evidence persists | ☐ |
| S14 | Ada Pike dead | Level 2 still reachable | ☐ |
| S15 | Skip SQ01 entirely | MQ01 completes normally | ☐ |
| S16 | Reload at 10/15/20/50 | State and options correct | ☐ |
| S17 | Report after posting | No double outcome | ☐ |

---

## 11. Build checklist (CK click-path)

- [ ] **0** Prereqs from MQ01 §15 done.
- [ ] **1** Globals: `TLM_G_SQ01_E1..E4`, `TLM_G_SQ01_Evidence`, `TLM_G_SQ01_Outcome`, `TLM_G_SQ01_YardAlerted`, `TLM_G_SQ01_VaneHasLedger`, `TLM_G_SQ01_HaskellScapegoated`.
- [ ] **2** Forms: `TLM_BOOK_RailMaintLedger`, `TLM_BOOK_MarshalLog`; **create the text** from §3.3.
- [ ] **3** Placed refs in the wreck cell: cab lockbox + ledger; shoe pile; draw-bar; journal on the marshal.
- [ ] **4** Messages: `TLM_MSG_E1`, `TLM_MSG_E2`, `TLM_MSG_PublishChoice`.
- [ ] **5** Quest shell, stages, objectives, aliases (§4).
- [ ] **6** Dialogue: Pike E4 topic; Vane sale topic; Pritchard option A (in MQ01 P0.A); barks for Keene/Pike about Haskell.
- [ ] **7** Scripts S1–S7; compile.
- [ ] **8** Run S01–S17; log results.
- [ ] **9** Port with the world (MQ01 §15 step 16).

### Rollback
Everything is additive and self-contained. Removing SQ01 means removing the cab lockbox, the quest, and the topics, and nothing in MQ01 depends on it except one optional Pritchard option (hidden when the quest isn't running).

---

## 12. Open questions for the owner

| ID | Question | Proposal |
|---|---|---|
| S-Q1 | Is **no named culprit in MQ01** acceptable? | Yes: it keeps Chapter 02 meaningful and makes the scapegoat branch a real test. |
| S-Q2 | Should an *innocent* person ever pay for the player's mistake in the opening hours? | Yes, with a deferred repair path; it is the most direct way to show "you are held to the same standard." Owner may soften to reputation-only. |
| S-Q3 | Does Vane buying the ledger prejudge his Chapter 04 arc? | No: his motive is stated ambiguously. Confirm. |
| S-Q4 | Does the inspector's death at Greenwater conflict with the planned Greenwater "missing food" thread? | Probably a useful cross-link; owner to confirm before Chapter 02 is designed. |
| S-Q5 | Is the maintenance version right, or should the falsified record be a **ration** ledger? | Maintenance fits the wreck and the "sabotage vs neglect" tension in Ch02. A ration version fits the Deep theme more directly but needs more town scaffolding. Both can exist later. |
| S-Q6 | Dispatch content (MQ01 Q4) assumed to reference audit of maintenance records. | Confirm. |
