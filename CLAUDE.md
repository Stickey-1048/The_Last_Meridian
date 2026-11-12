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
- On a PC with Fallout 4, follow `docs/design/TEST_RUNBOOK.md`. Record what was actually run in `docs/design/VERIFY_LOG.md`. `docs/design/BUILD_ENV.md` is the scan's inventory of that PC: it is git-ignored and must not be committed, and only the facts the build depends on go into the public docs.
- Never copy files into a Fallout London install. `tools/win/Install-Dev.ps1` refuses by default; do not override it without the owner saying so.
