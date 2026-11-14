# Act I research and editorial review

Status: first development pass, 2026-11-14. Proposed narrative work, not a canon amendment or game implementation.

## Findings from the existing writing

The opening's strongest material is already specific: the dead inspector's signature, worn train components, Pike's independent parts tally, the innocent freight clerk and Nell's refusal to talk after betrayal. Preserve these. They make the player interpret facts and live with a choice.

The rough cut deliberately compresses people into functional introductions. That makes it playable for testing, but the same compression would make a finished town sound like six service counters. Most residents need something underway before the player approaches, a limited opinion of another resident and a later behavior changed by events.

This review covers the dialogue in TLM_ACT1_first_section.md and the relevant MQ01/SQ01 designs. The generated act1_texts.json and casting_cards.json from the earlier conversation are not present in the branch inventory reviewed. Their complete wording has not been assessed. Do not describe this as a review of all 69 generated text entries.

### Targeted editorial changes

| Existing wording or pattern | Assessment | Treatment in the dialogue draft |
|---|---|---|
| Nell: "You watched. You kept walking." | Specific, plain and deserved only when the player actually encountered the hold-up | Retain; never use for Missed |
| Pike: "Pike. I fix what shoots." | Efficient introduction, but announces a service instead of showing her at work | Open with handling the item and observing wear |
| Vane: "Paper like this makes trouble for everyone." | Suggests menace early enough to weaken Chapter 4's evidentiary turn | Offer an ordinary purchase and terms; keep motive equivocal |
| Keene: "If you're bleeding, sit. If you're not, don't touch anything." | Readable, but close to a stock brusque-doctor introduction | Give her a specific clinical task and a boundary linked to the patient |
| Haskell: freight and Line 14 greeting only | Gives location information but little sense of the person whose reputation can be destroyed | Let him identify a count discrepancy while doing his work |
| Pritchard: witness's account is "different from the one you'll give me" | Presumes an answer before the player chooses it | State the witness's allegation, then let admission, denial or silence remain distinct |
| "The count's the count" | Fits brevity but can overstate what a supplier's book proves | Clarify that Pike knows her own sales, not every possible source |
| Repeated introductions by surname and occupation | Useful rough-cut compression; flattens social variety if shipped unchanged | Vary entrances: a request, a task, a question or recognition of an object |
| End-of-chapter list of three problems | Necessary navigation information | Keep clear; put emotional complexity around it rather than obscuring the destinations |

Sophisticated dialogue does not require every line to be longer. Some of the revision is subtraction: remove the sentence that announces what a gesture, receipt or empty chair already tells us.

## Research and original applications

### Halo and discovery through smaller stories

Halo's official ODST retrospective describes a scattered squad regrouping through an occupied city before discovering a larger objective. The useful design principle is a practical local task widening the player's understanding. Our proposed adaptation follows broken transport and the people using it; it does not reproduce the squad, city, alien discovery or sequence of missions. This application is an editorial inference. [Halo official ODST retrospective](https://www.halowaypoint.com/news/feet-first-into-fall).

Sadie's Story is an optional civilian narrative discovered through collectible audio logs in ODST. The transferable technique is that an apparently secondary person's actions change the meaning of places the player traverses. Our original proposal uses a porter's storage tally, a clinic supply request and freight counterfoils. These fragments remain optional and do not require collecting every item. We are not adapting Sadie's plot, characters, dialogue or particular incidents. [Halopedia overview of Sadie's Story](https://www.halopedia.org/Sadie%27s_Story).

The Rookie is the closer reference for sparse player speech; Master Chief should not be described as literally silent. The design aim here is room for player interpretation, not copying either protagonist's identity.

### Halo and cooperation after harm

Halo's official Anvil material describes a joint human and Sangheili initiative involving younger personnel and war veterans, with political efforts that could undermine their alliance. My narrative inference is that reconciliation becomes more credible when people must sustain shared work under persistent distrust. Our yard supervisor remains accountable while working beside people who no longer accept a sole signature. No Halo institution, species conflict or espionage plot is transplanted. [Halo official Anvil background](https://www.halowaypoint.com/news/canon-fodder-all-about-anvil).

This also sets a limit on the moral arc: a confession can begin a change, but victims need not forgive and a valuable skill cannot erase a harmful act. The supervisor must accept an actual reduction in authority. Vane, if retained, must release a profitable obstruction and accept scrutiny.

### Appalachian work and social spaces

The National Park Service's Cable Mill inventory describes milling as a community focal point, serving food preparation and other practical needs. It also explains that much of the present exhibit's surrounding building arrangement was assembled or moved later. We should draw on interdependent work, not mistake the visitor site's current arrangement for a wholly intact historical village. [NPS Cable Mill cultural landscape inventory](https://irma.nps.gov/DataStore/Reference/Profile/2196011).

The original story application is a recurring place where food, repairs, receipts and ordinary encounters overlap. A shortage should change what people do there, who waits and what work is postponed. This supports Tennessee specificity more effectively than attaching a mountain accent to generic frontier dialogue.

A mill or pump can also anchor an argument among competent people with unequal strength, money and authority. The machinery is a shared dependency; ownership of it need not confer unlimited moral authority over everyone who uses it.

### Boundaries for further research

Research next into regional oral histories, rail labor, river transport and mining communities to improve texture and competing perspectives. Check each factual detail before putting it into a scene. Historical vocabulary and practices need adaptation to the fictional date; real people and community tragedies should not become disguised villains or interchangeable dystopian decoration.

Do not claim that a fictional maintenance practice, famine or political organization is documented Appalachian history. Keep Fallout-lore research separate from these original social and narrative proposals.

## Decisions recorded by this draft

All entries are PROPOSED rather than approved canon.

| Decision | Reason | Where developed |
|---|---|---|
| Different local failures become targets for selective paid obstruction | Connects the act while preserving independent causes and human agency | Storyboard, Chapter 2 |
| An older supervisor owns a harmful repair deferral without automatically solving the signature forgery | Gives a gradual moral arc and keeps evidence claims precise | Storyboard and dialogue, Iron Junction |
| Introduce unnamed working roles before assigning new proper names | Allows personality development without multiplying naming conflicts | Character profiles |
| Keep Vane's Chapter 1 offer ordinary enough to permit several interpretations | Protects the later reveal | Chapter 1 dialogue |
| Give each principal faction one useful act and one contestable term | Makes politics a lived choice rather than four speeches | Chapter 3 |
| Make a public correction and practical restitution distinct from forgiveness | Gives Haskell agency after scapegoating | Return scenes |
| Use written and physical fragments for civilian stories | Suits the current asset scope without requiring an audio importer | Objects and callbacks |
| Keep Chapter 5 revelation dialogue open | Respects unresolved player history and Mara choices | Chapter 5 boundary |
| Use a separate feature branch for these documents | Keeps the engine branch available for ongoing work | feat/tlm-act1-story-depth |

## Handoff for implementation review

This pass adds only three narrative documents. It does not replace existing canonical or quest design files, edit scripts, change dialogue records, add globals, adjust timers, alter rewards or claim a game test.

Chapter 1 replacement candidates need a separate accepted-content pass through the paired text in SpecAct1.cs and Act1Walk.psc, preserving their synchronization and existing tests. Do not paste them into only one copy.

Chapter 2 onward needs explicit quest-state design and failure routes after narrative acceptance. Narrative suggestions such as a repaired pump, a public correction, duplicate records and independent review are not existing game features.

Review these cases before any implementation:

- Missed versus Evaded: a player who did not see the hold-up receives no accusation of watching it.
- Saved with a later death: dialogue reads actual survivors, not only the original rescue.
- Exploited: Nell's refusal remains; Keene does not grant forgiveness for her.
- Silent debrief: no confession, loyalty or lie is inferred.
- Thin evidence: no individual culprit is asserted; no Chapter 1 Vane confession.
- Signed Clean skipped, sold or burned: the main story remains available.
- Haskell absent or dead: no live-person callback or false suggestion he was guilty.
- Chapter 2 visited in any order: leads do not presume other visits.
- No Vane cooperation: Blackstone still has an independent main-route lead.
- Chapter 3: no early revelation of concealed facilities, no accidental fifth faction and no compulsory allegiance.
- Chapter 5: no predetermined player family details or involuntary emotional identification.

Editorial review completed for continuity boundaries, differentiated voices, action-based player choices, evidentiary restraint, consequence costs and source attribution. A performed read-through and player response to the revised conversations remain necessary. No engine checks are claimed for a documentation-only proposal.
