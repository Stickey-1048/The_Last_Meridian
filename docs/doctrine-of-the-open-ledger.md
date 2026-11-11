# The Doctrine of the Open Ledger
Status: **Core creative direction approved**, November 11, 2026. Specific historical NPC names and dates are provisional until a quest scripting review.

## Governing theme
The Deep's central struggle concerns competent leadership, honest evidence, individual responsibility, reciprocal cooperation, and institutional accountability versus an administration that claims equality while protecting an increasingly privileged political class. Ayn Rand's emphasis on reason, productive work, earned achievement and self-direction is a **creative influence**, not a requirement that every character repeat ideological slogans. Present human motivations, conflicting evidence and costs rather than preach. The player must meet the same accountability standard as their opponents.

The truth can be painful. Concealing real crop failures, electrical constraints, equipment defects or deaths eventually produces worse outcomes. However, survival requires cooperation, sound engineering, transparent triage and care for people unable to provide for themselves; the story does not equate hardship with virtue or rank with competence.

## Why the player's family was exiled
During the **Exile of the East Galleries** (provisionally ca. 2262, about two generations before the surface-born player), reformers challenged politically motivated rationing and falsified production figures. Their **Open Ledger Charter** demanded:
1. Publish generation, stored-energy, crop yields, food allocations, medical shortages and mortality figures.
2. Record who authorized each safety-critical decision and permit independent technical review.
3. Permit neighborhood workshops, trade and individual enterprise within defensible safety and common-system constraints.
4. Keep essential food, medical triage and housing free from partisan retaliation.
5. Establish due process, freedom of movement and the ability to challenge unjust orders.
6. Couple personal responsibility with voluntary aid and negotiated obligations among districts.

The ruling class claimed these principles were attacks on equality. Some opponents sincerely feared fragmentation and breakdown of the common infrastructure; others saw a chance to preserve privileges. The purge should emerge from intersecting institutional failures, not a single evil mastermind.

## The tragedy: One Degree Off
**Tomas Arden** — East Galleries maintenance engineer, talented and proud, exposed manipulated electrical reserve and ration reports. Ancestor of the player (exact family relationship to be set).
**Leora Arden** — physician and Open Ledger organizer; defended accurate clinical and nutrition records; capable of errors, not a flawless icon.
**Councilor Irena Sable** — once competent resource administrator, gradually allowed jealousy, personal resentment and desire to preserve status to influence public decisions after Tomas chose a relationship with Leora.
**Daniel Senn** — another administrator who cared for Irena, challenged her conduct, and was not entitled to her affection.
**Director Marius Haldane** — superior who ratified expulsions, suppressed evidence, and erased civil records to consolidate authority.

During a broader water/power crisis, Irena supported punitive load transfers away from East Galleries. These compromised ventilation and pumps, causing deaths amid emergency actions, technical constraints and imperfect decisions by multiple sides. Authorities called it sabotage, expelled reformers' families and altered the historical record. Personal correspondence and surviving electrical/control records eventually expose the abuse. Jealousy is a human motive, never a justification: **the fault is choosing to weaponize public office and then hide the consequences.**

Theme metaphor: a slight initial misalignment of a train, rocket, bullet or technical decision can compound into catastrophe if no one tests assumptions or corrects course.

## Player discovery, without chosen-one genetics
The player is a surface-born descendant of expelled East Galleries families with a legitimate childhood and incomplete family history. Subsequent selective memory tampering relates only to their covert Fifth Rider mission, not their whole life. Documentation, family aliases, witnesses and an ancestor's maintenance records make the player a meaningful investigator, **not a hereditary ruler**. Authority in The Deep must be earned.

## Three-act integration
**Act I – Symptoms:** flawed local records, coerced resource arrangements, early rumors of Open Ledger and lost family marks. Final reveal from Mara Vale: the player's family originated below.
**Act II – Evidence:** closed East Galleries, contradictory power and census logs, residents' testimony, administrative letters and external Oak Ridge records. The player learns why The Deep expelled and erased their ancestors; competing factions dispute responsibility.
**Act III – Judgment:** determine The Deep's governmental future: independent and accountable, a voluntary treaty partner, formally integrated, dominated, sealed, fractured, or Deep-led ascendant power. Test whether the player's chosen system tolerates dissent, correction and consequences.

### Proposed quests
- **The Ledger Doesn't Lie:** compare switchgear logs, crop reports and ration registers.
- **The East Galleries:** explore sealed residences, records and survivor accounts.
- **A Degree Off:** reconstruct a catastrophic load-transfer incident from physical evidence.
- **The Letters Nobody Read:** uncover the human motivations and limits of witnesses.
- **The Cost of Truth:** release evidence while managing unrest and preventing indiscriminate retaliation.
- **The Open Charter:** negotiate durable checks on governing, auditing, trade and essential services.

## Implementation hooks — design, not tested Papyrus
Quest flags: `TLM_OpenLedgerDiscovered`, `TLM_EastGalleriesProof`, `TLM_AncestryRevealed`, `TLM_ArchivePublished`, `TLM_DeepStatus`. Metrics (separate globals/quest variables): `TLM_Truth`, `TLM_Competence`, `TLM_Accountability`, `TLM_MutualTrust`. Track scarcity and supply physically, not as moral scores. Do not create Papyrus code or presume record FormIDs until Creation Kit quest architecture is specified.

## Fallout lore guardrails
This is **original fictional** postwar history. The Deep is neither an existing Vault-Tec vault nor a rebranded official Fallout 76 location. All Oak Ridge experimental details must be labeled invented; FEV/West Tek references cannot imply this program created official super mutants. Consult `docs/fallout-lore-audit.md` and `docs/external-fallout-encounters.md` before adding canon crossovers.

## Current approval distinction
The owner approved the **philosophical spine and premise of an ideologically motivated exile**. Names, dates, causation details and evidence remain **provisional**, to be reviewed as part of detailed quests.
