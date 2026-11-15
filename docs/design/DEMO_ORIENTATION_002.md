# DEMO-ORIENT-002: first spatial footprint

Implementation candidate, 2026-11-15. Owner feedback and authority: [game issue 7](https://github.com/Stickey-1048/The_Last_Meridian/issues/7). Base behavior is Sam's `40548b523999c5f94536673b38332bef9777d8e3`, separately reviewed by Iris. Dana owns this additive engineering candidate; Iris supplied the spatial plan and reviews it separately. No Nora session acceptance is claimed.

The owner subsequently authorized a tangible first pass using existing game assets: distinguish the wreck, optional hold-up and town inside the QA room. Custom lettering is deferred for this increment; this is not a finished worldspace, town or fully accepted orientation system. Existing placements, quest stages and outcomes stay unchanged.

## Seven new references

Coordinates are ahead/right/up from QASmoke arrival. Model X maps to right and model Y to ahead under the existing builder's placement/rotation convention. Exact Static EditorIDs were resolved from the owner's master; no vanilla mesh/material/texture is copied into the repository or package. Formkeys append seven new IDs; old IDs remain unchanged.

| Reference suffix | Static base | Ahead | Right | Up | Measured model bounds (X,Y,Z) |
| --- | --- | ---: | ---: | ---: | --- |
| DecorWreckOuter | StoneWallOldRubble | 500 | -750 | 0 | (-27,-37,-1) to (27,37,24) |
| DecorWreckRear | ExtRubble_BricksLrg_Clump01 | 575 | -625 | 0 | (-94,-104,0) to (96,94,38) |
| DecorRoadLeft | FenceWIBollardPost01 | 410 | -390 | 56 | (-4,-4,-56) to (4,4,48) |
| DecorRoadRight | FenceWIBollardPost01 | 410 | -30 | 56 | same |
| DecorMercyLeft | FenceWoodPost01 | 300 | 20 | 64 | (-8,-6,-64) to (8,6,176) |
| DecorMercyRight | FenceWoodPost01 | 300 | 280 | 64 | same |
| DecorMercyCounter | ModernDomesticTableLrg01 | 828 | 210 | 0 | (-70,-41,0) to (70,41,56) |

The wreck gets a low rear/left rubble edge, the road narrow 104-unit metal markers, and Mercy tall 240-unit timber posts plus a low rear table. Rubble is prototype set dressing, not train geometry. Posts are raised by the negative model minimum so their bottoms meet the floor. No enclosing wall, overhead beam, terrain/navmesh edit or blocking guide menu is introduced.

Earlier schematic debris sites overlapped the room's cooking spit/building bounds; they were rejected. Iris accepted the revised rear/left sites. The table moved farther behind the town actors to improve pickup/dialogue approach clearance. Only new decor moved. A read-only survey of 385 bounded vanilla object references found no transformed 3D object-AABB overlaps at the final seven sites. This is coarse record evidence, not mesh collision, floor/sightline or navigation certification. The room's original displays remain intact.

## Wiring and checks

`SpecOrientation.cs` declares only placed Static references and development-quest aliases. `SpecAct1.cs` appends them after existing placements/aliases and adds them only to Everything/EverythingNames. Existing SwitchOn enables them for the demo/audit; they are initially disabled otherwise. They enter neither People nor cast lists and have no dialogue, trigger box or activation script. No runtime Papyrus source changes are made by this increment.

The stand-in master has explicitly fake Static model paths for lookup/enable tests; it is not evidence of rendered geometry. A regression verifies all seven refs start disabled, enable in play setup, and do not set ambush/outcome stages. Existing other-scenario isolation tests continue to cover the appended disabled references. Real-master candidate and baseline builds both passed builder readback/self-check. Comparing their JSON reports proved all 34 old placed references identical in every reported field, existing aliases unchanged, and existing simple records/messages/NPCs/production quests identical. All seven new references resolved to the intended master bases; no fallback cap or silent omission is accepted as the candidate.

## Remaining acceptance and rollback

Independent exact-head review, remote CI, root-managed Windows compilation/install and physical acceptance must be recorded separately. No install or game launch was performed by this implementation task. From arrival and after turning around, the owner/Sam must assess whether the three areas are distinguishable, the optional encounter has a clear bypass, pickups/dialogue/fighting remain unobstructed and all decoration is on usable floor. Capture arrival and station screenshots. Setup/simulation cannot certify those observations.

Persistent readable station names, repeatable place/next-action guidance and a continuous route convention remain the next orientation increment. Changing an object's Name or borrowing a model does not render arbitrary 3D lettering. Existing incoming PNG signs are not an installed NIF/material/texture pipeline. Do not claim this first footprint meets the original full named-sign/guide acceptance.

Rollback the narrow footprint changes after separately authorized integration to remove the seven added references/aliases and restore the previous build; keep the behavior fix and original quest placements. Use a fresh TLM-Dev test session for acceptance rather than assuming old saves remove previously enabled references.
