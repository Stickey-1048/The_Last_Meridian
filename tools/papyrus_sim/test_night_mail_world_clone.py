"""Actual stand-in plugin binary cloning/readback; no terrain/native claim."""
import json
import math
import unittest
from test_greenwater_world_clone import clone


class NightMailClone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        got = clone()
        if got.returncode:
            raise AssertionError(got.stdout + got.stderr)
        cls.out = json.loads(got.stdout)

    def test_only_the_two_mercy_pieces_are_cloned_into_the_exterior(self):
        n = self.out["nightMail"]
        self.assertEqual(n["script"], "TLM:NightMailWalk")
        self.assertEqual(len(n["aliases"]), 51)
        self.assertEqual(len({a["id"] for a in n["aliases"]}), 51)
        exterior = {a["name"]: a for a in n["aliases"] if a["owner"] == "TLMWorldSlice.esp"}
        self.assertEqual(set(exterior), {"MercyTravel", "MercyReturn"})
        for name, a in exterior.items():
            self.assertEqual(a["reference"], "TLM_WS_ST_NM_" + name)
            self.assertEqual([a["x"], a["y"], a["z"]], self.out["nightMailSites"][name])
        for a in n["aliases"]:
            self.assertEqual(a["flags"] & 0xC00, 0xC00, a["name"])
            if a["name"] not in exterior:
                self.assertEqual(a["owner"], "TheLastMeridian.esp")
                self.assertEqual(a["reference"], "TLM_REF_NM_" + a["name"])
        self.assertEqual(self.out["persistentReferences"], 68)

    def test_binding_ownership_and_road_identity(self):
        n = self.out["nightMail"]
        self.assertEqual(self.out["firstSection"]["forms"]["TLM_NightMail"], "TLM_WS_NM")
        self.assertEqual(n["forms"]["TLM_MQ02A"], "TLM_MQ02A in TheLastMeridian.esp")
        self.assertNotIn("TLM_MQ02A", self.out["quests"])
        self.assertTrue(n["aliasScripts"])
        for a in n["aliasScripts"]:
            self.assertEqual((a["on"], a["scripts"]), ("TLM_WS_NM", ["TLM:NightMailTalk"]))
        for where in n["ownAliases"].values():
            self.assertTrue(where.startswith("TLM_WS_NM alias "), where)
        for name, entries in n["lists"].items():
            prefix = "TLM_MQ02A in TheLastMeridian.esp alias " if name == "CastInto" else "TLM_WS_NM alias "
            self.assertTrue(entries, name)
            self.assertTrue(all(e.startswith(prefix) for e in entries), (name, entries))

    def test_mercy_markers_are_clear_of_known_actors_and_cabin_footprint(self):
        sites = self.out["nightMailSites"]
        for name, (x, y, z) in sites.items():
            self.assertTrue(2536 < x < 3560 and 2560 < y < 2672, name)
            self.assertGreater(z, 0)
            for px, py in ((3260,2530),(2850,2530),(3380,2500),(3150,2620),(3150,2700)):
                self.assertGreaterEqual(math.hypot(x-px,y-py), 128, name)

    def test_invalid_night_mail_sources_are_refused(self):
        cases = {
            "night-mail-binding-removed": "First section is not bound",
            "night-mail-binding-to-another-quest": "First section is not bound",
            "night-mail-binding-as-alias": "First section is not bound",
            "night-mail-alias-dropped": "Unexpected Night Mail alias contract",
            "night-mail-placement-missing": "Missing or substituted Night Mail source placement",
            "night-mail-placement-substituted": "Missing or substituted Night Mail source placement",
            "night-mail-road-missing": "Night Mail greybox without its road quest",
            "night-mail-cell-missing": "Night Mail own cell missing",
            "night-mail-interior-moved": "Night Mail interior placement outside its own cell",
        }
        for damage, reason in cases.items():
            with self.subTest(damage=damage):
                got = clone(damage)
                self.assertEqual(got.returncode, 1, got.stdout + got.stderr)
                self.assertIn(reason, got.stderr)

    def test_pre_night_mail_source_preserves_greenwater(self):
        got = clone("source-without-night-mail")
        self.assertEqual(got.returncode, 0, got.stdout + got.stderr)
        out = json.loads(got.stdout)
        self.assertFalse(out["nightMail"]["present"])
        self.assertNotIn("TLM_NightMail", out["firstSection"]["forms"])
        self.assertEqual(out["persistentReferences"], 62)
        self.assertEqual(out["quests"], ["TLM_WS_A1", "TLM_WS_Entry", "TLM_WS_GW"])


if __name__ == "__main__":
    unittest.main()
