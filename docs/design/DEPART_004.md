# DEPART-004 — living-gang departure cue

Development-demo presentation only. The owner reported that peaceful Leave and
the demo endpoint worked, but gang cleanup needed a clear visible explanation.
This cue describes town cleanup, not a killing, a new outcome or walking AI.

Stage 40 keeps its existing resolution/wait/move/disable/update behavior. The same
four Cutter aliases are disabled in the same order. Before cleanup, their actor
references and alive/enabled state are recorded. Afterwards, departure is proven
only if all four references are known and unchanged, no living gang member is
still enabled, and at least one living actor was newly disabled. Missing or
replaced references, failed disables, already-disabled groups and all-dead groups
do not establish a new living departure.

After that proof, the existing A1 presentation script receives the surviving
count only if its manual Begin registered it. Only a begun manual demo, outside its quiet audit,
can show the one-time nonmodal notification:

- One living survivor: “The surviving Cutter has left the caravan road.”
- More than one: “The surviving Cutters have left the caravan road.”

No message box, death claim, scripted walking animation, quest stage, outcome,
reward or actor-kill action is added. A persisted one-shot flag and the verified
newly-disabled check prevent repeats. Scored sessions/audit 12 remain silent.
The private presentation reference is not a prerequisite for MQ01 cleanup.
It is registered at runtime, not added to plugin properties, so archived-script
binding checks remain strict and compatible. Scored sessions never register it.

The plugin itself, placements, aliases, form IDs, stages and scored checks are unchanged.
The current input includes all 44 references (36 A1 plus 8 trial); this task adds
no references. The historical pre-footprint total 34 remains a separate baseline.

Stand-in tests cover removal/first cue, lead death without departure, all dead,
one survivor, failed disable, missing alias, repeat town cleanup, continued
handoff and scored/audit silence. Compile/stand-in passes are not proof of native
notification visibility or physical walking. Maya must verify the new cue on
the exact game build before calling it a native pass. No installed preview or
owner save is changed by this source task.

Rollback: revert this presentation commit and rebuild. No outcome migration or
save reset is involved; use a fresh disposable demo for native comparison.
