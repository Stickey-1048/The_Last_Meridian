# NPC Naming Registry and Change Log
Status: v1-draft naming pass | Date: 2026-11-11
Purpose: distinct names in dialogue, quest logs, voice scripts and filenames; no accidental implied family connection.

## Canonical renamed characters
| Prior name | Current name | Role | Reason |
|---|---|---|---|
| Elias Rook | **Owen Pritchard** | Mercy Crossing sheriff / Old Warden | Distinguish from Gideon Rusk |
| Clara Voss | **Clara Whitcomb** | Free Meridian Compact speaker | Keep Cassian Voss unique |
| Gideon Ash | **Malcolm Ash** | Non-feral ghoul railway veteran, Ashen Brotherhood leader | Gideon Rusk retains the Gideon name |
| Dorran Vale | **Dorran Coyle** | Stonebound engineer/claimant | Mara Vale remains the only principal Vale |
| Dr. Silas Wren | **Dr. Julian Wren** | Oak Ridge Human Advancement researcher | Distinguish merchant Silas Vane |
| Miriam Bell | **Miriam Keene** | Mercy Crossing physician | Distinguish Dr Naomi Bell and judge Esther |
| Judge Esther Bell | **Judge Esther Quill** | Warden magistrate | Avoid unrelated Bells |
| Miriam Voss | **Miriam Kade** | Ashen Brotherhood Ember Hand leader | Distinguish Cassian Voss |
| Deputy Jonah Pike | **Deputy Jonah Talbot** | Young Warden recruitable companion | Avoid implied kinship with Ada Pike |

## Reserved canonical names / roles
- **Gideon Rusk**: Iron Dominion marshal; Gideon is unique among prominent NPCs.
- **Owen Pritchard**: Sheriff, mentor during Act I.
- **Mara Vale**: ex-Meridian Rider and principal narrative companion.
- **Cassian Voss**: silver-gunned Rider antagonist; no assumed relationship to any other cast member.
- **Edda Flint**: independent Rider.
- **Lucien Grey**: Ascendant-linked Rider.
- **Adrian Kess**: Ascendant Directorate leader.
- **Anton Vey**: People's Commonwealth leader.
- **Helena Sorrell**: The Deep's Stewards leader.
- **Imani Cross**: Open Door advocate.
- **Clara Whitcomb**: Compact speaker.
- **Evelyn Harrow**: Oak Ridge Assembly leader.
- **Malcolm Ash**: ghoul railway leader.
- **Dorran Coyle**: Stonebound claimant.

## Family-relationship policy
No shared surname implies kinship unless a relationship entry explicitly records it. When names are proposed, check exact duplicate names, same given names, near-homophones, shared surnames, and similar voice/dialogue tags. Reserve family connections for plot-relevant choices only. Do not silently revive names from earlier chat drafts.

## Voice and quest file labels
Prefer stable IDs independent of visible name spelling, e.g. TLM_NPC_SHERIFF_MERCY, TLM_NPC_GHOUL_RAIL, TLM_NPC_COMPACT_SPEAKER. Dialogue and script should reference stable records so later naming revisions do not break quests.

## Unreviewed minor NPCs
Some early outline-only names (e.g., other Stonebound minor officers, doctors and temporary traders) are not in the canonical registry; audit those at the quest-script phase.

## Act I expansion approved 16 November 2026

Approved under the owner's delegated creative review; see [the decision amendment](design/ACT1_CREATIVE_DECISIONS_2026-11-16.md). This registers narrative identities and display names. It does not create engine records or change the intake requirement that unbuilt characters use `record: null` and the appropriate intake status.

| Current name | Spoken name / aliases | Role | Stable intake ID |
|---|---|---|---|
| Augusta Lockridge | Gussie | Iron Junction yardmaster; forged Ostrander inspections | `lockridge` |
| Wilhelmina Tupper | Billie | Night Mail driver | `tarrow` |
| Reuben Ostrander | R. Ostrander; assumed Ezekiel "Preacher" Dole | Inspector reported dead; later Black Rail leader; one person | `dole` |
| Opal Starnes | Opal | Greenwater ration warden | `starnes` |
| Lyle Hatcher | Commodore Hatcher | Queen of Tellico owner | `hatcher` |
| Mose Rafferty | Catfish | River pilot; Opal's grandson | `pruitt` |
| Hobart Blevins | Captain Blevins | Red Hollow mine captain | `greer` |
| Dinah Roark | Dinah | Red Hollow hoist-woman; Pell's wife | `roark` |
| Juno Three-Fords | Juno | Courier | `threefords` |
| Temperance Beckett | Temperance | Vane's bookkeeper | `vickers` |
| Tolly Granger | Tolly | Mercy Crossing printer | `granger` |

Retired proposal spellings: Wilhelmina Tarrow → Wilhelmina Tupper (Harrow collision); Hobart Greer → Hobart Blevins (Grey collision); Mose Pruitt → Mose Rafferty (Pritchard collision); Temperance Vickers → Temperance Beckett (Vane/Vale/Vey/Veyr/Voss cluster). These old display spellings remain only as proposal/history identifiers. Machine IDs stay unchanged. Use "Captain Blevins" and "Delegate Belden" on first return in crowded scenes to distinguish their similar rhythm.

Gussie/Billie/Catfish/Preacher are aliases, not additional NPCs. Legal Reuben Ostrander and assumed Ezekiel Dole share the single `dole` identity. Use Preacher Dole/Ezekiel Dole as the public display identity until the evidence-led reveal; the legal identity in this registry must not leak through an early nameplate or speaker label. Only the grandmother/grandson relationship between Opal and Mose is established; no maternal or paternal branch is specified. Pell is a reference-only given name for Dinah's husband, with outcome-dependent fate; no surname or new actor record is approved here. Juno Three-Fords and Finn Nine-Trails have no implied family relationship.
