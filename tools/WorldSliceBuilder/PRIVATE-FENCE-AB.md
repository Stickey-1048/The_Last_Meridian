# Private sixteen-panel fence comparison

Unpublished art experiment from14d841. This is not the owner world or an approved appearance improvement. Do not change production manifests or install it through the owner launcher.

`--private-fence-ab` may appear only after `--natural`. It changes only the base link of16 already allocated boundary references: South/West4–7 and North/East21–24. Existing control is PicketFenceB_PW_Fence01/00125C67; specimen is PicketFenceStr02/0003622D. The master must match the audited record identities and bounds; there is no fallback. All34 Yard panels, gateway,104 other boundary panels, actors, story/guide refs, positions, rotations, flags, allocation and LAND remain unchanged. No mesh/material/texture editing or Z adjustment occurs.

The control local bound is(-64,-2,0)..(64,2,96), specimen(-64,-15,0)..(64,5,95). Both have128 span and centered localX; depth increases from4 to20 and top is1 lower. This is **not proof of darker color or a useful silhouette improvement**. At this builder's clockwise yawPI/2, localX maps to negative worldY and localY to positive worldX. South/West inside-facing extents increase3; North/East increase13. North specimen-to-supply ground obstacle gap drops34→21, with no rear access route promised.

Using your locally owned master and the reviewed AA52 story master in separate new output directories:

```text
dotnet run --project tools/WorldSliceBuilder -- <Fallout4.esm> build/fence-ab-control --story-source <TheLastMeridian.esp> --natural
dotnet run --project tools/WorldSliceBuilder -- <Fallout4.esm> build/fence-ab-str02 --story-source <TheLastMeridian.esp> --natural --private-fence-ab
python tools/verify_private_fence_ab.py build/fence-ab-control build/fence-ab-str02
```

Local GOG-master build/readback: default control reproducesB056F66D23D18BA7D156177C64B67552B10B2A74234C78139FBDCD5AED660723; specimen9EED4A7984AE1DFCCEEE6B44D623E0CE92EF73613DACBCB311DEACC904BBC37C. Raw audit requires identical record keys/header bytes and all subrecords except16NAME substitutions, exactly48 changed whole-file bytes,34 yard panels retained, all29 story refs unchanged, identical story/expansion metadata. It independently checks specimen rotated bounds and1414 sampled route centers plus27 protected story anchors. Bounds are a coarse screen, not Havok collision/navmesh proof.

Independent source review must precede a separately staged private native comparison. Preserve the ownerB056 artifact. Compare the selected four-panel runs and adjacent unchanged controls from matching wreck/town camera positions and lighting; record model joins, ground support, actual color/density and supply-edge clearance. Reject the hypothesis if it remains bright/visually dominant or harms joins/clearance. No global swap, darker/material claim, native walking, unjumpable edge, new region or navmesh acceptance follows from this build.

Luis's later audit addendum prefers separate rough-wood/chainlink/Beach specimens; this narrow Str02 experiment follows the coordinator's explicit one-candidate scope. It does not supersede that art advice or authorize a global picket replacement.
