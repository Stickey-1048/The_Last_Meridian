#!/usr/bin/env python3
"""Check that the quest matrix tests reject each single-rule regression.

This is a portable QA sensitivity check, not game, Papyrus, or plugin proof.
It runs isolated temporary copies; the production model is never edited.
A failed mutant is evidence only when unittest reports an assertion failure,
or the model's NotAvailable exception, not an import error, crash, missing
dependency, or unexpected skip.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "tools" / "logic_model"
FILES = ("tlm_model.py", "test_mq01_matrix.py", "test_sq01_matrix.py")
RULES = (
    "cutters_protected", "evade_blocked_in_combat", "betrayal_overrides",
    "resolve_unresolved_at_town", "debrief_resumable", "effects_at_debrief",
    "stage50_forces_40", "sq01_runs_from_start", "handover_keyed_on_stage",
    "hands_essential_in_town", "evade_blocked_in_conversation",
)
MARKER = "V02 = Rules()"


def run_case(directory, timeout):
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "-v", "test_mq01_matrix", "test_sq01_matrix"],
        cwd=directory, capture_output=True, text=True, timeout=timeout,
    )
    output = result.stdout + result.stderr
    summary = re.search(r"Ran (\d+) tests? in", output)
    failures = re.findall(r"^FAIL: (.+)$", output, re.MULTILINE)
    errors = re.findall(r"^ERROR: (.+)$", output, re.MULTILINE)
    error_sections = re.findall(r"^ERROR: .*?\n(.*?)(?=^={10}|^-{10}\nRan|\Z)", output, re.MULTILINE | re.DOTALL)
    model_errors = sum(bool(re.search(r"^tlm_model\.NotAvailable: .+$", section, re.MULTILINE)) for section in error_sections)
    skipped = re.findall(r"^(.+?) \.\.\. skipped (.+)$", output, re.MULTILINE)
    return {"exit_code": result.returncode,
            "tests": int(summary.group(1)) if summary else None,
            "failures": failures, "errors": errors, "model_errors": model_errors, "skipped": skipped}, output


def audit(timeout=30):
    source = (MODEL / FILES[0]).read_text()
    if source.count(MARKER) != 1:
        raise ValueError("Expected exactly one V02 = Rules() assignment; review the harness after model changes")
    report = {"scope": "logic-model matrix test sensitivity only; not game verification", "mutations": []}
    with tempfile.TemporaryDirectory(prefix="tlm-rule-qa-") as tmp:
        folder = Path(tmp)
        for name in FILES:
            shutil.copyfile(MODEL / name, folder / name)
        baseline, output = run_case(folder, timeout)
        report["baseline"] = baseline
        if baseline["exit_code"] != 0 or not baseline["tests"]:
            report["status"] = "baseline_failed"
            report["diagnostic"] = output
            return report
        for name in RULES:
            (folder / FILES[0]).write_text(source.replace(MARKER, f"V02 = Rules({name}=False)"))
            # Avoid same-size / same-second bytecode reuse between variants.
            shutil.rmtree(folder / "__pycache__", ignore_errors=True)
            result, output = run_case(folder, timeout)
            valid = (result["tests"] == baseline["tests"] and
                     result["skipped"] == baseline["skipped"] and len(result["errors"]) == result["model_errors"])
            status = ("caught" if valid and result["exit_code"] == 1 and (result["failures"] or result["model_errors"])
                      else "survived" if valid and result["exit_code"] == 0
                      else "invalid_run")
            report["mutations"].append({"rule": name, "status": status, **result})
            if status == "invalid_run":
                report["mutations"][-1]["diagnostic"] = output
        report["status"] = "passed" if all(x["status"] == "caught" for x in report["mutations"]) else "failed"
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=30, help="maximum seconds per isolated test run")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    try:
        report = audit(args.timeout)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "invalid_run", "error": str(exc)}, indent=2))
        sys.exit(2)
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["status"] == "passed" else 1)
