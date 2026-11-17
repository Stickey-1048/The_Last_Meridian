#!/usr/bin/env python3
"""The Night Mail story candidate (NIGHT-MAIL-STORY-001): its source manifest.

tools/win/night-mail-story-candidate.json says which source this candidate is:
the 26 script sources by digest, the builder's spec files, the id file, the
three documents' text. It is a manifest of SOURCE. It holds no digest of a
compiled script or of a built plugin until somebody has built one against the
game's own master and measured it; nothing here invents one.

This candidate is the Greenwater candidate (tools/win/greenwater-story-candidate.json,
commit 016b2b4, accepted for source, compilation and artifact gates; actual game
acceptance pending) composed with the Night Mail road. The Greenwater manifest,
its check, its packager and its fixture are unchanged and are pinned here as
text, so that an edit of any of them is seen. Nothing of an earlier package
describes this one: the Details, Natural and story manifests, the a8 manifest
and the Greenwater manifest all refuse this checkout, as they should.

WHICH COMPILED SCRIPTS GO INTO THE BUNDLE. Two things, kept apart:
  - proof that the source compiles: all 26 scripts compiled afresh, the log
    and the results kept;
  - the runtime selected for the bundle: the 17 scripts whose source is still
    the text the Details package pins are taken as the REVIEWED compiled files
    of that runtime, each only after its source text and its bytes have been
    checked against those pins; the other 9 are taken from the fresh compile:
    every script changed since that runtime (Act1Walk, Act1Guide), every one
    added since (MQ02AQuest, NightMailWalk and NightMailTalk of this road;
    MQ02BQuest, GreenwaterWalk and GreenwaterTalk of the Greenwater road;
    MercyBriefing).
Four of the nine have source unchanged since the Greenwater candidate and were
never compiled by anybody whose digest this repository records
(GreenwaterTalk, GreenwaterWalk, MQ02BQuest, MercyBriefing): they are compiled
afresh all the same and nothing is taken from an earlier candidate's pins.
The freshly compiled 17 are never put into the bundle in place of the reviewed
ones, and nothing here assumes that the compiler reproduces the old bytes.

    python3 tools/night_mail_story_candidate.py verify
        The checkout is the source the manifest describes. Exit 1 if not.

    python3 tools/night_mail_story_candidate.py describe
        Prints what the manifest would hold for the checkout as it is now
        (for whoever changes the candidate on purpose and reviews the diff).

    python3 tools/night_mail_story_candidate.py measure <bundle folder> [--fresh-compile <folder>]
        Prints, as JSON for a build receipt, the SHA-256 of TheLastMeridian.esp,
        TLMWorldSlice.esp and every Scripts/TLM/*.pex in a built bundle, and
        says of each compiled script whether it is the reviewed file it has to
        be or one of the nine fresh ones. With --fresh-compile, also the digests
        of the full compile, whether it holds all 26, and whether the bundle's
        nine fresh scripts are that compile's. Exit 1 if the selection is not
        the one above. It writes nothing and changes no pin.

Needs Python 3 only. Not a compile and not a game test.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tools" / "win" / "night-mail-story-candidate.json"
DETAILS = ROOT / "tools" / "win" / "world-details-artifact.json"
A8_MANIFEST = "tools/win/mercy-briefing-candidate.json"
GREENWATER_MANIFEST = "tools/win/greenwater-story-candidate.json"
# Pinned byte for byte; .gitattributes makes a checkout write these four with LF on every machine.
OLD_MANIFESTS = ("tools/win/world-details-artifact.json", "tools/win/world-natural-artifact.json",
                 "tools/win/world-story-artifact.json", "tools/WorldSliceBuilder/expanded-artifact.json")
# The earlier packages' own manifest, checks, packagers and launcher, pinned as text (line ends made LF, as a source
# is read), so that a Windows checkout's line ends are not taken for an edit and an edit is not missed.
FROZEN = (A8_MANIFEST, "tools/mercy_briefing_candidate.py", "tools/win/World-Story.psm1", "tools/win/Play-WorldStory.ps1",
          "tools/win/Build-WorldDetails.ps1", "tools/win/Build-WorldNatural.ps1", "tools/win/Stage-WorldDetails.ps1",
          # The Greenwater candidate as accepted (016b2b4): its manifest, its check, its packager.
          GREENWATER_MANIFEST, "tools/greenwater_story_candidate.py", "tools/win/Build-Greenwater.ps1")
BUILDER_SOURCES = ("tools/PluginBuilder/Spec.cs", "tools/PluginBuilder/SpecAct1.cs", "tools/PluginBuilder/SpecMercyBriefing.cs",
                   "tools/PluginBuilder/SpecGreenwater.cs", "tools/PluginBuilder/SpecNightMail.cs", "tools/PluginBuilder/SpecGuide.cs",
                   "tools/PluginBuilder/SpecOrientation.cs", "tools/PluginBuilder/Builder.cs", "tools/PluginBuilder/formkeys.txt",
                   "tools/WorldSliceBuilder/WorldStory.cs", "tools/WorldSliceBuilder/Program.cs")
# The id file as it was at 016b, before this candidate: its first 670 lines (the earlier 338 of a8's and the
# Greenwater candidate's 332).
OLD_ID_LINES = 670
DOCUMENTS = ("yard_rules", "hymn_chalk", "hymnal_flyleaf")
SCRIPTS, REVIEWED, FRESH = 26, 17, 9
FRESH_NAMES = ["Act1Guide.pex", "Act1Walk.pex", "GreenwaterTalk.pex", "GreenwaterWalk.pex", "MQ02AQuest.pex", "MQ02BQuest.pex",
               "MercyBriefing.pex", "NightMailTalk.pex", "NightMailWalk.pex"]
# No earlier manifest may speak of this candidate.
OWN_WORDS = ("Night Mail", "NightMail", "MQ02A", "night-mail-story")


def text_digest(path: Path) -> str:
    """As the Details packager reads a source: UTF-8 text with every line end made LF."""
    text = path.read_bytes().decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def pex(script_name: str) -> str:
    return script_name[:-len(".psc")] + ".pex"


def selection(root: Path, sources: dict) -> dict:
    """Which compiled scripts the bundle takes from where: by this checkout's
    sources against the earlier runtime's pins."""
    details = json.loads((root / "tools" / "win" / "world-details-artifact.json").read_text())
    old_source, old_pex = details["sourceTextSha256"], details["runtime"]
    unchanged = sorted(n for n in old_source if sources.get(n) == old_source[n])
    return {
        "policy": "The 17 scripts whose source text is still the text the Details package pins are bundled as the reviewed "
                  "compiled files of that runtime, byte for byte, after their source and their bytes have been checked "
                  "against its pins. The other 9 are bundled from the fresh compile: every changed script, every new one, "
                  "and MercyBriefing, whose source is unchanged since a8 but of which no measured compiled digest is "
                  "recorded. The four of them whose source is unchanged since the Greenwater candidate (GreenwaterTalk, "
                  "GreenwaterWalk, MQ02BQuest, MercyBriefing) are taken from the fresh compile too: no digest of a "
                  "compiled one is recorded, and no pin of the Greenwater candidate is a pin of this one. "
                  "A full fresh compile of all 26 is the proof that the source compiles and is kept with its "
                  "log; its 17 are not bundled, and no compiler output is assumed to equal an earlier one.",
        "reusedFrom": {"manifest": "tools/win/world-details-artifact.json",
                       "runtimeManifestSha256": details["runtimeManifestSha256"]},
        "reusedReviewedPex": {pex(n): old_pex[pex(n)] for n in unchanged},
        "freshlyCompiled": sorted(pex(n) for n in sources if n not in unchanged),
    }


def describe(root: Path = ROOT) -> dict:
    """What the manifest's measured-from-source part should hold for this checkout."""
    scripts = sorted((root / "scripts" / "Source" / "User" / "TLM").glob("*.psc"), key=lambda p: p.name)
    ids = (root / "tools" / "PluginBuilder" / "formkeys.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n")
    old = "\n".join(ids[:OLD_ID_LINES]) + "\n"
    added = [l for l in ids[OLD_ID_LINES:] if l]
    documents = {d["id"]: d for d in json.loads((root / "assets/incoming/act1/story/documents.json").read_text())["documents"]}
    sources = {p.name: text_digest(p) for p in scripts}
    return {
        "sourceTextSha256": sources,
        "runtimeSelection": selection(root, sources),
        "builderSourceTextSha256": {name: text_digest(root / name) for name in BUILDER_SOURCES},
        "idFile": {
            "earlierLines": OLD_ID_LINES,
            "earlierLinesSha256": hashlib.sha256(old.encode("utf-8")).hexdigest().upper(),
            "appended": {added[i]: int(added[i + 1]) for i in range(0, len(added) - 1, 2)},
        },
        "documents": {name: {"characters": len(documents[name]["text"]),
                             "textSha256": hashlib.sha256(documents[name]["text"].encode("utf-8")).hexdigest().upper()}
                      for name in DOCUMENTS},
        "earlierManifestsSha256": {name: file_digest(root / name) for name in OLD_MANIFESTS},
        "frozenTextSha256": {name: text_digest(root / name) for name in FROZEN},
    }


def against(old: dict, have: dict) -> tuple:
    """(unchanged, changed, added, gone) of the scripts here against an earlier set of source digests."""
    return (sorted(n for n in old if have.get(n) == old[n]), sorted(n for n in old if n in have and have[n] != old[n]),
            sorted(set(have) - set(old)), sorted(set(old) - set(have)))


def problems(root: Path = ROOT, manifest_path: Path = MANIFEST) -> list:
    out = []
    manifest = json.loads(manifest_path.read_text())
    now = describe(root)
    if manifest.get("schema") != 1:
        out.append("the manifest's schema is not 1")
    want = manifest["sourceTextSha256"]
    have = now["sourceTextSha256"]
    if len(want) != SCRIPTS or manifest.get("scripts") != SCRIPTS:
        out.append("the manifest names %d scripts, not %d" % (len(want), SCRIPTS))
    if sorted(have) != sorted(want):
        out.append("the scripts in the checkout are not the %d the manifest names: only here %s, only in the manifest %s"
                   % (SCRIPTS, sorted(set(have) - set(want)), sorted(set(want) - set(have))))
    for name in sorted(set(have) & set(want)):
        if have[name] != want[name]:
            out.append("%s is not the source the manifest describes" % name)
    for key in ("builderSourceTextSha256", "idFile", "documents"):
        if now[key] != manifest[key]:
            out.append("%s is not as the manifest describes" % key)

    # The four earlier package manifests, byte for byte. A file whose content is the pinned content with other line
    # ends is still not the pinned file and still fails; it is only said to be that, so that nobody hunts for an edit.
    for name, pinned in manifest["earlierManifestsSha256"].items():
        got = now["earlierManifestsSha256"].get(name)
        if got == pinned:
            continue
        raw = (root / name).read_bytes()
        as_lf = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        if as_lf != raw and hashlib.sha256(as_lf).hexdigest().upper() == pinned:
            out.append("earlierManifestsSha256: %s is not the pinned bytes: its content is the pinned content, but this "
                       "working copy holds it with other line ends than the committed file's. Write it again from the "
                       "repository (docs/design/ACT1_RUNTIME_001_LEDGER.md, section 13)" % name)
        else:
            out.append("earlierManifestsSha256: %s is not the pinned file" % name)
    if sorted(manifest["earlierManifestsSha256"]) != sorted(OLD_MANIFESTS):
        out.append("earlierManifestsSha256 does not name exactly the four earlier manifests")
    # The a8 manifest, its check, and the earlier packagers and launcher: unchanged text.
    if sorted(manifest["frozenTextSha256"]) != sorted(FROZEN):
        out.append("frozenTextSha256 does not name exactly the frozen files")
    for name, pinned in manifest["frozenTextSha256"].items():
        if now["frozenTextSha256"].get(name) != pinned:
            out.append("frozenTextSha256: %s is not the frozen text" % name)

    # Which compiled scripts are bundled from where: 17 reviewed, 6 fresh, by name and by pinned digest.
    want_selection, have_selection = manifest["runtimeSelection"], now["runtimeSelection"]
    if want_selection != have_selection:
        out.append("runtimeSelection is not what this source and the earlier runtime's pins give")
    reused, fresh = set(want_selection["reusedReviewedPex"]), set(want_selection["freshlyCompiled"])
    if len(reused) != REVIEWED or sorted(fresh) != FRESH_NAMES or reused & fresh or reused | fresh != {pex(n) for n in want}:
        out.append("runtimeSelection is not %d reviewed compiled scripts and the %d fresh ones, %d in all, one for each source"
                   % (REVIEWED, FRESH, SCRIPTS))

    # Against the 19-script runtime the reviewed files come from.
    old = json.loads((root / "tools" / "win" / "world-details-artifact.json").read_text())["sourceTextSha256"]
    same, changed, added, gone = against(old, have)
    said = manifest["againstTheDetailsPins"]
    if (same, changed, added) != (said["unchanged"], said["changed"], said["added"]) or gone:
        out.append("against the Details pins: changed %s, added %s, gone %s; the manifest says changed %s, added %s"
                   % (changed, added, gone, said["changed"], said["added"]))
    # Against the 20-script a8 source. Every script that is changed or new since a8 is
    # compiled afresh; none of them keeps an earlier compiled file.
    a8 = json.loads((root / A8_MANIFEST).read_text())["sourceTextSha256"]
    same, changed, added, gone = against(a8, have)
    said = manifest["againstA8"]
    if (same, changed, added) != (said["unchanged"], said["changed"], said["added"]) or gone:
        out.append("against the a8 source: changed %s, added %s, gone %s; the manifest says changed %s, added %s"
                   % (changed, added, gone, said["changed"], said["added"]))
    for name in changed + added:
        if pex(name) in want_selection["reusedReviewedPex"] or pex(name) not in want_selection["freshlyCompiled"]:
            out.append("%s is changed or new since a8 and is not taken from the fresh compile" % name)
    # Against the 23-script Greenwater source this candidate grew from (016b2b4, as its own manifest pins it).
    green = json.loads((root / GREENWATER_MANIFEST).read_text())["sourceTextSha256"]
    same, changed, added, gone = against(green, have)
    said = manifest["againstGreenwater"]
    if (same, changed, added) != (said["unchanged"], said["changed"], said["added"]) or gone:
        out.append("against the Greenwater source: changed %s, added %s, gone %s; the manifest says changed %s, added %s"
                   % (changed, added, gone, said["changed"], said["added"]))
    for name in changed + added:
        if pex(name) in want_selection["reusedReviewedPex"] or pex(name) not in want_selection["freshlyCompiled"]:
            out.append("%s is changed or new since the Greenwater candidate and is not taken from the fresh compile" % name)
    # The Greenwater candidate's own 17 reviewed digests were copied from the Details runtime; they are the same 17 here.
    if json.loads((root / GREENWATER_MANIFEST).read_text())["runtimeSelection"]["reusedReviewedPex"] != want_selection["reusedReviewedPex"]:
        out.append("the 17 reviewed compiled scripts are not the 17 of the Greenwater candidate")

    # Nothing compiled or built is claimed that nobody measured.
    measured = manifest["measured"]
    values = [measured[k] for k in ("masterSha256", "worldSha256", "runtime", "runtimeManifestSha256", "freshCompile")]
    if any(v is not None for v in values) and not (measured.get("measuredBy") and measured.get("measuredFrom")):
        out.append("a built or compiled digest is recorded without who measured it and from what")
    # Never under the old pins, and the old pins never describe this candidate.
    for name in OLD_MANIFESTS + (A8_MANIFEST, GREENWATER_MANIFEST):
        text = (root / name).read_text()
        if any(word in text for word in OWN_WORDS):
            out.append("%s mentions the Night Mail road; the candidate must not be put under an earlier manifest" % name)
    return out


def measure(bundle: Path, fresh_compile: Path = None, manifest_path: Path = MANIFEST) -> dict:
    """What is in a built bundle, and whether its compiled scripts are the selection the manifest records."""
    policy = json.loads(manifest_path.read_text())["runtimeSelection"]
    reviewed, fresh_names = policy["reusedReviewedPex"], policy["freshlyCompiled"]
    files = [bundle / "TheLastMeridian.esp", bundle / "TLMWorldSlice.esp"]
    scripts = sorted((bundle / "Scripts" / "TLM").glob("*.pex"), key=lambda p: p.name)
    runtime = {p.name: file_digest(p) for p in scripts}
    lines = "".join("%s %s\n" % (name, runtime[name]) for name in sorted(runtime))
    expected = set(reviewed) | set(fresh_names)
    chosen = {
        "reusedAsReviewed": sorted(n for n in reviewed if runtime.get(n) == reviewed[n]),
        # In the bundle under a reviewed script's name, and not the reviewed bytes: a fresh compile put in its place, or anything else.
        "notTheReviewedBytes": sorted(n for n in reviewed if n in runtime and runtime[n] != reviewed[n]),
        "freshlyCompiled": {n: runtime[n] for n in fresh_names if n in runtime},
        "missing": sorted(expected - set(runtime)),
        "unexpected": sorted(set(runtime) - expected),
    }
    chosen["ok"] = (len(chosen["reusedAsReviewed"]) == len(reviewed) == REVIEWED
                    and len(chosen["freshlyCompiled"]) == len(fresh_names) == FRESH
                    and not chosen["notTheReviewedBytes"] and not chosen["missing"] and not chosen["unexpected"])
    out = {
        "masterSha256": file_digest(files[0]) if files[0].exists() else None,
        "worldSha256": file_digest(files[1]) if files[1].exists() else None,
        "runtime": runtime,
        "runtimeCount": len(runtime),
        # This candidate's own formula, stated so that it can be repeated: SHA-256 of the lines
        # "<name> <digest>\n", names in ordinal order. It is not the formula of any earlier manifest.
        "runtimeManifestSha256": hashlib.sha256(lines.encode("utf-8")).hexdigest().upper() if runtime else None,
        "selection": chosen,
    }
    if fresh_compile is not None:
        compiled = {p.name: file_digest(p) for p in sorted(Path(fresh_compile).glob("*.pex"), key=lambda p: p.name)}
        out["freshCompile"] = {
            "digests": compiled,
            "count": len(compiled),
            "allTwentySix": set(compiled) == expected,
            # The bundle's nine fresh scripts are this compile's own.
            "theBundlesNineAreFromIt": all(n in compiled and compiled[n] == runtime.get(n) for n in fresh_names),
            # Observed and nothing more: which of the 17 the compiler happened to reproduce byte for byte.
            # Whatever this says, the bundle takes the reviewed files.
            "ofTheSeventeenByteIdenticalToTheReviewed": sorted(n for n in reviewed if compiled.get(n) == reviewed[n]),
        }
    return out


def measured_as_required(report: dict) -> bool:
    fresh = report.get("freshCompile")
    return report["selection"]["ok"] and (fresh is None or (fresh["allTwentySix"] and fresh["theBundlesNineAreFromIt"]))


def main(argv):
    if len(argv) == 2 and argv[1] == "verify":
        found = problems()
        if found:
            print("%d problem(s) with the Night Mail story candidate's source:" % len(found))
            for p in found:
                print("  - " + p)
            return 1
        manifest = json.loads(MANIFEST.read_text())
        print("Night Mail story candidate: the checkout is the source its manifest describes "
              "(%d scripts: %d still the text the Details package pins; since the Greenwater candidate %s changed and %s added; "
              "%d ids appended after the earlier %d lines)."
              % (SCRIPTS, len(manifest["againstTheDetailsPins"]["unchanged"]), ", ".join(manifest["againstGreenwater"]["changed"]),
                 ", ".join(manifest["againstGreenwater"]["added"]), len(manifest["idFile"]["appended"]), manifest["idFile"]["earlierLines"]))
        print("Source only: nothing compiled, nothing built against the game's master, nothing run in the game.")
        return 0
    if len(argv) == 2 and argv[1] == "describe":
        print(json.dumps(describe(), indent=2))
        return 0
    if len(argv) in (3, 5) and argv[1] == "measure" and (len(argv) == 3 or argv[3] == "--fresh-compile"):
        report = measure(Path(argv[2]), Path(argv[4]) if len(argv) == 5 else None)
        print(json.dumps(report, indent=2))
        return 0 if measured_as_required(report) else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
