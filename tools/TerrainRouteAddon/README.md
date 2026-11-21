# Optional two-cell terrain route — source/local build slice

This is a SEPARATE development addon, not a replacement for the frozen f491 demo. Base source is f491eeb4e670d306530446b60f82785950dbb747; the separately accepted landmark source is192a7cccfb2b40e90a9ebc5d311dc93f6b11c822/artifact6EB3A6167DE06353E39660180DE8858DBBBCBDEB793D3C84770BC7739AE6A81C. No existing source/manifest/verifier/package/launcher is modified, repinned or adopted.

Two ground clipboard controls are labelled **[Development] Visit terrain preview** and **[Development] Return to Meridian preview**. Normal player activation opens Travel/Stay here confirmation. The only gameplay API effect this new script calls is MoveTo on the current player after renewed live/out-of-combat/local/generation checks. No quest/stage/item/health/actor/companion APIs, NPCs, navmesh, settlement, canon or audio are added. Existing engine systems may naturally react to travel; this is not a promise that all game state freezes.

## Exact boundaries and identities

- Outbound control at256/512/0 in the existing Meridian world, outside its reviewed spawn envelope; destination is the terrain's EXISTING PERSISTENT marker000806:TLMSpectacleTerrainPrototype.esp at3072/1024/592.
- The old Meridian TLM_WS_Arrival000804:TLMWorldSlice.esp is TEMPORARY. Its flags are not edited or relied on across worlds. A NEW addon-owned PERSISTENT return anchor000804:TLMOptionalTerrainRoute.esp copies its reviewed448/640/32,yawpi/4 pose and static base.
- Terrain return control at3184/1104/576 lies wholly inside a flat576 LAND quad, on dry ground. Its clipboard footprint is124.807852units from the accepted57-point trail, above112=96half-corridor+16margin. The intermediate3072/1152choice was discarded for2.25units of slope gap; earlier ignored artifacts remain preserved.
- Exactly4declared header-only overrides: WRLD000800 and persistentCELL000801 of TLMWorldSlice.esp and of TLMSpectacleTerrainPrototype.esp. Typed copies have ALL child groups/references/LAND/navmesh removed, then only the THREE new persistent refs are added (outbound control+own return anchor in Meridian, return control in terrain). No existing terrain, placed actor/ref, quest, door, room, landmark or NAVM record is copied into the addon. Parent plugin bytes stay unchanged, retaining both donor cells and all13landmarks.
- Direct binary masters are Fallout4.esm, TLMSpectacleTerrainPrototype.esp, TLMWorldSlice.esp. TheLastMeridian.esp is a validated TRANSITIVE dependency through TLMWorldSlice, not an unused forced direct master. Normal typed writer enumeration is retained. Raw checks derive FormIDs from that actual table: own index3, terrain1, Meridian2. Header comparisons explicitly normalize FormKey-bearing fields by master NAME rather than assume byte identity under arbitrary master-index changes.
- Own records800/801ACTI,802/803MESG,804return anchor,805outbound and806return control. No QUST/NPC_/ACHR/LAND/NAVM exists in this addon. Total12records includes TES4+four overrides+seven own records.

## Local build and preservation

The accepted Windows SafeBuild.cs is copied byte-exact and still binds its actual caller project, exact owned Fallout4.esm hash, locked nonreparse paths, new direct build child and exclusive new files. TerrainPrototype.csproj keeps that guard's expected project filename; its output assembly is TerrainRouteAddon. Additional exact story/world/terrain files are fixed-path, read-only locked and hash checked. No output adoption/cleanup is added. Global NuGet package cache supplies0.53.1; restore uses the empty local feed only, with no download/SDK move.

From repository root:

    dotnet restore tools/TerrainRouteAddon/TerrainPrototype.csproj --source tools/TerrainRouteAddon/empty-feed --ignore-failed-sources
    dotnet build tools/TerrainRouteAddon/TerrainPrototype.csproj --no-restore
    dotnet tools/TerrainRouteAddon/bin/Debug/net8.0/TerrainRouteAddon.dll "C:/Program Files (x86)/GOG Galaxy/Games/Fallout 4 GOTY/Data/Fallout4.esm" build/NEW-unique-directory

The output directory is relative to the COMPONENT, not repository root. Existing targets are refused. Licensed ESPs/metadata outputs and all logs stay ignored in this component's build folder. Only source and small numeric/hash receipts are tracked. Frozen input paths/hashes in Program.cs are deliberate scope bounds, not general installation configuration.

One new runtime source is scripts/TLMDev/OptionalTerrainTravel.psc. Event OnLoad only invalidates a local attempt generation; it does not auto-travel. Busy is claimed before yielding context; old generations cannot release a newer lock. Destination3D is deliberately not required because it is a distant persistent marker. SDK ObjectReference.psc confirms GetWorldSpace/OnActivate/OnLoad signatures. **This script is not actually Papyrus compiled or packaged as PEX.** Current canonical34runtime sources and their build tools remain untouched; future inclusion is a separately reviewed35th runtime file under Scripts/TLMDev, not a substitution in the current34.

## Checks and evidence

Actual cached .NET build:0warnings/0errors. Actual ignored build/connection-003/TLMOptionalTerrainRoute.esp emitted; verify.py independently validates its12-record whitelist, exact flags/poses/persistent parents, two confirmations, VMAD destination/world/boolean links, actorless scope and both world/header payloads under name-based remap. It also pins all three plugin inputs and the accepted trail metadata, proves dry flat support/clearance, and does not infer native merge or collision.

Ten focused methods passed0.394s (build/evidence/tests-final.txt): normal raw checks; actual header/name/persistence/VMAD destination/pose damage; preserved source/accepted path guard; existing-output and wrong-owned-master no-output refusal; actual PSC confirm both directions, cancel/invalid/NPC/dead/combat/missing/far/wrong-world, post-confirm stale/death/combat/displacement/target loss/delivered OnLoad, recovery, reentry/old-generation lock, and unconfirmed movement. Cancel-guard mutant demonstrably travels against a declined choice. These use the existing PSC interpreter with explicitly synthetic world-identity/native responses, not the game. Delivered assignment-only OnLoad is executed before resume; this does not prove all real save/load paths deliver that event. No shared interpreter, old test or workflow is changed. Early author build/test errors and superseded ignored artifacts are retained, not counted as successful evidence.

Commands:

    python tools/TerrainRouteAddon/verify.py
    python tools/TerrainRouteAddon/verify.py --source
    python -m unittest discover -s tools/TerrainRouteAddon -p test_connection.py -v

The source receipt anchors component files and all changes must remain under this new component relative to exact f491. Old current-candidate verifiers intentionally remain frozen; they are never weakened or run against an already-invalid composition to claim a pass. No remote push/CI/aggregate is performed for this separate slice.

## Before any use

Root/Sam must independently review source and the local artifact; root owns actual Papyrus compilation and a separate dependency-pinned package/profile/launcher. The current launcher accepts exactly two plugins/34runtime files and MUST NOT be edited to slip in these extras. A future opt-in profile would need the existing two game plugins+terrain plugin+addon and the extra TLMDev runtime, with exact byte checks and normal ownership/cleanup. No installation or launch is authorized by this receipt.

Native gates remain: actual master loading and WRLD/CELL override-child merging; persistent cross-world MoveTo/load/settling/heading; control visibility/activation/cancellation; return accessibility, terrain seam/water/collision/Havok/LOD and absence of unintended engine reactions; controller/save-load/normal closure. Numeric model bounds are not native walkability. No background automation, NPC navigation or ready-demo claim is made.

Source-file receipt pins normalize UTF-8 BOM/CRLF/LF consistently with the accepted source policy; binary dependency/plugin hashes remain exact bytes. A fresh Windows worktree must not fail merely because Git materializes normal CRLF.


## Independent F1 repair

Historical3e89c469source was held by Sam's signed review0CFCEBDC7A919D70F94DFFF498512A71D93452F9E19E85FFC99800D14D1F0D96. Its raw artifact/preservation checks passed, but three additional actual-PSC callbacks at the renewed IsInDialogueWithPlayer read allowed travel after the player moved far, changed source world or the destination became disabled. Original failed probe/results remain preserved; earlier eleven nominal passes do not clear those counterexamples.

Current Context now finishes scene/dialogue observations first, then performs one finite final control/destination/world/locality/participant observation and retains captured current-player/generation checks last. No alternating loop, new state, geometry/UI text or outcome API is added. Three asserted-fired late-native regressions require no MoveTo/no success notice and ordinary retry after restoring the prerequisite. An actual historical3e89cscript mutant reproduces the forbidden movement. Existing confirm/cancel, readiness, generation/lock and raw artifact cases remain current. Native calls still yield; no atomic-world guarantee is made. C#builder and serialized addon bytes stay unchanged; only separate current script/test/source receipts change. Root retains actual Papyrus compile/integration/native gates.
