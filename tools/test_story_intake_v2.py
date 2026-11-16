#!/usr/bin/env python3
"""The fixtures of docs/design/ACT1_ENTRY_SELECTION_CONTRACT.md, for the tlm-talk-2 talk format.

  python3 tools/test_story_intake_v2.py

They run the intake check (tools/check_story_intake.py) and the reference selector
(tools/story_intake_select.py) on small folders made here, on the two worked examples and on the
revised Act I folder.

What a pass means: the check refuses what the contract says it must refuse, for the reason it is
wrong, and the selector says what the contract says it must say. In these tests a stage that a
button sets is only noted as set: the quest's own doing is not played. A pass is not a compile, not
a game test, and shows nothing about scenes, timers, inventories or who is standing where.
"""
import contextlib
import hashlib
import io
import importlib.util
import json
import sys
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_story_intake as intake                             # noqa: E402
import story_intake_select as select                            # noqa: E402

V1_EXAMPLE = ROOT / "docs/design/story_intake_example"
V2_EXAMPLE = ROOT / "docs/design/story_intake_example_v2"
STORY = ROOT / "assets/incoming/act1/story"
# The first worked example as it was before this format existed: it must not change.
V1_EXAMPLE_SHA256 = {       # of each file with line endings as LF, at 495de2a
    "RESEARCH.md": "0767a64d3ea4401b4c25a85965f857ecc534d369be07d712c31a59df547b75ba",
    "characters.json": "185281142fd3aad33458360eaf7d0177b5b8049cfc4477c87f0c233c9555c0f9",
    "documents.json": "f31ebec24fe8b05b147e7c4bbb89098b32370cad42662ebfe62d588787198f9d",
    "quests/tlm_sq01.json": "7fd0be7e7146a1ee3ead8f33325666ac1a23c9b3e45563953c07f763f4a8d438",
    "talk/tlm_mq01.json": "1d25ad8ed97194e2113a143e507ba4d5cc93f2c9b5422036300664a779cc3880",
}


def box(lid, speaker="pritchard", entry=True, priority=0, when=(), buttons=None, text="TEST: a line.", **more):
    line = {"id": lid, "speaker": speaker, "status": "new", "entry": entry, "priority": priority, "when": list(when), "text": text, "sources": []}
    if entry is None:
        del line["entry"]
    if buttons is not None:
        line["buttons"] = buttons
    line.update(more)
    return line


def talk(*lines, version="tlm-talk-2", quest="TLM_MQ01"):
    return json.dumps({"format": version, "quest": quest, "lines": list(lines)})


def problems(files):
    return intake.Intake(files).run()


class Refused(unittest.TestCase):
    """What the check must refuse, and why."""

    def refused(self, files, reason):
        found = problems(files)
        self.assertTrue(any(reason in p for p in found), "expected a refusal saying %r; the check said %r" % (reason, found))

    def test_a_sound_small_folder_passes(self):
        self.assertEqual(problems({"talk/a.json": talk(box("a", buttons=[{"label": "x", "then": "b"}]), box("b", entry=False))}), [])

    def test_missing_entry(self):
        self.refused({"talk/a.json": talk(box("a", entry=None))}, "does not say whether it is an entry")

    def test_entry_must_be_a_real_yes_or_no(self):
        for wrong in ("true", "false", 1, 0, None, [], 1.0):
            line = box("a")
            line["entry"] = wrong
            self.refused({"talk/a.json": talk(line)}, "entry is true or false")

    def test_entry_on_an_aside(self):
        self.refused({"talk/a.json": talk(box("a"), box("s", kind="aside"))}, "an aside is not said in a box")

    def test_an_aside_without_entry_passes(self):
        self.assertEqual(problems({"talk/a.json": talk(box("a"), box("s", entry=None, kind="aside"))}), [])

    def test_first_format_with_entry(self):
        self.refused({"talk/a.json": talk(box("a"), version="tlm-talk-1")}, "which tlm-talk-1 does not have")

    def test_first_format_without_entry_still_passes(self):
        self.assertEqual(problems({"talk/a.json": talk(box("a", entry=None), box("b", entry=None), version="tlm-talk-1")}), [])

    def test_mixed_formats(self):
        files = {"talk/a.json": talk(box("a")), "talk/b.json": talk(box("b", speaker="pike", entry=None), version="tlm-talk-1")}
        self.refused(files, "a folder uses one format")

    def test_an_empty_file_of_the_other_format_is_not_a_mix(self):
        files = {"talk/a.json": talk(box("a")), "talk/town.json": json.dumps({"format": "tlm-talk-1", "quest": None, "lines": []})}
        self.assertEqual(problems(files), [])

    def test_unknown_format(self):
        self.refused({"talk/a.json": talk(box("a"), version="tlm-talk-3")}, "format is not tlm-talk-1 or tlm-talk-2")

    def test_continuation_with_a_priority(self):
        files = {"talk/a.json": talk(box("a", buttons=[{"label": "x", "then": "b"}]), box("b", entry=False, priority=999))}
        self.refused(files, "is a continuation")

    def test_same_speaker_same_priority_in_two_files(self):
        one = talk(box("a", priority=60, when=["mq01 done 20"]))
        two = talk(box("b", priority=60, when=["mq01 notdone 20"]))        # they could never both hold; that is not accepted as a reason
        forward, backward = {"talk/a.json": one, "talk/b.json": two}, {"talk/b.json": two, "talk/a.json": one}
        self.refused(forward, "strictly ordered across the folder")
        self.assertEqual(sorted(problems(forward)), sorted(problems(backward)))

    def test_same_priority_for_two_speakers_is_fine(self):
        self.assertEqual(problems({"talk/a.json": talk(box("a", priority=60), box("b", speaker="pike", priority=60))}), [])

    def test_missing_target(self):
        self.refused({"talk/a.json": talk(box("a", buttons=[{"label": "x", "then": "nowhere"}]))}, "which is no line")

    def test_aside_target(self):
        files = {"talk/a.json": talk(box("a", buttons=[{"label": "x", "then": "s"}]), box("s", entry=None, kind="aside"))}
        self.refused(files, "which is an aside")

    def test_isolated_ring_of_continuations(self):
        ring = [box("b", entry=False, buttons=[{"label": "x", "then": "c"}]), box("c", entry=False, buttons=[{"label": "x", "then": "b"}])]
        self.refused({"talk/a.json": talk(box("a"), *ring)}, "no entry leads on to")

    def test_a_ring_an_entry_leads_into_passes(self):
        ring = [box("b", entry=False, buttons=[{"label": "x", "then": "c"}]), box("c", entry=False, buttons=[{"label": "x", "then": "b"}])]
        self.assertEqual(problems({"talk/a.json": talk(box("a", buttons=[{"label": "x", "then": "b"}]), *ring)}), [])

    def test_a_continuation_reached_only_through_a_speech_result(self):
        check = {"label": "x", "check": "speech", "pass": {"then": "b"}, "fail": {"then": "c"}}
        self.assertEqual(problems({"talk/a.json": talk(box("a", buttons=[check]), box("b", entry=False), box("c", entry=False))}), [])


class Selected(unittest.TestCase):
    """What the selector must say, on small folders."""

    def test_no_eligible_entry(self):
        s = select.Selector({"talk/a.json": talk(box("a", when=["mq01 done 20"], buttons=[{"label": "x", "then": "b"}]), box("b", entry=False))})
        state = select.State()
        r = s.greet("pritchard", state)
        self.assertIsNone(r.line)
        self.assertEqual(r.effects, [])
        self.assertIn("no eligible entry", r.diagnostic)
        self.assertEqual(state.stages, {})

    def test_a_continuation_never_greets_even_alone(self):
        s = select.Selector({"talk/a.json": talk(box("a", when=["mq01 done 20"], buttons=[{"label": "x", "then": "b"}]), box("b", entry=False))})
        self.assertIsNone(s.greet("pritchard", select.State()).line)

    def test_equal_highest_entries_past_the_check(self):
        lines = [box("a", priority=5), box("b", priority=5), box("c", priority=1)]
        for order in (lines, lines[::-1]):
            files = {"talk/a.json": talk(*order)}
            self.assertTrue(problems(files))                                # the check refuses it
            r = select.Selector(files, validate=False).greet("pritchard", select.State())
            self.assertIsNone(r.line)
            self.assertEqual(r.effects, [])
            self.assertIn("ambiguous", r.diagnostic)
            self.assertIn("a, b", r.diagnostic)                             # the same words whichever came first

    def test_the_check_refused_folder_is_refused_by_the_selector_too(self):
        with self.assertRaises(ValueError):
            select.Selector({"talk/a.json": talk(box("a", priority=5), box("b", priority=5))})

    def test_the_first_format_is_not_guessed_at(self):
        with self.assertRaises(ValueError):
            select.Selector({"talk/a.json": talk(box("a", entry=None), version="tlm-talk-1")})

    def folder(self):
        return {"talk/a.json": talk(
            box("high", priority=90, when=["mq01 done 20"]),
            box("menu", priority=50, when=["mq01 done 20", "mq01 notdone 50"], buttons=[
                {"label": "to the guarded entry", "then": "guarded"},
                {"label": "an effect that shuts the target", "do": ["mq01 set 50"], "then": "shut_after"},
                {"label": "an effect, then a target", "do": ["mq01 set 30", "give caps 5"], "then": "open_after"},
                {"label": "an effect and no target", "do": ["mq01 set 31"]}]),
            box("guarded", priority=10, when=["mq01 done 20"]),
            box("shut_after", entry=False, when=["mq01 notdone 50"]),
            box("open_after", entry=False, when=["mq01 done 30"]),
            box("fallback", priority=0))}

    def test_a_direct_target_is_not_hijacked_by_a_higher_entry(self):
        s, state = select.Selector(self.folder()), select.State(stages={"mq01": {20}})
        self.assertEqual(s.greet("pritchard", state).line, "high")           # the greeting is the highest entry
        r = s.press("menu", 0, state)
        self.assertEqual(r.line, "guarded")                                   # the button goes where it says, though "high" outranks it
        self.assertEqual(r.effects, [])

    def test_conditions_are_asked_after_the_effects(self):
        s, state = select.Selector(self.folder()), select.State(stages={"mq01": {20}})
        r = s.press("menu", 2, state)
        self.assertEqual((r.line, r.effects, r.diagnostic), ("open_after", ["mq01 set 30", "give caps 5"], None))
        self.assertEqual(state.caps, 5)

    def test_false_target_after_effects(self):
        s, state = select.Selector(self.folder()), select.State(stages={"mq01": {20}})
        r = s.press("menu", 1, state)
        self.assertIsNone(r.line)                                             # no target, and no default in its place
        self.assertEqual(r.effects, ["mq01 set 50"])                          # counted once
        self.assertIn("shut_after is not available", r.diagnostic)
        self.assertIn("mq01 set 50", r.diagnostic)
        self.assertIn("not undone", r.diagnostic)
        self.assertTrue(state.done("mq01", 50))                               # nothing was rolled back

    def test_a_stale_menu_does_nothing(self):
        s, state = select.Selector(self.folder()), select.State(stages={"mq01": {20}})
        s.press("menu", 1, state)                                             # sets 50, which makes "menu" itself invalid
        before = {k: set(v) for k, v in state.stages.items()}
        r = s.press("menu", 3, state)
        self.assertIsNone(r.line)
        self.assertEqual(r.effects, [])
        self.assertIn("no longer valid", r.diagnostic)
        self.assertEqual(state.stages, before)

    def test_a_button_with_no_target_closes(self):
        s, state = select.Selector(self.folder()), select.State(stages={"mq01": {20}})
        r = s.press("menu", 3, state)
        self.assertEqual((r.line, r.effects, r.diagnostic), (None, ["mq01 set 31"], None))

    def test_implicit_continue_closes_without_effects(self):
        for authored in (None, []):
            s = select.Selector({"talk/a.json": talk(box("a", buttons=authored))})
            st = select.State()
            r = s.press("a", 0, st)
            self.assertEqual((r.line, r.effects, r.diagnostic), (None, [], None))
            self.assertEqual(st.stages, {})
            self.assertEqual(st.caps, 0)
            for index in (-1, 1, True, "0"):
                with self.assertRaises(ValueError):
                    s.press("a", index, st)

    def test_implicit_continue_still_checks_a_stale_source(self):
        s = select.Selector({"talk/a.json": talk(box("a", when=["mq01 done 20"]))})
        r = s.press("a", 0, select.State())
        self.assertIsNone(r.line)
        self.assertEqual(r.effects, [])
        self.assertIn("no longer valid", r.diagnostic)

    def test_a_speech_check_takes_one_branch_once(self):
        check = {"label": "x", "check": "speech", "pass": {"do": ["mq01 set 31"], "then": "won"}, "fail": {"do": ["mq01 set 37"], "then": "lost"}}
        s = select.Selector({"talk/a.json": talk(box("a", buttons=[check]), box("won", entry=False), box("lost", entry=False))})
        for passed, line, stage, other in ((True, "won", 31, 37), (False, "lost", 37, 31)):
            state = select.State()
            r = s.press("a", 0, state, speech=passed)
            self.assertEqual((r.line, r.effects), (line, ["mq01 set %d" % stage]))
            self.assertFalse(state.done("mq01", other))
        with self.assertRaises(ValueError):
            s.press("a", 0, select.State())                                    # a check with no result is not guessed

    def test_conditions_use_the_checks_own_grammar(self):
        s = select.Selector(self.folder())
        with self.assertRaises(ValueError):
            s.holds("if the player is kind", select.State())
        with self.assertRaises(ValueError):
            s.holds("outcome is won", select.State())
        st = select.State(stages={"mq01": {20}}, words={"outcome": "saved"}, counters={"truth": 2}, flags={"yard_alerted"}, dead={"abel"})
        for text, want in (("mq01 done 20", True), ("mq01 notdone 20", False), ("outcome is saved", True), ("outcome isnot saved", False),
                           ("method is none", True), ("debrief is saved", False), ("truth >= 2", True), ("truth < 2", False),
                           ("alive nell", True), ("dead abel", True), ("alive abel", False), ("flag yard_alerted", True), ("notflag yard_alerted", False)):
            self.assertEqual(s.holds(text, st), want, text)


def story():
    return select.from_folder(STORY)


class RevisedActOne(unittest.TestCase):
    """The histories the contract names, on the revised Act I folder as it stands."""

    @classmethod
    def setUpClass(cls):
        cls.files = intake.read_folder(STORY)
        cls.s = select.Selector(cls.files)

    def test_the_folder_passes_the_strict_check(self):
        self.assertEqual(intake.Intake(self.files, strict=True).run(), [])

    def test_every_talk_file_is_the_second_format(self):
        for path, text in self.files.items():
            if path.startswith("talk/"):
                self.assertEqual(json.loads(text)["format"], "tlm-talk-2", path)

    def test_the_five_guarded_targets_are_still_greetings(self):
        targets = {o.get("then") for l in self.s.lines.values() for b in l.get("buttons", [])
                   for o in ([b["pass"], b["fail"]] if "check" in b else [b])}
        for lid in ("tarrow_in_cut", "dole_sermon", "tarrow_ran", "tarrow_backed", "hatcher_table"):
            self.assertIs(self.s.lines[lid]["entry"], True, lid)
            self.assertTrue(self.s.lines[lid]["when"], lid)
            self.assertIn(lid, targets, lid)

    def test_the_named_follow_ons_are_continuations(self):
        for lid in ("dole_name", "dole_silver", "dole_share", "dole_face", "quill_fine", "quill_shamed"):
            self.assertIs(self.s.lines[lid]["entry"], False, lid)
        self.assertNotIn("mq02a done 55", self.s.lines["dole_name"]["when"])
        self.assertEqual(self.s.lines["quill_shamed"]["when"], ["mq02c done 13"])

    # ---- Dole
    def test_dole_negative_history(self):
        """40, the sermon, the share, accepted (43), the name never learned (55 absent)."""
        st = select.State(stages={"mq02a": {10, 20, 30, 40}})
        self.assertEqual(self.s.greet("dole", st).line, "dole_sermon")
        r = self.s.press("dole_sermon", 1, st)                                 # "What's my share?"
        self.assertEqual(r.line, "dole_share")
        r = self.s.press("dole_share", 0, st)                                  # "Done."
        self.assertEqual(r.effects, ["mq02a set 43", "give caps 150"])
        self.assertIsNone(r.line)
        self.assertFalse(st.done("mq02a", 55))
        again = self.s.greet("dole", st)
        self.assertEqual(again.line, "dole_default")                           # an authored entry; never the name, the share, the silver or the threat
        self.assertNotIn(again.line, ("dole_name", "dole_share", "dole_silver", "dole_face", "dole_sermon"))

    def test_dole_positive_history(self):
        """40 and nothing settled: the sermon, then who he is. The name is said with 55 still unset; its button sets 55."""
        st = select.State(stages={"mq02a": {10, 20, 30, 40}})
        r = self.s.press("dole_sermon", 2, st)                                 # "They buried you. Who are you?"
        self.assertEqual((r.line, r.effects), ("dole_name", []))
        self.assertFalse(st.done("mq02a", 55))
        r = self.s.press("dole_name", 0, st)                                   # "And the silver in your plate?"
        self.assertEqual((r.line, r.effects), ("dole_silver", ["mq02a set 55"]))
        self.assertTrue(st.done("mq02a", 55))
        self.assertEqual(self.s.greet("dole", st).line, "dole_sermon")         # coming back: entries only
        st.stages["mq02a"].add(41)
        self.assertEqual(self.s.greet("dole", st).line, "dole_default")

    # ---- Quill
    def test_quill_negative_history(self):
        """10, the fine, paid (12); no docket held, no hearing (13)."""
        st = select.State(stages={"mq02c": {10}})
        self.assertEqual(self.s.greet("quill", st).line, "quill_court")
        self.assertNotIn("Show the 2298 docket. Demand a hearing.", [b["label"] for b in self.s.lines["quill_court"]["buttons"]])
        r = self.s.press("quill_court", 0, st)                                 # "What's the fine for a neck?"
        self.assertEqual(r.line, "quill_fine")
        r = self.s.press("quill_fine", 0, st)                                  # "Sixty. Cut him down."
        self.assertEqual(r.effects, ["mq02c set 12"])
        self.assertFalse(st.done("mq02c", 13))
        again = self.s.greet("quill", st)
        self.assertEqual(again.line, "quill_default")
        self.assertNotIn(again.line, ("quill_shamed", "quill_fine", "quill_court", "quill_court_docket"))

    def test_quill_positive_history(self):
        """10 with the docket in hand: the docket court outranks the ordinary one; the challenge sets 13 once; the supplied reply follows."""
        st = select.State(stages={"mq02c": {10}}, flags={"docket_2298_held"})
        self.assertEqual(self.s.greet("quill", st).line, "quill_court_docket")
        labels = [b["label"] for b in self.s.lines["quill_court_docket"]["buttons"]]
        r = self.s.press("quill_court_docket", labels.index("Show the 2298 docket. Demand a hearing."), st)
        self.assertEqual((r.line, r.effects, r.diagnostic), ("quill_shamed", ["mq02c set 13"], None))
        self.assertEqual(self.s.greet("quill", st).line, "quill_default")       # the court is over; the reply is not a greeting

    def test_quill_without_the_docket_in_hand(self):
        """Stage 16 says the copy was once taken. Without the flag the ordinary court is what is said."""
        st = select.State(stages={"mq02c": {10, 16}})
        self.assertEqual(self.s.greet("quill", st).line, "quill_court")

    def test_the_hearing_reply_is_shut_unless_13_is_set(self):
        self.assertFalse(self.s.valid(self.s.lines["quill_shamed"], select.State(stages={"mq02c": {10}})))

    def truce_at_authority(self, talbot=False):
        st = select.State(stages={"mq03": {10, 40}}, dead={"pritchard"} if talbot else ())
        demand = self.s.greet("brigg", st).line
        expected = "brigg_demand_talbot" if talbot else "brigg_demand"
        self.assertEqual(demand, expected)
        button = next(i for i, b in enumerate(self.s.lines[demand]["buttons"]) if "truce" in b["label"])
        r = self.s.press(demand, button, st)
        authority = "talbot_truce" if talbot else "pritchard_truce"
        for _ in range(4):
            if r.line == authority:
                self.assertFalse(st.done("mq03", 43))
                return st, authority
            self.assertIsNotNone(r.line)
            r = self.s.press(r.line, 0, st)
        self.fail("normal truce did not reach its authority in the bounded chain")

    def test_both_truce_authorities_recheck_death_before_effects(self):
        for talbot in (False, True):
            for dead in ("brigg", "whitcomb", "belden", "grey", "talbot" if talbot else "pritchard"):
                st, authority = self.truce_at_authority(talbot)
                st.dead.add(dead)
                r = self.s.press(authority, 0, st)
                self.assertEqual(r.effects, [], (talbot, dead))
                self.assertIsNone(r.line)
                self.assertFalse(st.done("mq03", 43))
                self.assertIn("no longer valid", r.diagnostic)

    def test_both_truce_authorities_recheck_changed_resolution_before_effects(self):
        for talbot in (False, True):
            for resolved in (41, 42, 43, 44, 70):
                st, authority = self.truce_at_authority(talbot)
                st.stages["mq03"].add(resolved)
                before = set(st.stages["mq03"])
                r = self.s.press(authority, 0, st)
                self.assertEqual(r.effects, [], (talbot, resolved))
                self.assertIsNone(r.line)
                self.assertEqual(st.stages["mq03"], before)

    def test_both_normal_truce_paths_still_reach_briggs_acknowledgement(self):
        for talbot in (False, True):
            st, authority = self.truce_at_authority(talbot)
            concession = "brigg_truce_concession_" + ("talbot" if talbot else "pritchard")
            r = self.s.press(authority, 0, st)                                 # the local officer's Continue records nothing
            self.assertEqual((r.line, r.effects, r.diagnostic), (concession, [], None))
            self.assertFalse(st.done("mq03", 43))                              # Brigg's concession is on the screen and 43 is still unset
            r = self.s.press(concession, 0, st)                                # only the Continue under it records 43
            self.assertEqual((r.line, r.effects, r.diagnostic), ("brigg_rifles", ["mq03 set 43"], None))
            self.assertTrue(st.done("mq03", 43))
            self.assertEqual(self.s.greet("brigg", st).line, "brigg_rifles")

    def test_dead_or_superseded_brgg_cannot_deliver_the_acknowledgement(self):
        for dead, other in (({"brigg"}, None), ((), 41), ((), 42), ((), 44), ((), 70)):
            stages = {10, 40, 43} | ({other} if other is not None else set())
            st = select.State(stages={"mq03": stages}, dead=dead)
            self.assertFalse(self.s.valid(self.s.lines["brigg_rifles"], st))
            self.assertNotEqual(self.s.greet("brigg", st).line, "brigg_rifles")

    # ---- a guarded target that is also a greeting
    def test_tarrow_in_cut_both_ways(self):
        st = select.State(stages={"mq02a": {10, 20, 30, 40}})
        self.assertEqual(self.s.greet("tarrow", st).line, "tarrow_in_cut")     # as a greeting
        labels = [b["label"] for b in self.s.lines["dole_sermon"]["buttons"]]
        r = self.s.press("dole_sermon", labels.index("(Go back to the footplate)"), st)
        self.assertEqual(r.line, "tarrow_in_cut")                              # and by the button that leads to it
        st.stages["mq02a"].add(44)
        self.assertEqual(self.s.greet("tarrow", st).line, "tarrow_backed")

    # ---- order does not matter
    def test_reordered_files_and_lines(self):
        turned = {}
        for path in reversed(sorted(self.files)):
            text = self.files[path]
            if path.startswith("talk/"):
                data = json.loads(text)
                data["lines"].reverse()
                text = json.dumps(data)
            turned[path] = text
        other = select.Selector(turned)
        states = [select.State(), select.State(stages={"mq02a": {10, 20, 30, 40}}), select.State(stages={"mq02c": {10}}, flags={"docket_2298_held"}),
                  select.State(stages={"mq01": {100}, "mq02": {100, 20}}, flags={"silver_rail"}),
                  select.State(stages={"mq03": {10, 40}}), select.State(stages={"mq03": {10, 40}}, dead={"pritchard"}),
                  select.State(stages={"mq02b": {41}}, dead={"hatcher"}), select.State(stages={"mq04": {10, 30, 50}})]
        speakers = sorted({l["speaker"] for l in self.s.lines.values()})
        for st in states:
            for who in speakers:
                a, b = self.s.greet(who, st), other.greet(who, st)
                self.assertEqual((a.line, a.diagnostic), (b.line, b.diagnostic), who)
        st1, st2 = select.State(stages={"mq02a": {10, 20, 30, 40}}), select.State(stages={"mq02a": {10, 20, 30, 40}})
        self.assertEqual(self.s.press("dole_sermon", 2, st1).line, other.press("dole_sermon", 2, st2).line)

    def test_no_greeting_is_ever_ambiguous_in_the_states_tried(self):
        for st in (select.State(), select.State(stages={"mq01": {100}, "mq02": {10, 20, 30, 40, 60, 100}, "mq02a": {41}, "mq02b": {42}, "mq02c": {51},
                                                         "mq03": {10, 40, 43, 50, 60, 100}, "mq04": {10, 30, 50, 61}})):
            for who in sorted({l["speaker"] for l in self.s.lines.values()}):
                r = self.s.greet(who, st)
                self.assertFalse(r.diagnostic and "ambiguous" in r.diagnostic, who)


class PacketThree(unittest.TestCase):
    """The histories docs/design/ACT1_CHARLES_PACKET3_ORDER.md asks for, on the revised Act I folder.

    A state is built from a line's own conditions, so each line is tried in a state where it really is on
    the screen; then one thing is changed and the button pressed."""

    SEARCH, STAY, TAKE, TRUCE = "(Search the roof and landing)", "(Stay with the courier)", "(Take the case and go)", "(Call the delegates to uphold the truce)"
    CHAIN = {False: ["whitcomb_truce", "belden_truce", "grey_truce", "pritchard_truce", "brigg_truce_concession_pritchard"],
             True: ["whitcomb_truce_talbot", "belden_truce_talbot", "grey_truce_talbot", "talbot_truce", "brigg_truce_concession_talbot"]}

    @classmethod
    def setUpClass(cls):
        cls.files = intake.read_folder(STORY)
        cls.s = select.Selector(cls.files)
        cls.p3 = json.loads((ROOT / "docs/design/ACT1_WRITING_CLOSURE_PACKET_3.json").read_text())
        L = cls.s.lines
        cls.demands = sorted(l for l in L if l.startswith("brigg_demand"))
        cls.fallbacks = sorted(l for l in L if "_courier_no_brigg_" in l)
        cls.course_lines = cls.demands + cls.fallbacks
        cls.truce_lines = cls.CHAIN[False] + cls.CHAIN[True]

    def state_for(self, lid):
        """A state in which exactly this line's conditions hold: its stages set, its dead dead, its flags raised."""
        st = select.State()
        for w in self.s.lines[lid]["when"]:
            a = w.split()
            if a[1] == "done":
                st.stages.setdefault(a[0], set()).add(int(a[2]))
            elif a[0] == "dead":
                st.dead.add(a[1])
            elif a[0] == "flag":
                st.flags.add(a[1])
        self.assertTrue(self.s.valid(self.s.lines[lid], st), lid)
        return st

    def effect_buttons(self, lid):
        return [i for i, b in enumerate(self.s.lines[lid].get("buttons", [])) if b.get("do")]

    def assert_nothing_happens(self, lid, st, why):
        for i in range(len(self.s.lines[lid].get("buttons", [])) or 1):
            before = ({k: set(v) for k, v in st.stages.items()}, set(st.flags), st.caps)
            r = self.s.press(lid, i, st)
            self.assertEqual((r.line, r.effects), (None, []), (lid, i, why))
            self.assertIn("no longer valid", r.diagnostic, (lid, i, why))
            self.assertEqual(({k: set(v) for k, v in st.stages.items()}, set(st.flags), st.caps), before, (lid, i, why))

    # ---- the concession comes first; only its Continue records 43
    def walk_truce(self, talbot, courier_dead=False):
        dead = ({"pritchard"} if talbot else set()) | ({"threefords"} if courier_dead else set())
        st = select.State(stages={"mq03": {10, 40}}, dead=dead)
        demand = self.s.greet("brigg", st).line
        self.assertEqual(demand, "brigg_demand" + ("_talbot" if talbot else "") + ("_courier_dead" if courier_dead else ""))
        labels = [b["label"] for b in self.s.lines[demand]["buttons"]]
        r = self.s.press(demand, labels.index(self.TRUCE), st)
        said = []
        for _ in range(len(self.CHAIN[talbot])):
            said.append(r.line)
            self.assertEqual(r.effects, [], r.line)
            self.assertFalse(st.done("mq03", 43), "43 was recorded before Brigg conceded, at %s" % r.line)
            if r.line == self.CHAIN[talbot][-1]:
                break
            r = self.s.press(r.line, 0, st)
        self.assertEqual(said, self.CHAIN[talbot])
        return st, said[-1]

    def test_both_paths_reach_briggs_concession_with_43_absent(self):
        for talbot in (False, True):
            for courier_dead in (False, True):
                st, concession = self.walk_truce(talbot, courier_dead)
                self.assertEqual(self.s.lines[concession]["speaker"], "brigg")
                self.assertEqual(self.s.lines[concession]["text"], "I accept a local search with witnesses. The fair stays outside Dominion command tonight. Put those limits on the record.")
                self.assertFalse(st.done("mq03", 43))
                r = self.s.press(concession, 0, st)
                self.assertEqual((r.line, r.effects, r.diagnostic), ("brigg_rifles", ["mq03 set 43"], None))

    def test_stage_43_has_exactly_two_setters_and_they_are_briggs(self):
        setters = sorted(lid for lid, l in self.s.lines.items() for b in l.get("buttons", []) if "mq03 set 43" in b.get("do", []))
        self.assertEqual(setters, ["brigg_truce_concession_pritchard", "brigg_truce_concession_talbot"])
        for lid in ("pritchard_truce", "talbot_truce"):
            self.assertEqual(self.effect_buttons(lid), [], lid)
        self.assertNotIn("mq03 notdone 43", self.s.lines["brigg_rifles"]["when"])
        self.assertIn("mq03 done 43", self.s.lines["brigg_rifles"]["when"])

    def test_a_death_before_the_concession_is_committed_records_nothing(self):
        for talbot in (False, True):
            for dead in ("brigg", "whitcomb", "belden", "grey", "talbot" if talbot else "pritchard"):
                st, concession = self.walk_truce(talbot)
                st.dead.add(dead)
                self.assert_nothing_happens(concession, st, "%s died" % dead)
                self.assertFalse(st.done("mq03", 43))
                self.assertNotEqual(self.s.greet("brigg", st).line, "brigg_rifles")     # and no false acknowledgement afterwards
        st, concession = self.walk_truce(True)
        st.dead.discard("pritchard")                                                    # Talbot's path is not Pritchard's
        self.assert_nothing_happens(concession, st, "Pritchard is alive on Talbot's path")

    def test_another_resolution_before_the_concession_is_committed_records_nothing(self):
        for talbot in (False, True):
            for resolved in (41, 42, 43, 44, 70, 100):
                st, concession = self.walk_truce(talbot)
                st.stages["mq03"].add(resolved)
                self.assert_nothing_happens(concession, st, "stage %d" % resolved)

    def test_every_line_of_the_truce_is_shut_by_a_death_another_course_or_completion(self):
        for lid in self.truce_lines:
            needs = [w.split()[1] for w in self.s.lines[lid]["when"] if w.startswith("alive ")]
            self.assertIn("brigg", needs, lid)
            for who in needs:
                st = self.state_for(lid)
                st.dead.add(who)
                self.assert_nothing_happens(lid, st, "%s died" % who)
            for resolved in (41, 42, 43, 44, 70, 100):
                st = self.state_for(lid)
                st.stages["mq03"].add(resolved)
                self.assert_nothing_happens(lid, st, "stage %d" % resolved)

    # ---- the courses: every menu rechecks who lives and what is resolved, and stops at completion
    def test_there_are_twelve_orders_and_six_fallbacks(self):
        self.assertEqual((len(self.demands), len(self.fallbacks)), (12, 6))
        setters = {n: sorted(lid for lid, l in self.s.lines.items() for b in l.get("buttons", []) if "mq03 set %d" % n in b.get("do", [])) for n in (41, 42, 44, 70)}
        self.assertEqual(setters[41], sorted(self.course_lines))
        self.assertEqual(setters[44], sorted(self.course_lines))
        self.assertEqual(setters[42], sorted(l for l in self.course_lines if "alive threefords" in self.s.lines[l]["when"]))
        self.assertEqual(setters[70], [])

    def test_every_course_menu_is_shut_by_a_death_another_course_or_completion(self):
        for lid in self.course_lines:
            self.assertTrue(self.effect_buttons(lid), lid)
            for who in [w.split()[1] for w in self.s.lines[lid]["when"] if w.startswith("alive ")]:
                st = self.state_for(lid)
                st.dead.add(who)
                self.assert_nothing_happens(lid, st, "%s died" % who)
            for who in [w.split()[1] for w in self.s.lines[lid]["when"] if w.startswith("dead ")]:
                st = self.state_for(lid)
                st.dead.discard(who)                                            # the menu was written for a state that is no longer so
                self.assert_nothing_happens(lid, st, "%s is alive after all" % who)
            for resolved in (41, 42, 43, 44, 70, 100):
                st = self.state_for(lid)
                st.stages["mq03"].add(resolved)
                self.assert_nothing_happens(lid, st, "stage %d" % resolved)

    def test_every_course_menu_works_while_its_conditions_hold(self):
        for lid in self.course_lines:
            for i in self.effect_buttons(lid):
                st = self.state_for(lid)
                r = self.s.press(lid, i, st)
                self.assertEqual(len(r.effects), 1, (lid, i))
                self.assertIsNone(r.diagnostic)
                self.assertFalse(st.done("mq03", 43) or st.done("mq03", 70), lid)

    def test_completed_100_blocks_every_active_courier_and_truce_source(self):
        for lid in self.course_lines + self.truce_lines:
            self.assertIn("mq03 notdone 100", self.s.lines[lid]["when"], lid)
            st = self.state_for(lid)
            st.stages["mq03"].add(100)
            self.assertFalse(self.s.valid(self.s.lines[lid], st), lid)
        done = select.State(stages={"mq03": {10, 40, 100}})
        for who in ("brigg", "pritchard", "talbot", "flint", "whitcomb", "belden", "grey"):
            self.assertNotIn(self.s.greet(who, done).line, self.course_lines + self.truce_lines, who)

    # ---- the courier, alive and dead
    def test_a_dead_courier_is_not_stayed_with_by_anyone(self):
        for lid in self.course_lines:
            labels = [b["label"] for b in self.s.lines[lid]["buttons"] if b["label"] != self.TRUCE]
            when = self.s.lines[lid]["when"]
            self.assertNotEqual("alive threefords" in when, "dead threefords" in when, lid)
            self.assertEqual(labels, [self.SEARCH] + ([self.STAY] if "alive threefords" in when else []) + [self.TAKE], lid)
        for dead_cast in (set(), {"pritchard"}, {"grey"}, {"brigg"}, {"brigg", "pritchard"}, {"brigg", "pritchard", "talbot"}):
            for courier_dead in (False, True):
                st = select.State(stages={"mq03": {10, 40}}, dead=dead_cast | ({"threefords"} if courier_dead else set()))
                offering = [w for w in ("brigg", "pritchard", "talbot", "flint") if self.s.greet(w, st).line in self.course_lines]
                self.assertEqual(len(offering), 1, (dead_cast, courier_dead, offering))   # one carrier, never two, never none while one lives
                menu = self.s.greet(offering[0], st).line
                self.assertEqual(self.STAY in [b["label"] for b in self.s.lines[menu]["buttons"]], not courier_dead, menu)

    def test_the_couriers_last_words_need_a_living_courier(self):
        self.assertEqual(self.s.greet("threefords", select.State(stages={"mq03": {10, 40, 42}})).line, "threefords_dying")
        dead = select.State(stages={"mq03": {10, 40, 42}}, dead={"threefords"})
        self.assertFalse(self.s.valid(self.s.lines["threefords_dying"], dead))
        self.assertNotEqual(self.s.greet("threefords", dead).line, "threefords_dying")
        stay = [x for x in self.p3["text_replacements"] if x["id"] == "stages[n=42]"][0]["text"]
        quest = json.loads(self.files["quests/tlm_mq03.json"])
        self.assertEqual([s_["log"] for s_ in quest["stages"] if s_["n"] == 42], [stay])
        self.assertNotIn("She said", stay)                                      # choosing to stay is not hearing her

    # ---- Brigg dead: Pritchard, then Talbot, then Flint; and nobody when none is left
    def test_fallback_precedence_with_brigg_dead(self):
        cases = [(set(), "pritchard"), ({"pritchard"}, "talbot"), ({"pritchard", "talbot"}, "flint")]
        for gone, carrier in cases:
            for courier_dead in (False, True):
                st = select.State(stages={"mq03": {10, 40}}, dead={"brigg"} | gone | ({"threefords"} if courier_dead else set()))
                want = "%s_courier_no_brigg_%s" % (carrier, "dead" if courier_dead else "living")
                self.assertEqual(self.s.greet(carrier, st).line, want)
                for other in {"pritchard", "talbot", "flint"} - {carrier}:
                    self.assertNotIn(self.s.greet(other, st).line, self.course_lines, (gone, other))
                self.assertNotIn(self.TRUCE, [b["label"] for b in self.s.lines[want]["buttons"]])
                self.assertNotIn(self.s.greet("brigg", st).line, self.course_lines)

    def test_every_carrier_dead_fails_closed(self):
        for courier_dead in (False, True):
            st = select.State(stages={"mq03": {10, 40}}, dead={"brigg", "pritchard", "talbot", "flint"} | ({"threefords"} if courier_dead else set()))
            for who in sorted({l["speaker"] for l in self.s.lines.values()}):
                self.assertNotIn(self.s.greet(who, st).line, self.course_lines + self.truce_lines, who)
            self.assertEqual(st.stages["mq03"], {10, 40})
        # In this source the quest then completes only through Pritchard's reading of the case. Getting at the
        # case is the game's business and is returned as a gate; nothing here pretends otherwise.
        setters_100 = sorted({lid for lid, l in self.s.lines.items() for b in l.get("buttons", []) if "mq03 set 100" in b.get("do", [])})
        self.assertEqual(setters_100, ["pritchard_case"])

    # ---- the roads still open after the fair
    def test_all_seven_open_road_contexts_keep_their_roads_and_offer_the_report_link(self):
        road = {20: "The spike. I'll take the rail.", 30: "The scoop. I'll go by river.", 40: "The tag. I'll walk the pike."}
        seen = set()
        # The fair is called either without a report (50) or after one (60); both are tried wherever both can be.
        histories = [((), {50, 100})] + [(d, called | set(d)) for d in ((20,), (30,), (40,), (20, 30), (20, 40), (30, 40)) for called in ({50, 100}, {10, 60, 100})]
        for done, hub in histories:
            for flags in ((), ("silver_rail", "silver_river", "silver_mine"), ("docket_2298_held",)):
                st = select.State(stages={"mq01": {100}, "mq02": set(hub)}, flags=flags)
                lid = self.s.greet("pritchard", st).line
                self.assertTrue(lid.startswith("pritchard_three_tokens_later"), (done, lid))
                seen.add(lid)
                labels = [b["label"] for b in self.s.lines[lid]["buttons"]]
                self.assertEqual(labels, [road[n] for n in (20, 30, 40) if n not in done] + ["Discuss a road account."])
                self.assertEqual(self.s.lines[lid]["text"], "There is still a road open if you want it. Or tell me what you've learned. No need to promise a journey just to ask a question.")
                before = ({k: set(v) for k, v in st.stages.items()}, set(st.flags), st.caps)
                r = self.s.press(lid, len(labels) - 1, st)
                self.assertEqual((r.line, r.effects, r.diagnostic), ("pritchard_report_open_roads", [], None))
                for i, leaf in enumerate(("pritchard_report_open_rail", "pritchard_report_open_river", "pritchard_report_open_pike")):
                    r = self.s.press("pritchard_report_open_roads", i, st)
                    self.assertEqual((r.line, r.effects, r.diagnostic), (leaf, [], None))
                    self.assertEqual(self.s.press(leaf, 0, st).line, None)      # its one implicit Continue closes
                r = self.s.press("pritchard_report_open_roads", 3, st)          # "Not now."
                self.assertEqual((r.line, r.effects), (None, []))
                self.assertEqual(({k: set(v) for k, v in st.stages.items()}, set(st.flags), st.caps), before, "a report changed what is known or done")
        self.assertEqual(len(seen), 7)

    def test_the_evidence_split_menus_remain_for_when_no_road_is_open(self):
        every = {"mq01": {100}, "mq02": {10, 20, 30, 40, 60, 100}}
        self.assertEqual(self.s.greet("pritchard", select.State(stages=every)).line, "pritchard_report_menu_uuu")
        st = select.State(stages=every, flags={"silver_rail"})
        self.assertEqual(self.s.greet("pritchard", st).line, "pritchard_report_menu_kuu")
        self.assertEqual(self.s.press("pritchard_report_menu_kuu", 0, st).line, "pritchard_hears_rail_after_fair")
        self.assertEqual(self.s.press("pritchard_report_menu_kuu", 1, st).line, "pritchard_hears_river_after_fair_unknown")

    # ---- what was learned is not what is in hand
    def test_learned_payment_evidence_needs_no_paper_and_the_docket_needs_to_be_in_hand(self):
        told = select.State(stages={"mq01": {100}, "mq02": {10, 20}}, flags={"silver_rail"})        # heard, with nothing carried
        self.assertEqual(self.s.greet("pritchard", told).line, "pritchard_hears_rail")
        self.assertIn("Silver. With a square stamped on it.", [b["label"] for b in self.s.lines["pritchard_hears_rail"]["buttons"]])
        untold = select.State(stages={"mq01": {100}, "mq02": {10, 20}}, flags={"docket_2298_held"})   # a paper in hand about something else
        self.assertEqual(self.s.greet("pritchard", untold).line, "pritchard_hears_rail_unknown")
        self.assertNotIn("Silver. With a square stamped on it.", [b["label"] for b in self.s.lines["pritchard_hears_rail_unknown"]["buttons"]])
        taken_once = select.State(stages={"mq02c": {10, 16}})                                       # the copy was taken; nothing says it is still held
        self.assertEqual(self.s.greet("quill", taken_once).line, "quill_court")
        in_hand = select.State(stages={"mq02c": {10}}, flags={"docket_2298_held"})                   # held, whatever stage 16 says
        self.assertEqual(self.s.greet("quill", in_hand).line, "quill_court_docket")
        self.assertFalse(any("mq02c done 16" in l["when"] for l in self.s.lines.values()))

    # ---- words
    def test_whitcomb_rates_is_packet_threes_and_says_nothing_act_one_may_not(self):
        want = [x for x in self.p3["text_replacements"] if x["id"] == "whitcomb_rates"][0]["text"]
        got = self.s.lines["whitcomb_rates"]["text"]
        self.assertEqual(got, want)
        for word in intake.NOT_IN_ACT_ONE:
            self.assertFalse(intake.names(word, got), word)
        self.assertNotIn("yonder", got)                                         # Nell's vote is history; nothing says where she is now
        st = select.State(stages={"mq03": {10}})
        self.assertEqual(self.s.press("whitcomb_offer", 0, st).line, "whitcomb_rates")

    def test_the_escape_names_no_fraction_and_a_dead_pilot_does_not_tell_it(self):
        for lid in ("pruitt_ran", "starnes_after_chute"):
            self.assertNotRegex(self.s.lines[lid]["text"], r"third|half|quarter")
        journal = [s_["log"] for s_ in json.loads(self.files["quests/tlm_mq02b.json"])["stages"] if s_["n"] == 42][0]
        self.assertNotRegex(journal, r"third|half|quarter")
        self.assertEqual(self.s.lines["pruitt_ran"]["when"], ["alive pruitt"])
        st = select.State(stages={"mq02b": {10, 20, 30}})
        self.assertEqual(self.s.press("pruitt_chain", 0, st).line, "pruitt_ran")
        st = select.State(stages={"mq02b": {10, 20, 30}}, dead={"pruitt"})
        r = self.s.press("pruitt_chain", 0, st)
        self.assertIsNone(r.line)                                               # nobody narrates for him
        self.assertEqual(r.effects, ["mq02b set 42"])                           # the escape itself is the quest's fact, not his line
        self.assertIn("pruitt_ran is not available", r.diagnostic)

    def test_the_reply_to_the_hanging_needs_the_choice_and_a_living_pritchard(self):
        self.assertEqual(self.s.greet("pritchard", select.State(stages={"mq04": {10, 30, 50, 64}})).line, "pritchard_after_rope")
        self.assertNotEqual(self.s.greet("pritchard", select.State(stages={"mq04": {10, 30, 50}})).line, "pritchard_after_rope")
        self.assertFalse(self.s.valid(self.s.lines["pritchard_after_rope"], select.State(stages={"mq04": {64}}, dead={"pritchard"})))
        setters = sorted(lid for lid, l in self.s.lines.items() for b in l.get("buttons", []) if "mq04 set 64" in b.get("do", []))
        self.assertEqual(setters, ["vane_porch"])

    def test_the_dissent_question_comes_before_the_way_out(self):
        for who in ("belden", "brigg", "grey"):
            buttons = self.s.lines[who + "_offer"]["buttons"]
            self.assertEqual(buttons[2].get("then"), who + "_dissent")
            self.assertEqual(buttons[3], {"label": "(Move on)"})


class FocusedTruceTermination(unittest.TestCase):
    def test_a_rooted_cycle_fails_both_focused_walks_without_hanging(self):
        files = intake.read_folder(STORY)
        path = "talk/tlm_mq03.json"
        data = json.loads(files[path])
        for line in data["lines"]:
            if line["id"] == "grey_truce":
                # The second edge keeps the normal final authority reachable.
                # Rooted cycles are permitted by the general v2 format.
                line["buttons"] = [{"label": "Continue", "then": "whitcomb_truce"},
                                   {"label": "Other", "then": "pritchard_truce"}]
        files[path] = json.dumps(data)
        self.assertEqual(intake.Intake(files, strict=True).run(), [])
        spec = importlib.util.spec_from_file_location("focused_cycle_probe", ROOT / "docs/design/ACT1_CHARLES_REVISION_CHECKS.py")
        focused = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(focused)
        out = io.StringIO()
        with mock.patch.object(focused.intake, "read_folder", return_value=files), contextlib.redirect_stdout(out):
            code = focused.main()
        self.assertEqual(code, 1)
        self.assertIn("truce chain from brigg_demand repeats", out.getvalue())
        self.assertIn("truce history repeats", out.getvalue())


class Legacy(unittest.TestCase):
    """The first format, its worked example and its self-test are as they were."""

    def test_the_first_example_is_byte_for_byte_what_it_was(self):
        for name, want in sorted(V1_EXAMPLE_SHA256.items()):
            self.assertEqual(hashlib.sha256((V1_EXAMPLE / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest(), want, name)

    def test_the_first_example_and_its_self_test(self):
        files = intake.read_folder(V1_EXAMPLE)
        self.assertEqual(intake.Intake(files).run(), [])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = intake.self_test(files)
        self.assertEqual(code, 0)
        self.assertIn("132 kinds of deliberate damage were each caught, for the reason each is wrong; 21 sound folders passed", out.getvalue())

    def test_the_second_example_and_its_self_test(self):
        files = intake.read_folder(V2_EXAMPLE)
        self.assertEqual(intake.Intake(files, strict=True).run(), [])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = intake.self_test(files)
        self.assertEqual(code, 0, out.getvalue())

    def test_the_second_example_says_what_the_first_means(self):
        s = select.from_folder(V2_EXAMPLE)
        self.assertEqual(s.greet("dunmore", select.State()).line, "dunmore_hold")
        self.assertEqual(s.greet("dunmore", select.State(words={"outcome": "saved"})).line, "dunmore_after")
        self.assertIsNone(s.greet("nell", select.State(words={"outcome": "exploited"})).line)     # her line is an aside, not a greeting


if __name__ == "__main__":
    unittest.main()
