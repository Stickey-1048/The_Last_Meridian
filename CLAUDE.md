# Instructions for Claude Code or other coding agents

## Read in this order
1. CANON.md
2. docs/naming-registry.md
3. docs/open-decisions.md
4. docs/fallout-lore-audit.md
5. docs/three-act-story.md
6. docs/development-plan.md
7. docs/factions-and-characters.md
8. docs/history-hollowborn.md
9. docs/the-deep.md
10. docs/child-of-the-deep.md
11. docs/external-fallout-encounters.md
12. docs/doctrine-of-the-open-ledger.md

## Mandatory operating rules
- Follow docs/naming-registry.md for all current NPC names; obsolete variants are not canonical.
- Treat CANON.md LOCKED facts as binding. Do not silently substitute earlier story versions or invent a fifth main faction.
- Setting: southern Appalachian TN/NC/GA, NOT Arizona or the Wild West.
- Four principal endgame factions; four ancillary factions; Hollowborn is umbrella term; Glassborn is a subgroup.
- All new Fallout-lore claims must be sourced/flagged; do not call original inventions Bethesda canon.
- Prefer a first working vertical slice to speculative full-scale code generation.
- If Creation Kit records or Papyrus code cannot be compiled/tested in the present environment, label as untested scaffolding.
- Use one issue/branch per feature; provide implementation checklist, quest stages, dependencies, tests and rollback.
- Never commit proprietary game assets, secrets, licensed music or other games' copyrighted materials.
- Avoid modifying canonical narrative files without a documented decision and review.
- Maintain playable alternatives so ancillary quests never gate core Act II/III progression.

## First task proposal
Produce a technical design document for TLM_MQ01 'Six Rounds to Mercy': prerequisite plugin setup; quest stage table; all aliases; scene/dialogue tree; caravan decision state; objectives; Papyrus scripts only where necessary; Creation Kit click-path checklist; test matrix. Start with documentation, then incrementally implement and test in Creation Kit on a machine with Fallout 4 installed.

## New narrative note
The current creative proposal re-centers the story on the player's concealed family descent from exiles of The Deep. Preserve the player's real childhood; recent Rider memory tampering is targeted. Do not draft detailed protagonist dialogue or implementation of ending branches until docs/child-of-the-deep.md choices are settled.

## Coding priorities — post-Open Ledger revision
Do NOT build late-story factions first. Propose an implementation-ready design for TLM_MQ01 Six Rounds to Mercy and one evidence-based secondary objective with a falsified maintenance or ration ledger. Include Creation Kit record types, quest aliases, objective/stage transitions, dialogue conditions, Papyrus responsibilities, NPC packages, persistence, failure/reload cases and tests. Keep ideological decisions expressed through consequences, not mandatory player monologues. Build no untested claim of a functioning mod.

## Tooling (added 2026-11-11)
- Run `tools/run_checks.sh` before committing any change to quest rules, scripts or the plugin spec. It needs Python 3 and the .NET 8 SDK, not the game.
- Change rules in this order: `tools/logic_model/` (model and tests), `scripts/Source/User/TLM/*.psc`, `tools/PluginBuilder/Spec.cs`. The checks fail if they drift apart.
- A pass means the design is internally consistent. It is not a compile and not a game test; say so when reporting.
- `tools/win/Run-Scenarios.ps1` counts scored scenarios and play sessions (number 900) apart: a play session is `SET UP` or `NOT SET UP`, has no checks and is never a pass; report it in those words. A scenario the runner had to close after its RESULT line is `TIMED OUT`, and a run that could not put back what it changed, or whose installed plugin is not the build, ends as failed whatever its scenarios did. The reading and counting are in `tools/win/Tlm.psm1`; after changing them run `pwsh -NoProfile -File tools/win/tests/Test-ScenarioReport.ps1` (stand-in logs, no game; Windows PowerShell 5.1 runs it too).
- The same script runs on GitHub for pull requests (`.github/workflows/portable-checks.yml`, "Portable checks"), followed by that PowerShell test. A green run there is the same thing and no more: not a compile, not a game test. The workflow has read-only access and needs no secret of the owner's (its checkout uses GitHub's own temporary read-only token); do not give it write access or secrets, and do not make it deploy or release.
- The in-game cases of the test matrices are generated: change `tools/logic_model/` or `tools/gen_matrix_cases.py`, then run `python3 tools/gen_matrix_cases.py`. Never edit `scripts/Source/User/TLM/MatrixCases.psc` or `tools/matrix_cases.json` by hand.
- `tools/papyrus_sim` runs the real scripts against a stand-in for the game (`python3 tools/papyrus_sim <scenario numbers>`). Use it to rehearse a script change before asking for a run on the PC. Its rules are marked seen / documented / assumed; a pass there is still not a game test. Add to `tools/papyrus_sim/game_runs.json` only from a real report, and never edit a recorded number to make a test pass.
- On a PC with Fallout 4, follow `docs/design/TEST_RUNBOOK.md`. Record what was actually run in `docs/design/VERIFY_LOG.md`. `docs/design/BUILD_ENV.md` is the scan's inventory of that PC: it is git-ignored and must not be committed, and only the facts the build depends on go into the public docs.
- Never copy files into a Fallout London install. `tools/win/Install-Dev.ps1` refuses by default; do not override it without the owner saying so.
- What the plugin places in a cell of the game is listed in `Spec.Placed` and written by the builder; nothing is placed by hand. The stand-in engine's rules for placed things (triggers, picking things up, the game's default alias scripts) were written from the Creation Kit wiki and borne out by the game on 2026-11-13 (`docs/design/VERIFY_LOG.md`, the thirteenth run). About placed people the game showed on 2026-11-13 (the fourteenth run): an actor with no packages and no script stands exactly where it is placed and can be activated, which reaches a script on its alias; the game's own settler does not stay, because its sandbox package puts it on a seat the moment it is enabled. Make the people of a walk-through as actors with no packages. `Enable` took between 1 and 30 seconds to come back for such a person, differently in every run, which is not explained; give such steps time. An actor in `Spec.Npcs` is made by the builder as a copy of one of the game's, on the PC, from that PC's own master; such a copy is for development builds only. The placed-content trial (`docs/design/TLM_GRAYBOX_trial.md`) is development only and must not ship.
- The first section of Act I as a rough cut (`docs/design/TLM_ACT1_first_section.md`) is development only and must not ship: its people are copies of the game's settler and it stands in the game's test room. Its records are in `tools/PluginBuilder/SpecAct1.cs`, its lines and its unattended check (scenario 12) in `scripts/Source/User/TLM/Act1Walk.psc`; a line changed in one is changed in the other, and `tools/papyrus_sim/test_act1.py` plays every road through the chapter against the logic model. It changes neither the two quests' rules nor their records: a button only sets a stage. No message box may open in an unattended scenario (nothing counts time while one is open, so the run never ends); the stand-in engine stops a session that opens one. To play it on the PC: `tools\win\Play-Act1.ps1`. It compiled and its unattended check passes in the game (2026-11-14: 39 of 42 in the fifteenth run, 42 of 42 in the sixteenth, in the seventeenth, where all 65 scenarios passed, and in the eighteenth; `docs/design/VERIFY_LOG.md`); the owner played it once, on 2026-11-14 (273 seconds, as the coordinator reported: the wreck's papers and clues found, the side quest finished, the dispatch never taken, "unclear what to do"); nothing may claim more of a person's play than that report holds, and a `SET UP` is not a play. After that play the opening notice and the main quest's first objective were reworded to say what to do at the wreck (amendment A26); change the two together. From that run: lists of aliases and of text as script properties, arrays made by a script, `ForceRefTo` for things, a placed actor that starts dead and `EnableNoWait` all work; thirteen people asked for together are there together 26 to 40 seconds later; a placed weapon can be picked up and the scripts on its aliases hear it; the game's .44 is the record `44`, which a player sees as ".44"; people of the plugin's own in factions of the plugin's own, with a temper that starts no fight, stand by a killing. A thing of the game's found by the name a player sees may be one no player can have (a companion's weapon was): the builder passes those over, and its output is to be read after every build on the PC. A spot in the test room is open floor only once somebody has stood on it.
