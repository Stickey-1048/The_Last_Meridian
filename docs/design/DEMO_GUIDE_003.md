# DEMO-GUIDE-003 — optional repeatable directions

Development-only increment for issue 7, based on reviewed b6ac8c93. Three named
**Demo guide - ... directions** activators are appended near the wreck, caravan
road and Mercy Crossing. Their activation verb is **Directions**. They borrow
the game's clipboard/folder model; this is not rendered sign lettering or a
finished exterior. Their floor positions, visibility and activation usability
still need native walking/controller acceptance.

The objects are separate from dispatch/journal/ledger and never enter inventory
or count as evidence. Only an explicit player activation opens one help box,
with current place and the next useful action. Repeated activation is allowed.
They start disabled and are enabled with the existing manual-demo setup. A
manual-session/quiet/conversation guard prevents their menus during the audit
or another conversation; they add no automatic prompt or quest advancement.

State queries use completed flags, never `GetStage >= 20`:

| State, in priority order | Guide instruction |
|---|---|
| Stage 60 completed | First section complete; three onward destinations unimplemented; optional evidence remains optional |
| Dispatch stage 20 not completed, even if town 40/missed 34 happened | Return to wreck, search the ground for dispatch |
| Handover 50 completed but not 60 | Speak to Pritchard again to finish hand-off |
| Town 40 completed, or reading the Mercy guide, with dispatch 20 | Hand dispatch to Sheriff Owen Pritchard |
| Dispatch 20 completed, before town 40 | Take dispatch to Mercy; caravan interaction optional, Fight/Leave distinction stated |

All pre-existing placements, existing 33 A1 aliases, their order, stages, triggers,
outcomes and cast bindings are preserved. Three guide activators, placements and
aliases append after that prefix. New local form IDs append to the persisted ID
map. The exact baseline has 33 A1 references plus eight trial references (41
total); this addition brings those to 36 and 44 respectively. No game assets
are bundled. The only Act1Walk change is a read-only
CanReadGuide guard; actual guide state queries live on their alias script.

Stand-in tests cover all three locations/repeated activation, early-town34
without20, dispatch/town/mid-handoff/completion precedence, nonplayer activation,
scenario 12 without a guide box, source mutation whitelist and old alias order.
These establish internal wiring/logic, not native model placement, readability,
navmesh or a controller-button pass. Existing scenario 12 remains 42 checks.

Rollback: revert this guide increment and rebuild. Old saves may retain added
alias script state; use a fresh disposable demo for acceptance. No installed
preview, owner's save or source checkout is changed by implementation/testing.
