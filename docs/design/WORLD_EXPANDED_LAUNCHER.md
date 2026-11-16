# Separate expanded world launcher — native pending

`tools/win/Play-WorldExpanded.cmd` explicitly selects `Play-WorldStory.ps1 -Expanded -UseF4SE`. Direct PowerShell use supports `-Expanded -ValidateOnly`; omitting `-Expanded` retains the original story variant. Neither route installs anything. No arbitrary manifest or profile selection is exposed by the launcher.

| Variant | Fixed world pin | Profile | Isolated mod | Ownership journal |
|---|---|---|---|---|
| Default story |6B617B6F1566F34499545B940690AAB3CBF9DBC62F8051BB8E29C48112E8BB62|TLM-World-Story-Preview|TheLastMeridian-WorldStoryPreview|build/world-story.unfinished.json|
| Expanded, opt-in |5629DA87DD925A9BD8423823DA27C0E4E52E05F8DE827B2C65F48D78117CBF40|TLM-World-Expanded-Preview|TheLastMeridian-WorldExpandedPreview|build/world-expanded.unfinished.json|

The expanded manifest is the reviewed `tools/WorldSliceBuilder/expanded-artifact.json`; the default `tools/win/world-story-artifact.json` is unchanged. Both pin the same286B master and19 compiled scripts. World source is the frozen expansion b590693be66455d258ec670bb43e60868806b7a9 composed with the reviewed process guard15ff020. See WORLD_EXPAND_003.md for the actual32static additions, two approved decorative-post moves, preserved quest content and collision/navigation limitations.

The coordinator must prepare the separate expanded profile with LocalSaves/LocalSettings true, the isolated mod containing the exact master, expanded world and19 pinned PEX, and only the already-approved optional F4SE Scripts0.6.23/FallUIWorkbench/MCM dependencies. Disable other Meridian variants/private probes in that profile. Never rename or overwrite the default installed world as a shortcut. The default profile/mod and earlier shell remain available as fallbacks. Preparation and native launch are separate from this source change.

The same fresh-only COC, seven SPECIAL4 writes and explicit QueueFreshEntry request are used. No runtime, character migration, inventory/perk/level, quest rule or stage change is introduced by selecting the expanded world. The existing Windows Get-Process+CIM guard blocks either variant if game/manager is listed or inventory cannot be confirmed; it does not repair the unresolved black-load/unfinished-process condition. Native testing remains blocked until a clean Windows session and ownership recovery.

Each new note and owned batch plan records its variant; each note records its fixed profile and exact INI/game paths. Recovery validates all these before touching settings, the batch or the journal. A default note/profile/batch presented to expanded recovery, or the converse, is refused. Unique CreateNew batches retain the existing ownership/hash/path protections. Legacy untagged default notes can still recover only as default with their matching expected paths; expanded recovery requires explicit identity. These are accidental cross-session protections, not a security guarantee against someone deliberately rewriting every field of a local ownership note.

After game AND manager fully exit, recovery restores only the selected profile's two temporary settings and removes its verified owned batch/note. It preserves the other variant's settings and journal. Keep the launch window open until cleanup confirmation. Do not delete notes or bypass a guard to start another game.

This integration has fixture/source evidence only. Before owner delivery, root must verify the expanded arrival/rail wreck/streets/shelter steps/interiors/egress/gateway, original cabin furniture, three guides,13actors/26casts, pickups, peaceful Leave and a separate fresh bypass/handover path, plus actual startup/clean exit/interrupted recovery. A generated artifact, passing fixtures or a process launch is not a native play pass. No navmesh, pursuit, functional new service, finished landscape or controller input acceptance is claimed.
