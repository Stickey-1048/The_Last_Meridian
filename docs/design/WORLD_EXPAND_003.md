# WORLD-EXPAND003 — useful exterior footprint, opt-in source candidate

Input: reviewed4c9903ae5fef550e005793835ae36f932a76c1e8. This layout composes the unchanged first-section quest and guarded entry with a recognizable rail wreck, exposed caravan road and three-building Mercy site. It remains one4096-square prototype cell, without NPC navigation certification or new services/quests.

## Build and fallback

```powershell
dotnet run --project tools/WorldSliceBuilder -- "C:\Program Files (x86)\GOG Galaxy\Games\Fallout 4 GOTY\Data\Fallout4.esm" build/expanded-new --story-source "C:\Modlists\TMR\mods\TheLastMeridian-Dev\TheLastMeridian.esp" --expand
```

Only the trailing explicit --expand selects this variant. Default mode reproduces the reviewed6B617B6F1566F34499545B940690AAB3CBF9DBC62F8051BB8E29C48112E8BB62story artifact. Existing shell/launcher source and its default pin are unchanged. Expanded binary and19unchanged runtime pins are recorded separately in tools/WorldSliceBuilder/expanded-artifact.json. Do not change the owner launcher's pin or install this variant without separate review/native acceptance.

Expansion appends32new static references after WorldStory.Add, preserving every existing form key and all29story/guide/trigger positions/bindings. LAND, first-section/main/side quest scripts, original cabin/bed/couch, main route and bypass point arrays remain unchanged. No actor package, dialogue, quest state, inventory or save manipulation is introduced. Licensed meshes/textures remain references to the local vanilla master and are never redistributed.

## Area composition

- Wreck: an audited RRBoxcar01at850/1700/yawPI/2 spans293–1407X,1587–1813Y behind the unchanged evidence foreground. A separate bogie at1100/1450 reinforces the rail silhouette. No collision or visibility pass is inferred from the model name.
- Road: keep the encounter and eastern bypass open. Sparse vanilla maple trees and low rock banks in northwest/southeast pockets frame the route without screening the cast. The exact asset IDs/model bounds are in world-expansion.json.
- Mercy: retain the existing rest/debrief cabin and its bed/couch. Add an open freight/repair shelter centered1880/2800(floor1624–2136X/2672–2928Y) and rear supply shelter3050/3800(floor2794–3306X/3672–3928Y). Both have two floor/roof tiles, back and side walls, with504units clear across the open south front. These are architectural spaces, not functional shops/medical services or assigned NPC interiors. Floor top16 and roof underside214 need native approach/walk checks.
- Gateway: paired posts at2920/2380 and3176/2380 leave240clear width, with canopy underside214. It is an open covered approach to the existing yard gap, not an interactive hinged gate. Its southward offset keeps128standing/activation clearance from Talbot/Pritchard. Existing town trigger remains fixed.
- Streets: a west spur joins the freight shelter approach; outside-west street2260X reaches rear backstreet3558Y and the supply entrance. Ground checks end before each16-unit floor step. Actual entry/egress and step collision remain native gates.

The original LAND is flat and byte-identical. Rock banks supply terrain silhouettes; no sculpted hill, new texture pass or landscape-collision result is claimed.

## Two approved decorative-post exceptions

The old bollard chain's~164-unit gaps blocked a192-wide west junction. Coordinator approved moving only these two decorative posts in expanded mode; IDs/z/yaw/base remain fixed:

| Reference | Old XY | Expanded XY |
|---|---|---|
| Main15L,0008D7 |2236.3018/2117.1777|2450/2550|
| Main16L,0008D9 |2376.3018/2217.1777|2440/2360|

The other247old shell placements are identical. Neither moved reference is a quest interaction/trigger. Default mode retains their old coordinates and exact baseline hash.

## Source evidence and native gates

Actual-master build/readback checks expanded world/cell/reference ownership and the unchanged story binding. Main/bypass/new streets are sampled101times per segment against actual rotated ObjectBounds at player height0–128; minimum center-to-AABB distance100 satisfies the96radius(192width), with only4units of coarse margin at a rear fence panel. All27non-trigger story anchors retain at least128clearance from new/moved player-height obstacles; minimum156.78near Talbot/gate. These are conservative AABB/sample checks, not exact Havok geometry, continuous swept-volume proof or navmesh tests. world-clearance.json exposes the inspected rectangles/anchor points for review.

Inspect the before/after map, raw record comparison and actual asset bounds before native staging. Native root acceptance must walk main/bypass/new streets, both shelter steps/interiors/egress and gateway; inspect boxcar/rock/tree collision and all three site views; verify existing pickups, guides,13actors and26casts, town trigger and original bed/couch behavior. No new navmesh exists. Native tests require a working game/OS fixture; source success does not override a blocked runtime session.

The current builder would replace a CK-authored navigation result if rerun over it; its output refuses nonempty directories. Future nav integration needs a separate reviewed artifact/pipeline. Do not silently rebuild away editor-authored work.
