# Story material for Act I, waiting to be taken in

**16 November, after the decisions:** the JSON below this line has since been revised to [the adopted creative decisions](../../../../docs/design/ACT1_CREATIVE_DECISIONS_2026-11-16.md). It is a revised proposal awaiting narrative acceptance and independent engineering review, not an accepted or playable chapter. What was done and what is missing: [the receipt](../../../../docs/design/ACT1_CHARLES_REVISION_RECEIPT.md).

**16 November, after packet 2:** writing closure packet 2 has been applied and the talk moved to the second format. One supplied line is withheld. What was done, what was run and what is still open: [the packet 2 receipt](../../../../docs/design/ACT1_CHARLES_PACKET2_RECEIPT.md). Still a proposal awaiting acceptance; nothing is built from it.

**16 November, after packet 3:** writing closure packet 3 has been applied in full, with the three reviewed source repairs kept. No supplied line is withheld. What was done, what was run and which runtime gates remain: [the packet 3 receipt](../../../../docs/design/ACT1_CHARLES_PACKET3_RECEIPT.md). Still a proposal awaiting acceptance; nothing is built from it.

Characters, quests, talk and papers written outside the repository. The format is
[docs/design/STORY_INTAKE.md](../../../../docs/design/STORY_INTAKE.md); a worked example is in
`docs/design/story_intake_example/`.

    python3 tools/check_story_intake.py --strict assets/incoming/act1/story

Nothing here is canon until the owner accepts it, and nothing is built from a file that has not been accepted.

## 2026-11-16: Chapters 2 to 4, a bolder proposal

Written in a Claude Code session at the owner's request, not by the usual writing partner. Start with
[OVERVIEW.md](OVERVIEW.md); how the owner's questions were resolved is in [QUESTIONS_FOR_OWNER.md](QUESTIONS_FOR_OWNER.md).

- `characters.json`: 26 people (7 of the plugin's, 19 it does not have). Four display names changed; ids kept.
- `quests/`: six quests (`mq02`, `mq02a`, `mq02b`, `mq02c`, `mq03`, `mq04`), 82 stages, 40 new flags.
- `talk/`: 227 lines in seven files, in the second talk format (`tlm-talk-2`).
- `documents.json`: 23 papers.
- `RESEARCH.md`: nine rows, unchanged; the six REAL rows are from web search summaries read on 2026-11-16, not from the full pages, and are not verified.

It passes the strict check. It is not accepted, and nothing has been built from it. A format pass is not a compile or a game test.

