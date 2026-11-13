"""Runs self-test scenarios against the stand-in engine and prints what the
game's runner would print.

  python3 tools/papyrus_sim 1 2 3          scenarios by number
  python3 tools/papyrus_sim --log 104      with the whole self-test log
  python3 tools/papyrus_sim all            every scenario; also: basic, matrix
  python3 tools/papyrus_sim --brief all    one line, plus any that did not pass
  python3 tools/papyrus_sim --calls-per-second 60 132
                                           every call out of a script takes a
                                           sixtieth of a second, so that two
                                           script threads can overlap
  python3 tools/papyrus_sim --brief --shake 5 all
                                           every scenario five times, the
                                           timing shaken differently each time

It needs a plugin description built against a master that holds the settler
and the marker, and, for scenario 10, the test room. tools/run_checks.sh
builds one, against a stand-in master, into build/sim/; without those the
scenarios that make actors or use what the plugin places say so and stop.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sim import run_scenario  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
BASIC = list(range(1, 12))


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
    ap.add_argument("--calls-per-second", type=float, default=0.0,
                    help="make every call out of a script take 1/N seconds; 0 (the default): nothing takes time")
    ap.add_argument("--shake", type=int, default=0, metavar="N",
                    help="run every scenario N times, the timing shaken a different way each time: calls, stage handlers "
                         "and events take a few frames more or less, and ready threads run in any order (sim.Session); "
                         "0 (the default): once, unshaken")
    args = ap.parse_args()
    if args.shake and args.calls_per_second:
        ap.error("--shake sets its own times for calls; leave --calls-per-second out")
    vanilla = args.vanilla or str(Path(args.plugin).with_name("TheLastMeridian.vanilla.json"))
    wanted = [(n, shake) for n in numbers(args.scenarios) for shake in (range(args.shake) if args.shake else [None])]
    bad = checks = 0
    for n, shake in wanted:
        s = run_scenario(n, args.scripts, args.plugin, vanilla, str(ROOT / "tools" / "papyrus_natives.json"),
                         until=3000.0 if args.shake else 2000.0,
                         native_delay=(1.0 / args.calls_per_second if args.calls_per_second else 0.0), shake=shake)
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
        print("scenario %d%s: %s  %d passed, %d failed; the session ended by: %s; virtual seconds: %.1f"
              % (n, "" if shake is None else " (shake %d)" % shake, "PASSED" if ok else "NOT PASSED",
                 passed, len(fails), s.ended, s.now))
        for l in (lines if args.log else [l for l in lines if l.startswith(("FAIL", "INFO"))] + result):
            print("    " + l)
        # what the main quest's timing guards wrote (amendment A24), and any error
        for l in [l for l in s.papyrus_log if l.startswith("TLM_MQ01: A24")] + errors:
            print("    script log: " + l)
    if args.brief:
        how = ", with %g calls a second" % args.calls_per_second if args.calls_per_second else ""
        how = ", each shaken %d ways" % args.shake if args.shake else how
        print("%d of %d %s passed, %d checks%s" % (len(wanted) - bad, len(wanted), "runs" if args.shake else "scenarios", checks, how))
    print("(the stand-in engine, not the game)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
