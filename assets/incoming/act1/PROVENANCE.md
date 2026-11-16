# Where each file came from

One line for each file or batch: the file or folder, what made it, who asked for it, and the date.

| File or batch | Made with | By | Date |
|---|---|---|---|
| `characters/tlm_a1_char_*_a_1024x1024.png` (ten portraits, listed below) | ChatGPT image generation (OpenAI), then resized to 1024 by 1024 with Pillow (LANCZOS), as the note that came with them says | The owner, from the brief in `docs/design/ACT1_chatgpt_asset_brief.md` | 2026-11-14 |
| `characters/casting_cards.json` (22 cards: option a and b for each of eleven roles) | ChatGPT | The owner, from the same brief | 2026-11-14 |
| `textures/` (34 PNG files, listed below) | ChatGPT: signs, notices, papers, seals and emblems from its own image generation, cut to size with the lettering drawn on by program (Pillow); the two maps and the road plan drawn by program from its own measurements. As the note that came with the pack says | The owner, from the same brief | 2026-11-14 |
| `text/act1_texts.json` (69 texts: 12 notices, 36 remarks, 6 ledgers, 5 letters, 10 labels) | ChatGPT | The owner, from the same brief | 2026-11-14 |
| `layout/road_plan.json` (45 measured things: buildings, spots for people, boxes, road, track, water) | ChatGPT | The owner, from the same brief | 2026-11-14 |
| `REVIEW_REQUIRED.md` | ChatGPT's own note on the pack: what is in it, what is not, and what to look at before any of it is used | | 2026-11-14 |
| `story/` (`OVERVIEW.md`, `QUESTIONS_FOR_OWNER.md`, `RESEARCH.md`, `characters.json`, `documents.json`, six files under `quests/`, seven under `talk/`) | Claude Code, in a cloud session: written directly by the assistant. The six REAL rows of `RESEARCH.md` are from web search summaries, not from reading the pages | The assistant, at the owner's request to develop more of Act I and make it bolder. Not by the usual writing partner; no other agent took part | 2026-11-16 |

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

## The textures, 2026-11-14

Taken into the repository from the archive the owner sent (`The_Last_Meridian_Act1_Asset_Pack_9.zip`). Each was
checked to be a sound PNG of the size its name gives, with no text inside the file. Every name the brief asked for is
there; the seals come in three versions (a, b, c) and the emblem for "unknown" in four (a to d), for the owner to
choose from. **None is in the game and none is approved.** No way of putting a flat picture into the game has been
built or tried yet.

| File | SHA-256 |
|---|---|
| `tlm_a1_emblem_unknown_512x512_a.png` | `08569d07018d10101f08a6729b6d3dd91de21d5ee5b18a1ae856db7092392456` |
| `tlm_a1_emblem_unknown_512x512_b.png` | `f6bd6913f6a309c55ee78a75ec00f10610e2f18df553542dfd983e855297dafb` |
| `tlm_a1_emblem_unknown_512x512_c.png` | `c0f9a2a1795642c4dba84a594fd91ef4f54de8885d2a0ec6dc3255f64567d2e9` |
| `tlm_a1_emblem_unknown_512x512_d.png` | `984c68328f1b09dd5add3af91530e77d80a70228b22a9fabf1ef8e1c0fc38f83` |
| `tlm_a1_map_broken_valleys_2048x2048.png` | `e3b630b4572b2a1bc7a2ee15f8eb1ccb885bccf2a302d38c02039c208395b82b` |
| `tlm_a1_map_broken_valleys_2048x2048_blank.png` | `39952c83a6a79540cf52bc210461287034f7684c1f273d03b1f83f8673f1ab37` |
| `tlm_a1_notice_cutters_reward_512x1024.png` | `a0c9ceb40d5b2bbf9c2aa03a63205bbbc019bb6ac37ba5a196ae25f934984c29` |
| `tlm_a1_notice_cutters_reward_512x1024_blank.png` | `695e29a8c59ff89c587608a653a45d0e5d954b5356e10bbeb9fb9d53ae9890f9` |
| `tlm_a1_notice_greenwater_512x512.png` | `74db68b7f767839ce42126557db2946afffc6c35cb973975f72dfbbe0f886269` |
| `tlm_a1_notice_greenwater_512x512_blank.png` | `6782a4dbd083aefeee8389e58ebee0d752ecb2a6d81343fc95053b4b3afdc205` |
| `tlm_a1_notice_line14_suspended_512x512.png` | `a86c9abaa28440d24038b97473430161d5183b3d238ab7f70803e1fd70901c97` |
| `tlm_a1_notice_line14_suspended_512x512_blank.png` | `6782a4dbd083aefeee8389e58ebee0d752ecb2a6d81343fc95053b4b3afdc205` |
| `tlm_a1_notice_red_hollow_512x512.png` | `1b4dd0cb61501fbdc571ab7800b0a0b6eb11b8ce7095b45fc2a4943419fada65` |
| `tlm_a1_notice_red_hollow_512x512_blank.png` | `9c068d8e8fe9bc577e5e07f10641913be3b2cb4e283f4554d166b1e65b376ca6` |
| `tlm_a1_notice_track_512x512.png` | `9a30a975a70523948cc136d84c7c0fe3f6db6f6bb46a5fc35f24eec153ecd22d` |
| `tlm_a1_notice_track_512x512_blank.png` | `259e74eb7aee1f1e1541040dcfb399deb97cffedc6c9a95dac0fccc6c0d50cb6` |
| `tlm_a1_paper_ledger_1024x1024.png` | `7bd1df7db074775ca7e236593b9211880b9661b87a0a34303d994e14908e5b71` |
| `tlm_a1_paper_letter_1024x1024.png` | `a547b49a8046e6b8cfd047a9e9301d0d516f5412396e77855cdac1d6ddaed3f6` |
| `tlm_a1_plan_road_2048x1024.png` | `463ca147b9a3f7e374749ab6a8df9e1ce274bcd55fb87cc68c994eed46e4d979` |
| `tlm_a1_seal_line_512x512_a.png` | `bf868db42266dc8fd4d3b521f1ae9a64a11be3894ad6b04fb529ef5324d20709` |
| `tlm_a1_seal_line_512x512_b.png` | `6df91ff1e41d61961f7f77734ee921ca9c621ac60274a4fbf8940969379b3a9a` |
| `tlm_a1_seal_line_512x512_c.png` | `a1a6a21cfdb7e9373a8ae779370ab9513db53f515e211e1d7b7f7d03cc688fcd` |
| `tlm_a1_sign_clinic_1024x512.png` | `a482fb47d7de93dfe5213c4994d755d5049c9913320ae3c91fd651011bf72b84` |
| `tlm_a1_sign_clinic_1024x512_blank.png` | `6d1b6349389d24595f06fa54563f715ae4267c5f0ffda88adcac6d29f7eab8f0` |
| `tlm_a1_sign_freight_1024x512.png` | `e35ee42f3b15f0042b38de8ad7cd8f9e7fbe9826f3a9f4be201e78c01ed8c149` |
| `tlm_a1_sign_freight_1024x512_blank.png` | `4f2a999ff95ae7664d4647083be8b867def59e85f8c11cc2a2c4d9f3cb0c9569` |
| `tlm_a1_sign_gunsmith_1024x512.png` | `c2b24ae488b594e7c2a0d37dbe714ae3c28bbd920c17b407fe82d3e717ecd7ad` |
| `tlm_a1_sign_gunsmith_1024x512_blank.png` | `0ba70fc8f928fa52bb4e80976d7be986aa14238611ce624c5c71e502c46c3a22` |
| `tlm_a1_sign_mercy_crossing_2048x512.png` | `1df352140d2d4f85ce9e9510ff67e6861ac3e581d6bd298ee62e70d03d6e5b76` |
| `tlm_a1_sign_mercy_crossing_2048x512_blank.png` | `18a3b98852951d14dcdcff23b391d41796ce3dc7bdeff25111829b61def0e7d5` |
| `tlm_a1_sign_trading_post_1024x512.png` | `12e146ed4ecf24df54991802f40bbd670d3c4b71547c060f3154d639c902b00f` |
| `tlm_a1_sign_trading_post_1024x512_blank.png` | `85348ced1e2e732de3ea379fdaa81a03bc58ace3de3b0cb82cdfc0aaf2ce955a` |
| `tlm_a1_sign_warden_office_1024x512.png` | `91a1cd9d8b6fe463e14c9cfe2f36f68c0518e62f486edf3daead3a15176b4088` |
| `tlm_a1_sign_warden_office_1024x512_blank.png` | `6d4707151aeaa68072a506b5a89e4abf768386a0774b1a69966eae3c604e3ed1` |
