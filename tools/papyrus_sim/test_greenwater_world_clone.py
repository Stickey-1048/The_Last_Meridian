"""The exterior builder's story-cloning step, on a stand-in build (GREENWATER-STORY-001).

tools/WorldSliceBuilder needs the game's own master to build the owner's
world, and that is not here. Its cloning of the story quests into that world
needs only the story plugin. This test builds the plugin against the default
stand-in master, runs that one step and the builder's own check of the
written file (WorldSliceBuilder --story-clone-check), and reads what came
out: the first section cloned as before, the Greenwater greybox cloned beside
it with its own references at its sites, every binding pointing where it
must, and the road quest left in the story master. Then the source is damaged
in memory, one way at a time, and each has to be refused.

Also here, from the sources and with no build: that the sites in the
exterior builder are the ones the plugin spec gives, and that they stand on
ground the expansion leaves free.

This is the cloning code on a stand-in. It is NOT the exterior build: no
terrain, scenery, route, collision or prop check ran, nothing was built
against the game's master, and nothing here was seen in the game.
"""
import json
import math
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_sim import ROOT

DLL = ROOT / "tools" / "WorldSliceBuilder" / "bin" / "Debug" / "net8.0" / "WorldSliceBuilder.dll"
SPEC = ROOT / "tools" / "PluginBuilder" / "SpecGreenwater.cs"
STORY = ROOT / "tools" / "WorldSliceBuilder" / "WorldStory.cs"
EXPANSION = ROOT / "tools" / "WorldSliceBuilder" / "Expansion.cs"
PROGRAM = ROOT / "tools" / "WorldSliceBuilder" / "Program.cs"
# The commit the repair was made from: the first section's own sites are as they were there.
REVIEWED = "7e05c6b879e21940786c008f9dcdef4d5404654c"
PEOPLE = {"Opal", "Hatcher", "Rafferty", "Belden", "Crew1", "Crew2"}
_built = {}


def dotnet(*args, **kw):
    return subprocess.run(["dotnet"] + [str(a) for a in args], cwd=ROOT, capture_output=True, text=True,
                          env={**__import__("os").environ, "DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_NOLOGO": "1"}, **kw)


def stand_in_story():
    """The story plugin built against the default stand-in master, once for this module."""
    if "story" not in _built:
        folder = Path(tempfile.mkdtemp(prefix="tlm-clone-"))
        made = dotnet("run", "--project", "tools/StandInMaster", "--", folder / "Fallout4.esm", "default")
        if made.returncode != 0:
            raise AssertionError("the stand-in master was not written: " + made.stdout[-400:] + made.stderr[-400:])
        built = dotnet("run", "--project", "tools/PluginBuilder", "--", "--out", folder / "out", "--fallout4-esm", folder / "Fallout4.esm")
        if built.returncode != 0 or "self-check: the file read back matches the spec" not in built.stdout:
            raise AssertionError("the plugin was not built against the stand-in master: " + built.stdout[-600:] + built.stderr[-400:])
        if not DLL.exists():
            dotnet("build", "tools/WorldSliceBuilder", "--nologo")
        _built["folder"], _built["story"] = folder, folder / "out" / "TheLastMeridian.esp"
    return _built["story"]


def clone(damage=None):
    out = Path(tempfile.mkdtemp(prefix="tlm-clone-out-")) / "world"
    args = [DLL, "--story-clone-check", stand_in_story(), out] + (["--damage", damage] if damage else [])
    return dotnet(*args)


def spec_sites():
    """(x, y, z) of every part in the plugin spec, by alias."""
    sites = {}
    for m in re.finditer(r'new\("(\w+)", (?:"[^"]*"|\w+), "[^"]+", (\d+), (\d+)(?:, (\d+))?', SPEC.read_text()):
        sites[m.group(1)] = [float(m.group(2)), float(m.group(3)), float(m.group(4) or 0)]
    return sites


class TheClone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        got = clone()
        if got.returncode != 0:
            raise AssertionError("the cloning step refused the stand-in build: " + got.stderr[-600:])
        cls.out = json.loads(got.stdout)

    def test_the_first_section_is_cloned_as_it_was(self):
        a = self.out["firstSection"]
        self.assertEqual((a["script"], len(a["aliases"])), ("TLM:Act1Walk", 29))
        self.assertEqual(a["forms"]["TLM_MercyBriefing"], "TLM_MercyBriefing in TheLastMeridian.esp")
        self.assertEqual(a["forms"]["TLM_MQ01"], "TLM_MQ01 in TheLastMeridian.esp")
        self.assertEqual(len(a["lists"]["Everything"]), 29)
        self.assertTrue(all(ref["reference"].startswith("TLM_WS_ST_") and not ref["reference"].startswith("TLM_WS_ST_GW_") for ref in a["aliases"]))

    def test_the_exterior_first_section_opens_the_exterior_greybox(self):
        self.assertEqual(self.out["firstSection"]["forms"]["TLM_Greenwater"], "TLM_WS_GW")

    def test_the_greybox_has_its_own_references_at_its_sites(self):
        g = self.out["greenwater"]
        self.assertTrue(g["present"])
        self.assertEqual(g["script"], "TLM:GreenwaterWalk")
        sites = self.out["sites"]
        self.assertEqual(len(g["aliases"]), 31)
        self.assertEqual(sorted(a["name"] for a in g["aliases"]), sorted(sites))
        for a in g["aliases"]:
            self.assertEqual([a["x"], a["y"], a["z"]], sites[a["name"]], a["name"])
            self.assertEqual(a["reference"], "TLM_WS_ST_GW_" + a["name"])
            self.assertEqual(a["flags"] & 0xC00, 0xC00, a["name"] + " is not persistent and initially disabled")
            self.assertEqual(a["actor"], a["name"] in PEOPLE, a["name"])
        self.assertEqual(self.out["persistentReferences"], 29 + 31)

    def test_the_greyboxs_bindings_point_where_they_must(self):
        g = self.out["greenwater"]
        self.assertEqual(g["forms"]["TLM_MQ02B"], "TLM_MQ02B in TheLastMeridian.esp")
        self.assertEqual(g["forms"]["TLM_MQ01"], "TLM_MQ01 in TheLastMeridian.esp")
        self.assertEqual(g["forms"]["TLM_G_MQ01_Done"], "TheLastMeridian.esp" if False else g["forms"]["TLM_G_MQ01_Done"])
        for name, where in g["forms"].items():
            self.assertTrue(where.endswith("TheLastMeridian.esp"), "%s points at %s" % (name, where))
        for name, where in g["ownAliases"].items():
            self.assertTrue(where.startswith("TLM_WS_GW alias "), "%s points at %s" % (name, where))
        self.assertEqual(len(g["ownAliases"]), 19)
        for name in ("ZoneOn", "CastFrom"):
            self.assertTrue(all(item.startswith("TLM_WS_GW alias ") for item in g["lists"][name]), name)
        self.assertTrue(all(item.startswith("TLM_MQ02B in TheLastMeridian.esp alias ") for item in g["lists"]["CastInto"]))
        self.assertEqual((len(g["lists"]["CastFrom"]), len(g["lists"]["CastInto"]), len(g["lists"]["ZoneOn"])), (11, 11, 26))
        self.assertEqual(len(g["aliasScripts"]), 27)
        self.assertTrue(all(s["on"] == "TLM_WS_GW" and s["scripts"] == ["TLM:GreenwaterTalk"] for s in g["aliasScripts"]))

    def test_the_road_stays_in_the_story_master(self):
        self.assertEqual(self.out["quests"], ["TLM_WS_A1", "TLM_WS_Entry", "TLM_WS_GW"])
        self.assertEqual(self.out["masters"], ["Fallout4.esm", "TheLastMeridian.esp"])


class WhatTheClonerRefuses(unittest.TestCase):
    def test_each_damaged_source(self):
        cases = {
            "greenwater-binding-removed": "First section is not bound to the story master's Greenwater greybox",
            "greenwater-binding-to-another-quest": "First section is not bound to the story master's Greenwater greybox",
            "greenwater-binding-as-alias": "First section is not bound to the story master's Greenwater greybox",
            "briefing-binding-removed": "Mercy briefing binding missing or not the story master's TLM_MercyBriefing",
            "greenwater-alias-dropped": "Unexpected Greenwater alias contract",
            "greenwater-placement-missing": "Missing Greenwater source placement",
            "road-quest-missing": "Greenwater greybox without its road quest",
        }
        for damage, why in cases.items():
            with self.subTest(damage):
                got = clone(damage)
                self.assertEqual(got.returncode, 1, got.stdout[-300:] + got.stderr[-300:])
                self.assertIn("REFUSED: " + why, got.stderr)

    def test_a_source_from_before_the_road_is_cloned_as_it_was(self):
        got = clone("source-without-greenwater")
        self.assertEqual(got.returncode, 0, got.stderr[-400:])
        out = json.loads(got.stdout)
        self.assertEqual((out["quests"], out["persistentReferences"], out["greenwater"]["present"]), (["TLM_WS_A1", "TLM_WS_Entry"], 29, False))
        self.assertNotIn("TLM_Greenwater", out["firstSection"]["forms"])

    def test_an_unknown_damage_and_an_occupied_output_are_not_run(self):
        self.assertEqual(clone("no-such-damage").returncode, 2)
        occupied = Path(tempfile.mkdtemp(prefix="tlm-clone-occupied-"))
        (occupied / "keep.txt").write_text("owner content")
        got = dotnet(DLL, "--story-clone-check", stand_in_story(), occupied)
        self.assertEqual(got.returncode, 2)
        self.assertEqual((occupied / "keep.txt").read_text(), "owner content")


class TheSites(unittest.TestCase):
    """From the sources; no build."""

    def setUp(self):
        text = STORY.read_text().split("GreenwaterSites=new(){")[1].split("};")[0]
        self.sites = {m.group(1): [float(m.group(2)), float(m.group(3)), float(m.group(4))]
                      for m in re.finditer(r'\["(\w+)"\]=\((\d+),(\d+),(\d+)\)', text)}

    def test_the_exterior_builder_and_the_plugin_spec_give_the_same_sites(self):
        self.assertEqual(self.sites, spec_sites())
        self.assertEqual(len(self.sites), 31)

    def test_greenwater_stands_on_ground_the_expansion_leaves_free(self):
        scenery = [(m.group(1), float(m.group(2)), float(m.group(3)))
                   for m in re.finditer(r'Place\("(\w+)","\w+",(\d+),(\d+)', EXPANSION.read_text())]
        self.assertGreater(len(scenery), 15)
        for name, (x, y, z) in self.sites.items():
            if name.startswith("Mercy"):
                continue
            self.assertTrue(1250 <= x <= 2850 and 200 <= y <= 700, name)
            near = min((math.hypot(x - sx, y - sy), prop) for prop, sx, sy in scenery)
            self.assertGreaterEqual(near[0], 600, "%s is %d from %s" % (name, near[0], near[1]))
        # The bypass road's nearest stretch, (1200,1200)-(2200,1000)-(2700,1700), with its posts 144 to either side.
        for name, (x, y, z) in self.sites.items():
            if not name.startswith("Mercy"):
                self.assertLessEqual(y, 700, name)

    def cabin_floor(self):
        """The cabin's floor as the exterior builder's source lays it: (min x, max x, min y, max y, surface z).
        From the source only. The tile's real bounds are in the game's master, which is not here; the builder's
        own furniture check takes the same footprint 4 units smaller on every side."""
        source = PROGRAM.read_text()
        loop = re.search(r"for\(int col=0;col<(\d+);col\+\+\)for\(int row=0;row<(\d+);row\+\+\)\{\s*"
                         r"float x=(\d+)\+col\*(\d+),y=(\d+)\+row\*(\d+);\s*Put\(\$\"CabinFloor\{col\}\{row\}\",floor,x,y,(\d+)\);", source)
        self.assertIsNotNone(loop, "the cabin's floor is no longer laid as this test reads it")
        cols, rows, x0, dx, y0, dy, z = (int(v) for v in loop.groups())
        self.assertEqual((dx, dy), (256, 256))
        self.assertIn('var floor=Static("workshop_ShackMidFloor01B")', source)
        return (x0 - dx / 2, x0 + (cols - 1) * dx + dx / 2, y0 - dy / 2, y0 + (rows - 1) * dy + dy / 2, z)

    def test_the_return_marker_stands_above_the_cabins_floor_and_nothing_else_is_over_it(self):
        """Repair, finding 8. MercyReturn is the one site inside the footprint of the cabin's floor tiles, whose
        surface the exterior builder gives as Z 16 ("the native-tested supporting surface"). It stands 16 units
        above that surface, to settle, as the builder's own arrival marker stands at Z 32. This holds the
        numbers together; whether the player lands and stands there is not known and is not claimed."""
        min_x, max_x, min_y, max_y, surface = self.cabin_floor()
        self.assertEqual((min_x, max_x, min_y, max_y, surface), (2664, 3432, 2672, 3184, 16))
        self.assertIn("Existing floors are the native-tested supporting surface atZ16", PROGRAM.read_text())
        self.assertIn('Put("Arrival",Static("COCMarkerHeading"),448,640,32,', PROGRAM.read_text())
        over = sorted(name for name, (x, y, z) in self.sites.items() if min_x <= x <= max_x and min_y <= y <= max_y)
        self.assertEqual(over, ["MercyReturn"])
        x, y, z = self.sites["MercyReturn"]
        self.assertEqual((x, y, z), (3150, 2700, 32))
        self.assertEqual(z - surface, 16)
        # In front of the front wall (the tiles' middle line, y 2800) and before the gap the middle tile leaves in it.
        self.assertLess(y, 2800)
        self.assertTrue(3048 - 128 < x < 3048 + 128)
        # And the travel point, which is used and not landed on, is clear of the floor altogether.
        self.assertLess(self.sites["MercyTravel"][1], min_y)

    def test_no_other_site_moved_in_the_repair(self):
        def sites_at(commit, path, begin, end):
            got = subprocess.run(["git", "show", commit + ":" + path], cwd=ROOT, capture_output=True, text=True)
            if got.returncode != 0:
                return None
            return got.stdout.split(begin)[1].split(end)[0]
        before = sites_at(REVIEWED, "tools/WorldSliceBuilder/WorldStory.cs", "GreenwaterSites=new(){", "};")
        if before is None:
            self.skipTest("the reviewed commit is not in this copy")
        was = {m.group(1): [float(m.group(2)), float(m.group(3)), float(m.group(4))]
               for m in re.finditer(r'\["(\w+)"\]=\((\d+),(\d+),(\d+)\)', before)}
        self.assertEqual(was["MercyReturn"], [3150.0, 2700.0, 0.0])
        self.assertEqual({k: v for k, v in self.sites.items() if k != "MercyReturn"}, {k: v for k, v in was.items() if k != "MercyReturn"})
        # The first section's 29 sites and the cabin itself: the same text as at the reviewed commit.
        now = STORY.read_text()
        old = subprocess.run(["git", "show", REVIEWED + ":tools/WorldSliceBuilder/WorldStory.cs"], cwd=ROOT, capture_output=True, text=True).stdout
        cut = lambda text: text.split("var sites=new Dictionary<string,(float X,float Y,float Z)>")[1].split("};")[0]
        self.assertEqual(cut(now), cut(old))
        for name in ("tools/WorldSliceBuilder/Program.cs", "tools/WorldSliceBuilder/Expansion.cs", "tools/WorldSliceBuilder/ShelterDetails.cs"):
            self.assertEqual(subprocess.run(["git", "diff", "--quiet", REVIEWED, "--", name], cwd=ROOT).returncode, 0, name)

    def test_mercys_two_pieces_stand_in_the_yard_clear_of_what_is_there(self):
        # The yard's fence: x 2408 to 3688, y 2432 to 3456; the cabin's front wall at y 2800 (its floor reaches 128
        # units in front of that: see the test above); Pritchard at (3260, 2530), Talbot at (2850, 2530), the guide
        # at (3380, 2500); the gateway's posts at (2920, 2380) and (3176, 2380).
        there = {"Pritchard": (3260, 2530), "Talbot": (2850, 2530), "GuideMercy": (3380, 2500), "GateLeft": (2920, 2380), "GateRight": (3176, 2380)}
        for name in ("MercyTravel", "MercyReturn"):
            x, y, z = self.sites[name]
            self.assertTrue(2408 + 128 < x < 3688 - 128 and 2432 + 128 < y < 2800 - 64, name)
            for what, (sx, sy) in there.items():
                self.assertGreaterEqual(math.hypot(x - sx, y - sy), 128, "%s is too close to %s" % (name, what))


if __name__ == "__main__":
    unittest.main()
