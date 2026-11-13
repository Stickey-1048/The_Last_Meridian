# The placed-content trial

Phase 2, first step. Branch `feat/tlm-mq01-graybox`. Self-test scenario 10.

**Status: ran in the game on 2026-11-13 and passed.** Scenario 10, with nobody at the keyboard: 17 of 17 checks, and both comparison triggers set their stages ([VERIFY_LOG.md](VERIFY_LOG.md), the thirteenth run). What the game showed is in [What the first run showed](#what-the-first-run-showed). Two things were changed afterwards and have **not** been compiled or run: the comparison triggers now leave the collision layer out, and the steps that move the player are allowed more time. Not done at all: a look at the plugin in the Creation Kit, and a look at the settler's name by eye.

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
| A copy of the record of the game's test room, `QASmoke` | A plugin puts something into a cell it does not own by carrying its own copy of that cell's record with the new references under it. Only the cell's record is copied. The game's own contents of the room stay in the game's master file: the library's copy leaves them out, the builder takes out and reports anything that comes along all the same, and the checks look again in the written file |
| `TLM_REF_TrialPerson` | A placed copy of the game's generic settler (`WorkshopNPC`), **initially disabled** |
| `TLM_REF_TrialTrigger` | A placed `TLM_ACTI_TrialTrigger` with a box reaching 150 units from its middle on each axis, on the collision layer `L_TRIGGER` |
| `TLM_REF_TrialTriggerGameBase` | The same box on the game's own empty trigger (`DefaultEmptyTrigger`), naming no collision layer, for comparison. Left out, and reported, if the game has no activator of that name |
| `TLM_REF_TrialTriggerNoLayer` | The same box on `TLM_ACTI_TrialTrigger` again, naming no collision layer, for comparison |
| `TLM_REF_TrialObject` | A placed `TLM_MISC_TrialObject` |

The five references are persistent, which a reference needs to be for a quest alias to point at it.

**Why two comparison triggers.** In the first run the comparisons were a box on the game's own empty trigger and a box on the layer `L_ACTORZONE`, and both worked, as the scored one did. The same build counted which layers the game's own box triggers name: none, for 405 of 407. So the comparisons now ask the question that is left: does a box of ours work with no layer named, on the game's activator and on the plugin's? If so, a trigger needs nothing but its box, and the walk-through's triggers will be written the way the game writes its own.

The person starts disabled so that nobody new stands about in the other 62 scenarios. A bystander changes what the game makes of a killing (VERIFY_LOG, the twelfth run), and those scenarios must stay what they were.

### Where things go

The builder does not know the room. It reads from the game's master where the console command `coc qasmoke` puts the player (the room's arrival marker, `COCMarkerHeading`) and which way the player then faces, and places everything from there:

| Reference | Ahead | To the right | Up |
|---|---|---|---|
| Person | 300 | 150 | 0 |
| Trigger | 600 | 200 to the left | 100 |
| Comparison trigger on the game's base, no layer | 600 | 200 | 100 |
| Comparison trigger on the plugin's base, no layer | 360 | 520 to the left | 100 |
| Object | 150 | 60 to the left | 20 |

The three triggers are the same distance from the arrival point (640 units), and the scenario brings the player back to where it began before each, so that each is entered the same way. A move by script over a longer distance may be handled differently by the game than a short one, and a difference between the three should say something about the one thing each differs in, not about how the player got there.

The first two triggers' spots were open floor in the first run. The third box then stood 200 ahead and 600 to the right, where the player came down on top of something; it has been moved. Whether the other spots are open floor is not known. It does not matter for the test, which moves the player by script and picks the object up by script; it matters for a person who walks in to look. The build output says where the arrival marker is, how far the room's own objects reach, where each thing went and whether that is within their reach seen from above; and the scenario reports where the player and each thing really are, so the two can be compared.

The builder refuses a trigger whose box holds, or nearly holds, the arrival point (someone already inside never "enters"), and two boxes that overlap. If the room has no arrival marker it places from the origin and says so.

## The quest: `TLM_Trial`

Not Start Game Enabled. Run Once. Started only by scenario 10.

| Stage | Set by | Meaning |
|---|---|---|
| 10 | `DefaultAliasOnTriggerEnter` on the `Trigger` alias | The player entered the placed trigger |
| 11 | The same script on the `TriggerGameBase` alias | The player entered the comparison trigger made on the game's own empty trigger, with no layer |
| 12 | The same script on the `TriggerNoLayer` alias | The player entered the comparison trigger of the plugin's own with no layer |
| 20 | `DefaultAliasOnContainerChangedTo` on the `Object` alias | The player picked the placed object up |
| 100 | Scenario 10, at its end | Finished. Completes the quest |

No objectives, no log text. Each stage has its one item, as every stage of this project must (amendment A22).

| Alias | Filled with | Flags | Script |
|---|---|---|---|
| `Person` | `TLM_REF_TrialPerson` (forced reference) | Optional, Allow Disabled; display name `TLM_MSG_TrialPersonName` | none |
| `Trigger` | `TLM_REF_TrialTrigger` | Optional | `DefaultAliasOnTriggerEnter`, `StageToSet` = 10 |
| `TriggerGameBase` | `TLM_REF_TrialTriggerGameBase` | Optional | `DefaultAliasOnTriggerEnter`, `StageToSet` = 11 |
| `Object` | `TLM_REF_TrialObject` | Optional | `DefaultAliasOnContainerChangedTo`, `StageToSet` = 20 |
| `TriggerNoLayer` | `TLM_REF_TrialTriggerNoLayer` | Optional | `DefaultAliasOnTriggerEnter`, `StageToSet` = 12 |

Every alias is Optional on purpose: an alias that stays empty in the game is then reported by name, and the quest still starts. `Person` has Allow Disabled because its reference starts disabled; whether the game needs the flag for a reference an alias is forced to is not documented (see below), and with it set the question does not arise.

The two scripts on the aliases are the game's own. They are the same two the main quest's design relies on for the sealed dispatch, the ambush trigger and the town gate, where they have never yet had anything to act on.

In the first run each also had `ShowTraces` set, which the wiki describes as "Set to TRUE if you want the traces in this script to show up in the log". The game took the property without complaint and wrote nothing, to the script log or anywhere else, so it is not set any more. The run's report still lists, for scenario 10, every line of the game's script log that names the trial's quest, and any other log a script wrote in that session.

The quest's own script, `TLM:PlacedTrial`, holds scenario 10 and nothing else.

## Scenario 10

`cqf TLM_Core RunSelfTest 10`, or unattended as below. One fresh session, like every scenario.

Scored, 17 checks, in this order:

1. the quest runs once started;
2. the `Person` alias holds a reference, it is an actor, it starts disabled, and it is not dead;
3. the `Object` alias holds a reference in the player's cell; the player has none of the item before; `Activate` by the player (which for an item means picking it up) leaves the player with one; and stage 20 is then set, not before;
4. the `Trigger` alias holds a reference; stage 10 is not set before; moving the player into the middle of the trigger sets it;
5. the person, enabled only now so that nobody stands near the triggers while they are tried, is no longer disabled and is in the cell the player is in;
6. the quest is completed by its last stage.

Reported, not scored (lines beginning INFO):

- where the player begins, and where the person, the object and each trigger are, with their distances from the player;
- whether the person's and the object's 3D is loaded;
- what `Start` and `Activate` returned;
- how many things each trigger counts inside itself before and after the move. A trigger counts things of any kind its layer lets in, and the room is full of loose items, so the number itself means little: what matters is whether it went up by one;
- the two comparison triggers: whether entering each set its stage (11, 12). Both leave the collision layer out. If the one on the game's activator works and the one on the plugin's does not, the plugin's activator needs a layer named; if neither works, a box of ours needs one whatever it stands on;
- if picking the object up did not set stage 20, the reference is moved into the player's inventory by `AddItem` and the result reported, which tells a pick-up that failed from a script that did not hear it.

The player is brought back to where the scenario began before each trigger and after the last.

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
| `L_TRIGGER` | Collision layer | The scored trigger is placed without one, and the build says so |
| `DefaultEmptyTrigger` | Activator | The comparison trigger is left out |

All of them were found in the real master on 2026-11-13 (`L_ACTORZONE` too, which the trial no longer uses).

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
| The library's box sizes are whole sizes, and the file holds half of each | Seen in the bytes the library wrote: a box given as 150 came out as 75. The builder now doubles what it hands over, and the check reads the bytes. UESP's file-format page for the game before this one says the same of the file ("Bounds / 2") |
| A box's reach can be in the file twice: in the primitive, and again as the reference's bound; the editor refuses a box where the two differ | UESP, *Skyrim Mod:Mod File Format/REFR* (fields XPRM, XMBO), for the game before this one; the library's Fallout 4 records have the same field. Whether a plain trigger carries the bound is not known, so the builder does as most of the game's own box triggers do: the build output counts them and says which way it went. Where it writes the bound, the byte check compares the two |
| A trigger's collision layer is stored as a number, the index of the layer's record | The same UESP page (field XTRI), and the library. The builder looks the layer up by name and stores its index |

Not documented anywhere I could find, and assumed:

- that an alias is not filled with a disabled reference unless it has Allow Disabled. The plugin sets the flag, so the game's answer does not matter to the trial; the stand-in engine takes the cautious reading;
- that the player moved into a trigger by script "enters" it. The nearest thing to a source was a note on the wiki of the game before this one, seen only as quoted in a search result, not read on the page: a trigger around a door's arrival marker fires for the player who comes through the door. **Seen in the game on 2026-11-13: it does.**

## Implementation checklist

- [x] `Spec.cs`: the item with a borrowed model, the activator, the name message, the five placed references, the quest.
- [x] `Builder.cs`: model borrowing; the copy of the cell's record; the arrival marker; placing from it; the box, with its colour copied from one of the game's own box triggers when one is found; the collision layer by name; forced-reference aliases; alias display names. Ids for the placed references are given out with and without the master, so `formkeys.txt` never changes on the PC.
- [x] The build output says what was found and where everything went, including a count of which collision layers the game's own box triggers use (a sample of a few hundred), for comparison if ours does not work.
- [x] `Report.cs`, `SelfCheck.cs`: the written file is read back and compared with the spec, the references included; the cell's copy must be filed where the master files the cell and hold only this plugin's references.
- [x] `tools/check_plugin_layout.py`: the same from the bytes, without the library, with sixteen kinds of deliberate damage that must each be caught.
- [x] `tools/StandInMaster`: a stand-in test room, so that all of the above runs on Linux; the same with its text in strings files, as the game's master has it; one whose own triggers carry no bound; and a bare room with nothing in it that the builder looks for.
- [x] The name of the room. The game keeps a cell's name apart from the master, in strings files; this plugin's copy of the cell needs it as text. The builder reads it once, puts it into the copy and says what it read. If the strings cannot be read the copy has no name, the build says so, and nothing stops.
- [x] `TLM:PlacedTrial` and scenario 10 in `TLM:SelfTest`.
- [x] `tools/papyrus_sim`: placed references, forced fills, triggers, picking up, and the game's two default alias scripts played from their documentation. `test_placed.py`.
- [x] `tools/win/Run-Scenarios.ps1`: scenario 10 in `basic` and `all`; an error in the game's script log now counts for this project when the scripts it happened in are ours, even if its own line does not name us.
- [x] **Compile on the PC.** Done 2026-11-13.
- [x] **Build against the real `Fallout4.esm`.** Done 2026-11-13: everything looked up was found, and the read-back check passed.
- [x] **Run scenario 10 in the game.** Done 2026-11-13: 17 of 17.
- [ ] Run it again with the comparison triggers that name no layer.
- [ ] Find out why the settler did not stay where it was placed, and what makes a placed person stay.
- [ ] Look at the person's name by eye.
- [ ] Open the plugin in the Creation Kit (checklist item 4 in VERIFY_LOG; it now has a cell and references to look at as well).

## Tests

On Linux, all in `tools/run_checks.sh`:

| What | Shows |
|---|---|
| Plugin built without a master | Nothing is placed, the aliases are empty and Optional, ids are still given out |
| Plugin built against the stand-in room | Five references, where the arrival marker and its heading put them; read back through the library and again from the bytes; the id file unchanged |
| Plugin built against a bare room | Placed from the origin; no collision layer; no comparison trigger; each said in the build output; the file still sound |
| Plugin built against a master with its text in strings files, with and without those files | The room's name is carried into the copy; without the files the copy has none and the build says so |
| Plugin built against a master whose own triggers carry no bound | The builder writes none either |
| Deliberate damage to the written file (20 kinds, 16 of them to the cell, its references and the aliases that point at them) | Each is caught by the byte check |
| Seven faults put into the builder, one at a time | Each is caught by the builder's own read-back check, which is the one that runs on the PC |
| Scenario 10 on the stand-in engine | 17 passed, in the ordinary mode, with every call taking a frame, and shaken 25 ways |
| `test_placed.py`, 12 tests that each break one thing in the plugin or in how the game answers | The scenario fails on the check that is there for that thing, and still closes the game |
| `test_placed.py`, 15 tests of the stand-in's new rules | The rules do what `sim.py` says |
| Eight faults put into `TLM:PlacedTrial`, one at a time | Each makes scenario 10 fail on the stand-in engine |
| The other 62 scenarios | Unchanged: 1,561 checks |
| The Windows chain against the stand-in PC | Build, compile (a stand-in compiler), install, scenario 10, report |

**What none of that shows.** (Written before the first run; the run has since confirmed the stand-in's rules for triggers, picking up and the two default scripts, and corrected nothing in them. What it does not model is where a placed person ends up.) The stand-in engine's rules for everything else have game runs behind them. Its rules for placed references, triggers and picking things up have none: they are the wiki's words and, where the wiki is silent, a cautious guess. A pass says the script, the plugin and those readings agree with each other. It says nothing about the game.

On the PC, the first run was started with this, which also moved the folder onto the branch, once:

```powershell
git fetch origin; if ($LASTEXITCODE -eq 0) { git checkout feat/tlm-mq01-graybox; if ($LASTEXITCODE -eq 0) { powershell -ExecutionPolicy Bypass -File tools\win\Update-And-Run.ps1 -Install -Unattended -Scenarios 10,1,2,129-132 } }
```

It took five minutes: the build, then seven sessions of about half a minute, 87 seconds for scenario 10. From now on the usual command is enough, with the scenarios wanted:

```powershell
powershell -ExecutionPolicy Bypass -File tools\win\Update-And-Run.ps1 -Install -Unattended -Scenarios 10,2
```

### Reading the result

| What comes back | What it means |
|---|---|
| The build stops in step 4 with an error | The builder met something in the real master it was not written for. Its message says what. Nothing was installed |
| Scenario 10 "NOT STARTED" | No game appeared after Mod Organizer was started. That is about Mod Organizer or Steam, as on 2026-11-13, not about the plugin |
| Scenario 10 "NO RESULT", with "the game ran, but the core quest never started" or "the game wrote no script log", and "STOPPED EARLY" under the table | The game started and never got as far as the test room with the plugin running: it closed, or sat at its menu until the runner closed it. Most likely it did not take the plugin, and the cell's copy or a reference is the first suspect, since this never happened before they were added |
| Scenario 10 "UNFINISHED" | The scenario began and the game went away under it. The last STEP line in the report says what it was doing |
| "the Person/Object/Trigger alias holds a reference" fails | The reference is not there, or the alias did not take it. The INFO lines of the others say which kind |
| The person or the object is not in the player's cell, or absurdly far | The cell's copy landed somewhere other than the room |
| Stage 20 not set, and the `AddItem` line says it then was | `Activate` did not pick the object up; the default script is fine |
| Stage 20 not set either way | The default script did not act, or did not hear |
| Stage 10 not set, and the trigger's count of things inside did not go up | The game does not see the player in the box: the box, its layer or the activator. Compare with the two comparison triggers and with the layers the build output counted |
| Stage 10 not set, and the count went up by one | The trigger works; the default script did not act |
| The count was already high before the move, or the player was within 150 of the trigger's middle before it | The player began inside the box, or loose things are in it. If the build placed from the origin (no arrival marker), move the boxes |
| Stage 10 not set, stage 11 set | Our activator is the fault |
| Stage 10 not set, stage 12 set | The layer is the fault: use `L_ACTORZONE` |
| None of 10, 11, 12 set | Something the three share: the box itself, the default script, or that a move by script is not "entering" |
| All 17 pass | A placed trigger and a placed object can be generated and drive a quest, and a placed person can be found and switched on. Read the INFO line about the person's 3D before concluding that the person is really standing there: that is reported, not scored |

## Rollback

The trial is a branch of its own. `main` and `feat/tlm-mq01-prebuild` are untouched, and the tag `mq01-logic-proof` still names the scripted proof.

- **On the PC, to go back to the plugin as it was:** `git checkout feat/tlm-mq01-prebuild`, then the usual `powershell -ExecutionPolicy Bypass -File tools\win\Update-And-Run.ps1 -Install -Unattended` rebuilds and installs it over the trial's. `tools\win\Uninstall-Dev.ps1` removes the test build altogether. Nothing outside Mod Organizer's `TheLastMeridian-Dev` mod and the `TLM-Dev` profile is written; the game's own files, and its test room, are as they were the moment the plugin is not loaded.
- **Saves:** the unattended sessions never save. A save made by hand with the trial loaded would carry its quest and references; do not keep one.
- **In the repository, to take the trial out again:** delete the entries marked "trial" in `Spec.cs` (item, activator, message, `Placed`, the quest `Trial` and its place in `Quests`, the `TLM_Trial` property of `TLM:SelfTest`), `scripts/Source/User/TLM/PlacedTrial.psc`, scenario 10's branch and property in `SelfTest.psc`, scenario 10 in the runner and the stand-in's lists, and `tools/papyrus_sim/test_placed.py`. The builder's placing code and the stand-in engine's rules can stay: with nothing in `Spec.Placed` they do nothing, and the rough walk-through needs them.
- **Ids:** 2083 to 2090 in `tools/PluginBuilder/formkeys.txt` stay given out. An id is never reused.

It must not ship. `TLM_Trial`, its records and the copy of `QASmoke` are development only, like the self-test.

## What the first run showed

The thirteenth run, 2026-11-13, commit `3c7ac5f`; the whole record is in [VERIFY_LOG.md](VERIFY_LOG.md).

**It works.** The game took the plugin's copy of the room's record and the five references under it. The quest started when asked, and each of its aliases held the reference it is forced to. The object, which only borrows the path of one of the game's models, was there to be seen and picked up, and picking it up set its stage through the game's own script. The player, moved into a box, was counted by the box and set its stage through the game's own script, for all three recipes tried. Every reference was where the builder had put it, to the last digit the game prints, and the player arrives exactly at the room's arrival marker: the arithmetic of "so far ahead, so far to the right" is right.

What it also showed, which matters for what is built next:

| What | Seen | So |
|---|---|---|
| The game's own triggers name no collision layer | 405 of 407 box triggers looked at in the game's master | A trigger of ours probably needs none either; the two comparison triggers now ask |
| The settler did not stay where it was placed | Enabled, it stood 489 units from its spot within the same second | People are the open question. The game's settler belongs to the workshop system and brings that system's packages and script; whether those moved it is not known |
| A scripted move puts the player on the floor, or on whatever stands at that spot | Height 0 at two spots; on top of something at the third | Two spots of open floor are known: 600 ahead of the arrival point, 200 to either side. The room's own objects lie between (-5024, -3776) and (-832, 2176); it is about 4,200 by 5,950 units and called 'Tunnels' |
| A scripted move of the player can take long | Between a second and 38 seconds, for the same distance | Fine for a test, with a generous limit. Nothing a player would meet should depend on it |
| The default scripts' `ShowTraces` | Taken, and nothing written | Not worth setting |

## What comes next

Triggers and objects written by the builder can drive a quest. That is two of the three things a rough walk-through of *Six Rounds to Mercy* is made of. The third is people who stand where they are put, can be told apart, and can be "talked to" (in the rough version: activated, with a message box for the conversation). So the next step is a trial of people, small like this one, before anything is laid out.

After that comes the first real design decision of phase 2, and it is the owner's: **where the walk-through stands.** The game's test room again, which is known to load and has a floor, light and paths for people to walk, but is full of the game's own things; or a cell of the project's own, built from a handful of the game's floor and wall pieces, which is what a player could actually walk through but needs a floor, light and, for people to move in it, a navigation mesh, none of which the builder has ever written.
