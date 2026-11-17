"""The Mercy briefing's text (ACT1-RUNTIME-001), against the accepted writing.

docs/design/ACT1_RUNTIME_001_MAPPING.json says which field of the writing in
assets/incoming/act1/story each native record takes its words from. Here the
plugin as built is read back and every such string is compared with its field,
character by character: the spoken boxes and their buttons from the plugin's
description (build/sim), the book's text from the bytes of the written plugin
(build/TheLastMeridian.esp), without the library that wrote them.

Also here: that the plugin holds no briefing record the mapping does not
name and the mapping names none the plugin lacks; that every displayed string
stays under the length at which the game was seen to cut a box short; and
that the availability text stands outside the quoted speech.

This is agreement of the built records with source documents. It is not a
compile and not a game test: nobody has seen one of these boxes in the game.
"""
import hashlib
import json
import sys
import unittest

from test_sim import PLUGIN, ROOT, need_build

sys.path.insert(0, str(ROOT / "tools"))
from check_plugin_layout import records, subrecords                # noqa: E402

MAPPING = ROOT / "docs" / "design" / "ACT1_RUNTIME_001_MAPPING.json"
SPEC = ROOT / "tools" / "PluginBuilder" / "SpecMercyBriefing.cs"
ESP = ROOT / "build" / "TheLastMeridian.esp"
PREFIX = "TLM_MSG_MB_"
# Act I's barred words (docs/design/STORY_INTAKE.md), as the first section's own lines are held to.
BARRED = ("deep", "meridian", "rider", "charter", "open ledger", "vault")


def book_texts(path):
    """EditorID -> (name, text) of every BOOK record, from the file's bytes."""
    buf = path.read_bytes()
    out = {}
    for kind, off, size, _formid, flags in records(buf, 0, len(buf)):
        if kind != "BOOK":
            continue
        if flags & 0x00040000:
            raise AssertionError("a BOOK record is compressed; this reader does not expect that of the builder")
        subs = dict((k, v) for k, v in subrecords(buf[off:off + size]))
        text = lambda b: b.rstrip(b"\x00").decode("utf-8")           # noqa: E731
        out[text(subs["EDID"])] = (text(subs.get("FULL", b"")), text(subs.get("DESC", b"")))
    return out


class Projection(unittest.TestCase):
    def setUp(self):
        need_build(self)
        self.map = json.loads(MAPPING.read_text())
        story = ROOT / self.map["source"]["folder"]
        self.lines = {l["id"]: l for l in json.loads((story / self.map["source"]["talk"]).read_text())["lines"]}
        self.documents = {d["id"]: d for d in json.loads((story / self.map["source"]["documents"]).read_text())["documents"]}
        self.people = {c["id"]: c for c in json.loads((story / self.map["source"]["characters"]).read_text())["characters"]}
        self.plugin = json.loads(PLUGIN.read_text())
        self.messages = {m["EditorId"]: m for m in self.plugin["Messages"]}
        self.ui = self.map["ui"]
        who = self.map["speech"]["name_from"]
        self.name = self.people[who["id"]][who["field"]]

    def spoken(self, text):
        return '%s: "%s"' % (self.name, text)

    def source_text(self, entry):
        ref = entry["text"]
        if "line" in ref:
            return self.lines[ref["line"]][ref["field"]]
        # The same speech as another record of the plugin: what stands between its quotes.
        other = self.messages[ref["same_speech_as_record"]]["Text"]
        self.assertTrue(other.startswith(self.name + ': "'), other)
        return other[len(self.name) + 3:other.index('"\n\n[')]

    def test_the_name_is_the_registered_one(self):
        self.assertEqual(self.name, "Owen Pritchard")
        self.assertEqual(self.people["pritchard"]["record"], "TLM_NPC_SHERIFF_MERCY")

    def test_every_briefing_message_is_mapped_and_every_mapped_message_is_built(self):
        built = sorted(m for m in self.messages if m.startswith(PREFIX))
        mapped = sorted(e["record"] for e in self.map["messages"])
        self.assertEqual(built, mapped)
        self.assertEqual(len(mapped), 9)

    def test_every_spoken_box_is_its_source_field_word_for_word(self):
        for entry in self.map["messages"]:
            if "text" not in entry:
                continue
            with self.subTest(entry["record"]):
                built = self.messages[entry["record"]]
                want = self.spoken(self.source_text(entry))
                if "ui_under_the_speech" in entry:
                    want += "\n\n[" + self.ui[entry["ui_under_the_speech"]] + "]"
                self.assertEqual(built["Text"], want)
                self.assertEqual(built["Title"], self.name)
                self.assertTrue(built["Box"])

    def test_every_button_is_its_source_label_in_its_source_place(self):
        for entry in self.map["messages"]:
            if "buttons" not in entry:
                continue
            with self.subTest(entry["record"]):
                want = []
                for b in entry["buttons"]:
                    if "ui" in b:
                        want.append(self.ui[b["ui"]])
                    else:
                        want.append(self.lines[b["line"]]["buttons"][b["button"]]["label"])
                built = self.messages[entry["record"]]["Buttons"]
                self.assertEqual([b["Text"] for b in built], want)
                self.assertTrue(all(not b["Conditions"] for b in built))
                self.assertLessEqual(len(built), 4)

    def test_the_labels_are_the_ones_the_contract_names(self):
        label = lambda record: [b["Text"] for b in self.messages[PREFIX + record]["Buttons"]]      # noqa: E731
        self.assertEqual(label("Hub"), ["The rail.", "The river.", "Red Hollow.", "Not now."])
        self.assertEqual(label("Pike"), ["What should I ask Quill?", "Continue"])
        self.assertEqual(label("Docket"), ["Take the review copy.", "Leave the copy."])
        self.assertEqual(label("DocketIssued"), ["Continue"])
        self.assertNotIn("Take", " ".join(label("DocketIssued")))

    def test_the_notes_are_ui_and_not_boxes(self):
        for entry in self.map["messages"]:
            if "ui_only" in entry:
                built = self.messages[entry["record"]]
                self.assertEqual(built["Text"], self.ui[entry["ui_only"]])
                self.assertFalse(built["Box"])
                self.assertEqual(built["Buttons"], [])
                self.assertNotIn('"', built["Text"])

    def test_availability_text_is_outside_the_quotes_and_as_the_contract_words_it(self):
        # As GREENWATER-STORY-001's order words them for this candidate (item 1), in which Greenwater is playable.
        # The a8 source keeps ACT1-RUNTIME-001's own wording, which said that no destination is.
        self.assertEqual(self.ui["briefing_only"], "Mercy briefing. Greenwater, Iron Junction and Red Hollow are playable. The fair is not.")
        self.assertEqual(self.ui["hand_off_footer"], "Opening complete. Ask for briefings or use a story test point.")
        self.assertEqual(self.ui["journal_complete"], "Mercy briefing complete. Greenwater, Iron Junction and Red Hollow are playable; the fair is not.")
        self.assertEqual(self.ui["objective"], "Ask Pritchard about the three roads.")
        for record in ("Hub", "HandOff"):
            text = self.messages[PREFIX + record]["Text"]
            speech, _, rest = text.partition('"\n\n[')
            self.assertTrue(rest.endswith("]"), text)
            self.assertNotIn("Mercy brief", speech)
            self.assertNotIn("playable", speech)
            self.assertNotIn("story test", speech)
        hub = self.messages[PREFIX + "Hub"]["Text"]
        self.assertTrue(hub.endswith("\n\n[" + self.ui["briefing_only"] + "]"))

    def test_no_displayed_string_is_long_enough_to_be_cut_short(self):
        limit = self.map["limit"]["longest_displayed_string"]
        self.assertLess(limit, 255)
        longest = 0
        for name, m in self.messages.items():
            if name.startswith(PREFIX):
                text = m["Text"]
                self.assertEqual(text, text.encode("ascii").decode("ascii"), name)
                self.assertNotIn("%", text, name)
                self.assertLessEqual(len(text), limit, name)
                longest = max(longest, len(text))
                for b in m["Buttons"]:
                    self.assertLessEqual(len(b["Text"]), 48, name)
        self.assertEqual(longest, 233)                 # measured: the hand-off with this candidate's footer; the longest spoken box alone is 221

    def test_nothing_names_what_act_one_does_not_know(self):
        for name, m in self.messages.items():
            if name.startswith(PREFIX):
                for word in BARRED:
                    self.assertNotIn(word, m["Text"].lower(), name)

    def test_the_book_is_the_document_word_for_word(self):
        if not ESP.exists():
            self.fail("%s is missing. Run tools/run_checks.sh, which builds it." % ESP)
        entry = self.map["book"]
        doc = self.documents[entry["title"]["document"]]
        books = book_texts(ESP)
        self.assertIn(entry["record"], books)
        name, text = books[entry["record"]]
        self.assertEqual(name, doc["title"])
        self.assertEqual(text, doc["text"])
        self.assertEqual(len(text), entry["text_characters"])
        self.assertEqual(len(text), 629)
        self.assertEqual(hashlib.sha256(text.encode("utf-8")).hexdigest(),
                         "1613a058406d0776cbd073d1c6be83e969ff078a269366140b9d96e832e03b11")
        described = [r for r in self.plugin["Records"] if r["EditorId"] == entry["record"]]
        self.assertEqual([(r["Type"], r["Name"]) for r in described], [("Book", doc["title"])])
        self.assertIsNotNone(described[0]["Model"], "against a master the book takes after one of its notes")
        # The first section's two papers are as they were.
        # (TLM_BOOK_LetterOfHire is GREENWATER-STORY-001's; test_greenwater_projection.py reads it.)
        self.assertEqual(sorted(books), ["TLM_BOOK_Docket2298", "TLM_BOOK_HymnalFlyleaf", "TLM_BOOK_LetterOfHire", "TLM_BOOK_MarshalLog", "TLM_BOOK_RailMaintLedger"])

    def test_the_quest_is_a_utility_task_of_its_own(self):
        entry = self.map["quest"]
        quest = [q for q in self.plugin["Quests"] if q["EditorId"] == entry["record"]][0]
        self.assertEqual(quest["Name"], self.ui[entry["name"]])
        self.assertNotIn("StartGameEnabled", quest["Flags"])
        self.assertEqual([(s["Index"], s["Log"], s["CompleteQuest"]) for s in quest["Stages"]],
                         [(10, self.ui["briefing_only"], False), (20, self.ui["journal_complete"], True)])
        self.assertEqual([(o["Index"], o["Text"]) for o in quest["Objectives"]], [(10, self.ui["objective"])])
        self.assertEqual([(a["Name"], a["Flags"], a["Fill"], a["Scripts"]) for a in quest["Aliases"]], [("Briefer", ["Optional"], None, [])])
        self.assertEqual(quest["Objectives"][0]["TargetAliases"], [0])
        self.assertEqual([s["Name"] for s in quest["Scripts"]], ["TLM:MercyBriefing"])
        ids = {q["EditorId"] for q in self.plugin["Quests"]}
        self.assertEqual(ids, {"TLM_Core", "TLM_MQ01", "TLM_SQ01", "TLM_Trial", "TLM_A1", "TLM_MercyBriefing", "TLM_MQ02A", "TLM_MQ02B", "TLM_GW", "TLM_MQ02C", "TLM_RH", "TLM_NM", "TLM_GW_Relief"})
        for later in entry["not_a_stage_of"]:
            # TLM_MQ02B now exists (GREENWATER-STORY-001): the briefing is still no stage of it.
            if later != "TLM_MQ02b":
                self.assertNotIn(later, ids)
        self.assertNotEqual(quest["EditorId"], "TLM_MQ02B")

    def test_every_property_points_at_the_record_the_mapping_names(self):
        quest = [q for q in self.plugin["Quests"] if q["EditorId"] == "TLM_MercyBriefing"][0]
        props = {p["Name"]: (p["Target"], p["Alias"]) for p in quest["Scripts"][0]["Props"]}
        want = {e["property"]: (e["record"], None) for e in self.map["messages"]}
        want[self.map["book"]["property"]] = (self.map["book"]["record"], None)
        want["TLM_MQ01"] = ("TLM_MQ01", None)
        want["TLM_G_MQ01_Done"] = ("TLM_G_MQ01_Done", None)
        want["Alias_Briefer"] = ("TLM_MercyBriefing", 0)
        self.assertEqual(props, want)
        walk = [q for q in self.plugin["Quests"] if q["EditorId"] == "TLM_A1"][0]["Scripts"][0]
        self.assertEqual(walk["Name"], "TLM:Act1Walk")
        bound = [(p["Target"], p["Alias"]) for p in walk["Props"] if p["Name"] == "TLM_MercyBriefing"]
        self.assertEqual(bound, [("TLM_MercyBriefing", None)])

    def test_the_spec_holds_no_speech_the_mapping_does_not_account_for(self):
        """Every string in quotes in the spec file is a mapped source field, a
        mapped label, UI named in the mapping, or a name of a record or of a
        property. Nothing else is said."""
        import re
        accounted = set(self.ui[k] for k in self.ui if isinstance(self.ui[k], str))
        for entry in self.map["messages"]:
            if "text" in entry:
                accounted.add(self.source_text(entry))
            for b in entry.get("buttons", []):
                if "line" in b:
                    accounted.add(self.lines[b["line"]]["buttons"][b["button"]]["label"])
        doc = self.documents["docket_2298"]
        accounted.add(doc["title"])
        source = SPEC.read_text()
        code = "\n".join(l.split("//")[0] if l.lstrip().startswith("//") else l for l in source.splitlines())
        said = [s.encode().decode("unicode_escape") for s in re.findall(r'"((?:[^"\\]|\\.)*)"', code)]
        body = "".join(s for s in said if s and s in doc["text"] and len(s) > 20)
        left = []
        for s in said:
            if s in accounted or (len(s) > 20 and s in doc["text"]):
                continue
            if re.fullmatch(r"[A-Za-z_:0-9]+", s) or s in ("", ": \"", "\"", "\n\n[", "]", "Owen Pritchard"):
                continue                               # record, property, alias, script and type names; the box format
            if s.startswith(("Briefing begun.", "A road's brief was shown", "whoever was asked")):
                continue                               # editor notes on the stages and the alias; never displayed
            left.append(s)
        self.assertEqual(left, [])
        self.assertEqual(body, doc["text"])


if __name__ == "__main__":
    unittest.main()
