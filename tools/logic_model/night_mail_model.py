"""The Iron Junction road, TLM_MQ02A "The Night Mail" (NIGHT-MAIL-STORY-001), as a
state model.

Apart from tlm_model.py and greenwater_model.py on purpose: the rules of
TLM_MQ01, TLM_SQ01 and TLM_MQ02B are not changed by this road and are not
repeated here. What it needs of them is read: whether the opening is over, and
how the side quest ended.

The model says what scripts/Source/User/TLM/MQ02AQuest.psc (the rules) and
NightMailWalk.psc (the boxes, the pieces and the staged scenes) must do, action
by action: what is shown, in order, and what the road then holds.
tools/papyrus_sim/test_night_mail.py plays the real scripts and compares after
every action.

Its rules, in the order's words:
  - run, Dole defeated, sold and backed out exclude one another;
  - killing Dole delivers nothing: the mail is carried forward or back
    afterwards, and the outcome stays "Dole defeated";
  - refusing the job, walking away from the parley and declining at a notice
    start no fight and lose nothing;
  - nobody dead speaks, countersigns, is paid or receives anything, and no
    action asks for anybody it does not need;
  - silver, the name, the stamp found, the decision about it, holding it and
    Pritchard having it are separate; hearing gives no book;
  - lockridge_reported is the stamp delivered AND the yard shown without a
    master.

The model is of scenes that are seen to finish. A scene that is begun and not
seen (a piece that will not switch, a move that does nothing) is tried in the
stand-in's tests by seeding, and compared there with what the scripts must
then hold, not with this model.

A person here is either alive and there, or not. Somebody alive and in a
fight is tried separately in the stand-in's tests, except Dole and the Black
Rail once the player has chosen the fight: then nobody of them speaks.

Not a compile and not a game test.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

# The same names and numbers as TLM:MQ02AQuest; the stand-in's tests compare them.
NM_NONE, NM_RUN, NM_DEFEAT, NM_SOLD, NM_BACKED = 0, 41, 42, 43, 44
NM_MAIL_ABOARD, NM_MAIL_DELIVERED, NM_MAIL_RETAINED, NM_MAIL_SEIZED = range(4)
NM_ENGINE_SOUND, NM_ENGINE_DAMAGED = range(2)
NM_TRAIN_YARD, NM_TRAIN_CUT, NM_TRAIN_PLATFORM, NM_TRAIN_TAKEN = range(4)
NM_DOLE_ALIVE, NM_DOLE_BY_PLAYER, NM_DOLE_OTHERWISE = range(3)
NM_STAMP_NONE, NM_STAMP_KEPT, NM_STAMP_SIGNED, NM_STAMP_TAKEN = 0, 61, 62, 63
NM_YARD_HELD, NM_YARD_WITHDRAWN, NM_YARD_VACANT = range(3)
NM_SCENE_NONE, NM_SCENE_DEPART, NM_SCENE_RUN, NM_SCENE_FORWARD, NM_SCENE_REVERSE, NM_SCENE_RETURN, NM_SCENE_SALE, NM_SCENE_DEFEAT = range(8)
NM_YARD_NONE, NM_YARD_COUNTERSIGN, NM_YARD_AUTHORITY = range(3)
NM_GO_NONE, NM_GO_DEPART, NM_GO_REJOIN, NM_GO_WALK = range(4)
NM_AT_NOTHING, NM_AT_OPEN, NM_AT_CLEAR = range(3)
NM_HOW_SEEN, NM_HOW_TOLD = 1, 2
NM_GREET_NONE, NM_GREET_GATE, NM_GREET_ALERTED, NM_GREET_SOLD = range(4)
NM_SQ01_SOLD = 5
NM_SHARE_CAPS = 150

OBJECTIVES = (10, 20, 40, 55, 70, 80, 90)
# Where the player stands: the zones a scene sets them down in.
MERCY, YARD, CUT, PLATFORM = "Mercy", "the yard", "the Cut", "the platform"


@dataclass
class Line:
    # ---- the world, as a test sets it
    main_over: bool = True          # the dispatch delivered, acknowledged, and the debrief ended
    lockridge: bool = True          # alive and there
    billie: bool = True
    dole: bool = True
    rifles: List[bool] = field(default_factory=lambda: [True, True, True])
    sheriff: bool = True            # Owen Pritchard, at Mercy
    sq01_outcome: int = 0           # TLM_G_SQ01_Outcome, as the side quest left it
    yard_alerted: bool = False      # TLM_G_SQ01_YardAlerted
    caps_bound: bool = True
    rules_pages: int = 4
    flyleaf_pages: int = 2
    refused: Set[str] = field(default_factory=set)   # requests the game does not honour: "caps", "hymnal", "stamp"

    # ---- the road
    zones_up: bool = False
    where: str = MERCY
    stages: Set[int] = field(default_factory=set)
    shown: Dict[int, bool] = field(default_factory=dict)
    ticked: Dict[int, bool] = field(default_factory=dict)
    claim: int = NM_NONE
    scene: int = NM_SCENE_NONE
    yard_scene: int = NM_YARD_NONE
    outcome: int = NM_NONE
    mail: int = NM_MAIL_ABOARD
    engine: int = NM_ENGINE_SOUND
    train: int = NM_TRAIN_YARD
    dole_fate: int = NM_DOLE_ALIVE
    stamp: int = NM_STAMP_NONE
    stamp_delivered: bool = False
    yard_authority: int = NM_YARD_HELD
    reported: bool = False
    mail_through: bool = False
    mail_sold: bool = False
    line_closed: bool = False
    dole_lives: bool = False
    silver_rail: bool = False
    ostrander_known: bool = False
    lockridge_stamping: bool = False
    lockridge_signed: bool = False
    lockridge_reported: bool = False
    billie_drives: bool = False
    dole_met: bool = False
    fight: bool = False             # the player chose it: Dole and the Black Rail are on the player
    share_pending: bool = False
    share_paid: bool = False
    billie_released: bool = False
    billie_reported: bool = False
    hymnal_shown: bool = False
    ran_said: bool = False
    backed_said: bool = False

    # ---- what the player was given, and what the game was asked for
    caps: int = 0
    hymnals: int = 0
    stamps: int = 0                 # in the player's inventory
    stamps_with_sheriff: int = 0
    asked: Dict[str, int] = field(default_factory=dict)

    # ================================================================ queries
    def done(self, stage: int) -> bool:
        return stage in self.stages

    def road_open(self) -> bool:
        return self.zones_up and self.done(10)

    def assigned(self) -> bool:
        return self.done(20) or self.done(21)

    def dispatches(self) -> bool:
        return self.yard_authority == NM_YARD_HELD

    def dole_can_speak(self) -> bool:
        return self.dole and not self.fight

    def anybody_dead(self) -> bool:
        return not (self.lockridge and self.billie and self.dole and all(self.rifles))

    def at_the_cut(self) -> bool:
        return self.done(40) and self.train == NM_TRAIN_CUT

    def train_offered(self) -> int:
        if not self.road_open() or not self.at_the_cut() or self.scene != NM_SCENE_NONE or self.mail != NM_MAIL_ABOARD:
            return NM_AT_NOTHING
        if self.outcome == NM_NONE and self.claim == NM_NONE:
            return NM_AT_OPEN
        if self.outcome == NM_DEFEAT:
            return NM_AT_CLEAR
        return NM_AT_NOTHING

    def go_offered(self) -> int:
        if not self.road_open() or self.scene != NM_SCENE_NONE:
            return NM_GO_NONE
        if self.train == NM_TRAIN_CUT:
            return NM_GO_REJOIN
        if self.assigned() and self.train == NM_TRAIN_YARD and self.mail == NM_MAIL_ABOARD and self.claim == NM_NONE and self.outcome == NM_NONE:
            return NM_GO_DEPART
        if self.done(40):
            return NM_GO_WALK
        return NM_GO_NONE

    def greeting(self) -> int:
        if not self.road_open() or self.assigned() or self.claim != NM_NONE or self.outcome != NM_NONE or not self.dispatches():
            return NM_GREET_NONE
        if self.yard_alerted:
            return NM_GREET_ALERTED
        if self.sq01_outcome == NM_SQ01_SOLD:
            return NM_GREET_SOLD
        return NM_GREET_GATE

    def share_offered(self) -> bool:
        return (self.train_offered() == NM_AT_OPEN and self.dole_can_speak()
                and not self.share_paid and not self.share_pending and self.caps_bound)

    def can_complete(self) -> bool:
        return self.outcome != NM_NONE and self.scene == NM_SCENE_NONE

    def stamp_undecided(self) -> bool:
        return self.done(60) and self.stamp == NM_STAMP_NONE and self.yard_scene == NM_YARD_NONE

    def can_show_hymnal(self) -> bool:
        return (self.road_open() and not self.hymnal_shown and self.hymnals > 0 and self.lockridge and self.dispatches()
                and self.dole and self.stamp == NM_STAMP_NONE and self.yard_scene == NM_YARD_NONE)

    def can_hand_over(self) -> bool:
        return self.stamp == NM_STAMP_TAKEN and not self.stamp_delivered and self.stamps > 0 and self.sheriff

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
        self._retire(20)
        if self.outcome == NM_DEFEAT and self.mail == NM_MAIL_ABOARD:
            self._show(70)
        self._show(80)

    # ==================================================================== travel
    def travel(self, go: bool = True) -> List[str]:
        if not self.main_over:
            return ["NoteTravelNotYet"]
        shown = ["AskTravelAgain" if self.done(100) else "AskTravel"]
        if go:
            self.zones_up = True
            self.where = YARD
            if not self.done(10):
                self.stages.add(10)
                self._show(10)
        return shown

    def leave(self, go: bool = True) -> List[str]:
        """An exit at the yard or the platform."""
        if not self.zones_up:
            return []
        if self.done(100):
            shown = ["AskLeaveAgain"]
        elif self.can_complete():
            shown = ["AskLeaveResolved"]
        else:
            shown = ["AskLeaveUnresolved"]
        if not go:
            return shown
        self.where = MERCY
        if self.done(100):
            return shown
        if self.can_complete():
            self._tick(80)
            self._retire(70)
            self.stages.add(100)
            shown.append("NoteRoadComplete")
        else:
            shown.append("NoteLeftUnresolved")
        return shown

    def back_to_yard(self, go: bool = True) -> List[str]:
        """On foot from the Cut or the platform. Settles nothing."""
        if not self.road_open():
            return []
        # Never shut, whatever was begun and not seen: no scene is tried again by it.
        shown = ["AskBackToYard"]
        if go:
            self.where = YARD
        return shown

    def _resume(self) -> Optional[List[str]]:
        """A scene of the train that was begun and not seen finished is tried again by any control of the
        train. In this model every scene is seen finished, so there is never one."""
        return None

    # ================================================================ the items
    def _give(self, what: str) -> bool:
        self.asked[what] = self.asked.get(what, 0) + 1
        return what not in self.refused

    # ========================================================== Augusta Lockridge
    def talk_lockridge(self, pick: Optional[str] = None, show: Optional[bool] = None, stamp: Optional[str] = None,
                       confirm: bool = True, morning: Optional[bool] = True) -> List[str]:
        """pick: at her gate greeting "ride", "hymns", "rails" or "no"; after a run "rails" or None.
        show: with the hymnal in hand, True to show it, False for "not now".
        stamp: once the drawer is open, "keep", "sign", "take" or "close". confirm: the countersigning's notice.
        morning: after a sale, True to let Billie's return and report be shown, False for "not now"."""
        if not self.road_open() or not self.lockridge:
            return []
        if not self.dispatches():
            return ["NoteNoDispatch"]
        if self.outcome == NM_SOLD:
            return self._after_sale(morning)
        shown: List[str] = []
        if self.can_show_hymnal():
            shown.append("AskShowHymnal")
            if show:
                shown.append("LockridgeHymnal")
                self.hymnal_shown = True
                self._find_stamp()
                self._decide(shown, stamp, confirm)
                return shown
            if show is None:
                return shown
        greet = self.greeting()
        if greet != NM_GREET_NONE:
            self._gate(shown, greet, pick)
        elif self.outcome == NM_RUN and self.mail == NM_MAIL_DELIVERED and not self.done(60):
            shown.append("LockridgeAfterRan")
            if pick == "rails":
                shown.append("LockridgeRails")
        elif self.outcome == NM_DEFEAT and not self.dole and not self.ostrander_known:
            shown.append("LockridgeAfterDole")
        else:
            shown.append("LockridgeDefault")
        return shown

    def _gate(self, shown, greet, pick):
        if greet == NM_GREET_ALERTED:
            shown.append("LockridgeGateAlerted")
            allowed = ("ride", "rails", "no")
        elif greet == NM_GREET_SOLD:
            shown.append("LockridgeGateSold")
            allowed = ("ride", "hymns", "no")
        else:
            shown += ["LockridgeGateA", "LockridgeGateB"]
            allowed = ("ride", "hymns", "rails", "no")
        if pick not in allowed:
            if pick is not None:
                raise AssertionError("that greeting has no button %r" % pick)
            return
        if pick == "ride":
            shown.append("LockridgeHired" if self.billie else "NoteAssignedNoBillie")
            self.stages.add(20)
            self._tick(10)
            self._show(20)
        elif pick == "hymns":
            shown.append("LockridgeDole")
        elif pick == "rails":
            shown.append("LockridgeRails")

    def _after_sale(self, morning) -> List[str]:
        if self.billie_reported:
            return ["LockridgeAfterSold"]
        if not (self.billie_released and self.billie):
            return ["NoteSaleStatus"]
        shown = ["AskBillieReport"]
        if morning:
            self.billie_reported = True
            shown.append("LockridgeAfterSold")
        elif morning is False:
            shown.append("NoteSaleStatus")
        return shown

    # ================================================================ the drawer
    def _find_stamp(self):
        if not self.done(60):
            self.stages.add(60)
            self._tick(55)

    def use_drawer(self, stamp: Optional[str] = None, confirm: bool = True) -> List[str]:
        """stamp: "keep", "sign", "take" or "close" (her question); without her, "take" or "close"."""
        if not self.road_open():
            return []
        shown: List[str] = []
        if not self.done(60):
            shown.append("NoteDrawer")
            self._find_stamp()
        self._decide(shown, stamp, confirm)
        return shown

    def _decide(self, shown, stamp, confirm):
        if self.stamp == NM_STAMP_KEPT:
            shown.append("NoteDrawerKept")
            return
        if self.stamp == NM_STAMP_SIGNED:
            shown.append("NoteDrawerSigned")
            return
        if self.stamp == NM_STAMP_TAKEN:
            shown.append("NoteDrawerGone")
            return
        if not self.stamp_undecided():
            return
        hers = self.lockridge and self.dispatches()
        shown.append("LockridgeStamp" if hers else "AskStampAlone")
        if stamp == "keep" and hers:
            self.stamp = NM_STAMP_KEPT
            self.lockridge_stamping = True
            self.stages.add(61)
            shown.append("NoteStampKept")
        elif stamp == "sign" and hers:
            shown.append("AskCountersignScene")
            if confirm:
                self.stamp = NM_STAMP_SIGNED
                self.lockridge_signed = True
                self.stages.add(62)
                shown.append("NoteCountersigned")
        elif stamp == "take":
            if self.asked.get("stamp", 0) or not self._give("stamp"):
                # Asked for once. Not seen to arrive: nothing was taken, and it is never asked for again.
                shown.append("NoteStampFailed")
                return
            self.stamps += 1
            self.stamp = NM_STAMP_TAKEN
            self.stages.add(63 if self.lockridge else 64)
            self._show(90)
            shown.append("NoteStampTaken")
        elif stamp in ("keep", "sign"):
            raise AssertionError("nobody is at the desk to answer %r" % stamp)

    def use_board(self) -> List[str]:
        if not self.road_open():
            return []
        if self.yard_authority != NM_YARD_HELD:
            return ["LabelBoardClosed"]
        return ["LabelBoardSigned" if self.stamp == NM_STAMP_SIGNED else "LabelBoardStamped"]

    # ============================================================== Billie Tupper
    def talk_billie(self, pick: Optional[str] = None, confirm: bool = True) -> List[str]:
        """On the footplate before leaving: "cut" to ask what is in it. At the lanterns: "run", "down" or "back"."""
        if not self.road_open():
            return []
        resumed = self._resume()
        if resumed is not None:
            return resumed
        if not self.billie:
            return []
        if self.outcome == NM_SOLD and self.billie_released:
            return ["BillieWalking"]
        if self.train_offered() == NM_AT_OPEN:
            return self._in_cut(pick, confirm, True)
        if self.outcome == NM_RUN and self.billie_drives and not self.ran_said:
            self.ran_said = True
            return ["BillieRan"]
        if self.outcome == NM_BACKED and self.billie_drives and not self.backed_said and not self.anybody_dead():
            self.backed_said = True
            return ["BillieBacked"]
        if self.assigned() and not self.done(40) and self.train == NM_TRAIN_YARD and self.outcome == NM_NONE:
            shown = ["BillieFootplate"]
            if pick == "cut":
                shown.append("BillieCutBefore")
            return shown
        return ["BillieDefault"]

    # ==================================================================== the train
    def use_depart(self, go: bool = True) -> List[str]:
        if not self.road_open():
            return []
        resumed = self._resume()
        if resumed is not None:
            return resumed
        offered = self.go_offered()
        shown: List[str] = []
        if offered == NM_GO_NONE:
            if self.assigned() or self.train != NM_TRAIN_YARD or self.outcome != NM_NONE or self.claim != NM_NONE:
                return ["NoteTrainNothing"]
            if self.lockridge and self.dispatches():
                return ["NoteNotAssigned"]
            shown.append("AskBoard")
            if not go:
                return shown
            self.stages.add(21)
            self._retire(10)
            self._show(20)
            offered = self.go_offered()
        if offered in (NM_GO_REJOIN, NM_GO_WALK):
            shown.append("AskRejoin" if offered == NM_GO_REJOIN else "AskWalkToCut")
            if go:
                self.where = CUT
            return shown
        shown.append("AskDepartScene")
        if not go:
            return shown
        self.stages.add(30 if self.billie else 31)
        self._tick(20)
        self.train = NM_TRAIN_CUT
        self.where = CUT
        self.stages.add(40)
        self._show(40)
        self._show(55)
        return shown

    def use_train(self, pick: Optional[str] = None, confirm: bool = True) -> List[str]:
        """The regulator or the reverser at the Cut. Unsettled: "run", "down" or "back". After Dole's defeat:
        "forward", "back" or "leave"."""
        if not self.road_open():
            return []
        resumed = self._resume()
        if resumed is not None:
            return resumed
        at = self.train_offered()
        if at == NM_AT_OPEN:
            return self._in_cut(pick, confirm, self.billie)
        if at == NM_AT_CLEAR:
            shown = ["AskAfterDefeat"]
            if pick == "forward":
                shown.append("AskForwardScene")
                if confirm:
                    self.billie_drives = self.billie
                    self.mail = NM_MAIL_DELIVERED
                    self.mail_through = True
                    self.train = NM_TRAIN_PLATFORM
                    self.where = PLATFORM
                    self._tick(70)
                    shown.append("NoteForwardDone")
            elif pick == "back":
                shown.append("AskCarryBackScene")
                if confirm:
                    self.billie_drives = self.billie
                    self.mail = NM_MAIL_RETAINED
                    self.train = NM_TRAIN_YARD
                    self.where = YARD
                    self._tick(70)
                    shown.append("NoteCarriedBack")
            return shown
        return ["NoteTrainNothing"]

    def _in_cut(self, pick, confirm, hers) -> List[str]:
        shown = ["BillieInCut" if hers else "AskRegulator"]
        if pick == "run":
            shown.append("AskRunScene")
            if not confirm:
                return shown
            self.claim = NM_RUN
            self.billie_drives = self.billie
            self.outcome = NM_RUN
            self.mail = NM_MAIL_DELIVERED
            self.mail_through = True
            self.engine = NM_ENGINE_DAMAGED
            self.train = NM_TRAIN_PLATFORM
            self.where = PLATFORM
            if self.dole:
                self.dole_lives = True
            self.stages.add(41 if self.billie_drives else 46)
            self._course_taken()
            shown.append("NoteRunDone")
            if self.billie_drives and not self.ran_said:
                shown.append("BillieRan")
                self.ran_said = True
        elif pick == "back":
            shown.append("AskReverseScene")
            if not confirm:
                return shown
            self.claim = NM_BACKED
            self.billie_drives = self.billie
            self.outcome = NM_BACKED
            self.mail = NM_MAIL_RETAINED
            self.line_closed = True
            self.train = NM_TRAIN_YARD
            self.where = YARD
            if self.dole and self.dole_met:
                self.dole_lives = True
            self.stages.add(44 if self.billie_drives else 49)
            self._course_taken()
            shown.append("NoteBackedOut")
            if self.billie_drives and not self.anybody_dead() and not self.backed_said:
                shown.append("BillieBacked")
                self.backed_said = True
        return shown

    # ================================================================ Ezekiel Dole
    def talk_dole(self, picks=()) -> List[str]:
        """picks, in order: at his sermon "aside", "share", "name" or "back"; at his name "silver", "aside" or
        "share"; at his silver "aside" or "share"; at his offer "done", "no" or "back"."""
        if not self.road_open():
            return []
        resumed = self._resume()
        if resumed is not None:
            return resumed
        if not self.dole_can_speak():
            return []
        if self.train_offered() != NM_AT_OPEN:
            return ["DoleDefault"]
        picks = list(picks)
        shown = ["DoleSermon"]
        # Whichever of his four buttons is pressed, he has spoken to the player and seen their face.
        self.dole_met = True
        self._after(shown, picks.pop(0) if picks else "back", picks, ("aside", "share", "name", "back"))
        return shown

    def _after(self, shown, pick, picks, allowed):
        if pick not in allowed:
            raise AssertionError("that box has no button %r" % pick)
        if pick == "aside":
            shown.append("DoleFace")
            self.fight = True
        elif pick == "share":
            self._share(shown, picks)
        elif pick == "name":
            shown.append("DoleName")
            if not picks:
                raise AssertionError("his name has three buttons and no way to leave it: one has to be pressed")
            self.ostrander_known = True
            self.stages.add(56)
            self._after(shown, picks.pop(0), picks, ("silver", "aside", "share"))
        elif pick == "silver":
            shown.append("DoleSilver")
            if not picks:
                raise AssertionError("his silver has two buttons and no way to leave it: one has to be pressed")
            self.silver_rail = True
            self.stages.add(51)
            self._after(shown, picks.pop(0), picks, ("aside", "share"))

    def _share(self, shown, picks):
        if not self.share_offered():
            shown.append("NoteShareFailed")
            return
        if self.billie:
            shown.append("DoleShare")
        else:
            shown += ["DoleShareNoBillie", "AskShareOffer"]
        pick = picks.pop(0) if picks else None
        if pick == "no":
            shown.append("DoleFace")
            self.fight = True
        elif pick == "done":
            self.share_pending = True
            if not self._give("caps"):
                shown.append("NoteShareFailed")
                return
            self.claim = NM_SOLD
            self.caps += NM_SHARE_CAPS
            self.share_paid = True
            self.share_pending = False
            self.billie_released = self.billie
            self.outcome = NM_SOLD
            self.mail = NM_MAIL_SEIZED
            self.mail_sold = True
            self.train = NM_TRAIN_TAKEN
            self.dole_lives = True
            self.stages.add(43 if self.billie_released else 48)
            self._course_taken()
            shown.append("NoteSold" if self.billie_released else "NoteSoldNoBillie")
        elif pick not in (None, "back"):
            raise AssertionError("his offer has no button %r" % pick)

    def dole_dies(self, by_player: bool) -> List[str]:
        """He is killed. In the unsettled encounter that is the outcome "Dole defeated"; the Black Rail who
        live go up the hill. Otherwise it is only his death."""
        if not self.dole:
            return []
        self.dole = False
        self.dole_lives = False
        self.fight = False
        if self.at_the_cut() and self.claim == NM_NONE and self.outcome == NM_NONE:
            self.claim = NM_DEFEAT
            self.dole_fate = NM_DOLE_BY_PLAYER if by_player else NM_DOLE_OTHERWISE
            self.outcome = NM_DEFEAT
            self.stages.add(42 if by_player else 47)
            self._course_taken()
            return ["NoteDefeat"]
        self.dole_fate = NM_DOLE_OTHERWISE
        if not self.done(42) and not self.done(47):
            self.stages.add(47)
        return []

    # =================================================================== evidence
    def use_plate(self) -> List[str]:
        if not self.road_open():
            return []
        self.silver_rail = True
        self.stages.add(50)
        return ["NotePlate"]

    def read_hymnal(self) -> List[str]:
        if not self.road_open():
            return []
        shown = ["FlyleafPage%d" % (i + 1) for i in range(self.flyleaf_pages)]
        first = not self.done(55)
        self.ostrander_known = True
        self.stages.add(55)
        if first and self._give("hymnal"):
            self.hymnals += 1
        return shown

    def read_rules(self) -> List[str]:
        return ["RulesPage%d" % (i + 1) for i in range(self.rules_pages)] if self.road_open() else []

    def read_chalk(self) -> List[str]:
        return ["ChalkPage1"] if self.road_open() else []

    def use_cargo(self) -> List[str]:
        if not self.road_open():
            return []
        resumed = self._resume()
        if resumed is not None:
            return resumed
        return [{NM_MAIL_DELIVERED: "LabelCargoDelivered", NM_MAIL_RETAINED: "LabelCargoRetained",
                 NM_MAIL_SEIZED: "LabelCargoSeized"}.get(self.mail, "LabelCargoAboard")]

    # ============================================================== the report
    def report(self, give: Optional[bool] = True, hand: Optional[bool] = True, acknowledge: bool = True) -> List[str]:
        """What Pritchard's conversation shows of the Night Mail. give: True for "[Report on Iron Junction]",
        False for "[Later]". hand: True for "[Hand the stamp to Pritchard]", False for "[Keep it for now]".
        [] if nothing is due."""
        if not self.zones_up or not self.done(10) or not self.sheriff:
            return []
        shown: List[str] = []
        if self.done(100) and not self.reported:
            shown.append("ReportKnown" if self.silver_rail else "ReportUnknown")
            if give:
                self.reported = True
                shown.append({NM_MAIL_DELIVERED: "ReportMailDelivered", NM_MAIL_RETAINED: "ReportMailRetained",
                              NM_MAIL_SEIZED: "ReportMailSeized"}.get(self.mail, "ReportMailAboard"))
                if self.outcome == NM_RUN:
                    shown.append("ReportRan")
                elif self.outcome == NM_SOLD:
                    shown.append("ReportSold")
                elif self.outcome == NM_BACKED:
                    shown.append("ReportBacked")
                else:
                    shown.append("ReportDoleByYou" if self.dole_fate == NM_DOLE_BY_PLAYER else "ReportDoleDead")
                if self.silver_rail and self.ostrander_known:
                    shown.append("ReportKnowBoth")
                elif self.silver_rail:
                    shown.append("ReportKnowSilver")
                elif self.ostrander_known:
                    shown.append("ReportKnowName")
                else:
                    shown.append("ReportKnowNeither")
                shown.append("ReportEnd")
            elif give is None:
                return shown
        if self.can_hand_over():
            shown.append("AskHandOver")
            if hand:
                self.stamps -= 1
                self.stamps_with_sheriff += 1
                self.stamp_delivered = True
                self._tick(90)
                shown.append("NoteStampDelivered")
            elif hand is None:
                return shown
        if self.stamp_delivered and self.yard_authority == NM_YARD_HELD:
            shown.append("NoteAuthorityWithdrawn" if self.lockridge else "NoteAuthorityVacant")
            if acknowledge:
                self.yard_authority = NM_YARD_WITHDRAWN if self.lockridge else NM_YARD_VACANT
                self.lockridge_reported = True
        return shown

    # ============================================================ what must hold
    def problems(self) -> List[str]:
        out = []
        s = self.stages
        if self.outcome not in (NM_NONE, NM_RUN, NM_DEFEAT, NM_SOLD, NM_BACKED):
            out.append("an outcome that is none of the four")
        logs = {NM_RUN: (41, 46), NM_DEFEAT: (42, 47), NM_SOLD: (43, 48), NM_BACKED: (44, 49)}
        for course, pair in logs.items():
            here = [n for n in pair if n in s]
            if course == NM_DEFEAT:
                # 47 is also the note of a death that is not the outcome.
                if 42 in s and self.outcome != NM_DEFEAT:
                    out.append("stage 42 without the outcome Dole defeated")
                continue
            if here and self.outcome != course:
                out.append("stage %s without its outcome" % here)
            if len(here) > 1:
                out.append("both journals of one outcome: %s" % here)
            if self.outcome == course and not here:
                out.append("outcome %d with no journal" % course)
        if self.outcome == NM_DEFEAT and not (42 in s or 47 in s):
            out.append("Dole defeated with no journal")
        if self.outcome == NM_DEFEAT and self.dole:
            out.append("Dole defeated, and alive")
        if (42 in s) != (self.dole_fate == NM_DOLE_BY_PLAYER):
            out.append("a kill credited to the player that is not stage 42, or the other way about")
        if self.mail_through != (self.mail == NM_MAIL_DELIVERED):
            out.append("mail_through does not say where the mail is")
        if self.mail_sold != (self.outcome == NM_SOLD) or (self.mail == NM_MAIL_SEIZED) != (self.outcome == NM_SOLD):
            out.append("mail_sold, the seized mail and the sale do not agree")
        if self.line_closed != (self.outcome == NM_BACKED):
            out.append("line_closed without the back-out, or the other way about")
        if self.mail == NM_MAIL_DELIVERED and self.outcome not in (NM_RUN, NM_DEFEAT):
            out.append("mail delivered by neither the run nor a train taken forward after Dole's defeat")
        if self.mail == NM_MAIL_RETAINED and self.outcome not in (NM_BACKED, NM_DEFEAT):
            out.append("mail retained by neither the back-out nor a train taken back after Dole's defeat")
        if self.engine == NM_ENGINE_DAMAGED and self.outcome != NM_RUN:
            out.append("a damaged engine without the run")
        if self.dole_lives and not self.dole:
            out.append("dole_lives of a dead man")
        if self.outcome == NM_SOLD and not (self.share_paid and self.caps == NM_SHARE_CAPS):
            out.append("a sale without exactly one payment")
        if self.caps not in (0, NM_SHARE_CAPS) or self.asked.get("caps", 0) > 1:
            out.append("caps paid other than once: %d, asked %d times" % (self.caps, self.asked.get("caps", 0)))
        if self.silver_rail != (50 in s or 51 in s):
            out.append("silver known without either way of learning it")
        if self.ostrander_known != (55 in s or 56 in s):
            out.append("the name known without either way of learning it")
        if self.hymnals and 55 not in s:
            out.append("a hymnal held without its flyleaf read")
        if self.hymnals > 1 or self.asked.get("hymnal", 0) > 1:
            out.append("more than one hymnal")
        decisions = [n for n in (61, 62) if n in s] + (["taken"] if 63 in s or 64 in s else [])
        if len(decisions) > 1:
            out.append("more than one decision about the stamp: %s" % decisions)
        if decisions and 60 not in s:
            out.append("a decision about a stamp that was not found")
        if self.lockridge_stamping != (61 in s) or self.lockridge_signed != (62 in s):
            out.append("the stamping or signing flag does not match its stage")
        if self.stamps + self.stamps_with_sheriff > 1 or self.asked.get("stamp", 0) > 1:
            out.append("more than one stamp")
        if (self.stamps + self.stamps_with_sheriff > 0) != (self.stamp == NM_STAMP_TAKEN):
            out.append("a stamp out of the drawer without the decision to take it")
        if self.stamp_delivered != (self.stamps_with_sheriff == 1):
            out.append("delivered does not say where the stamp is")
        if self.lockridge_reported != (self.stamp_delivered and self.yard_authority != NM_YARD_HELD):
            out.append("lockridge_reported is not the stamp delivered and the yard without a master")
        if self.yard_authority != NM_YARD_HELD and not self.stamp_delivered:
            out.append("the yard without a master before Pritchard had the stamp")
        if 100 in s and self.outcome == NM_NONE:
            out.append("complete with no outcome")
        if self.reported and 100 not in s:
            out.append("reported before the road was complete")
        if 40 in s and not (30 in s or 31 in s):
            out.append("in the Cut without having boarded")
        if (30 in s or 31 in s) and not (20 in s or 21 in s):
            out.append("boarded without the job")
        if 20 in s and 21 in s:
            out.append("the job both given and taken unasked")
        return out
