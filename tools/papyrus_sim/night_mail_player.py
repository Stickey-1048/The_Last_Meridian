"""Somebody playing the Night Mail on the stand-in engine, and the road's model
keeping step (NIGHT-MAIL-STORY-001). Used by test_night_mail*.py.

The real scripts are driven the way the game drives them: the stand-in's
person plays the first section to its end, walks up to a piece or a person,
presses the button on it and answers the boxes that open by the place of a
button. Travel between the floors is the scripts' own: the harness refuses
to walk to a piece that is not in the cell the player is in, on the floor a
scene last put them on. After every action what was shown, in order,
everything the road then holds, which pieces are switched on, and where the
player stands are compared with tools/logic_model/night_mail_model.py.

What a test can SEED, and nothing here does unless a test asks: a call into
the game that does nothing (enable, disable, moveto, kill, startcombat,
additem, removeitem), every time or so many times; something that happens
just before such a call; a death that comes some seconds after Kill; a box
that comes back with a value no person could press. These are not rules
about the game. They are ways a call could fail to do what was asked, which
the scripts must not take for its having been done.

NONE OF THIS HAS BEEN SEEN IN THE GAME. Not a compile and not a game test.
"""
import copy
import json
import sys

from sim import Actor, GlobalVariable, unwrap
from test_sim import PLUGIN, ROOT, SCRIPTS
from test_act1 import BRIEF_HUB, MSG, REF, Person

sys.path.insert(0, str(ROOT / "tools" / "logic_model"))
import night_mail_model as nm                                     # noqa: E402
from night_mail_model import Line                                 # noqa: E402

G = "TLM_MSG_NM_"
R = "TLM_REF_NM_"
ROAD = "TLM_MQ02A"
STAGE = "TLM_NM"
CELL = "TLM_CELL_NightMail"
OBJECTIVES = nm.OBJECTIVES

YES_NO = {True: 0, False: 1}
INDEX = {
    "AskTravel": YES_NO, "AskTravelAgain": YES_NO,
    "AskLeaveResolved": YES_NO, "AskLeaveUnresolved": YES_NO, "AskLeaveAgain": YES_NO,
    "AskBackToYard": YES_NO, "AskRejoin": YES_NO, "AskWalkToCut": YES_NO, "AskBoard": YES_NO, "AskDepartScene": YES_NO,
    "AskRunScene": YES_NO, "AskReverseScene": YES_NO, "AskForwardScene": YES_NO, "AskCarryBackScene": YES_NO,
    "AskCountersignScene": YES_NO, "AskBillieReport": YES_NO, "AskShowHymnal": YES_NO,
    "LockridgeGateB": {"ride": 0, "hymns": 1, "rails": 2, "no": 3},
    "LockridgeGateAlerted": {"ride": 0, "rails": 1, "no": 2},
    "LockridgeGateSold": {"ride": 0, "hymns": 1, "no": 2},
    "LockridgeAfterRan": {"rails": 0, "night": 1},
    "LockridgeStamp": {"keep": 0, "sign": 1, "take": 2, "close": 3},
    "AskStampAlone": {"take": 0, "close": 1},
    "BillieFootplate": {"on": 0, "cut": 1, "drive": 2},
    "BillieInCut": {"run": 0, "down": 1, "back": 2}, "AskRegulator": {"run": 0, "down": 1, "back": 2},
    "AskAfterDefeat": {"forward": 0, "back": 1, "leave": 2},
    "DoleSermon": {"aside": 0, "share": 1, "name": 2, "back": 3},
    "DoleName": {"silver": 0, "aside": 1, "share": 2},
    "DoleSilver": {"aside": 0, "share": 1},
    "DoleShare": {"done": 0, "no": 1, "back": 2}, "AskShareOffer": {"done": 0, "no": 1, "back": 2},
    "ReportKnown": YES_NO, "ReportUnknown": YES_NO, "AskHandOver": YES_NO,
}
# The cargo, engine and board pieces: which are on is what the road's facts say.
PIECES = ("CargoAboard", "CargoAtCut", "CargoDelivered", "CargoRetained", "CargoSeized", "EngineSound", "EngineDamaged",
          "BoardStamped", "BoardSigned", "BoardClosed", "HeldStock", "StampInDrawer")
# The x of the three floors' edges, with the tiles' half width.
FLOORS = {nm.YARD: (-128, 1152), nm.CUT: (2944, 4736), nm.PLATFORM: (6016, 6784)}


class Rider:
    def __init__(self, test, scripts=SCRIPTS, travel=True, finish=True, with_ledger=False, refuse=(), sheriff=True,
                 person=None, sq01=None):
        """person: a first section already played to its end by another harness in the same session.
        sq01: how the side quest is to have ended, played for real before the road: "reported" or "sold"."""
        self.test = test
        self.p = person or Person(test, scripts=scripts)
        self.s = s = self.p.s
        self.road = s.quests[ROAD]
        self.stage = s.quests[STAGE]
        self.rules = self.road.scripts[0]
        self.walk = self.stage.scripts[0]
        plugin = json.loads(PLUGIN.read_text())
        self.buttons = {m["EditorId"]: len(m["Buttons"]) for m in plugin["Messages"]}
        self.caps = self.p.caps
        self.hymnal = s.forms["TLM_BOOK_HymnalFlyleaf"]
        self.stampitem = s.forms["TLM_MISC_OstranderStamp"]
        self.who = {"lockridge": s.placed[R + "Lockridge"], "billie": s.placed[R + "Billie"], "dole": s.placed[R + "Dole"],
                    "rifle1": s.placed[R + "Rifle1"], "rifle2": s.placed[R + "Rifle2"], "rifle3": s.placed[R + "Rifle3"],
                    "sheriff": s.placed[REF + "Pritchard"]}
        self.room = self.who["sheriff"].cell
        self.cell = s.placed[R + "YardArrival"].cell
        self.refuse = set(refuse)
        self.asked = {"caps": 0, "hymnal": 0, "stamp": 0}
        self._seed_calls()
        self.with_ledger = with_ledger or sq01 is not None
        if finish and person is None:
            self.finish_chapter(sq01)
        outcome, alerted = s.get_global("TLM_G_SQ01_Outcome"), s.get_global("TLM_G_SQ01_YardAlerted")
        self.m = Line(refused=set(self.refuse), caps_bound=self.rules.props.get("caps") is not None,
                      rules_pages=len([m for m in self.buttons if m.startswith(G + "RulesPage")]),
                      flyleaf_pages=len([m for m in self.buttons if m.startswith(G + "FlyleafPage")]),
                      sq01_outcome=int(outcome), yard_alerted=bool(alerted))
        if not sheriff:
            self.kill("sheriff")
        self.caps_before = s.player.inventory.get(self.caps, 0)
        self.before = self.world()
        if travel:
            self.travel()

    # ---------------------------------------------------------------- set-up
    def finish_chapter(self, sq01=None):
        """The first section, played to its end; and, if asked, the side quest ended for real through
        Pritchard's own report box or Vane's offer, as test_act1.py plays them."""
        p = self.p
        p.press("Dispatch", events=["take_dispatch"])
        if self.with_ledger:
            p.press("Ledger", events=["take_ledger"])
            p.press("BrakeShoes", boxes={"TLM_MSG_E1": [0]}, events=["examine_e1"])
        p.to_town()
        if sq01 == "sold":
            p.press("Vane", {"VaneOffer": [0]}, ["sq_sell"])
        p.hand_over("DebriefMissed", more=self.with_ledger and sq01 != "sold")
        if sq01 == "reported":
            p.press("Pritchard", {"PritchardAfterAndMore": [1], "PritchardReported": [0]}, ["sq_report"])
        self.test.assertEqual(p.g("TLM_G_MQ01_Done"), 1)

    # --------------------------------------------- calls the game does not carry out
    def _seed_calls(self):
        """SEEDED, for a test, and off unless a test asks. Every call of these kinds is counted, refused or not."""
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

        add, remove = s.n_objectreference_additem, s.n_objectreference_removeitem

        def what_is(form):
            form = unwrap(form)
            return "caps" if form is self.caps else "hymnal" if form is self.hymnal else "stamp" if form is self.stampitem else None

        def count_add(ref, context, form, count=1, silent=False):
            what = what_is(form)
            if what and ref is s.player and self.road.running:
                self.asked[what] += 1
                if what in self.refuse:
                    return None                                   # SEEDED: the game does not honour the request
            return add(ref, context, form, count, silent)
        s.n_objectreference_additem = count_add

        def count_remove(ref, context, form, count=1, silent=False, other=None):
            if what_is(form) == "stamp" and ref is s.player:
                self.calls.append(("removeitem", "stamp", "handover" not in self.refuse))
                if "handover" in self.refuse:
                    return None                                   # SEEDED: the stamp does not leave the player
            return remove(ref, context, form, count, silent, other)
        s.n_objectreference_removeitem = count_remove

    def _key(self, kind, what):
        if what in self.who:
            return (kind, self.s._whom(self.who[what]))
        if what == "player":
            return (kind, "player")
        return (kind, what if what.startswith("TLM_") else R + what)

    def refuse_call(self, kind, what, times=None):
        """SEEDED: that call on that person or piece does nothing: every time, or the next `times` times."""
        self.refused_calls[self._key(kind, what)] = times

    def allow_calls(self):
        self.refused_calls.clear()
        self.before_call.clear()
        self.late_death.clear()

    def just_before(self, kind, what, do):
        """SEEDED: `do` happens just before that call is carried out."""
        self.before_call[self._key(kind, what)] = do

    def dies_late(self, who, seconds):
        self.late_death[self.s._whom(self.who[who])] = seconds

    def asked_of(self, kind, what):
        key = self._key(kind, what)
        return len([c for c in self.calls if c[:2] == key])

    def alias(self, name, quest=None):
        q = quest or self.stage
        return [a for a in q.aliases.values() if a.name == name][0]

    def kill(self, who, by_player=None, where=None):
        """SEEDED death. The yard's people are protected, so only the player can kill them; Dole and the Black
        Rail die by other hands unless a test says otherwise. What the scripts then show is compared with the
        model's."""
        actor = self.who[who]
        if who == "sheriff":
            actor.dead = True                                     # the first section keeps Pritchard from dying; simply SEEDED
            self.m.sheriff = False
            return []
        if by_player is None:
            by_player = who in ("lockridge", "billie")
        at = len(self.s.messages_shown)
        self._kill(actor, None, self.s.player if by_player else None)
        self.p.pause(3.0)
        self.test.assertTrue(actor.dead, who + " did not die")
        want = []
        if who == "dole":
            want = self.m.dole_dies(by_player)
        elif who.startswith("rifle"):
            self.m.rifles[int(who[-1]) - 1] = False
        else:
            setattr(self.m, who, False)
        got = [m[len(G):] for m in self.s.messages_shown[at:] if m.startswith(G)]
        self.test.assertEqual(got, want, "what was shown when %s died, against the model" % who)
        if where is not False:
            self.before = self.world() if who in ("lockridge", "billie", "dole") or who.startswith("rifle") else self.before
            self.same(where or who + " died")
        return got

    # ------------------------------------------------------- what the game holds
    def g(self, name):
        return self.s.get_global("TLM_G_MQ02A_" + name)

    def count(self, form, who=None):
        return (who or self.s.player).inventory.get(form, 0)

    def on(self, alias):
        return not self.s.placed[R + alias].disabled

    def fighting(self, who):
        return self.who[who].combat_target is not None

    def at(self, who, marker, reach=64.0):
        a = self.who[who] if isinstance(who, str) and who in self.who else who
        b = self.s.placed[marker if marker.startswith("TLM_") else R + marker]
        return a.cell is b.cell and sum((x - y) ** 2 for x, y in zip(a.pos, b.pos)) ** 0.5 <= reach

    def player_at(self, marker, reach=64.0):
        return self.at(self.s.player, marker, reach)

    def facts(self):
        v, q = self.rules.vars, self.road
        return {
            "stages": sorted(set(q.done)),
            "stages set twice": sorted(n for n in set(q.done) if q.done.count(n) > 1),
            "shown": {n: bool(q.displayed.get(n, False)) for n in OBJECTIVES},
            "ticked": {n: bool(q.completed_objectives.get(n, False)) for n in OBJECTIVES},
            "claim": v["claim"], "scene": v["scenepending"], "yard scene": v["yardpending"],
            "outcome": self.g("Outcome"), "mail": self.g("Mail"), "engine": self.g("Engine"), "train": self.g("Train"),
            "dole fate": self.g("Dole"), "stamp": self.g("Stamp"), "stamp delivered": self.g("StampDelivered"),
            "yard authority": self.g("YardAuthority"), "reported": self.g("Reported"),
            "mail_through": self.g("MailThrough"), "mail_sold": self.g("MailSold"), "line_closed": self.g("LineClosed"),
            "dole_lives": self.g("DoleLives"), "silver_rail": self.g("SilverRail"), "ostrander_known": self.g("OstranderKnown"),
            "lockridge_stamping": self.g("LockridgeStamping"), "lockridge_signed": self.g("LockridgeSigned"),
            "lockridge_reported": self.g("LockridgeReported"),
            "dole met": bool(v["dolemet"]), "share pending": bool(v["sharepending"]), "share paid": bool(v["sharepaid"]),
            "billie released": bool(v["billiereleased"]), "billie reported": bool(v["billiereported"]),
            "hymnal shown": bool(v["hymnalshown"]),
            "caps": self.count(self.caps) - self.caps_before, "hymnals": self.count(self.hymnal),
            "stamps": self.count(self.stampitem), "stamps with the sheriff": self.count(self.stampitem, self.who["sheriff"]),
            "asked for caps": self.asked["caps"], "asked for the hymnal": self.asked["hymnal"], "asked for the stamp": self.asked["stamp"],
            "complete": q.completed,
            "alive": {w: not self.who[w].dead for w in ("lockridge", "billie", "dole", "rifle1", "rifle2", "rifle3")},
            "busy": bool(self.walk.vars["talking"]),
        }

    def model_facts(self):
        m = self.m
        return {
            "stages": sorted(m.stages),
            "stages set twice": [],
            "shown": {n: bool(m.shown.get(n, False)) for n in OBJECTIVES},
            "ticked": {n: bool(m.ticked.get(n, False)) for n in OBJECTIVES},
            "claim": m.claim, "scene": m.scene, "yard scene": m.yard_scene,
            "outcome": m.outcome, "mail": m.mail, "engine": m.engine, "train": m.train,
            "dole fate": m.dole_fate, "stamp": m.stamp, "stamp delivered": int(m.stamp_delivered),
            "yard authority": m.yard_authority, "reported": int(m.reported),
            "mail_through": int(m.mail_through), "mail_sold": int(m.mail_sold), "line_closed": int(m.line_closed),
            "dole_lives": int(m.dole_lives), "silver_rail": int(m.silver_rail), "ostrander_known": int(m.ostrander_known),
            "lockridge_stamping": int(m.lockridge_stamping), "lockridge_signed": int(m.lockridge_signed),
            "lockridge_reported": int(m.lockridge_reported),
            "dole met": m.dole_met, "share pending": m.share_pending, "share paid": m.share_paid,
            "billie released": m.billie_released, "billie reported": m.billie_reported, "hymnal shown": m.hymnal_shown,
            "caps": m.caps, "hymnals": m.hymnals, "stamps": m.stamps, "stamps with the sheriff": m.stamps_with_sheriff,
            "asked for caps": m.asked.get("caps", 0), "asked for the hymnal": m.asked.get("hymnal", 0),
            "asked for the stamp": m.asked.get("stamp", 0),
            "complete": 100 in m.stages,
            "alive": {"lockridge": m.lockridge, "billie": m.billie, "dole": m.dole,
                      "rifle1": m.rifles[0], "rifle2": m.rifles[1], "rifle3": m.rifles[2]},
            "busy": False,
        }

    def pieces(self):
        return {name: self.on(name) for name in PIECES}

    def model_pieces(self):
        m = self.m
        if not m.zones_up:
            # Nothing of Iron Junction is switched on before the first travel.
            return {name: False for name in PIECES}
        held = m.yard_authority == nm.NM_YARD_HELD
        return {
            "CargoAboard": m.mail == nm.NM_MAIL_ABOARD and m.train == nm.NM_TRAIN_YARD,
            "CargoAtCut": m.mail == nm.NM_MAIL_ABOARD and m.train == nm.NM_TRAIN_CUT,
            "CargoDelivered": m.mail == nm.NM_MAIL_DELIVERED,
            "CargoRetained": m.mail == nm.NM_MAIL_RETAINED,
            "CargoSeized": m.mail == nm.NM_MAIL_SEIZED,
            "EngineSound": m.train == nm.NM_TRAIN_PLATFORM and m.engine == nm.NM_ENGINE_SOUND,
            "EngineDamaged": m.train == nm.NM_TRAIN_PLATFORM and m.engine == nm.NM_ENGINE_DAMAGED,
            "BoardStamped": held and m.stamp != nm.NM_STAMP_SIGNED,
            "BoardSigned": held and m.stamp == nm.NM_STAMP_SIGNED,
            "BoardClosed": not held,
            "HeldStock": m.stamp == nm.NM_STAMP_SIGNED,
            "StampInDrawer": m.stamp != nm.NM_STAMP_TAKEN,
        }

    def where(self):
        """Where the player stands: Mercy (the first section's room), or the floor of the Night Mail's cell."""
        player = self.s.player
        if player.cell is not self.cell:
            return nm.MERCY
        for name, (low, high) in FLOORS.items():
            if low - 64 <= player.pos[0] <= high:          # the stand-in sets a walker down a step short of a piece
                return name
        return "off the floors, at x %s" % player.pos[0]

    def world(self):
        """Everything this road must leave alone: the earlier quests, the briefing, Greenwater, every other
        global, the first section's people, and what the player carries apart from this road's own things."""
        s = self.s
        mine = (ROAD, STAGE)
        return {
            "globals": {k: f.value for k, f in s.forms.items() if isinstance(f, GlobalVariable) and not k.startswith("TLM_G_MQ02A_")},
            "stages": {q.editor_id: list(q.done) for q in s.quests.values() if q.editor_id not in mine},
            "objectives": {q.editor_id: (dict(q.displayed), dict(q.completed_objectives)) for q in s.quests.values() if q.editor_id not in mine},
            "completed": {q.editor_id: (q.running, q.completed) for q in s.quests.values() if q.editor_id not in mine},
            "people": {k: (r.dead, r.disabled, r.pos) for k, r in s.placed.items() if isinstance(r, Actor) and not k.startswith(R)},
            "carried": {getattr(f, "editor_id", repr(f)): n for f, n in s.player.inventory.items()
                        if n and f is not self.caps and f is not self.hymnal and f is not self.stampitem},
            "sheriff carries": {getattr(f, "editor_id", repr(f)): n for f, n in self.who["sheriff"].inventory.items()
                                if n and f is not self.stampitem},
        }

    def same(self, where, world=True):
        t = self.test
        t.assertEqual(self.facts(), self.model_facts(), "the road against its model (game, model) after: " + where)
        t.assertEqual(self.pieces(), self.model_pieces(), "which pieces are switched on (game, model) after: " + where)
        t.assertEqual(self.where(), self.m.where, "where the player stands (game, model) after: " + where)
        t.assertEqual(self.m.problems(), [], where)
        t.assertEqual([l for l in self.s.papyrus_log if l.startswith("error")], [], where)
        if world:
            t.assertEqual(self.world(), self.before, "something outside this road changed after: " + where)

    # ------------------------------------------------------------- one action
    def reach(self, piece):
        """The player can only use what is in the cell they are in, on the floor they stand on."""
        ref = self.s.placed[piece]
        self.test.assertIs(ref.cell, self.s.player.cell, "%s is not in the cell the player is in: the scripts have to take them there" % piece)
        if ref.cell is self.cell and ref.box is None:
            here = self.where()
            low, high = FLOORS.get(here, (None, None))
            self.test.assertTrue(low is not None and low <= ref.pos[0] <= high, "%s is not on the floor the player stands on (%s)" % (piece, here))

    def act(self, piece, want, picks=None, also=None, where=None, mercy=None, world=True):
        """Walks to a piece and uses it, answering the boxes the model expects with the buttons the picks name.
        What the Night Mail's scripts then showed must be what the model said. mercy: full ids of other boxes
        to answer at Mercy (the first section's, Greenwater's and the briefing's)."""
        s = self.s
        self.reach(piece)
        answers = {m: [0] * 40 for m, n in self.buttons.items() if m.startswith(G) and n == 1}
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

    def leave(self, go=True, at="Exit"):
        return self.act(R + at, self.m.leave(go), {"AskLeaveResolved": go, "AskLeaveUnresolved": go, "AskLeaveAgain": go})

    def back(self, go=True, at="BackFromCut"):
        return self.act(R + at, self.m.back_to_yard(go), {"AskBackToYard": go})

    def lockridge(self, pick="no", show=False, stamp="close", confirm=True, morning=True):
        want = self.m.talk_lockridge(pick=pick, show=show, stamp=stamp, confirm=confirm, morning=morning)
        return self.act(R + "Lockridge", want, {
            "LockridgeGateB": pick, "LockridgeGateAlerted": pick, "LockridgeGateSold": pick,
            "LockridgeAfterRan": pick if pick == "rails" else "night",
            "AskShowHymnal": show, "LockridgeStamp": stamp, "AskStampAlone": stamp,
            "AskCountersignScene": confirm, "AskBillieReport": morning})

    def hire(self):
        """Her gate greeting answered "I'll ride your mail."."""
        return self.lockridge("ride")

    def drawer(self, stamp="close", confirm=True, piece="Drawer"):
        return self.act(R + piece, self.m.use_drawer(stamp, confirm),
                        {"LockridgeStamp": stamp, "AskStampAlone": stamp, "AskCountersignScene": confirm})

    def board(self):
        return self.act(R + "BoardClosed" if self.m.yard_authority != nm.NM_YARD_HELD
                        else R + "BoardSigned" if self.m.stamp == nm.NM_STAMP_SIGNED else R + "BoardStamped", self.m.use_board())

    def billie(self, pick=None, confirm=True):
        at_cut = self.m.train_offered() == nm.NM_AT_OPEN and self.m.billie
        want = self.m.talk_billie(pick=pick or ("down" if at_cut else "drive"), confirm=confirm)
        return self.act(R + "Billie", want, {"BillieFootplate": pick or "drive", "BillieInCut": pick or "down",
                                             "AskRunScene": confirm, "AskReverseScene": confirm})

    def depart(self, go=True):
        want = self.m.use_depart(go)
        return self.act(R + "Depart", want, {"AskBoard": go, "AskDepartScene": go, "AskRejoin": go, "AskWalkToCut": go})

    def train(self, pick=None, confirm=True, piece="Regulator"):
        clear = self.m.train_offered() == nm.NM_AT_CLEAR
        pick = pick or ("leave" if clear else "down")
        want = self.m.use_train(pick, confirm)
        return self.act(R + piece, want, {"BillieInCut": pick, "AskRegulator": pick, "AskAfterDefeat": pick,
                                          "AskRunScene": confirm, "AskReverseScene": confirm,
                                          "AskForwardScene": confirm, "AskCarryBackScene": confirm})

    def dole(self, *picks):
        want = self.m.talk_dole(picks)
        queue = list(picks) or ["back"]
        choose = {}
        for box in want:
            if box in ("DoleSermon", "DoleName", "DoleSilver", "DoleShare", "AskShareOffer"):
                choose.setdefault(box, []).append(queue.pop(0) if queue else "back")
        shown = self.act(R + "Dole", want, choose)
        return shown

    def plate(self):
        return self.act(R + "Plate", self.m.use_plate())

    def hymnal_read(self):
        return self.act(R + "Hymnal", self.m.read_hymnal())

    def chalk(self):
        return self.act(R + "Chalk", self.m.read_chalk())

    def rules_read(self):
        return self.act(R + "Rules", self.m.read_rules())

    def cargo(self, piece):
        return self.act(R + piece, self.m.use_cargo())

    def report(self, give=True, hand=True, acknowledge=True, more=None, river=None):
        """Pritchard, at Mercy. What he shows of the Night Mail; then, if everything offered was left for later
        or nothing was due, the Mercy briefing's hub, answered "Not now". river: full ids and answers of
        Greenwater's boxes, if its report is due first."""
        before = (self.m.reported, self.m.stamp_delivered, self.m.yard_authority)
        want = self.m.report(give, hand, acknowledge)
        mercy = dict(river or {})
        if more is not None:
            mercy[MSG + "PritchardAfterAndMore"] = [more]
        if before == (self.m.reported, self.m.stamp_delivered, self.m.yard_authority) and acknowledge:
            mercy[BRIEF_HUB] = [3]
        shown = self.act(REF + "Pritchard", want, {"ReportKnown": give, "ReportUnknown": give, "AskHandOver": hand}, mercy=mercy, world=False)
        self.before = self.world()                                # the Mercy briefing may have begun: that is its own business
        return shown

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

    def press(self, piece, answers=None, more=4.0):
        """Uses a piece with no model beside it. Returns the Night Mail's messages then shown (other messages
        by their full id)."""
        s = self.s
        self.reach(piece)
        base = {m: [0] * 40 for m, n in self.buttons.items() if m.startswith(G) and n == 1}
        base.update({m: list(b) for m, b in (answers or {}).items()})
        s.answers = base
        at = len(s.messages_shown)
        s.walk_to(piece)
        s.press_activate(piece)
        self.p.pause(more)
        return [m[len(G):] if m.startswith(G) else m for m in s.messages_shown[at:]]


def snapshot(rider):
    return copy.deepcopy(rider.facts()), copy.deepcopy(rider.pieces()), copy.deepcopy(rider.world())
