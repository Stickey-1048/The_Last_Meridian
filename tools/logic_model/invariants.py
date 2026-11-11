"""Invariants for the TLM_MQ01 / TLM_SQ01 logic model.

Each check returns a list of human-readable violation strings (empty = holds).
The same checks run against the amended rules (V02, must be clean) and the
v0.1 draft rules (V01, expected to fail in specific, documented ways).
"""
from __future__ import annotations

from dataclasses import fields
from typing import Dict, Iterable, List, Set, Tuple

import tlm_model as m
from tlm_model import State

METRIC_FIELDS = ("truth", "competence", "accountability", "mutual_trust")

SQ_FIELDS = (
    "sq_running", "sq_stages", "e1", "e2", "e3", "e4", "has_ledger", "ledger_lost",
    "has_journal", "journal_sold", "sq_outcome", "sq_o10", "sq_o20", "haskell",
    "pike_alive", "vane_alive", "yard_alerted", "vane_has_ledger",
    "haskell_scapegoated", "sold_for_caps",
)
MQ_FIELDS = tuple(
    f.name for f in fields(State) if f.name not in SQ_FIELDS and f.name not in METRIC_FIELDS
)


def derive_caravan_state(stages: Iterable[int], outcome: int) -> int:
    """MQ01 section 12: CaravanState must be re-derivable after any load
    from the stage list and TLM_G_CaravanOutcome alone."""
    stages = set(stages)
    if 10 not in stages:
        return m.DORMANT
    if outcome != m.OUT_NONE:
        return m.RESOLVED
    if 30 in stages:
        return m.LIVE
    return m.ARMED


def mq01_metric_expectation(s: State) -> Tuple[int, int, int, int]:
    """(truth, competence, accountability, mutual_trust) owed to MQ01 choices.
    MQ01 section 9.2."""
    truth = acc = trust = 0
    if s.debrief_answer in ("admit", "confess"):
        truth, acc = 1, 1
    elif s.debrief_answer in ("deny", "blame"):
        truth = -1
    if s.debrief_variant == m.V_WITNESS and s.debrief_answer == "deny":
        trust -= 1
    if s.done(50) and s.debrief_variant == m.V_SAVED:
        trust += 1
    return truth, 0, acc, trust


def sq01_metric_expectation(s: State) -> Tuple[int, int, int, int]:
    """SQ01 section 7."""
    return {
        m.SQ_NONE: (0, 0, 0, 0),
        m.SQ_REPORTED: (1, 1, 0, 0),
        m.SQ_POSTED: (1, 0, 0, 0),
        m.SQ_POSTED_YARD: (1, 1, 0, 1),
        m.SQ_POSTED_HASKELL: (-1, -1, -1, -1),
        m.SQ_SOLD: (0, 0, 0, 0),
        m.SQ_DESTROYED: (-1, 0, 0, 0),
    }[s.sq_outcome]


def check_mq01_state(s: State) -> List[str]:
    v: List[str] = []

    def bad(msg: str) -> None:
        v.append(msg)

    if s.outcome not in (0, 1, 2, 3, 4):
        bad("outcome out of range")
    if (s.outcome == m.OUT_EXPLOITED) != (s.method != m.METHOD_NONE):
        bad("method set without Exploited outcome (or the reverse)")
    if derive_caravan_state(s.stages, s.outcome) != s.caravan_state:
        bad("CaravanState is not derivable from stages + outcome global")
    for outcome, stage in ((1, 31), (2, 32), (4, 34)):
        if s.outcome == outcome and not s.done(stage):
            bad("outcome %d without stage %d" % (outcome, stage))
    if s.method == m.METHOD_DEAL and not s.done(33):
        bad("deal recorded without stage 33")
    if s.method == m.METHOD_BETRAYAL and not s.done(35):
        bad("betrayal recorded without stage 35")
    if s.done(35) and not s.hands_killed_by_player:
        bad("stage 35 without the player killing a caravan hand")
    for stage in (31, 32, 33, 35):
        if s.done(stage) and not s.done(30):
            bad("stage %d set before stage 30" % stage)
    if s.done(50):
        if s.outcome == m.OUT_NONE:
            bad("stage 50 reached with no caravan outcome (Pritchard has no line)")
        if s.debrief_variant is None:
            bad("stage 50 reached with no debrief variant")
        if not s.done(20):
            bad("stage 50 without stage 20")
        if not s.done(40):
            bad("stage 50 without stage 40 (town failsafe never ran)")
        if not s.dispatch_delivered or s.has_dispatch:
            bad("stage 50 but the dispatch was not handed over")
        if s.rep != m.reputation_delta(s.outcome, s.witness_alive):
            bad("reputation does not match section 9.1")
        if s.alive_at_mercy != (1 if s.nell_alive else 0):
            bad("CaravanAliveAtMercy disagrees with Nell being alive")
        if s.hands_killed_by_player and s.outcome != m.OUT_EXPLOITED:
            bad("player killed a caravan hand but the outcome is not Exploited")
        if s.debrief_variant == m.V_NOWITNESS and s.witness_alive:
            bad("'no witness' line used while a caravan hand is alive")
        if s.debrief_variant == m.V_WITNESS and not s.witness_alive:
            bad("'witness' line used with no caravan hand alive")
    else:
        if s.rep != 0:
            bad("reputation changed before stage 50")
        if s.debrief_answer is not None:
            bad("debrief answered before stage 50")
    if not 0 <= s.rep <= 2:
        bad("reputation outside 0..2")
    if s.done(60) != s.done(100) or s.done(100) != bool(s.mq01_done):
        bad("stages 60 / 100 / TLM_G_MQ01_Done disagree")
    if s.done(60) and not s.done(50):
        bad("stage 60 without stage 50")
    if (s.o10 == m.COMPLETE) != s.done(20):
        bad("objective O10 completion disagrees with stage 20")
    if (s.o20 == m.HIDDEN) != (not s.done(20)):
        bad("objective O20 shown without the dispatch (or hidden with it)")
    if (s.o20 == m.COMPLETE) != s.done(50):
        bad("objective O20 completion disagrees with stage 50")
    if s.has_dispatch and (not s.done(20) or s.dispatch_delivered or s.dispatch_lost):
        bad("dispatch possession is inconsistent")
    if s.debrief_answer not in (None, "silent") and s.debrief_answer not in m.DEBRIEF_CHOICES.get(
        s.debrief_variant or "", ()
    ):
        bad("debrief answer %r is not offered for variant %r" % (s.debrief_answer, s.debrief_variant))
    if s.reward_taken and not s.done(31):
        bad("Nell's reward given without the caravan ever being saved")
    return v


def check_sq01_state(s: State) -> List[str]:
    v: List[str] = []

    def bad(msg: str) -> None:
        v.append(msg)

    decided = s.sq_outcome != m.SQ_NONE
    if decided != s.sq_done(50) or decided != s.sq_done(100):
        bad("SQ01 outcome and stages 50/100 disagree")
    if s.sq_done(20) and not (s.sq_done(10) and s.evidence_level >= 1):
        bad("SQ01 stage 20 without the ledger and one piece of evidence")
    if s.sq_done(10) and s.evidence_level >= 1 and not decided and not s.sq_done(20):
        bad("evidence level >= 1 with the ledger found, but stage 20 was never set")
    if s.sq_done(25) and s.evidence_level < 2:
        bad("SQ01 stage 25 below evidence level 2")
    if s.sq_done(10) and s.evidence_level >= 2 and not decided and not s.sq_done(25):
        bad("evidence level 2 with the ledger found, but stage 25 was never set")
    if (s.haskell == "gone") != (s.sq_outcome == m.SQ_POSTED_HASKELL):
        bad("Haskell removed without the scapegoat outcome (or the reverse)")
    if bool(s.haskell_scapegoated) != (s.sq_outcome == m.SQ_POSTED_HASKELL):
        bad("HaskellScapegoated flag disagrees with the outcome")
    if bool(s.vane_has_ledger) != (s.sq_outcome == m.SQ_SOLD):
        bad("VaneHasLedger flag disagrees with the outcome")
    if bool(s.yard_alerted) != (s.sq_outcome == m.SQ_REPORTED):
        bad("YardAlerted flag disagrees with the outcome")
    if s.sq_outcome == m.SQ_POSTED_YARD and s.evidence_level < 2:
        bad("Yard Office named below evidence level 2")
    if s.has_ledger and not s.sq_done(10):
        bad("ledger held but SQ01 stage 10 not set")
    if s.has_ledger and s.sq_outcome in (m.SQ_SOLD, m.SQ_DESTROYED):
        bad("ledger still held after being sold or destroyed")
    if (s.sq_o20 == m.COMPLETE) != decided:
        bad("SQ01 objective O20 completion disagrees with the outcome")
    if s.sq_o20 != m.HIDDEN and not s.sq_done(10):
        bad("SQ01 objective O20 shown before the ledger was found")
    return v


def check_metrics(s: State) -> List[str]:
    a = mq01_metric_expectation(s)
    b = sq01_metric_expectation(s)
    want = tuple(x + y for x, y in zip(a, b))
    got = (s.truth, s.competence, s.accountability, s.mutual_trust)
    if want != got:
        return ["hidden metrics %r do not match the tables (expected %r)" % (got, want)]
    return []


def check_state(s: State) -> List[str]:
    return check_mq01_state(s) + check_sq01_state(s) + check_metrics(s)


def check_edges(graph: Dict[State, List[Tuple[str, State]]]) -> List[str]:
    """Checks that depend on the transition, not just the state."""
    v: Set[str] = set()
    for s, edges in graph.items():
        for name, t in edges:
            if name == "npc_kills_lead" and t.outcome == m.OUT_SAVED and s.outcome != m.OUT_SAVED:
                v.add("caravan 'saved' by an NPC kill with no player action")
            if name == "evade_timer" and s.in_combat and t.outcome == m.OUT_EVADED:
                v.add("evade timer resolved Evaded while the player was in combat")
            if s.done(50) and (t.outcome != s.outcome or t.rep != s.rep or t.method != s.method):
                v.add("caravan outcome or reputation changed after the debrief")
            if s.sq_outcome != m.SQ_NONE and t.sq_outcome != s.sq_outcome:
                v.add("SQ01 outcome changed after it was decided")
            if t.evidence_level < s.evidence_level:
                v.add("SQ01 evidence level went down")
    return sorted(v)


def cannot_reach(
    graph: Dict[State, List[Tuple[str, State]]],
    goal,
    only_events: Iterable[str] = None,
) -> List[State]:
    """States from which no path reaches a state satisfying goal(state).
    With only_events set, paths may use just those events."""
    allowed = set(only_events) if only_events is not None else None
    rev: Dict[State, List[State]] = {}
    for s, edges in graph.items():
        for name, t in edges:
            if allowed is None or name in allowed:
                rev.setdefault(t, []).append(s)
    ok = {s for s in graph if goal(s)}
    stack = list(ok)
    while stack:
        t = stack.pop()
        for s in rev.get(t, ()):
            if s not in ok:
                ok.add(s)
                stack.append(s)
    return [s for s in graph if s not in ok]


def collect(graph: Dict[State, List[Tuple[str, State]]]) -> Dict[str, int]:
    """Violation message -> number of reachable states showing it."""
    out: Dict[str, int] = {}
    for s in graph:
        for msg in check_state(s):
            out[msg] = out.get(msg, 0) + 1
    for msg in check_edges(graph):
        out[msg] = out.get(msg, 0) + 1
    return out
