# Portable rule-regression sensitivity check

Run `python3 tools/qa/check_rule_mutations.py` from any directory. It needs only
Python 3 and the checked-out logic model/matrix tests. JSON is printed to stdout;
exit 0 means the clean baseline passed and every one-rule regression was caught.
A survivor or invalid run exits nonzero. `--timeout 30` bounds each subprocess.

The harness copies three files into a temporary directory and disables each of
the eleven V02 safety rules separately. It never edits the checkout model.
It requires the same test count and skip list as the baseline, and accepts only
assertion failures or the model's `NotAvailable` domain exception as detections.
Import errors, test-runner crashes, and changed skips are not detections.

Harness tests: `python3 -m unittest discover -s tools/qa -v`.
This optional check does not change the existing CI or replace `tools/run_checks.sh`.

## Bounded QA task and evidence, 2026-11-15

Authority: Chris asked to advance Meridian independently while he is away.
Scope: test sensitivity only, using source at
`70b6ec552bfc45943b2a9728dc8bb9417a9970b2` as the baseline.
No quest logic, Papyrus, plugin, narrative, workflow permissions, or game install
changes. Role: independent QA investigation and regression-test candidate,
not a claim of Claude implementation or owner acceptance.

The original fast matrices ran 69 tests, with 8 explicit engine-only skips.
They did not detect individual regressions in `cutters_protected` or
`debrief_resumable`. The full exhaustive suite was not mutation-tested; this is
not a claim that those defects escape every existing check.

The added protected-lead test explicitly rejects an NPC resolving that encounter.
The strengthened resume test asserts that abandonment is unavailable under V02,
then confirms the return/handoff path remains available. The V01 comparison stays.
With these test changes, 70 matrix tests run with the same 8 engine-only skips,
and all eleven single-rule regressions are detected. The original five
negative/classification tests passed on Linux/Python 3. Independent review added
a sixth test: an import error raised while handling `NotAvailable` must invalidate
the audit, rather than count as a semantic detection. All six tests and the full
eleven-rule audit passed with bundled Python on Windows after that correction.

No .NET SDK was present in the QA environment. The full plugin aggregate,
Papyrus compilation, Windows execution, and physical player acceptance were not
run. Remote CI and separate review are pending until their actual results are
recorded on the draft PR. No merge or release is authorized by this result.

Rollback: revert the test-only commit or discard its task branch. No saved game
or installed build is touched.
