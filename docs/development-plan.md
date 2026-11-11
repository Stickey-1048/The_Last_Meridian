# Engineering Roadmap — Fallout 4
**Engine/tools:** Fallout 4 Creation Kit for quests/locations/dialogue; Papyrus for behavior. Tool versions and game build must be checked before code generation. AI coding assistants create files and designs, not a compiled functioning mod automatically.

## Vertical slice v0.1
Objective: 30–60 minutes of playable **Act I: Six Rounds to Mercy**:
1. Small Appalachian rail wreck cell and a road to Mercy Crossing.
2. Sheriff office, trading post, gunsmith workstation and five named NPCs.
3. Quest trigger at wreck; deliver sealed dispatch; resolve caravan encounter; dialogue and objective markers.
4. One persistent binary choice and one faction-reputation increment.
5. Basic local save/load, completion and fallback testing.

## Implementation passes
**Preproduction:** freeze canonical records; Fallout lore audit; install Creation Kit; choose DLC and dependency requirements; define plugin prefix TLM_ and form ID policy.
**Prototype:** worldspace/interior blockout; NPC records/AI packages; quest aliases and stages; Papyrus fragment hooks; dialogue topics and conditions; gameplay tests.
**Act I:** Greenwater/Red Hollow/Iron Junction; faction consequences; gunplay, transport and settlement scripting.
**Act II:** underground interiors, Oak Ridge, Shrouded Divide, Hollowborn NPCs and optional train.
**Act III:** branching coalition quest stages, shared Meridian Prime, endings.
**Polish:** save compatibility, navmesh, performance, voiced dialogue, packaging, attribution and permissions.

## Example non-executable quest stage sketch
TLM_MQ01:
- 0 Unstarted
- 10 Awaken at wreck / dispatch acquired
- 20 Locate Mercy Crossing
- 30 Speak with Elias Rook
- 40 Caravan encounter resolved
- 100 Completed
- 900 Recovery stage (missing alias/objective fallback)

This is a DESIGN stage table, not tested Papyrus code. Avoid hardcoding scripts until quest aliases and conditions are built in CK.

## Testing checklist
New game, reload from each stage, skip optional NPC, kill/disable nonessential NPC, reject dialogue, reach town before collecting dispatch, walk away mid-encounter, retest quest objectives and map markers. Avoid compulsory quest NPC deaths that soft-lock the campaign.
