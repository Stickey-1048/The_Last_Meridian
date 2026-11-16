# Opt-in Shelter Details preview

Source candidate; independent review and the coordinator's normal-startup/targeted native checks must pass before owner handoff. This is a first-section exterior prototype, not a finished world.

The Details option adds six existing vanilla scenery props to the freight shelter and supply hut: crates, barrels and shelves. They do not provide inventory, crafting or medical services. Its world is the independently reviewed shelter-only E127 artifact from e69c306; it does not include the experimental sixteen fence replacements. The master and nineteen normal production scripts are identical to the reviewed Natural bundle. No private test Core is loaded.

## Separate fixed variant

| Item | Details identity |
| --- | --- |
| Option | `Play-WorldStory.ps1 -Details` |
| Clickable command file | `tools/win/Play-WorldDetails.cmd` |
| Profile | `TLM-World-Details-Preview` |
| Mod | `TheLastMeridian-WorldDetailsPreview` |
| Ownership journal | `build/world-details.unfinished.json` |
| Artifact manifest | `tools/win/world-details-artifact.json` |
| World SHA256 | E1279E42DAA19D94A628F1270D285EB8A175EE21579924C0DE51B017C25F5965 |
| Master SHA256 | AA52CBC3A6153BF83BB99EF22D8CC385DA2254052B49E4A78252494003250F3F |

Details, Natural and Expanded switches are mutually exclusive. The existing default, Expanded and Natural manifests/profile names/launch behavior remain unchanged. No arbitrary profile or artifact override is exposed by the launcher. Details uses the same fresh-character startup, balanced SPECIAL4, delayed guarded QueueFreshEntry, saved-load cancellation and owned normal-exit restoration already reviewed for the story launcher; no quest/script/stat/save behavior changes.

After reviewed staging and native acceptance, select the Details command file deliberately. Wait for exterior setup, use Directions, search the wreck and follow the first-section story. Quit normally **without saving**; close Mod Organizer too and wait for the launch window to confirm startup restored. The new profile keeps controller input enabled and preserves other copied preferences. Existing previews remain available separately.

## Workspace package and staging boundary

`Build-WorldDetails.ps1` builds only into a wholly new directory under this checkout's build folder, refusing existing/redirected ancestry. It rebuilds/readbacks the master and shelter-only world against the locally owned Fallout4.esm, verifies AA52/E127 and copies the exact nineteen reviewed runtime files after source-digest/hash checks. It does **not** invoke Papyrus or claim a new script compile: scripts are unchanged. It writes no game, manager, profile or save files.

```powershell
./tools/win/Build-WorldDetails.ps1 -VanillaMaster '<owned Fallout4.esm>' -ReviewedRuntime '<reviewed normal Scripts/TLM>' -OutputDirectory '<this checkout>/build/new-details-package'
```

The separate coordinator-only `tools/win/Stage-WorldDetails.ps1 -ReviewedSourceCommit <exact independently reviewed40hex commit>` checks the checkout against that receipt before staging. It is versioned for independent review; a local fixed-head wrapper can invoke it without changing this source. It refuses existing targets, reparse/unreadable ancestry, wrong source/bundle hashes and live/unknown game/manager/editor inventories. It copies only explicitly listed profile files, no saves, enables only the new mod and two plugins, sets controller1 only in the new profile, and preserves all existing preview/fallback bytes. Staging alone is not a native pass. No staging command was executed during source preparation.

Required before owner-ready: fixed package validation; actual normal nineteen-script `-Details` fresh startup and clean normal exit; actual rendering/support/contact of all six props and unchanged open entrances/center aisles; preserved controller preference and startup journals/batches removed after both process inventories clear. Use separate disposable QA for mouse-driven testing rather than silently changing owner controls. No new navigation, collision, services or visual-quality acceptance follows from source bounds alone. Any use of a private diagnostic Core is a separate QA context and cannot prove normal nineteen-script startup.
