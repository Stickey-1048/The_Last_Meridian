"""The Greenwater road, TLM_MQ02B "The Queen of Tellico" (GREENWATER-STORY-001),
as a state model.

Apart from tlm_model.py on purpose: the rules of TLM_MQ01 and TLM_SQ01 are not
changed by this road and are not repeated here. What it needs of the main
quest is one fact it only reads (main_over).

The model says what scripts/Source/User/TLM/MQ02BQuest.psc (the rules) and
GreenwaterWalk.psc (the boxes and the pieces) must do, action by action: what
is shown, in order, and what the road then holds. tools/papyrus_sim/
test_greenwater.py plays the real scripts and compares after every action.

Its rules, in the order's words:
  - winning at cards (41) is not the grain at the landing;
  - the paid share (44), the lie and Opal's thanks (46) are three things:
    grain_sold is the paid share and the lie delivered to her alive; her
    thanks in the journal (46) and her cup wait for her answer;
  - a cut chain is an escape pending: no cards, no share and no fire after it,
    only the pilot lever, however often;
  - nobody dead speaks, is handed a prisoner or hands anything over, and no
    action asks for anybody it does not need;
  - nothing is hanged, released or lied about that the player did not choose;
  - friend and hunting are facts only when earned;
  - every one-time thing is asked for once and fails closed.

A person here is either alive and there, or not. Somebody alive and in a
fight is tried separately in the stand-in's tests.

Not a compile and not a game test.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

# The same names and numbers as TLM:MQ02BQuest; the stand-in's tests compare them.
RV_NONE, RV_CARDS, RV_CHUTE, RV_FIRE, RV_SHARE = 0, 41, 42, 43, 44
RV_CARGO_LASHED, RV_CARGO_YIELDED, RV_CARGO_HOME_WHOLE, RV_CARGO_HOME_REDUCED, RV_CARGO_DESTROYED = range(5)
RV_H_FREE, RV_H_RELEASED, RV_H_CUSTODY, RV_H_HANGED, RV_H_DEAD, RV_H_UNACCOUNTED = range(6)
RV_CARD_NONE, RV_CARD_LOST, RV_CARD_WON = range(3)
RV_CARD_THRESHOLD = 5
RV_UNITS_WHOLE, RV_UNITS_PILOTED, RV_UNITS_ALONE = 12, 8, 6
RV_SHARE_CAPS = 200
RV_RETURN_NONE, RV_RETURN_ESCAPE, RV_RETURN_TOW = range(3)
RV_HIRE_LETTER, RV_HIRE_ADMISSION = 1, 2
RV_GRANT_BOWL, RV_GRANT_CUP, RV_GRANT_RELIEF = 1, 2, 3

BOARD_GANGWAY, BOARD_OFFSIDE, BOARD_DECK = 1, 2, 3

# What a request to the game for an item can do.
ASKED_FOR = ("caps", "letter", "bowl", "cup", "relief")


@dataclass
class River:
    # ---- the world, as a test sets it
    main_over: bool = True          # the dispatch delivered, acknowledged, and the debrief ended
    opal: bool = True               # alive and there
    hatcher: bool = True
    rafferty: bool = True
    belden: bool = True
    sheriff: bool = True            # Owen Pritchard, at Mercy
    charisma: float = 4.0           # the player's current Charisma
    caps_bound: bool = True         # the game's bottle cap was found by the build
    charisma_bound: bool = True
    meal_bound: bool = True         # a food item of the game's was found by the build
    letter_pages: int = 3
    refused: Set[str] = field(default_factory=set)   # requests the game does not honour, of ASKED_FOR

    # ---- the road
    zones_up: bool = False
    stages: Set[int] = field(default_factory=set)
    shown: Dict[int, bool] = field(default_factory=dict)       # objectives displayed
    ticked: Dict[int, bool] = field(default_factory=dict)      # objectives completed
    claim: int = RV_NONE
    card: int = RV_CARD_NONE
    escape_pending: bool = False
    return_pending: int = RV_RETURN_NONE
    fire_warned: bool = False
    burning: bool = False
    share_pending: bool = False
    share_paid: bool = False
    lie_told: bool = False
    lie_heard: bool = False
    denied_said: bool = False
    approach: int = 0
    outcome: int = RV_NONE
    cargo: int = RV_CARGO_LASHED
    recovered: int = 0
    fate: int = RV_H_FREE           # TLM_G_MQ02B_Hatcher
    grain_home: bool = False
    grain_sold: bool = False
    queen_burned: bool = False
    hatcher_hanged: bool = False
    hatcher_friend: bool = False
    hatcher_hunting: bool = False
    silver_river: bool = False
    reported: bool = False
    hire_read: bool = False
    hire_heard: bool = False
    ran_said: bool = False
    burned_said: bool = False
    arrival_brief_read: bool = False
    hatcher_in_irons: bool = False

    # ---- what the player was given, and what the game was asked for
    caps: int = 0
    food: int = 0
    letters: int = 0
    asked: Dict[str, int] = field(default_factory=dict)
    given: Set[str] = field(default_factory=set)
    pending: Set[str] = field(default_factory=set)

    # ================================================================ queries
    def done(self, stage: int) -> bool:
        return stage in self.stages

    def road_open(self) -> bool:
        return self.zones_up and self.done(10)

    def unsettled(self) -> bool:
        return self.claim == RV_NONE

    def hatcher_state(self) -> int:
        if self.fate in (RV_H_FREE, RV_H_RELEASED) and not self.hatcher:
            return RV_H_DEAD
        return self.fate

    def hatcher_dies(self) -> None:
        """He is killed, by whoever: not the hanging, which keeps its own record."""
        self.hatcher = False
        if self.fate in (RV_H_FREE, RV_H_RELEASED):
            self.fate = RV_H_DEAD

    def hatcher_there(self) -> bool:
        """Alive and on the deck: not burned out of it and not taken to Mercy."""
        return self.hatcher and self.fate in (RV_H_FREE, RV_H_RELEASED) and not self.queen_burned and not self.burning

    def hatcher_at_table(self) -> bool:
        return self.hatcher_there()

    def hatcher_to_judge(self) -> bool:
        return self.done(41) and self.hatcher and self.fate == RV_H_FREE

    def share_offered(self) -> bool:
        return self.claim == RV_NONE and not self.share_paid and not self.share_pending and self.caps_bound

    def can_complete(self) -> bool:
        return (self.done(42) or self.done(43) or (self.done(44) and self.share_paid)
                or (self.done(41) and self.cargo == RV_CARGO_HOME_WHOLE))

    def belden_there(self) -> bool:
        return self.belden and self.outcome in (RV_FIRE, RV_SHARE)

    # ============================================================== objectives
    def _show(self, n):
        if not self.shown.get(n) and not self.ticked.get(n):
            self.shown[n] = True

    def _tick(self, n):
        self.ticked[n] = True

    def _retire(self, n):
        if self.shown.get(n) and not self.ticked.get(n):
            self.shown[n] = False

    def _course_taken(self):
        self._tick(40)
        if self.can_complete():
            self._tick(60)
            self._show(80)

    # ==================================================================== travel
    def travel(self, go: bool = True) -> List[str]:
        if not self.main_over:
            return ["NoteTravelNotYet"]
        shown = ["AskTravelAgain" if self.done(100) else "AskTravel"]
        if go:
            self.zones_up = True
            if not self.arrival_brief_read and self.outcome == RV_NONE and not self.done(20) and self.opal:
                shown.append("ArrivalBrief")
                self.arrival_brief_read = True
        return shown

    def step_onto_landing(self) -> None:
        if self.zones_up and not self.done(10):
            self.stages.add(10)
            self._show(10)

    def leave(self, go: bool = True) -> List[str]:
        if not self.zones_up:
            return []
        if self.done(100):
            shown = ["AskLeaveAgain"]
        elif self.can_complete():
            shown = ["AskLeaveResolved"]
        else:
            shown = ["AskLeaveUnresolved"]
        if not go or self.done(100):
            return shown
        if self.can_complete():
            self._tick(80)
            self.stages.add(100)
            shown.append("NoteRoadComplete")
        else:
            shown.append("NoteLeftUnresolved")
        return shown

    # ================================================================ the items
    def _give(self, what: str, caps: int = 0) -> bool:
        """Asked of the game once. True if it arrived."""
        if what in self.given or what in self.pending:
            return False
        self.pending.add(what)
        self.asked[what] = self.asked.get(what, 0) + 1
        if what in self.refused:
            return False                            # fails closed: pending for good
        self.pending.discard(what)
        self.given.add(what)
        if what == "caps":
            self.caps += caps
        elif what == "letter":
            self.letters += 1
        else:
            self.food += 1
        return True

    def _portion(self, which: str, shown: List[str]) -> None:
        if not self.meal_bound:
            shown.append("NoteNoMeal")
            return
        if which in ("bowl", "cup") and not self.opal:
            return
        if which == "cup" and not self.lie_heard:
            return
        if which == "relief" and not (self.belden and (self.done(43) or self.done(44))):
            return
        self._give(which)

    # ============================================================== Opal Starnes
    def talk_opal(self, first: Optional[str] = None, judge: Optional[str] = None, lie: Optional[bool] = None) -> List[str]:
        """first: "wants", "guns" or "bowl". judge: "hang", "custody" or "release". lie: tell it or not."""
        if not self.road_open() or not self.opal:
            return []
        fate = self.hatcher_state()
        if self.outcome == RV_CARDS and self.cargo == RV_CARGO_HOME_WHOLE:
            if fate == RV_H_HANGED and self.done(60):
                return ["OpalAfterHanging"]
            if fate == RV_H_FREE and self.hatcher_to_judge():
                return self._judge_before_opal(judge)
            if fate == RV_H_DEAD:
                return ["OpalWonHatcherDead"]
            if fate in (RV_H_RELEASED, RV_H_CUSTODY) and not self.denied_said:
                self.denied_said = True
                return ["OpalDenied"]
            return ["OpalDefault"]
        if self.outcome == RV_CHUTE and self.done(42) and self.cargo == RV_CARGO_HOME_REDUCED and self.recovered > 0:
            return ["OpalAfterChute"]
        if self.outcome == RV_FIRE and self.done(43) and self.cargo == RV_CARGO_DESTROYED:
            return ["OpalAfterFire"]
        if self.outcome == RV_SHARE and self.done(44) and self.share_paid:
            return self._after_share(lie)
        if self.outcome == RV_NONE and not self.done(20) and not self.escape_pending:
            shown = ["OpalFirst"]
            if first == "wants":
                shown.append("OpalWants")
                self.stages.add(20)
                self._tick(10)
                if not self.done(30):
                    self._show(20)
                shown += ["Goal", "Stakes"]
            elif first == "guns":
                shown.append("OpalGuns")
            elif first == "bowl":
                shown.append("OpalBowl")
                self._portion("bowl", shown)
            return shown
        return ["OpalDefault"]

    def _judge_before_opal(self, judge) -> List[str]:
        shown = ["OpalAfterWon" if self.sheriff else "OpalAfterWonNoSheriff"]
        if judge == "hang":
            self._judge(60, shown)
        elif judge == "custody" and self.sheriff:
            if self._judge(61, shown):
                self._deny(shown)
        elif judge == "release":
            if self._judge(1, shown):
                self._deny(shown)
        return shown

    def _deny(self, shown):
        if self.opal and not self.denied_said:
            shown.append("OpalDenied")
            self.denied_said = True

    def _after_share(self, lie) -> List[str]:
        if self.lie_heard:
            return ["OpalDefault"]
        shown = []
        if not self.lie_told:
            shown.append("AskLie")
            if not lie:
                return shown
            # The paid deal and the lie delivered to her, alive: that is grain_sold, and it is kept.
            self.lie_told = True
            self.grain_sold = True
        # Her answer is another thing: the journal's thanks (46) and her cup wait for it.
        shown.append("OpalAfterShare")
        self.lie_heard = True
        self.stages.add(46)
        self._portion("cup", shown)
        return shown

    # ============================================================ Mose Rafferty
    def talk_rafferty(self, pick: Optional[str] = None) -> List[str]:
        """Before boarding: "gangway", "offside" or "confess". Aboard and unsettled: as use_chain."""
        if not self.road_open() or not self.rafferty:
            return []
        if self.done(43) and not self.burned_said:
            self.burned_said = True
            return ["RaffertyBurned"]
        if self.done(30) and self.unsettled():
            return self.use_chain(pick)
        if self.done(20) and not self.done(30) and self.unsettled():
            shown = ["RaffertySkiff"]
            if pick == "offside":
                shown.append("NoteSkiffScene")
            elif pick == "confess":
                shown.append("RaffertyConfess")
            return shown
        return ["RaffertyDefault"]

    def take_skiff(self) -> List[str]:
        return ["NoteSkiffScene"] if self.road_open() else []

    def board(self, approach: int) -> None:
        if not self.road_open() or self.done(30):
            return
        self.approach = approach
        self.stages.add(30)
        self._retire(10)
        if self.shown.get(20):
            self._tick(20)
        if self.claim == RV_NONE:
            self._show(40)
        if not self.done(50):
            self._show(50)

    # ============================================================== Lyle Hatcher
    def use_table(self, picks=(), then: Optional[str] = None, done: bool = True, judge: Optional[str] = None) -> List[str]:
        """picks: what is pressed at his offer, in order: "deal", "share", "paid", "leave".
        then: after a lost hand, "share" or "leave". done: "Done." or "No." to the share.
        judge: after a won hand, "hang", "custody", "release" or "silent"."""
        if not self.road_open():
            return []
        self.board(BOARD_DECK)
        if self.hatcher_state() == RV_H_CUSTODY:
            return ["NoteHatcherCustody"]
        if not self.hatcher_at_table():
            return ["NoteTableEmpty"]
        shown: List[str] = []
        if self.unsettled():
            self.stages.add(40)
            picks = list(picks)
            for _ in range(3):
                share = self.share_offered()
                shown.append("HatcherTable" if share else "HatcherTableNoShare")
                pick = picks.pop(0) if picks else "leave"
                if pick == "deal":
                    self._deal(shown, then, done, judge)
                    return shown
                if pick == "share" and share:
                    self._buy_share(shown, done)
                    return shown
                if pick == "paid":
                    shown += ["HatcherPaidA", "HatcherPaidB"]
                    self._learn(RV_HIRE_ADMISSION)
                    continue
                return shown
            return shown
        if self.hatcher_to_judge():
            self._judge_at_table(shown, judge)
            return shown
        return ["HatcherDefault"]

    def _deal(self, shown, then, done, judge):
        shown.append("CardStakes")
        if not self.charisma_bound:
            return
        if self.charisma >= RV_CARD_THRESHOLD:
            self.claim = RV_CARDS
            self.card = RV_CARD_WON
            self.outcome = RV_CARDS
            self.cargo = RV_CARGO_YIELDED
            self.stages.add(41)
            self._tick(40)
            self._show(60)
            self._judge_at_table(shown, judge)
            return
        self.card = RV_CARD_LOST
        self.stages.add(45)
        if self.share_offered():
            shown.append("HatcherWon")
            if then == "share":
                self._buy_share(shown, done)
        else:
            shown.append("HatcherWonNoShare")

    def _buy_share(self, shown, done):
        shown.append("HatcherShare")
        if not done:
            return
        if not self.share_offered():
            shown.append("NoteShareFailed")
            return
        shown.append("ConfirmShare")
        self.claim = RV_SHARE
        self.share_pending = True
        self.asked["caps"] = self.asked.get("caps", 0) + 1
        if "caps" in self.refused:
            self.claim = RV_NONE                    # the deal is off; never offered or asked for again
            shown.append("NoteShareFailed")
            return
        self.caps += RV_SHARE_CAPS
        self.share_paid = True
        self.share_pending = False
        self.outcome = RV_SHARE
        self.stages.add(44)
        self._course_taken()
        shown.append("NoteSharePaid")

    def _judge_at_table(self, shown, judge):
        if not self.hatcher_at_table() or not self.hatcher_to_judge():
            return
        if self.opal and self.sheriff:
            shown.append("HatcherLost")
            verdict = {"hang": 60, "custody": 61, "release": 1}.get(judge, 0)
        elif self.opal:
            shown.append("HatcherLostNoSheriff")
            verdict = {"hang": 60, "release": 1}.get(judge, 0)
        elif self.sheriff:
            shown.append("HatcherLostNoOpal")
            verdict = {"custody": 61, "release": 1}.get(judge, 0)
        else:
            shown.append("HatcherLostAlone")
            verdict = {"release": 1}.get(judge, 0)
        if verdict:
            self._judge(verdict, shown)

    def _judge(self, verdict: int, shown) -> bool:
        if self.road_open() and self.hatcher_to_judge():
            if verdict == 60 and self.opal:shown.append("ConfirmHang")
            elif verdict == 61 and self.sheriff:shown.append("ConfirmCustody")
            elif verdict == 1:shown.append("ConfirmRelease")
        ok = False
        if self.road_open() and self.hatcher_to_judge():
            if verdict == 60 and self.opal:
                self.hatcher = False
                self.fate = RV_H_HANGED
                self.hatcher_hanged = True
                self.stages.add(60)
                ok = True
            elif verdict == 61 and self.sheriff:
                self.fate = RV_H_CUSTODY
                self.hatcher_in_irons = True
                self.stages.add(61)
                ok = True
            elif verdict == 1:
                self.fate = RV_H_RELEASED
                self.hatcher_friend = True
                ok = True
        if not ok:
            shown.append("NoteJudgmentFailed")
        return ok

    def _learn(self, how: int):
        if not self.road_open():
            return
        if how == RV_HIRE_LETTER:
            self.hire_read = True
        else:
            self.hire_heard = True
        if not self.done(50):
            self.silver_river = True
            self.stages.add(50)
            self._tick(50)

    def open_strongbox(self, read: bool = True) -> List[str]:
        if not self.road_open():
            return []
        self.board(BOARD_DECK)
        if not read:
            return ["LetterPage1"]
        shown = ["LetterPage%d" % (i + 1) for i in range(self.letter_pages)]
        self._learn(RV_HIRE_LETTER)
        self._give("letter")
        return shown

    # ======================================================= chain, pilot, fire
    def use_chain(self, pick: Optional[str] = None) -> List[str]:
        """pick: "cut", "burn" or "notyet"."""
        if not self.road_open():
            return []
        self.board(BOARD_DECK)
        if self.escape_pending:
            return ["NoteChainCut"]
        if not self.unsettled():
            return ["NoteChainNothing"]
        shown = ["RaffertyChain" if self.rafferty else "AskChain"]
        if pick == "cut":
            self.claim = RV_CHUTE
            self.escape_pending = True
            self._tick(40)
            self._show(60)
            shown.append("NoteChainCut")
        elif pick == "burn":
            self.fire_warned = True
            shown.append("NoteFireWarned")
        return shown

    def use_pilot(self) -> List[str]:
        if not self.road_open():
            return []
        self.board(BOARD_DECK)
        if self.escape_pending and not self.done(42):
            self.return_pending = RV_RETURN_ESCAPE
            return ["NoteChuteScene"]
        if self.claim == RV_CARDS and self.cargo == RV_CARGO_YIELDED:
            self.return_pending = RV_RETURN_TOW
            return ["NoteTowScene"]
        return ["NotePilotNothing"]

    def reach_dock(self) -> List[str]:
        if not self.road_open():
            return []
        if self.return_pending == RV_RETURN_ESCAPE and self.escape_pending:
            self.return_pending = RV_RETURN_NONE
            self.escape_pending = False
            self.recovered = RV_UNITS_PILOTED if self.rafferty else RV_UNITS_ALONE
            self.cargo = RV_CARGO_HOME_REDUCED
            self.grain_home = True
            self.outcome = RV_CHUTE
            if self.hatcher_state() == RV_H_FREE:
                self.hatcher_hunting = True
            self.stages.add(42)
            self._course_taken()
            if self.rafferty:
                shown = ["NoteHomePiloted"]
                if not self.ran_said:
                    shown.append("RaffertyRan")
                    self.ran_said = True
                return shown
            return ["NoteHomeAlone"]
        if self.return_pending == RV_RETURN_TOW and self.cargo == RV_CARGO_YIELDED:
            self.return_pending = RV_RETURN_NONE
            self.recovered = RV_UNITS_WHOLE
            self.cargo = RV_CARGO_HOME_WHOLE
            self.grain_home = True
            self._course_taken()
            return ["NoteHomeWhole"]
        return []

    def use_fire(self, confirm: bool = True) -> List[str]:
        if not self.road_open():
            return []
        self.board(BOARD_DECK)
        if not self.unsettled():
            return ["NoteChainNothing"]
        if not self.fire_warned:
            return ["NoteFireNotWarned"]
        shown = ["AskFire"]
        if not confirm:
            return shown
        self.claim = RV_FIRE
        self.cargo = RV_CARGO_DESTROYED
        self.recovered = 0
        self.queen_burned = True
        self.outcome = RV_FIRE
        if self.fate == RV_H_FREE and self.hatcher:
            self.fate = RV_H_UNACCOUNTED
        self.stages.add(43)
        self._course_taken()
        shown.append("NoteFireScene")
        if self.rafferty and not self.burned_said:
            shown.append("RaffertyBurned")
            self.burned_said = True
        return shown

    # ============================================================== Tomas Belden
    def talk_belden(self) -> List[str]:
        if not self.road_open() or not self.belden_there():
            return []
        shown = ["BeldenRelief"]
        self._portion("relief", shown)
        return shown

    # ============================================================== the report
    def report(self, give: bool = True) -> List[str]:
        """What Pritchard's conversation shows of the river report. [] if there is none to make."""
        if not self.done(100) or self.reported or not self.sheriff:
            return []
        shown = ["ReportKnown" if self.done(50) else "ReportUnknown"]
        if not give:
            return shown
        self.reported = True
        shown.append({RV_CARGO_HOME_WHOLE: "ReportWhole", RV_CARGO_HOME_REDUCED: "ReportReduced",
                      RV_CARGO_DESTROYED: "ReportDestroyed"}.get(self.cargo, "ReportSold"))
        shown.append("ReportEndKnown" if self.done(50) else "ReportEndUnknown")
        return shown

    # ============================================================ what must hold
    def problems(self) -> List[str]:
        out = []
        s = self.stages
        resolutions = [n for n in (41, 42, 43, 44) if n in s]
        if len(resolutions) > 1:
            out.append("more than one course: %s" % resolutions)
        if self.escape_pending and (resolutions or self.claim != RV_CHUTE):
            out.append("an escape pending beside another course")
        if 100 in s and not self.can_complete():
            out.append("complete with nothing carried through")
        if 42 in s and not (self.cargo == RV_CARGO_HOME_REDUCED and self.recovered in (RV_UNITS_PILOTED, RV_UNITS_ALONE)):
            out.append("the Chute run without a reduced cargo at home")
        if 43 in s and not (self.cargo == RV_CARGO_DESTROYED and self.recovered == 0 and self.queen_burned):
            out.append("a fire with cargo left")
        if 41 in s and self.cargo not in (RV_CARGO_YIELDED, RV_CARGO_HOME_WHOLE):
            out.append("a card win and the cargo neither yielded nor whole at home")
        if 44 in s and not (self.share_paid and self.caps == RV_SHARE_CAPS and self.cargo == RV_CARGO_LASHED):
            out.append("a share without exactly one payment and the grain aboard")
        if self.caps not in (0, RV_SHARE_CAPS) or self.asked.get("caps", 0) > 1:
            out.append("caps paid other than once: %d, asked %d times" % (self.caps, self.asked.get("caps", 0)))
        if self.grain_home != (self.cargo in (RV_CARGO_HOME_WHOLE, RV_CARGO_HOME_REDUCED)):
            out.append("grain_home does not say what is at the landing")
        if self.grain_sold != self.lie_told or (self.grain_sold and not (44 in s and self.share_paid)):
            out.append("grain_sold is not the paid deal and the lie told")
        if (46 in s) != self.lie_heard or (46 in s and not self.grain_sold):
            out.append("her thanks in the journal without the lie told and her answer heard")
        if self.hatcher_hanged != (60 in s) or (60 in s and (self.fate != RV_H_HANGED or self.hatcher or 41 not in s)):
            out.append("a hanging that is not a hanged man after a card win")
        if 61 in s and (self.fate != RV_H_CUSTODY or 41 not in s):
            out.append("custody that is not a prisoner after a card win")
        if self.fate == RV_H_RELEASED and not self.hatcher_friend:
            out.append("released without the friend fact")
        if self.hatcher_friend and 41 not in s:
            out.append("a friend who was never beaten at cards")
        if self.hatcher_hunting and 42 not in s:
            out.append("hunting without the Chute run")
        if self.silver_river != (50 in s) or (50 in s and not (self.hire_read or self.hire_heard)):
            out.append("the hire known without the letter read or the admission heard")
        if self.reported and 100 not in s:
            out.append("reported before the road was complete")
        for what, times in self.asked.items():
            if times > 1:
                out.append("%s asked for %d times" % (what, times))
        if self.letters > 1 or self.food > 3:
            out.append("more given than there is to give")
        if (60 in s or 61 in s) and 41 not in s:
            out.append("a judgment without a card win")
        return out
