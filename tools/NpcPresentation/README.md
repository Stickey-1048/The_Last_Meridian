# NPC presentation 003: optional appearance studies

Standalone source prototype from exact f491eeb4e670d306530446b60f82785950dbb747. It creates three NEW, clearly labelled role-study actors in a NEW lit audition interior. It does not edit the original quest actors, appearance, inventory, factions, aliases, voice or progression. Frozen 43-file preparation and all prior prototypes are unchanged. Nothing is installed/launched; no new assets, FaceGen payload, morphs or real-person likeness were generated.

## Actual role and donor choices

| Study | Canon input considered | Terminal vanilla Traits donor | Stock outfit |
| --- | --- | --- | --- |
| Owen Pritchard, sheriff | Male, 61, grey; existing accepted story registry | EncWorkshopNPCMaleFarmer03b,0024A024; HumanRace; steel-grey hair | Drifter Outfit,000B2D8D |
| Ada Pike, gunsmith | Female, 43; burn scars and jeweller's glass in accepted registry | EncWorkshopNPCFemaleFarmer03,00113348; HumanRace; black hair | Mechanic Jumpsuit,001C26B9 |
| Miriam Keene, physician | Female from first-section spec; casting age 53/57 and grey hair are UNAPPROVED reference options, not a new locked fact | EncWorkshopNPCFemaleFarmer07b,0024A01B; HumanRace; steel-grey hair | Wasteland Lab Coat,00178B68, plus glasses001C4BE8 |

These are stock appearance studies, not final character likenesses or an assertion that vanilla faces reproduce canon ages/scars/skin tones. Grey hair supports Owen's brief; Ada's scars/jeweller's glass and Owen's star are not fabricated. No game portrait/face render has been inspected. Miriam's proposal age remains provisional.

All three chosen donors differ from those currently inherited by the real actors. Donor flags 8126 exclude further Traits inheritance; each owns human face data, a different actual vanilla FaceGeom NIF, native head parts/tint layers/morphs and the expected sex. The three FaceGeom hashes differ. Own prototypes inherit only Traits (flag 1) from the selected donor and retain unchanged ordered original copied face payloads; no head part, hair, tint or morph field is authored locally. This avoids changing a face field which an inherited template would override. Native inherited FaceGen lookup/colour must still be tested; metadata presence alone is not proof of a rendered face.

Inventory inheritance is OFF, and default outfit is explicitly bound to a new own OTFT. The prototype has no scripts/packages/default package list/factions/carried items, and is unaggressive; no vanilla settlement behavior is imported. Actual stock ARMO/ARMA references have the appropriate male/female worn models. Female glasses have their owned stock model too. Worn NIFs and all three FaceGeom NIFs are checked in memory against the exact selected asset hashes before output; no mesh/vertex/texture payload is exported. Only original code and small metadata/receipts are tracked.

## Inspectable cell and ordinary optional access

TLM_NPC_Audition is a1536x1024 enclosed room using22 new passive floor/roof/wall refs from the existing quarry/cave kit, with even ambient/directional light. Actors stand at(-384,384,16),(0,384,16),(384,384,16), facing the arrival. They have no navigation mesh or movement packages; no walking/scheduling behavior is claimed. Their displayed names include sheriff/gunsmith/physician study and prototype labels.

A new labelled freestanding door at640,512,0 in the existing Meridian road preview leads to this separate interior. The interior door returns to640,384,16 on the road; the interior landing is0,0,16. Only ordinary player door activation uses the reciprocal XTEL links; no scripts, forced transfer or automatic input were added. The room can also be located by its own EditorID for separately authorized diagnostics, but no console/game action occurred here. Two exact header-only WRLD/CELL overrides attach the new exterior door; no original child reference is copied or overridden. Native merge, door travel/landing, frame clearance, collision, room enclosure visibility and return remain open.

This is a separate optional addon requiring Fallout4.esm and TLMWorldSlice.esp (whose accepted dependency is TheLastMeridian.esp). The serializer correctly trims the unused explicit story master from the new plugin because all original actor links were removed. The builder still pins and reads the exact f491 story/world inputs as source evidence. Do not add it to the frozen 43-file candidate; a future integration requires its own review.

## Local proof

Actual ignored `build/audition-003/TLMNpcPresentation.esp` SHA256:
`A0719A3D59C811E91FB157FCB7A218DB974DB51B1D007FEAE25DCD4216CF6EF2`.

Cached offline .NET build:0 warnings/errors. Typed readback verifies the3 actors/outfits/doors and actual Traits-only/outfit/package/faction/item/persistent placement and reciprocal door targets. No Papyrus/runtime/compiler or CK export is needed for this no-script source candidate; that does not confer native acceptance.

Independent raw source-side verifier checks39 records:3NPC_,3ACHR,3OTFT,2DOOR,24REFR,2CELL,1WRLD,1TES4. Only the old world/cell headers are overridden and remain payload/flags exact after local-ID remapping. All other records are own new IDs. Native selected donor race/sex/template state, explicit clothes, sex-appropriate model, unique FaceGeom targets, ordered unchanged face payloads, persistent room/actor placement, exact geometry poses and reciprocal door/landing links are checked. Eight focused corruption methods pass, including missing Traits/inherited inventory, swapped donor/outfit, unbound actor/custom morph byte, broken return/landing, room/old-header damage and duplicate face asset hashes. A test exposed that a dictionary dropped repeated face-morph subrecords; the checker now compares the full ordered face-subrecord sequence and the first repeated-morph mutation correctly refuses. The actual plugin did not contain that test mutation.

SafeBuild is copied from the accepted source guard with only its bound project marker changed. It pins the owned master and actual project root, rejects redirected/existing outputs, uses exclusive new writes and preserves partials. Frozen LockedInput pins story/world read-only. No recursive deletion, adoption, SDK/model/service download, installation/profile/save/remote/workflow/provider action or game launch occurred.

Run cached `dotnet build --no-restore`, then guarded builder with exact owned master and a fresh project-build child. `python verify.py` / `python test_audition.py -v` use the new audition artifact and read-only exact base inputs. Old verifiers and manifests were not repinned. Rollback is to keep this opt-in addon out; no installed state changed.

Independent source/artifact review is still required. Then separately authorize a native check of face identity/colour versus vanilla donor, outfit fit/sex/age readability, room support/lighting, ordinary entry/return and closure/reload. No new face is claimed installed on an original actor.
