# Private explicit art composition

Source-only integration of independently accepted fence9a073c4 and shelter-detail e69c306, based on14d841. This is NOT owner adoption or native visual approval. No script/runtime, actor, quest, LAND, weather, navmesh, service or material change is added by integration.

Only trailing `--private-art-combined` after `--natural` enables both deltas. Individual `--private-fence-ab` and `--private-shelter-detail` remain available and mutually exclusive through that single trailing selector. Stacking them does not silently compose them; it is rejected. Default natural output is unchanged.

Local GOG-master build/readback from this integrated source reproduces:

| Mode | World SHA256 |
| --- | --- |
| Default natural | B056F66D23D18BA7D156177C64B67552B10B2A74234C78139FBDCD5AED660723 |
| Private fence only | 9EED4A7984AE1DFCCEEE6B44D623E0CE92EF73613DACBCB311DEACC904BBC37C |
| Private detail only | E1279E42DAA19D94A628F1270D285EB8A175EE21579924C0DE51B017C25F5965 |
| Private combined | 60A7FEE8BAD8D39184CE5FEC458B9907ADC10885C2A43814AF2E62143BF5C963 |

The combined plugin retains all old reference identities/positions/flags except exactly16 accepted Boundary NAME base links. It appends only six accepted own STATIC references941–946. TES4 HEDR count/nextID increase6; no other existing record changes. All29 story refs, LAND, gateway and34 Yard panels stay untouched. The actual new reference bytes match accepted detail E127 exactly; the16 fence record bytes match accepted fence9EED exactly. This does not authorize a global fence change.

```text
dotnet run --project tools/WorldSliceBuilder -- <owned Fallout4.esm> <new output> --story-source <AA52 TheLastMeridian.esp> --natural --private-art-combined
python tools/verify_private_art_combined.py <B056 control directory> <9EED fence directory> <E127 detail directory> <combined directory>
```

The read-only integration audit runs both accepted audits, checks raw exact composition and new bytes/header identity, and rescreens combined1414 original route samples,202 interior aisle samples and27 protected anchors. Floors alone remain excluded from the interior upright-obstacle screen because they are the existing support surfaceZ16. New prop top145 remains below roof214; north-supply ground fence gap21 remains explicit. These are coarse record-bound checks, not physical/native proof.

The original individual private READMEs describe exact placements/assets and limitations. Any later private native trial must be separately staged/reviewed with unchanged AA52 and normal19 production runtime pins. Inspect actual appearance, model joins/support, clipping, collision and routes/aisles. No darker-fence, service, walking, containment, navmesh or owner-ready claim follows from this integration. Preserve ownerB056 and both individual candidates as evidence/fallbacks.
