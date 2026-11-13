# Act I asset brief: prompts for ChatGPT

**Status: a working brief, written 2026-11-13.** Nothing in it changes the canon. Where it has to assume something the canon does not say, it says **[PROPOSED]**, and those points are listed at the end for the owner to accept or strike.

This file is for the project's owner. It holds prompts to paste into ChatGPT so that it produces things the plugin's builder can take in: textures, character sheets, short texts and layouts for **Act I, The Broken Roads**, starting with its first chapter, *Six Rounds to Mercy*, and the town of Mercy Crossing.

## What can be imported, and what cannot

| Kind | What happens to it | How sure |
|---|---|---|
| **Text** (notices, letters, ledgers, signs, one-line remarks by townsfolk) | Goes straight into the plugin as books, notes and messages. | Works today: books and messages are already written by the builder, and a message shown on activating a person ran in the game on 2026-11-13. |
| **Layout data** (where things stand, as numbers) | The builder places people, triggers and objects from numbers already. | Works today for the test room. A room of the project's own has not been tried yet. |
| **Flat images** (signs, posters, notices, maps, emblems) | To be put on walls and floors as decals, or on the game's own flat sign and poster pieces. | **Not yet tried in the game.** The importer has to be written and proven with one image first. Make the images now; they will be used as soon as that works. |
| **Character portraits** | **Reference only.** A face in the game is built from the game's own head parts and sliders, not from a picture. What is used is the written casting card beside each portrait: it tells the builder which of the game's own bodies, hair and clothes to pick. Portraits can also appear in the world on wanted bills and notices. | The cards are usable today. |
| Sound, music, voice | Not now. | No importer, and rights to settle. |
| 3D models | Not now. | No importer. |

## Rules for everything ChatGPT makes

1. **Original work only.** No Fallout or Bethesda logos, characters or designs: no Vault Boy, Vault-Tec, Pip-Boy, Nuka-Cola, Brotherhood of Steel or Enclave insignia, power armour, or anything copied from the games' art or fonts. No real company logos, no real people's faces, no text taken from existing books, songs or films.
2. **Nothing goes into the canon by being generated.** Every new proper name or fact must be flagged, so the owner can accept or strike it.
3. Keep every file. Name files exactly as asked. Put them in the repository under `assets/incoming/act1/` (sub-folders `textures/`, `characters/`, `text/`, `layout/`), with a line in `assets/incoming/act1/PROVENANCE.md` saying which tool made the file and when.

## How to use this

Start a new ChatGPT conversation (or a ChatGPT Project) and paste **Part A** first. Then paste one task prompt from **Part B** at a time. Check each result against the rules before saving it.

---

## Part A: context to paste first

```text
You are helping with an unofficial, non-commercial fan mod for Fallout 4 called
THE LAST MERIDIAN. I am its owner. You will make original textures, character
sheets, short in-world texts and layouts for its first act. Follow these rules
exactly. If a rule stops you from doing something I ask, say so; do not work
around it.

HARD RULES
- Original work only. Never use or imitate Fallout/Bethesda logos, characters,
  mascots, fonts or designs (no Vault Boy, Vault-Tec, Pip-Boy, Nuka-Cola,
  Brotherhood of Steel, Enclave, power armour). No real brands, no real
  people's likenesses, no quotations from existing works.
- Do not invent canon silently. If you need a name, place, date, emblem or fact
  that is not in the SETTING below, mark it [NEW] and list all [NEW] items at
  the end of your answer. Prefer not to invent.
- Never write lines for the player character. Only write what other people
  say or write.
- No speeches and no moral lessons. People in this world talk about freight,
  weather, debts, rations and each other. Themes show through objects and
  consequences.
- Plain ASCII punctuation in all text (straight quotes, hyphen, three dots).
  No emoji.

SETTING (canon; do not change it)
- Year 2317. Southern Appalachia: eastern Tennessee, western North Carolina,
  northern Georgia. An Appalachian gunslinger Western: mountain valleys, rail
  lines, river fords, isolated towns, frontier justice. NOT a desert, NOT
  Arizona, NOT the Wild West of films. Wet green hills, fog, hemlock, laurel,
  red clay, old rail iron, timber and tin.
- Technology: scavenged pre-war machinery kept running by hand. Revolvers,
  lever guns, hand tools, old locomotives and rolling stock patched for
  generations, sealed dispatch cases. Pack animals are brahmin (two-headed
  cattle), not horses. Currency is bottle caps ("caps").
- Act I is called THE BROKEN ROADS. It is about local survival, road and rail
  sabotage, and records that do not match the facts. Ordinary people in Act I
  have never heard of any underground city or any machine intelligence. Do not
  mention such things.
- The opening region is the BROKEN VALLEYS, along the Tellico River. Its hub
  is the town of MERCY CROSSING. North lies the IRON CORRIDOR with the rail
  yards and foundries of IRON JUNCTION.
- The railway is "the line". The stretch through the valley is LINE 14, kept
  from the IRON JUNCTION YARD. Rail marshals carry the line's mail in sealed
  dispatch cases.

ACT I, CHAPTER 1: "SIX ROUNDS TO MERCY"
- A train on Line 14 has wrecked in the Tellico valley, some hours east of
  Mercy Crossing. The player wakes in the wreck, a stranger to everyone.
- In the wreck lies RAIL MARSHAL TOBIAS GANTT, dead, with a revolver holding
  six rounds, a sealed dispatch addressed to the Sheriff of Mercy Crossing,
  and a pocket journal.
- On the road to town a wagon is being robbed by a gang called the TELLICO
  CUTTERS, led by REESE DUNMORE. The wagon belongs to NELL FENWICK, a caravan
  owner; her hired hand is ABEL RUDD. The player may help, walk past, or take
  a share. Whatever happens is remembered.
- In Mercy Crossing the dispatch goes to SHERIFF OWEN PRITCHARD.
- A side matter, "SIGNED CLEAN": the train's maintenance ledger says the
  brakes and couplers were inspected and sound, signed by inspector
  R. OSTRANDER. The wreckage says otherwise, and the marshal's journal shows
  Ostrander died of fever at GREENWATER before the dates he supposedly
  signed. Nobody in Chapter 1 knows who forged the entries.

PEOPLE OF MERCY CROSSING (canon roles; looks are not yet decided)
- OWEN PRITCHARD: sheriff, an Old Warden (the older, law-minded kind of
  lawman). Mentor figure. Spare with words.
- ADA PIKE: gunsmith. Keeps her own parts book. Practical.
- SILAS VANE: merchant, runs the trading post. Smooth, careful. Do not show
  him as guilty or innocent of anything.
- MIRIAM KEENE: physician, runs the clinic.
- JONAH TALBOT: young deputy at the town gate.
- CORWIN HASKELL: freight agent; signs for goods received. An ordinary,
  blameless clerk.
- NELL FENWICK, ABEL RUDD, REESE DUNMORE, TOBIAS GANTT: as above.

LATER IN ACT I (only as distant hints, one line at most)
- GREENWATER is short of food. RED HOLLOW has sealed its mine. Someone is
  cutting the rails near IRON JUNCTION.

When I give you a task, answer with exactly the deliverables asked for, in the
formats asked for, then the list of [NEW] items (or "No new items").
Reply "Ready" if you understand.
```

---

## Part B: task prompts

### B1. Signs and posters (images)

Paste once for each numbered item, or ask for them in small groups. Sizes are in pixels and must be exact: the game needs sides that are powers of two.

```text
TASK B1: flat textures for signs and posters.

For each item below make ONE image, and then a second version of the same
image with all lettering removed (same art, blank where the words were).

Every image must be:
- exactly the pixel size given, PNG;
- perfectly flat and straight-on, as if scanned: no perspective, no frame, no
  wall or nails around it, no drop shadow, no mock-up, no lighting gradient;
- filled edge to edge by the object itself (the board or the sheet of paper);
- weathered but readable: hand-painted boards, letterpress and stencil on
  paper, rust stains, water marks, pencil notes. Appalachian rail town, 2317.
- lettered with EXACTLY the words given, spelled exactly, in capitals unless
  shown otherwise. Check the spelling letter by letter before you answer.

File names: use the name given, plus "_blank" for the version without words.

 1. tlm_a1_sign_mercy_crossing_2048x512.png
    A long painted timber town sign. Words: MERCY CROSSING
 2. tlm_a1_sign_warden_office_1024x512.png
    A painted board. Words: WARDEN OFFICE   and smaller: O. PRITCHARD, SHERIFF
 3. tlm_a1_sign_trading_post_1024x512.png
    A merchant's signboard, neater than the others. Words: TRADING POST
    and smaller: S. VANE
 4. tlm_a1_sign_gunsmith_1024x512.png
    A stencilled iron plate. Words: A. PIKE   and below: GUNSMITH
 5. tlm_a1_sign_clinic_1024x512.png
    A whitewashed board. Words: CLINIC   and smaller: M. KEENE, PHYSICIAN
 6. tlm_a1_sign_freight_1024x512.png
    A railway-style enamel plate, chipped. Words: FREIGHT   and smaller:
    LINE 14 - C. HASKELL, AGENT
 7. tlm_a1_notice_line14_suspended_512x512.png
    A printed railway notice on paper. Words: NOTICE   LINE 14   SERVICE
    SUSPENDED UNTIL FURTHER WORD   BY ORDER OF THE YARD OFFICE, IRON JUNCTION
 8. tlm_a1_notice_cutters_reward_512x1024.png
    A reward bill with a rough ink drawing of a lean man in his forties with a
    cut across one eyebrow (not a real person). Words: REWARD   THE TELLICO
    CUTTERS   ROAD-TAKERS ON THE TELLICO ROAD   APPLY TO THE WARDEN OFFICE
 9. tlm_a1_notice_greenwater_512x512.png
    A handwritten notice in pencil and ink. Words: Greenwater is short.
    Carters with flour or beans see S. Vane. Fair weight paid.
10. tlm_a1_notice_red_hollow_512x512.png
    A stamped official notice. Words: RED HOLLOW MINE   CLOSED   NO ENTRY
11. tlm_a1_notice_track_512x512.png
    A printed railway notice. Words: TAMPERING WITH TRACK OR SIGNAL IS A
    HANGING MATTER   REPORT IT TO A MARSHAL
12. tlm_a1_paper_ledger_1024x1024.png
    A blank ruled ledger page, aged, columns drawn in faded ink, no words at
    all. (Only one version needed.)
13. tlm_a1_paper_letter_1024x1024.png
    A blank sheet of cheap letter paper, folded twice and opened flat, aged,
    no words at all. (Only one version needed.)
14. tlm_a1_seal_line_512x512.png
    A round wax seal pressed with a simple device for the railway: a rail
    spike crossed with a key, inside a ring. No words. Centred, on a plain
    flat mid-grey background. [The device is a proposal; give three
    different designs as three files ending _a, _b, _c.]
15. tlm_a1_emblem_unknown_512x512.png
    A small worn emblem as printed on an old travel pass: an abstract mark
    nobody in the valley recognises. Geometric, quiet, unexplained: no words,
    no letters, no numbers, nothing that looks like any known logo. On aged
    card. [Give four different designs as _a, _b, _c, _d. This one matters to
    the story later; keep it plain.]
```

### B2. Character sheets (reference portraits and casting cards)

```text
TASK B2: character sheets for Act I, Chapter 1.

The game builds faces from its own parts, so a picture cannot be imported as a
face. What I need most is the CASTING CARD: a short, exact description that
lets a person or a program choose from a stock of bodies, hair and clothes.
The portrait is a reference to go with it.

Nobody's looks are decided yet. For each person give TWO different options
(A and B) so I can choose. Vary age, build and colouring sensibly between
them; this is a mountain trade valley with people of many backgrounds. Do not
make anyone glamorous. Clothes are worn, mended, practical: canvas, wool,
leather, oilcloth, old railway and work clothing. No armour of recognisable
Fallout design, no brand marks.

For each option give:
1. A portrait, 1024x1024 PNG, head and shoulders, facing three-quarters
   toward the viewer, plain mid-grey background, even light, no text.
   File name: tlm_a1_char_<id>_<a|b>_1024x1024.png
2. A casting card as JSON, exactly this shape:
   {
     "id": "<id>", "option": "a",
     "name": "<name>",
     "sex": "male|female",
     "apparent_age": 0,
     "build": "slight|lean|average|sturdy|heavy",
     "height": "short|average|tall",
     "skin_tone": "<plain words>",
     "hair": {"colour": "", "length": "shaved|short|medium|long", "style": ""},
     "facial_hair": "none|stubble|moustache|short beard|full beard",
     "eyes": "",
     "marks": ["scars, missing teeth, glasses and the like"],
     "clothes": {"head": "", "body": "", "legs": "", "feet": "", "extras": []},
     "carries": [""],
     "manner": ["three short words"],
     "voice": "one line on how they sound"
   }

People (id, name, what is known):
- sheriff, Owen Pritchard: sheriff of Mercy Crossing, an Old Warden. Older,
  spare with words, has buried colleagues.
- gunsmith, Ada Pike: gunsmith, keeps her own books, practical.
- merchant, Silas Vane: runs the trading post. Careful, well-kept. Neither a
  villain nor a saint to look at.
- physician, Miriam Keene: runs the clinic.
- deputy, Jonah Talbot: young deputy at the town gate.
- freight, Corwin Haskell: freight agent. An ordinary clerk.
- caravan_master, Nell Fenwick: owns a wagon and trades along the valley.
- drover, Abel Rudd: her hired hand.
- cutter_lead, Reese Dunmore: leads the Tellico Cutters, road robbers. Makes
  deals. The reward bill shows a cut across one eyebrow.
- marshal, Tobias Gantt: a rail marshal, dead in the wreck. Railway greatcoat,
  dispatch case.
- cutter, (no name): one sheet for an ordinary member of the gang.

Put all the casting cards together in one JSON array at the end of your
answer, as well as beside each portrait.
```

### B3. Short texts (data, ready to import)

```text
TASK B3: short in-world texts for Mercy Crossing and the Tellico road.

Write the batches below. Answer with ONE JSON array and nothing else except
the [NEW] list. Each entry has exactly this shape:
  {
    "id": "tlm_a1_<kind>_<nn>",
    "kind": "notice|letter|ledger|remark|label",
    "by": "<one of the people in the SETTING, or 'unsigned'>",
    "where": "<where it is found or said>",
    "title": "<3 to 6 words>",
    "text": "<the text itself>",
    "new": ["any name, place or fact not in the SETTING"]
  }

Rules for the text:
- Plain ASCII. No line longer than 60 characters; break lines with \n.
- Period voice: plain, dry, practical. No modern slang. No jokes about the
  setting. No speeches. Nobody explains the world.
- Nothing may contradict the SETTING. Nobody knows who forged the ledger.
  Silas Vane is never shown guilty or innocent. Corwin Haskell has done
  nothing wrong.
- Do not use any of these words: Deep, Meridian, Rider, Charter, Open Ledger,
  vault.
- Dates are written as day and month only ("the 9th of May"), never a year.

Batches:
a) 12 notices pinned to the town notice board (kind "notice", 20 to 50 words
   each): lost stock, freight rates, a burial, a boil-water warning, a
   deputy's hours, a wagon for sale, and the like. Two of them may hint, in
   one plain sentence, at trouble elsewhere (Greenwater's food, Red Hollow's
   mine, cut rails near Iron Junction).
b) 4 remarks for each of these six people (kind "remark", at most 18 words
   each, said to a stranger who has just walked up; no questions that need an
   answer): Owen Pritchard, Ada Pike, Silas Vane, Miriam Keene, Jonah Talbot,
   Corwin Haskell. 24 in all.
c) 4 remarks each for Nell Fenwick in three different moods, said in town
   afterwards: grateful (her wagon was saved), bitter (a stranger watched and
   walked on), and cold (she was robbed and saw who shared in it). 12 in all.
   Put the mood in "where".
d) 6 pages for the freight shed (kind "ledger", 6 to 10 lines each, as
   columns of text): received-goods entries signed C. Haskell. Ordinary
   freight: nails, lamp oil, flour, brake shoes NOT among them.
e) 5 letters or scraps found on the road and in the wreck (kind "letter", 40
   to 90 words): a passenger's unfinished letter, a fireman's note about the
   grade, a bill of lading, a child's drawing described in one line, a
   pencilled list of names with one crossed out. None may explain the wreck.
f) 10 labels (kind "label", at most 6 words): crates, sacks, shelf tags and
   door plates in the trading post, the clinic and the freight shed.
```

### B4. Maps and layout (images, with the same thing as numbers)

```text
TASK B4: two maps.

1) THE ROAD TO MERCY: a site plan.
Draw a clear top-down plan, 2048x1024 PNG, north at the top, of a strip of
valley 260 metres long (east to west) and 110 metres wide. Ink and wash on
aged paper, like a surveyor's field sheet, with a scale bar and a north arrow
but NO other words (I will add labels). File: tlm_a1_plan_road_2048x1024.png

The wreck is at the EAST end (the right-hand edge) and the town at the WEST
end (the left-hand edge). Distances below are measured from the east end,
going west along a dirt road that runs beside a single railway track:
- 0 to 40 m: the wreck. A locomotive on its side and five cars off the rails,
  one burnt. A lockbox in the cab. A body beside the third car.
- 40 to 90 m: the road climbs to a low rise with boulders and laurel.
- 90 to 130 m: a dip where the road narrows between a rock cut and the river
  bank. A covered wagon stopped across the road, two brahmin in harness.
- 130 to 180 m: the road straightens. Split-rail fence, a ford marker.
- 180 m: the town gate: two timber posts, a lamp and a bench.
- 180 to 260 m: one street. North side, going west: Warden office (with a
  yard behind), clinic. South side, going west: trading post (larger, with a
  gunsmith's lean-to on its near end), freight shed beside the track. At the
  far end a notice board and a water pump. A wagon yard behind the freight
  shed.

Then give the same plan as JSON, measured in metres from the east end of the
strip going west (x, 0 to 260) and from its south edge (y, 0 to 110):
  [{"id": "", "kind": "building|vehicle|person_spot|prop|road|track|water|
     trigger_area", "x": 0, "y": 0, "width": 0, "depth": 0,
     "facing_degrees": 0, "note": ""}]
Include every item named above, plus sensible spots for these people to
stand: Owen Pritchard, Ada Pike, Silas Vane, Miriam Keene, Jonah Talbot,
Corwin Haskell, Nell Fenwick, Abel Rudd, Reese Dunmore and three more of his
gang.

2) THE BROKEN VALLEYS: a wall map.
A hand-drawn regional map, 2048x2048 PNG, of the kind a sheriff would pin up:
ink on canvas-backed paper, stained, with pencil marks. North at the top.
File: tlm_a1_map_broken_valleys_2048x2048.png, and a second version with no
lettering, ending _blank.
Show mountains as hachures, a river running from the south-east to the
north-west, a railway following it, and roads. Mark and letter these places
only: MERCY CROSSING (centre), TELLICO RIVER (along the river), LINE 14 (along
the railway), IRON JUNCTION (far north-west corner, with an arrow off the
map), GREENWATER (downstream, west), RED HOLLOW (in the hills, south-east).
[The positions of Greenwater and Red Hollow are proposals.]
A pencilled X on the railway about a third of the way from Mercy Crossing
toward the south-east, with no label.
```

---

## Where the answers go

```
assets/incoming/act1/
  textures/     the PNG files of B1, and the maps of B4
  characters/   the portraits of B2, and casting_cards.json
  text/         act1_texts.json (the array from B3)
  layout/       road_plan.json (the array from B4)
  PROVENANCE.md one line per file or batch: made with what, by whom, when
```

Upload them to the repository on the branch `feat/tlm-mq01-graybox` (GitHub's "Add file → Upload files" works), and say so in the chat. Images are large: keep to the sizes asked for.

## What was assumed, for the owner to accept or strike

| # | Assumption in this brief | Where the canon stands |
|---|---|---|
| 1 | The names Tobias Gantt, Nell Fenwick, Abel Rudd, Reese Dunmore, Corwin Haskell and R. Ostrander | Proposed in the Chapter 1 design; not yet in the naming registry (design question Q8) |
| 2 | "Miriam Keene" for the physician | In the registry as provisional; shares a given name with Miriam Kade |
| 3 | Shop signs: "TRADING POST, S. VANE", "A. PIKE, GUNSMITH", "CLINIC, M. KEENE, PHYSICIAN", "FREIGHT, LINE 14, C. HASKELL, AGENT" | Invented wording; the canon names the people and their trades only |
| 4 | A seal for the line: a rail spike crossed with a key | Invented; the canon has no emblem for the railway |
| 5 | The unknown emblem on the torn transit pass | The pass is in the Chapter 1 design as an optional silent seed (Q6). Its look is the owner's to choose; the brief asks for four plain options and explains nothing |
| 6 | Greenwater downstream to the west, Red Hollow in the hills to the south-east, Iron Junction off the map to the north-west | The canon fixes the region and names the places; exact placement is provisional |
| 7 | A reward bill for the Tellico Cutters at the Warden office | Invented; consistent with Pritchard's line that he "hangs road-takers" |
| 8 | The road to Mercy as a strip 260 metres long | A rough walk-through's distances, not the story's ("six hours east") |
| 9 | Nobody in Act I has heard of the Deep or of MERIDIAN | From the canon: Act I shows symptoms only |
| 10 | The player is a stranger to everyone in Mercy Crossing | Proposed in the Chapter 1 design (question Q3) |
| 11 | Reese Dunmore: lean, in his forties, a cut across one eyebrow | Invented for the reward bill; the canon gives him no looks |
| 12 | The wreck: a locomotive and five cars, a lockbox in the cab, the marshal beside the third car | The side quest's ledger names cars 3 and 5 and a cab lockbox; the rest is invented |
