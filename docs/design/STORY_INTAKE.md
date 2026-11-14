# Story intake: the format writing arrives in

For whoever writes characters, storylines and dialogue outside the repository, and for the mechanics that take it in. **The format is binding; what is written in it is not canon until the owner accepts it.**

Two parties, one division of labour:

- **The writer** (the owner's writing partner) researches, imagines and writes: who people are, what happens, what is said. It decides nothing about how the game does it.
- **The mechanics** (the plugin builder, the scripts, the tests) take what is written **exactly as written** and make it run. They do not improve a line, fill a gap or settle a contradiction; they send it back.

So everything the writer hands over has to be in a form a program can read. This page is that form. `python3 tools/check_story_intake.py --strict <folder>` checks a folder against it, and a folder that does not pass is not taken in. A worked example, made from what the plugin already holds, is in [story_intake_example/](story_intake_example/).

## Where it goes

`assets/incoming/act1/story/` on the branch `feat/tlm-mq01-graybox`. Text files only.

| File | Holds |
|---|---|
| `RESEARCH.md` | What was looked up, and where |
| `characters.json` | The people |
| `quests/<key>.json` | One file for each quest |
| `talk/<key>.json` | What is said, one file for each quest (or `talk/town.json` for talk that belongs to no quest) |
| `documents.json` | Papers a player can read |
| `QUESTIONS_FOR_OWNER.md` | Every decision that is the owner's: a name, a change to something locked, a choice between alternatives |

Never edit `CANON.md`, anything under `docs/` or any script. A proposal to change one of those is a line in `QUESTIONS_FOR_OWNER.md`.

## Rules for every piece of text a player sees

- Plain ASCII: straight quotes and apostrophes, three dots for an ellipsis, a hyphen for a dash, no accents.
- No percent sign, and no double quote inside a spoken line (the speaker's words are put in quotes by the builder).
- A spoken line: at most 240 characters. A button: at most 48. An objective: 100. A document: 1,500, with line breaks.
- In Act I nobody knows of the Deep, MERIDIAN, the Riders, the Charter, the Open Ledger or a vault. A line that uses one of those words is refused: in a quest's log, an objective, a choice, a line of talk, a button, a paper. A word counts in every form of it: as it stands, in the plural, as an owner (*the Rider*, *the Riders*, *the Rider's*), in capitals or not. Longer words that only begin the same (*deeper*, *deeply*, *vaulted*) are other words.
- **One exception, and a narrow one.** The canon ends Act I with the player recovering proof of having been a Meridian Rider and Mara Vale saying that the player's family came from the Deep ([three-act-story.md](../three-act-story.md), "05 The Fifth Rider"; [child-of-the-deep.md](../child-of-the-deep.md), quest beats). So the words *Deep*, *Meridian* and *Rider*, and no others, may be used by that chapter's own quest and by the talk file that belongs to it, and only when the quest file is unmistakably that quest: `"key": "mq05"`, `"id": "TLM_MQ05"`, `"chapter": 5`, and no second file with that key. Under any other key, id or chapter the words are refused as everywhere else; so are they in `talk/town.json` and in every paper, whatever chapter it is found in; and the Charter, the Open Ledger and a vault stay unsaid in all of Act I, the last chapter included. This says what the check lets through. It does not say that chapter may be written yet: the choices in child-of-the-deep.md are the owner's and are not settled.
- The player's part is a button: a few words, never a speech, never a statement of belief. At most four buttons to a box.

## RESEARCH.md

A table, one row for each thing the writing leans on:

```
| # | What was looked up | Source | What it gave the story | Kind |
|---|---|---|---|---|
| R1 | ... | https://... (title, publisher) | ... | REAL |
```

Kind is `REAL` (the world as it is or was), `FALLOUT` (something the Fallout games establish) or `INVENTED` (this project's own). `REAL` and `FALLOUT` rows carry the address they were read at. Every `sources` and `draws_on` entry elsewhere names a row here (`"R1"`). A Fallout fact is only ever cited, never copied, and an invention is never called Fallout's.

## characters.json

```json
{
 "format": "tlm-characters-1",
 "characters": [
  {
   "id": "pritchard", "record": "TLM_NPC_SHERIFF_MERCY", "name": "Owen Pritchard",
   "status": "canon", "role": "Sheriff of Mercy Crossing; Old Warden", "sex": "male", "age": 58,
   "looks": "", "voice": "", "wants": "", "fears": "", "secret": "", "wrong_about": "",
   "knows": [], "does_not_know": [],
   "ties": [ { "to": "pike", "what": "" } ],
   "sources": [ "R3" ]
  }
 ]
}
```

- `id` is the short word every other file uses for the person. The people the plugin has, and their records:

  | id | record | | id | record |
  |---|---|---|---|---|
  | `pritchard` | `TLM_NPC_SHERIFF_MERCY` | | `gantt` | `TLM_NPC_MARSHAL_DEAD` |
  | `pike` | `TLM_NPC_GUNSMITH_MERCY` | | `nell` | `TLM_NPC_CARAVAN_MASTER` |
  | `vane` | `TLM_NPC_MERCHANT_MERCY` | | `abel` | `TLM_NPC_CARAVAN_DROVER` |
  | `keene` | `TLM_NPC_PHYSICIAN_MERCY` | | `dunmore` | `TLM_NPC_CUTTER_LEAD` |
  | `talbot` | `TLM_NPC_DEPUTY_MERCY` | | `cutter` | none: stands for any of the three |
  | `haskell` | `TLM_NPC_FREIGHT_MERCY` | | | |

- A new person has `"record": null` and `"status": "proposed"`, and a name that is in `docs/naming-registry.md` or is asked for in `QUESTIONS_FOR_OWNER.md`.
- `sex` is `male` or `female`: the builder picks a face by it.
- `voice` is how the person talks (rhythm, words they favour, what they never say), so that lines written later sound like them.
- `knows` and `does_not_know` are short statements. They are what keeps a line from saying what its speaker cannot know.

## quests/&lt;key&gt;.json

```json
{
 "format": "tlm-quest-1",
 "key": "mq02a", "id": "TLM_MQ02A", "title": "", "chapter": 2, "kind": "main",
 "premise": "", "draws_on": [ "R7" ],
 "reads": [ "ledger is reported", "flag yard_alerted" ],
 "cast": [ "pritchard" ],
 "places": [ { "id": "", "name": "", "what": "" } ],
 "stages": [ { "n": 10, "set_by": "what in the world sets it", "log": "journal text, or null" },
             { "n": 100, "set_by": "", "log": null, "completes": true } ],
 "objectives": [ { "n": 10, "text": "" } ],
 "choices": [ { "at": 30, "options": [ { "label": "", "sets": 31, "now": "", "later": "" } ] } ],
 "evidence": [ { "id": "", "kind": "note", "found": "", "sets": 12 } ],
 "ways_through": [ "", "" ],
 "cannot_break": "",
 "new_flags": [ { "name": "", "meaning": "" } ],
 "open_questions": [ "" ]
}
```

- `key` is a short lower-case word; conditions and effects elsewhere use it (`mq02a done 30`). **One file for each key**: a second file with a key that is already used, whether by a quest the plugin has or by a new one, is refused.
- `id` is the quest's record name: `TLM_` and the key in capitals (`mq02a` is `TLM_MQ02A`). For the two quests the plugin has it is `TLM_MQ01` and `TLM_SQ01`. A file whose key and id do not belong together is refused, and so is a new quest under the id of another.
- **A stage is a fact that has become true**, numbered 1 to 999. `set_by` says what in the world makes it true: something picked up, a place entered, somebody dead, a button. Exactly one stage completes the quest.
- **A choice** has two to four options. Each says what it changes `now` and what it changes `later`. A choice is shown by what follows from it, never by what the player says about it.
- `ways_through`: at least two, and one of them needs nothing optional. No quest may be a dead end, and no side quest may stand in the way of a main one.
- `cannot_break`: what happens if the player skips it, kills somebody in it, or comes back to it late.
- `reads` lists what the quest looks at from earlier (the vocabulary below). `new_flags` are facts later quests may read.
- The two quests the plugin has are `mq01` and `sq01`. Their stages are fixed: write talk and documents for them, not new stages. A wish for one is a line in `QUESTIONS_FOR_OWNER.md`.

## talk/&lt;key&gt;.json

```json
{
 "format": "tlm-talk-1", "quest": "TLM_MQ01",
 "lines": [
  {
   "id": "dunmore_hold", "speaker": "dunmore", "status": "design", "priority": 10,
   "when": [ "outcome is none", "mq01 notdone 37" ],
   "text": "Keep walking. Or stay and pick up a share.",
   "buttons": [
    { "label": "Pritchard hangs road-takers. Leave.", "check": "speech",
      "pass": { "do": [ "mq01 set 31" ], "then": "dunmore_breaks" },
      "fail": { "do": [ "mq01 set 37" ], "then": "dunmore_turns" } },
    { "label": "Let them go.", "do": [ "mq01 set 37" ], "then": "dunmore_turns" },
    { "label": "What kind of share?", "then": "dunmore_share" },
    { "label": "Not my business." }
   ],
   "sources": []
  }
 ]
}
```

- `quest` is the `id` of the quest the talk belongs to: one of the plugin's (`TLM_MQ01`, `TLM_SQ01`) or one that a file under `quests/` in the same folder declares. A talk file about a quest nothing declares is refused. In `talk/town.json`, which belongs to no quest, it is `null`.
- A person who is spoken to says **the line with the highest `priority` among those whose `when` all hold**. Give each person a line with an empty `when` and priority 0, so that there is always something to say. `priority` is a whole number from 0 to 1000; left out, it is 0. Anything else (a word, a number in quotes, a fraction, a negative number) is refused, because it cannot be compared.
- `kind`: `talk` (the default: a box) or `aside` (a line at the edge of the screen; no buttons).
- `status`: `design` if the line is already in the designs, `new` otherwise.
- A line with no buttons gets one, "Continue". A button may `do` things, lead on to another line (`then`), both, or neither (the box closes).
- `check: speech` stands for a test of persuasion; say what follows under `pass` and under `fail`.
- An id is unique across all the talk files.

### What a `when` may ask

| Form | Means | Values |
|---|---|---|
| `mq01 done 20`, `mq01 notdone 50` | A stage of a quest is or is not set | `mq01`: 10 started, 15 revolver, 20 dispatch taken, 30 ambush live, 31 saved, 32 walked past, 33 deal, 34 never met, 35 the player killed a caravan hand, 37 the Cutters turn on the player, 40 in town, 50 delivered, 51 to 55 the debrief answers, 60 hand-off, 100 complete. `sq01`: 5 running, 10 ledger found, 11 brake shoes, 12 draw-bar, 13 journal, 14 Pike's book, 20 case presentable, 25 falsification established, 41 reported, 42 posted, 43 posted naming the Yard Office, 44 posted naming Haskell, 45 sold, 46 burned, 50 resolved, 100 complete |
| `outcome is saved` (or `isnot`) | How the wagon came out | `none`, `saved`, `evaded` (walked past: Abel Rudd is dead), `exploited` (a share taken, or the caravan shot at), `missed` (never met: Abel Rudd is dead) |
| `method is deal` | How it was exploited | `none`, `deal`, `betrayal` |
| `debrief is witness` | What Pritchard makes of the road | `saved`, `evaded`, `witness`, `no_witness`, `missed`, `lost` |
| `answer is admit` | What the player told him | `none`, `admit`, `deny`, `confess`, `blame`, `lying`, `silent` |
| `ledger is sold` | What was done with the ledger | `none`, `reported`, `posted`, `posted_yard`, `posted_haskell`, `sold`, `destroyed` |
| `evidence >= 2` | How strong the case is | 0, 1 (the ledger is wrong), 2 (it was falsified) |
| `alive nell`, `dead abel` | A person lives or not | any character id |
| `flag yard_alerted`, `notflag vane_has_ledger` | A fact set earlier | `yard_alerted`, `vane_has_ledger`, `haskell_scapegoated`, and any `new_flags` |
| `truth >= 1` | A hidden count | `truth`, `competence`, `accountability`, `mutual_trust`, `regard` (Mercy Crossing's regard for the player) |

### What a button may `do`

| Form | Means |
|---|---|
| `mq01 set 50` | Sets a stage. What the stage then does is the quest's own business. Not allowed: stages the quest sets itself (`mq01` 10 and 100; `sq01` 5, 20, 25, 50, 100) |
| `give caps 30` | Gives the player caps |

Anything else a line should bring about is a stage: propose it in the quest's file.

## documents.json

```json
{ "format": "tlm-documents-1",
  "documents": [ { "id": "marshal_journal", "kind": "note", "title": "Rail Marshal's Journal",
                   "found": "On the dead marshal, at the wreck", "text": "...", "sources": [ "R1" ] } ] }
```

`kind` is `note`, `letter`, `ledger`, `notice` or `label`.

## What the check does and does not say

It says that every name used is one the plugin and the scripts know, that the limits hold, and that nothing is left blank. It says nothing about whether the writing is any good, and passing it makes nothing canon. That is the owner's to say, file by file.
