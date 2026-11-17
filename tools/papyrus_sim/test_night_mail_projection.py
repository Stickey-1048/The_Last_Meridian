"""The Night Mail's text (NIGHT-MAIL-STORY-001), against the accepted writing.

docs/design/NIGHT_MAIL_STORY_001_MAPPING.json says which field of the writing
in assets/incoming/act1/story each native record takes its words from, and
gives this build's own text record by record. Here the plugin as built is
read back and compared: every spoken box and its buttons with the node they
are from, character by character; the three excerpts with exactly what they
are excerpts of; the three documents, page by page, with the documents; the
hymnal's book, from the bytes of the written plugin; the road's journal and
objectives with the quest file; and this build's own text with the mapping,
so that neither can change without the other.

This is agreement of the built records with source documents. It is not a
compile and not a game test: nobody has seen one of these boxes in the game.
"""
import json
import re
import unittest

from test_sim import PLUGIN, ROOT, need_build
from test_mercy_briefing_projection import BARRED, ESP, book_texts

MAPPING = ROOT / "docs" / "design" / "NIGHT_MAIL_STORY_001_MAPPING.json"
SPEC = ROOT / "tools" / "PluginBuilder" / "SpecNightMail.cs"
RULES = ROOT / "scripts" / "Source" / "User" / "TLM" / "MQ02AQuest.psc"
G = "TLM_MSG_NM_"
PEOPLE = ("Augusta Lockridge:", "Wilhelmina Tupper:", "Ezekiel Dole:", "Owen Pritchard:")


class Projection(unittest.TestCase):
    def setUp(self):
        need_build(self)
        self.map = json.loads(MAPPING.read_text())
        story = ROOT / self.map["source"]["folder"]
        src = self.map["source"]
        self.lines = {l["id"]: l for l in json.loads((story / src["talk"]).read_text())["lines"]}
        self.own = set(self.lines)
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
        if "from" in kind:
            self.assertEqual(whole.count(kind["from"]), 1)
            return whole[whole.index(kind["from"]):]
        cut = kind["cut_before"]
        self.assertEqual(whole.count(cut), 1)
        at = whole.index(cut)
        return whole[:at] if kind["part"] == 1 else whole[at + 1:]

    def test_the_names_are_the_registered_ones(self):
        self.assertEqual([self.name(k) for k in ("lockridge", "tarrow", "dole", "pritchard")],
                         ["Augusta Lockridge", "Wilhelmina Tupper", "Ezekiel Dole", "Owen Pritchard"])
        registry = (ROOT / "docs" / "naming-registry.md").read_text()
        for name in ("Augusta Lockridge", "Wilhelmina Tupper"):
            self.assertIn(name, registry)
        # Dole's legal identity is not on a nameplate or a speaker label before it is found out.
        for m in self.messages.values():
            if m["EditorId"].startswith(G):
                self.assertNotIn("Ostrander", m["Title"] or "")
                self.assertNotIn("Reuben", m["Title"] or "")
                self.assertFalse(m["Text"].startswith("Reuben") or m["Text"].startswith("R. Ostrander:"))
        people = [r for r in self.plugin["Records"] if r["EditorId"].startswith("TLM_NPC_") and r.get("Name")]
        self.assertNotIn("Reuben Ostrander", [r["Name"] for r in people])

    def test_every_record_is_mapped_once_and_every_mapped_record_is_built(self):
        built = sorted(m for m in self.messages if m.startswith(G))
        mapped = [e["record"] for e in self.map["speech"]] + [e["record"] for e in self.map["ui"]["boxes"]]
        for doc in self.map["documents"]:
            mapped += doc["pages"]
        self.assertEqual(sorted(mapped), built)
        self.assertEqual(len(mapped), len(set(mapped)))

    def test_every_node_of_the_road_is_used(self):
        used = {e["node"] for e in self.map["speech"]}
        self.assertEqual(sorted(self.own - used), [], "a line of the accepted road that no record shows")
        self.assertEqual(sorted(used - self.own), ["pritchard_hears_rail_after_fair", "pritchard_hears_rail_after_fair_unknown"])

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

    def test_the_excerpts_are_exactly_what_they_are_said_to_be(self):
        strip = lambda t, who: t[len(who) + 3:-1]                     # noqa: E731
        # Her gate greeting, in two boxes: together they are the line, and it is too long for one.
        a, b = self.messages[G + "LockridgeGateA"]["Text"], self.messages[G + "LockridgeGateB"]["Text"]
        whole = self.lines["lockridge_gate"]["text"]
        self.assertEqual(strip(a, "Augusta Lockridge") + " " + strip(b, "Augusta Lockridge"), whole)
        self.assertGreater(len('Augusta Lockridge: "%s"' % whole), self.limit)
        self.assertTrue(strip(a, "Augusta Lockridge").endswith("."))
        # His offer without Billie: the part that promises nothing about her.
        rest = strip(self.messages[G + "DoleShareNoBillie"]["Text"], "Ezekiel Dole")
        share = self.lines["dole_share"]["text"]
        self.assertTrue(share.endswith(rest))
        self.assertNotIn("girl", rest)
        self.assertNotIn("unharmed", rest)
        self.assertIn("the girl walks home unharmed", share[:len(share) - len(rest)])
        offer = self.messages[G + "AskShareOffer"]
        self.assertEqual(offer["Text"], "[Offer]\n\nOffer: 150 caps.")
        self.assertEqual([x["Text"] for x in offer["Buttons"]], [x["label"] for x in self.lines["dole_share"]["buttons"]])
        # The regulator without Billie: her three answers under this build's heading, and none of her words.
        regulator = self.messages[G + "AskRegulator"]
        self.assertEqual([x["Text"] for x in regulator["Buttons"]], [x["label"] for x in self.lines["tarrow_in_cut"]["buttons"]])
        self.assertNotIn(self.lines["tarrow_in_cut"]["text"][:20], regulator["Text"])
        alone = self.messages[G + "AskStampAlone"]
        self.assertEqual([x["Text"] for x in alone["Buttons"]], [self.lines["lockridge_stamp"]["buttons"][2]["label"], "(Close the drawer)"])

    def test_the_documents_are_shown_whole_page_by_page(self):
        for doc in self.map["documents"]:
            with self.subTest(doc["document"]):
                source = self.documents[doc["document"]]
                text, at = source["text"], 0
                self.assertLessEqual(len(doc["pages"]), 4)
                for n, record in enumerate(doc["pages"], 1):
                    built = self.messages[record]
                    heading = "[%s, page %d of %d]\n\n" % (source["title"], n, len(doc["pages"]))
                    self.assertTrue(built["Text"].startswith(heading), built["Text"][:60])
                    page = built["Text"][len(heading):]
                    self.assertTrue(text.startswith(page, at), "page %d is not the next piece of the document" % n)
                    at += len(page)
                    while at < len(text) and text[at] == "\n":             # only line breaks stand between two pages
                        at += 1
                    self.assertEqual([b["Text"] for b in built["Buttons"]], ["Continue"])
                    self.assertIsNone(built["Title"])
                self.assertEqual(at, len(text), "the pages do not reach the document's end")
        self.assertEqual([len(self.documents[d]["text"]) for d in ("yard_rules", "hymn_chalk", "hymnal_flyleaf")], [533, 135, 301])

    def test_the_hymnal_is_a_book_word_for_word(self):
        if not ESP.exists():
            self.fail("%s is missing. Run tools/run_checks.sh, which builds it." % ESP)
        books = book_texts(ESP)
        doc = self.documents["hymnal_flyleaf"]
        self.assertEqual(books["TLM_BOOK_HymnalFlyleaf"], (doc["title"], doc["text"]))
        described = [r for r in self.plugin["Records"] if r["EditorId"] == "TLM_BOOK_HymnalFlyleaf"]
        self.assertEqual([(r["Type"], r["Name"]) for r in described], [("Book", doc["title"])])
        stamp = [r for r in self.plugin["Records"] if r["EditorId"] == "TLM_MISC_OstranderStamp"]
        self.assertEqual([(r["Type"], r["Name"]) for r in stamp], [("MiscItem", "Inspector's Stamp")])

    def test_this_builds_own_text_is_what_the_mapping_says_and_is_never_speech(self):
        for entry in self.map["ui"]["boxes"]:
            with self.subTest(entry["record"]):
                built = self.messages[entry["record"]]
                self.assertEqual(built["Text"], entry["text"])
                self.assertEqual([b["Text"] for b in built["Buttons"]], entry["buttons"])
                self.assertTrue(built["Text"].startswith("["), "this build's text begins with its bracketed heading")
                self.assertIsNone(built["Title"])
                self.assertNotIn('"', built["Text"])
                for person in PEOPLE:
                    self.assertNotIn(person, built["Text"])
                self.assertTrue(entry["shown_when"])

    def test_the_availability_text_is_the_orders(self):
        texts = {k: m["Text"] for k, m in self.messages.items()}
        both = "Greenwater and Iron Junction are playable in this candidate; Red Hollow and the fair are not."
        self.assertIn(both, texts[G + "AskTravel"])
        self.assertIn(both, texts["TLM_MSG_GW_AskTravel"])
        self.assertTrue(texts[G + "ReportEnd"].endswith("Night Mail road complete. Greenwater remains playable; Red Hollow and the fair are not."))
        for end in ("ReportEndKnown", "ReportEndUnknown"):
            self.assertTrue(texts["TLM_MSG_GW_" + end].endswith("Greenwater road complete. Iron Junction is also playable; Red Hollow and the fair are not."))
        self.assertIn("Mercy briefing. Greenwater and Iron Junction are playable. Red Hollow and the fair are not.", texts["TLM_MSG_MB_Hub"])
        for record in ("PritchardHandOff", "PritchardAfter", "PritchardAfterAndMore"):
            self.assertIn("[Opening complete. Greenwater and Iron Junction are playable.]", texts["TLM_MSG_A1_" + record])
        travel = [r for r in self.plugin["Records"] if r["EditorId"] == "TLM_ACTI_NM_Travel"][0]
        self.assertEqual(travel["Name"], "Iron Junction story test")
        guide = (ROOT / "scripts" / "Source" / "User" / "TLM" / "Act1Guide.psc").read_text()
        self.assertIn("Greenwater and Iron Junction are available at their story test points. Red Hollow and the fair are not playable. "
                      "Optional Mercy evidence and briefs remain available.", guide)
        # Nothing built still says that one road alone is playable, or that Iron Junction is not.
        for name, text in texts.items():
            self.assertNotIn("Only Greenwater", text, name)
            self.assertNotIn("Only the Greenwater", text, name)
            self.assertNotIn("the other roads are not", text, name)

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
                self.assertLessEqual(len(m["Buttons"]), 4, name)
                for b in m["Buttons"]:
                    self.assertLessEqual(len(b["Text"]), 48, name)
        self.assertEqual(longest, 239)                               # measured: Dole naming himself, with his name

    def test_nothing_names_what_act_one_does_not_know(self):
        for name, m in self.messages.items():
            if name.startswith(G):
                for word in BARRED + ("red hollow fair", "your mother", "your father"):
                    self.assertNotIn(word, m["Text"].lower(), name)

    def test_the_journal_and_the_objectives_are_the_quest_files(self):
        road = [q for q in self.plugin["Quests"] if q["EditorId"] == "TLM_MQ02A"][0]
        self.assertEqual(road["Name"], self.quest["title"])
        self.assertEqual(road["Type"], "MainQuest")
        accepted = {s["n"]: s["log"] for s in self.quest["stages"]}
        built = {s["Index"]: s["Log"] for s in road["Stages"]}
        native = []
        for entry in self.map["quest"]["stages"]:
            n = entry["n"]
            if "log_ui" in entry:
                self.assertEqual(built[n], entry["log_ui"])
                native.append(n)
            else:
                self.assertEqual(built[n], accepted[n], n)
        self.assertEqual(sorted(built), sorted(e["n"] for e in self.map["quest"]["stages"]))
        # Every accepted stage is there under its own number; what is added is this build's, and says so.
        self.assertEqual(sorted(accepted), sorted(n for n in built if n not in (21, 31, 46, 47, 48, 49, 51, 56, 64)))
        self.assertEqual(native, [21, 31, 46, 47, 48, 49, 51, 56, 62, 64])
        # 62 does not say a night passed.
        self.assertNotIn("morning", built[62])
        self.assertIn("until morning", accepted[62])
        # The fallbacks' journals do not name who was not there.
        for n in (31, 46, 49):
            self.assertNotIn("Billie", built[n])
        self.assertNotIn("walk", built[48])
        self.assertNotIn("watched", built[64])
        objectives = {o["n"]: o["text"] for o in self.quest["objectives"]}
        got = {o["Index"]: o["Text"] for o in road["Objectives"]}
        for entry in self.map["quest"]["objectives"]:
            self.assertEqual(got[entry["n"]], entry["text_ui"] if entry.get("native_only") else objectives[entry["n"]])
        self.assertEqual(sorted(got), [10, 20, 40, 55, 70, 80, 90])

    def test_every_accepted_flag_has_one_fact_of_its_own(self):
        flags = [f["name"] for f in self.quest["new_flags"]]
        mapped = {f["flag"]: f["global"] for f in self.map["flags"]}
        self.assertEqual(sorted(mapped), sorted(flags))
        globals_ = {r["EditorId"] for r in self.plugin["Records"] if r["Type"] == "Global"}
        for flag, name in mapped.items():
            self.assertIn(name, globals_, flag)
        for name in self.map["facts"]:
            self.assertIn(name, globals_)
        self.assertEqual(len(set(mapped.values())), 9)
        self.assertEqual(len([g for g in globals_ if g.startswith("TLM_G_MQ02A_")]), 18)
        source = RULES.read_text()
        bodies = {}
        for piece in source.split("Function ")[1:]:
            bodies[piece.split("(")[0].strip()] = piece.split("EndFunction")[0]
        setters = {"mail_through": ["FinishForward", "FinishRun"], "mail_sold": ["FinishSale"], "line_closed": ["FinishReverse"],
                   "dole_lives": ["DoleDied", "FinishReverse", "FinishRun", "FinishSale"], "silver_rail": ["LearnSilver"],
                   "ostrander_known": ["LearnName"], "lockridge_stamping": ["KeepStamping"], "lockridge_signed": ["FinishCountersign"],
                   "lockridge_reported": ["FinishAuthority"]}
        for flag, name in mapped.items():
            where = sorted(fn for fn, body in bodies.items() if name + ".SetValueInt(" in body)
            self.assertEqual(where, setters[flag], flag)
        # No fact of this road is written by the greybox, the first section or the conversation router.
        for other in ("NightMailWalk.psc", "NightMailTalk.psc", "Act1Walk.psc"):
            text = (RULES.parent / other).read_text()
            self.assertEqual(re.findall(r"TLM_G_MQ02A_\w+\.SetValue", text), [], other)
            self.assertEqual(re.findall(r"TLM_G_SQ01_\w+\.SetValue", text), [], other)
        self.assertEqual(re.findall(r"TLM_G_SQ01_\w+\.SetValue", source), [], "the side quest's facts are read here, never written")
        self.assertEqual(re.findall(r"TLM_G_MQ02B_\w+", source), [], "Greenwater's facts are nothing to this road")

    def test_the_spec_holds_no_speech_the_writing_does_not(self):
        """The spec's accepted-writing block is the JSON's own strings: every node's text and labels, every stage's
        journal, every objective, the three documents."""
        source = SPEC.read_text()
        block = source.split("// ------------------------------------------------- the accepted writing")[1].split(
            "// ------------------------------------------------------------------ UI")[0]
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
        for d in ("yard_rules", "hymn_chalk", "hymnal_flyleaf"):
            allowed.update((self.documents[d]["title"], self.documents[d]["text"]))
        allowed.update(self.name(k) for k in ("lockridge", "tarrow", "dole"))
        # The two places a line is cut at: each is a piece of its line and nothing more.
        cuts = {" Tonight I send": "lockridge_gate", "The physic goes up the hill:": "dole_share"}
        for cut, node in cuts.items():
            self.assertEqual(self.lines[node]["text"].count(cut), 1)
        self.assertEqual([s for s in said if s not in allowed and s not in cuts], [])
        self.assertGreater(len(said), 60)


if __name__ == "__main__":
    unittest.main()
