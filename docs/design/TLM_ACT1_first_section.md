# Act I, first section: a rough cut a person can walk through

Branch `feat/tlm-mq01-graybox`. Self-test scenario 12, and one command to play it by hand.

**Status: built and checked on the stand-in engine. Nothing here has been compiled by the Papyrus compiler or run in the game.** The pieces it is made of have each run in the game (placed people who stay, activation that reaches a script, triggers, objects that are picked up: [VERIFY_LOG.md](VERIFY_LOG.md), the thirteenth and fourteenth runs). This is the first time they are put together, and the first thing in the project a person is meant to play. What is new to the game in it is listed under [What the game has not been asked yet](#what-the-game-has-not-been-asked-yet).

## What it is

*Six Rounds to Mercy* and its side matter *Signed Clean*, from the wreck to Sheriff Pritchard's hand-off, with the people of the wreck, the road and Mercy Crossing standing in the game's test room and the real quests `TLM_MQ01` and `TLM_SQ01` running underneath. The quests' rules are the ones the logic model and the 64 earlier scenarios have proved. What is new is everything a player touches: thirteen named people, what they say, the papers that can be read, the things that can be picked up or examined, and the two places that matter (where the ambush is seen from, and the town gate).

It is a **rough cut**. The room is the game's own test room, the people wear the faces and clothes of the game's settlers, the distances are a few steps where the story has hours, and a conversation is a box with buttons. It is for finding out whether the chapter works as a sequence of things to do, and for having something to look at.

What it is not: dialogue with voices and a camera; a place built for the story; combat that has been tuned; anything from Chapter 2 on.

## How it is put together

**The quests are not changed**, neither their rules nor their records. `TLM_MQ01` and `TLM_SQ01` keep their aliases unfilled, as in every run so far. A development quest, `TLM_A1`, holds the placed people and things in aliases of its own, and its script (`TLM:Act1Walk`) **puts each into the alias of the real quests that is meant for it** with `ForceRefTo`, exactly as the test scenarios do with their stand-ins. So scenarios 1 to 11 and the 53 matrix cases see what they have always seen.

**Everything placed starts switched off** and is switched on only by that script. Nobody new stands about in any other scenario. The two boxes (the place the ambush is seen from, the town gate) are switched on last, when the people are there: a player who wandered into an ambush that was not there yet would start its clock for nothing.

**The player's choices are boxes.** Activating a person runs `TLM:Act1Talk` on that person's alias in `TLM_A1`, which only says who was activated. `TLM:Act1Walk` looks at where the two quests stand, shows the line that fits as a message box, and sets the stage that goes with the button pressed. The buttons are the short answers of the two designs, or a plain word for "go on"; nothing is written out for the player to say beyond them. Every button sets a stage the quest scripts already guard, so a box cannot do anything the rules do not allow.

Three small things are given by `TLM:Act1Walk` and are not known to the quests: Nell Fenwick's thanks (30 caps, once), the share of a deal with Reese Dunmore (20 caps, only if the deal is what the quest then made of it), and six rounds with the marshal's revolver.

## The cast

All are actors of the plugin's own: copies of the game's settler with no packages, no script and no default package list, which is what stood still on 2026-11-13. Three more things are done to each copy, all new and untried in the game:

- **Looks.** The game's settler draws its looks from a list of settlers, one at random for every person placed. Each copy is pointed at one settler of that list, of the sex the table gives: the first man listed gets the first man of the list (in the order of their ids), the second the second, and round again if the people outnumber the faces (the build says when). Whatever else the game's settler takes from that list (what it wears and carries among it), the copy takes from the same one settler.
- **Faction.** Each is in one faction of the plugin's own and in none of the game's: the town in `TLM_Fac_MercyCrossing`, the caravan in `TLM_Fac_Caravan`, the gang in `TLM_Fac_Cutters`. The game's factions decide who takes whose side in a fight and whose law a blow breaks; with those of the settler on everybody, the caravan would have been the gang's ally. (The dead marshal keeps the settler's: he is nobody's ally any more.)
- **Temper.** Nobody starts a fight, nobody runs from one, and nobody joins one, except the Cutters, who join a fight one of their own is in. A fight begins when the quest says so (stage 37) or when the player starts one.

| Record | Name | Stands in for | Looks | Faction |
|---|---|---|---|---|
| `TLM_NPC_SHERIFF_MERCY` | Owen Pritchard | Sheriff, Old Warden | male | town |
| `TLM_NPC_GUNSMITH_MERCY` | Ada Pike | Gunsmith | female | town |
| `TLM_NPC_MERCHANT_MERCY` | Silas Vane | Merchant | male | town |
| `TLM_NPC_PHYSICIAN_MERCY` | Miriam Keene | Physician | female | town |
| `TLM_NPC_DEPUTY_MERCY` | Jonah Talbot | Deputy at the gate | male | town |
| `TLM_NPC_FREIGHT_MERCY` | Corwin Haskell | Freight agent | male | town |
| `TLM_NPC_MARSHAL_DEAD` | Tobias Gantt | Rail marshal, dead in the wreck | male | (the settler's) |
| `TLM_NPC_CARAVAN_MASTER` | Nell Fenwick | Caravan owner | female | caravan |
| `TLM_NPC_CARAVAN_DROVER` | Abel Rudd | Her hired hand | male | caravan |
| `TLM_NPC_CUTTER_LEAD` | Reese Dunmore | Leads the Tellico Cutters | male **[PROPOSED]** | gang |
| `TLM_NPC_CUTTER_01` to `_03` | Tellico Cutter | Three of the gang | male, female, male **[PROPOSED]** | gang |

The names are those of the naming registry and of the Chapter 1 design; six of them are still proposals there (design question Q8).

In `TLM_A1` the townsfolk whom the real quests hold in no alias, or in one without a flag (Talbot, Pike, Vane, Keene, Haskell), are Protected: only the player can kill them. Pritchard is Essential, the caravan hands and the Cutters Protected, by the main quest's own aliases, as designed.

## Where things stand

Placed from the test room's arrival point, as in the trial: so many units ahead, to the right, and up. Three corners: the wreck to the left, the road ahead, the town to the right. All within some 750 units of where the player arrives, on and around the five spots known to be floor.

| What | Reference | Ahead | Right | Up |
|---|---|---|---|---|
| **The wreck** | | | | |
| Tobias Gantt, dead | `TLM_REF_A1_Marshal` | 230 | -420 | 0 |
| The sealed dispatch, beside him | `TLM_REF_A1_Dispatch` | 190 | -360 | 10 |
| His revolver | `TLM_REF_A1_Revolver` | 260 | -340 | 10 |
| His journal | `TLM_REF_A1_Journal` | 200 | -470 | 10 |
| The maintenance ledger | `TLM_REF_A1_Ledger` | 330 | -600 | 10 |
| The brake shoes | `TLM_REF_A1_BrakeShoes` | 360 | -520 | 12 |
| The draw-bar | `TLM_REF_A1_DrawBar` | 450 | -480 | 12 |
| **The road** | | | | |
| The place the ambush is seen from (a box, 100 each way) | `TLM_REF_A1_AmbushSight` | 300 | -150 | 100 |
| The middle of the ambush (a marker) | `TLM_REF_A1_AmbushCenter` | 540 | -200 | 0 |
| The wagon's cargo | `TLM_REF_A1_Wagon` | 520 | -330 | 0 |
| Nell Fenwick | `TLM_REF_A1_Nell` | 600 | -200 | 0 |
| Abel Rudd | `TLM_REF_A1_Abel` | 640 | -320 | 0 |
| Reese Dunmore | `TLM_REF_A1_Dunmore` | 480 | -180 | 0 |
| Three Cutters | `TLM_REF_A1_Cutter1` to `3` | 520, 420, 560 | -80, -60, -260 | 0 |
| **The town** | | | | |
| The town gate (a box, 100 each way) | `TLM_REF_A1_TownGate` | 300 | 150 | 100 |
| Jonah Talbot | `TLM_REF_A1_Talbot` | 380 | 260 | 0 |
| Owen Pritchard | `TLM_REF_A1_Pritchard` | 600 | 200 | 0 |
| Ada Pike | `TLM_REF_A1_Pike` | 700 | 300 | 0 |
| Silas Vane | `TLM_REF_A1_Vane` | 700 | 120 | 0 |
| Miriam Keene | `TLM_REF_A1_Keene` | 520 | 330 | 0 |
| Corwin Haskell | `TLM_REF_A1_Haskell` | 460 | 420 | 0 |
| The notice board | `TLM_REF_A1_NoticeBoard` | 480 | 180 | 12 |
| The stove | `TLM_REF_A1_Stove` | 600 | 400 | 12 |
| The caravan yard (a marker) | `TLM_REF_A1_CaravanYard` | 620 | 320 | 0 |

Whether every one of these spots is open floor is not known: five places in the room are. Scenario 12 asks the game's navigation mesh about each person's spot and reports it, and whoever plays it will see.

## The things

| Record | What it is | Looks like (the first of these the game has) |
|---|---|---|
| `TLM_MISC_Dispatch` | The sealed rail dispatch. Picking it up sets stage 20 | Folder, Clipboard |
| `TLM_BOOK_MarshalLog`, `TLM_BOOK_RailMaintLedger` | The journal and the ledger. Activated, the game opens them to be read | One of the game's notes (below) |
| The game's own revolver | The marshal's. Picking it up sets stage 15, and the player then has six rounds for it | Itself: .44 Pistol, Pipe Revolver, 10mm Pistol |
| `TLM_ACTI_BrakeShoes`, `TLM_ACTI_DrawBar` | Examined, each shows its box and counts as evidence | Hubcap, Gears; Connecting Rod, Adjustable Wrench, Wrench |
| `TLM_ACTI_NoticeBoard`, `TLM_ACTI_Stove` | Where the pages can be posted; where the ledger can be burned | Clipboard, Folder; Hot Plate, Cooking Pot |
| `TLM_CONT_WagonCargo` | The wagon's cargo, with 40 caps in it. Emptied when the Cutters loot it | Wooden Crate, Crate, Steamer Trunk, Trunk, Suitcase, Toolbox |
| `TLM_TRIG_AmbushSight`, `TLM_TRIG_TownGate` | The two boxes. No model | |

Each "looks like" is a model **borrowed by its path**, as the trial's object borrowed the bottle cap's: the plugin names the game's own file and nothing is copied. The things are looked up by **the name a player sees**, because the names the game uses inside are not known here and a guess that misses costs a run. If the game has none of the names, the thing looks like a bottle cap, and the build says so. The build output lists what each name found.

The two papers take after **one of the game's notes**: the model that most of the game's books lie in the world as, and of the books that use it a plain one. From it they take the model, the picture a note is read on, and its sounds, all by name.

A game started in the test room has nothing on the player's arm. The set-up gives the player the game's own (`Pipboy`), so that the quest's entries can be read.

## What people say

All of it provisional, and all of it other people's words. The player's part is a button. Lines marked *design* are from the Chapter 1 design (section 8) and the Signed Clean design (sections 4 and 6); the rest are new and marked. "Continue" and "(Say nothing)" are not speech.

### Reese Dunmore, at the wagon

Only while nothing has been settled and the Cutters have not turned on the player. Speaking to him counts as meeting the ambush.

> "Keep walking. Or stay and pick up a share." *(design)*

| Button *(all design)* | What happens |
|---|---|
| "Pritchard hangs road-takers. Leave." | A coin is tossed, for want of a speech check. Heads: "Not for one wagon. We're gone." **[NEW]**, the Cutters break and the wagon is saved (stage 31). Tails: "Then you're in the way." **[NEW]**, and they turn on the player (stage 37) |
| "Let them go." | "Then you're in the way." They turn on the player (stage 37) |
| "What kind of share?" | "Half the cargo. The drover won't be a problem." *(design)* Then "Done.": "Smart. Stand clear." **[NEW]**, the deal (stage 33) and 20 caps; or "No.": they turn on the player (stage 37) |
| "Not my business." | Nothing. The quest's own rules for walking on apply |

Afterwards, if he lives: "We're done here. Walk on." **[NEW]**

### Nell Fenwick, Abel Rudd, the Cutters

| Who, and how it stands | Says | Buttons |
|---|---|---|
| Nell, nothing settled | "They want the wagon. Don't make it worse." **[NEW]** | |
| Nell, wagon saved | "They'd have had the wagon and Abel both. Take this. It's what I can spare." **[NEW]** | "Take it." (30 caps, once) / "Keep it." / "Who hit you?" ("Tellico Cutters. Reese Dunmore's lot." **[NEW]**, and the offer again) *(buttons: design)* |
| Nell, after that | "We'll be at the yard in Mercy Crossing. I won't forget it." **[NEW]** | |
| Nell, walked past | "You watched. You kept walking." *(design)* | "I couldn't." / "Not my fight." / (Say nothing). No effect, as designed |
| Nell, a share taken or the caravan shot at | A line at the edge of the screen: she looks through the player and says nothing *(design: she refuses to talk)* | |
| Nell, never met | "They took the wagon and they killed Abel. Nobody came." **[NEW]** | |
| Abel, nothing settled | "Don't look at me. Look at them." **[NEW]** | |
| Abel, wagon saved | "Thought that was the end of me. Obliged." **[NEW]** | |
| A Cutter, nothing settled | "Talk to Dunmore." **[NEW]** | |

### Sheriff Owen Pritchard

| Where things stand | He says | Buttons |
|---|---|---|
| No dispatch yet | "Gantt's train never reached us. Where's his case?" *(design)* | "I haven't looked." / "Lost it." / "I'll go back for it." *(design)* Then: "Six hours east at the wreck. I'll mark it." *(design)* No stage |
| Carrying the dispatch | "Off the Tellico wreck. That's Tobias Gantt's case you're carrying." *(design)* | "Hand over the dispatch" (stage 50) / "Not yet." *(design)* |
| Delivered, wagon saved | "The line keeps losing marshals. Word is Nell Fenwick's wagon got through. Obliged." *(design)* | |
| Delivered, walked past | "... Abel Rudd's dead on the Tellico road. Nell Fenwick says someone watched it happen." *(design)* | "I watched." (51) / "I never saw it." (52) / (Say nothing) |
| Delivered, a share taken, Nell alive | "... Nell Fenwick's at Miriam Keene's clinic. Her account is different from the one you'll give me." *(design)* | "I took a share." (53) / "The Cutters forced it." (54) / "She's lying." (55) / (Say nothing) |
| The same, and the one left to speak is Abel | "... Abel Rudd's at Miriam Keene's clinic. His account is different from the one you'll give me." **[NEW]** | The same, with "He's lying." (55) |
| Delivered, nobody left to say | "... Two dead on the Tellico road and no one to say how." *(design)* | |
| Delivered, never met the wagon | "... Fenwick's wagon was hit on the Tellico road, and you came in by it." **[NEW]** | |
| Delivered, Nell dead otherwise | "... Nell Fenwick's wagon never came in." **[NEW]** | |
| Then, in the same breath | "Greenwater's food has gone short. Red Hollow's sealed the mine. Iron Junction's rails are being cut. Pick one. I don't have the people for all three." *(design)* | "Continue" (stage 60, which completes the chapter) |
| After that | "Greenwater, Red Hollow or Iron Junction. Pick one." **[NEW]** | |

Whenever the side quest's case can be presented and nothing has been done with it, his box (before the dispatch, with it, and after the chapter) has one button more: "There's something else from that train." *(design)* It reports the ledger to him (side quest stage 41): "Show me. I'll take copies and send word up the line." **[NEW]**

### The town

| Who | When | Says |
|---|---|---|
| Ada Pike | Otherwise | "Pike. I fix what shoots. Forty-fours are scarce, so make yours count." **[NEW]** |
| Ada Pike | With the ledger found and nothing done with it | "They used to buy shoes off me every season. Haven't taken a pair since spring. I kept the count. Here, look." *(design)* Buttons: "Look at her parts book" (side quest stage 14) / "Leave it" |
| Ada Pike | After that | "The count's the count. I don't know who wrote yours." **[NEW]** |
| Silas Vane | Otherwise | "Vane. If it came down the line, I can price it." **[NEW]** |
| Silas Vane | The case presentable, nothing done with it | "Paper like this makes trouble for everyone. I'll take it off your hands." *(design)* Buttons: "Sell him the ledger and the journal" (side quest stage 45) / "Keep them" |
| Silas Vane | After buying | "Paid in full. Good day to you." **[NEW]** |
| Miriam Keene | Otherwise | "Clinic's open. If you're bleeding, sit. If you're not, don't touch anything." **[NEW]** |
| Miriam Keene | In town, Nell alive after a bad road | "Nell Fenwick's on the cot. She'll mend. Leave her be." **[NEW]** |
| Keene and Pike | After Haskell was named | "Corwin signed for freight. That's all he did." *(design)* |
| Jonah Talbot | Before the dispatch is delivered | "Deputy Talbot. Keep your iron holstered inside the posts." **[NEW]** |
| Jonah Talbot | After | "Sheriff's got your paper. He'll want a word more, I'd reckon." **[NEW]** |
| Corwin Haskell | Always | "Freight's signed for at the shed. Line 14's run nothing since the wreck." **[NEW]** |

The notice board, the stove, the brake shoes and the draw-bar show the boxes they always had (`TLM_MSG_PublishChoice`, `TLM_MSG_BurnLedger`, `TLM_MSG_E1`, `TLM_MSG_E2`), through the side quest's own alias scripts.

Nothing said names the Deep, the Charter or MERIDIAN, and nobody shows Silas Vane guilty or innocent. A test holds the lines to that.

## The quests underneath

Unchanged. For reference, what each thing a player does sets:

| The player | Sets |
|---|---|
| Picks up the dispatch | `TLM_MQ01` 20, by the game's script on the alias |
| Picks up the revolver | 15 |
| Walks into the place the ambush is seen from, speaks to Dunmore, or starts a fight | 30 |
| Answers Dunmore | 31, 33 or 37; or kills, or walks on, and the quest's own rules decide |
| Walks through the town gate | 40 |
| Hands over the dispatch | 50 (and 40, if the gate was walked round) |
| Answers Pritchard | 51 to 55, then 60, which sets 100 |
| Picks up the ledger, the journal | `TLM_SQ01` 10, 13 |
| Examines the brake shoes, the draw-bar; looks at Pike's book | 11, 12, 14 |
| Reports, posts, sells, burns | 41 to 46 |

The quest's clock is the design's: once the ambush is live, ninety seconds without a fight or a settlement and the player "kept walking". It does not run while a box is open.

## Scenario 12, with nobody at the keyboard

`TLM:Act1Walk.Audit`. It cannot press a button, and no box may open (a box waits for an answer, and neither a script's wait nor a timer counts time while one is open: the run would never end). So it checks what is placed and then walks one road through the chapter by doing what the buttons would do. 42 checks, among them:

1. the development quest starts and holds every placed reference (the revolver aside: the chapter allows there to be none);
2. each of the 26 aliases of the two real quests holds the reference put into it;
3. everybody is there within five minutes of being switched on, the marshal dead and the others alive;
4. six seconds later every living person stands within 64 units of where it was placed;
5. the dispatch, picked up, sets stage 20; the ledger and the journal, moved into the player's inventory, set the side quest's 10 and 13 (they are moved by script: activating a book opens it to be read); the revolver, picked up, sets 15, and the player has six rounds or more;
6. the player, moved into the place the ambush is seen from, sets stage 30;
7. the Cutter lead killed by the player sets 31, and the outcome is "saved";
8. the player, moved through the town gate, sets stage 40: the Cutters are gone, Nell Fenwick is counted alive at Mercy;
9. stage 50 as the hand-over sets it: the objective is completed, the dispatch gone, the town's regard 2, the debrief the "saved" one; stage 60: the chapter is completed;
10. the side quest: Pike's book as her button sets it (14), then reported as Pritchard's button does (41): the evidence level is 2, the outcome "reported", the yard alerted, the quest completed.

Reported and not scored: how long each person took to appear; whether the player is in combat at three points (the killing among them); and, last, what the navigation mesh answers about each person's spot.

## Playing it by hand

```powershell
powershell -ExecutionPolicy Bypass -File tools\win\Play-Act1.ps1
```

brings the folder up to date, compiles, builds and installs, starts the game through Mod Organizer in the test profile, and has the game enter the test room. A few seconds later the section is set up; when the line "Act I, first section. The wreck is to your left, the road ahead, Mercy Crossing to your right." appears at the edge of the screen, everybody is there. Nothing is scored and the game stays open until it is quit from its own menu. The window then collects which stages were set, in what order, and what the script log says of the section. What to look for is in [the runbook](TEST_RUNBOOK.md).

From the console instead, in the test room of a fresh session: `cqf TLM_A1 Begin`.

## What the game has not been asked yet

Each of these is new to the game in this cut. Scenario 12 or the first play will say which hold.

| What | Where it would show |
|---|---|
| A script property that is a list of aliases (some of another quest), and one that is a list of text | Scenario 12's first checks |
| Arrays made by a script (`new float[...]`), `EnableNoWait`, `Utility.RandomInt`, `EquipItem` | Compiling; scenario 12; play |
| `ForceRefTo` for a thing (it has run for actors), and the game's own alias scripts on an alias filled that way | Scenario 12, checks 2 and 5 |
| A placed actor that starts dead, held by an alias | Scenario 12, check 3 (if not, the script kills him and goes on) |
| A copy of the settler pointed at one settler for its looks, in a faction of the plugin's own, with a temper set | Scenario 12 (do they stay; is anybody in a fight); play (do they look like the same person each time) |
| How long thirteen people take to appear, switched on side by side | Scenario 12's INFO lines |
| What the other three Cutters, the caravan and the town do when the player kills the Cutter lead | Scenario 12's INFO lines; play |
| A book, a weapon and a container placed by the plugin; activators that borrow an item's model | Play (can they be seen, read, picked up, opened) |
| A message box with buttons, and that the button's number is its place in the message | Play |
| Whether the things found by name are what they were meant to be | The build output; play |

## Implementation checklist

- [x] `SpecAct1.cs`: the thirteen actors; the things; the lines as messages; the placed references; `TLM_A1` with its aliases and `TLM:Act1Talk` on the speakers'. `Spec.cs`: the dispatch's look, the papers' look, the two scripts on `TLM_Core` given the new quest.
- [x] `Builder.cs`: an actor's looks, faction and temper; a placed actor that starts dead; things found by the name a player sees; a note to take after; activators and a container with a borrowed model; script properties that are an alias of another quest, a list of aliases, a list of text.
- [x] `Report.cs`, `SelfCheck.cs`, `check_plugin_layout.py`: the same read back and checked, the last from the bytes, with 35 kinds of deliberate damage.
- [x] `tools/StandInMaster`: a list of settlers to draw looks from, and things with names a player sees.
- [x] `TLM:Act1Talk`, `TLM:Act1Walk`; scenario 12 in `TLM:SelfTest` and the hand-played start in `TLM:Core`.
- [x] `tools/papyrus_sim`: arrays, a box that is answered (for tests), `EnableNoWait`, `RandomInt`, a person pressing the button; `test_act1.py`.
- [x] `tools/win`: scenario 12 in `basic` and `all`; `Play-Act1.ps1`, and the play run in `Run-Scenarios.ps1`.
- [ ] An independent review. One was started on 2026-11-14 and was cut off before it reported; nothing came back from it. What stands in its place is the author's own second reading and the tests below.
- [ ] Compile on the PC; build against the real master; run scenario 12; play it by hand.

## Tests

All on this side of the game; none is a compile or a game test.

| What | Result |
|---|---|
| The build against eight stand-in masters, read back and compared with the spec | Passes; the id file comes out the same with and without a master |
| The written bytes, read without the library that wrote them | Pass; 35 kinds of deliberate damage each caught (14 of them to the actors: whose looks, which faction, what temper among them) |
| Looks: three men, three women and one of no one sex offered; told apart by the flag, by the actor a settler takes its looks from, by a list all of one sex; nine men for three faces | As specified, and the build says which faces are used twice |
| Things by name: two with one name, one with a name and no model, none at all, a master without its strings files | The lower id; the next name; the bottle cap; the bottle cap, and the revolver left out and said to be |
| Scenario 12 on the stand-in engine | 42 of 42; also with every call taking a frame; no box opens |
| Scenario 12 with a fault put in: a marshal who is alive, somebody who walks off, somebody who never appears, a reference not placed, a box put into the wrong alias, no revolver, a script that activates a book, a box in the audit | Each noticed, or (no revolver) rightly not a failure |
| **Every road through the chapter, played by its buttons** and compared with the logic model after every step: talked down; the speech failed and a fight; "Let them go."; shooting first; a deal with each of the four answers; the deal refused; walked past with each of the three answers; walking on to town; never met; the wagon saved and its owner lost; the caravan shot and nobody left; the one left to speak is Abel; Pritchard before the dispatch; "Not yet."; the evidence piece by piece; reported in three places; sold; posted three ways; the Yard Office not to be named on thin evidence; burned | 31 roads; the game's state equals the model's at every step |
| Faults put into the talk on purpose (two answers swapped, a coin that always falls one way, walking on that settles something, a share paid whatever became of the deal, thanks given twice, a line shown to somebody dead) | Each noticed |
| The lines: every one is shown somewhere and brought up by a test; none names what Act I does not know; no box has more than four buttons | Pass |
| The Windows scripts on a stand-in PC: scenario 12, and the play run | Scenario 12 passes; the play run waits for the game to be closed, lists the stages set, and puts back what it changed |

## Rollback

`TLM_A1`, `SpecAct1.cs`, the two scripts, scenario 12, `Play-Act1.ps1` and `test_act1.py` can be deleted together; besides them only these refer to the cut: the lines in `Spec.cs` that take its records into the plugin's lists (each names `Act1`), the property `TLM_A1` on `TLM:Core` and `TLM:SelfTest`, and the play run in `Run-Scenarios.ps1`. The dispatch and the two papers would keep the looks they were given, which does no harm. The quests' rules, the logic model and the 64 earlier scenarios are not touched by any of it.

It must not ship as it is: the people are copies of the game's settler (see the trial's note on what a copy is), and it stands in the game's own test room.

## What was assumed

| # | Assumed here | Where the canon and the designs stand |
|---|---|---|
| 1 | Reese Dunmore and the three Cutters as male, female, male | The canon gives them no sex |
| 2 | The lines marked **[NEW]** | Written for this cut; the designs have the others |
| 3 | A coin for Dunmore's speech check | The design leaves the difficulty to the editor |
| 4 | Nell Fenwick's thanks as 30 caps; a deal's share as 20 | The design says "reserve ammo and caps", and "half the cargo" |
| 5 | A "(Say nothing)" button where a witness lives | The design lists three answers; the quest's rules already allow silence |
| 6 | Pritchard's line when the witness is Abel Rudd | The design's line names Nell Fenwick only |
| 7 | The hand-off follows the debrief in the same conversation | The design has them as two nodes and does not say |
| 8 | Pritchard can be told of the ledger before the dispatch and after the chapter, as well as with it | The side quest's design puts the button on the "has dispatch" greeting |
| 9 | The three factions keep to themselves, and nobody but a Cutter joins a fight | The designs do not say who stands by whom |
| 10 | The cargo is not marked as the caravan's property, so taking from it is not theft | The main quest's design has the wagon owned by `TLM_Fac_Caravan` |
| 11 | Everything in [ACT1_chatgpt_asset_brief.md](ACT1_chatgpt_asset_brief.md), "What was assumed" | |
