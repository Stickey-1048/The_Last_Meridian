# Questions for the owner

**Resolution, 16 November 2026:** the owner delegated these decisions to the creative team. The adopted answers are in [the canon decision amendment](../../../../docs/design/ACT1_CREATIVE_DECISIONS_2026-11-16.md). The original questions below are preserved as proposal history. The submitted JSON still needs the required writing/continuity revisions before it is accepted for construction.

Everything in this folder that is yours to decide. Nothing here is canon until you say so, and nothing is built from a file you have not accepted. Start with the five under "Decide first": the rest follow from them.

## Decide first

1. **One purse.** Is it true that Silas Vane has paid for all three towns' troubles, and for the Cutters on the Tellico road, out of silver sent down from Blackstone Station? This answers the question the canon notes left open ("is one hand behind the three troubles?") with: one purse, four hands, and each hand had a reason of its own. Chapters 2 and 4 stand on it.
2. **Who signed for Ostrander.** Is the inspector alive, and is he Preacher Dole? Is Gussie Lockridge the one who kept stamping his name? Chapter 1's side quest says only that a dead man cannot have signed and names nobody; this names two people, both with a case. It also makes the wreck in Chapter 1 neglect signed clean, not sabotage: Dole says he never touched that train.
3. **The Stonebound under Red Hollow.** May the player meet Helga Dorn at a stone door in Chapter 2? It is the first sign that the valleys are not the only place with people in them, eight chapters before the canon's Chapter 9. The smaller version, if you would rather wait: the knocking is only the trapped shift, the lamp is an old company one, and the choice is between the cage and the charges.
4. **The man with the silver gun, on stage.** May Cassian Voss walk onto the fairground in Chapter 3, unnamed, speak to the player and shoot the courier? Everything he says can be cut and the shot still comes off the roof. He cannot be caught or killed in this chapter.
5. **Being recognised.** Voss says the player has "a familiar sort of face" and that not knowing him is "a mercy". Lucien Grey asks how the player's memory is. Edda Flint says somebody good taught the player to shoot. Nobody says what they know, and the player's only replies are buttons. Is even that too much before the choices in `docs/child-of-the-deep.md` are settled? If so, four lines come out (`voss_line`, `voss_know`, `flint_line`, `flint_hat`) and two lose their last sentence (`grey_offer`, `grey_train`); nothing else changes.

## Names

Eleven new names need the registry. None is an exact match for a given name or a surname in `docs/naming-registry.md` or `docs/factions-and-characters.md` (checked by eye, not by a tool). Four sit close to an existing name and may want changing: Greer beside Lucien Grey, Tarrow beside Evelyn Harrow, Pruitt beside Pritchard, and Vickers among the many V surnames (Vane, Voss, Vey, Vale).

| Name | Who |
|---|---|
| Augusta "Gussie" Lockridge | Yardmaster of Iron Junction |
| Wilhelmina "Billie" Tarrow | Driver of the Night Mail |
| Ezekiel "Preacher" Dole | Leader of the Black Rail; in truth the inspector, whose first name is given here as Reuben |
| Opal Starnes | Ration warden of Greenwater |
| Lyle Hatcher | Owner of the Queen of Tellico |
| Mose "Catfish" Pruitt | River pilot; Starnes's grandson |
| Hobart Greer | Mine captain of Red Hollow |
| Dinah Roark | Hoist-woman of Red Hollow; her husband is Pell |
| Juno Three-Fords | The courier; named after the fashion of Finn Nine-Trails |
| Temperance Vickers | Vane's bookkeeper |
| Tolly Granger | Printer at Mercy Crossing |

Eight people here already have names in the canon or the registers and are used under them: Esther Quill, Helga Dorn, Clara Whitcomb, Amos Brigg, Tomas Belden, Lucien Grey, Cassian Voss, Edda Flint. Their files say `proposed` only because the plugin does not have them yet; the format requires that word. **Is each of them wanted in Act I in person?** Whitcomb and Brigg especially: the fair could be carried by their juniors.

Places named for the first time: Sawtooth Cut, Hangman's Chute, the Queen of Tellico, the Mouth, the Nine level, the camp-ground. Things: Old Contrary, the Black Rail (the canon's Black Rail Syndicate, shortened as its own people would say it).

## Things that change what Chapter 1 means

6. **What the dispatch says.** The Chapter 1 design leaves it open (its question Q4). `documents.json` proposes a text: three towns, "somebody is being paid", and a name Gantt would not write down.
7. **Why the Cutters were there.** Paid to wait for whoever walked away from the train and to take the marshal's pouch; the wagon was to pass the time. This means somebody expected the wreck and expected a survivor. It does not say who the survivor is.
8. **Pritchard's secret.** He hanged the wrong man in the spring of ninety-eight and has not hanged anyone since. Judge Quill knew on the day. It is new, it is the lever the player can use at the gallows wagon, and it is why his hand shakes. It also turns the first chapter's threat to Dunmore, "Pritchard hangs road-takers", into a reputation he no longer deserves.
9. **Ada Pike cut the mould** for the silver cartridge, twelve years ago, for a stranger. She says so only after the fair, and only in an aside. It gives her a reason to be in the story after Chapter 1 and a tie to Flint.

## Tone and content

10. **Two hangings and a lynching.** A judge's gallows the player can interrupt; a town hanging a man from a steeple at the player's word; a mob hanging Vane while the sheriff fails to draw. None is shown as right. Do you want them in the game at all, and if so all three?
11. **Eleven men buried alive** if the player tells Greer to fire, or does nothing. The widow says she will come after the player.
12. **Thirty people in the water** if the player burns the Queen, cooks and a fiddler among them.
13. **A preacher who wrecks trains.** Dole quotes track gauge like scripture. He is a wronged man doing an evil thing, not a comment on faith; Decoration Day in Chapter 3 shows the valley's religion as the one thing that keeps a truce. Say if it reads otherwise.
14. **Real places.** The reservoir that inspired Greenwater drowned real communities, Cherokee town sites among them, and the real turnpike that inspired the pike was a road of the removal. Neither is named or shown; Greenwater's drowned town is invented. Is that the right distance?
15. **The courier** is the first Hollowborn the player sees. Her ears turn toward a sound before her head does, and nobody remarks on it. Is a silent first meeting what you want?

## How the factions show themselves

16. **The Directorate in a valley that has never heard of it.** Here it is one surveyor who offers to bring the power back in a year and will not say at what price. Nothing he says names what is under the mountains.
17. **The Commonwealth** arrives as a soup wagon and a list. Its delegate is pleasant and the menace is in what he cannot remember anyone asking. The canon asks for credible advocates: Belden's offer is real food for hungry people, and Greenwater takes it if the player sells the grain.
18. **The Dominion** takes the camp-ground after the shot unless the player walks in front of its rifles. Brigg did not arrange the shot; he arranged to be ready for one.
19. **The Compact** is the only flag whose speaker admits a fault in her own offer. Is that weighting it?

## What the format could not hold

20. **A fight.** Three lines end with a count ("One.") and then the game has to do the rest. Whether a duel on a rail track by lantern light can be staged is the mechanics' question.
21. **A chase** over a roof to a river, with a man who always reaches the boat first.
22. **A ride** on a moving engine, and a jump.
23. **A ballad that changes.** The printer has three sheets for three outcomes of Chapter 1; only one is written out, with the other two as lines he calls in the street.
24. **Conditions with "or".** A line can only ask for several things at once, not one thing or another, so some replies exist in two or three copies.

## What is not here

- **Chapter 5.** Not written. It waits on the choices in `docs/child-of-the-deep.md`, as the project's rule says. Chapter 4 ends by pointing at Blackstone Station and says nothing of what is there.
- **Chapter 1.** No new lines for the two built quests, apart from twelve asides in `talk/town.json` that read how they came out.
- **A check on the writing by anyone else.** No second person or agent has read this.
