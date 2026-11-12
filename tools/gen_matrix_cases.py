#!/usr/bin/env python3
"""Writes the in-game test cases of the matrix from the logic model.

  python3 tools/gen_matrix_cases.py           write the files
  python3 tools/gen_matrix_cases.py --check   fail if the files on disk are stale

Output:
  scripts/Source/User/TLM/MatrixCases.psc   one Papyrus function per case
  tools/matrix_cases.json                   the same list as data (for the
                                            runner on the PC and the docs)

A case is a row, or a few rows, of the test matrices in tools/logic_model
(T01-T28 for TLM_MQ01, S01-S24 for TLM_SQ01), written as a list of the logic
model's events. For every event the generated code

  1. does what stands for the event in the game (TLM:CaseDriver), and
  2. compares everything the driver can see of both quests with the state the
     logic model reaches after that event.

So no expected value is typed by hand: the model computes all of them here.
Three kinds of step:

  do(e)         the model applies e; it must be available.
  attempt(e)    the model says e is NOT available here and its guard is in the
                quest script (not in a dialogue condition). The game is made to
                try it anyway; nothing may change.
  via(e, a)     the model applies e, but the game is given the action of a.
                For the one place where the script turns one request into
                another: posting with Haskell's name when Haskell is dead
                posts with no name.

What the cases cannot show is listed in NOT_RUN below, row by row.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "logic_model"))
sys.path.insert(0, str(ROOT / "tools" / "papyrus_sim"))

import tlm_model as m                      # noqa: E402
from tlm_model import apply, available     # noqa: E402
from psc import parse_file                 # noqa: E402

SCRIPTS = ROOT / "scripts" / "Source" / "User" / "TLM"
OUT_PSC = SCRIPTS / "MatrixCases.psc"
OUT_JSON = ROOT / "tools" / "matrix_cases.json"

# The stages the driver looks at, in the order it reports them
# (TLM:CaseDriver.MainStages / SideStages; test_matrix_cases.py compares).
MQ_STAGES = [10, 15, 20, 30, 31, 32, 33, 34, 35, 37, 40, 50, 51, 52, 53, 54, 55, 60, 100, 900]
SQ_STAGES = [5, 10, 11, 12, 13, 14, 20, 25, 41, 42, 43, 44, 45, 46, 50, 100, 900]

VARIANT_CODE = {None: 0, m.V_SAVED: 1, m.V_EVADED: 2, m.V_WITNESS: 3, m.V_NOWITNESS: 4, m.V_MISSED: 5, m.V_LOST: 6}
ANSWER_CODE = {None: 0, "admit": 1, "deny": 2, "confess": 3, "blame": 4, "silent": 9}
ANSWER_LYING = 5                # "deny" when a witness accuses: "She's lying."
HASKELL_CODE = {"present": 0, "gone": 1, "dead": 2}
DECISION_STAGE = {"sq_report": 41, "sq_post": 42, "sq_post_yard": 43, "sq_post_haskell": 44, "sq_sell": 45, "sq_destroy": 46}
ANSWER_STAGE = {"debrief_admit": 51, "debrief_deny": 52, "debrief_confess": 53, "debrief_blame": 54}
COMBAT_EVENTS = {"attack_cutter", "break_combat", "dunmore_speech_fail", "dunmore_refuse"}
SKIP = -999                     # TLM:CaseDriver.SKIP: "not looked at in this step"


def do(event):
    return ("do", event, event)


def attempt(event):
    return ("attempt", event, event)


def via(event, action):
    return ("via", event, action)


def steps(*items):
    return [do(x) if isinstance(x, str) else x for x in items]


TO_AMBUSH = ["start", "take_dispatch", "goto_ambush"]
DELIVER = ["goto_town", "pritchard_handover"]
FINISH = DELIVER + ["pritchard_handoff"]
LEDGER = ["start", "take_ledger"]
LEVEL1 = LEDGER + ["examine_e1", "goto_town"]
LEVEL2 = LEDGER + ["examine_e1", "take_journal", "goto_town"]
NO_ANSWER = [attempt("debrief_admit"), attempt("debrief_deny"), attempt("debrief_confess"), attempt("debrief_blame")]

# (scenario number, matrix rows it stands for, title, steps)
CASES = [
    (101, ["T01", "T02", "T03"], "the start, the revolver hint once, the dispatch",
     steps("start", "take_revolver", attempt("take_revolver"), "take_dispatch")),
    (102, ["T04", "T10b", "T23 missed", "S15"], "never meets the ambush; no answer is offered; the side quest untouched",
     steps("start", "take_dispatch", *DELIVER, *NO_ANSWER, "pritchard_handoff")),
    (103, ["T05", "T05b"], "three Cutters dead is not a rescue; the lead's death is",
     steps(*TO_AMBUSH, "player_kills_cutter", "player_kills_cutter", "player_kills_cutter", "player_kills_lead")),
    (104, ["T06", "T26", "T23 saved", "T24 saved"], "saved by killing the lead, delivered, handed off",
     steps(*TO_AMBUSH, "player_kills_lead", *FINISH)),
    (105, ["T07"], "saved by talking the Cutters down",
     steps(*TO_AMBUSH, "dunmore_speech_success", *FINISH)),
    (106, ["T08"], "the speech fails, the Cutters turn on the player, the lead dies",
     steps(*TO_AMBUSH, "dunmore_speech_fail", "player_kills_lead")),
    (107, ["T09", "T23 evaded", "T24 evaded, admit"], "evaded when the timer runs out; admitted",
     steps(*TO_AMBUSH, "evade_timer", *DELIVER, "debrief_admit", "pritchard_handoff")),
    (108, ["T24 evaded, deny"], "evaded; denied",
     steps(*TO_AMBUSH, "evade_timer", *DELIVER, "debrief_deny", "pritchard_handoff")),
    (109, ["T24 evaded, silent", "T26b"], "evaded; walks away after the hand-over, comes back, says nothing",
     steps(*TO_AMBUSH, "evade_timer", *DELIVER, "goto_wreck", "goto_town", "pritchard_handoff")),
    (110, ["T09b"], "evaded by leaving, with the caravan there",
     steps(*TO_AMBUSH, *FINISH)),
    (111, ["T10a"], "going back to the wreck from a live ambush is evading",
     steps(*TO_AMBUSH, "goto_wreck")),
    (112, ["T11", "T23 deal", "T24 deal, confess", "T25"], "the deal; confessed; one answer only",
     steps(*TO_AMBUSH, "dunmore_deal", *DELIVER, "debrief_confess", attempt("debrief_confess"), attempt("debrief_blame"), "pritchard_handoff")),
    (113, ["T24 deal, blame"], "the deal; the Cutters blamed",
     steps(*TO_AMBUSH, "dunmore_deal", *DELIVER, "debrief_blame", "pritchard_handoff")),
    (114, ["T24 deal, deny"], "the deal; the witness called a liar",
     steps(*TO_AMBUSH, "dunmore_deal", *DELIVER, "debrief_deny", "pritchard_handoff")),
    (115, ["T12", "T23 betrayal, no witness"], "the caravan master killed at the ambush; nobody left to tell",
     steps(*TO_AMBUSH, "player_kills_nell", *FINISH)),
    (116, ["T12b", "T23 betrayal, witness"], "the drover killed at the ambush; the caravan master saw it",
     steps(*TO_AMBUSH, "player_kills_abel", *FINISH)),
    (117, ["T12c"], "saved, then the caravan master killed; the drover saw it",
     steps(*TO_AMBUSH, "player_kills_lead", "player_kills_nell", *FINISH)),
    (118, ["T12d"], "in town the caravan hands cannot be killed",
     steps(*TO_AMBUSH, "player_kills_lead", "goto_town", attempt("player_kills_nell"), attempt("player_kills_abel"))),
    (119, ["T14"], "the timer does not resolve the ambush during a fight",
     steps(*TO_AMBUSH, "attack_cutter", attempt("evade_timer"))),
    (120, ["T14b"], "leaving during a fight is evading",
     steps(*TO_AMBUSH, "attack_cutter", "goto_town")),
    (121, ["T14c"], "a fight, then quiet, then the timer: evaded",
     steps(*TO_AMBUSH, "attack_cutter", "break_combat", "evade_timer")),
    (122, ["T17"], "town before the dispatch: the sheriff sends the player back",
     steps("start", "goto_ambush", "goto_town", "pritchard_no_dispatch", attempt("pritchard_handover"))),
    (123, ["T18"], "the dispatch taken late",
     steps("start", "goto_ambush", "goto_town", "pritchard_no_dispatch", "goto_wreck", "take_dispatch", "goto_town",
           "pritchard_handover", "pritchard_handoff")),
    (124, ["T19"], "the dispatch lost and given back by recovery, once",
     steps("start", "take_dispatch", "dispatch_vanishes", "recovery", attempt("recovery"), *FINISH)),
    (125, ["T19b"], "recovery gives nothing that was not earned",
     steps("start", attempt("recovery"))),
    (126, ["T19c"], "the hand-over stands without the dispatch",
     steps("start", "take_dispatch", "dispatch_vanishes", *DELIVER)),
    (127, ["T21"], "the caravan master dead by another cause",
     steps(*TO_AMBUSH, "player_kills_lead", "nell_dies_other", *FINISH)),
    (128, ["T26c"], "the gate trigger never touched: the hand-over runs the town stage",
     steps(*TO_AMBUSH, "player_kills_lead", "goto_town_bypass_gate", "pritchard_handover")),

    (201, ["S01"], "the ledger alone decides nothing",
     steps(*LEDGER, "goto_town", attempt("sq_report"), attempt("sq_post"), attempt("sq_post_yard"),
           attempt("sq_post_haskell"), attempt("sq_sell"))),
    (202, ["S02"], "a clue examined before the ledger counts",
     steps("start", "examine_e1", "take_ledger")),
    (203, ["S03"], "the ledger and one clue",
     steps(*LEDGER, "examine_e1")),
    (204, ["S04", "S04b"], "the journal alone is level 1; with one more it is level 2",
     steps(*LEDGER, "take_journal", "examine_e1")),
    (205, ["S05", "S05b"], "two physical clues are level 1; three without the journal are level 2",
     steps(*LEDGER, "examine_e1", "examine_e2", "goto_town", "pike_parts_book")),
    (206, ["S06", "S22"], "reported to the sheriff, before the dispatch is delivered",
     steps(*LEVEL1, "sq_report")),
    (207, ["S07"], "posted with no name",
     steps(*LEVEL1, "sq_post")),
    (208, ["S08"], "the Yard Office cannot be named at level 1",
     steps(*LEVEL1, attempt("sq_post_yard"))),
    (209, ["S09"], "the Yard Office named at level 2",
     steps(*LEVEL2, "sq_post_yard")),
    (210, ["S10"], "Haskell made the scapegoat",
     steps(*LEVEL1, "sq_post_haskell")),
    (211, ["S10b"], "the scapegoat is open even with full evidence",
     steps(*LEVEL2, "sq_post_haskell")),
    (212, ["S11"], "sold",
     steps(*LEVEL2, "sq_sell")),
    (213, ["S12"], "destroyed, straight after finding it",
     steps(*LEDGER, "sq_destroy")),
    (214, ["S13"], "doing nothing leaves the decision open",
     steps(*LEVEL1, "goto_wreck", "goto_town", "sq_report")),
    (215, ["S17"], "one outcome only",
     steps(*LEVEL2, "sq_post", attempt("sq_report"), attempt("sq_post_yard"), attempt("sq_post_haskell"),
           attempt("sq_sell"), attempt("sq_destroy"))),
    (216, ["S18"], "the journal taken before the ledger",
     steps("start", "take_journal", "take_ledger", "examine_e1")),
    (217, ["S19"], "Haskell dead: naming him posts the pages with no name",
     steps(*LEVEL1, "haskell_dies", via("sq_post", "sq_post_haskell"))),
    (218, ["S21"], "the ledger lost, given back by recovery, then reported",
     steps(*LEVEL1, "ledger_vanishes", "recovery", "sq_report")),
    (219, ["S21 unrepaired"], "the ledger lost; the report stands without it",
     steps(*LEVEL1, "ledger_vanishes", "sq_report")),
    (220, ["S23"], "reported after the main quest is finished",
     steps("start", "take_dispatch", "take_ledger", "examine_e1", *FINISH, "sq_report")),
    (221, ["S24"], "evidence is frozen after the outcome",
     steps(*LEVEL1, "sq_sell", "goto_wreck", attempt("examine_e2"))),
]

# Rows of the matrices that no case stands for, and why.
NOT_RUN = {
    "T13": "ownership and theft: engine behaviour, needs a placed container",
    "T15": "reload in mid-encounter: needs a save and a load",
    "T16": "reload at each stage: needs a save and a load",
    "T20": "the sheriff's Essential flag: needs the placed actor",
    "T22": "arrival at night: packages and time of day",
    "T27": "clean plugin load: seen in every run, not a case",
    "T28": "unrelated saves: needs other saves",
    "S14": "Pike dead: the guard is a dialogue condition, and there is no dialogue yet",
    "S16": "reload: needs a save and a load",
    "S20": "Vane dead hides the sale: the guard is a dialogue condition, and there is no dialogue yet",
}

# Attempts the matrices make that are left out because only a dialogue
# condition stands in their way (the script would obey the stage).
DIALOGUE_GUARDED = {
    "T08": "the deal is no longer offered once the fight has started",
}


class Bad(Exception):
    pass


def stage_text(done, order):
    return "".join(" %d" % st for st in order if st in done)


def flag(b):
    return 1 if b else 0


def papyrus_bool(b):
    return "true" if b else "false"


def action_for(event, pre, post):
    """The driver calls that stand for an event, and the stages they set by hand."""
    live_at_ambush = pre.loc == m.AMBUSH and pre.caravan_state == m.LIVE
    newly = set(post.stages) - set(pre.stages)
    if event == "start":
        return ["DoStart()"], {10}, set()
    if event == "take_revolver":
        return ["DoTakeRevolver()"], {15}, set()
    if event == "take_dispatch":
        return ["DoTakeDispatch()"], {20}, set()
    if event == "goto_ambush":
        if 30 in newly:
            return ["DoEnterAmbush()"], {30}, set()
        return [], set(), set()
    if event in ("goto_wreck", "goto_town_bypass_gate"):
        return (["DoLeaveAmbush()"] if live_at_ambush else []), set(), set()
    if event == "goto_town":
        calls = ["DoLeaveAmbush()"] if live_at_ambush else []
        if 40 in newly:
            return calls + ["DoReachTown()"], {40}, set()
        return calls, set(), set()
    if event == "evade_timer":
        return ["DoEvadeTimer(%s)" % papyrus_bool(32 in newly)], set(), set()
    if event == "attack_cutter":
        return ["DoAttackCutter()"], set(), set()
    if event == "break_combat":
        return ["DoBreakCombat()"], set(), set()
    if event == "player_kills_lead":
        return ["DoKillLead(%s)" % papyrus_bool(31 in newly)], set(), set()
    if event == "player_kills_cutter":
        return ["DoKillCutter()"], set(), set()
    if event == "dunmore_speech_success":
        return ["DoSpeechSuccess()"], {31}, set()
    if event in ("dunmore_speech_fail", "dunmore_refuse"):
        return ["DoSpeechFail()"], {37}, set()
    if event == "dunmore_deal":
        return ["DoDeal()"], {33}, set()
    if event == "player_kills_nell":
        return ["DoKillNell(%s)" % papyrus_bool(35 in newly)], set(), set()
    if event == "player_kills_abel":
        return ["DoKillAbel(%s)" % papyrus_bool(35 in newly)], set(), set()
    if event == "nell_dies_other":
        return ["DoNellDiesOther()"], set(), set()
    if event == "dispatch_vanishes":
        return ["DoDispatchVanishes()"], set(), set()
    if event == "recovery":
        return ["DoRecovery()"], {900}, {900}
    if event == "pritchard_no_dispatch":
        return [], set(), set()
    if event == "pritchard_handover":
        return ["DoHandover()"], {50}, set()
    if event in ANSWER_STAGE:
        stage = ANSWER_STAGE[event]
        if event == "debrief_deny" and pre.debrief_variant == m.V_WITNESS:
            stage = 55
        return ["DoAnswer(%d)" % stage], {stage}, set()
    if event == "pritchard_handoff":
        return ["DoHandoff()"], {60}, set()
    if event == "take_ledger":
        return ["DoTakeLedger()"], set(), {10}
    if event == "examine_e1":
        return ["DoExamine(11)"], set(), {11}
    if event == "examine_e2":
        return ["DoExamine(12)"], set(), {12}
    if event == "take_journal":
        return ["DoTakeJournal()"], set(), {13}
    if event == "pike_parts_book":
        return ["DoPartsBook()"], set(), {14}
    if event in DECISION_STAGE:
        return ["DoDecide(%d)" % DECISION_STAGE[event]], set(), {DECISION_STAGE[event]}
    if event == "haskell_dies":
        return ["DoHaskellDies()"], set(), set()
    if event == "ledger_vanishes":
        return ["DoLedgerVanishes()"], set(), set()
    raise Bad("no action in the game stands for the event %s" % event)


def sale_price():
    prop = parse_file(SCRIPTS / "SQ01Quest.psc").properties["saleprice"]
    return prop.default[1]


def cargo_count():
    var = parse_file(SCRIPTS / "CaseDriver.psc").variables["cargo_count"]
    return var.init[1]


def build_case(number, rows, title, case_steps, price, cargo):
    """The Papyrus lines of one case, and a description of it."""
    name = "C%d" % number
    s = m.State()
    extra_mq, extra_sq = set(), set()
    in_town = {"master": 0, "drover": 0}
    lines = []
    listed = []
    for index, (kind, event, act) in enumerate(case_steps, 1):
        pre = s
        if kind == "attempt":
            if event in available(pre):
                raise Bad("%s step %d: the model says %s IS available here; it cannot be an attempt" % (name, index, event))
            post = pre
            what = "attempt: " + event
        else:
            try:
                post = apply(pre, event)
            except m.NotAvailable:
                raise Bad("%s step %d: the model says %s is not available here" % (name, index, event))
            what = event if kind == "do" else "%s, asked for as %s" % (event, act)
        # What the game is asked to do. For "via" the request is another event's.
        if kind == "via":
            calls, set_mq, set_sq = action_for(act, pre, pre)
        else:
            calls, set_mq, set_sq = action_for(act, pre, post)
        extra_mq |= set_mq
        extra_sq |= set_sq
        if 40 in set(post.stages) - set(pre.stages):
            in_town = {"master": flag(post.nell_alive), "drover": flag(post.abel_alive)}
        elif post.done(40) and (pre.nell_alive, pre.abel_alive) != (post.nell_alive, post.abel_alive):
            raise Bad("%s step %d: a caravan hand dies after the town stage; the driver cannot tell that apart" % (name, index))
        listed.append(what)
        lines.append("\tcaseDriver.Mark(%d, \"%s\")" % (index, what))
        if not calls:
            lines.append("\t; nothing in the game stands for this: only the model's idea of where the player is changes")
        for call in calls:
            lines.append("\tcaseDriver." + call)
        s = post
        answer = ANSWER_CODE[s.debrief_answer]
        if s.debrief_answer == "deny" and s.debrief_variant == m.V_WITNESS:
            answer = ANSWER_LYING
        lines.append("\tcaseDriver.ExpectMain(\"%s\", %d, %d, %d, %d, %d, %d, %d, %d, %d)" % (
            stage_text(set(s.stages) | extra_mq, MQ_STAGES), s.outcome, s.method, s.alive_at_mercy, s.rep,
            VARIANT_CODE[s.debrief_variant], answer, s.mq01_done, s.o10, s.o20))
        lines.append("\tcaseDriver.ExpectWorld(%d, %d, %d, %d, %d, %d, %d, %d, %d, %d)" % (
            flag(s.nell_alive), flag(s.abel_alive), flag(s.lead_alive), s.cutters_alive,
            cargo if s.cargo == "intact" else 0,
            in_town["master"] if s.done(40) else 0, in_town["drover"] if s.done(40) else 0,
            4 if s.done(40) else 0, flag(s.has_dispatch),
            flag(s.in_combat) if act in COMBAT_EVENTS else SKIP))
        lines.append("\tcaseDriver.ExpectMetrics(%d, %d, %d, %d)" % (s.truth, s.competence, s.accountability, s.mutual_trust))
        lines.append("\tcaseDriver.ExpectSide(\"%s\", %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d)" % (
            stage_text(set(s.sq_stages) | extra_sq, SQ_STAGES), s.evidence_count, s.evidence_level, s.sq_outcome,
            s.yard_alerted, s.vane_has_ledger, s.haskell_scapegoated, s.sq_o10, s.sq_o20,
            flag(s.has_ledger), flag(s.has_journal), HASKELL_CODE[s.haskell], price if s.sold_for_caps else 0))
    for st in set(s.stages) | extra_mq:
        if st not in MQ_STAGES:
            raise Bad("%s: stage %d of the main quest is not one the driver looks at" % (name, st))
    for st in set(s.sq_stages) | extra_sq:
        if st not in SQ_STAGES:
            raise Bad("%s: stage %d of the side quest is not one the driver looks at" % (name, st))
    full_title = "%s: %s" % (", ".join(rows), title)
    head = [
        "Function Case%d(TLM:SelfTest akTest)" % number,
        "\t{%s." % full_title,
        "\tIn the logic model: %s.}" % ", ".join(listed),
        "\tTLM:CaseDriver caseDriver = (Self as Quest) as TLM:CaseDriver",
        "\tIf !caseDriver",
        "\t\takTest.Fail(\"%s: the case driver script is not attached to this quest\")" % name,
        "\t\tReturn",
        "\tEndIf",
        "\tIf !caseDriver.CaseBegin(akTest, \"%s\", \"%s\")" % (name, full_title),
        "\t\tReturn",
        "\tEndIf",
    ]
    tail = ["\tcaseDriver.CaseEnd()", "EndFunction"]
    info = {"scenario": number, "rows": rows, "title": title, "steps": listed, "checks": 4 * len(case_steps)}
    return head + lines + tail, info


HEADER = """Scriptname TLM:MatrixCases extends Quest
{GENERATED by tools/gen_matrix_cases.py from the logic model. DO NOT EDIT:
change the model or the generator and run it again. tools/run_checks.sh fails
if this file is stale.

Development only, attached to TLM_Core. It must be removed before any release.

Self-test scenarios 101 and up: the rows of the two test matrices, each as a
list of the logic model's events. After every event TLM:CaseDriver compares
what it can see of both quests with what the model predicts. What each
action in the game stands for, and what a pass does and does not say, is in
TLM:CaseDriver. Rows that cannot be played this way are listed in the
generator with the reason.

First compiled and run in the game on 2026-11-12. docs/design/VERIFY_LOG.md
says which cases have passed in the game and at which commit; a case added
since then has only run in the stand-in engine (tools/papyrus_sim), which is
not the game.}
"""


def generate():
    price, cargo = sale_price(), cargo_count()
    out = [HEADER.rstrip("\n"), ""]
    out.append("Function RunCase(int aiCase, TLM:SelfTest akTest)")
    out.append("\t{Runs the case with this scenario number.}")
    infos, bodies = [], []
    seen = set()
    for i, (number, rows, title, case_steps) in enumerate(CASES):
        if number in seen:
            raise Bad("scenario %d is listed twice" % number)
        seen.add(number)
        body, info = build_case(number, rows, title, case_steps, price, cargo)
        bodies.append(body)
        infos.append(info)
        out.append("\t%s aiCase == %d" % ("If" if i == 0 else "ElseIf", number))
        out.append("\t\tCase%d(akTest)" % number)
    out.append("\tElse")
    out.append("\t\takTest.Fail(\"there is no scenario \" + aiCase)")
    out.append("\tEndIf")
    out.append("EndFunction")
    for body in bodies:
        out.append("")
        out.extend(body)
    psc = "\n".join(out) + "\n"
    data = {
        "_note": "GENERATED by tools/gen_matrix_cases.py. The in-game cases of the test matrix: scenario number, the matrix rows each stands for, and the logic model's events it plays.",
        "cases": infos,
        "not_run": NOT_RUN,
        "attempts_left_out": DIALOGUE_GUARDED,
    }
    return psc, json.dumps(data, indent=1) + "\n"


def main():
    check = "--check" in sys.argv[1:]
    try:
        psc, data = generate()
    except Bad as e:
        print("gen_matrix_cases: " + str(e))
        return 1
    stale = []
    for path, text in ((OUT_PSC, psc), (OUT_JSON, data)):
        current = path.read_text() if path.exists() else None
        if current != text:
            stale.append(path)
            if not check:
                path.write_text(text)
    if check and stale:
        print("STALE: %s. Run:  python3 tools/gen_matrix_cases.py" % ", ".join(str(p.relative_to(ROOT)) for p in stale))
        return 1
    cases = json.loads(data)["cases"]
    print("matrix cases: %d (%d steps, %d checks)%s" % (
        len(cases), sum(len(c["steps"]) for c in cases), sum(c["checks"] for c in cases),
        "" if check else "; wrote %d file(s)" % len(stale)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
