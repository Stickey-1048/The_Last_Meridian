#!/usr/bin/env python3
"""The Mercy briefing candidate (ACT1-RUNTIME-001): its source manifest.

tools/win/mercy-briefing-candidate.json says which source this candidate is:
the 20 script sources by digest, the builder's spec files, the id file, the
approved document's text. It is a manifest of SOURCE. It holds no digest of a
compiled script or of a built plugin until somebody has built one against the
game's own master and measured it; nothing here invents one.

It is not, and must never be put under, the pins of the Details, Natural or
story packages (tools/win/world-*-artifact.json). Those describe the 19-script
runtime and are unchanged; their packagers refuse this checkout's source, as
they should.

WHICH COMPILED SCRIPTS GO INTO THE BUNDLE. Two things, kept apart:
  - proof that the source compiles: all 20 scripts compiled afresh, the log
    and the results kept;
  - the runtime selected for the bundle: the 18 scripts whose source is
    unchanged are taken as the REVIEWED compiled files of the earlier runtime
    (the ones tools/win/world-details-artifact.json pins), each only after its
    source text and its bytes have been checked against those pins; Act1Walk
    and MercyBriefing are taken from the fresh compile.
The freshly compiled 18 are never put into the bundle in place of the reviewed
ones, and nothing here assumes that the compiler reproduces the old bytes.

    python3 tools/mercy_briefing_candidate.py verify
        The checkout is the source the manifest describes. Exit 1 if not.

    python3 tools/mercy_briefing_candidate.py describe
        Prints what the manifest would hold for the checkout as it is now
        (for whoever changes the candidate on purpose and reviews the diff).

    python3 tools/mercy_briefing_candidate.py measure <bundle folder> [--fresh-compile <folder>]
        Prints, as JSON for a build receipt, the SHA-256 of TheLastMeridian.esp,
        TLMWorldSlice.esp and every Scripts/TLM/*.pex in a built bundle, and
        says of each compiled script whether it is the reviewed file it has to
        be or one of the two fresh ones. With --fresh-compile, also the digests
        of the full compile, whether it holds all 20, and whether the bundle's
        two fresh scripts are that compile's. Exit 1 if the selection is not
        the one above. It writes nothing and changes no pin.

Needs Python 3 only. Not a compile and not a game test.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tools" / "win" / "mercy-briefing-candidate.json"
SCRIPTS = ROOT / "scripts" / "Source" / "User" / "TLM"
DETAILS = ROOT / "tools" / "win" / "world-details-artifact.json"
OLD_MANIFESTS = ("tools/win/world-details-artifact.json", "tools/win/world-natural-artifact.json",
                 "tools/win/world-story-artifact.json", "tools/WorldSliceBuilder/expanded-artifact.json")
BUILDER_SOURCES = ("tools/PluginBuilder/Spec.cs", "tools/PluginBuilder/SpecAct1.cs", "tools/PluginBuilder/SpecMercyBriefing.cs",
                   "tools/PluginBuilder/SpecGuide.cs", "tools/PluginBuilder/SpecOrientation.cs", "tools/PluginBuilder/Builder.cs",
                   "tools/PluginBuilder/formkeys.txt", "tools/WorldSliceBuilder/WorldStory.cs")
# The id file as it was before this candidate: its first 316 lines.
OLD_ID_LINES = 316


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
        "policy": "The 18 scripts whose source text is unchanged are bundled as the reviewed compiled files of the earlier "
                  "runtime, byte for byte, after their source and their bytes have been checked against its pins. "
                  "Act1Walk.pex and MercyBriefing.pex are bundled from the fresh compile. A full fresh compile of all 20 "
                  "is the proof that the source compiles and is kept with its log; its 18 are not bundled, and no "
                  "compiler output is assumed to equal an earlier one.",
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
    document = {d["id"]: d for d in json.loads((root / "assets/incoming/act1/story/documents.json").read_text())["documents"]}["docket_2298"]
    sources = {p.name: text_digest(p) for p in scripts}
    return {
        "sourceTextSha256": sources,
        "runtimeSelection": selection(root, sources),
        "builderSourceTextSha256": {name: text_digest(root / name) for name in BUILDER_SOURCES},
        "idFile": {
            "earlierLines": OLD_ID_LINES,
            "earlierLinesSha256": hashlib.sha256(old.encode("utf-8")).hexdigest().upper(),
            "appended": {added[i]: int(added[i + 1]) for i in range(0, len(added), 2)},
        },
        "document": {"id": "docket_2298", "characters": len(document["text"]),
                     "textSha256": hashlib.sha256(document["text"].encode("utf-8")).hexdigest().upper()},
        "earlierManifestsSha256": {name: file_digest(root / name) for name in OLD_MANIFESTS},
    }


def problems(root: Path = ROOT, manifest_path: Path = MANIFEST) -> list:
    out = []
    manifest = json.loads(manifest_path.read_text())
    now = describe(root)
    if manifest.get("schema") != 1:
        out.append("the manifest's schema is not 1")
    want = manifest["sourceTextSha256"]
    have = now["sourceTextSha256"]
    if len(want) != 20:
        out.append("the manifest names %d scripts, not 20" % len(want))
    if sorted(have) != sorted(want):
        out.append("the scripts in the checkout are not the 20 the manifest names: only here %s, only in the manifest %s"
                   % (sorted(set(have) - set(want)), sorted(set(want) - set(have))))
    for name in sorted(set(have) & set(want)):
        if have[name] != want[name]:
            out.append("%s is not the source the manifest describes" % name)
    for key in ("builderSourceTextSha256", "idFile", "document"):
        if now[key] != manifest[key]:
            out.append("%s is not as the manifest describes" % key)
    # The earlier manifests, byte for byte. A file whose content is the pinned content with other line ends is
    # still not the pinned file and still fails; it is only said to be that, so that nobody hunts for an edit.
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

    # Which compiled scripts are bundled from where: 18 reviewed, 2 fresh, by name and by pinned digest.
    want_selection, have_selection = manifest["runtimeSelection"], now["runtimeSelection"]
    if want_selection != have_selection:
        out.append("runtimeSelection is not what this source and the earlier runtime's pins give")
    reused, fresh = set(want_selection["reusedReviewedPex"]), set(want_selection["freshlyCompiled"])
    if len(reused) != 18 or fresh != {"Act1Walk.pex", "MercyBriefing.pex"} or reused & fresh \
            or reused | fresh != {pex(n) for n in want}:
        out.append("runtimeSelection is not 18 reviewed compiled scripts and the 2 fresh ones, 20 in all, one for each source")

    # Against the 19-script runtime this candidate grew from: one script changed, one added, eighteen untouched.
    old = json.loads((root / "tools" / "win" / "world-details-artifact.json").read_text())["sourceTextSha256"]
    changed = sorted(n for n in old if n in have and have[n] != old[n])
    added = sorted(set(have) - set(old))
    gone = sorted(set(old) - set(have))
    if changed != manifest["changed"] or added != manifest["added"] or gone:
        out.append("against the Details pins: changed %s, added %s, gone %s; the manifest says changed %s, added %s"
                   % (changed, added, gone, manifest["changed"], manifest["added"]))
    if sorted(n for n in old if n in have and have[n] == old[n]) != sorted(manifest["unchangedFromTheDetailsPins"]):
        out.append("the scripts unchanged from the Details pins are not the eighteen the manifest names")

    # Nothing compiled or built is claimed that nobody measured.
    measured = manifest["measured"]
    values = [measured[k] for k in ("masterSha256", "worldSha256", "runtime", "runtimeManifestSha256", "freshCompile")]
    if any(v is not None for v in values) and not (measured.get("measuredBy") and measured.get("measuredFrom")):
        out.append("a built or compiled digest is recorded without who measured it and from what")
    # Never under the old pins, and the old pins never describe this candidate.
    for name in OLD_MANIFESTS:
        text = (root / name).read_text()
        if "MercyBriefing" in text or "mercy-briefing" in text:
            out.append("%s mentions the Mercy briefing; the candidate must not be put under an earlier manifest" % name)
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
    chosen["ok"] = (len(chosen["reusedAsReviewed"]) == len(reviewed) == 18 and len(chosen["freshlyCompiled"]) == len(fresh_names) == 2
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
            "allTwenty": set(compiled) == expected,
            # The bundle's two fresh scripts are this compile's own.
            "theBundlesTwoAreFromIt": all(n in compiled and compiled[n] == runtime.get(n) for n in fresh_names),
            # Observed and nothing more: which of the 18 the compiler happened to reproduce byte for byte.
            # Whatever this says, the bundle takes the reviewed files.
            "ofTheEighteenByteIdenticalToTheReviewed": sorted(n for n in reviewed if compiled.get(n) == reviewed[n]),
        }
    return out


def measured_as_required(report: dict) -> bool:
    fresh = report.get("freshCompile")
    return report["selection"]["ok"] and (fresh is None or (fresh["allTwenty"] and fresh["theBundlesTwoAreFromIt"]))


def main(argv):
    if len(argv) == 2 and argv[1] == "verify":
        found = problems()
        if found:
            print("%d problem(s) with the Mercy briefing candidate's source:" % len(found))
            for p in found:
                print("  - " + p)
            return 1
        manifest = json.loads(MANIFEST.read_text())
        print("Mercy briefing candidate: the checkout is the source its manifest describes "
              "(20 scripts: %d unchanged from the Details pins, %s changed, %s added; %d ids appended after the earlier %d lines)."
              % (len(manifest["unchangedFromTheDetailsPins"]), ", ".join(manifest["changed"]), ", ".join(manifest["added"]),
                 len(manifest["idFile"]["appended"]), manifest["idFile"]["earlierLines"]))
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
