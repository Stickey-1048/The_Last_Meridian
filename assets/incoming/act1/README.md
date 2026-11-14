# Incoming material for Act I

Things made outside the repository for Act I, waiting to be taken into the plugin.
What to make, at which sizes and under which names is in
[docs/design/ACT1_chatgpt_asset_brief.md](../../../docs/design/ACT1_chatgpt_asset_brief.md).

| Folder | Holds |
|---|---|
| `textures/` | Flat PNG images: signs, posters, notices, papers, emblems, maps |
| `characters/` | Reference portraits and `casting_cards.json` |
| `text/` | `act1_texts.json` |
| `layout/` | `road_plan.json` |

Rules:

- Original work only. Nothing from Fallout or any other game, no real brands, no real people.
- Every file or batch gets a line in [PROVENANCE.md](PROVENANCE.md).
- Nothing here is canon until the owner says so. A name or fact that a generator
  invented stays out of the plugin until it has been accepted.

## 2026-11-14 generated pack (external staging)
A ChatGPT-created ZIP has been prepared in the accompanying chat, to upload at this path after owner review. The GitHub text connector does not accept the large PNG set as a direct attachment, so the ZIP's binary and JSON contents are **NOT yet committed** to the branch. Do not assume that files are present merely because this README mentions them.

ZIP contents (all under `assets/incoming/act1/`):
- `textures/`: 34 exact-dimension PNGs (11 lettered signs/notices and their 11 blanks, 2 paper textures, 3 seal experiments, 4 geometric emblem experiments, 3 maps).
- `characters/casting_cards.json`: 22 alternate casting cards, 11 role IDs each with A and B. **No individual portrait PNGs yet**.
- `text/act1_texts.json`: 69 import-ready texts: 12 town notices, 36 NPC remarks, 6 freight ledgers, 5 road/wreck letters, 10 shelf and crate labels.
- `layout/road_plan.json`: 45 measured placements and trigger regions in a 260 m by 110 m schematic.
- `PROVENANCE.md` and `REVIEW_REQUIRED.md` documenting generation, source art, canon risks and limitations.

**Before using:** Owner reviews proposed names/positions, uploads extracted files via GitHub or their working copy, and asks Claude to validate each field against the plugin builder spec. Image imports remain untested. The road strip is a compressed walkthrough and does not establish literal journey time to the wreck. No game binaries or tested Papyrus scripts changed here.
