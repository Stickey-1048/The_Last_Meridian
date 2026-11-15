# WORLD-SLICE-001: first optional exterior site

Development prototype, 2026-11-15. Owner explicitly requested a walkable exterior with cabin, fence, bed and couch. Iris supplies the compact site brief; Dana implements; separate exact-head review and native acceptance remain required. Input is `ed738b0dc135bd2974e81088b85d6740c21153e6`.

## What this candidate actually builds

An optional **separate `TLMWorldSlice.esp`**, dependent only on Fallout4.esm: a NEW worldspace, persistent cell and exterior cell at grid0,0; an original generated33×33flat LAND heightmap with dirt/gravel texture; a768×512modular wood cabin with floor/roof/walls and a256-unit open front bay; native Furniture bed/couch; a low fenced yard with256-unit entrance; a perimeter rail; separated wreck/road/Mercy sites and continuously edged main/bypass routes. It is not a finished town or terrain world.

It does not edit QASmoke, existing preview/world/quest references, scripts, player presets or a save. This first exterior **shell** has no quest/actor/ambush binding or navmesh. The playable first-section interactions remain in the existing preview until a separately reviewed relocation/alias plan. Native bed sleep/couch sitting is an acceptance requirement, not inferred from a static lookalike: both chosen bases are actual Furniture records, but runtime usability has not yet been observed.

## Build and explicit entry

From the repository root, using the owner's master and a workspace output:

```powershell
dotnet run --project tools/WorldSliceBuilder -- "F:\SteamLibrary\steamapps\common\Fallout 4\Data\Fallout4.esm" build/world-slice
```

The builder writes only that output, never an installation. Its readback checks verify new ownership/no vanilla override, exterior grid, LAND dimensions and reference count. It also samples every route segment against transformed placed-object bounds, requiring192units of clear corridor at player height. Junction markers inside another route's corridor are omitted. This is record/geometry evidence, not engine collision certification.

Explicit development entry for later isolated native QA: `coc TLM_WS_Clearing`. Worldspace: `TLM_WS_Meridian`. Arrival marker: `TLM_WS_Arrival`, new local FormID000804 in TLMWorldSlice.esp; actual load-order prefix must be resolved rather than assumed. Arrival is448/640/32, heading45degrees toward the route. COC exterior entry itself remains a native test. If it does not resolve correctly, stop and investigate; an isolated QA-only MoveTo of that explicit marker is an alternative test entry, not an established player startup route.

## Layout and asset facts

- Wreck site around700/900: rubble/wood debris sit outside the walking corridor. No train geometry, marshal, dispatch or quest pickup is claimed in this shell.
- Hold-up site around1900/1700: timber markers delimit the future encounter area. The bypass branches before it and rejoins toward Mercy; no trigger/actors are installed yet, so avoiding an actual ambush remains a later integration test.
- Mercy yard:256-unit gap centered3048/2432. The main path squares up at3048/2200 before the entrance, avoiding fence collision bounds. Cabin spans approximately2664–3432X and2672–3184Y; front center tile is left unwalled. Floor top16, roof underside about214, front opening about256wide×198high. Native walking/roof/steps remain unverified.
- Bed: `WorkshopNpcBedMilitaryCottLay01`, a native IsSleepFurniture base, at2800/3040/16. Couch: `NpcCouchSet02Weathered1x2Straight01Sit01`, native Furniture, at3280/3040/9; its7-unit model minimum puts it on the16-unit floor. The central aisle and front approach are unobstructed by these object bounds; animation/exit space requires actual use.
- Floors `workshop_ShackMidFloor01B`; roof `ShackMidRoof01`; thin wall `ShackWallFlat02`; fence `PicketFenceB_PW_Fence01`. Exact EditorIDs are required; missing assets fail rather than substitute caps. Only references are written, never bundled vanilla meshes/textures.

The generated LAND is flat at0 and uses33×33normals/heights with four dirt/gravel quadrants. There is no copied landscape record, LOD generation, navigation mesh, water, terrain seam beyond this single cell, cluttered world or distant environment. A96-unit perimeter rail discourages accidental walking off this cell; it is not an invisible wall or a guarantee against jumping over it.

## Next milestone and native acceptance

First pass must be reviewed at its exact commit, then root may install the optional plugin into a disposable isolated profile. Preserve owner preview/controller settings. Root keyboard/mouse QA may use only the disposable profile's gamepad-enable setting; this builder changes no profile settings.

Prove exterior entry and supported terrain under the player; walk spawn→wreck→road→yard/cabin without teleporting; walk the bypass; inspect cabin doorway/floor lips/roof and fence opening; activate/sleep in bed, sit on couch and exit. Record screenshots, exact artifact hash and observed failures. Falling, blocked furniture or a bad world/cell group is a failed native gate even if serialization passes. Do not call the world finished or the quest transplanted from source/readback results.

Rollback: disable/remove the optional plugin from the isolated profile; never save an ordinary character with this development prototype. Existing preview source/ESP remains available unchanged. After this physical shell passes, separately scope quest/actor/trigger placement and native navigation; do not fake chapter completion in the empty world.
