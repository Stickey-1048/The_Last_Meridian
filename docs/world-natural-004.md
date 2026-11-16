# WORLD-NATURAL004: replace the route-post course with landmarks

The expanded exterior's 66 paired metal route posts dominate the player-height view. This revision hides those decorative references in expanded mode, retains the existing wooden road markers and covered town gateway, and adds four smaller trees in two groups. The exterior directions now name those landmarks and explain the eastern bypass without promising a continuously marked path.

This is a source/build candidate, not a tested owner demo. It changes no quest outcomes, actor positions, trigger extents, furniture, terrain heights or new services. It preserves the old references and IDs; the 66 old route-post references remain allocated but initially disabled. The four new static trees are appended after the previous expansion. The default story output remains byte-identical to 6B617B6F1566F34499545B940690AAB3CBF9DBC62F8051BB8E29C48112E8BB62.

## Exact candidate

- World: B056F66D23D18BA7D156177C64B67552B10B2A74234C78139FBDCD5AED660723.
- Story master: unchanged 286B2C78146413F4519351805A504264C52D7B06F51C56241F8D07D6EE5BE103.
- Changed runtime: Act1Guide.pex DFFD07D540AFD85A477253000A7A7AED38D6B0264FA51EE6FCFCE3B3B2896B2F. Other18 pins unchanged in expanded-artifact.json.
- Builder base: b590693be66455d258ec670bb43e60868806b7a9. Frozen5629 expanded and6B617 default artifacts remain separate fallbacks. No installed profile or mod is replaced by this source change.

Four TreeMapleForestsmall1 additions use the existing audited vanilla static06C6D0. Roots/yaw-radians: wreck650/2360/0.35 and800/2210/1.1; town3630/3690/0.7 and3690/3720/1.5. Each rootZ4 offsets the model's minimumZ-4 to ground. Full rotated bounds pass the builder's existing192-wide route and128-radius protected story-anchor checks. Those are conservative object-bound checks, not Havok collision or walking proof.

## Validation already performed

Actual .NET build and local licensed-master world generation succeeded. Raw-byte comparison against5629 found all318 previous record keys and payloads preserved, only the66 intended initial-disable flags changed, and four appended scenery references; the new total is322 records. Terrain, quest records, actors and triggers remain unchanged. Real Papyrus2.8 compiled the single changed guide successfully. A separate default rebuild retained the exact6B617 hash.

The intermediate posts-only95CA artifact received independent preservation review. That does not accept this later four-tree/guide composition. The final candidate requires independent review, remote checks, and new actual views of wreck, caravan/bypass and town. Guide text must be displayed and route landmarks verified in the game. Full walking, roof/doorway collision and navigation remain separate gates. Bright perimeter treatment and supply-shelter relocation are deferred; this pass does not claim to solve those larger composition/access issues.

The caravan-death acknowledgment repair and shortened ending-master candidate are separate work. They are not part of this manifest and must be explicitly composed and retested before any combined demo handoff.
