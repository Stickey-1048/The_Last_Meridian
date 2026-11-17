"""The Mercy briefing candidate's source manifest (ACT1-RUNTIME-001):
tools/win/mercy-briefing-candidate.json, read by tools/mercy_briefing_candidate.py.

That the checkout is the source the manifest describes: 20 scripts, eighteen
of them the text the Details package pins, one changed, one added; the id
file's earlier 316 lines untouched and eleven ids appended; the earlier
manifests unchanged, byte for byte on every machine, and saying nothing of
this candidate; which compiled scripts a bundle takes from where (18 reviewed
ones of the earlier runtime, 2 fresh), kept apart from the proof that all 20
compile; and no digest of anything compiled or built for this candidate
recorded that nobody measured. And that the check notices each of those going
wrong.

It lives here, with the stand-in engine's tests, only so that
tools/run_checks.sh runs it without being changed. It needs no build.

SINCE GREENWATER-STORY-001 THIS MANIFEST IS A FROZEN EARLIER ONE. It
describes the a8 source (a8f6d64), not this checkout: Act1Walk and Act1Guide
have changed since and three scripts were added. The manifest and its check
are unchanged, and what is tested now is that
  - the check REFUSES this checkout, and for those reasons;
  - on the a8 source itself, taken from Git, it still passes and still
    notices every kind of damage it did.
The Greenwater candidate has its own manifest
(tools/win/greenwater-story-candidate.json, test_greenwater_candidate.py).

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
# The source this manifest describes: the repaired Mercy briefing.
A8 = "a8f6d6482b4b5dc9d545e197ed4cf2c8f6324306"
NEEDED = (("scripts/Source/User/TLM", True), ("tools/PluginBuilder", False), ("tools/WorldSliceBuilder", False),
          ("tools/win", False), ("assets/incoming/act1/story", False))


def copy_of_the_tree():
    """Just what the check reads, AS IT WAS AT a8, taken out of Git: the source the manifest describes.
    None if that commit is not in this copy."""
    names = ("scripts/Source/User/TLM",) + candidate.BUILDER_SOURCES + candidate.OLD_MANIFESTS + (
        "tools/win/mercy-briefing-candidate.json", "assets/incoming/act1/story/documents.json")
    packed = subprocess.run(["git", "archive", "--format=tar", A8, "--"] + list(names), cwd=ROOT, capture_output=True)
    if packed.returncode != 0:
        return None
    root = Path(tempfile.mkdtemp(prefix="tlm-candidate-"))
    subprocess.run(["tar", "-x", "-C", str(root)], input=packed.stdout, check=True)
    return root


class TheCandidate(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(candidate.MANIFEST.read_text())

    def test_the_manifest_and_its_check_are_the_ones_a8_had(self):
        for name in ("tools/win/mercy-briefing-candidate.json", "tools/mercy_briefing_candidate.py"):
            got = subprocess.run(["git", "diff", "--quiet", A8, "--", name], cwd=ROOT)
            if got.returncode not in (0, 1):
                self.skipTest("the a8 commit is not in this copy")
            self.assertEqual(got.returncode, 0, name + " differs from a8's: a frozen manifest and its check are not edited")

    def test_the_a8_source_is_the_source_the_manifest_describes(self):
        root = copy_of_the_tree()
        if root is None:
            self.skipTest("the a8 commit is not in this copy")
        self.assertEqual(candidate.problems(root, root / "tools/win/mercy-briefing-candidate.json"), [])

    def test_this_checkout_is_refused_and_for_the_right_reasons(self):
        """The Greenwater candidate changed two of the 20 scripts and added three. The a8 manifest must not pass
        for it, and no compiled script selected by that manifest may be taken for this source's."""
        said = " | ".join(candidate.problems())
        self.assertIn("Act1Walk.psc is not the source the manifest describes", said)
        self.assertIn("Act1Guide.psc is not the source the manifest describes", said)
        self.assertIn("only here ['GreenwaterTalk.psc', 'GreenwaterWalk.psc', 'MQ02AQuest.psc', 'MQ02BQuest.psc', 'MQ02CQuest.psc', 'NightMailTalk.psc', 'NightMailWalk.psc', 'RedHollowTalk.psc', 'RedHollowWalk.psc']", said)
        self.assertIn("runtimeSelection", said)
        self.assertNotIn("MercyBriefing.psc is not the source", said)       # that script is a8's, word for word
        self.assertNotIn("earlierManifestsSha256", said)                    # and the four older manifests are as they were

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
        for key in ("masterSha256", "worldSha256", "runtime", "runtimeManifestSha256", "freshCompile", "measuredBy", "measuredFrom"):
            self.assertIsNone(measured[key], key)
        self.assertIn("SOURCE CANDIDATE ONLY", self.manifest["status"])
        text = candidate.MANIFEST.read_text()
        old = json.loads(candidate.DETAILS.read_text())
        # The earlier package's plugin, exterior and Act1Walk are not this candidate's and are nowhere in its manifest.
        for pinned in (old["masterSha256"], old["worldSha256"], old["runtime"]["Act1Walk.pex"]):
            self.assertNotIn(pinned, text, "a digest of the 19-script package's own plugin, exterior or Act1Walk is in the candidate's manifest")
        # Its runtime manifest is named once, as where the 18 reviewed scripts come from; the 18 once each, as inputs.
        self.assertEqual(text.count(old["runtimeManifestSha256"]), 1)
        self.assertEqual(self.manifest["runtimeSelection"]["reusedFrom"]["runtimeManifestSha256"], old["runtimeManifestSha256"])
        for name, pinned in old["runtime"].items():
            self.assertEqual(text.count(pinned), 0 if name == "Act1Walk.pex" else 1, name)

    def test_which_compiled_scripts_go_into_the_bundle(self):
        chosen = self.manifest["runtimeSelection"]
        old = json.loads(candidate.DETAILS.read_text())
        reused, fresh = chosen["reusedReviewedPex"], chosen["freshlyCompiled"]
        self.assertEqual((len(reused), fresh), (18, ["Act1Walk.pex", "MercyBriefing.pex"]))
        self.assertEqual(set(reused) & set(fresh), set())
        self.assertEqual(sorted(list(reused) + fresh), sorted(n[:-4] + ".pex" for n in self.manifest["sourceTextSha256"]))
        # Each reused one is the earlier runtime's pinned file, and its source is that runtime's pinned source.
        for name, digest in reused.items():
            self.assertEqual(digest, old["runtime"][name], name)
            source = name[:-4] + ".psc"
            self.assertEqual(self.manifest["sourceTextSha256"][source], old["sourceTextSha256"][source], source)
            self.assertIn(source, self.manifest["unchangedFromTheDetailsPins"])
        self.assertNotIn("Act1Walk.pex", reused)
        self.assertNotIn("MercyBriefing.pex", old["runtime"])
        self.assertEqual(chosen["reusedFrom"]["manifest"], "tools/win/world-details-artifact.json")
        for word in ("18", "reviewed", "byte for byte", "fresh compile", "not bundled", "assumed"):
            self.assertIn(word, chosen["policy"])
        steps = " ".join(self.manifest["recipe"]["steps"])
        self.assertIn("COMPILE PROOF: compile all 20", steps)
        self.assertIn("Never the freshly compiled 18", steps)
        self.assertIn("--fresh-compile", steps)
        self.assertNotIn("no earlier PEX is reused", steps)

    def test_the_earlier_manifests_are_as_they_were_and_say_nothing_of_it(self):
        for name, digest in self.manifest["earlierManifestsSha256"].items():
            self.assertEqual(candidate.file_digest(ROOT / name), digest, name)
            self.assertNotIn("MercyBriefing", (ROOT / name).read_text())
        got = subprocess.run(["git", "diff", "--quiet", COMPOSITION, "--"] + list(candidate.OLD_MANIFESTS), cwd=ROOT)
        if got.returncode not in (0, 1):
            self.skipTest("the composition commit is not in this copy")
        self.assertEqual(got.returncode, 0, "an earlier manifest differs from the composition commit's")

    def test_the_four_earlier_manifests_are_the_same_bytes_on_every_machine(self):
        """Their committed blobs are the pinned bytes, and Git is told to write exactly those bytes out whatever
        the machine's line-end setting. (A fresh Windows checkout is root's to try; this reads what Git holds.)"""
        for name, pinned in self.manifest["earlierManifestsSha256"].items():
            with self.subTest(name):
                blob = subprocess.run(["git", "cat-file", "blob", ":" + name], cwd=ROOT, capture_output=True)
                if blob.returncode != 0:
                    self.skipTest("not a Git working copy")
                self.assertEqual(candidate.hashlib.sha256(blob.stdout).hexdigest().upper(), pinned, "the committed bytes are not the pinned bytes")
                self.assertNotIn(b"\r", blob.stdout, "the committed file holds a carriage return")
                attr = subprocess.run(["git", "check-attr", "text", "eol", "--", name], cwd=ROOT, capture_output=True, text=True).stdout
                self.assertIn(name + ": text: set", attr)
                self.assertIn(name + ": eol: lf", attr)
        rules = [l for l in (ROOT / ".gitattributes").read_text().splitlines() if l.endswith("-artifact.json text eol=lf")]
        self.assertEqual(sorted(l.split()[0] for l in rules), sorted(candidate.OLD_MANIFESTS))

    def bundle(self, scripts):
        """A folder laid out like a built bundle, with stand-in bytes for the compiled scripts."""
        root = Path(tempfile.mkdtemp(prefix="tlm-bundle-"))
        (root / "Scripts" / "TLM").mkdir(parents=True)
        (root / "TheLastMeridian.esp").write_bytes(b"not a plugin")
        for name, data in scripts.items():
            (root / "Scripts" / "TLM" / name).write_bytes(data)
        return root

    def reviewed_like(self):
        """Stand-in files that hash to made-up 'reviewed' digests, and a manifest copy that pins those, so that a
        selection can be tried without any real compiled script (none is in the repository)."""
        chosen = self.manifest["runtimeSelection"]
        files = {name: ("reviewed " + name).encode() for name in chosen["reusedReviewedPex"]}
        pins = dict(self.manifest)
        pins["runtimeSelection"] = dict(chosen, reusedReviewedPex={n: candidate.hashlib.sha256(d).hexdigest().upper() for n, d in files.items()})
        path = Path(tempfile.mkdtemp(prefix="tlm-pins-")) / "candidate.json"
        path.write_text(json.dumps(pins))
        fresh = {name: ("fresh " + name).encode() for name in list(files) + chosen["freshlyCompiled"]}
        return files, fresh, path

    def test_measuring_reads_a_bundle_and_changes_nothing(self):
        before = candidate.MANIFEST.read_bytes()
        got = candidate.measure(self.bundle({"B.pex": b"B.pex", "A.pex": b"A.pex"}))
        self.assertEqual((got["runtimeCount"], sorted(got["runtime"]), got["worldSha256"]), (2, ["A.pex", "B.pex"], None))
        self.assertEqual(len(got["masterSha256"]), 64)
        self.assertFalse(got["selection"]["ok"])
        self.assertEqual((got["selection"]["unexpected"], len(got["selection"]["missing"])), (["A.pex", "B.pex"], 20))
        self.assertEqual(candidate.MANIFEST.read_bytes(), before)

    def test_a_bundle_of_eighteen_reviewed_and_two_fresh_is_the_selection(self):
        reviewed, fresh, pins = self.reviewed_like()
        compile_folder = self.bundle({})
        for name, data in fresh.items():
            (compile_folder / name).write_bytes(data)
        good = dict(reviewed, **{"Act1Walk.pex": fresh["Act1Walk.pex"], "MercyBriefing.pex": fresh["MercyBriefing.pex"]})
        got = candidate.measure(self.bundle(good), compile_folder, pins)
        self.assertTrue(candidate.measured_as_required(got))
        self.assertEqual((len(got["selection"]["reusedAsReviewed"]), sorted(got["selection"]["freshlyCompiled"]), got["runtimeCount"]),
                         (18, ["Act1Walk.pex", "MercyBriefing.pex"], 20))
        self.assertEqual((got["freshCompile"]["count"], got["freshCompile"]["allTwenty"], got["freshCompile"]["theBundlesTwoAreFromIt"]), (20, True, True))
        # The compiler did not reproduce any of the 18 here; that is observed, and changes nothing.
        self.assertEqual(got["freshCompile"]["ofTheEighteenByteIdenticalToTheReviewed"], [])

    def test_what_is_not_the_selection(self):
        reviewed, fresh, pins = self.reviewed_like()
        two = {"Act1Walk.pex": fresh["Act1Walk.pex"], "MercyBriefing.pex": fresh["MercyBriefing.pex"]}
        good = dict(reviewed, **two)
        compile_folder = self.bundle({})
        for name, data in fresh.items():
            (compile_folder / name).write_bytes(data)

        def measured(scripts, compiled=compile_folder):
            return candidate.measure(self.bundle(scripts), compiled, pins)

        # All 20 taken from the fresh compile: what the first recipe said, and what the contract forbids.
        got = measured(dict(fresh))
        self.assertFalse(candidate.measured_as_required(got))
        self.assertEqual(len(got["selection"]["notTheReviewedBytes"]), 18)
        # One freshly compiled script in a reviewed one's place.
        got = measured(dict(good, **{"Core.pex": fresh["Core.pex"]}))
        self.assertEqual((got["selection"]["notTheReviewedBytes"], got["selection"]["ok"]), (["Core.pex"], False))
        # One missing; one too many; a fresh one missing.
        self.assertEqual(measured({n: d for n, d in good.items() if n != "SelfTest.pex"})["selection"]["missing"], ["SelfTest.pex"])
        self.assertEqual(measured(dict(good, **{"Extra.pex": b"x"}))["selection"]["unexpected"], ["Extra.pex"])
        got = measured({n: d for n, d in good.items() if n != "MercyBriefing.pex"})
        self.assertEqual((got["selection"]["missing"], got["selection"]["ok"]), (["MercyBriefing.pex"], False))
        # The bundle's Act1Walk is not the one the full compile produced.
        got = measured(dict(good, **{"Act1Walk.pex": b"from somewhere else"}))
        self.assertTrue(got["selection"]["ok"])
        self.assertFalse(got["freshCompile"]["theBundlesTwoAreFromIt"])
        self.assertFalse(candidate.measured_as_required(got))
        # The full compile did not produce all 20: no proof that the source compiles.
        short = self.bundle({})
        for name, data in fresh.items():
            if name != "MQ01Quest.pex":
                (short / name).write_bytes(data)
        got = measured(good, short)
        self.assertEqual((got["freshCompile"]["count"], got["freshCompile"]["allTwenty"]), (19, False))
        self.assertFalse(candidate.measured_as_required(got))
        # Where the compiler does reproduce a reviewed file, that is recorded, and the reviewed file is still what is bundled.
        same = self.bundle({})
        for name, data in fresh.items():
            (same / name).write_bytes(reviewed[name] if name == "Core.pex" else data)
        got = measured(good, same)
        self.assertEqual(got["freshCompile"]["ofTheEighteenByteIdenticalToTheReviewed"], ["Core.pex"])
        self.assertTrue(candidate.measured_as_required(got))


class WhatTheCheckCatches(unittest.TestCase):
    def damaged(self, change):
        root = copy_of_the_tree()
        if root is None:
            self.skipTest("the a8 commit is not in this copy")
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
        # Whichever line ends this working copy has (a Windows checkout writes the scripts with CRLF), the other kind.
        def other(root, to):
            path = root / "scripts/Source/User/TLM/MercyBriefing.psc"
            path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", to))
        self.assertEqual(self.damaged(lambda r: other(r, b"\r\n")), "")
        self.assertEqual(self.damaged(lambda r: other(r, b"\n")), "")

    def test_an_earlier_id_renumbered_or_a_new_one_moved(self):
        self.assertIn("idFile", self.damaged(lambda r: self.edit(r, "tools/PluginBuilder/formkeys.txt", "TLM_G_CaravanOutcome\n2049", "TLM_G_CaravanOutcome\n2999")))
        self.assertIn("idFile", self.damaged(lambda r: self.edit(r, "tools/PluginBuilder/formkeys.txt", "TLM_MercyBriefing\n2207", "TLM_MercyBriefing\n2300")))

    def test_the_spec_or_the_document_changed(self):
        self.assertIn("builderSourceTextSha256", self.damaged(lambda r: self.edit(r, "tools/PluginBuilder/SpecMercyBriefing.cs", "Not now.", "Later.")))
        self.assertIn("document", self.damaged(lambda r: self.edit(r, "assets/incoming/act1/story/documents.json", "MERCY ROAD CASE: SPRING 2298", "MERCY ROAD CASE: SPRING 2299")))

    def test_an_earlier_manifest_changed_or_made_to_describe_the_candidate(self):
        said = self.damaged(lambda r: self.edit(r, "tools/win/world-details-artifact.json", '"schema": 1', '"schema": 2'))
        self.assertIn("world-details-artifact.json is not the pinned file", said)
        self.assertNotIn("line ends", said)

        def under_the_old_pins(root):
            path = root / "tools/win/world-details-artifact.json"
            data = json.loads(path.read_text())
            data["sourceTextSha256"]["MercyBriefing.psc"] = "0" * 64
            path.write_text(json.dumps(data, indent=2))
        self.assertIn("must not be put under an earlier manifest", self.damaged(under_the_old_pins))

    def test_an_earlier_manifest_with_other_line_ends_is_still_not_the_pinned_file(self):
        def crlf(root):
            path = root / "tools/win/world-natural-artifact.json"
            path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        said = self.damaged(crlf)
        self.assertIn("world-natural-artifact.json is not the pinned bytes", said)
        self.assertIn("other line ends", said)
        # An edit is never called a matter of line ends, with or without them.
        def edited(root):
            path = root / "tools/win/world-natural-artifact.json"
            path.write_bytes(path.read_bytes().replace(b'"schema": 1', b'"schema": 3').replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        said = self.damaged(edited)
        self.assertIn("world-natural-artifact.json is not the pinned file", said)
        self.assertNotIn("other line ends", said)

    def test_the_selection_changed(self):
        def moved(root):
            path = root / "tools/win/mercy-briefing-candidate.json"
            data = json.loads(path.read_text())
            chosen = data["runtimeSelection"]
            chosen["reusedReviewedPex"]["Act1Walk.pex"] = json.loads((root / "tools/win/world-details-artifact.json").read_text())["runtime"]["Act1Walk.pex"]
            chosen["freshlyCompiled"] = ["MercyBriefing.pex"]
            path.write_text(json.dumps(data, indent=2))
        self.assertIn("runtimeSelection", self.damaged(moved))

        def all_fresh(root):
            path = root / "tools/win/mercy-briefing-candidate.json"
            data = json.loads(path.read_text())
            data["runtimeSelection"]["freshlyCompiled"] = sorted(list(data["runtimeSelection"]["reusedReviewedPex"]) + data["runtimeSelection"]["freshlyCompiled"])
            data["runtimeSelection"]["reusedReviewedPex"] = {}
            path.write_text(json.dumps(data, indent=2))
        self.assertIn("is not 18 reviewed compiled scripts and the 2 fresh ones", self.damaged(all_fresh))

        def another_digest(root):
            path = root / "tools/win/mercy-briefing-candidate.json"
            data = json.loads(path.read_text())
            data["runtimeSelection"]["reusedReviewedPex"]["Core.pex"] = "0" * 64
            path.write_text(json.dumps(data, indent=2))
        self.assertIn("runtimeSelection is not what this source and the earlier runtime's pins give", self.damaged(another_digest))

        # A reviewed script whose source is no longer the reviewed text may not be reused.
        said = self.damaged(lambda r: (r / "scripts/Source/User/TLM/Core.psc").write_text((r / "scripts/Source/User/TLM/Core.psc").read_text() + "\n; x\n"))
        self.assertIn("runtimeSelection", said)

    def test_a_built_digest_nobody_measured(self):
        def invented(root):
            path = root / "tools/win/mercy-briefing-candidate.json"
            data = json.loads(path.read_text())
            data["measured"]["masterSha256"] = "A" * 64
            path.write_text(json.dumps(data, indent=2))
        self.assertIn("without who measured it", self.damaged(invented))


if __name__ == "__main__":
    unittest.main()
