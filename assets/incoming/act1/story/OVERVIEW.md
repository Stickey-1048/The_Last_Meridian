# Act I, turned up: Chapters 2 to 4

**16 November decision update:** this overview preserves the submitted proposal. [The adopted creative decisions](../../../../docs/design/ACT1_CREATIVE_DECISIONS_2026-11-16.md) supersede conflicting recognition, naming, foreknowledge, Voss-cameo and automatic-catastrophe proposals below. The JSON and prose still require revision; this is not an accepted playable chapter.

2026-11-16. Written at the owner's request ("it's all been very boring, push into things more"). **A proposal. Nothing here is canon, nothing is built, and no canonical file, design or script was changed.** It is in the story-intake format and passes `python3 tools/check_story_intake.py --strict assets/incoming/act1/story`. Every decision that is the owner's is in [QUESTIONS_FOR_OWNER.md](QUESTIONS_FOR_OWNER.md).

Who wrote it: the coding assistant in this session, not the usual writing partner. The owner said to ask Maya to bring the other agents in if more story was needed; no other agent session was reachable from here, so it was written directly.

## What was wrong, and what this does about it

The earlier storyboard for these chapters (branch `feat/tlm-act1-story-depth`) was careful and bloodless. Its troubles were a deferred repair, a disputed freight charge and a pump awaiting review; its people were "a yard supervisor" and "a ration custodian"; almost every paragraph ended by saying what must not happen. Nobody in it wanted anything badly enough to do something stupid.

This version keeps the same skeleton (three towns, the fair, Vane's books, Blackstone) and the same rules (the player's part is a button, no dead ends, nothing optional required, four factions and never a fifth). What changes:

- **Every chapter has a set piece you could put on a poster.** A train jumped over a gap in the rails. A gambling boat burned to the waterline. A cage ride four hundred feet down to something that knocks back. A shot off a roof on the one day nobody shoots. A sheriff who cannot hold his gun, on a porch, in front of a rope.
- **Every trouble has a face, and the face has a reason.** A train-wrecker who preaches from a flatcar and used to be the line's inspector. A grandmother with a ladle chained to her wrist who wants a man hanged from a steeple. A judge who holds court on a gallows wagon. A merchant who has kept four armies out of the valley with a pencil.
- **Every choice costs somebody the player has met.** There is no button marked with the right answer.
- **Chapter 1 comes back.** The first chapter's loose ends are picked up and pulled: who kept signing for the dead inspector, why the Cutters were on the Tellico road, what the wagon was really for, and what the stranger did there.

## The spine in one breath

Somebody up the dead rail line at Blackstone Station has been sending silver down to Silas Vane for six years to keep the valleys poor, slow and apart. Vane spends it on four people who each had their own reason to do the thing anyway. The player follows the silver up three roads, watches it get a courier killed at a fair, reads it in a ledger, decides what a town does to the man who took it, and ends Act I looking up the line.

## Chapter 2: Three Roads to Ruin (`mq02`, and one quest per road)

Pritchard puts a rail spike, a grain scoop and a miner's brass tag on his desk and says pick one up. One road is enough to move on; all three can be done in any order; refusing gets his deputy shot.

**The Night Mail** (`mq02a`, by rail). Iron Junction is a walled roundhouse run by Gussie Lockridge from a dining car on the turntable, so that her office can be turned to face whoever is coming. She has lost four trains to pulled rails, each wreck chalked with a hymn number. The player rides the footplate of a patched engine called Old Contrary, beside a driver who bets on everything, into a cutting where Preacher Dole is waiting on a flatcar with thirty rifles.

- Run the gap, face Dole, sell him the train, or back out.
- Dole is R. Ostrander, the inspector the first chapter's ledger was signed for. He is not dead. He condemned a trestle, was overruled, and came back to make every false signature on the line bleed.
- The one who kept signing his name is Lockridge. No inspector would come out to a line that kills inspectors, so she took his stamp and passed her own trains, including the one the player walked out of. The player finds the stamp in her drawer with the pad still wet and decides what happens to it.

**The Queen of Tellico** (`mq02b`, by river). Greenwater stands on stilts over a drowned town and ties its boats to a steeple. Its winter grain is lashed to a gambling boat in plain sight, and Commodore Lyle Hatcher is selling the town its own corn by the cup across a faro table and calling it salvage. Opal Starnes, who rations with a ladle chained to her wrist, wants the grain and wants him hanged.

- Win the barge at cards, cut it loose and run the rapids at night, burn the boat, or buy a share and tell the town it sank.
- If the player wins, Opal asks for Hatcher. The player can hand him over.

**What Knocks in Red Hollow** (`mq02c`, by road). The pike runs through a Dominion toll-gate where Judge Esther Quill holds court from a gallows wagon. On her rope at noon is Reese Dunmore if he lived through Chapter 1, or one of his gang if he did not. He knows why the Cutters were on that road: they were paid to wait for whoever walked away from the train.

- Shoot the rope, pay the fine, shame the judge with a secret of Pritchard's, or watch.

Past the gate the hills are bald and red, and the mine has been chained shut from the outside with eleven men below. The captain fires his charges at dawn. The wives can hear knocking. One of them can read it, and says something is knocking back.

- Go down in the cage. The night shift is alive, and has been fed, by a woman in an iron collar sitting in front of a door of fitted stone: the first of the Stonebound anyone above has met. She wants somebody who can swear for the whole town, and is frightened to learn there is no such person.
- Swear a boundary, bring the men up and blast the way shut, let the captain fire, or pocket her lamp and sell what is under Red Hollow.

## Chapter 3: The Four Flags (`mq03`)

Decoration Day on the camp-ground: graves dressed with paper flowers, dinner on the ground, a beef shoot, and no gun drawn in forty years. Pritchard uses the truce to put four flags at one table. Clara Whitcomb for the Compact sells like an auctioneer and admits what she has no rule for. Colonel Brigg for the Dominion offers one thing, a road you can walk at night, and names its price without blinking. Tomas Belden for the Commonwealth brings a soup wagon and a list. Lucien Grey for the Directorate measures the reservoir, offers to light the valley, and asks the player how their memory is.

- The player can shoot for the beef against Edda Flint, a bounty hunter with a string of silver cartridge cases round her neck.
- A courteous stranger in a grey duster out-shoots everybody with a pistol, gives the prize to a widow, and looks at the player a moment too long. He is never named.
- A courier from the high country crosses the meadow at a run with a case chained to her wrist. She is three steps from Pritchard when the shot comes off the meeting shed roof.
- One thing, now: chase the shooter over the roof to the river, stay and hear the courier's last words, walk between Brigg's rifles and the crowd, or cut the case off her wrist and leave.
- On the roof is one empty silver case, stood on end to be found. In the case is a ledger number in Silas Vane's handwriting.

## Chapter 4: The Black Ledger (`mq04`)

Four ways to the book: Pritchard's warrant in daylight, the safe during Vane's Harvest Supper while the whole town eats at his table, the strongbox off the night freight, or Vane himself, who shows it gladly to a stranger who took a share on the Tellico road.

The book has four columns, rail, river, mine and road, a payment against each, and a fifth column for what he received, with a small square where a name should be. Between the player and the door is Temperance Vickers, his bookkeeper, with a sawn-off in a cash box, who corrects the player's arithmetic before she counts to two.

Then the town finds out, and comes to his porch with a rope. Pritchard stands on the steps and cannot make his hand hold still. Vane asks the only person who has read the book what he is.

- Read it all out to the street, make him sign the holds away for silence, take him into the player's own service, or step aside.

Whichever it is, the silver comes from Blackstone Station, and that is where Act I's last chapter begins. That chapter is not written here: the owner's choices about the player's past come first.

## What is in this folder

| File | Holds |
|---|---|
| `characters.json` | 26 people: 7 from Chapter 1 given wants, fears and secrets, and 19 the plugin does not have yet (8 of those are names the naming registry or the faction register already holds) |
| `quests/` | Six quests: the chapter hub, the three roads, the fair, the black ledger. Stages, choices with what each changes now and later, evidence, ways through, what cannot break, and 40 new facts later chapters can read |
| `talk/` | 164 lines with their buttons, in seven files |
| `documents.json` | 18 papers: the dispatch Gantt died carrying, a ballad about the player, a ration board, a letter of hire, a gallows docket, a chalk message from the mine, a page of the black book, Vane's will |
| `RESEARCH.md` | Six things looked up in the real world and where, and three rows for what is the project's own |
| `QUESTIONS_FOR_OWNER.md` | Everything here that is the owner's to decide |

## What this is not

- Not canon, and not accepted. A name a generator invented stays out of the plugin until the owner says so.
- Not built. No logic model, script or plugin record exists for any of it, and none was written.
- Not Chapter 1. The two built quests keep their stages; this only reads them.
- Not judged by the check. The check says the mechanics can take the files in. Whether the writing is any good is the owner's to say.
