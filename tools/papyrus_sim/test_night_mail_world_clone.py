"""The exterior builder's story-cloning step, for the Night Mail (NIGHT-MAIL-STORY-001), on a stand-in build.

As test_greenwater_world_clone.py: the story plugin is built against the
default stand-in master, WorldSliceBuilder --story-clone-check runs the
cloning step and the builder's own check of the written file, and what comes
out is read. The Night Mail's greybox is cloned beside the first section's and
Greenwater's with new persistent references for ONLY its two pieces at Mercy;
every other alias of the clone keeps pointing at the story master's own cell
(TLM_CELL_NightMail); the road quest stays in the story master. Then the
source is damaged in memory, one way at a time, and each has to be refused.

Also from the sources, with no build: that the exterior builder's two sites
are the ones the plugin spec gives, and that they stand in the yard clear of
everything else there, Greenwater's pieces included.

This is the cloning code on a stand-in. It is NOT the exterior build: no
terrain, scenery, route, collision or prop check ran, nothing was built
against the game's master, and nothing here was seen in the game.
"""
import json
import math
import re
import unittest

from test_sim import ROOT
from test_greenwater_world_clone import STORY, clone, dotnet, DLL, stand_in_story, spec_sites

SPEC = ROOT / "tools" / "PluginBuilder" / "SpecNightMail.cs"


class TheClone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        got = clone()
        if got.returncode != 0:
            raise AssertionError("the cloning step refused the stand-in build: " + got.stderr[-600:])
        cls.out = json.loads(got.stdout)
        cls.nm = cls.out["nightMail"]

    def test_the_exterior_first_section_opens_the_exterior_night_mail_greybox(self):
        self.assertEqual(self.out["firstSection"]["forms"]["TLM_NightMail"], "TLM_WS_NM")
        self.assertEqual(self.out["firstSection"]["forms"]["TLM_Greenwater"], "TLM_WS_GW")

    def test_only_the_two_pieces_at_mercy_have_references_of_their_own(self):
        n = self.nm
        self.assertTrue(n["present"])
        self.assertEqual(n["script"], "TLM:NightMailWalk")
        mine = {a["name"]: a for a in n["aliases"] if a["inAddon"]}
        self.assertEqual(sorted(mine), sorted(self.out["nightMailSites"]))
        for name, a in mine.items():
            self.assertEqual([a["x"], a["y"], a["z"]], self.out["nightMailSites"][name], name)
            self.assertEqual(a["reference"], "TLM_WS_ST_NM_" + name)
            self.assertEqual(a["flags"] & 0xC00, 0xC00, name + " is not persistent and initially disabled")
            self.assertFalse(a["actor"])
        self.assertEqual(self.out["persistentReferences"], 29 + 31 + 2)

    def test_every_other_alias_still_points_at_the_story_masters_own_cell(self):
        rest = [a for a in self.nm["aliases"] if not a["inAddon"]]
        self.assertEqual(len(rest) + 2, len(self.nm["aliases"]))
        self.assertGreater(len(rest), 40)
        for a in rest:
            self.assertTrue(a["reference"].startswith("TLM_REF_NM_"), a)
        # Including the three people and the three Black Rail, who are actors of the master's own.
        self.assertEqual(sorted(a["name"] for a in rest if a["actor"]), ["Billie", "Dole", "Lockridge", "Rifle1", "Rifle2", "Rifle3"])

    def test_the_greyboxs_bindings_point_where_they_must(self):
        n = self.nm
        self.assertEqual(n["forms"]["TLM_MQ02A"], "TLM_MQ02A in TheLastMeridian.esp")
        for name, where in n["forms"].items():
            self.assertTrue(where.endswith("TheLastMeridian.esp"), "%s points at %s" % (name, where))
        for name, where in n["ownAliases"].items():
            self.assertTrue(where.startswith("TLM_WS_NM alias "), "%s points at %s" % (name, where))
        self.assertGreater(len(n["ownAliases"]), 30)
        for name in ("ZoneOn", "CastFrom"):
            self.assertTrue(all(item.startswith("TLM_WS_NM alias ") for item in n["lists"][name]), name)
        self.assertTrue(all(item.startswith("TLM_MQ02A in TheLastMeridian.esp alias ") for item in n["lists"]["CastInto"]))
        self.assertEqual(len(n["lists"]["CastFrom"]), len(n["lists"]["CastInto"]))
        self.assertTrue(all(s["on"] == "TLM_WS_NM" and s["scripts"] == ["TLM:NightMailTalk"] for s in n["aliasScripts"]))

    def test_the_road_and_the_cell_stay_in_the_story_master(self):
        self.assertEqual(self.out["quests"], ["TLM_WS_A1", "TLM_WS_Entry", "TLM_WS_GW", "TLM_WS_NM"])
        self.assertEqual(self.out["masters"], ["Fallout4.esm", "TheLastMeridian.esp"])
        self.assertEqual(self.nm["forms"].get("TLM_MQ01"), "TLM_MQ01 in TheLastMeridian.esp")

    def test_greenwaters_clone_is_as_it_was(self):
        g = self.out["greenwater"]
        self.assertEqual(len(g["aliases"]), 31)
        self.assertTrue(all(a["reference"].startswith("TLM_WS_ST_GW_") for a in g["aliases"]))


class WhatTheClonerRefuses(unittest.TestCase):
    def test_each_damaged_source(self):
        cases = {
            "nightmail-binding-removed": "First section is not bound to the story master's Night Mail greybox",
            "nightmail-binding-to-another-quest": "First section is not bound to the story master's Night Mail greybox",
            "nightmail-binding-as-alias": "First section is not bound to the story master's Night Mail greybox",
            "nightmail-alias-dropped": "Unexpected Night Mail alias contract",
            "nightmail-mercy-placement-missing": "Unexpected Night Mail alias contract",
            "nightmail-road-quest-missing": "Night Mail greybox without its road quest",
            "nightmail-source-without-the-second-mercy-piece": "Unexpected Night Mail alias contract",
        }
        for damage, why in cases.items():
            with self.subTest(damage):
                got = clone(damage)
                self.assertEqual(got.returncode, 1, got.stdout[-300:] + got.stderr[-300:])
                self.assertIn("REFUSED: " + why, got.stderr)

    def test_a_source_from_before_the_road_is_cloned_as_it_was(self):
        got = clone("source-without-nightmail")
        self.assertEqual(got.returncode, 0, got.stderr[-400:])
        out = json.loads(got.stdout)
        self.assertEqual((out["quests"], out["persistentReferences"], out["nightMail"]["present"]),
                         (["TLM_WS_A1", "TLM_WS_Entry", "TLM_WS_GW"], 29 + 31, False))
        self.assertNotIn("TLM_NightMail", out["firstSection"]["forms"])
        self.assertIn("TLM_Greenwater", out["firstSection"]["forms"])


class TheSites(unittest.TestCase):
    """From the sources; no build."""

    def setUp(self):
        text = STORY.read_text().split("NightMailSites=new(){")[1].split("};")[0]
        self.sites = {m.group(1): [float(m.group(2)), float(m.group(3)), float(m.group(4))]
                      for m in re.finditer(r'\["(\w+)"\]=\((\d+),(\d+),(\d+)\)', text)}
        green = STORY.read_text().split("GreenwaterSites=new(){")[1].split("};")[0]
        self.green = {m.group(1): (float(m.group(2)), float(m.group(3)), float(m.group(4)))
                      for m in re.finditer(r'\["(\w+)"\]=\((\d+),(\d+),(\d+)\)', green)}

    def test_the_exterior_builder_and_the_plugin_spec_give_the_same_sites(self):
        spec = {k: v for k, v in spec_sites_of_night_mail().items() if k in self.sites}
        self.assertEqual(sorted(self.sites), ["MercyReturn", "MercyTravel"])
        self.assertEqual(self.sites, spec)

    def test_the_two_stand_in_the_yard_clear_of_what_is_there_and_of_greenwaters_pieces(self):
        # The yard's fence: x 2408 to 3688, y 2432 to 3456; the cabin's floor from y 2672 (Program.cs); Pritchard at
        # (3260, 2530), Talbot at (2850, 2530), the guide at (3380, 2500); the gateway's posts at (2920, 2380) and
        # (3176, 2380); Greenwater's own two pieces.
        there = {"Pritchard": (3260, 2530), "Talbot": (2850, 2530), "GuideMercy": (3380, 2500), "GateLeft": (2920, 2380), "GateRight": (3176, 2380),
                 "GreenwaterTravel": self.green["MercyTravel"][:2], "GreenwaterReturn": self.green["MercyReturn"][:2]}
        for name, (x, y, z) in self.sites.items():
            self.assertTrue(2408 + 128 < x < 3688 - 128 and 2432 + 128 < y < 2672, name)
            for what, (sx, sy) in there.items():
                self.assertGreaterEqual(math.hypot(x - sx, y - sy), 128, "%s is too close to %s" % (name, what))
        a, b = self.sites["MercyTravel"], self.sites["MercyReturn"]
        self.assertGreaterEqual(math.hypot(a[0] - b[0], a[1] - b[1]), 128)

    def test_greenwaters_sites_did_not_move(self):
        self.assertEqual(self.green["MercyTravel"], (3150.0, 2620.0, 12.0))
        self.assertEqual(self.green["MercyReturn"], (3150.0, 2700.0, 32.0))
        self.assertEqual(len(self.green), 31)


def spec_sites_of_night_mail():
    """(x, y, z) of the two Mercy pieces in the plugin spec, by alias."""
    text = SPEC.read_text()
    out = {}
    for name in ("MercyTravel", "MercyReturn"):
        m = re.search(r'new\("%s", "[^"]*", "[^"]+", (\d+), (\d+), (\d+)' % name, text)
        out[name] = [float(m.group(1)), float(m.group(2)), float(m.group(3))]
    return out


if __name__ == "__main__":
    unittest.main()
