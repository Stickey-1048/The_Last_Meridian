"""The Greenwater road's text (GREENWATER-STORY-001), against the accepted
writing.

docs/design/GREENWATER_STORY_001_MAPPING.json says which field of the writing
in assets/incoming/act1/story each native record takes its words from, and
gives this build's own text record by record. Here the plugin as built is
read back and compared: every spoken box and its buttons with the node they
are from, character by character; the two excerpts the order allows with
exactly what they are excerpts of; the two documents, page by page, with the
documents; the letter's book, from the bytes of the written plugin; the
road's journal and objectives with the quest file; and this build's own text
with the mapping, so that neither can change without the other.

This is agreement of the built records with source documents. It is not a
compile and not a game test: nobody has seen one of these boxes in the game.
"""
import json
import sys
import unittest

from test_sim import PLUGIN, ROOT, need_build
from test_mercy_briefing_projection import BARRED, ESP, book_texts

MAPPING = ROOT / "docs" / "design" / "GREENWATER_STORY_001_MAPPING.json"
SPEC = ROOT / "tools" / "PluginBuilder" / "SpecGreenwater.cs"
G = "TLM_MSG_GW_"


class Projection(unittest.TestCase):
    def setUp(self):
        need_build(self)
        self.map = json.loads(MAPPING.read_text())
        story = ROOT / self.map["source"]["folder"]
        src = self.map["source"]
        self.lines = {l["id"]: l for l in json.loads((story / src["talk"]).read_text())["lines"]}
        self.lines.update({l["id"]: l for l in json.loads((story / src["hub_talk"]).read_text())["lines"]})
        self.documents = {d["id"]: d for d in json.loads((story / src["documents"]).read_text())["documents"]}
        self.people = {c["id"]: c for c in json.loads((story / src["characters"]).read_text())["characters"]}
        self.quest = json.loads((story / src["quest"]).read_text())
        self.plugin = json.loads(PLUGIN.read_text())
        self.messages = {m["EditorId"]: m for m in self.plugin["Messages"]}
        self.limit = self.map["limit"]["longest_displayed_string"]

    def name(self, speaker):
        return self.people[speaker]["name"]

    def text_of(self, entry):
        whole = self.lines[entry["node"]]["text"]
        kind = entry["text"]
        if kind == "whole":
            return whole
        if "prefix_through" in kind:
            end = kind["prefix_through"]
            self.assertEqual(whole.count(end), 1)
            return whole[:whole.index(end) + len(end)]
        cut = kind["cut_before"]
        self.assertEqual(whole.count(cut), 1)
        at = whole.index(cut)
        return whole[:at] if kind["part"] == 1 else whole[at + 1:]

    def test_the_names_are_the_registered_ones(self):
        self.assertEqual([self.name(k) for k in ("starnes", "hatcher", "pruitt", "belden", "pritchard")],
                         ["Opal Starnes", "Lyle Hatcher", "Mose Rafferty", "Tomas Belden", "Owen Pritchard"])
        registry = (ROOT / "docs" / "naming-registry.md").read_text()
        for name in ("Opal Starnes", "Lyle Hatcher", "Mose Rafferty"):
            self.assertIn(name, registry)

    def test_every_record_is_mapped_once_and_every_mapped_record_is_built(self):
        built = sorted(m for m in self.messages if m.startswith(G))
        mapped = [e["record"] for e in self.map["speech"]] + [e["record"] for e in self.map["ui"]["boxes"]]
        for doc in self.map["documents"]:
            mapped += doc["pages"]
        self.assertEqual(sorted(mapped), built)
        self.assertEqual(len(mapped), len(set(mapped)))

    def test_every_spoken_box_is_its_source_field_word_for_word(self):
        for entry in self.map["speech"]:
            with self.subTest(entry["record"]):
                built = self.messages[entry["record"]]
                name = self.name(entry["speaker"])
                self.assertEqual(built["Text"], '%s: "%s"' % (name, self.text_of(entry)))
                self.assertEqual(built["Title"], name)
                self.assertTrue(built["Box"])
                self.assertNotIn("[", built["Text"])                 # no build text inside or beside a character's speech

    def test_every_button_is_its_source_label_in_its_source_place(self):
        for entry in self.map["speech"]:
            with self.subTest(entry["record"]):
                node = self.lines[entry["node"]]
                if entry["buttons"] == "node":
                    want = [b["label"] for b in node["buttons"]] if node.get("buttons") else ["Continue"]
                else:
                    want = [b["ui"] if "ui" in b else self.lines[b["node"]]["buttons"][b["button"]]["label"] for b in entry["buttons"]]
                built = self.messages[entry["record"]]["Buttons"]
                self.assertEqual([b["Text"] for b in built], want)
                self.assertTrue(all(not b["Conditions"] for b in built))
                self.assertLessEqual(len(built), 4)

    def test_the_two_excerpts_are_exactly_what_the_order_allows(self):
        lost = self.lines["hatcher_lost"]["text"]
        for record in ("HatcherLostNoOpal", "HatcherLostAlone"):
            text = self.messages[G + record]["Text"]
            self.assertEqual(text, 'Lyle Hatcher: "' + lost[:lost.index("Now. Do you mean")].rstrip() + '"')
            self.assertTrue(text.endswith('She\'s yours, friend, every sack."'))
            self.assertNotIn("Opal", text)
            self.assertNotIn("He's yours, Opal.", [b["Text"] for b in self.messages[G + record]["Buttons"]])
        for record in ("HatcherLost", "HatcherLostNoSheriff"):
            self.assertIn("Do you mean to give me to Opal?", self.messages[G + record]["Text"])
            self.assertEqual(self.messages[G + record]["Buttons"][0]["Text"], "He's yours, Opal.")
        for record in ("HatcherLostNoSheriff", "OpalAfterWonNoSheriff"):
            self.assertNotIn("He goes to Pritchard, alive.", [b["Text"] for b in self.messages[G + record]["Buttons"]])
        # His admission, in two boxes: together they are the line, and neither is long enough to be cut short.
        a, b = self.messages[G + "HatcherPaidA"]["Text"], self.messages[G + "HatcherPaidB"]["Text"]
        strip = lambda t: t[len('Lyle Hatcher: "'):-1]                # noqa: E731
        self.assertEqual(strip(a) + " " + strip(b), self.lines["hatcher_paid"]["text"])
        self.assertGreater(len('Lyle Hatcher: "%s"' % self.lines["hatcher_paid"]["text"]), self.limit)

    def test_the_documents_are_shown_whole_page_by_page(self):
        for doc in self.map["documents"]:
            with self.subTest(doc["document"]):
                source = self.documents[doc["document"]]
                text, at = source["text"], 0
                self.assertGreaterEqual(len(doc["pages"]), 2)
                self.assertLessEqual(len(doc["pages"]), 4)
                for n, record in enumerate(doc["pages"], 1):
                    built = self.messages[record]
                    heading = "[%s, page %d of %d]\n\n" % (source["title"], n, len(doc["pages"]))
                    self.assertTrue(built["Text"].startswith(heading), built["Text"][:60])
                    page = built["Text"][len(heading):]
                    self.assertTrue(text.startswith(page, at), "page %d is not the next piece of the document" % n)
                    at += len(page)
                    # Only line breaks stand between two pages.
                    while at < len(text) and text[at] == "\n":
                        at += 1
                    self.assertEqual([b["Text"] for b in built["Buttons"]], ["Continue"])
                    self.assertIsNone(built["Title"])
                self.assertEqual(at, len(text), "the pages do not reach the document's end")
        self.assertEqual((len(self.documents["ration_board"]["text"]), len(self.documents["letter_of_hire"]["text"])), (431, 486))

    def test_the_letter_is_a_book_word_for_word(self):
        if not ESP.exists():
            self.fail("%s is missing. Run tools/run_checks.sh, which builds it." % ESP)
        books = book_texts(ESP)
        doc = self.documents["letter_of_hire"]
        self.assertEqual(books["TLM_BOOK_LetterOfHire"], (doc["title"], doc["text"]))
        described = [r for r in self.plugin["Records"] if r["EditorId"] == "TLM_BOOK_LetterOfHire"]
        self.assertEqual([(r["Type"], r["Name"]) for r in described], [("Book", doc["title"])])

    def test_this_builds_own_text_is_what_the_mapping_says_and_is_never_speech(self):
        for entry in self.map["ui"]["boxes"]:
            with self.subTest(entry["record"]):
                built = self.messages[entry["record"]]
                self.assertEqual(built["Text"], entry["text"])
                self.assertEqual([b["Text"] for b in built["Buttons"]], entry["buttons"])
                self.assertTrue(built["Text"].startswith("["), "this build's text begins with its bracketed heading")
                self.assertIsNone(built["Title"])
                self.assertNotIn('"', built["Text"])
                for person in ("Opal Starnes:", "Lyle Hatcher:", "Mose Rafferty:", "Tomas Belden:", "Owen Pritchard:"):
                    self.assertNotIn(person, built["Text"])
        # The occupancy warning without Rafferty: his line's own words and buttons, under the build's heading.
        chain = self.messages[G + "AskChain"]
        self.assertEqual(chain["Text"], "[Anchor chain]\n\n" + self.lines["pruitt_chain"]["text"])
        self.assertEqual([b["Text"] for b in chain["Buttons"]], [b["label"] for b in self.lines["pruitt_chain"]["buttons"]])
        fire = self.messages[G + "AskFire"]
        self.assertEqual([b["Text"] for b in fire["Buttons"]], ["Burn the occupied Queen.", "Not yet."])
        self.assertIn("Thirty people are aboard", fire["Text"])

    def test_the_availability_text_is_the_orders(self):
        texts = {k: m["Text"] for k, m in self.messages.items()}
        self.assertIn("Only the Greenwater road is playable in this candidate.", texts[G + "AskTravel"])
        for end in ("ReportEndKnown", "ReportEndUnknown"):
            self.assertTrue(texts[G + end].endswith("Greenwater road complete. The other roads and the fair are not playable in this candidate."))
        travel = [r for r in self.plugin["Records"] if r["EditorId"] == "TLM_ACTI_GW_Travel"][0]
        self.assertEqual(travel["Name"], "Greenwater story test")

    def test_no_displayed_string_is_long_enough_to_be_cut_short(self):
        self.assertLess(self.limit, 255)
        longest = 0
        for name, m in self.messages.items():
            if name.startswith(G):
                text = m["Text"]
                self.assertEqual(text, text.encode("ascii").decode("ascii"), name)
                self.assertNotIn("%", text, name)
                self.assertLessEqual(len(text), self.limit, name)
                longest = max(longest, len(text))
                for b in m["Buttons"]:
                    self.assertLessEqual(len(b["Text"]), 48, name)
        self.assertEqual(longest, 236)                               # measured: Rafferty's line at the chain, with his name

    def test_nothing_names_what_act_one_does_not_know(self):
        for name, m in self.messages.items():
            if name.startswith(G):
                for word in BARRED:
                    self.assertNotIn(word, m["Text"].lower(), name)

    def test_the_journal_and_the_objectives_are_the_quest_files(self):
        road = [q for q in self.plugin["Quests"] if q["EditorId"] == "TLM_MQ02B"][0]
        self.assertEqual(road["Name"], self.quest["title"])
        accepted = {s["n"]: s["log"] for s in self.quest["stages"]}
        built = {s["Index"]: s["Log"] for s in road["Stages"]}
        for entry in self.map["quest"]["stages"]:
            n = entry["n"]
            if "log_ui" in entry:
                self.assertEqual(built[n], entry["log_ui"])
            elif entry.get("native_only"):
                self.assertEqual(built[n], accepted[int(entry["log"].split()[1])])
                self.assertNotIn(n, accepted)
            else:
                self.assertEqual(built[n], accepted[n], n)
        self.assertEqual(sorted(built), sorted(e["n"] for e in self.map["quest"]["stages"]))
        # Every accepted stage is there, under its own number.
        self.assertEqual(sorted(accepted), sorted(n for n in built if n != 46))
        # 44 does not say what payment has not earned; 46 says it.
        self.assertEqual(built[44], "You accepted Hatcher's share. The grain remains aboard the Queen.")
        self.assertEqual(built[46], accepted[44])
        self.assertIn("thanked you", built[46])
        objectives = {o["n"]: o["text"] for o in self.quest["objectives"]}
        got = {o["Index"]: o["Text"] for o in road["Objectives"]}
        for entry in self.map["quest"]["objectives"]:
            self.assertEqual(got[entry["n"]], entry["text_ui"] if entry.get("native_only") else objectives[entry["n"]])
        self.assertEqual(sorted(got), [10, 20, 40, 50, 60, 80])

    def test_every_accepted_flag_has_one_fact_of_its_own(self):
        flags = [f["name"] for f in self.quest["new_flags"]]
        mapped = {f["flag"]: f["global"] for f in self.map["flags"]}
        self.assertEqual(sorted(mapped), sorted(flags))
        globals_ = {r["EditorId"] for r in self.plugin["Records"] if r["Type"] == "Global"}
        for flag, name in mapped.items():
            self.assertIn(name, globals_, flag)
        self.assertEqual(len(set(mapped.values())), 7)
        source = (ROOT / "scripts" / "Source" / "User" / "TLM" / "MQ02BQuest.psc").read_text()
        # Each is written in one function only: grain_home in CompleteReturn (its two arrivals), the rest once each.
        # grain_sold in TellLie: the paid deal and the lie delivered to her alive (repair, finding 5), not her answer.
        # hatcher_hanged in RecordHanging, which the wait in Hang and his death event both go through (finding 2).
        setter = {"grain_home": "CompleteReturn", "grain_sold": "TellLie", "queen_burned": "FireDone", "hatcher_hanged": "RecordHanging",
                  "hatcher_friend": "Release", "hatcher_hunting": "CompleteReturn", "silver_river": "LearnHire"}
        bodies = {}
        for piece in source.split("Function ")[1:]:
            bodies[piece.split("(")[0].strip()] = piece.split("EndFunction")[0]
        for flag, name in mapped.items():
            where = [fn for fn, body in bodies.items() if name + ".SetValueInt(" in body]
            self.assertEqual(where, [setter[flag]], flag)
            self.assertEqual(source.count(name + ".SetValueInt("), 2 if flag == "grain_home" else 1, flag)

    def test_the_spec_holds_no_speech_the_writing_does_not(self):
        """The spec's accepted-writing block is the JSON's own strings: every node's text and labels, every stage's
        journal, every objective, both documents."""
        source = SPEC.read_text()
        block = source.split("// ------------------------------------------------- the accepted writing")[1].split("// Hatcher's admission is 239")[0]
        import re
        said = [s.encode().decode("unicode_escape") for s in re.findall(r'"((?:[^"\\]|\\.)*)"', block)]
        allowed = set()
        for l in self.lines.values():
            allowed.add(l["id"])
            allowed.add(l["text"])
            allowed.update(b["label"] for b in l.get("buttons", []))
        for s in self.quest["stages"]:
            if s["log"]:
                allowed.add(s["log"])
        allowed.update(o["text"] for o in self.quest["objectives"])
        allowed.add(self.quest["title"])
        for d in ("ration_board", "letter_of_hire"):
            allowed.update((self.documents[d]["title"], self.documents[d]["text"]))
        allowed.update(self.name(k) for k in ("starnes", "hatcher", "pruitt", "belden"))
        self.assertEqual([s for s in said if s not in allowed], [])
        self.assertGreater(len(said), 80)


if __name__ == "__main__":
    unittest.main()
