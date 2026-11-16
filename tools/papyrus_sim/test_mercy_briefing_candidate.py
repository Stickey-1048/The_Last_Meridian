"""The Mercy briefing candidate's source manifest (ACT1-RUNTIME-001):
tools/win/mercy-briefing-candidate.json, read by tools/mercy_briefing_candidate.py.

That the checkout is the source the manifest describes: 20 scripts, eighteen
of them the text the Details package pins, one changed, one added; the id
file's earlier 316 lines untouched and eleven ids appended; the earlier
manifests unchanged and saying nothing of this candidate; and no digest of
anything compiled or built recorded that nobody measured. And that the check
notices each of those going wrong.

It lives here, with the stand-in engine's tests, only so that
tools/run_checks.sh runs it without being changed. It needs no build.

Source provenance only. Not a compile and not a game test.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_sim import ROOT

sys.path.insert(0, str(ROOT / "tools"))
import mercy_briefing_candidate as candidate                      # noqa: E402

COMPOSITION = "2efe2dbbaba543f7976a3df86bb81a96463aaa90"
NEEDED = (("scripts/Source/User/TLM", True), ("tools/PluginBuilder", False), ("tools/WorldSliceBuilder", False),
          ("tools/win", False), ("assets/incoming/act1/story", False))


def copy_of_the_tree():
    """A copy of just what the check reads."""
    root = Path(tempfile.mkdtemp(prefix="tlm-candidate-"))
    for name in ("scripts/Source/User/TLM",):
        shutil.copytree(ROOT / name, root / name)
    for name in candidate.BUILDER_SOURCES + candidate.OLD_MANIFESTS + ("tools/win/mercy-briefing-candidate.json",
                                                                         "assets/incoming/act1/story/documents.json"):
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, root / name)
    return root


class TheCandidate(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(candidate.MANIFEST.read_text())

    def test_the_checkout_is_the_source_the_manifest_describes(self):
        self.assertEqual(candidate.problems(), [])

    def test_it_is_twenty_scripts_one_changed_and_one_added(self):
        m = self.manifest
        self.assertEqual((m["scripts"], len(m["sourceTextSha256"])), (20, 20))
        self.assertEqual((m["changed"], m["added"], len(m["unchangedFromTheDetailsPins"])), (["Act1Walk.psc"], ["MercyBriefing.psc"], 18))
        old = json.loads(candidate.DETAILS.read_text())
        self.assertEqual(len(old["sourceTextSha256"]), 19)
        self.assertEqual(len(old["runtime"]), 19)
        for name in m["unchangedFromTheDetailsPins"]:
            self.assertEqual(m["sourceTextSha256"][name], old["sourceTextSha256"][name], name)
        self.assertNotEqual(m["sourceTextSha256"]["Act1Walk.psc"], old["sourceTextSha256"]["Act1Walk.psc"])
        for untouched in ("MQ01Quest.psc", "SQ01Quest.psc", "Act1Talk.psc", "WorldEntry.psc", "WorldEntryPlayer.psc", "Core.psc",
                          "SelfTest.psc", "MatrixCases.psc"):
            self.assertIn(untouched, m["unchangedFromTheDetailsPins"])

    def test_the_earlier_ids_are_untouched_and_eleven_are_appended(self):
        ids = self.manifest["idFile"]
        self.assertEqual(ids["earlierLines"], 316)
        self.assertEqual(len(ids["appended"]), 11)
        self.assertEqual(sorted(ids["appended"].values()), list(range(2206, 2217)))
        self.assertEqual(ids["appended"]["TLM_MercyBriefing"], 2207)
        self.assertEqual(ids["appended"]["TLM_BOOK_Docket2298"], 2206)
        # Against the id file of the commit this candidate was composed from, where that commit is to hand.
        got = subprocess.run(["git", "show", COMPOSITION + ":tools/PluginBuilder/formkeys.txt"], cwd=ROOT, capture_output=True)
        if got.returncode != 0:
            self.skipTest("the composition commit is not in this copy; the recorded digest of the earlier lines was still checked")
        before = got.stdout.decode("utf-8").replace("\r\n", "\n")
        now = (ROOT / "tools/PluginBuilder/formkeys.txt").read_text().replace("\r\n", "\n")
        self.assertEqual(len(before.splitlines()), 316)
        self.assertTrue(now.startswith(before), "the id file no longer begins with the id file it grew from")

    def test_nothing_built_or_compiled_is_claimed(self):
        measured = self.manifest["measured"]
        for key in ("masterSha256", "worldSha256", "runtime", "runtimeManifestSha256", "measuredBy", "measuredFrom"):
            self.assertIsNone(measured[key], key)
        self.assertIn("SOURCE CANDIDATE ONLY", self.manifest["status"])
        text = candidate.MANIFEST.read_text()
        old = json.loads(candidate.DETAILS.read_text())
        for pinned in [old["masterSha256"], old["worldSha256"], old["runtimeManifestSha256"]] + list(old["runtime"].values()):
            self.assertNotIn(pinned, text, "a digest of the 19-script package is in the candidate's manifest")

    def test_the_earlier_manifests_are_as_they_were_and_say_nothing_of_it(self):
        for name, digest in self.manifest["earlierManifestsSha256"].items():
            self.assertEqual(candidate.file_digest(ROOT / name), digest, name)
            self.assertNotIn("MercyBriefing", (ROOT / name).read_text())
        got = subprocess.run(["git", "diff", "--quiet", COMPOSITION, "--"] + list(candidate.OLD_MANIFESTS), cwd=ROOT)
        if got.returncode not in (0, 1):
            self.skipTest("the composition commit is not in this copy")
        self.assertEqual(got.returncode, 0, "an earlier manifest differs from the composition commit's")

    def test_measuring_reads_a_bundle_and_changes_nothing(self):
        bundle = Path(tempfile.mkdtemp(prefix="tlm-bundle-"))
        (bundle / "Scripts" / "TLM").mkdir(parents=True)
        (bundle / "TheLastMeridian.esp").write_bytes(b"not a plugin")
        for name in ("B.pex", "A.pex"):
            (bundle / "Scripts" / "TLM" / name).write_bytes(name.encode())
        before = candidate.MANIFEST.read_bytes()
        got = candidate.measure(bundle)
        self.assertEqual((got["runtimeCount"], sorted(got["runtime"]), got["worldSha256"]), (2, ["A.pex", "B.pex"], None))
        self.assertEqual(len(got["masterSha256"]), 64)
        self.assertEqual(candidate.MANIFEST.read_bytes(), before)


class WhatTheCheckCatches(unittest.TestCase):
    def damaged(self, change):
        root = copy_of_the_tree()
        self.assertEqual(candidate.problems(root, root / "tools/win/mercy-briefing-candidate.json"), [], "the copy is sound before it is damaged")
        change(root)
        return " | ".join(candidate.problems(root, root / "tools/win/mercy-briefing-candidate.json"))

    def edit(self, root, name, old, new):
        path = root / name
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1))

    def test_a_script_changed(self):
        self.assertIn("MercyBriefing.psc is not the source", self.damaged(lambda r: self.edit(r, "scripts/Source/User/TLM/MercyBriefing.psc", "ACK_POLLS = 10", "ACK_POLLS = 11")))
        self.assertIn("MQ01Quest.psc is not the source", self.damaged(lambda r: self.edit(r, "scripts/Source/User/TLM/MQ01Quest.psc", "TIMER_EVADE = 1", "TIMER_EVADE = 2")))

    def test_an_untouched_script_changed_is_also_seen_against_the_details_pins(self):
        self.assertIn("against the Details pins: changed ['Act1Walk.psc', 'Core.psc']",
                      self.damaged(lambda r: (r / "scripts/Source/User/TLM/Core.psc").write_text((r / "scripts/Source/User/TLM/Core.psc").read_text() + "\n; x\n")))

    def test_a_script_more_or_fewer(self):
        self.assertIn("only here ['Extra.psc']", self.damaged(lambda r: (r / "scripts/Source/User/TLM/Extra.psc").write_text("Scriptname TLM:Extra\n")))
        self.assertIn("only in the manifest ['MercyBriefing.psc']", self.damaged(lambda r: (r / "scripts/Source/User/TLM/MercyBriefing.psc").unlink()))

    def test_line_ends_alone_are_not_a_change(self):
        def crlf(root):
            path = root / "scripts/Source/User/TLM/MercyBriefing.psc"
            path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        self.assertEqual(self.damaged(crlf), "")

    def test_an_earlier_id_renumbered_or_a_new_one_moved(self):
        self.assertIn("idFile", self.damaged(lambda r: self.edit(r, "tools/PluginBuilder/formkeys.txt", "TLM_G_CaravanOutcome\n2049", "TLM_G_CaravanOutcome\n2999")))
        self.assertIn("idFile", self.damaged(lambda r: self.edit(r, "tools/PluginBuilder/formkeys.txt", "TLM_MercyBriefing\n2207", "TLM_MercyBriefing\n2300")))

    def test_the_spec_or_the_document_changed(self):
        self.assertIn("builderSourceTextSha256", self.damaged(lambda r: self.edit(r, "tools/PluginBuilder/SpecMercyBriefing.cs", "Not now.", "Later.")))
        self.assertIn("document", self.damaged(lambda r: self.edit(r, "assets/incoming/act1/story/documents.json", "MERCY ROAD CASE: SPRING 2298", "MERCY ROAD CASE: SPRING 2299")))

    def test_an_earlier_manifest_changed_or_made_to_describe_the_candidate(self):
        self.assertIn("earlierManifestsSha256", self.damaged(lambda r: self.edit(r, "tools/win/world-details-artifact.json", '"schema": 1', '"schema": 2')))

        def under_the_old_pins(root):
            path = root / "tools/win/world-details-artifact.json"
            data = json.loads(path.read_text())
            data["sourceTextSha256"]["MercyBriefing.psc"] = "0" * 64
            path.write_text(json.dumps(data, indent=2))
        self.assertIn("must not be put under an earlier manifest", self.damaged(under_the_old_pins))

    def test_a_built_digest_nobody_measured(self):
        def invented(root):
            path = root / "tools/win/mercy-briefing-candidate.json"
            data = json.loads(path.read_text())
            data["measured"]["masterSha256"] = "A" * 64
            path.write_text(json.dumps(data, indent=2))
        self.assertIn("without who measured it", self.damaged(invented))


if __name__ == "__main__":
    unittest.main()
