# Worked example, second talk format

The talk of the first worked example (`../story_intake_example/talk/tlm_mq01.json`), with nothing changed but the format:
`tlm-talk-2`, and on every boxed line an `entry` that says whether a person may open with it.

    python3 tools/check_story_intake.py --self-test docs/design/story_intake_example_v2

| Line | entry | Why |
|---|---|---|
| `dunmore_hold` | true | What Dunmore says while the hold-up is unsettled |
| `dunmore_share`, `dunmore_breaks`, `dunmore_turns`, `dunmore_deal` | false | Said only when one of his buttons leads on to them |
| `dunmore_after` | true | What he says once it is settled. Priority 0, below `dunmore_hold` at 10 |
| `nell_silent` | none | An aside. An aside is not said in a box and carries no `entry` |
| `pritchard_case` | true | What Pritchard says when the case can be put to him |
| `pritchard_reported` | false | Said only after the button that reports it |

The first example is not changed and is still checked as `tlm-talk-1`. The format is described in
[STORY_INTAKE.md](../STORY_INTAKE.md); the rules behind it are in
[ACT1_ENTRY_SELECTION_CONTRACT.md](../ACT1_ENTRY_SELECTION_CONTRACT.md). Nothing is built from this folder.
