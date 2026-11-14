# Act I asset pack: review before use

Status: generated staging assets, **not canon or in-engine verified**.

## Included
- 22 character casting cards (11 roles x A/B), `characters/casting_cards.json`.
- 69 entries of in-world data in `text/act1_texts.json` (12 notices, 36 spoken remarks, 6 ledgers, 5 letters, 10 labels).
- A 260 m by 110 m survey strip in `layout/road_plan.json`, with 12 actor spots, wreck, town buildings and 4 trigger volumes.
- 31 PNG sign, notice, paper, seal and emblem images from original image-generation tile art with programmatic lettering; and 3 PNG maps.

## Not delivered in this batch
- 22 individually generated 1024 x 1024 portrait images. Casting cards are usable references but portrait images are not present.
- A tested game-image/decal importer, 3D models, recorded sound or voices.
- Any verified Fallout 4 in-engine placement of these coordinates.

## Design caveats
- Sign backgrounds are an original texture atlas; all typography applied programmatically and visually checkable. These are prototype textures rather than final UV-ready texture sets.
- Wax seal variants use aged paper backgrounds, not the originally requested plain mid-gray background. Revise before final import.
- The Cutter reward image contains a symbolic drawing, not an approved accurate face portrait.
- The blank regional map removes all words; it retains graphic geography. West/north orientation is schematic. The labels for Greenwater, Red Hollow, Iron Junction are proposed.
- The road-strip 260 m length is a *gameplay compression*, not a literal journey of 'hours east' from the wreck to town. The final design should create a worldspace transition or reinterpret the opening narrative distance.
- Several introduced names from the brief (Tobias Gantt, Nell Fenwick, Abel Rudd, Reese Dunmore, Corwin Haskell, R. Ostrander) remain [NEW/PROPOSED] until approved.
- One text notice mentions a lost boot owner but introduces no named NPC.
- `road_plan.json` measures x increasing WEST from the EAST end, y increasing NORTH from the SOUTH edge. Convert to Fallout 4 world coordinates before using Spec.Placed.
- Material is original art; no official franchise logos or characters have been copied.

## QA
- Image dimensions programmatically validated; JSON parses; entry counts validated.
- Readable font and long-line fitting should receive human review at in-game resolution.
- Do not add any of these assets to shipping build until the project's image importer is implemented, provenance and permissions are approved, and actual placement is verified in Creation Kit.
