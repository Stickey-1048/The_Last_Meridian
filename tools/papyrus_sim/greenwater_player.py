"""Somebody playing the Greenwater road on the stand-in engine, and the road's
model keeping step (GREENWATER-STORY-001). Used by test_greenwater*.py.

The real scripts are driven the way the game drives them: the stand-in's
person plays the first section to its end, walks up to a piece or a person,
presses the button on it, answers the boxes that open by the place of a
button, and walks into the trigger boxes. After every action what was shown,
in order, and everything the road then holds are compared with
tools/logic_model/greenwater_model.py.

NONE OF THIS HAS BEEN SEEN IN THE GAME. Not a compile and not a game test.
"""
import copy
import json
import sys

from sim import Actor, GlobalVariable, unwrap
from test_sim import PLUGIN, ROOT, SCRIPTS
from test_act1 import BRIEF_HUB, MSG, REF, Person

sys.path.insert(0, str(ROOT / "tools" / "logic_model"))
import greenwater_model as gw                                     # noqa: E402
from greenwater_model import River                                # noqa: E402

G = "TLM_MSG_GW_"
R = "TLM_REF_GW_"
ROAD = "TLM_MQ02B"
STAGE = "TLM_GW"
OBJECTIVES = (10, 20, 40, 50, 60, 80)

# The place of each button, by what the model calls the choice.
JUDGE = {"hang": 0, "custody": 1, "release": 2}
INDEX = {
    "AskTravel": {True: 0, False: 1}, "AskTravelAgain": {True: 0, False: 1},
    "AskLeaveResolved": {True: 0, False: 1}, "AskLeaveUnresolved": {True: 0, False: 1}, "AskLeaveAgain": {True: 0, False: 1},
    "OpalFirst": {"wants": 0, "guns": 1, "bowl": 2},
    "OpalAfterWon": JUDGE, "OpalAfterWonNoSheriff": {"hang": 0, "release": 1},
    "AskLie": {True: 0, False: 1},
    "RaffertySkiff": {"gangway": 0, "offside": 1, "confess": 2},
    "RaffertyChain": {"cut": 0, "burn": 1, "notyet": 2}, "AskChain": {"cut": 0, "burn": 1, "notyet": 2},
    "HatcherTable": {"deal": 0, "share": 1, "paid": 2, "leave": 3},
    "HatcherTableNoShare": {"deal": 0, "paid": 1, "leave": 2},
    "HatcherLost": JUDGE, "HatcherLostNoSheriff": {"hang": 0, "release": 1, "silent": 2},
    "HatcherLostNoOpal": {"custody": 0, "release": 1, "silent": 2}, "HatcherLostAlone": {"release": 0, "silent": 1},
    "HatcherWon": {"share": 0, "leave": 1}, "HatcherWonNoShare": {"leave": 0},
    "HatcherShare": {True: 0, False: 1},
    "AskFire": {True: 0, False: 1},
    "ReportKnown": {True: 0, False: 1}, "ReportUnknown": {True: 0, False: 1},
}


class Player:
    def __init__(self, test, scripts=SCRIPTS, travel=True, finish=True, with_ledger=False, charisma=4.0, refuse=(), sheriff=True):
        self.test = test
        self.p = Person(test, scripts=scripts)
        self.s = s = self.p.s
        self.road = s.quests[ROAD]
        self.stage = s.quests[STAGE]
        self.rules = self.road.scripts[0]
        self.walk = self.stage.scripts[0]
        plugin = json.loads(PLUGIN.read_text())
        self.buttons = {m["EditorId"]: len(m["Buttons"]) for m in plugin["Messages"]}
        self.caps = self.p.caps
        self.letter = s.forms["TLM_BOOK_LetterOfHire"]
        self.meal = self.rules.props.get("meal")
        self.who = {"opal": s.placed[R + "Opal"], "hatcher": s.placed[R + "Hatcher"], "rafferty": s.placed[R + "Rafferty"],
                    "belden": s.placed[R + "Belden"], "crew1": s.placed[R + "Crew1"], "crew2": s.placed[R + "Crew2"],
                    "sheriff": s.placed[REF + "Pritchard"]}
        s.player_values["Charisma"] = float(charisma)
        s.player_base_values["Charisma"] = float(charisma)
        # SEEDED by a test: requests for an item that the game does not honour: "caps", "letter", "food".
        self.refuse = set(refuse)
        self.asked = {"caps": 0, "letter": 0, "food": 0}
        self._count()
        self._seed_calls()
        refused = set(self.refuse) - {"food"}
        if "food" in self.refuse:
            refused |= {"bowl", "cup", "relief"}
        self.m = River(charisma=float(charisma), refused=refused, meal_bound=self.meal is not None,
                       caps_bound=self.rules.props.get("caps") is not None, charisma_bound=self.rules.props.get("charisma") is not None,
                       letter_pages=len([m for m in self.buttons if m.startswith(G + "LetterPage")]))
        self.with_ledger = with_ledger
        if finish:
            self.finish_chapter()
        if not sheriff:
            self.kill("sheriff")
        self.caps_before = s.player.inventory.get(self.caps, 0)
        self.before = self.world()
        if travel:
            self.travel()
            self.step_onto_landing()

    # ---------------------------------------------------------------- set-up
    def finish_chapter(self):
        p = self.p
        p.press("Dispatch", events=["take_dispatch"])
        if self.with_ledger:
            p.press("Ledger", events=["take_ledger"])
            p.press("BrakeShoes", boxes={"TLM_MSG_E1": [0]}, events=["examine_e1"])
        p.to_town()
        p.hand_over("DebriefMissed", more=self.with_ledger)
        self.test.assertEqual(p.g("TLM_G_MQ01_Done"), 1)

    def _count(self):
        s = self.s
        add = s.n_objectreference_additem

        def count_add(ref, context, form, count=1, silent=False):
            form_ = unwrap(form)
            what = "caps" if form_ is self.caps else "letter" if form_ is self.letter else "food" if form_ is self.meal and self.meal is not None else None
            if what and ref is s.player and self.road.running:
                self.asked[what] += 1
                if what in self.refuse:
                    return None                                   # SEEDED: the game does not honour the request
            return add(ref, context, form, count, silent)
        s.n_objectreference_additem = count_add

    # --------------------------------------------- calls the game does not carry out
    def _seed_calls(self):
        """SEEDED, for a test, and off unless a test asks: a call into the game that does nothing, something
        that happens just before a call, or a death that comes late. These are NOT rules about the game. They
        are ways a call could fail to do what was asked, which the scripts must not take for its having been
        done. Every call of these kinds is counted, refused or not: enable, disable, moveto, kill, startcombat."""
        s = self.s
        self.refused_calls = {}                    # (kind, who or what) -> None: every time; a number: that many more times
        self.before_call = {}                      # (kind, who or what) -> something to do just before that call
        self.late_death = {}                       # who -> seconds after Kill at which the death happens
        self.calls = []                            # (kind, who or what, carried out)
        self._kill = kill = s.n_actor_kill

        def wrapped(kind, native):
            def call(ref, context, *args):
                key = (kind, s._whom(ref))
                if key in self.before_call:
                    self.before_call[key]()
                left = self.refused_calls.get(key, 0)
                if key in self.refused_calls and (left is None or left > 0):
                    if left is not None:
                        self.refused_calls[key] = left - 1
                    self.calls.append(key + (False,))
                    return None                                   # SEEDED: asked, and nothing happens
                self.calls.append(key + (True,))
                return native(ref, context, *args)
            return call
        s.n_objectreference_enable = wrapped("enable", s.n_objectreference_enable)
        s.n_objectreference_enablenowait = wrapped("enable", s.n_objectreference_enablenowait)
        s.n_objectreference_disable = wrapped("disable", s.n_objectreference_disable)
        s.n_objectreference_moveto = wrapped("moveto", s.n_objectreference_moveto)
        s.n_actor_startcombat = wrapped("startcombat", s.n_actor_startcombat)

        def late_or_not(actor, context, killer=None):
            whom = s._whom(actor)
            seconds = self.late_death.get(whom)
            if seconds is None:
                return kill(actor, context, killer)

            def die():
                kill(actor, None, killer)
                return
                yield
            s.later(seconds, "SEEDED: the death of %s, %s seconds after Kill" % (whom, seconds), die, exact=True)
            return None
        s.n_actor_kill = wrapped("kill", late_or_not)

    def _key(self, kind, what):
        if what in self.who:
            return (kind, self.s._whom(self.who[what]))
        return (kind, what if what.startswith("TLM_") else R + what)

    def refuse_call(self, kind, what, times=None):
        """SEEDED: "enable", "disable", "moveto" or "kill" on that person or piece does nothing: every time, or
        the next `times` times."""
        self.refused_calls[self._key(kind, what)] = times

    def allow_calls(self):
        self.refused_calls.clear()
        self.before_call.clear()
        self.late_death.clear()

    def just_before(self, kind, what, do):
        """SEEDED: `do` happens just before that call is carried out."""
        self.before_call[self._key(kind, what)] = do

    def dies_late(self, who, seconds):
        """SEEDED: Kill on that person takes effect only that many seconds later."""
        self.late_death[self.s._whom(self.who[who])] = seconds

    def asked_of(self, kind, what):
        """How often that call was made on that person or piece, carried out or not."""
        key = self._key(kind, what)
        return len([c for c in self.calls if c[:2] == key])

    def alias(self, name, quest=None):
        """The alias of that name on the greybox's quest (or on the road's)."""
        q = quest or self.stage
        return [a for a in q.aliases.values() if a.name == name][0]

    def kill(self, who, by_player=None):
        """SEEDED death, as the stand-in's own tests of the first section do it. The town's people are protected,
        so only the player can kill them; Hatcher and his crew die by other hands unless a test says otherwise."""
        actor = self.who[who]
        if who == "sheriff":
            actor.dead = True                                     # the first section keeps Pritchard from dying; simply SEEDED
            self.m.sheriff = False
            return
        if by_player is None:
            by_player = who in ("opal", "rafferty", "belden")
        self._kill(actor, None, self.s.player if by_player else None)         # the game's own: no seed applies
        self.p.pause()
        self.test.assertTrue(actor.dead, who + " did not die")
        if who == "hatcher":
            self.m.hatcher_dies()
        elif who in ("opal", "rafferty", "belden"):
            setattr(self.m, who, False)

    # ------------------------------------------------------- what the game holds
    def g(self, name):
        return self.s.get_global("TLM_G_MQ02B_" + name)

    def count(self, form):
        return self.s.player.inventory.get(form, 0) if form is not None else 0

    def on(self, alias):
        return not self.s.placed[R + alias].disabled

    def facts(self):
        v, q = self.rules.vars, self.road
        return {
            "stages": sorted(q.done),
            "shown": {n: bool(q.displayed.get(n, False)) for n in OBJECTIVES},
            "ticked": {n: bool(q.completed_objectives.get(n, False)) for n in OBJECTIVES},
            "claim": v["claim"], "card": v["cardresult"], "escape pending": bool(v["escapepending"]),
            "return pending": v["returnpending"], "fire warned": bool(v["firewarned"]), "burning": bool(v["burning"]),
            "share pending": bool(v["sharepending"]), "share paid": bool(v["sharepaid"]), "lie told": bool(v["lietold"]),
            "lie heard": bool(v["lieheard"]), "denied said": bool(v["deniedsaid"]),
            "hire read": bool(v["hireread"]), "hire heard": bool(v["hireheard"]),
            "outcome": self.g("Outcome"), "cargo": self.g("Cargo"), "recovered": self.g("Recovered"), "fate": self.g("Hatcher"),
            "grain_home": self.g("GrainHome"), "grain_sold": self.g("GrainSold"), "queen_burned": self.g("QueenBurned"),
            "hatcher_hanged": self.g("HatcherHanged"), "hatcher_friend": self.g("HatcherFriend"),
            "hatcher_hunting": self.g("HatcherHunting"), "silver_river": self.g("SilverRiver"), "reported": self.g("Reported"),
            "caps": self.count(self.caps) - self.caps_before, "food": self.count(self.meal), "letters": self.count(self.letter),
            "asked for caps": self.asked["caps"], "asked for the letter": self.asked["letter"], "asked for food": self.asked["food"],
            "complete": q.completed, "hatcher alive": not self.who["hatcher"].dead,
            "busy": bool(self.walk.vars["talking"]) or bool(v["judging"]) or v["hangintent"] in (1, 2),
        }

    def model_facts(self):
        m = self.m
        food_asked = sum(m.asked.get(k, 0) for k in ("bowl", "cup", "relief"))
        return {
            "stages": sorted(m.stages),
            "shown": {n: bool(m.shown.get(n, False)) for n in OBJECTIVES},
            "ticked": {n: bool(m.ticked.get(n, False)) for n in OBJECTIVES},
            "claim": m.claim, "card": m.card, "escape pending": m.escape_pending, "return pending": m.return_pending,
            "fire warned": m.fire_warned, "burning": m.burning, "share pending": m.share_pending, "share paid": m.share_paid,
            "lie told": m.lie_told, "lie heard": m.lie_heard, "denied said": m.denied_said,
            "hire read": m.hire_read, "hire heard": m.hire_heard,
            "outcome": m.outcome, "cargo": m.cargo, "recovered": m.recovered, "fate": m.fate,
            "grain_home": int(m.grain_home), "grain_sold": int(m.grain_sold), "queen_burned": int(m.queen_burned),
            "hatcher_hanged": int(m.hatcher_hanged), "hatcher_friend": int(m.hatcher_friend),
            "hatcher_hunting": int(m.hatcher_hunting), "silver_river": int(m.silver_river), "reported": int(m.reported),
            "caps": m.caps, "food": m.food, "letters": m.letters,
            "asked for caps": m.asked.get("caps", 0), "asked for the letter": m.asked.get("letter", 0), "asked for food": food_asked,
            "complete": 100 in m.stages, "hatcher alive": m.hatcher,
            "busy": False,
        }

    def world(self):
        """Everything this road must leave alone: the two earlier quests, the briefing, every other global, the
        first section's people, and what the player carries apart from this road's caps, food and letter."""
        s = self.s
        mine = (ROAD, STAGE)
        return {
            "globals": {k: f.value for k, f in s.forms.items() if isinstance(f, GlobalVariable) and not k.startswith("TLM_G_MQ02B_")},
            "stages": {q.editor_id: list(q.done) for q in s.quests.values() if q.editor_id not in mine},
            "objectives": {q.editor_id: (dict(q.displayed), dict(q.completed_objectives)) for q in s.quests.values() if q.editor_id not in mine},
            "completed": {q.editor_id: (q.running, q.completed) for q in s.quests.values() if q.editor_id not in mine},
            "people": {k: (r.dead, r.disabled, r.pos) for k, r in s.placed.items() if isinstance(r, Actor) and k.startswith(REF)},
            "carried": {getattr(f, "editor_id", repr(f)): n for f, n in s.player.inventory.items()
                        if n and f is not self.caps and f is not self.letter and f is not self.meal},
        }

    def same(self, where, world=True):
        t = self.test
        t.assertEqual(self.facts(), self.model_facts(), "the road against its model (game, model) after: " + where)
        t.assertEqual(self.m.problems(), [], where)
        t.assertEqual([l for l in self.s.papyrus_log if l.startswith("error")], [], where)
        if world:
            t.assertEqual(self.world(), self.before, "something outside this road changed after: " + where)

    # ------------------------------------------------------------- one action
    def act(self, piece, want, picks=None, enter=False, also=None, where=None, mercy=None, world=True):
        """Walks to a piece and uses it (or, for a trigger box, walks into it), answering the boxes the model
        expects with the buttons the picks name. What the Greenwater scripts then showed must be what the model
        said. mercy: full ids of other boxes to answer at Mercy (the first section's and the briefing's)."""
        s = self.s
        answers = {m: [0] * 40 for m, n in self.buttons.items() if m.startswith(G) and n == 1}
        # Existing route helpers model explicit acceptance of the new local
        # confirmations. Adverse/cancel tests supply their own exact responses.
        for box in ('ConfirmShare','CardStakes','ConfirmHang','ConfirmCustody','ConfirmRelease'):
            if box in want:answers[G+box]=[0]*40
        explicit = {}
        queues = {box: list(v) if isinstance(v, (list, tuple)) else [v] for box, v in (picks or {}).items()}
        for box in want:
            if box in INDEX:
                choice = queues[box].pop(0) if queues.get(box) else None
                if choice not in INDEX[box]:
                    raise AssertionError("the test gives no button for the box %s (asked for %r)" % (box, choice))
                explicit.setdefault(G + box, []).append(INDEX[box][choice])
        for box, presses in (mercy or {}).items():
            explicit.setdefault(box, []).extend(presses)
        answers.update({m: list(b) for m, b in explicit.items()})
        s.answers = answers
        s.on_box = also
        at = len(s.messages_shown)
        s.walk_to(piece)
        if not enter:
            s.press_activate(piece)
        self.p.pause(4.0)
        s.on_box = None
        left = {m: b for m, b in s.answers.items() if m in explicit and b}
        self.test.assertEqual(left, {}, "boxes the test expected and never saw, at " + piece)
        got = [m[len(G):] for m in s.messages_shown[at:] if m.startswith(G)]
        self.test.assertEqual(got, want, "what was shown at %s, against the model" % piece)
        if where is not False:
            self.same(where or "used " + piece, world=world)
        return s.messages_shown[at:]

    # ------------------------------------------------------------ the actions
    def travel(self, go=True):
        return self.act(R + "MercyTravel", self.m.travel(go), {"AskTravel": go, "AskTravelAgain": go})

    def step_onto_landing(self):
        self.m.step_onto_landing()
        return self.act(R + "LandingSight", [], enter=True)

    def leave(self, go=True):
        return self.act(R + "Exit", self.m.leave(go), {"AskLeaveResolved": go, "AskLeaveUnresolved": go, "AskLeaveAgain": go})

    def opal(self, first=None, judge=None, lie=None):
        want = self.m.talk_opal(first=first, judge=judge, lie=lie)
        return self.act(R + "Opal", want, {"OpalFirst": first, "OpalAfterWon": judge, "OpalAfterWonNoSheriff": judge, "AskLie": lie})

    def rafferty(self, pick=None):
        want = self.m.talk_rafferty(pick)
        return self.act(R + "Rafferty", want, {"RaffertySkiff": pick, "RaffertyChain": pick, "AskChain": pick})

    def skiff(self):
        return self.act(R + "Skiff", self.m.take_skiff())

    def gangway(self):
        self.m.board(gw.BOARD_GANGWAY)
        return self.act(R + "GangwaySight", [], enter=True)

    def offside(self):
        self.m.board(gw.BOARD_OFFSIDE)
        return self.act(R + "OffSideSight", [], enter=True)

    def table(self, picks=(), then=None, done=True, judge=None, piece="Table"):
        want = self.m.use_table(list(picks), then=then, done=done, judge=judge)
        table_picks = list(picks)
        choose = {"HatcherTable": table_picks, "HatcherTableNoShare": table_picks, "HatcherWon": then, "HatcherWonNoShare": "leave",
                  "HatcherShare": done, "HatcherLost": judge, "HatcherLostNoSheriff": judge, "HatcherLostNoOpal": judge,
                  "HatcherLostAlone": judge}
        # The two table boxes share one run of picks; whichever is shown takes the next.
        want_boxes = [b for b in want if b in ("HatcherTable", "HatcherTableNoShare")]
        choose["HatcherTable"] = [p for b, p in zip(want_boxes, table_picks + ["leave"] * 3) if b == "HatcherTable"]
        choose["HatcherTableNoShare"] = [p for b, p in zip(want_boxes, table_picks + ["leave"] * 3) if b == "HatcherTableNoShare"]
        return self.act(R + piece, want, choose)

    def strongbox(self, read=True):
        want = self.m.open_strongbox(read)
        if read:
            return self.act(R + "Strongbox", want)
        # SEEDED: the first page comes back with no answer; the letter was not read through.
        self.box_returns(G + "LetterPage1", -1)
        try:
            return self.act(R + "Strongbox", want)
        finally:
            self.box_returns(None, None)

    def chain(self, pick=None):
        return self.act(R + "Chain", self.m.use_chain(pick), {"RaffertyChain": pick, "AskChain": pick})

    def pilot(self):
        return self.act(R + "Pilot", self.m.use_pilot())

    def dock(self):
        return self.act(R + "ReturnDock", self.m.reach_dock(), enter=True)

    def fire(self, confirm=True):
        return self.act(R + "FireControl", self.m.use_fire(confirm), {"AskFire": confirm})

    def belden(self):
        return self.act(R + "Belden", self.m.talk_belden())

    def report(self, give=True, more=None):
        """Pritchard, at Mercy. What he shows of the river report; then, if it was left for later or there was
        none to make, the Mercy briefing's hub, answered "Not now"."""
        want = self.m.report(give)
        mercy = {}
        if more is not None:
            mercy[MSG + "PritchardAfterAndMore"] = [more]
        if not (want and give):
            mercy[BRIEF_HUB] = [3]
        shown = self.act(REF + "Pritchard", want, {"ReportKnown": give, "ReportUnknown": give}, mercy=mercy, world=False)
        self.before = self.world()                                # the Mercy briefing may have begun: that is its own business
        return shown

    def win_and_say_nothing(self):
        """A hand won, and his question left without an answer. SEEDED: the box comes back with none; a person
        would have to press one of its buttons."""
        self.m.use_table(["deal"])
        self.box_returns(G + "HatcherLost", -1)
        try:
            self.press(R + "Table", {G + "HatcherTable": [0]})
        finally:
            self.box_returns(None, None)
        self.same("the hand won and his question unanswered")

    # ----------------------------------------------------------------- seeding
    def box_returns(self, message, value):
        """SEEDED: that box comes back with this value, whatever a person could have pressed. None: undo."""
        if message is None:
            if getattr(self, "_show", None) is not None:
                self.s.n_message_show = self._show
                self._show = None
            return
        self._show = show = self.s.n_message_show

        def fixed(m, context, *floats):
            if m.editor_id == message:
                self.s.messages_shown.append(m.editor_id)
                return value
            return show(m, context, *floats)
        self.s.n_message_show = fixed

    def press(self, piece, answers=None, enter=False):
        """Uses a piece with no model beside it. Returns the Greenwater messages then shown."""
        s = self.s
        base = {m: [0] * 40 for m, n in self.buttons.items() if m.startswith(G) and n == 1}
        for box in ('ConfirmShare','CardStakes','ConfirmHang','ConfirmCustody','ConfirmRelease'):
            base[G+box]=[0]*40
        base.update({m: list(b) for m, b in (answers or {}).items()})
        s.answers = base
        at = len(s.messages_shown)
        s.walk_to(piece)
        if not enter:
            s.press_activate(piece)
        self.p.pause(4.0)
        return [m[len(G):] if m.startswith(G) else m for m in s.messages_shown[at:]]

    def near(self, who, piece, reach=200.0):
        a, b = self.who[who] if isinstance(who, str) and who in self.who else who, self.s.placed[R + piece]
        return a.cell is b.cell and sum((x - y) ** 2 for x, y in zip(a.pos, b.pos)) ** 0.5 <= reach

    def player_at(self, piece, reach=200.0):
        b = self.s.placed[piece]
        a = self.s.player
        return a.cell is b.cell and sum((x - y) ** 2 for x, y in zip(a.pos, b.pos)) ** 0.5 <= reach


def snapshot(player):
    return copy.deepcopy(player.facts()), copy.deepcopy(player.world())
