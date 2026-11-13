"""Executable model of the TLM_MQ01 / TLM_SQ01 quest logic.

WHAT THIS IS
    A small, deterministic state machine that encodes the *rules* in
    docs/design/TLM_MQ01_six-rounds-to-mercy.md and TLM_SQ01_signed-clean.md
    (stages, globals, outcomes, reputation, hidden metrics, recovery).
    It lets the stage table be tested and exhaustively explored without the
    game, so logic holes are found before any Creation Kit work.

WHAT THIS IS NOT
    It is not Fallout 4. It says nothing about AI, navmesh, packages, timing,
    dialogue presentation, or whether a Papyrus call behaves as documented.
    In particular it has no time in it: an event is over before the next
    begins. The game announces a death late and runs handlers side by side;
    what the quest script does about that is amendment A24, and is tested in
    tools/papyrus_sim/test_overlap.py, not here.
    A green run here means "the design is internally consistent", not
    "the mod works". In-game cases T01-T28 / S01-S17 still have to be run.

RULE SETS
    V02 is the amended design (docs/design/DESIGN_AMENDMENTS_v0.2.md).
    V01 reproduces the v0.1 draft where it differed, so the tests can show
    which v0.1 rules break an invariant.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Dict, FrozenSet, Iterable, List, Optional, Tuple

# --------------------------------------------------------------------------
# Rule switches
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Rules:
    # A1: Cutters are Protected until the encounter resolves, so only the
    #     player can kill them (v0.1: an NPC kill could "save" the caravan).
    cutters_protected: bool = True
    # A2: the evade timer never resolves while the player is in combat.
    evade_blocked_in_combat: bool = True
    # A3: the player killing a caravan hand before the debrief always
    #     converts the outcome to Exploited/Betrayal (v0.1: ignored after
    #     the first resolution).
    betrayal_overrides: bool = True
    # A4: an unresolved encounter is force-resolved when the player reaches
    #     town (never met -> Missed, walked away mid-fight -> Evaded).
    resolve_unresolved_at_town: bool = True
    # A5: the Pritchard conversation can be resumed after stage 50.
    debrief_resumable: bool = True
    # A6: outcome-based metric and reputation effects are applied once, at
    #     the debrief, from the final state (v0.1: MutualTrust at the save).
    effects_at_debrief: bool = True
    # A7: stage 50 forces stage 40 if the gate trigger was bypassed.
    stage50_forces_40: bool = True
    # A8: SQ01 runs (silently) from MQ01 stage 10 so clue scripts are live
    #     before the ledger is found.
    sq01_runs_from_start: bool = True
    # A9: Pritchard's greeting is keyed on stage 20, not on holding the item.
    #     If the dispatch is missing the hand-over repairs it first.
    handover_keyed_on_stage: bool = True
    # A10: caravan hands become Essential once they are in town, so the
    #      "no witness" line can only follow a killing on the road.
    hands_essential_in_town: bool = True
    # A25 (owner decision D9, 2026-11-13): the evade timer never resolves
    #      while the hold-up conversation with the Cutter lead is open
    #      (v0.1: it kept running, and a deal taken after it ran out was
    #      silently refused).
    evade_blocked_in_conversation: bool = True


V02 = Rules()
V01 = Rules(
    cutters_protected=False,
    evade_blocked_in_combat=False,
    betrayal_overrides=False,
    resolve_unresolved_at_town=False,
    debrief_resumable=False,
    effects_at_debrief=False,
    stage50_forces_40=False,
    sq01_runs_from_start=False,
    handover_keyed_on_stage=False,
    hands_essential_in_town=False,
    evade_blocked_in_conversation=False,
)

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

# TLM_G_CaravanOutcome
OUT_NONE, OUT_SAVED, OUT_EVADED, OUT_EXPLOITED, OUT_MISSED = 0, 1, 2, 3, 4
# TLM_G_CaravanMethod
METHOD_NONE, METHOD_DEAL, METHOD_BETRAYAL = 0, 1, 2
# CaravanState (derived cache in the quest script)
DORMANT, ARMED, LIVE, RESOLVED = 0, 1, 2, 3
# Objective display state
HIDDEN, SHOWN, COMPLETE = 0, 1, 2
# Player location (abstract)
WRECK, AMBUSH, TOWN = "wreck", "ambush", "town"

# Pritchard debrief variants (TLM_G_MQ01_DebriefVariant)
V_SAVED = "saved"            # outcome 1, Nell alive
V_EVADED = "evaded"          # outcome 2, Nell alive       -> admit / deny / silent
V_WITNESS = "witness"        # outcome 3, a hand is alive  -> confess / blame / deny
V_NOWITNESS = "no_witness"   # outcome 3, both hands dead
V_MISSED = "missed"          # outcome 4, Nell alive (player never met the ambush)
V_LOST = "lost"              # outcome 1/2/4 but Nell died by a non-player cause

DEBRIEF_CHOICES = {
    V_EVADED: ("admit", "deny"),
    V_WITNESS: ("confess", "blame", "deny"),
}

# TLM_G_SQ01_Outcome
SQ_NONE, SQ_REPORTED, SQ_POSTED, SQ_POSTED_YARD, SQ_POSTED_HASKELL, SQ_SOLD, SQ_DESTROYED = range(7)

# --------------------------------------------------------------------------
# State
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class State:
    # ---- MQ01: persisted truth (stages + globals) ----
    stages: FrozenSet[int] = frozenset()
    outcome: int = OUT_NONE
    method: int = METHOD_NONE
    alive_at_mercy: int = 0
    rep: int = 0
    mq01_done: int = 0
    truth: int = 0
    competence: int = 0
    accountability: int = 0
    mutual_trust: int = 0
    o10: int = HIDDEN
    o20: int = HIDDEN
    # ---- MQ01: world ----
    loc: str = WRECK
    caravan_state: int = DORMANT
    in_combat: bool = False            # player currently in combat with Cutters
    talking: bool = False              # the hold-up conversation with the Cutter lead is open
    lead_alive: bool = True
    cutters_alive: int = 3             # the three unnamed Cutters
    cutters_gone: bool = False         # withdrew / disabled after resolution
    nell_alive: bool = True
    abel_alive: bool = True
    hands_killed_by_player: int = 0
    hands_in_town: bool = False
    cargo: str = "intact"              # intact | looted | split
    has_dispatch: bool = False
    dispatch_delivered: bool = False
    dispatch_lost: bool = False        # engine failure: the item exists nowhere
    has_revolver: bool = False
    reward_taken: bool = False
    debrief_variant: Optional[str] = None
    debrief_answer: Optional[str] = None   # None | admit | deny | confess | blame | silent
    # ---- SQ01 ----
    sq_running: bool = False
    sq_stages: FrozenSet[int] = frozenset()
    e1: bool = False
    e2: bool = False
    e3: bool = False
    e4: bool = False
    has_ledger: bool = False
    ledger_lost: bool = False
    has_journal: bool = False
    journal_sold: bool = False
    sq_outcome: int = SQ_NONE
    sq_o10: int = HIDDEN
    sq_o20: int = HIDDEN
    haskell: str = "present"           # present | gone | dead
    pike_alive: bool = True
    vane_alive: bool = True
    yard_alerted: int = 0
    vane_has_ledger: int = 0
    haskell_scapegoated: int = 0
    sold_for_caps: bool = False

    # ---- derived helpers ----
    def done(self, stage: int) -> bool:
        return stage in self.stages

    def sq_done(self, stage: int) -> bool:
        return stage in self.sq_stages

    @property
    def evidence_count(self) -> int:
        return sum((self.e1, self.e2, self.e3, self.e4))

    @property
    def evidence_level(self) -> int:
        return evidence_level(self.e1, self.e2, self.e3, self.e4)

    @property
    def witness_alive(self) -> bool:
        return self.nell_alive or self.abel_alive


def evidence_level(e1: bool, e2: bool, e3: bool, e4: bool) -> int:
    """SQ01 section 3.2. Level 2 = falsification established (author is not)."""
    n = sum((e1, e2, e3, e4))
    if n == 0:
        return 0
    if (e3 and n >= 2) or (e1 and e2 and e4):
        return 2
    return 1


def set_stage(s: State, stage: int) -> State:
    return replace(s, stages=s.stages | {stage})


def sq_set_stage(s: State, stage: int) -> State:
    return replace(s, sq_stages=s.sq_stages | {stage})


# --------------------------------------------------------------------------
# MQ01 internals (mirror the Papyrus function names in TLM_MQ01_QuestScript)
# --------------------------------------------------------------------------


def _enter_live(s: State) -> State:
    if s.caravan_state != ARMED or not s.done(10):
        return s
    return replace(set_stage(s, 30), caravan_state=LIVE)


def _resolve_saved(s: State) -> State:
    if s.caravan_state != LIVE:
        return s
    s = replace(
        set_stage(s, 31),
        caravan_state=RESOLVED,
        outcome=OUT_SAVED,
        in_combat=False,
        cutters_gone=True,
    )
    return s


def _resolve_evaded(s: State) -> State:
    if s.caravan_state != LIVE:
        return s
    return replace(
        set_stage(s, 32),
        caravan_state=RESOLVED,
        outcome=OUT_EVADED,
        in_combat=False,
        abel_alive=False,          # killed by the Cutters (scripted)
        cargo="looted",
        cutters_gone=True,
    )


def _resolve_missed(s: State) -> State:
    """A4: the player reached town without ever meeting the ambush."""
    if s.caravan_state != ARMED:
        return s
    return replace(
        set_stage(s, 34),
        caravan_state=RESOLVED,
        outcome=OUT_MISSED,
        abel_alive=False,
        cargo="looted",
        cutters_gone=True,
    )


def _resolve_deal(s: State) -> State:
    if s.caravan_state != LIVE:
        return s
    return replace(
        set_stage(s, 33),
        caravan_state=RESOLVED,
        outcome=OUT_EXPLOITED,
        method=METHOD_DEAL,
        in_combat=False,
        abel_alive=False,          # "The drover won't be a problem."
        cargo="split",
        cutters_gone=True,
    )


def _player_killed_hand(s: State, rules: Rules) -> State:
    """P5: a caravan hand died and the player is the killer."""
    s = replace(s, hands_killed_by_player=s.hands_killed_by_player + 1)
    if s.done(50):
        return s                    # after the debrief the outcome is frozen
    if s.caravan_state == ARMED:
        s = _enter_live(s)
    if s.caravan_state == LIVE:
        # First resolution: Exploited / Betrayal (stage 35).
        s = replace(
            set_stage(s, 35),
            caravan_state=RESOLVED,
            outcome=OUT_EXPLOITED,
            method=METHOD_BETRAYAL,
            in_combat=False,
            cargo="looted",
            cutters_gone=True,
        )
        if not s.nell_alive and s.abel_alive:
            # Nell dead, wagon overrun: the Cutters finish the drover.
            s = replace(s, abel_alive=False)
        return s
    if s.caravan_state == RESOLVED and rules.betrayal_overrides:
        return replace(set_stage(s, 35), outcome=OUT_EXPLOITED, method=METHOD_BETRAYAL)
    return s


def _debrief_variant(s: State) -> str:
    if s.outcome == OUT_EXPLOITED:
        return V_WITNESS if s.witness_alive else V_NOWITNESS
    if not s.nell_alive:
        return V_LOST
    if s.outcome == OUT_SAVED:
        return V_SAVED
    if s.outcome == OUT_EVADED:
        return V_EVADED
    if s.outcome == OUT_MISSED:
        return V_MISSED
    raise ValueError("no Pritchard variant for outcome %r" % s.outcome)


def reputation_delta(outcome: int, witness_alive: bool) -> int:
    """MQ01 section 9.1, applied once at stage 50."""
    d = 1                                   # dispatch delivered
    if outcome == OUT_SAVED:
        d += 1
    if outcome == OUT_EXPLOITED and witness_alive:
        d -= 1
    return d


# --------------------------------------------------------------------------
# MQ01 events. Each returns the new State, or None when the action is not
# available in this state (the guard is part of the specification).
# --------------------------------------------------------------------------

Event = Callable[[State, Rules], Optional[State]]


def ev_start(s: State, r: Rules) -> Optional[State]:
    """Stage 10: TLM_Core or the dev console starts the quest."""
    if s.done(10):
        return None
    s = replace(set_stage(s, 10), caravan_state=ARMED, o10=SHOWN, loc=WRECK)
    if r.sq01_runs_from_start:
        s = replace(sq_set_stage(s, 5), sq_running=True)
    return s


def ev_take_revolver(s: State, r: Rules) -> Optional[State]:
    if not s.done(10) or s.has_revolver or s.loc != WRECK:
        return None
    return replace(set_stage(s, 15), has_revolver=True)


def ev_take_dispatch(s: State, r: Rules) -> Optional[State]:
    if not s.done(10) or s.has_dispatch or s.dispatch_delivered or s.dispatch_lost or s.loc != WRECK:
        return None
    s = replace(set_stage(s, 20), has_dispatch=True, o10=COMPLETE)
    if s.o20 == HIDDEN:
        s = replace(s, o20=SHOWN)
    return s


def ev_goto_wreck(s: State, r: Rules) -> Optional[State]:
    if not s.done(10) or s.loc == WRECK:
        return None
    return _leave(s, r, WRECK)


def ev_goto_ambush(s: State, r: Rules) -> Optional[State]:
    """Player walks into TLM_TRIG_AmbushSight."""
    if not s.done(10) or s.loc == AMBUSH:
        return None
    s = replace(s, loc=AMBUSH)
    return _enter_live(s)


def ev_goto_town(s: State, r: Rules) -> Optional[State]:
    """Player crosses TLM_TRIG_TownGate (stage 40)."""
    if not s.done(10) or s.loc == TOWN:
        return None
    s = _leave(s, r, TOWN)
    return _stage40(s, r)


def ev_goto_town_bypass_gate(s: State, r: Rules) -> Optional[State]:
    """Player gets into town without touching the gate trigger."""
    if not s.done(10) or s.loc == TOWN or s.done(40):
        return None
    return _leave(s, r, TOWN)


def _leave(s: State, r: Rules, dest: str) -> State:
    """Moving away from the ambush while it is LIVE is the distance rule."""
    if s.loc == AMBUSH and s.caravan_state == LIVE:
        s = _resolve_evaded(replace(s, in_combat=False))
    return replace(s, loc=dest, in_combat=False)


def _stage40(s: State, r: Rules) -> State:
    if s.done(40):
        return s
    s = set_stage(s, 40)
    if r.resolve_unresolved_at_town:
        if s.caravan_state == ARMED:
            s = _resolve_missed(s)
        elif s.caravan_state == LIVE:
            s = _resolve_evaded(s)
    if s.nell_alive or s.abel_alive:
        s = replace(s, hands_in_town=True)       # failsafe move to TLM_MARK_CaravanYard
    return replace(s, alive_at_mercy=1 if s.nell_alive else 0)


def ev_evade_timer(s: State, r: Rules) -> Optional[State]:
    """OnTimer(TIMER_EVADE) while LIVE."""
    if s.caravan_state != LIVE:
        return None
    if r.evade_blocked_in_combat and s.in_combat:
        return None                              # timer restarts; no change
    if r.evade_blocked_in_conversation and s.talking:
        return None                              # A25: the same while he is being talked to
    return _resolve_evaded(s)


def ev_attack_cutter(s: State, r: Rules) -> Optional[State]:
    """Player hits a Cutter (hostile act)."""
    if s.loc != AMBUSH or s.caravan_state not in (ARMED, LIVE) or s.cutters_gone:
        return None
    if not (s.lead_alive or s.cutters_alive):
        return None
    s = _enter_live(s)
    if s.in_combat:
        return None
    return replace(s, in_combat=True)


def ev_break_combat(s: State, r: Rules) -> Optional[State]:
    """Player hides / combat ends without leaving the area."""
    if not s.in_combat:
        return None
    return replace(s, in_combat=False)


def _cutter_down(s: State, lead: bool) -> State:
    s = _enter_live(s)
    if lead:
        s = replace(s, lead_alive=False)
    else:
        s = replace(s, cutters_alive=s.cutters_alive - 1)
    # "All Cutters dead OR lead dead": every "all dead" case includes the lead,
    # so the lead's death is the whole condition. Killing only the three
    # unnamed Cutters leaves the encounter LIVE.
    if s.caravan_state == LIVE and not s.lead_alive:
        s = _resolve_saved(s)
    return s


def ev_player_kills_lead(s: State, r: Rules) -> Optional[State]:
    if s.loc != AMBUSH or not s.lead_alive or s.cutters_gone or s.caravan_state not in (ARMED, LIVE):
        return None
    return _cutter_down(replace(s, in_combat=True), lead=True)


def ev_player_kills_cutter(s: State, r: Rules) -> Optional[State]:
    if s.loc != AMBUSH or s.cutters_alive == 0 or s.cutters_gone or s.caravan_state not in (ARMED, LIVE):
        return None
    return _cutter_down(replace(s, in_combat=True), lead=False)


def ev_npc_kills_lead(s: State, r: Rules) -> Optional[State]:
    """The caravan hands kill Dunmore with no help from the player."""
    if r.cutters_protected:
        return None                              # Protected: only the player can
    if not s.lead_alive or s.cutters_gone or s.caravan_state not in (ARMED, LIVE):
        return None
    return _cutter_down(s, lead=True)


def _dunmore_available(s: State) -> bool:
    return (
        s.loc == AMBUSH
        and s.caravan_state == LIVE
        and s.lead_alive
        and not s.in_combat
        and not s.cutters_gone
    )


def ev_dunmore_talk(s: State, r: Rules) -> Optional[State]:
    """The hold-up conversation opens and no line has been chosen yet (A25).

    The four lines below can also be taken in one step from a state where
    the conversation is not open: that stands for opening it and choosing
    at once, which is how the matrix rows written before A25 read."""
    if not _dunmore_available(s) or s.talking:
        return None
    return replace(s, talking=True)


def ev_walk_away_from_dunmore(s: State, r: Rules) -> Optional[State]:
    """The conversation is left without a line being chosen. Nothing else
    changes; the ambush is as live as it was."""
    if not s.talking:
        return None
    return replace(s, talking=False)


def _conversation_closes(ev: "Event") -> "Event":
    """The conversation cannot outlast what it needs. Whatever else an event
    does, the conversation is over once the Cutter lead cannot be talked to:
    a line was chosen, a fight began, he died, the player left, or the
    ambush was resolved some other way."""
    def settled(s: State, r: Rules) -> Optional[State]:
        t = ev(s, r)
        if t is not None and t.talking and not _dunmore_available(t):
            t = replace(t, talking=False)
        return t
    settled.__name__ = getattr(ev, "__name__", "event")
    settled.__doc__ = ev.__doc__
    return settled


def ev_dunmore_speech_success(s: State, r: Rules) -> Optional[State]:
    if not _dunmore_available(s):
        return None
    return _resolve_saved(s)                     # Cutters break


def ev_dunmore_speech_fail(s: State, r: Rules) -> Optional[State]:
    if not _dunmore_available(s):
        return None
    return replace(s, in_combat=True)


def ev_dunmore_deal(s: State, r: Rules) -> Optional[State]:
    if not _dunmore_available(s):
        return None
    return _resolve_deal(s)


def ev_dunmore_refuse(s: State, r: Rules) -> Optional[State]:
    if not _dunmore_available(s):
        return None
    return replace(s, in_combat=True)


def _hand_reachable(s: State, r: Rules) -> bool:
    """The player can kill a living caravan hand."""
    if s.done(50) or not s.done(10):
        return False
    if s.loc == AMBUSH and not s.hands_in_town:
        return True
    if r.hands_essential_in_town:
        return False                             # A10: Essential in town
    return s.loc == TOWN and s.hands_in_town


def ev_player_kills_nell(s: State, r: Rules) -> Optional[State]:
    if not s.nell_alive or not _hand_reachable(s, r):
        return None
    return _player_killed_hand(replace(s, nell_alive=False), r)


def ev_player_kills_abel(s: State, r: Rules) -> Optional[State]:
    if not s.abel_alive or not _hand_reachable(s, r):
        return None
    return _player_killed_hand(replace(s, abel_alive=False), r)


def ev_nell_dies_other(s: State, r: Rules) -> Optional[State]:
    """Engine edge (T21): Nell dies with no player killer, e.g. console kill."""
    if not s.nell_alive or not s.done(10) or s.done(50):
        return None
    return replace(s, nell_alive=False)


def ev_nell_reward(s: State, r: Rules) -> Optional[State]:
    """Nell's one-time reward topic (Saved only)."""
    if s.outcome != OUT_SAVED or not s.nell_alive or s.reward_taken:
        return None
    if not ((s.loc == AMBUSH and not s.hands_in_town) or (s.loc == TOWN and s.hands_in_town)):
        return None
    s = replace(s, reward_taken=True)
    if not r.effects_at_debrief:
        s = replace(s, mutual_trust=s.mutual_trust + 1)   # v0.1: "+1 on first thanks"
    return s


def ev_dispatch_vanishes(s: State, r: Rules) -> Optional[State]:
    """Engine failure the Quest Object flag should prevent (T19)."""
    if not s.has_dispatch or s.dispatch_delivered:
        return None
    return replace(s, has_dispatch=False, dispatch_lost=True)


def ev_recovery(s: State, r: Rules) -> Optional[State]:
    """Stage 900. Restores only what the player already earned."""
    changed = False
    if s.dispatch_lost and s.done(20) and not s.dispatch_delivered:
        s = replace(s, has_dispatch=True, dispatch_lost=False)
        changed = True
    if s.ledger_lost and s.sq_done(10) and s.sq_outcome == SQ_NONE:
        s = replace(s, has_ledger=True, ledger_lost=False)
        changed = True
    if not changed:
        return None
    return set_stage(s, 900)


def ev_pritchard_no_dispatch(s: State, r: Rules) -> Optional[State]:
    """Branch B: sends the player back. No stage change, no fail state."""
    if s.loc != TOWN or not s.done(10) or s.done(50):
        return None
    if r.handover_keyed_on_stage:
        if s.done(20):
            return None                          # greeting A applies instead
    elif s.has_dispatch:
        return None
    if s.o10 == SHOWN:
        return s                                 # already displayed; nothing changes
    # v0.1 only: stage 20 is done but the item is gone, so O10 is re-opened
    # even though it was completed.
    return replace(s, o10=SHOWN)


def ev_pritchard_handover(s: State, r: Rules) -> Optional[State]:
    """Node P1: hands over the dispatch (stage 50)."""
    if s.loc != TOWN or s.done(50):
        return None
    if r.handover_keyed_on_stage:
        if not s.done(20):
            return None
        if not s.has_dispatch:
            # A9: the hand-over is keyed on stage 20. If the item has gone
            # missing the delivery stands: nothing is given back first and
            # stage 900 is not involved (TLM:MQ01Quest.ApplyDelivered).
            s = replace(s, dispatch_lost=False)
    elif not s.has_dispatch:
        return None
    if not s.done(40):
        if r.stage50_forces_40:
            s = _stage40(s, r)
    if s.outcome == OUT_NONE:
        # v0.1 hole: stage 50 with no outcome has no Pritchard line.
        variant = None
    else:
        variant = _debrief_variant(s)
    s = replace(
        set_stage(s, 50),
        has_dispatch=False,
        dispatch_delivered=True,
        o20=COMPLETE,
        debrief_variant=variant,
        alive_at_mercy=1 if s.nell_alive else 0,
        rep=s.rep + reputation_delta(s.outcome, s.witness_alive),
    )
    if r.effects_at_debrief and s.outcome == OUT_SAVED and variant == V_SAVED:
        s = replace(s, mutual_trust=s.mutual_trust + 1)
    return s


def _debrief(choice: str) -> Event:
    def ev(s: State, r: Rules) -> Optional[State]:
        if s.loc != TOWN or not s.done(50) or s.done(60) or s.debrief_answer is not None:
            return None
        if choice not in DEBRIEF_CHOICES.get(s.debrief_variant or "", ()):
            return None
        s = replace(s, debrief_answer=choice)
        if choice in ("admit", "confess"):
            return replace(s, truth=s.truth + 1, accountability=s.accountability + 1)
        if choice == "blame":
            return replace(s, truth=s.truth - 1)
        if choice == "deny":
            s = replace(s, truth=s.truth - 1)
            if s.debrief_variant == V_WITNESS:
                s = replace(s, mutual_trust=s.mutual_trust - 1)   # "She's lying."
            return s
        raise AssertionError(choice)

    ev.__name__ = "ev_debrief_" + choice
    return ev


def ev_pritchard_handoff(s: State, r: Rules) -> Optional[State]:
    """Node P2: Chapter 02 hook (stage 60 -> 100)."""
    if s.loc != TOWN or not s.done(50) or s.done(60):
        return None
    if s.debrief_answer == "abandoned":
        return None                              # v0.1: no greeting leads back here
    if s.debrief_answer is None:
        s = replace(s, debrief_answer="silent")
    s = set_stage(set_stage(s, 60), 100)
    return replace(s, mq01_done=1)


def ev_walk_away_from_pritchard(s: State, r: Rules) -> Optional[State]:
    """Player leaves the conversation between P1 and P2."""
    if s.loc != TOWN or not s.done(50) or s.done(60):
        return None
    if r.debrief_resumable or s.debrief_answer == "abandoned":
        return None                              # nothing is lost; P0.C resumes
    # v0.1: greeting A needs the dispatch, greeting B needs stage < 20.
    # After the hand-over neither matches, so P2 can never be reached.
    return replace(s, debrief_answer="abandoned")


# --------------------------------------------------------------------------
# SQ01 events
# --------------------------------------------------------------------------


def _sq_recompute(s: State) -> State:
    """TLM_SQ01_QuestScript.RecomputeEvidence()."""
    if not s.sq_done(10) or s.sq_outcome != SQ_NONE:
        return s
    if s.evidence_level >= 1 and not s.sq_done(20):
        s = replace(sq_set_stage(s, 20), sq_o10=COMPLETE, sq_o20=SHOWN)
    if s.evidence_level >= 2 and not s.sq_done(25):
        s = sq_set_stage(s, 25)
    return s


def _clue_scripts_live(s: State, r: Rules) -> bool:
    """Alias scripts only receive events while their quest is running."""
    return s.sq_running


def ev_take_ledger(s: State, r: Rules) -> Optional[State]:
    """E0: picking up the ledger starts (or reveals) SQ01."""
    if not s.done(10) or s.loc != WRECK or s.has_ledger or s.sq_done(10) or s.ledger_lost:
        return None
    s = replace(sq_set_stage(s, 10), has_ledger=True, sq_running=True, sq_o10=SHOWN)
    return _sq_recompute(s)


def _examine(flag: str) -> Event:
    def ev(s: State, r: Rules) -> Optional[State]:
        if not s.done(10) or s.loc != WRECK or getattr(s, flag):
            return None
        if s.sq_outcome != SQ_NONE:
            return None
        if not _clue_scripts_live(s, r):
            # v0.1 hole: the quest is not running, so the alias script never
            # hears the activation. The player sees the part; nothing is
            # recorded. (They can examine it again once SQ01 is running.)
            return s
        return _sq_recompute(replace(s, **{flag: True}))

    ev.__name__ = "ev_examine_" + flag
    return ev


def ev_take_journal(s: State, r: Rules) -> Optional[State]:
    """E3: the marshal's pocket journal."""
    if not s.done(10) or s.loc != WRECK or s.has_journal or s.journal_sold:
        return None
    s = replace(s, has_journal=True)
    if s.sq_outcome != SQ_NONE or not _clue_scripts_live(s, r):
        # v0.1 hole: OnContainerChanged fires once. If SQ01 is not running
        # when the journal is picked up, E3 is never recorded.
        return s
    return _sq_recompute(replace(s, e3=True))


def ev_pike_parts_book(s: State, r: Rules) -> Optional[State]:
    """E4: Ada Pike shows her own tally (needs the ledger in hand)."""
    if s.loc != TOWN or not s.pike_alive or s.e4 or not s.sq_done(10) or s.sq_outcome != SQ_NONE:
        return None
    return _sq_recompute(replace(s, e4=True))


def _sq_can_decide(s: State) -> bool:
    # Keyed on stages, not on holding the item (same reasoning as A9).
    return s.sq_done(20) and s.sq_outcome == SQ_NONE


def _sq_apply(s: State, outcome: int) -> State:
    """TLM_SQ01_QuestScript.ApplyOutcome(). One outcome, ever."""
    assert s.sq_outcome == SQ_NONE
    if s.ledger_lost:
        # The stage is the proof, so the decision stands without the item.
        # The item is not given back (TLM:SQ01Quest.ApplyOutcome).
        s = replace(s, ledger_lost=False)
    s = replace(s, sq_outcome=outcome, sq_o10=COMPLETE, sq_o20=COMPLETE)
    if outcome == SQ_REPORTED:
        s = replace(s, yard_alerted=1, truth=s.truth + 1, competence=s.competence + 1)
    elif outcome == SQ_POSTED:
        s = replace(s, truth=s.truth + 1)
    elif outcome == SQ_POSTED_YARD:
        s = replace(s, truth=s.truth + 1, competence=s.competence + 1, mutual_trust=s.mutual_trust + 1)
    elif outcome == SQ_POSTED_HASKELL:
        s = replace(
            s,
            haskell="gone",
            haskell_scapegoated=1,
            truth=s.truth - 1,
            competence=s.competence - 1,
            accountability=s.accountability - 1,
            mutual_trust=s.mutual_trust - 1,
        )
    elif outcome == SQ_SOLD:
        s = replace(
            s,
            has_ledger=False,
            journal_sold=s.has_journal,
            has_journal=False,
            vane_has_ledger=1,
            sold_for_caps=True,
        )
    elif outcome == SQ_DESTROYED:
        s = replace(s, has_ledger=False, truth=s.truth - 1)
    return sq_set_stage(sq_set_stage(s, 50), 100)


def ev_sq_report(s: State, r: Rules) -> Optional[State]:
    if s.loc != TOWN or not _sq_can_decide(s):
        return None
    return _sq_apply(s, SQ_REPORTED)


def ev_sq_post(s: State, r: Rules) -> Optional[State]:
    if s.loc != TOWN or not _sq_can_decide(s):
        return None
    return _sq_apply(s, SQ_POSTED)


def ev_sq_post_yard(s: State, r: Rules) -> Optional[State]:
    if s.loc != TOWN or not _sq_can_decide(s) or s.evidence_level < 2:
        return None
    return _sq_apply(s, SQ_POSTED_YARD)


def ev_sq_post_haskell(s: State, r: Rules) -> Optional[State]:
    if s.loc != TOWN or not _sq_can_decide(s) or s.haskell != "present":
        return None
    return _sq_apply(s, SQ_POSTED_HASKELL)


def ev_sq_sell(s: State, r: Rules) -> Optional[State]:
    if s.loc != TOWN or not _sq_can_decide(s) or not s.vane_alive:
        return None
    return _sq_apply(s, SQ_SOLD)


def ev_sq_destroy(s: State, r: Rules) -> Optional[State]:
    """Burn the ledger. Possible from the moment the player holds it."""
    if not s.sq_done(10) or s.sq_outcome != SQ_NONE:
        return None
    return _sq_apply(s, SQ_DESTROYED)


def ev_pike_dies(s: State, r: Rules) -> Optional[State]:
    if not s.pike_alive or not s.done(10):
        return None
    return replace(s, pike_alive=False)


def ev_haskell_dies(s: State, r: Rules) -> Optional[State]:
    if s.haskell != "present" or not s.done(10):
        return None
    return replace(s, haskell="dead")


def ev_vane_dies(s: State, r: Rules) -> Optional[State]:
    if not s.vane_alive or not s.done(10):
        return None
    return replace(s, vane_alive=False)


def ev_ledger_vanishes(s: State, r: Rules) -> Optional[State]:
    if not s.has_ledger or s.sq_outcome != SQ_NONE:
        return None
    return replace(s, has_ledger=False, ledger_lost=True)


# --------------------------------------------------------------------------
# Registries
# --------------------------------------------------------------------------

MQ01_EVENTS: Dict[str, Event] = {
    "start": ev_start,
    "take_revolver": ev_take_revolver,
    "take_dispatch": ev_take_dispatch,
    "goto_wreck": ev_goto_wreck,
    "goto_ambush": ev_goto_ambush,
    "goto_town": ev_goto_town,
    "goto_town_bypass_gate": ev_goto_town_bypass_gate,
    "evade_timer": ev_evade_timer,
    "attack_cutter": ev_attack_cutter,
    "break_combat": ev_break_combat,
    "player_kills_lead": ev_player_kills_lead,
    "player_kills_cutter": ev_player_kills_cutter,
    "npc_kills_lead": ev_npc_kills_lead,
    "dunmore_talk": ev_dunmore_talk,
    "walk_away_from_dunmore": ev_walk_away_from_dunmore,
    "dunmore_speech_success": ev_dunmore_speech_success,
    "dunmore_speech_fail": ev_dunmore_speech_fail,
    "dunmore_deal": ev_dunmore_deal,
    "dunmore_refuse": ev_dunmore_refuse,
    "player_kills_nell": ev_player_kills_nell,
    "player_kills_abel": ev_player_kills_abel,
    "nell_dies_other": ev_nell_dies_other,
    "nell_reward": ev_nell_reward,
    "dispatch_vanishes": ev_dispatch_vanishes,
    "recovery": ev_recovery,
    "pritchard_no_dispatch": ev_pritchard_no_dispatch,
    "pritchard_handover": ev_pritchard_handover,
    "debrief_admit": _debrief("admit"),
    "debrief_deny": _debrief("deny"),
    "debrief_confess": _debrief("confess"),
    "debrief_blame": _debrief("blame"),
    "pritchard_handoff": ev_pritchard_handoff,
    "walk_away_from_pritchard": ev_walk_away_from_pritchard,
}
MQ01_EVENTS = {name: _conversation_closes(ev) for name, ev in MQ01_EVENTS.items()}

SQ01_EVENTS: Dict[str, Event] = {
    "take_ledger": ev_take_ledger,
    "examine_e1": _examine("e1"),
    "examine_e2": _examine("e2"),
    "take_journal": ev_take_journal,
    "pike_parts_book": ev_pike_parts_book,
    "sq_report": ev_sq_report,
    "sq_post": ev_sq_post,
    "sq_post_yard": ev_sq_post_yard,
    "sq_post_haskell": ev_sq_post_haskell,
    "sq_sell": ev_sq_sell,
    "sq_destroy": ev_sq_destroy,
    "pike_dies": ev_pike_dies,
    "haskell_dies": ev_haskell_dies,
    "vane_dies": ev_vane_dies,
    "ledger_vanishes": ev_ledger_vanishes,
}

ALL_EVENTS: Dict[str, Event] = {**MQ01_EVENTS, **SQ01_EVENTS}

# The shortest-path actions that must always be enough to finish MQ01 (C6).
MQ01_SPINE = (
    "start",
    "recovery",
    "goto_wreck",
    "take_dispatch",
    "goto_town",
    "pritchard_handover",
    "pritchard_handoff",
)


class NotAvailable(Exception):
    pass


def apply(s: State, name: str, rules: Rules = V02) -> State:
    out = ALL_EVENTS[name](s, rules)
    if out is None:
        raise NotAvailable("%s is not available in this state" % name)
    return out


def run(names: Iterable[str], rules: Rules = V02, start: Optional[State] = None) -> State:
    s = start or State()
    for n in names:
        s = apply(s, n, rules)
    return s


def available(s: State, rules: Rules = V02, events: Optional[Dict[str, Event]] = None) -> List[str]:
    events = events or ALL_EVENTS
    return [n for n, f in events.items() if f(s, rules) is not None]


def explore(
    rules: Rules = V02,
    events: Optional[Dict[str, Event]] = None,
    start: Optional[State] = None,
    limit: int = 2_000_000,
) -> Tuple[Dict[State, List[Tuple[str, State]]], Dict[State, Tuple[Optional[State], Optional[str]]]]:
    """Breadth-first search of every reachable state.

    Returns (graph, parent) where graph[state] = [(event, next_state), ...]
    and parent[state] = (previous_state, event) for path reconstruction.
    """
    events = events or ALL_EVENTS
    s0 = start or State()
    graph: Dict[State, List[Tuple[str, State]]] = {}
    parent: Dict[State, Tuple[Optional[State], Optional[str]]] = {s0: (None, None)}
    frontier = [s0]
    while frontier:
        nxt: List[State] = []
        for s in frontier:
            edges: List[Tuple[str, State]] = []
            for name, fn in events.items():
                t = fn(s, rules)
                if t is None or t == s:
                    continue
                edges.append((name, t))
                if t not in parent:
                    parent[t] = (s, name)
                    nxt.append(t)
            graph[s] = edges
        if len(parent) > limit:
            raise RuntimeError("state space exceeded %d states" % limit)
        frontier = nxt
    return graph, parent


def path_to(parent: Dict[State, Tuple[Optional[State], Optional[str]]], s: State) -> List[str]:
    out: List[str] = []
    while True:
        prev, name = parent[s]
        if prev is None:
            break
        out.append(name)  # type: ignore[arg-type]
        s = prev
    return list(reversed(out))
