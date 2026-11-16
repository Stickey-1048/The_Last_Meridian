# Natural exterior story — separate opt-in package

This source composition combines launcher53f61 (including conservative Windows process guard15ff), landscape29cae1b and quest/ending4f1ece. It adds `tools/win/Play-WorldNatural.cmd` or `Play-WorldStory.ps1 -Natural`. Native acceptance of the composed package remains pending. Source build, portable checks and prior component playtests are separate evidence.

| Selection | World pin prefix | Master | Dedicated profile | Dedicated mod | Ownership note under build |
|---|---|---|---|---|---|
| Default |6B617|286B|TLM-World-Story-Preview|TheLastMeridian-WorldStoryPreview|world-story.unfinished.json|
| -Expanded |5629|286B|TLM-World-Expanded-Preview|TheLastMeridian-WorldExpandedPreview|world-expanded.unfinished.json|
| -Natural |B056|AA52|TLM-World-Natural-Preview|TheLastMeridian-WorldNaturalPreview|world-natural.unfinished.json|

All exact hashes are in the corresponding fixed manifests. Natural uses repaired MQ01Quest70E4, Act1WalkB5CE and landmark guideDFFD; its other16 scripts retain their exact normal pins, including production CoreBD7. Default and Expanded still require their previous19-script bundles; the new package cannot satisfy either old manifest. The natural flag cannot be combined with Expanded. The launcher exposes no arbitrary manifest/profile path.

Builder modes also remain distinct: no flag reproduces6B, `--expand` reproduces5629, and explicit `--natural` producesB056. Natural implies the expansion shell and gates only the66 initially-disabled route posts and four appended trees. Existing form allocation, story/geometry data and normal source APIs remain coherent. Current shared guide source describes natural landmarks; it is compiled for the new package only. Do not recompile and silently adopt the new guide into old fallback installations.

## Build a reviewable package

Run `tools/win/Build-WorldNatural.ps1` with `-VanillaMaster`, `-PapyrusCompiler`, `-BaseSources`, `-ReviewedRuntime` and `-OutputDirectory`. Output must be wholly new and under this checkout's build directory. Existing empty directories, any existing reparse-point ancestor (junction/symlink), or unreadable ancestry metadata cause refusal before writes. The guard checks all existing ancestors through the drive root; no redirected checkout/build path is supported. This helper never installs or launches anything. Do not redistribute licensed master assets; generated development-only NPC copies remain subject to the existing project restrictions.

ReviewedRuntime is a local directory containing exactly the19 approved PEX files pinned in `tools/win/world-natural-artifact.json`: source-approved4f1ece package plus DFFD guide from29cae1b. The helper verifies current normalized logical source text against19 recorded source digests and verifies every selected reviewed PEX before creating output. Logical normalization is UTF8 text, CRLF/CR to LF, final newline retained. Provenance links each script to an approved source head; no claim that a hash proves its behavior.

The helper builds/reads back the master and natural world from current sources and actually compiles all19 scripts into a separate fresh-compile directory. New PEX contains compiler time/path metadata and may reorder string tables. It is **not** substituted for reviewed runtime or normalized to look identical. `bundle` contains only the exact reviewed frozen PEX after source/provenance checks. Preserve fresh compile logs and reviewed-runtime provenance separately. A compiler pass proves compilation, not runtime equivalence or native acceptance.

`tools/win/tests/Test-WorldVariantBuilds.ps1` optionally reproduces all three world hashes against the owner's actual master without installing. Ordinary CI uses stand-in/launcher/refusal fixtures and needs no game files or secrets.

## Root preparation and owner use

After independent review, root prepares a NEW dedicated Natural profile/mod. Copy the verified bundle only into TheLastMeridian-WorldNaturalPreview; never overwrite old fallback mods. Use LocalSaves=true and LocalSettings=true. Enable only that mod plus optional already-reviewed F4SE Scripts0.6.23/FallUI Workbench/MCM; activate TheLastMeridian.esp then TLMWorldSlice.esp. No private probe or alternate Meridian mod may be enabled or shadow files in overwrite/game Data. Preserve owner settings and saves; source builder performs none of these installation steps.

Validate using `Play-WorldStory.ps1 -Natural -ValidateOnly` (include `-UseF4SE` when the chosen UI mods require it). Then the Natural CMD explicitly opts into F4SE and the fresh-only balanced SPECIAL4 startup. No loaded-character reset occurs. Startup is COC, seven stat writes, then guarded QueueFreshEntry; no fixture/helper quest advancement. Do not load an owner save into this disposable profile.

Quit normally without saving, close Mod Organizer if it remains open, and wait for restoration confirmation. Launch/recovery refuses while Get-Process OR CIM still lists a game/manager, or either inventory fails. Only the selected profile's two temporary settings, owned startup batch and matching journal may be restored; wrong-variant/profile/batch/path notes remain untouched. Legacy untagged recovery remains default-only. If recovery fails, preserve the ownership note and files for root diagnosis. Never force cleanup while a process is still present.

Root must verify actual staged pins, fresh startup, quest setup, visible guides/landmarks, real pickup/Leave/bypass/handover, normal exit and recovery on the composed package before describing it as ready. Earlier observations used separate packages and direct-position private fixtures; they do not prove this integration, walking, pursuit/navmesh or future chapters. Rollback selects the unchanged default/Expanded fallback profile/mod and manifest; it does not mix runtime files.
