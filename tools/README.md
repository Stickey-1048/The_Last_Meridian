# Tools

Everything here supports building and checking the mod. None of it is the mod. The Windows scripts and the plugin builder first ran on the owner's PC on 2026-11-11 (results in [docs/design/VERIFY_LOG.md](../docs/design/VERIFY_LOG.md)); nothing has been loaded by the Creation Kit, and the first attempt to load the plugin in the game (2026-11-12) did not reach it.

| Path | What it is | Runs on | Tested how |
|---|---|---|---|
| `logic_model/` | Python model of the MQ01 and SQ01 rules, the test matrix, and an exhaustive state search | anywhere (Python 3.10+) | 84 tests: 76 pass, 8 engine-only cases are skipped |
| `PluginBuilder/` | Generates `TheLastMeridian.esp` data records from `Spec.cs` (.NET 8, Mutagen) | anywhere | writes the file, reads it back, compares with the spec. Not loaded in the Creation Kit or game. The `--fallout4-esm` path has run against the real `Fallout4.esm` (GOG 1.10.163): `Caps001` and the player reference both resolve |
| `check_consistency.py` | Lints the Papyrus against documented native signatures; cross-checks scripts, plugin and model | anywhere | 11 kinds of injected fault were each caught |
| `papyrus_natives.json` | Signatures of the natives the scripts call, from the Creation Kit wiki | data | |
| `run_checks.sh` | Runs the three checks above | Linux, macOS, Git Bash | |
| `StandInMaster/` | Generates tiny stand-in `Fallout4.esm` files (three variants) so the builder's vanilla lookups can be exercised without the game | anywhere | used by `run_checks.sh` |
| `win/Run-FirstBuild.ps1` | One command for the game PC: scan, plugin build, script compile, one log file (also copied to the clipboard); `-Install` adds the install, `-Play` the in-game test | Windows | ran on the owner's PC under Windows PowerShell 5.1 up to and including `-Install`: every step passed. `-Play` is tested against stand-ins only |
| `win/Get-BuildEnv.ps1` | Read-only scan of the PC's Fallout 4 installs, mod managers and settings folders; writes `docs/design/BUILD_ENV.md`, which is git-ignored and stays on that PC | Windows | against stand-in folder trees (Steam layout; GOG + Mod Organizer layout) on Linux PowerShell 7; registry lookups untested |
| `win/Build-Scripts.ps1` | Compiles the scripts with the game's Papyrus compiler into `build\Scripts` | Windows | with a stand-in compiler |
| `win/Package-Dev.ps1` | Packs the plugin and scripts into `build\TheLastMeridian-Dev.zip`, laid out like a Data folder, for installing with any mod manager (Vortex, Mod Organizer) | Windows | zip contents checked on Linux PowerShell 7; not yet installed with a real mod manager |
| `win/Install-Dev.ps1`, `win/Uninstall-Dev.ps1` | Install the build as a Mod Organizer mod and create a separate test profile (or copy into a game folder), and remove it again | Windows | against a stand-in Mod Organizer setup: the new profile is checked byte for byte, existing profiles and both game folders are confirmed unchanged. `Install-Dev.ps1` ran on the owner's PC on 2026-11-11, and the real Mod Organizer opened the profile it made. `Uninstall-Dev.ps1` has only run on Linux |
| `win/Start-TestGame.ps1` | Starts the base game by its full path through Mod Organizer in the test profile, reads from the running process which copy of the game it is, waits for it to close, then collects the results | Windows | against stand-ins for Mod Organizer and the game (right copy, wrong copy, nothing starts, started by hand, already open). The Mod Organizer command line comes from its 2.5.2 source and has not met the real program |
| `win/Get-TestResults.ps1` | After an in-game test, puts a verdict, the self-test's log, the relevant lines of the game's script log, and what the game was given to load onto the clipboard | Windows | against stand-in folders and log files. Its first version ran on the owner's PC |

`Run-FirstBuild.ps1`, `Get-BuildEnv.ps1`, `Build-Scripts.ps1` and `Install-Dev.ps1` have run under Windows PowerShell 5.1 on the owner's PC. `Start-TestGame.ps1`, `Uninstall-Dev.ps1`, `Package-Dev.ps1` and the present `Get-TestResults.ps1` have only run under PowerShell 7 on Linux.

## Everyday use

```bash
tools/run_checks.sh                 # all checks that need no game
```

Change a rule in this order: `logic_model/tlm_model.py` and its tests, then `scripts/Source/User/TLM/*.psc`, then `PluginBuilder/Spec.cs`. `run_checks.sh` fails if the three drift apart.

`PluginBuilder/formkeys.txt` maps each EditorID to its FormID. Keep it in git: it is what stops a rebuild from renumbering records.

On the game PC, follow [docs/design/TEST_RUNBOOK.md](../docs/design/TEST_RUNBOOK.md).
