"""The Greenwater story candidate's source manifest (GREENWATER-STORY-001):
tools/win/greenwater-story-candidate.json, read by tools/greenwater_story_candidate.py.

That the checkout is the source the manifest describes: 23 scripts, seventeen
of them still the text the Details package pins; against the a8 source two
changed and three added; the id file's earlier 338 lines untouched and 162
ids appended; the four earlier package manifests unchanged byte for byte, the
a8 manifest, its check and the earlier packagers and launcher unchanged as
text, and none of them saying anything of this candidate; which compiled
scripts a bundle takes from where (17 reviewed ones of the Details runtime, 6
fresh: every changed script, every new one, and MercyBriefing), kept apart
from the proof that all 23 compile; the records as the stand-in build reads
them back; and no digest of anything compiled or built for this candidate
recorded that nobody measured. And that the check notices each of those going
wrong.

About tools/win/Build-Greenwater.ps1 this file can say only what its text
says: no PowerShell is here, so that script has never been run or parsed.

Source provenance only. Not a compile and not a game test.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_sim import ROOT

sys.path.insert(0, str(ROOT / "tools"))
import greenwater_story_candidate as candidate                    # noqa: E402

CONTRACT = "637cbeda836c55b7c93bb45583b1ea2914f2d46d"
A8 = "a8f6d6482b4b5dc9d545e197ed4cf2c8f6324306"
MANIFEST_NAME = "tools/win/greenwater-story-candidate.json"
PACKAGER = ROOT / "tools" / "win" / "Build-Greenwater.ps1"
FRESH = ["Act1Guide.pex", "Act1Walk.pex", "GreenwaterTalk.pex", "GreenwaterWalk.pex", "MQ02BQuest.pex", "MercyBriefing.pex"]


def copy_of_the_tree():
    """Just what the check reads, as it is in this working copy."""
    root = Path(tempfile.mkdtemp(prefix="tlm-gw-candidate-"))
    names = ("scripts/Source/User/TLM",) + candidate.BUILDER_SOURCES + candidate.OLD_MANIFESTS + candidate.FROZEN + (
        MANIFEST_NAME, "assets/incoming/act1/story/documents.json")
    for name in dict.fromkeys(names):
        source, target = ROOT / name, root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target, ignore=lambda folder, items: [i for i in items if not i.endswith(".psc")])
        else:
            shutil.copyfile(source, target)
    return root


def in_git(commit):
    return subprocess.run(["git", "cat-file", "-e", commit + "^{commit}"], cwd=ROOT, capture_output=True).returncode == 0


class TheCandidate(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(candidate.MANIFEST.read_text())
        self.details = json.loads(candidate.DETAILS.read_text())
        self.a8 = json.loads((ROOT / candidate.A8_MANIFEST).read_text())

    def test_the_checkout_is_the_source_the_manifest_describes(self):
        self.assertEqual(candidate.problems(), [])

    def test_it_is_twenty_three_scripts_and_what_changed(self):
        m = self.manifest
        self.assertEqual((m["scripts"], len(m["sourceTextSha256"])), (23, 23))
        d, a = m["againstTheDetailsPins"], m["againstA8"]
        self.assertEqual((len(d["unchanged"]), d["changed"]), (17, ["Act1Guide.psc", "Act1Walk.psc"]))
        self.assertEqual(d["added"], ["GreenwaterTalk.psc", "GreenwaterWalk.psc", "MQ02BQuest.psc", "MercyBriefing.psc"])
        self.assertEqual((len(a["unchanged"]), a["changed"], a["added"]),
                         (18, ["Act1Guide.psc", "Act1Walk.psc"], ["GreenwaterTalk.psc", "GreenwaterWalk.psc", "MQ02BQuest.psc"]))
        self.assertEqual(len(self.details["sourceTextSha256"]), 19)
        self.assertEqual(len(self.a8["sourceTextSha256"]), 20)
        for name in d["unchanged"]:
            self.assertEqual(m["sourceTextSha256"][name], self.details["sourceTextSha256"][name], name)
        self.assertEqual(m["sourceTextSha256"]["MercyBriefing.psc"], self.a8["sourceTextSha256"]["MercyBriefing.psc"])
        # The two quests whose rules this road must not touch, the opening's talk, and the normal start.
        for untouched in ("MQ01Quest.psc", "SQ01Quest.psc", "Act1Talk.psc", "Core.psc", "SelfTest.psc", "MatrixCases.psc",
                          "CaseDriver.psc", "WorldEntry.psc", "WorldEntryPlayer.psc"):
            self.assertIn(untouched, d["unchanged"])

    def test_the_earlier_ids_are_untouched_and_the_new_ones_follow(self):
        ids = self.manifest["idFile"]
        self.assertEqual((ids["earlierLines"], len(ids["appended"])), (338, 162))
        self.assertEqual(sorted(ids["appended"].values()), list(range(2217, 2379)))
        self.assertEqual(len(set(ids["appended"].values())), 162)
        got = subprocess.run(["git", "show", A8 + ":tools/PluginBuilder/formkeys.txt"], cwd=ROOT, capture_output=True)
        if got.returncode != 0:
            self.skipTest("the a8 commit is not in this copy; the recorded digest of the earlier lines was still checked")
        before = got.stdout.decode("utf-8").replace("\r\n", "\n")
        now = (ROOT / "tools/PluginBuilder/formkeys.txt").read_text().replace("\r\n", "\n")
        self.assertEqual(len(before.splitlines()), 338)
        self.assertTrue(now.startswith(before), "the id file no longer begins with the id file it grew from")
        # And every earlier id is one of a8's own: none was given a second time.
        old = before.split("\n")
        earlier = {int(old[i + 1]) for i in range(0, len(old) - 1, 2) if old[i]}
        self.assertEqual(earlier & set(ids["appended"].values()), set())
        self.assertEqual({old[i] for i in range(0, len(old) - 1, 2)} & set(ids["appended"]), set())

    def test_nothing_built_or_compiled_is_claimed(self):
        measured = self.manifest["measured"]
        for key in ("masterSha256", "worldSha256", "runtime", "runtimeManifestSha256", "freshCompile", "measuredBy", "measuredFrom"):
            self.assertIsNone(measured[key], key)
        self.assertIn("SOURCE CANDIDATE ONLY", self.manifest["status"])
        text = candidate.MANIFEST.read_text()
        old = self.details
        # The earlier package's plugin and exterior, and its compiled Act1Walk and Act1Guide, are not this candidate's.
        for pinned in (old["masterSha256"], old["worldSha256"], old["runtime"]["Act1Walk.pex"], old["runtime"]["Act1Guide.pex"]):
            self.assertNotIn(pinned, text, "a digest of the 19-script package's own plugin, exterior, Act1Walk or Act1Guide is in the candidate's manifest")
        self.assertEqual(text.count(old["runtimeManifestSha256"]), 1)
        for name, pinned in old["runtime"].items():
            self.assertEqual(text.count(pinned), 0 if name in ("Act1Walk.pex", "Act1Guide.pex") else 1, name)
        # The only 64-digit digests under a compiled script's name are the 17 reviewed inputs.
        self.assertEqual(len(re.findall(r'"\w+\.pex": "[0-9A-F]{64}"', text)), 17)

    def test_which_compiled_scripts_go_into_the_bundle(self):
        chosen, old = self.manifest["runtimeSelection"], self.details
        reused, fresh = chosen["reusedReviewedPex"], chosen["freshlyCompiled"]
        self.assertEqual((len(reused), fresh), (17, FRESH))
        self.assertEqual(set(reused) & set(fresh), set())
        self.assertEqual(sorted(list(reused) + fresh), sorted(n[:-4] + ".pex" for n in self.manifest["sourceTextSha256"]))
        for name, digest in reused.items():
            self.assertEqual(digest, old["runtime"][name], name)
            source = name[:-4] + ".psc"
            self.assertEqual(self.manifest["sourceTextSha256"][source], old["sourceTextSha256"][source], source)
        # Every script changed or new since a8 is fresh; so is MercyBriefing, for which no reviewed file is recorded.
        since = self.manifest["againstA8"]
        for source in since["changed"] + since["added"]:
            self.assertIn(source[:-4] + ".pex", fresh)
            self.assertNotIn(source[:-4] + ".pex", reused)
        self.assertEqual(list(self.manifest["freshThoughUnchangedSinceA8"]), ["MercyBriefing.pex"])
        self.assertNotIn("MercyBriefing.pex", old["runtime"])
        self.assertIsNone(self.a8["measured"]["runtime"], "a8 has a measured runtime now: MercyBriefing's selection is to be looked at again")
        for word in ("17", "reviewed", "byte for byte", "fresh compile", "not bundled", "assumed", "MercyBriefing"):
            self.assertIn(word, chosen["policy"])
        steps = " ".join(self.manifest["recipe"]["steps"])
        self.assertIn("COMPILE PROOF: compile all 23", steps)
        self.assertIn("Never the freshly compiled 17", steps)
        self.assertIn("--fresh-compile", steps)

    def test_the_earlier_manifests_and_verifiers_are_as_they_were_and_say_nothing_of_it(self):
        for name, digest in self.manifest["earlierManifestsSha256"].items():
            self.assertEqual(candidate.file_digest(ROOT / name), digest, name)
            self.assertEqual(digest, self.a8["earlierManifestsSha256"][name], name + " is not the file the a8 manifest pinned")
        for name in candidate.OLD_MANIFESTS + (candidate.A8_MANIFEST,):
            text = (ROOT / name).read_text()
            for word in candidate.OWN_WORDS:
                self.assertNotIn(word, text, name)
        if not in_git(CONTRACT):
            self.skipTest("the contract commit is not in this copy; the pinned digests were still checked")
        frozen = list(candidate.OLD_MANIFESTS + candidate.FROZEN) + [
            "tools/win/Play-WorldDetails.cmd", "tools/win/Play-WorldNatural.cmd", "tools/win/Play-WorldStory.cmd", "tools/win/Play-WorldExpanded.cmd",
            "tools/win/tests", "tools/test_world_story_launcher.py", ".gitattributes", ".github"]
        got = subprocess.run(["git", "diff", "--quiet", CONTRACT, "--"] + frozen, cwd=ROOT)
        self.assertEqual(got.returncode, 0, "a frozen manifest, verifier, packager, launcher or workflow differs from the contract commit's")

    def test_the_records_are_the_ones_the_stand_in_build_reads_back(self):
        built_file = ROOT / "build" / "sim" / "TheLastMeridian.json"
        if not built_file.exists():
            self.skipTest("no stand-in build here (tools/run_checks.sh makes one)")
        built = {q["EditorId"]: q for q in json.loads(built_file.read_text())["Quests"]}
        self.assertEqual(sorted(built), sorted(["TLM_Core", "TLM_MQ01", "TLM_SQ01", "TLM_Trial", "TLM_A1", "TLM_MercyBriefing", "TLM_MQ02B", "TLM_GW"]))
        for name, said in self.manifest["records"]["quests"].items():
            q = built[name]
            self.assertEqual(said["scripts"], [s["Name"] for s in q["Scripts"]], name)
            self.assertEqual(said["stages"], [s["Index"] for s in q["Stages"]], name)
            self.assertEqual(said["completes"], [s["Index"] for s in q["Stages"] if s["CompleteQuest"]], name)
            self.assertEqual(said["objectives"], {str(o["Index"]): o["Text"] for o in q["Objectives"]}, name)
            self.assertEqual(said["aliases"], {str(a["Id"]): a["Name"] for a in q["Aliases"]}, name)
            self.assertEqual(said["properties"], {s["Name"]: len(s["Props"]) for s in q["Scripts"]}, name)
            self.assertEqual((said["type"], said["priority"], said["name"]), (q["Type"], q["Priority"], q["Name"]), name)
        road, stage = self.manifest["records"]["quests"]["TLM_MQ02B"], self.manifest["records"]["quests"]["TLM_GW"]
        self.assertEqual(road["stages"], [10, 20, 30, 40, 41, 42, 43, 44, 45, 46, 50, 60, 61, 100])
        self.assertEqual((road["completes"], len(road["aliases"]), road["aliasesWithAScript"]), ([100], 11, 0))
        self.assertEqual((len(stage["aliases"]), stage["aliasesWithAScript"], stage["aliasScripts"], stage["stages"]), (31, 27, ["TLM:GreenwaterTalk"], []))
        records = self.manifest["records"]
        self.assertEqual((len(records["globals"]), len(records["factions"]), len(records["actors"]), records["book"], len(records["placedReferences"]),
                          len(records["activators"]), len(records["triggers"]), records["messages"]),
                         (12, 2, 6, ["TLM_BOOK_LetterOfHire"], 31, 17, 4, 87))
        # Every appended id is accounted for by one of those kinds, or is one of the two quests.
        named = set(records["globals"] + records["factions"] + records["actors"] + records["book"] + records["placedReferences"]
                    + records["activators"] + records["triggers"]) | {"TLM_MQ02B", "TLM_GW"}
        rest = [n for n in self.manifest["idFile"]["appended"] if n not in named]
        self.assertEqual(len(rest), 87)
        self.assertTrue(all(n.startswith("TLM_MSG_GW_") for n in rest))

    def test_the_normal_start_is_untouched_and_no_qa_helper_is_in_the_source(self):
        # The scenario is TLM:Core's, read from TLM_G_DevScenario, which is 0 in every build. Core is the reviewed
        # text, and the road's spec and scripts never name that global.
        self.assertIn("Core.psc", self.manifest["againstTheDetailsPins"]["unchanged"])
        self.assertNotIn("DevScenario", (ROOT / "tools/PluginBuilder/SpecGreenwater.cs").read_text())
        new = "".join((ROOT / "scripts/Source/User/TLM" / n).read_text() for n in ("MQ02BQuest.psc", "GreenwaterWalk.psc", "GreenwaterTalk.psc"))
        for word in ("SetValue(Charisma", "ModValue", "SetAV", "ModAV", "ForceAV", "DevScenario", "Scenario", "ConsoleUtil", "CenterOnCell", "Debug.MessageBox"):
            self.assertNotIn(word, new, word + " is in the road's scripts")

    def bundle(self, scripts):
        root = Path(tempfile.mkdtemp(prefix="tlm-gw-bundle-"))
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
        path = Path(tempfile.mkdtemp(prefix="tlm-gw-pins-")) / "candidate.json"
        path.write_text(json.dumps(pins))
        fresh = {name: ("fresh " + name).encode() for name in list(files) + chosen["freshlyCompiled"]}
        return files, fresh, path

    def compile_folder(self, fresh, leave_out=None, replace=None):
        folder = self.bundle({})
        for name, data in fresh.items():
            if name != leave_out:
                (folder / name).write_bytes((replace or {}).get(name, data))
        return folder

    def test_measuring_reads_a_bundle_and_changes_nothing(self):
        before = candidate.MANIFEST.read_bytes()
        got = candidate.measure(self.bundle({"B.pex": b"B.pex", "A.pex": b"A.pex"}))
        self.assertEqual((got["runtimeCount"], sorted(got["runtime"]), got["worldSha256"]), (2, ["A.pex", "B.pex"], None))
        self.assertFalse(got["selection"]["ok"])
        self.assertEqual((got["selection"]["unexpected"], len(got["selection"]["missing"])), (["A.pex", "B.pex"], 23))
        self.assertEqual(candidate.MANIFEST.read_bytes(), before)

    def test_a_bundle_of_seventeen_reviewed_and_six_fresh_is_the_selection(self):
        reviewed, fresh, pins = self.reviewed_like()
        good = dict(reviewed, **{n: fresh[n] for n in FRESH})
        got = candidate.measure(self.bundle(good), self.compile_folder(fresh), pins)
        self.assertTrue(candidate.measured_as_required(got))
        self.assertEqual((len(got["selection"]["reusedAsReviewed"]), sorted(got["selection"]["freshlyCompiled"]), got["runtimeCount"]), (17, FRESH, 23))
        self.assertEqual((got["freshCompile"]["count"], got["freshCompile"]["allTwentyThree"], got["freshCompile"]["theBundlesSixAreFromIt"]), (23, True, True))
        self.assertEqual(got["freshCompile"]["ofTheSeventeenByteIdenticalToTheReviewed"], [])

    def test_what_is_not_the_selection(self):
        reviewed, fresh, pins = self.reviewed_like()
        good = dict(reviewed, **{n: fresh[n] for n in FRESH})
        whole = self.compile_folder(fresh)

        def measured(scripts, compiled=whole):
            return candidate.measure(self.bundle(scripts), compiled, pins)

        # All 23 taken from the fresh compile.
        got = measured(dict(fresh))
        self.assertFalse(candidate.measured_as_required(got))
        self.assertEqual(len(got["selection"]["notTheReviewedBytes"]), 17)
        # One freshly compiled script in a reviewed one's place.
        got = measured(dict(good, **{"Core.pex": fresh["Core.pex"]}))
        self.assertEqual((got["selection"]["notTheReviewedBytes"], got["selection"]["ok"]), (["Core.pex"], False))
        # One missing; one too many; each fresh one missing.
        self.assertEqual(measured({n: d for n, d in good.items() if n != "SelfTest.pex"})["selection"]["missing"], ["SelfTest.pex"])
        self.assertEqual(measured(dict(good, **{"Extra.pex": b"x"}))["selection"]["unexpected"], ["Extra.pex"])
        for name in FRESH:
            got = measured({n: d for n, d in good.items() if n != name})
            self.assertEqual((got["selection"]["missing"], got["selection"]["ok"]), ([name], False))
        # A changed or new script that is not the one the full compile produced: an earlier Act1Walk, say.
        for name in FRESH:
            got = measured(dict(good, **{name: b"from somewhere else"}))
            self.assertTrue(got["selection"]["ok"])
            self.assertFalse(got["freshCompile"]["theBundlesSixAreFromIt"], name)
            self.assertFalse(candidate.measured_as_required(got), name)
        # The full compile did not produce all 23: no proof that the source compiles.
        got = measured(good, self.compile_folder(fresh, leave_out="MQ02BQuest.pex"))
        self.assertEqual((got["freshCompile"]["count"], got["freshCompile"]["allTwentyThree"]), (22, False))
        self.assertFalse(candidate.measured_as_required(got))
        # Where the compiler does reproduce a reviewed file, that is recorded, and the reviewed file is still what is bundled.
        got = measured(good, self.compile_folder(fresh, replace={"Core.pex": reviewed["Core.pex"]}))
        self.assertEqual(got["freshCompile"]["ofTheSeventeenByteIdenticalToTheReviewed"], ["Core.pex"])
        self.assertTrue(candidate.measured_as_required(got))


class WhatTheCheckCatches(unittest.TestCase):
    def damaged(self, change):
        root = copy_of_the_tree()
        self.assertEqual(candidate.problems(root, root / MANIFEST_NAME), [], "the copy is sound before it is damaged")
        change(root)
        return " | ".join(candidate.problems(root, root / MANIFEST_NAME))

    def edit(self, root, name, old, new):
        path = root / name
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1))

    def append(self, root, name, more="\n; x\n"):
        path = root / name
        path.write_text(path.read_text() + more)

    def in_manifest(self, change):
        def do(root):
            path = root / MANIFEST_NAME
            data = json.loads(path.read_text())
            change(data, root)
            path.write_text(json.dumps(data, indent=2))
        return self.damaged(do)

    def test_a_script_changed(self):
        self.assertIn("MQ02BQuest.psc is not the source", self.damaged(lambda r: self.edit(r, "scripts/Source/User/TLM/MQ02BQuest.psc", "RV_CARD_THRESHOLD = 5", "RV_CARD_THRESHOLD = 4")))
        self.assertIn("MQ01Quest.psc is not the source", self.damaged(lambda r: self.edit(r, "scripts/Source/User/TLM/MQ01Quest.psc", "TIMER_EVADE = 1", "TIMER_EVADE = 2")))
        self.assertIn("GreenwaterWalk.psc is not the source", self.damaged(lambda r: self.append(r, "scripts/Source/User/TLM/GreenwaterWalk.psc")))

    def test_a_reviewed_script_changed_may_not_keep_its_reviewed_file(self):
        said = self.damaged(lambda r: self.append(r, "scripts/Source/User/TLM/Core.psc"))
        self.assertIn("against the Details pins: changed ['Act1Guide.psc', 'Act1Walk.psc', 'Core.psc']", said)
        self.assertIn("runtimeSelection is not what this source", said)
        self.assertIn("Core.psc is changed or new since a8 and is not taken from the fresh compile", said)

    def test_a_script_more_or_fewer(self):
        self.assertIn("only here ['Extra.psc']", self.damaged(lambda r: (r / "scripts/Source/User/TLM/Extra.psc").write_text("Scriptname TLM:Extra\n")))
        self.assertIn("only in the manifest ['GreenwaterTalk.psc']", self.damaged(lambda r: (r / "scripts/Source/User/TLM/GreenwaterTalk.psc").unlink()))

    def test_line_ends_alone_are_not_a_change(self):
        def other(root, to):
            for name in ("scripts/Source/User/TLM/MQ02BQuest.psc", "tools/win/Build-WorldDetails.ps1", "tools/mercy_briefing_candidate.py", candidate.A8_MANIFEST):
                path = root / name
                path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", to))
        self.assertEqual(self.damaged(lambda r: other(r, b"\r\n")), "")
        self.assertEqual(self.damaged(lambda r: other(r, b"\n")), "")

    def test_an_earlier_id_renumbered_or_a_new_one_moved(self):
        self.assertIn("idFile", self.damaged(lambda r: self.edit(r, "tools/PluginBuilder/formkeys.txt", "TLM_MercyBriefing\n2207", "TLM_MercyBriefing\n2999")))
        self.assertIn("idFile", self.damaged(lambda r: self.edit(r, "tools/PluginBuilder/formkeys.txt", "TLM_MQ02B\n", "TLM_MQ02B\n9")))

    def test_the_spec_the_exterior_builder_or_a_document_changed(self):
        self.assertIn("builderSourceTextSha256", self.damaged(lambda r: self.append(r, "tools/PluginBuilder/SpecGreenwater.cs", "\n// x\n")))
        self.assertIn("builderSourceTextSha256", self.damaged(lambda r: self.append(r, "tools/WorldSliceBuilder/WorldStory.cs", "\n// x\n")))

        def reworded(root):
            path = root / "assets/incoming/act1/story/documents.json"
            data = json.loads(path.read_text())
            for d in data["documents"]:
                if d["id"] == "letter_of_hire":
                    d["text"] += " x"
            path.write_text(json.dumps(data))
        self.assertIn("documents is not as the manifest describes", self.damaged(reworded))

    def test_an_earlier_manifest_changed_or_made_to_describe_the_candidate(self):
        said = self.damaged(lambda r: self.edit(r, "tools/win/world-details-artifact.json", '"schema": 1', '"schema": 2'))
        self.assertIn("world-details-artifact.json is not the pinned file", said)

        def under_the_old_pins(root):
            path = root / "tools/win/world-details-artifact.json"
            data = json.loads(path.read_text())
            data["sourceTextSha256"]["MQ02BQuest.psc"] = "0" * 64
            path.write_text(json.dumps(data, indent=2))
        self.assertIn("must not be put under an earlier manifest", self.damaged(under_the_old_pins))
        said = self.damaged(lambda r: self.edit(r, candidate.A8_MANIFEST, '"scripts": 20', '"scripts": 23, "also": "Greenwater"'))
        self.assertIn("mercy-briefing-candidate.json is not the frozen text", said)
        self.assertIn("mercy-briefing-candidate.json mentions the Greenwater road", said)

    def test_an_earlier_manifest_with_other_line_ends_is_still_not_the_pinned_file(self):
        def crlf(root):
            path = root / "tools/win/world-natural-artifact.json"
            path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        said = self.damaged(crlf)
        self.assertIn("world-natural-artifact.json is not the pinned bytes", said)
        self.assertIn("other line ends", said)

    def test_an_earlier_verifier_or_packager_edited(self):
        for name, old in (("tools/mercy_briefing_candidate.py", "len(reused) != 18"), ("tools/win/Build-WorldDetails.ps1", "-ne 19"),
                          ("tools/win/World-Story.psm1", "Set-StrictMode"), ("tools/win/Stage-WorldDetails.ps1", "Set-StrictMode"),
                          ("tools/win/Build-WorldNatural.ps1", "Set-StrictMode"), ("tools/win/Play-WorldStory.ps1", "Set-StrictMode")):
            with self.subTest(name):
                self.assertIn(name + " is not the frozen text", self.damaged(lambda r: self.edit(r, name, old, old + " ")))

    def test_the_selection_changed(self):
        def old_walk(data, root):
            chosen = data["runtimeSelection"]
            chosen["reusedReviewedPex"]["Act1Walk.pex"] = json.loads((root / "tools/win/world-details-artifact.json").read_text())["runtime"]["Act1Walk.pex"]
            chosen["freshlyCompiled"].remove("Act1Walk.pex")
        said = self.in_manifest(old_walk)
        self.assertIn("runtimeSelection is not what this source", said)
        self.assertIn("Act1Walk.psc is changed or new since a8 and is not taken from the fresh compile", said)

        def old_guide(data, root):
            chosen = data["runtimeSelection"]
            chosen["reusedReviewedPex"]["Act1Guide.pex"] = json.loads((root / "tools/win/world-details-artifact.json").read_text())["runtime"]["Act1Guide.pex"]
            chosen["freshlyCompiled"].remove("Act1Guide.pex")
        self.assertIn("Act1Guide.psc is changed or new since a8 and is not taken from the fresh compile", self.in_manifest(old_guide))

        def invented_briefing(data, root):
            data["runtimeSelection"]["reusedReviewedPex"]["MercyBriefing.pex"] = "A" * 64
            data["runtimeSelection"]["freshlyCompiled"].remove("MercyBriefing.pex")
        self.assertIn("is not 17 reviewed compiled scripts and the 6 fresh ones", self.in_manifest(invented_briefing))

        def all_fresh(data, root):
            chosen = data["runtimeSelection"]
            chosen["freshlyCompiled"] = sorted(list(chosen["reusedReviewedPex"]) + chosen["freshlyCompiled"])
            chosen["reusedReviewedPex"] = {}
        self.assertIn("is not 17 reviewed compiled scripts and the 6 fresh ones", self.in_manifest(all_fresh))

        def another_digest(data, root):
            data["runtimeSelection"]["reusedReviewedPex"]["Core.pex"] = "0" * 64
        self.assertIn("runtimeSelection is not what this source and the earlier runtime's pins give", self.in_manifest(another_digest))

    def test_a_built_digest_nobody_measured(self):
        def invented(data, root):
            data["measured"]["masterSha256"] = "A" * 64
        self.assertIn("without who measured it", self.in_manifest(invented))

        def invented_runtime(data, root):
            data["measured"]["runtime"] = {"MQ02BQuest.pex": "B" * 64}
        self.assertIn("without who measured it", self.in_manifest(invented_runtime))


class ThePackagersText(unittest.TestCase):
    """tools/win/Build-Greenwater.ps1, read as text. It has never been run or parsed: no PowerShell is here."""

    def setUp(self):
        self.text = PACKAGER.read_text()
        self.code = "\n".join(l for l in self.text.split("#>", 1)[1].splitlines() if not l.strip().startswith("#"))

    def test_it_says_it_is_untested(self):
        self.assertIn("UNTESTED SCAFFOLDING", self.text)
        self.assertIn("has not been run, not even parsed", self.text)

    def test_its_output_guard_is_the_details_packagers_line_for_line(self):
        details = (ROOT / "tools/win/Build-WorldDetails.ps1").read_text()
        start, end = "$repo=[IO.Path]::GetFullPath(", "foreach ($file in @($VanillaMaster))"
        guard = details[details.index(start):details.index(end)]
        self.assertGreater(len(guard.splitlines()), 20)
        self.assertIn(guard, self.text)
        # And nothing is created before the guard and the checks of the inputs and of the source have passed.
        first_write = min(self.code.index(w) for w in ("New-Item", "Copy-Item", "WriteAllText", "dotnet run"))
        for check in ("reparse point", "Current source differs", "Reviewed runtime input pin mismatch", "The fresh compile must hold exactly"):
            self.assertLess(self.code.index(check), first_write, check)

    def test_it_reads_its_own_manifest_and_takes_no_earlier_pin_for_its_output(self):
        self.assertIn("greenwater-story-candidate.json", self.code)
        for pin in ("masterSha256", "worldSha256"):
            self.assertNotIn("$pins." + pin, self.code)
            self.assertNotIn("$details." + pin, self.code)
        # The Details manifest is read for two things only: the 17 reviewed files' digests and their sources' text.
        self.assertEqual(sorted(set(re.findall(r"\$details\.(\w+)", self.code))), ["runtime", "sourceTextSha256"])
        self.assertNotIn("verified-manifest", self.code)
        self.assertIn("MEASURED, NOT VERIFIED", self.code)
        self.assertNotIn("world-natural-artifact", self.code)
        self.assertNotIn("world-story-artifact", self.code)

    def test_it_installs_nothing_and_compiles_nothing(self):
        for word in ("PapyrusCompiler", "Install-Dev", "Stage-WorldDetails", "World-Story.psm1", "Start-Process", "Remove-Item", "Move-Item",
                     "Fallout4.exe", "f4se", "ModOrganizer", "Invoke-WebRequest", "Invoke-Expression", "Set-Content"):
            self.assertNotIn(word.lower(), self.code.lower(), word)
        # Everything it writes is under the output folder it has checked.
        for line in self.code.splitlines():
            if "Copy-Item" in line:
                self.assertRegex(line, r"-Destination (\$bundle|\$packaged|\(Join-Path \$output )", line)
        self.assertEqual(self.code.count("WriteAllText"), 1)
        self.assertIn("WriteAllText((Join-Path $output 'measured.json')", self.code)

    def test_it_counts_what_the_manifest_counts(self):
        self.assertIn("$sourcePins.Count -ne 23 -or $reviewed.Count -ne 17 -or $fresh.Count -ne 6", self.code)
        self.assertIn("--natural --private-shelter-detail", self.code)
        # Its braces and brackets at least pair up.
        for open_, close in ("{}", "()", "[]"):
            self.assertEqual(self.code.count(open_), self.code.count(close), open_ + close)


if __name__ == "__main__":
    unittest.main()
