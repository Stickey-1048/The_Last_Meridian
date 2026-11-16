# Private six-prop shelter detail

Unpublished source experiment from14d841, separate from the ownerB056 and private fence branches. `--private-shelter-detail` is allowed only as the trailing flag after `--natural`. Default natural output remains B056. No owner launcher/manifest adopts it.

Six new vanilla STATIC references are appended after every existing shell/story/expansion reference. West freight shelter receives WoodCrate03, MetalBarrelStatic01 and MetalShelf01; north supply hut receives MetalShelf04, WoodCrate01 and WoodBarrel01. These are stored-cargo/supplies set dressing, not containers, crafting benches, medical services, seats or new quest interactions. No actors/scripts/weather/terrain/navmesh/old placement change occurs. Existing yard/gateway/route/guide/actor records remain unchanged.

The builder matches each asset's actual EditorID, FormID, model and full OBND to the locally audited master; mismatch throws, never substitutes caps or a different model. All new bound minima areZ0 and sit at the existing native-tested floor surfaceZ16. Highest top145 leaves69 below the existing roof underside214. Actual mesh support/collision/rendering must still be tested.

Props are parked at side/back margins. In addition to the original1414 route-center samples, two192-wide interior center-aisle screens run from freight(1880,2560)→(1880,2824) and supply(3050,3572)→(3050,3824). Only the known supporting floor bodies are excluded from the interior upright-obstacle screen. Existing gateway and all main/bypass/rear-street routes stay untouched. This is coarse AABB clearance, not navmesh/Havok/walking proof.

```text
dotnet run --project tools/WorldSliceBuilder -- <owned Fallout4.esm> <new control directory> --story-source <AA52 TheLastMeridian.esp> --natural
dotnet run --project tools/WorldSliceBuilder -- <owned Fallout4.esm> <new detail directory> --story-source <AA52 TheLastMeridian.esp> --natural --private-shelter-detail
python tools/verify_private_shelter_detail.py <control directory> <detail directory>
```

Local actual-master final readback gives candidateE1279E42DAA19D94A628F1270D285EB8A175EE21579924C0DE51B017C25F5965, versus default/controlB056F66D23D18BA7D156177C64B67552B10B2A74234C78139FBDCD5AED660723. All321 old nonheader major records are byte-identical, including all285 shell/29 story refs, LAND and gateway. The header only increases HEDR record count and nextFormID by6; six own REFR records are appended. Original story/expansion metadata is unchanged. No old runtime binary needs recompilation or substitution.

Independent source review is required before any separately staged private visual trial. Later root inspection must check shelf/crate/barrel support, wall/roof/model clearance, entrances/aisles and visual usefulness in the actual engine. Do not imply those checks passed from bounds. Do not compose this with the private fence candidate or owner package until both deltas and final composition are explicitly reviewed.
