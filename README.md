# The Last Meridian

An original, fan-created **Fallout 4 total-conversion RPG concept** set in the southern Appalachian Mountains in 2317: eastern Tennessee, western North Carolina and northern Georgia. A gunslinger frontier encounters underground societies, buried research, mutant human lineages and a predictive intelligence.

**Status:** Preproduction. There are design documents, a logic model, Papyrus scripts that compile, and a generated plugin skeleton. On 2026-11-12 the game loaded the plugin for the first time and a scripted self-test passed: in 62 scenarios, run with nobody at the keyboard, the two quests' logic set the stages, objectives and counters the logic model predicts at every step. 49 of the scenarios are the rows of the quests' test matrices and four are about two things happening at once, all played with characters the test creates itself. The commit that passed carries the tag `mq01-logic-proof`. Nothing placed in the world has been tested: in everything that has run, a stage number stands for every trigger, pickup and line of dialogue. A first trial of things the plugin itself places (a person, a trigger and an object in the game's test room, on the branch `feat/tlm-mq01-graybox`) ran in the game on 2026-11-13 and passed: a placed trigger and a placed object each moved a quest along through the game's own scripts. A second trial the same day settled the question of people: an actor of the plugin's own with no packages stood exactly where it was placed, and activating it reached the project's script. So triggers, objects and people can all be written into the plugin by code, with no hand work in the Creation Kit. Nothing in a built place or with a player has been tested, and no playable mod exists.

## Start here
- [Open Ledger doctrine](docs/doctrine-of-the-open-ledger.md): approved philosophical spine, exile cause and quest evidence.
- [Child of the Deep](docs/child-of-the-deep.md): proposed protagonist family-exile mystery and Deep-led ending.
- [External Fallout encounters](docs/external-fallout-encounters.md): optional Brotherhood, FEV, Blue Ridge, D.C., TVA and Carolinas lore integrations.
- [Canon registry](CANON.md): current approved creative direction and provisional details.
- [NPC naming registry](docs/naming-registry.md): approved names and old-name crosswalk.
- [The Deep](docs/the-deep.md): provisional industrial vertical habitat and political choices.
- [Three-act quest spine](docs/three-act-story.md): 17 main chapters.
- [Faction and character register](docs/factions-and-characters.md): exactly four principal and four ancillary factions.
- [Fallout lore audit](docs/fallout-lore-audit.md): research agenda and compatibility risks, not yet a verified final audit.
- [World history and Hollowborn](docs/history-hollowborn.md): in-universe chronology and disputed origin theories.
- [Development plan](docs/development-plan.md): Fallout 4 Creation Kit/Papyrus vertical slice.
- [MQ01 design: Six Rounds to Mercy](docs/design/TLM_MQ01_six-rounds-to-mercy.md) and [SQ01 design: Signed Clean](docs/design/TLM_SQ01_signed-clean.md): implementation-ready design drafts (untested; no Creation Kit build yet).
- [Design amendments v0.2](docs/design/DESIGN_AMENDMENTS_v0.2.md), [verification log](docs/design/VERIFY_LOG.md) and [test runbook](docs/design/TEST_RUNBOOK.md): what changed after the designs were modelled and checked against the Creation Kit wiki, and how to take it to the game PC.
- [Tools](tools/README.md): logic model, plugin builder, consistency checks and Windows scripts. The Papyrus scripts are in `scripts/Source/User/TLM/`; they compile with the game's own compiler, and in the game one scripted scenario of their stage logic passes; nothing that needs the world has run.
- [Claude Code instructions](CLAUDE.md): repo guidance for AI-assisted engineering.
- [Open decisions](docs/open-decisions.md): unresolved continuity issues.

## Canon management
Edits should be proposed via branches and pull requests; do not silently overwrite approved canonical facts. Treat **CANON.md** as the source of truth, with supporting files expanding it. Record Fallout source provenance during lore research.

## IP and distribution
This is an unofficial fan concept, unaffiliated with Bethesda. Avoid copying assets or prose from other franchises (Tolkien, Stephen King, etc.). Follow Bethesda's modding and redistribution terms when producing distributable files.

## First playable milestone
One Appalachian rail-wreck start, Mercy Crossing hub, five NPCs, and **Six Rounds to Mercy**, including a meaningful caravan encounter. Do not start with all worldspaces or the final battle.
