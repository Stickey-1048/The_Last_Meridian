# Candidate outdoor Mercy gathering green

Source-only next playable-footprint increment from frozen b280847/E127 Details. The existing owner Details manifest/launcher/package, all scripts and all older modes stay unchanged. No installation or engine acceptance is implied.

Only trailing `--private-gathering-green` after `--natural` selects this candidate. It includes the accepted six E127 shelter props and appends five references after their allocation. It never enables the experimental sixteen fence substitutions. No actor, quest, terrain, weather, navmesh, material, stat/save or new service logic is added.

| New own ref | Vanilla base | XYZ/yaw |
| --- | --- | --- |
| 000947 BenchSouth | FURN NPCBenchParkSit01/0DF45A |1880,3190,0 /0|
| 000948 BenchNorth | same FURN |1880,3720,0 /PI|
| 000949 UnlitHearth | STAT CampFireMed01_Off_NoSkirt/06356D |1880,3455,-3 /0|
| 00094A WestRockSouth | STAT RockBoulder03/02F79B |1525,3335,59 /0|
| 00094B WestRockNorth | same STAT |1525,3550,59 /0|

The north rock moves35 south from the planning brief, solely to clear the actual bench's side approaches. Original E127 refs are not moved. Asset EditorIDs/FormIDs/models/fullbounds are checked against the actual master with no fallback.

Bench audit: HasModel,0conditions/no VMAD/items, BenchTypeNone, chairSit/eating/relaxation keywords, two enabled markers offsetX±32 with zeroY/Z/rotation, header Right/Left entrymask and Sit marker rows. This establishes no observed record-level condition/script block, not native player eligibility or animation proof. Marker raw245/249 entry parameters are retained as observations without guessing their undocumented bits. Major flags8192 are checked for identity without assigning unsupported semantics.

The green approach joins the existing west street at(2260,3455)→(2080,3455). A192-wide loop runs(2080,3303)→(1710,3303)→(1710,3607)→(2080,3607)→start, with four short side-entry branches toX1696/2064 atY3190/3720. Four virtual standing checks reserve128 from other obstacles, excluding only the corresponding target bench. These points are validation metadata, not extra game references.

Existing LAND remainsZ0. Benches have localminZ0 and sit at0; hearthminZ3 uses−3, rocksminZ−59 use59. Record-bound contact is not mesh/contact certification. No hearth fire/cooking/damage service is introduced; no NPC gathering AI is authored. Existing encounter timers/rules remain live.

```text
dotnet run --project tools/WorldSliceBuilder -- <owned Fallout4.esm> <new output> --story-source <AA52 TheLastMeridian.esp> --natural --private-gathering-green
python tools/verify_gathering_green.py <E127 control directory> <green directory>
```

Local actual-master candidate hash984117B991118EA9632ECF394B6B3C54D096529A2B2A2C265EF7307C38B29728. Raw audit requires all327 old nonheader records byte-identical versus E127, header count/nextID+5 only, five enabled own REFR records947–94B with exact base/DATA and no extra scripts/ownership, and identical story/expansion/shelter metadata. Existing291 shell+29 story refs are preserved. Normal default/Expanded/Natural/Details builds reproduce6B617/5629/B056/E127 exactly.

Focused bounds audit covers1414 old route samples,909 connected green approach/loop/side samples,27 existing anchors and four bench standing points. Native collision, walking, seat orientation and entry/exit remain pending independent review and root's controlled engine check. Native test must begin idle, use one real Activate, confirm actual sitting/rendered state, stand and walk away; a true Activate return or furniture-looking mesh is insufficient. Do not force controls/AI, use godmode/no-clip, or double-toggle a fixture that already entered furniture. No owner manifest adoption until the exact reviewed native gate passes.
