# Greenwater owner playtest: payment-choice clarity

Signed Nora, independent narrative/player UX reviewer,17 November2026. Read-only review of source `1cdd4666b12e3b40f0c3bf5a3e877f561c7b8d83` in `work/red-hollow-source-rereview-ab4e01b`. No live edits, game/input, install, replay request or source mutation.

**Disposition: choice clarity NOT PASS. Recommend a small candidate-only technical consequence confirmation before payment, preserving accepted NPC speech. The observation does not establish an unintended controller input, scripted misdelivery or intentional player betrayal.**

## What is actually known

Coordinator reported ordinary owner controller play on the current runtime: Greenwater10 at08:29:38, then20/30/50/40/44 by08:32:39 and100 at08:33. Asked whether deliberately accepting Hatcher's payment/telling Opal the grain was lost matched the intended choice, the owner replied: **“The choice or result was unclear.”** The follow-up about what the owner thought they accepted remains pending. These are coordinator-provided live observations; I did not observe the screen or input.

The provided stage44/100 sequence establishes the logged paid-share branch, not the player's understanding, and not by itself TellLie, grain_sold or Opal's stage46 reply. Do not record a combined bribery-plus-lie intentional-choice pass from this evidence. No replay of the already completed branch is needed just to collect this clarity finding.

## Exact source sequence

`assets/incoming/act1/story/talk/tlm_mq02b.json` preserves accepted `hatcher_share` speech: Hatcher offers two hundred and a berth, tells the player to tell Opal the Chute took it, and explicitly says soup is not replacement winter grain. Its buttons are simply **“Done.” / “No.”** The earlier entry says **“Sell me a share, Commodore.”** This colloquial framing can obscure who receives the money and which consequential route is being settled; that is a source-grounded clarity hypothesis, not proof of this owner's thought process.

`GreenwaterWalk.psc:964 BuyShare` treats button0 from `SayHatcherShare` as authorization, revalidates road/Hatcher/unsettled context, then calls `TakeShare`. `MQ02BQuest.psc:537` claims the share route, pays200caps once, verifies arrival, records outcome/stage44 and closes the competing cargo-route choice. The grain remains aboard the Queen. A promised berth is accepted character speech, not an implemented transport-service promise. Current technical interim journal/report says: **“You accepted Hatcher's share. The grain remains aboard the Queen.”** Stage100 can complete from the paid share alone (`CanComplete`), without lying to Opal.

The lie is a separate ordinary Opal interaction: `GreenwaterWalk.psc:765 AfterShare` first presents `AskLie`, currently **“Opal Starnes has not heard what became of the barge.”**, buttons **“Tell her the Chute took it” / “Say nothing of it.”** Only the first valid choice plus current Opal context reaches `TellLie` (`MQ02BQuest.psc:575`). That sets grain_sold because payment and the delivered lie have both happened. Opal's actual valid reply separately commits stage46/meal through `LieWasHeard`; cancellation or missing reply must not erase an already delivered lie. These boundaries should remain intact.

## Smallest recommended clarification

Preserve exact accepted Hatcher/Opal speech and authored dialogue buttons. Add a clearly technical consequence confirmation **between valid Hatcher “Done.” and `TakeShare`**, before any claim, caps transfer or stage44:

> [Accept Hatcher's deal?]
>
> Receive200caps and leave the grain aboard Hatcher's barge. This settles your cargo choice; Greenwater does not get its grain back. Telling Opal a false story remains a separate choice.

Buttons: **“Accept200caps; leave the grain”** / **“Cancel; make no deal”**. Use normally spaced rendered text (“Receive 200 caps”, “Accept 200 caps”) when implementing. Cancel/invalid/context loss closes without payment or route claim; do not automatically return into another consequential choice. Recheck current Hatcher/road/claim context after this new page and before the existing once-only payment function. No payment reversal, new branch or route reset is proposed.

For the already technical `AskLie`, minimally make the deception explicit before its existing commit:

> [Lie to Opal?]
>
> The grain is still aboard Hatcher's barge. Tell Opal it was lost in the Chute instead?

Buttons: **“[Lie] Say the Chute took it”** / **“Do not tell that story”**. This is candidate technical UI, not a rewrite of Opal's response. Keep payment separate from the lie and her reply; do not imply the earlier deal automatically delivered either.

A valid paid-share result notice can retain existing journal truth while stating **“200caps received; the grain remains with Hatcher.”** This is optional reinforcement, not a substitute for before-commit clarity. Do not describe the result as recovered grain or a berth/transport service implemented for the player.

## Narrow acceptance gates for a future change

- Explicit payment acceptance alone pays once, leaves grain with Hatcher, records44; cancel/invalid/lost context pays nothing and commits no route.
- Already paid repeat activation never offers another payment or cargo-route reset.
- Separate explicit lie acceptance records grain_sold only with the existing paid/current-Opal conditions; decline closes without a lie. A valid later Opal reply alone earns46 and its reward.
- Readable controller labels, selection and the intended outcome must be observed in a future ordinary-input test. Current completed owner route remains useful native evidence, with **understanding/intent unresolved**, not a clarity pass. Do not demand immediate owner replay while Iron Junction testing remains available.

No broad harness, new quest, new canon or live build is requested by this review. Root owns any separately authorized candidate implementation and independent/native checks.

## Owner clarification: scene comprehension is the primary finding

The owner subsequently said: **“the whole thing was unclear. there was a barge, there was corn, there were people on the barge, I assumed that someone wanted me to be quiet, but it's hard to really know what was what.”** This broadens the finding from a payment button to goal, character roles and physical scene comprehension. It does not identify a controller-delivery defect or prove deliberate payment-plus-lie intent. No further owner question or immediate replay is required. The current Iron Junction playtest can continue while a separate candidate is prepared; do not hot-patch the running session.

### Bounded engineering-ready clarity packet

All additions below are explicitly technical orientation/UI. Preserve accepted NPC speech/buttons, canon, the four route mechanics, actor identities, quest triggers, old frozen packages and all existing placements. No new service, companion, animated boat ride, tally of deaths or evidence revelation is introduced. Freshly compile/pin every actually changed script; do not label a changed runtime as the old normal29 package.

**1. Entry orientation, before the player must interpret the scene.** Add technical `TLM_MSG_GW_ArrivalBrief` to `SpecGreenwater.cs`, property on `GreenwaterWalk`, bound by existing message projection. Hook it once per actual successful outward `Travel` after current player/arrival position is verified, before returning control; do not set a quest stage just to show it. One explicit Continue/invalid-close only, no automatic dialogue/choice. Do not open it from an unclaimed trigger callback concurrently with another message.

Exact text (title `[Greenwater: your task]`):

> Opal Starnes needs the town's winter grain back. Speak to her at the landing. Hatcher holds the grain barge beside the Queen of Tellico. The Queen is his occupied gambling boat; it is NOT the grain barge. Signs identify both staged areas.

Button **“Find Opal at the landing”** is an acknowledgement, not movement or forced activation. Repeat travel after44/100 must not reissue an unresolved-task assertion: use current-state technical overview instead, or leave the initial brief initial-only. Later interaction with the existing landing label always permits rereading role/layout information without resetting progress.

**2. Make existing labels visible and informative; preserve locations.** These are actual `Greenwater.Parts` and `WorldStory.GreenwaterSites`, not proposed new destinations:

| Actual alias / current site XYZ | Activation/display name | Technical page replacement or additional current-state page |
| --- | --- | --- |
| `LabelLanding` (1880,580,12), `TLM_ACTI_GW_LabelLanding` | `Greenwater landing - find Opal` | `[Greenwater landing]` / `Opal Starnes keeps the food stores here. Her winter grain is held beside Hatcher's Queen, not at this landing. Speak to Opal, then to Mose Rafferty about reaching the boats. The Mercy return point is nearby.` |
| `LabelQueen` (2520,600,12), `TLM_ACTI_GW_LabelQueen` | `Queen gambling boat - Hatcher and crew` | `[Queen of Tellico - occupied boat]` / `This marked area stands for Hatcher's gambling boat. Hatcher is at the card table with his crew nearby. The grain is on the separate barge off this deck, beside the chain and pilot lever. Fire threatens both people and grain.` |
| `CargoLashed` (2680,300,12), `TLM_ACTI_GW_CargoLashed` | `Opal's grain barge - tied to the Queen` | `LabelCargoLashed`: `[Grain barge - separate cargo boat]` / `These crates stand for Greenwater's winter grain aboard the barge tied beside the Queen. This is the cargo Opal needs. It is separate from Hatcher's occupied gambling boat.` |
| `Table` (2600,540,12), `TLM_ACTI_GW_Table` | `Hatcher's card table - grain or payment` | Use existing ordinary Hatcher/table interaction and exact accepted speech; do not add a second unrelated consequence commit here. |
| `Chain` (2740,300,12), `TLM_ACTI_GW_Chain` | `Grain barge lashing - inspect choices` | Keep existing warning/explicit route choices and physical effects. The label must not imply examination already cuts the chain. |
| `Pilot` (2790,340,12), `TLM_ACTI_GW_Pilot` | `Grain barge pilot - move freed cargo` | Preserve existing freed/current-cargo guards and explicit travel acknowledgement. No actual moving-boat/navigation claim. |

Source handling: `Used` already routes labels and `LookAtCargo` selects actual current cargo messages. **Do not put the unresolved initial-goal text on every state.** After44, landing/cargo current-state overlay must say `You accepted Hatcher's payment. The grain remains with him; Greenwater did not receive it.` After whole/reduced recovery, existing actual12/12,8/12,6/12 pages remain truthful. After actual fire/cargo destruction, show the existing destroyed state rather than present grain as still safely held. Missing/dead cast means “find/speak” direction must be conditional or use an appropriate neutral layout page, not ghost dialogue.

**3. Reinforce Opal's goal at the existing stage20 boundary.** After the first complete eligible accepted `starnes_first`/goal conversation, show optional technical `TLM_MSG_GW_Goal` only within that same conversation claim, with context recheck. Exact title `[Your choices concern the grain]`; text:

> Opal wants the winter grain returned. Hatcher has it beside the Queen. You can negotiate at his table or investigate the barge with Rafferty. Taking Hatcher's money leaves the grain with him. No route is chosen by this note.

Button **“Continue”**. It acknowledges information only. No automatic Hatcher judgment, card game, purchase, chain/fire action, evidence fact or forced travel. Existing stage20 objective should retain approved story content; a separate technical note can supply clarity without rewriting the journal's accepted voice.

**4. Before the irreversible paid route.** Add technical `TLM_MSG_GW_ConfirmShare`, property/binding, in `BuyShare` after a valid accepted Hatcher “Done.” but before `TakeShare`. Exact title `[Accept Hatcher's deal?]`; text:

> Receive 200 caps and leave the grain aboard Hatcher's barge. This settles your cargo choice; Greenwater does not get its grain back. Telling Opal a false story remains a separate choice.

Buttons **“Accept 200 caps; leave the grain”** / **“Cancel; make no deal”**. Only exact first-button plus current road, table/Hatcher and unsettled state may call the existing once-only `TakeShare`. Cancel/invalid/lost context closes without another implicit choice. Successful payment can show current-state technical acknowledgement `200 caps received. The grain remains with Hatcher. You have not told Opal anything yet.` **Only show its last sentence if `IsLieTold` is false**; never erase a true prior fact or assert it as a repeat-state default.

**5. Keep the lie visibly separate.** Replace existing technical `TLM_MSG_GW_AskLie` title/body/buttons with the explicit Lie prompt above; leave `TellLie`, `LieWasHeard` and exact accepted Opal speech unchanged. Do not show it as a request to remain generally silent or as evidence of a previous crime. `Say nothing` must mean only declining this lie now, not erasing the payment or automatically telling the truth. Native stage44 alone is not grain_sold/46 proof.

### Small visual increment: identify, do not rebuild

The actual current scene is flat staged ground: landing actors/food at x1800–2330; Queen/table/crew at x2450–2760,y440–660; cargo/chain/pilot at x2680–2790,y300–340. The existing short separation is source evidence, not verified legibility. The owner's report shows the current visual distinction was insufficient.

First candidate should reuse the existing marker/activator references above, change their display labels, and supply arrival/current-state pages. Do not invent floating world-text rendering or treat optional paper signs as already read. A small stock-prop outline is allowed **only if the engineer audits actual model/transformed bounds first**: separate a Queen/deck pocket from the grain-crate pocket, with no actor/interactive ref relocation, no closed perimeter and a continuous192-unit approach to every existing action. No exact prop base/origin is asserted here without that audit. If an outline cannot preserve these clearances in the compressed existing footprint, omit it and explicitly leave physical silhouette clarity for the next independent native gate; do not squeeze collision into a route or sell flat ground as a modeled ship. This is a bounded layout clarification, not a new landscape/quest project.

### Meaningful candidate checks and native disposition

Require source/projection checks for unchanged exact accepted speech, existing four outcomes/refusal availability, current-role text and first-visit/revisit/dead-cast correctness. Verify normal/cancel/invalid/stale confirmation sequences BEFORE any caps/claim/stage44, once-only payment and the separate lie/reply commits. Verify arrival/goal notices cannot overlap ordinary dialogue or force stages. Readback must preserve old reference IDs/coordinates, actors, cargo facts and all unrelated road state; any approved new static geometry needs audited bounds/access checks and its own precise delta. Independently compile and package only a new candidate, not the live/accepted bundle.

The next ordinary-controller observation should establish that a fresh player can identify **Opal's goal, Hatcher/Queen versus grain barge, which action returns grain versus takes money, and whether a later statement to Opal is a lie**. The owner need not replay the current completed branch now. Until that actual observation, mark this issue **SCENE/CHOICE CLARITY HOLD**, even if mechanics and source tests pass. No additional canon decision or owner interrogation is required.

## Final owner requirement: human stakes before choosing

The owner further asked for clarity about who is helped/harmed: **“Doesnt mean anyone is good or bad, just that people will die with one decision and live in the other.”** Treat this as a request for visible human consequences, not hero/villain labels or permission to invent deterministic deaths. Preserve moral ambiguity while explaining the known stakes before the action commits.

| Existing decision / source hook | What must be clear BEFORE commitment | Truthful result shown afterward |
| --- | --- | --- |
| Card route at `TableTalk`/`DealCards`, `SayHatcherTable` | `The stake is the grain barge. Winning gives you a chance to bring Greenwater's winter food home. A lost hand is not a death sentence or an automatic deal.` Exact accepted card speech stays unchanged. | Actual win/loss only. A card win alone is not a delivered cargo claim: existing pilot/arrival acknowledgement still matters. |
| Paid deal at `BuyShare`/`ConfirmShare` | `You receive 200 caps. Hatcher keeps the grain; Greenwater does not get its winter food back through this deal. The lie to Opal is a separate choice.` | Actual caps received and grain retained, not “everybody starves” or an invented famine death count. The loss of access to winter food is the human stake, not a proven death event. |
| Chain/Chute at `AtChain`, existing `AskChain` and `pruitt_chain`; departure at `AtPilot` | `Free the grain barge and try to bring it home through the dangerous Chute. Cargo can be lost. Burning the occupied Queen is a different choice.` Existing warning must be read/acknowledged and action-specific confirmation must precede the actual cut/departure. | Actual cargo accounting only:12/12 whole,8/12 with pilot or6/12 alone as the existing confirmed route records. Do not invent a passenger drowning or call partial recovery a complete food supply. |
| Occupied-boat fire at `AtFire`/`AskFire` | `Thirty people are aboard the Queen, and Greenwater's grain is tied beside it. Fire endangers them and destroys the cargo. This cannot be undone.` Strengthen only technical warning emphasis if needed; exact accepted Rafferty speech stays unchanged. | Actual fire/cargo loss, and `People were endangered; this build has not established an exact death toll.` No “30 killed”, “all safe” or invented individual survivor. |
| Hatcher judgment at `JudgeAtTable`, existing Opal/custody/release choices | `Give him to Opal` means execution risk/intended hanging; `Pritchard, alive` means living custody; release means letting the actual living Hatcher go. Make the consequence explicit on a technical precommit confirmation rather than rewriting accepted speech. Only offer the existing actually viable living/present routes. | Show only acknowledged actual hanging/death, actual custody arrival or actual release. No killing-on-cancel, dead-sheriff delivery or guaranteed future friendliness beyond implemented facts. |

**Small exact insertion to the ArrivalBrief/Goal sequence:** add separate technical `TLM_MSG_GW_Stakes` after the concise role briefing, within the same current-player conversation claim, not as concurrent trigger UI:

Title `[Who is affected]`; text:

> Greenwater needs this grain for winter. Hatcher's payment helps you and leaves the grain with him. The Chute risks cargo loss. Burning the occupied Queen endangers the people aboard and the grain. Hatcher's fate is a separate decision if you win.

Button **“I understand the stakes”** acknowledges information only; it records no moral choice, role allegiance, actual death, evidence, reward or quest outcome. The local action confirmations remain necessary: a one-time overview is not consent for a later fire or execution. Cancellation/invalid response closes safely; no automatic default consequential action.

Engineering may fold this text into an existing technical orientation page instead of creating another message, provided the words remain readable and the same before-commit/current-state guarantees hold. Prefer a small number of concise pages to a barrage of notices. This packet authorizes no new outcome or claim of death observation. An aftermath must distinguish **known harm/risk**, **actual cargo/effects**, **actually acknowledged deaths** and **unaccounted people**.

Final bounded recommendation: implement the role/layout/goal plus human-stakes technical clarity and explicit payment/lie confirmations in a separate reviewed candidate. No hot edits, morality tags, new canon, forced owner recall or immediate branch replay. Mechanics/source acceptance alone cannot close the owner's comprehension finding.
