# Instructions for Claude Code or other coding agents

## Read in this order
1. CANON.md
2. docs/open-decisions.md
3. docs/fallout-lore-audit.md
4. docs/three-act-story.md
5. docs/development-plan.md
6. docs/factions-and-characters.md
7. docs/history-hollowborn.md

## Mandatory operating rules
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
