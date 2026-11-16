# Act I, Chapters 2 to 4: the revised writing intake

16 November 2026. **Status: a revised proposal, returned for narrative acceptance and independent engineering review. Not accepted, not built, not compiled, not tested in the game.** The installed first-section demo and the tested world packages are unchanged.

This file describes the package as it stands after the delegated creative decisions and writing closure packets 2 and 3 were applied, with the talk in the second format (`tlm-talk-2`). The original proposal, including the earlier version of this overview, is in Git at `6f21643`.

- What was decided: [ACT1_CREATIVE_DECISIONS_2026-11-16.md](../../../../docs/design/ACT1_CREATIVE_DECISIONS_2026-11-16.md).
- What was received, what was done and what is still missing: [ACT1_CHARLES_REVISION_RECEIPT.md](../../../../docs/design/ACT1_CHARLES_REVISION_RECEIPT.md).
- Every node that changed in that first revision, before and after: [ACT1_CHARLES_REVISION_CHANGES.md](../../../../docs/design/ACT1_CHARLES_REVISION_CHANGES.md).
- Packet 3, the latest: [the receipt](../../../../docs/design/ACT1_CHARLES_PACKET3_RECEIPT.md), [every node that changed](../../../../docs/design/ACT1_CHARLES_PACKET3_CHANGES.md), and [the complete entry and priority ledger](../../../../docs/design/ACT1_CHARLES_PACKET3_ENTRY_LEDGER.md).
- Packet 2 and the entry format: [the receipt](../../../../docs/design/ACT1_CHARLES_PACKET2_RECEIPT.md), [every node that changed](../../../../docs/design/ACT1_CHARLES_PACKET2_CHANGES.md), and [every line's entry label and priority](../../../../docs/design/ACT1_CHARLES_PACKET2_ENTRY_LEDGER.md).

The format check passes (`python3 tools/check_story_intake.py --strict assets/incoming/act1/story`). That says the mechanics can take the files in. It says nothing about fairness, whether a duel or a moving train can be staged, or whether the writing is good.

## The spine

Silver from Blackstone Station has reached Silas Vane for six years, and he has spent it keeping the valley's roads slow and its towns apart. The present rail attacks, the held grain, the chained mine and the watch on the Tellico road are separate commissions inside that network. Each person who took the silver had purposes of their own and answers for what they did. Vane funds; he does not control every hand, cause every accident or know who is paying him.

## Chapter 2: Three Roads to Ruin (`mq02`, and one quest per road)

Pritchard puts a rail spike, a grain scoop and a miner's brass tag on his desk. One completed road opens the fair. So does telling him to call the fair without a report: nobody is hurt for refusing, and the roads stay open. While a road is still open after the fair he offers it, and beside it a way to talk over any road's account without promising a journey. A road that is never visited, or is left half done, stays unresolved; calling the fair settles nothing on it.

**The Night Mail** (`mq02a`, by rail). Gussie Lockridge runs Iron Junction from a dining car on the roundhouse turntable. The player rides the footplate of Old Contrary beside Billie Tupper into Sawtooth Cut, where Preacher Dole waits on a flatcar. Run the gap, face him, take his share or back out. Dole is Reuben Ostrander, the inspector reported dead of fever; the player learns it from him or from his hymnal, not from a nameplate. Lockridge kept using his stamp to pass unsafe equipment. The wreck in Chapter 1 came from that neglect and false certification. Dole's rail attacks are his own, later crimes. The moving engine, the jump and the duel are feasibility-gated and need a grounded alternative.

**The Queen of Tellico** (`mq02b`, by river). Greenwater's winter grain is lashed to Lyle Hatcher's gambling boat. Opal Starnes keeps the ration; her grandson Mose Rafferty, called Catfish, has the skiff. Win the barge at cards, cut it loose and run Hangman's Chute, buy a share, or burn the boat. The Chute escape and the fire are alternatives: the fire takes the occupied boat and the winter grain still lashed to it. Before it can be ordered Rafferty says who is aboard and what else will burn, and the button says what it is: "Burn the occupied Queen." No death count is asserted.

**What Knocks in Red Hollow** (`mq02c`, by road). At the Dominion's toll-gate Judge Quill is about to hang a man from the Tellico road. He can say what the Cutters were paid for: to watch the road for Gantt's delayed freight and take the marshal's pouch. Nobody named a wreck or a survivor; the wagon was their own idea. The player can shoot the rope, pay the fine or watch. A fourth course, showing Pritchard's review copy of a wrongful hanging in spring 2298, exists only while the player has that copy in hand, and earns an adjournment and a review, not a pardon. Pritchard offers the copy if asked about Quill before the pike; taking it is optional and nothing waits on it.

At Red Hollow, Captain Hobart Blevins has chained the mine with eleven of the night shift below. Dinah Roark can read the knocking. The player can go down, find the shift alive and meet Helga Dorn, who answers for one gallery and one House. The bargain on offer is personal: keep to the line on your own passage and carry her terms up to the mine. It binds nobody else. The mine is sealed with the shift below only by an explicit order, or when a local deadline runs out. That deadline is armed only when the player accepts Roark's warning in so many words; talking to her does not arm it, and a dead Captain cannot fire. Roark says a different thing in each case.

## Chapter 3: The Four Flags (`mq03`)

Decoration Day on the camp-ground. Four flags at one table: Clara Whitcomb for the Compact, Colonel Brigg for the Dominion, Tomas Belden for the Commonwealth, Lucien Grey for the Directorate. Each now names a cost of its own offer. A beef shoot, with Edda Flint as the shot to beat.

A courier comes in with a case chained to her wrist. The shot comes from the meeting-shed roof. The shooter is a distant figure leaving by a boat that was already waiting: no face, no name, no conversation, no chase that cannot be won. Brigg gives his order where it can be read, and the player's courses come after it: search the roof and the landing, stay with the courier, call the delegates to uphold the truce, or take the case. The truce is spoken by the three living delegates and a local officer in turn. Then Brigg says his concession, and only the Continue under those words records it. If any of those voices is dead the truce is not offered and the other courses remain; that is a decision, not a gap. If the courier is dead nobody offers to stay with her. If Brigg is dead the courses are carried by Pritchard, or Talbot, or Flint, by who is alive. Once the quest is complete none of these lines can be used. Nobody at the fair hints that they know the player.

Each of the four flags names a disagreement inside itself.

## Chapter 4: The Black Ledger (`mq04`)

Four ways to Vane's second book. Temperance Beckett, his bookkeeper, stands between the player and the door. Then the town comes to his porch with a rope and Pritchard on the steps. Read the book out, make Vane sign the holds away, take him into the player's service, or say "Let the crowd hang him." Leaving, or never coming, does not choose that. The silver comes from Blackstone Station. Chapter 5 is not written.

## What is in the folder

| File | Holds |
|---|---|
| `characters.json` | 26 people: 7 of the plugin's, 19 it does not have |
| `quests/` | Six quest files, 82 stages, 40 facts later chapters can read |
| `talk/` | 227 lines in seven files, in the second talk format: 129 entries, 86 continuations, 12 asides |
| `documents.json` | 23 papers. Five are the ballad: one sheet for each recorded outcome of Chapter 1, one for a betrayal, one for none. One is Pritchard's 2298 review copy |
| `RESEARCH.md` | Unchanged. Its six real-world rows come from search summaries and have not been verified |
| `QUESTIONS_FOR_OWNER.md` | The original questions as resolved, and what is open now |

## Names

Four surnames changed: Tupper (was Tarrow), Blevins (was Greer), Rafferty (was Pruitt), Beckett (was Vickers). The machine ids `tarrow`, `greer`, `pruitt` and `vickers` are kept, so line ids such as `greer_first` still carry the old spelling. The eleven registered names are in [the naming registry](../../../../docs/naming-registry.md).
