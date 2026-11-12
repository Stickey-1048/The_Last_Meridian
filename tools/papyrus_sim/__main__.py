"""Runs self-test scenarios against the stand-in engine and prints what the
game's runner would print.

  python3 tools/papyrus_sim --plugin build/TheLastMeridian.json 1 2 3

It needs a plugin description built against a master that holds the settler
and the marker (tools/run_checks.sh builds one against a stand-in master);
without them the scenarios that make actors report that and stop.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sim import run_scenario  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("scenarios", nargs="+", type=int)
    ap.add_argument("--plugin", default=str(ROOT / "build" / "TheLastMeridian.json"))
    ap.add_argument("--vanilla", default=None, help="default: TheLastMeridian.vanilla.json beside the plugin description")
    ap.add_argument("--scripts", default=str(ROOT / "scripts" / "Source" / "User" / "TLM"))
    ap.add_argument("--log", action="store_true", help="print the whole self-test log")
    args = ap.parse_args()
    vanilla = args.vanilla or str(Path(args.plugin).with_name("TheLastMeridian.vanilla.json"))
    bad = 0
    for n in args.scenarios:
        s = run_scenario(n, args.scripts, args.plugin, vanilla, str(ROOT / "tools" / "papyrus_natives.json"))
        lines = s.user_logs.get("TLM", [])
        passed = sum(1 for l in lines if l.startswith("PASS"))
        fails = [l for l in lines if l.startswith("FAIL")]
        result = [l for l in lines if "==== RESULT" in l]
        errors = [l for l in s.papyrus_log if l.startswith("error:")]
        ok = bool(result) and not fails and not errors and s.ended == "quit"
        bad += 0 if ok else 1
        print("scenario %d: %s  %d passed, %d failed; the session ended by: %s; virtual seconds: %.1f"
              % (n, "PASSED" if ok else "NOT PASSED", passed, len(fails), s.ended, s.now))
        for l in (lines if args.log else [l for l in lines if l.startswith(("FAIL", "INFO"))] + result):
            print("    " + l)
        for l in errors:
            print("    script log: " + l)
    print("(the stand-in engine, not the game)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
