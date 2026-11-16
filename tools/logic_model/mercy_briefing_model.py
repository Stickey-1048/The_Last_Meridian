"""The Mercy briefing (ACT1-RUNTIME-001) as a small state model.

Apart from tlm_model.py on purpose: the rules of TLM_MQ01 and TLM_SQ01 are not
changed by the briefing and are not repeated here. What this model needs of
the main quest is five facts it only reads (see Gates).

The briefing is a preview utility task. It is not TLM_MQ02, its two stages are
not that quest's stages, and nothing in it starts, finishes or pays for a road.

What it models, and what scripts/Source/User/TLM/MercyBriefing.psc must do:

  - Pritchard offers it only when the main quest's delivery is acknowledged and
    its stages 60 and 100 and its Done global are all set, he is alive and in
    no fight, the player is alive, and the briefing's records are bound;
  - the first access sets stage 10 and shows objective 10, once;
  - a visit shows the hub, then at most one road's brief (and, for the pike,
    at most the one follow-on about the 2298 review copy), then ends;
  - stage 20 and the objective's completion come once, after a brief was
    actually shown, and only if Pritchard and the player are still as required
    when its box closes;
  - one review copy is given, only on the explicit Take, with the intent
    written down before the game is asked for the item and acknowledged from
    the count the player then holds;
  - holding the copy is read from the inventory when asked, never remembered.

Not a compile and not a game test.
"""
from dataclasses import dataclass, field, replace
from typing import List, Optional, Tuple

# The briefing's own stages and objective. Named apart from every constant of
# tlm_model.py, so that tools/check_consistency.py never compares the two.
BRIEF_STAGE_BEGUN = 10
BRIEF_STAGE_DONE = 20
BRIEF_OBJECTIVE = 10

# The hub's buttons, by place. The order is the contract with the script.
HUB_RAIL, HUB_RIVER, HUB_PIKE, HUB_NOT_NOW = range(4)
# The pike brief's buttons.
PIKE_ASK_QUILL, PIKE_CONTINUE = range(2)
# The review-copy context's buttons while a copy can still be given.
COPY_TAKE, COPY_LEAVE = range(2)

# The messages a visit can show, by the last part of their EditorID.
HUB, RAIL, RIVER, PIKE = "Hub", "Rail", "River", "Pike"
DOCKET, DOCKET_ISSUED = "Docket", "DocketIssued"
NOTE_ISSUED, NOTE_PENDING = "CopyIssuedNote", "CopyPendingNote"

# What the game does when asked for the item.
ADD_OK, ADD_FAILS = "ok", "fails"


@dataclass(frozen=True)
class Gates:
    """What the briefing reads of the main quest and of the two people. It
    writes none of them."""
    delivered: bool = True        # TLM_MQ01 stage 50
    acknowledged: bool = True     # TLM:MQ01Quest.DeliveryAcknowledged()
    stage60: bool = True
    stage100: bool = True
    done: bool = True             # TLM_G_MQ01_Done == 1
    briefer_alive: bool = True
    briefer_fighting: bool = False
    player_alive: bool = True
    bound: bool = True            # the briefing's quest, messages and book are filled in

    def open(self) -> bool:
        return (self.delivered and self.acknowledged and self.stage60 and self.stage100 and self.done
                and self.briefer_alive and not self.briefer_fighting and self.player_alive and self.bound)


@dataclass(frozen=True)
class Brief:
    begun: bool = False                  # stage 10
    done: bool = False                   # stage 20; the task is complete
    objective_shown: bool = False
    objective_complete: bool = False
    times_objective_shown: int = 0       # must never pass 1
    times_completed: int = 0             # must never pass 1
    copy_issued: bool = False            # history: a copy was given and seen in the inventory
    copy_pending: bool = False           # an intent with no acknowledgment
    copies_held: int = 0                 # the player's inventory, now
    copies_given: int = 0                # how many the briefing ever put there; must never pass 1
    add_requests: int = 0                # how often the game was asked for the item; must never pass 1

    def has_review_copy(self) -> bool:
        """Read from the inventory when asked. Not copy_issued, not done."""
        return self.copies_held > 0

    def take_offered(self) -> bool:
        return not (self.copy_issued or self.copy_pending or self.has_review_copy())


@dataclass(frozen=True)
class Visit:
    """One explicit activation of Pritchard that reaches the briefing: the
    buttons a person presses, by place, and what happens meanwhile."""
    hub: int = HUB_NOT_NOW
    pike: int = PIKE_CONTINUE
    copy: int = COPY_LEAVE
    add: str = ADD_OK
    # The gates as they are when a box closes, where they differ from the
    # gates the visit began with: somebody died or a fight began while a box
    # was open. Keyed by the box.
    after: Tuple[Tuple[str, Gates], ...] = ()

    def gates_after(self, box: str, default: Gates) -> Gates:
        for name, gates in self.after:
            if name == box:
                return gates
        return default


def visit(brief: Brief, gates: Gates, v: Visit) -> Tuple[Brief, List[str], bool]:
    """One visit. Returns the briefing afterwards, the messages shown in order,
    and whether the briefing took the activation (False: the first section's
    own ending is shown instead, as before)."""
    shown: List[str] = []
    if not gates.open():
        return brief, shown, False

    if not brief.begun:
        brief = replace(brief, begun=True, objective_shown=True, times_objective_shown=brief.times_objective_shown + 1)

    shown.append(HUB)
    now = v.gates_after(HUB, gates)
    if not now.open():
        return brief, shown, True
    if v.hub == HUB_RAIL:
        leaf = RAIL
    elif v.hub == HUB_RIVER:
        leaf = RIVER
    elif v.hub == HUB_PIKE:
        leaf = PIKE
    else:
        return brief, shown, True                 # Not now: nothing else happens

    shown.append(leaf)
    now = v.gates_after(leaf, now)
    if leaf == PIKE and v.pike == PIKE_ASK_QUILL and now.open():
        brief, now = _docket(brief, now, v, shown)

    if now.open() and not brief.done:
        brief = replace(brief, done=True, objective_complete=True, times_completed=brief.times_completed + 1)
    return brief, shown, True


def _docket(brief: Brief, gates: Gates, v: Visit, shown: List[str]) -> Tuple[Brief, Gates]:
    brief = reconcile(brief)
    if not brief.take_offered():
        shown.append(DOCKET_ISSUED)
        now = v.gates_after(DOCKET_ISSUED, gates)
        shown.append(NOTE_PENDING if brief.copy_pending else NOTE_ISSUED)
        return brief, now

    shown.append(DOCKET)
    now = v.gates_after(DOCKET, gates)
    if v.copy != COPY_TAKE or not now.open():
        return brief, now
    if brief.has_review_copy() or brief.copy_issued or brief.copy_pending:
        return brief, now
    # The intent first, then the game is asked, then the count is read.
    brief = replace(brief, copy_pending=True, add_requests=brief.add_requests + 1)
    if v.add == ADD_OK:
        brief = replace(brief, copies_held=brief.copies_held + 1, copies_given=brief.copies_given + 1)
    if brief.has_review_copy():
        brief = replace(brief, copy_issued=True, copy_pending=False)
    else:
        shown.append(NOTE_PENDING)                # fails closed: no second request, ever
    return brief, now


def reconcile(brief: Brief) -> Brief:
    """A pending intent is acknowledged when the copy is seen in the
    inventory. With none there it stays pending: nothing is given again."""
    if brief.copy_pending and brief.has_review_copy():
        return replace(brief, copy_issued=True, copy_pending=False)
    return brief


# ---- what a person does with the copy between visits

def drop(brief: Brief) -> Brief:
    """Dropped, stored in a container or otherwise out of the inventory."""
    return replace(brief, copies_held=0) if brief.copies_held else brief


def retrieve(brief: Brief) -> Brief:
    """The copy that was given is picked up again. Only what was given can be."""
    if brief.copies_given > 0 and brief.copies_held == 0:
        return replace(brief, copies_held=1)
    return brief


def late_arrival(brief: Brief) -> Brief:
    """The item the game was asked for turns up after all (the request was cut
    off by a save before it was acknowledged, not lost)."""
    if brief.copy_pending and brief.copies_given == 0 and brief.add_requests == 1:
        return replace(brief, copies_held=1, copies_given=1)
    return brief


def problems(brief: Brief) -> List[str]:
    """What must hold of the briefing whatever has happened."""
    out = []
    if brief.times_objective_shown > 1:
        out.append("the objective was shown %d times" % brief.times_objective_shown)
    if brief.times_completed > 1:
        out.append("the task was completed %d times" % brief.times_completed)
    if brief.done and not brief.begun:
        out.append("complete without having begun")
    if brief.objective_complete != brief.done:
        out.append("the objective and the task disagree on completion")
    if brief.add_requests > 1:
        out.append("the game was asked for the copy %d times" % brief.add_requests)
    if brief.copies_given > 1 or brief.copies_held > 1:
        out.append("more than one copy: given %d, held %d" % (brief.copies_given, brief.copies_held))
    if brief.copies_held > brief.copies_given:
        out.append("a copy is held that was never given")
    if brief.copy_issued and brief.copy_pending:
        out.append("issued and pending at once")
    if brief.copy_issued and brief.copies_given != 1:
        out.append("issued without a copy given")
    if (brief.copy_issued or brief.copy_pending) and brief.add_requests != 1:
        out.append("an issue or an intent without exactly one request")
    return out
