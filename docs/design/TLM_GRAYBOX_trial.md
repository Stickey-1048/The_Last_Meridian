# The placed-content trial

Phase 2, first step. Branch `feat/tlm-mq01-graybox`. Self-test scenario 10.

**Status: untested scaffolding.** Nothing described here has been compiled by the Papyrus compiler, opened in the Creation Kit or run in the game. Every check that works without the game passes (`tools/run_checks.sh`); what that does and does not show is in [Tests](#tests). The first run on the game PC decides whether any of it works. Record that run in [VERIFY_LOG.md](VERIFY_LOG.md) and change this line.

## What it is for

Everything proved in the game so far was made at run time by a test script: actors spawned beside the player, markers placed and moved, stages set. A place a player can walk through needs something else: people, triggers and objects that are **in the plugin**, placed in a cell, with quest aliases that point at them. The plan is to generate those by code, as the quests are, so that no hand work in the Creation Kit is needed for a rough walk-through of *Six Rounds to Mercy*.

Before building that, this trial asks the smallest version of the question: **does a person, a trigger and an object written into the plugin by the builder work in the game at all?** It is a throw-away. Nothing in it is story content, and it is deleted when the rough walk-through replaces it.

It does not touch `TLM_MQ01` or `TLM_SQ01`. It has a quest of its own.

## What the plugin gains

All of it is development only and marked "trial" in `tools/PluginBuilder/Spec.cs`.

| Record | What it is |
|---|---|
| `TLM_MISC_TrialObject` | An item. Its world model is borrowed from the game's bottle cap (`Caps001`): the builder copies the **path** of the model file and the size of its bounding box into the plugin. No file of the game's is copied anywhere |
| `TLM_ACTI_TrialTrigger` | An activator with no model. Placed with a box around it, it is a trigger |
| `TLM_MSG_TrialPersonName` | A message whose title, "Trial Settler", is the name the placed person is shown under. A placeholder, not a character and not in the naming registry |
| `TLM_Trial` | The quest (below) |
| A copy of the record of the game's test room, `QASmoke` | A plugin puts something into a cell it does not own by carrying its own copy of that cell's record with the new references under it. Only the cell's record is copied. The game's own contents of the room stay in the game's master file; the builder stops if the copy comes with any of them, and the checks look again in the written file |
| `TLM_REF_TrialPerson` | A placed copy of the game's generic settler (`WorkshopNPC`), **initially disabled** |
| `TLM_REF_TrialTrigger` | A placed `TLM_ACTI_TrialTrigger` with a box reaching 150 units from its middle on each axis, on the collision layer `L_TRIGGER` |
| `TLM_REF_TrialTriggerGameBase` | The same box on the game's own empty trigger (`DefaultEmptyTrigger`), for comparison. Left out, and reported, if the game has no activator of that name |
| `TLM_REF_TrialTriggerActorZone` | The same box on `TLM_ACTI_TrialTrigger` again, on the collision layer `L_ACTORZONE`, for comparison |
| `TLM_REF_TrialObject` | A placed `TLM_MISC_TrialObject` |

The five references are persistent, which a reference needs to be for a quest alias to point at it.

**Why two comparison triggers.** The wiki says a trigger's layer is "typically L_TRIGGER". A forum report (Nexus Mods, game not certain) has someone changing a trigger's layer *from* `L_ACTORZONE`, which suggests that is what the editor gives a new trigger. Both should let the player set a trigger off. Each comparison differs from the scored trigger in one thing, so one run answers both questions: is it the activator, is it the layer.

The person starts disabled so that nobody new stands about in the other 62 scenarios. A bystander changes what the game makes of a killing (VERIFY_LOG, the twelfth run), and those scenarios must stay what they were.

### Where things go

The builder does not know the room. It reads from the game's master where the console command `coc qasmoke` puts the player (the room's arrival marker, `COCMarkerHeading`) and which way the player then faces, and places everything from there:

| Reference | Ahead | To the right | Up |
|---|---|---|---|
| Person | 300 | 150 | 0 |
| Trigger | 600 | 200 to the left | 100 |
| Comparison trigger on the game's base | 600 | 200 | 100 |
| Comparison trigger on `L_ACTORZONE` | 950 | 0 | 100 |
| Object | 150 | 60 to the left | 20 |

Whether those spots are open floor is not known. It does not matter for the test, which moves the player by script and picks the object up by script; it matters for a person who walks in to look. The build output says where the arrival marker is and where each thing went, and the scenario reports where the player and each thing really are, so the two can be compared.

The builder refuses a trigger whose box holds, or nearly holds, the arrival point (someone already inside never "enters"), and two boxes that overlap. If the room has no arrival marker it places from the origin and says so.

## The quest: `TLM_Trial`

Not Start Game Enabled. Run Once. Started only by scenario 10.

| Stage | Set by | Meaning |
|---|---|---|
| 10 | `DefaultAliasOnTriggerEnter` on the `Trigger` alias | The player entered the placed trigger |
| 11 | The same script on the `TriggerGameBase` alias | The player entered the comparison trigger made on the game's own empty trigger |
| 12 | The same script on the `TriggerActorZone` alias | The player entered the comparison trigger on `L_ACTORZONE` |
| 20 | `DefaultAliasOnContainerChangedTo` on the `Object` alias | The player picked the placed object up |
| 100 | Scenario 10, at its end | Finished. Completes the quest |

No objectives, no log text. Each stage has its one item, as every stage of this project must (amendment A22).

| Alias | Filled with | Flags | Script |
|---|---|---|---|
| `Person` | `TLM_REF_TrialPerson` (forced reference) | Optional, Allow Disabled; display name `TLM_MSG_TrialPersonName` | none |
| `Trigger` | `TLM_REF_TrialTrigger` | Optional | `DefaultAliasOnTriggerEnter`, `StageToSet` = 10 |
| `TriggerGameBase` | `TLM_REF_TrialTriggerGameBase` | Optional | `DefaultAliasOnTriggerEnter`, `StageToSet` = 11 |
| `Object` | `TLM_REF_TrialObject` | Optional | `DefaultAliasOnContainerChangedTo`, `StageToSet` = 20 |
| `TriggerActorZone` | `TLM_REF_TrialTriggerActorZone` | Optional | `DefaultAliasOnTriggerEnter`, `StageToSet` = 12 |

Every alias is Optional on purpose: an alias that stays empty in the game is then reported by name, and the quest still starts. `Person` needs Allow Disabled because its reference starts disabled.

The two scripts on the aliases are the game's own. They are the same two the main quest's design relies on for the sealed dispatch, the ambush trigger and the town gate, where they have never yet had anything to act on.

For the trial each also has `ShowTraces` set, which the wiki describes as "Set to TRUE if you want the traces in this script to show up in the log". Whether the scripts as shipped still write anything then is not known. If they do, the run's report shows it: for scenario 10 it lists every line of the game's script log that names the trial's quest, and any other log a script wrote in that session.

The quest's own script, `TLM:PlacedTrial`, holds scenario 10 and nothing else.

## Scenario 10

`cqf TLM_Core RunSelfTest 10`, or unattended as below. One fresh session, like every scenario.

Scored, 18 checks:

1. the quest is not running before, and runs once started;
2. the `Person` alias holds a reference, it is an actor, it starts disabled, it is not dead, it is in the cell the player is in, and it is no longer disabled after `Enable`;
3. the `Object` alias holds a reference in the player's cell; the player has none of the item before; `Activate` by the player (which for an item means picking it up) leaves the player with one; and stage 20 is then set, not before;
4. the `Trigger` alias holds a reference; stage 10 is not set before; moving the player into the middle of the trigger sets it;
5. the quest is completed by its last stage.

Reported, not scored (lines beginning INFO):

- where the player begins, and where the person, the object and each trigger are, with their distances from the player;
- whether the person's and the object's 3D is loaded;
- what `Start` and `Activate` returned;
- how many things each trigger counts inside itself before and after the move;
- the two comparison triggers: whether entering each set its stage (11, 12). If ours fails and the one on the game's base works, the fault is in the activator the plugin makes; if the one on `L_ACTORZONE` works, it is the layer;
- if picking the object up did not set stage 20, the reference is moved into the player's inventory by `AddItem` and the result reported, which tells a pick-up that failed from a script that did not hear it.

At the end the player is moved back to where the scenario began.

**What it cannot check: the person's name.** The alias gives the reference a display name, but a script can only read a display name through a script extender (`GetDisplayName` is an F4SE function), and this project does not use one. A person has to look, and only once the unattended run has shown that the rest works:

1. `powershell -ExecutionPolicy Bypass -File tools\win\Start-TestGame.ps1`, and at the main menu `coc qasmoke` in the console, as in the runbook.
2. In the console: `cqf TLM_Core RunSelfTest 10`. Close the console and wait for the message box with the result. (Run by hand, the scenario does not close the game.)
3. The settler now stands to the front and right of where you arrived. Walk up and look at them: the name shown should be "Trial Settler". If it is "Settler", the display name did not take.

Do not save. Quit to the desktop afterwards.

## What it rests on

Looked up by name in `Fallout4.esm` when the plugin is built; none is hard-coded as a number:

| Name | Kind | If it is missing |
|---|---|---|
| `QASmoke` | Cell | Nothing is placed. The aliases stay empty and scenario 10 says so |
| `COCMarkerHeading` | Static | Everything is placed from the origin, and the build says so |
| `WorkshopNPC` | Actor | The person is not placed |
| `Caps001` | Item | The object has no world model |
| `XMarker` | Static | The player is not moved back at the end |
| `L_TRIGGER`, `L_ACTORZONE` | Collision layers | A trigger whose layer is missing is placed without one, and the build says so |
| `DefaultEmptyTrigger` | Activator | The comparison trigger is left out |

`WorkshopNPC`, `Caps001` and `XMarker` have been found in the real master before. The other five have not been looked up there yet. The names are from memory of the game's data, the wiki (`L_TRIGGER`) and forum posts that use them (`DefaultEmptyTrigger`, `L_ACTORZONE`, `COCMarkerHeading`); the first build on the PC shows whether they are right.

From the game itself: the scripts `DefaultAliasOnTriggerEnter` and `DefaultAliasOnContainerChangedTo`.

No script extender. No new dependency on the PC.

### Where each claim comes from

| Claim | Source |
|---|---|
| A trigger tells scripts when it is entered; its collision layer, "typically L_TRIGGER", decides by what; actors do | Creation Kit wiki, *OnTriggerEnter - ObjectReference* |
| `DefaultAliasOnTriggerEnter` sets `StageToSet` when the alias's reference is triggered, by the player only unless told otherwise | Wiki, *DefaultAliasOnTriggerEnter* |
| `DefaultAliasOnContainerChangedTo` sets `StageToSet` when the reference is picked up, by the player only unless told otherwise | Wiki, *DefaultAliasOnContainerChangedTo* |
| `Activate` does the "normal processing (i.e. picking up the object, opening the door, etc)" | Wiki, *Activate - ObjectReference* |
| `AddItem` with a reference moves that reference into the container | Wiki, *AddItem - ObjectReference* |
| `Start` is latent and returns whether the quest started | Wiki, *Start - Quest* |
| A message used as a name: "fill in the Title and leave the Message Text blank" | Wiki, *Message* |
| `GetDisplayName` needs F4SE | Wiki, *GetDisplayName - ObjectReference* |
| How a cell and its references are laid out in the file | The library that writes it (Mutagen), and the layout in xEdit's record definitions as remembered, not re-read for this work. The written bytes are checked against that layout by `tools/check_plugin_layout.py` |
| The library's box sizes are whole sizes, and the file holds half of each | Seen in the bytes the library wrote: a box given as 150 came out as 75. The builder now doubles what it hands over, and the check reads the bytes |

Not documented anywhere I could find, and assumed:

- that an alias is not filled with a disabled reference unless it has Allow Disabled. The plugin sets the flag, so the game's answer does not matter to the trial; the stand-in engine takes the cautious reading;
- that the player moved into a trigger by script "enters" it. If stage 10 is not set, the count of things inside the trigger after the move says whether the game saw the player in it.

## Implementation checklist

- [x] `Spec.cs`: the item with a borrowed model, the activator, the name message, the five placed references, the quest.
- [x] `Builder.cs`: model borrowing; the copy of the cell's record; the arrival marker; placing from it; the box, with its colour copied from one of the game's own box triggers when one is found; the collision layer by name; forced-reference aliases; alias display names. Ids for the placed references are given out with and without the master, so `formkeys.txt` never changes on the PC.
- [x] The build output says what was found and where everything went, including a count of which collision layers the game's own box triggers use (a sample of a few hundred), for comparison if ours does not work.
- [x] `Report.cs`, `SelfCheck.cs`: the written file is read back and compared with the spec, the references included; the cell's copy must be filed where the master files the cell and hold only this plugin's references.
- [x] `tools/check_plugin_layout.py`: the same from the bytes, without the library, with eight kinds of deliberate damage that must each be caught.
- [x] `tools/StandInMaster`: a stand-in test room, so that all of the above runs on Linux; and a bare room with nothing in it that the builder looks for.
- [x] `TLM:PlacedTrial` and scenario 10 in `TLM:SelfTest`.
- [x] `tools/papyrus_sim`: placed references, forced fills, triggers, picking up, and the game's two default alias scripts played from their documentation. `test_placed.py`.
- [x] `tools/win/Run-Scenarios.ps1`: scenario 10 in `basic` and `all`; an error in the game's script log now counts for this project when the scripts it happened in are ours, even if its own line does not name us.
- [ ] **Compile on the PC** (13 scripts; `PlacedTrial.psc` is new, `SelfTest.psc` changed).
- [ ] **Build against the real `Fallout4.esm`.** First use of the cell lookup, the arrival marker, the layer and the empty trigger on real data.
- [ ] **Run scenario 10 in the game.**
- [ ] Look at the person's name by eye.
- [ ] Open the plugin in the Creation Kit (checklist item 4 in VERIFY_LOG; it now has a cell and references to look at as well).

## Tests

On Linux, all in `tools/run_checks.sh`:

| What | Shows |
|---|---|
| Plugin built without a master | Nothing is placed, the aliases are empty and Optional, ids are still given out |
| Plugin built against the stand-in room | Five references, where the arrival marker and its heading put them; read back through the library and again from the bytes; the id file unchanged |
| Plugin built against a bare room | Placed from the origin; no collision layer; no comparison trigger; each said in the build output; the file still sound |
| Deliberate damage to the written file (12 kinds, 8 of them to the cell and its references) | Each is caught by the byte check |
| Scenario 10 on the stand-in engine | 18 passed, in the ordinary mode, with every call taking a frame, and shaken 25 ways |
| `test_placed.py`, 12 tests that each break one thing in the plugin or in how the game answers | The scenario fails on the check that is there for that thing, and still closes the game |
| `test_placed.py`, 15 tests of the stand-in's new rules | The rules do what `sim.py` says |
| The other 62 scenarios | Unchanged: 1,561 checks |
| The Windows chain against the stand-in PC | Build, compile (a stand-in compiler), install, scenario 10, report |

**What none of that shows.** The stand-in engine's rules for everything else have game runs behind them. Its rules for placed references, triggers and picking things up have none: they are the wiki's words and, where the wiki is silent, a cautious guess. A pass says the script, the plugin and those readings agree with each other. It says nothing about the game.

On the PC:

```powershell
git fetch origin; if ($LASTEXITCODE -eq 0) { git checkout feat/tlm-mq01-graybox; if ($LASTEXITCODE -eq 0) { powershell -ExecutionPolicy Bypass -File tools\win\Update-And-Run.ps1 -Install -Unattended -Scenarios 10,1,2,129-132 } }
```

The first two steps move the folder onto this branch, once; each step runs only if the one before it worked (rehearsed against a scratch copy: a branch that is not there, a fetch that fails and a switch that git refuses each end with nothing run). After that the usual command is enough.

About ten minutes. Scenario 10 runs first, so that a plugin the game cannot load shows at once. Scenario 1 says whether the two real quests still behave with the larger plugin. 2 and 129 to 132 are the short run that was already owed (the bystander experiment and the timer guard).

### Reading the result

| What comes back | What it means |
|---|---|
| The build stops in step 4 with an error | The builder met something in the real master it was not written for. Its message says what. Nothing was installed |
| Scenario 10 "NOT STARTED", or the game closes at once | The game did not take the plugin, most likely the cell's copy or a reference. Scenario 1 never having failed this way before points the same way |
| "the Person/Object/Trigger alias holds a reference" fails | The reference is not there, or the alias did not take it. The INFO lines of the others say which kind |
| The person is not in the player's cell, or absurdly far | The cell's copy landed somewhere other than the room |
| Stage 20 not set, and the `AddItem` line says it then was | `Activate` did not pick the object up; the default script is fine |
| Stage 20 not set either way | The default script did not act, or did not hear |
| Stage 10 not set, things inside the trigger = 0 | The game does not see the player in the box: the box, its layer or the activator. Compare with the two comparison triggers and with the layers the build output counted |
| Stage 10 not set, things inside = 1 | The trigger works; the default script did not act |
| Stage 10 not set, stage 11 set | Our activator is the fault |
| Stage 10 not set, stage 12 set | The layer is the fault: use `L_ACTORZONE` |
| None of 10, 11, 12 set | Something the three share: the box itself, the default script, or that a move by script is not "entering" |
| All 18 pass | Placed people, triggers and objects can be generated. The rough walk-through can be built this way |

## Rollback

The trial is a branch of its own. `main` and `feat/tlm-mq01-prebuild` are untouched, and the tag `mq01-logic-proof` still names the scripted proof.

- **On the PC, to go back to the plugin as it was:** `git checkout feat/tlm-mq01-prebuild`, then the usual `powershell -ExecutionPolicy Bypass -File tools\win\Update-And-Run.ps1 -Install -Unattended` rebuilds and installs it over the trial's. `tools\win\Uninstall-Dev.ps1` removes the test build altogether. Nothing outside Mod Organizer's `TheLastMeridian-Dev` mod and the `TLM-Dev` profile is written; the game's own files, and its test room, are as they were the moment the plugin is not loaded.
- **Saves:** the unattended sessions never save. A save made by hand with the trial loaded would carry its quest and references; do not keep one.
- **In the repository, to take the trial out again:** delete the entries marked "trial" in `Spec.cs` (item, activator, message, `Placed`, the quest `Trial` and its place in `Quests`, the `TLM_Trial` property of `TLM:SelfTest`), `scripts/Source/User/TLM/PlacedTrial.psc`, scenario 10's branch and property in `SelfTest.psc`, scenario 10 in the runner and the stand-in's lists, and `tools/papyrus_sim/test_placed.py`. The builder's placing code and the stand-in engine's rules can stay: with nothing in `Spec.Placed` they do nothing, and the rough walk-through needs them.
- **Ids:** 2083 to 2090 in `tools/PluginBuilder/formkeys.txt` stay given out. An id is never reused.

It must not ship. `TLM_Trial`, its records and the copy of `QASmoke` are development only, like the self-test.

## If it works

The same machinery places what *Six Rounds to Mercy* needs: the wreck, the ambush sight trigger, the town gate, the marshal's body with the dispatch, the caravan and the Cutters. Where they go is the next question, and the first real design decision of phase 2: the game's test room again, or a cell of the project's own built from a handful of the game's floor and wall pieces, which is what a player could actually walk through. That is for the owner to decide once this trial has reported.
