"""Runs self-test scenarios against the stand-in engine and prints what the
game's runner would print.

  python3 tools/papyrus_sim 1 2 3          scenarios by number
  python3 tools/papyrus_sim --log 104      with the whole self-test log
  python3 tools/papyrus_sim all            every scenario; also: basic, matrix
  python3 tools/papyrus_sim --brief all    one line, plus any that did not pass

It needs a plugin description built against a master that holds the settler
and the marker. tools/run_checks.sh builds one, against a stand-in master,
into build/sim/; without those two forms the scenarios that make actors say
so and stop.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sim import run_scenario  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
BASIC = list(range(1, 10))


def matrix_numbers():
    path = ROOT / "tools" / "matrix_cases.json"
    return [c["scenario"] for c in json.loads(path.read_text())["cases"]] if path.exists() else []


def numbers(words):
    out = []
    for w in words:
        if w == "basic":
            out += BASIC
        elif w == "matrix":
            out += matrix_numbers()
        elif w == "all":
            out += BASIC + matrix_numbers()
        elif "-" in w:
            a, b = w.split("-", 1)
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(w))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("scenarios", nargs="+", help="numbers, ranges like 101-128, or: basic, matrix, all")
    ap.add_argument("--plugin", default=str(ROOT / "build" / "sim" / "TheLastMeridian.json"),
                    help="default: build/sim/TheLastMeridian.json, which tools/run_checks.sh builds")
    ap.add_argument("--vanilla", default=None, help="default: TheLastMeridian.vanilla.json beside the plugin description")
    ap.add_argument("--scripts", default=str(ROOT / "scripts" / "Source" / "User" / "TLM"))
    ap.add_argument("--log", action="store_true", help="print the whole self-test log")
    ap.add_argument("--brief", action="store_true", help="print only a total and the scenarios that did not pass")
    args = ap.parse_args()
    vanilla = args.vanilla or str(Path(args.plugin).with_name("TheLastMeridian.vanilla.json"))
    wanted = numbers(args.scenarios)
    bad = checks = 0
    for n in wanted:
        s = run_scenario(n, args.scripts, args.plugin, vanilla, str(ROOT / "tools" / "papyrus_natives.json"))
        lines = s.user_logs.get("TLM", [])
        passed = sum(1 for l in lines if l.startswith("PASS"))
        fails = [l for l in lines if l.startswith("FAIL")]
        result = [l for l in lines if "==== RESULT" in l]
        errors = [l for l in s.papyrus_log if l.startswith("error:")]
        ok = bool(result) and not fails and not errors and s.ended == "quit"
        bad += 0 if ok else 1
        checks += passed
        if args.brief and ok:
            continue
        print("scenario %d: %s  %d passed, %d failed; the session ended by: %s; virtual seconds: %.1f"
              % (n, "PASSED" if ok else "NOT PASSED", passed, len(fails), s.ended, s.now))
        for l in (lines if args.log else [l for l in lines if l.startswith(("FAIL", "INFO"))] + result):
            print("    " + l)
        for l in errors:
            print("    script log: " + l)
    if args.brief:
        print("%d of %d scenarios passed, %d checks" % (len(wanted) - bad, len(wanted), checks))
    print("(the stand-in engine, not the game)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
