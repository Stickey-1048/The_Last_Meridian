# Tools

Everything here supports building and checking the mod. None of it is the mod, and none of it has been run against a real Fallout 4 install yet.

| Path | What it is | Runs on | Tested how |
|---|---|---|---|
| `logic_model/` | Python model of the MQ01 and SQ01 rules, the test matrix, and an exhaustive state search | anywhere (Python 3.10+) | 83 tests pass; 8 engine-only cases are skipped |
| `PluginBuilder/` | Generates `TheLastMeridian.esp` data records from `Spec.cs` (.NET 8, Mutagen) | anywhere | writes the file, reads it back, compares with the spec. Not loaded in the Creation Kit or game. The `--fallout4-esm` path has run only against a generated stand-in master, never the real one |
| `check_consistency.py` | Lints the Papyrus against documented native signatures; cross-checks scripts, plugin and model | anywhere | 11 kinds of injected fault were each caught |
| `papyrus_natives.json` | Signatures of the natives the scripts call, from the Creation Kit wiki | data | |
| `run_checks.sh` | Runs the three checks above | Linux, macOS, Git Bash | |
| `StandInMaster/` | Generates a tiny stand-in `Fallout4.esm` (two records) so the builder's vanilla lookups can be exercised without the game | anywhere | used by `run_checks.sh` |
| `win/Run-FirstBuild.ps1` | One command for the first session on the game PC: scan, plugin build, script compile, one log file | Windows | three cases against stand-ins: still downloading, all installed, compiler error |
| `win/Get-BuildEnv.ps1` | Read-only scan of the PC's Fallout 4 installs and a Mod Organizer 2 instance; writes `docs/design/BUILD_ENV.md` | Windows | against stand-in folder trees (Steam layout; GOG + Mod Organizer layout) on Linux PowerShell 7; registry lookups untested |
| `win/Build-Scripts.ps1` | Compiles the scripts with the game's Papyrus compiler into `build\Scripts` | Windows | with a stand-in compiler |
| `win/Package-Dev.ps1` | Packs the plugin and scripts into `build\TheLastMeridian-Dev.zip`, laid out like a Data folder, for installing with any mod manager (Vortex, Mod Organizer) | Windows | zip contents checked on Linux PowerShell 7; not yet installed with a real mod manager |
| `win/Install-Dev.ps1`, `win/Uninstall-Dev.ps1` | Install the build as a Mod Organizer mod (or into a game folder) and remove it again, with backups and a manifest | Windows | against stand-in folder trees; the game and Fallout London folders were confirmed untouched in Mod Organizer mode |

The Windows scripts were only ever run under PowerShell 7 (`pwsh`). They avoid 7-only syntax so Windows PowerShell 5.1 should work, but that is untested.

## Everyday use

```bash
tools/run_checks.sh                 # all checks that need no game
```

Change a rule in this order: `logic_model/tlm_model.py` and its tests, then `scripts/Source/User/TLM/*.psc`, then `PluginBuilder/Spec.cs`. `run_checks.sh` fails if the three drift apart.

`PluginBuilder/formkeys.txt` maps each EditorID to its FormID. Keep it in git: it is what stops a rebuild from renumbering records.

On the game PC, follow [docs/design/TEST_RUNBOOK.md](../docs/design/TEST_RUNBOOK.md).
