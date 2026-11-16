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

    python3 tools/mercy_briefing_candidate.py verify
        The checkout is the source the manifest describes. Exit 1 if not.

    python3 tools/mercy_briefing_candidate.py describe
        Prints what the manifest would hold for the checkout as it is now
        (for whoever changes the candidate on purpose and reviews the diff).

    python3 tools/mercy_briefing_candidate.py measure <bundle folder>
        Prints the SHA-256 of TheLastMeridian.esp, TLMWorldSlice.esp and every
        Scripts/TLM/*.pex in a built bundle, as JSON, for a build receipt.
        It writes nothing and changes no pin.

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


def describe(root: Path = ROOT) -> dict:
    """What the manifest's measured-from-source part should hold for this checkout."""
    scripts = sorted((root / "scripts" / "Source" / "User" / "TLM").glob("*.psc"), key=lambda p: p.name)
    ids = (root / "tools" / "PluginBuilder" / "formkeys.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n")
    old = "\n".join(ids[:OLD_ID_LINES]) + "\n"
    added = [l for l in ids[OLD_ID_LINES:] if l]
    document = {d["id"]: d for d in json.loads((root / "assets/incoming/act1/story/documents.json").read_text())["documents"]}["docket_2298"]
    return {
        "sourceTextSha256": {p.name: text_digest(p) for p in scripts},
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
    for key in ("builderSourceTextSha256", "idFile", "document", "earlierManifestsSha256"):
        if now[key] != manifest[key]:
            out.append("%s is not as the manifest describes" % key)

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
    values = [measured[k] for k in ("masterSha256", "worldSha256", "runtime", "runtimeManifestSha256")]
    if any(v is not None for v in values) and not (measured.get("measuredBy") and measured.get("measuredFrom")):
        out.append("a built or compiled digest is recorded without who measured it and from what")
    # Never under the old pins, and the old pins never describe this candidate.
    for name in OLD_MANIFESTS:
        text = (root / name).read_text()
        if "MercyBriefing" in text or "mercy-briefing" in text:
            out.append("%s mentions the Mercy briefing; the candidate must not be put under an earlier manifest" % name)
    return out


def measure(bundle: Path) -> dict:
    files = [bundle / "TheLastMeridian.esp", bundle / "TLMWorldSlice.esp"]
    scripts = sorted((bundle / "Scripts" / "TLM").glob("*.pex"), key=lambda p: p.name)
    runtime = {p.name: file_digest(p) for p in scripts}
    lines = "".join("%s %s\n" % (name, runtime[name]) for name in sorted(runtime))
    return {
        "masterSha256": file_digest(files[0]) if files[0].exists() else None,
        "worldSha256": file_digest(files[1]) if files[1].exists() else None,
        "runtime": runtime,
        "runtimeCount": len(runtime),
        # This candidate's own formula, stated so that it can be repeated: SHA-256 of the lines
        # "<name> <digest>\n", names in ordinal order. It is not the formula of any earlier manifest.
        "runtimeManifestSha256": hashlib.sha256(lines.encode("utf-8")).hexdigest().upper() if runtime else None,
    }


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
    if len(argv) == 3 and argv[1] == "measure":
        print(json.dumps(measure(Path(argv[2])), indent=2))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
