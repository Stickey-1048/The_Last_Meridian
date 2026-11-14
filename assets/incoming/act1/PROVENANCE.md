# Where each file came from

One line for each file or batch: the file or folder, what made it, who asked for it, and the date.

| File or batch | Made with | By | Date |
|---|---|---|---|
| `characters/tlm_a1_char_*_a_1024x1024.png` (ten portraits, listed below) | ChatGPT image generation (OpenAI), then resized to 1024 by 1024 with Pillow (LANCZOS), as the note that came with them says | The owner, from the brief in `docs/design/ACT1_chatgpt_asset_brief.md` | 2026-11-14 |
| `characters/casting_cards.json` (22 cards: option a and b for each of eleven roles) | ChatGPT | The owner, from the same brief | 2026-11-14 |

## The ten portraits, 2026-11-14

Reference pictures only: what a person might look like, for casting and for the eye. They are not in the game, the
plugin does not use them, and none is approved. The people in the rough cut still wear the faces of the game's
settlers. Each file is `tlm_a1_char_<role>_a_1024x1024.png` and goes with the card of that role and option "a" in
`casting_cards.json`. Taken into the repository from the archive the owner sent
(`The_Last_Meridian_10_Portraits_GitHub_Ready.zip`); each was checked to be a sound PNG of 1024 by 1024 with no text
inside it, and its SHA-256 is the one the archive's own note gave.

| File | Card | SHA-256 |
|---|---|---|
| `tlm_a1_char_caravan_master_a_1024x1024.png` | caravan_master, option a (Nell Fenwick) | `5c3c5f1ac39e1520e7a874f819852706629df7d049fec47139b93e92a6fea747` |
| `tlm_a1_char_cutter_lead_a_1024x1024.png` | cutter_lead, option a (Reese Dunmore) | `b6151e078ebfdd04af4a51946f81e2e7ed906237e78b8e1b3545f420327ba661` |
| `tlm_a1_char_deputy_a_1024x1024.png` | deputy, option a (Jonah Talbot) | `b974316cf9c66dac367a8d2ee445894667530353a2b6d919418a22998a6bd2dd` |
| `tlm_a1_char_drover_a_1024x1024.png` | drover, option a (Abel Rudd) | `f97d7e8017df554ea3913960f52dcc313534e8ceb97dcb38aa576cb4e3401216` |
| `tlm_a1_char_freight_a_1024x1024.png` | freight, option a (Corwin Haskell) | `3195af17a9a9a2b288fb7efdbc3891a5ea3a73808fd77efceb9ac812820575dd` |
| `tlm_a1_char_gunsmith_a_1024x1024.png` | gunsmith, option a (Ada Pike) | `aee2bc8728479798b33a8302e6352d9bc812f9fc32d48dba16240e33ef4f6412` |
| `tlm_a1_char_marshal_a_1024x1024.png` | marshal, option a (Tobias Gantt) | `081d2bfcbdc6fe10d538d2f7688faedc065edf42bbfd49d3bf51fb16c5b90f7a` |
| `tlm_a1_char_merchant_a_1024x1024.png` | merchant, option a (Silas Vane) | `d81084a2c53c221c83ad9698f2d742ba1f8f674f9b3b0688366090dd0e4aa254` |
| `tlm_a1_char_physician_a_1024x1024.png` | physician, option a (Miriam Keene) | `ec3abdf195c543394412064df3fef2e4e9828013ef7cb2afbe40c80ceaef9a68` |
| `tlm_a1_char_sheriff_a_1024x1024.png` | sheriff, option a (Owen Pritchard) | `cce6cd71348000a1c6fbe1460bef1a8bb96490d97692656158df78c1dd1902a8` |

Not there: a portrait for the role `cutter` (the unnamed Tellico Cutter), and any portrait for an option "b" card.
