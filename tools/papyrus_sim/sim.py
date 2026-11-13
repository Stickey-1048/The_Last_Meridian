"""A stand-in for the game, enough to run this project's Papyrus scripts.

It reads the scripts (psc.py), the description of the plugin that the builder
writes (build/TheLastMeridian.json, with the game records it points at in
TheLastMeridian.vanilla.json), and then plays the game's part: quests, stages,
aliases, actors, items, timers, distance events, and the order in which the
game hands events to scripts.

WHAT IT IS FOR. Running the self-test's scenarios on a machine without
Fallout 4, so that a mistake in a script, in an expected number or in the
plugin's wiring shows here and does not cost a run on the game PC.

WHAT IT IS NOT. It is not the game. Every rule below about how the game
behaves is one of three kinds, and says which:

  [seen]        observed in Fallout 4 1.10.163 on the owner's PC
                (docs/design/VERIFY_LOG.md, 2026-11-12)
  [documented]  stated on the Creation Kit wiki
  [assumed]     neither; the simplest behaviour that fits. A scenario that
                depends on an assumed rule proves nothing about the game.

A pass here means the scripts, the plugin and the expectations agree with
each other under those rules. Only a run in the game says what the game does.
"""
import json
import math
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

from psc import Function, Script, parse_folder


class SimError(Exception):
    """The stand-in met something it does not model. Never swallowed."""


class QuitGame(Exception):
    pass


class _Return(Exception):
    def __init__(self, value):
        self.value = value


# How long after Kill the game announces the death to scripts. [documented]
# OnDeath is sent "when the actor finishes dying"; [seen] it arrives within a
# second or two. The number itself is [assumed].
DEATH_EVENT_DELAY = 0.7
COMBAT_EVENT_DELAY = 0.3      # [assumed] number; [seen] that the event arrives
DISTANCE_EVENT_DELAY = 0.1    # [assumed] number; [seen] within a second
FRAME = 1.0 / 60.0


# ------------------------------------------------------------ game objects

class Form:
    kind = "Form"

    def __init__(self, editor_id: str, kind: str, has_model: bool = False):
        self.editor_id = editor_id
        self.kind = kind
        self.has_model = has_model

    def __repr__(self):
        return "[%s <%s>]" % (self.kind, self.editor_id)


class GlobalVariable(Form):
    def __init__(self, editor_id):
        super().__init__(editor_id, "Global")
        self.value = 0.0


class Message(Form):
    def __init__(self, editor_id, box, buttons):
        super().__init__(editor_id, "Message")
        self.box = box
        self.buttons = buttons


class Faction(Form):
    def __init__(self, editor_id):
        super().__init__(editor_id, "Faction")
        self.player_enemy = False


class ObjectReference:
    count = 0

    def __init__(self, base: Optional[Form], pos=(0.0, 0.0, 0.0)):
        ObjectReference.count += 1
        self.id = ObjectReference.count
        self.base = base
        self.pos = tuple(pos)
        self.disabled = False
        self.deleted = False
        self.inventory: Dict[Form, int] = {}
        # Nothing in the stand-in opens a conversation. A test that wants one
        # sets this, as a person would by talking to the actor.
        self.talking_to_player = False

    def has_3d(self) -> bool:
        # [seen] a placed copy of an item with no model reports Is3DLoaded false
        return bool(self.base and self.base.has_model) and not self.disabled

    def __repr__(self):
        return "[%s #%d of %s]" % (type(self).__name__, self.id, self.base.editor_id if self.base else "?")


class Actor(ObjectReference):
    def __init__(self, base, pos=(0.0, 0.0, 0.0), is_player=False):
        super().__init__(base, pos)
        self.is_player = is_player
        self.dead = False
        self.protected_override: Optional[bool] = None
        self.essential_override: Optional[bool] = None
        self.combat_target: Optional["Actor"] = None


class Alias:
    def __init__(self, quest, info):
        self.quest = quest
        self.id = info["Id"]
        self.name = info["Name"]
        self.flags = set(info["Flags"])
        self.fill = info.get("Fill")
        self.ref: Optional[ObjectReference] = None
        self.scripts: List["Instance"] = []

    def __repr__(self):
        return "[alias %s on %s]" % (self.name, self.quest.editor_id)


class Quest(Form):
    def __init__(self, info):
        super().__init__(info["EditorId"], "Quest")
        self.flags = set(info["Flags"])
        self.stages = {s["Index"]: s for s in info["Stages"]}
        self.objectives = {o["Index"] for o in info["Objectives"]}
        self.done: List[int] = []
        self.displayed: Dict[int, bool] = {}
        self.completed_objectives: Dict[int, bool] = {}
        self.running = False
        self.completed = False
        self.aliases: Dict[int, Alias] = {}
        self.scripts: List["Instance"] = []


class Instance:
    """One script attached to one game object."""

    def __init__(self, script: Script, obj):
        self.script = script
        self.obj = obj
        self.props: Dict[str, Any] = {}
        self.vars: Dict[str, Any] = {}

    def __repr__(self):
        return "[%s on %r]" % (self.script.name, self.obj)


class Thread:
    def __init__(self, gen, name):
        self.gen = gen
        self.name = name
        self.wake = 0.0
        self.blocked = False
        self.done = False


NATIVE_TYPES = {
    "scriptobject": object, "form": Form, "quest": Quest, "globalvariable": GlobalVariable,
    "message": Message, "faction": Faction, "objectreference": ObjectReference, "actor": Actor,
    "alias": Alias, "referencealias": Alias,
    # base forms the scripts only pass around
    "miscobject": Form, "book": Form, "actorbase": Form, "static": Form,
}
GLOBAL_SCRIPTS = {"game", "debug", "utility"}


def unwrap(v):
    """A script attached to a quest or an alias stands for that quest or alias."""
    return v.obj if isinstance(v, Instance) else v


def to_string(v) -> str:
    v = unwrap(v)
    if v is None:
        return "None"
    if isinstance(v, bool):
        return "True" if v else "False"       # [seen] in the self-test's log
    if isinstance(v, float):
        return "%f" % v                        # [seen] "2000.000000"
    return str(v)


def truthy(v) -> bool:
    if v is None:
        return False
    if isinstance(v, (bool, int, float)):
        return bool(v)
    if isinstance(v, str):
        return v != ""
    if isinstance(v, list):
        return len(v) > 0
    return True


def default_for(type_name: Optional[str]):
    t = (type_name or "").lower()
    if t == "int":
        return 0
    if t == "float":
        return 0.0
    if t == "bool":
        return False
    if t == "string":
        return ""
    return None


def coerce(value, type_name: Optional[str]):
    """What Papyrus does to a value going into a typed slot."""
    t = (type_name or "").lower()
    if t == "int":
        if isinstance(value, bool):
            return 1 if value else 0
        if isinstance(value, (int, float)):
            return int(value)
        return 0 if value is None else value
    if t == "float":
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        if isinstance(value, (int, float)):
            return float(value)
        return 0.0 if value is None else value
    if t == "bool":
        return truthy(value)
    if t == "string":
        return to_string(value)
    return value


_parsed: Dict[tuple, Dict[str, Script]] = {}


def parsed(folder) -> Dict[str, Script]:
    """The scripts of a folder, read once for as long as the files stay as they
    are. A script's tree is only read by a session, never changed, so sessions
    can share it."""
    files = sorted(Path(folder).glob("*.psc"))
    key = (str(folder),) + tuple((f.name, f.stat().st_mtime_ns, f.stat().st_size) for f in files)
    if key not in _parsed:
        _parsed[key] = parse_folder(folder)
    return _parsed[key]


# ---------------------------------------------------------------- session

class Session:
    """One game session: from the main menu into the test room, until the game closes."""

    def __init__(self, scripts_folder, plugin_json, vanilla_json=None, natives_json=None, older_scripts=False,
                 native_delay=0.0, shake=None):
        """older_scripts: the scripts are an earlier version than the plugin
        description (used to replay a recorded game run). A property the
        plugin fills and the older script does not declare is then left out
        instead of stopping the session.

        native_delay: seconds that every call out of a script takes (into the
        game, or onto another object). 0, the default, is the mode the
        recorded game runs are replayed in: nothing takes time, so two script
        threads never overlap. In the game they do: [documented] a script
        gives other threads a turn at every such call. With a delay of one
        frame the stand-in lets threads overlap at exactly those points. That
        is a pessimistic picture, not a measured one: in the game many calls
        come back within the frame. It is for provoking overlaps, not for
        predicting timings.

        shake: a number. With it the session is shaken, the same way every
        time for the same number: every call into the game takes 0 to 3
        frames, a stage's handlers begin 0 to 3 frames after the stage is
        marked as set ([assumed] that this can happen; [seen] only that
        SetStage comes back after them), events arrive up to 3 frames late,
        and threads that are ready at the same instant run in any order. For
        hunting interleavings that a fixed timing never produces. It is
        harsher than the game: there, [documented], a call on the script's
        own quest or alias does not give other threads a turn; here it may.
        Only what a script does with no call at all between two steps is
        left whole."""
        self.older_scripts = older_scripts
        self.native_delay = float(native_delay)
        self.rng = random.Random(shake) if shake is not None else None
        self.shake_frames = 3
        # Which of two threads that are ready at the same instant goes first.
        # The game promises no order; a test of overlapping handlers should
        # hold either way.
        self.newest_first = False
        self.scripts: Dict[str, Script] = parsed(scripts_folder)
        self.plugin = json.loads(Path(plugin_json).read_text())
        self.vanilla = json.loads(Path(vanilla_json).read_text()) if vanilla_json and Path(vanilla_json).exists() else []
        self.natives_doc = json.loads(Path(natives_json).read_text())["natives"] if natives_json else {}
        self.now = 0.0
        self.threads: List[Thread] = []
        self.timers: Dict[tuple, tuple] = {}          # (id(instance), timer id) -> (due, instance)
        self.pending: List[tuple] = []                # (due, order, name, make generator)
        self.order = 0
        self.distance_watches: List[dict] = []
        self.papyrus_log: List[str] = []
        self.user_logs: Dict[str, List[str]] = {}
        self.open_logs = set()
        self.notifications: List[str] = []
        self.message_boxes: List[str] = []
        self.messages_shown: List[str] = []
        self.god_mode = False
        self.ended = None                             # 'quit' | 'idle' | 'timeout'
        self.unknown_scripts = set()
        self.calls_on_none = 0
        self.forms: Dict[str, Form] = {}
        self.quests: Dict[str, Quest] = {}
        self.player = Actor(Form("Player", "Npc", has_model=True), is_player=True)
        self.actors: List[Actor] = [self.player]
        self._build()

    # ---- building the world from the plugin's description
    def _build(self):
        for rec in self.plugin["Records"]:
            eid = rec["EditorId"]
            if rec["Type"] == "Global":
                self.forms[eid] = GlobalVariable(eid)
            elif rec["Type"] == "Faction":
                self.forms[eid] = Faction(eid)
            else:
                # The plugin's items carry no model yet. [seen] Is3DLoaded false.
                self.forms[eid] = Form(eid, rec["Type"], has_model=False)
        for m in self.plugin["Messages"]:
            self.forms[m["EditorId"]] = Message(m["EditorId"], m["Box"], m["Buttons"])
        self.by_formkey: Dict[str, Any] = {}
        for v in self.vanilla:
            if v["Kind"] == "Player":
                self.by_formkey[v["FormKey"]] = self.player
            else:
                # The game's own records have models. [seen] for the marker
                # (MoveTo returns) and the settler (it stands, fights and dies).
                self.by_formkey[v["FormKey"]] = Form(v["EditorId"], v["Kind"], has_model=True)
        for q in self.plugin["Quests"]:
            quest = Quest(q)
            self.quests[quest.editor_id] = quest
            self.forms[quest.editor_id] = quest
            for a in q["Aliases"]:
                quest.aliases[a["Id"]] = Alias(quest, a)
        for q in self.plugin["Quests"]:
            quest = self.quests[q["EditorId"]]
            for bind in q["Scripts"]:
                inst = self._attach(bind, quest, quest)
                if inst:
                    quest.scripts.append(inst)
            for a in q["Aliases"]:
                alias = quest.aliases[a["Id"]]
                for bind in a["Scripts"]:
                    inst = self._attach(bind, alias, quest)
                    if inst:
                        alias.scripts.append(inst)

    def _target(self, name: str):
        if name in self.forms:
            return self.forms[name]
        if name in self.by_formkey:
            return self.by_formkey[name]
        raise SimError("the plugin points at %s, which the stand-in does not have" % name)

    def _attach(self, bind, obj, quest) -> Optional[Instance]:
        script = self.scripts.get(bind["Name"].lower())
        if script is None:
            # One of the game's own scripts (DefaultAliasOn...). Not run here.
            self.unknown_scripts.add(bind["Name"])
            return None
        inst = Instance(script, obj)
        for p in bind["Props"]:
            low = p["Name"].lower()
            if low not in script.properties:
                if self.older_scripts:
                    continue
                raise SimError("%s: the plugin fills %s, which the script does not declare" % (script.name, p["Name"]))
            if p["Kind"] == "object":
                if p["Alias"] is not None:
                    inst.props[low] = self.quests[p["Target"]].aliases[p["Alias"]]
                else:
                    inst.props[low] = self._target(p["Target"])
            elif p["Kind"] == "int[]":
                inst.props[low] = list(p["Value"])
            else:
                inst.props[low] = p["Value"]
        for low, prop in script.properties.items():
            if low not in inst.props:
                # A property the plugin leaves alone keeps its default. [documented]
                inst.props[low] = coerce(self._const(prop.default, inst), prop.type) if prop.default is not None else default_for(prop.type)
        for low, var in script.variables.items():
            inst.vars[low] = coerce(self._const(var.init, inst), var.type) if var.init is not None else default_for(var.type)
        return inst

    def _const(self, node, inst):
        """A default or initial value: a literal, possibly negated."""
        if node[0] == "lit":
            return node[1]
        if node[0] == "unary" and node[1] == "-" and node[2][0] == "lit":
            return -node[2][1]
        raise SimError("%s: an initial value that is not a plain literal" % inst.script.name)

    # ---- logs
    def trace(self, text: str):
        self.papyrus_log.append(text)

    def papyrus_error(self, text: str, inst: Optional[Instance] = None, line: int = 0):
        where = " (%s, line %d)" % (inst.script.name, line) if inst else ""
        self.papyrus_log.append("error: " + text + where)

    # ---- scheduling
    def spawn(self, gen, name: str):
        th = Thread(gen, name)
        th.wake = self.now
        self.threads.append(th)
        return th

    def later(self, delay: float, name: str, make, exact: bool = False):
        self.order += 1
        if self.rng and not exact:
            delay += self.rng.randint(0, self.shake_frames) * FRAME
        self.pending.append((self.now + delay, self.order, name, make))

    def send_event(self, inst: Instance, event: str, args: list, delay: float = 0.0):
        fn = inst.script.functions.get(event.lower())
        if fn is None:
            return
        self.later(delay, "%s.%s" % (inst.script.name, event), lambda: self.call(inst, fn, args))

    def actor_event(self, actor: Actor, event: str, args: list, delay: float):
        """[documented] an alias's scripts receive its reference's events; [seen] for OnDeath, OnCombatStateChanged, OnPlayerLoadGame."""
        for quest in self.quests.values():
            if not quest.running:
                continue
            for alias in quest.aliases.values():
                if alias.ref is actor:
                    for inst in alias.scripts:
                        self.send_event(inst, event, args, delay)

    def run(self, until: float = 900.0) -> str:
        """Runs until the game is closed by a script, nothing is left that could
        ever happen ('idle'), or the clock passes `until` ('timeout')."""
        while True:
            state = self.run_once(until)
            if state != "running":
                return state

    def run_once(self, until: float) -> str:
        """Lets every script thread that can run do so, then moves the clock to
        the next thing due. Returns 'running', or how the session ended."""
        try:
            self.run_ready()
            return self.advance(until)
        except QuitGame:
            self.ended = "quit"
            return self.ended

    def run_ready(self):
        """Lets every script thread that can run now do so. The clock stands still."""
        progressed = True
        while progressed:
            progressed = False
            order = list(reversed(self.threads)) if self.newest_first else list(self.threads)
            if self.rng:
                self.rng.shuffle(order)
            for th in order:
                if th.done or th.blocked or th.wake > self.now + 1e-9:
                    continue
                self._step(th)
                progressed = True
            self.threads = [t for t in self.threads if not t.done]

    def advance(self, until: float) -> str:
        """Moves the clock to the next thing due and starts what is due then."""
        times = [t.wake for t in self.threads if not t.blocked]
        times += [due for due, _inst in self.timers.values()]
        times += [p[0] for p in self.pending]
        if not times:
            self.ended = "idle"
            return self.ended
        nxt = min(times)
        if nxt > until:
            self.ended = "timeout"
            return self.ended
        self.now = max(self.now, nxt)
        for key, (due, inst) in sorted(self.timers.items(), key=lambda kv: kv[1][0]):
            if due <= self.now + 1e-9:
                del self.timers[key]
                self.send_event(inst, "OnTimer", [key[1]])
        due_now = sorted([p for p in self.pending if p[0] <= self.now + 1e-9], key=lambda p: (p[0], p[1]))
        self.pending = [p for p in self.pending if p[0] > self.now + 1e-9]
        for _due, _order, name, make in due_now:
            self.spawn(make(), name)
        return "running"

    def _step(self, th: Thread):
        try:
            req = next(th.gen)
        except StopIteration:
            th.done = True
            return
        if req[0] == "sleep":
            th.wake = self.now + max(0.0, float(req[1]))
        elif req[0] == "block":
            th.blocked = True
        else:
            raise SimError("unknown request from a script thread: %r" % (req,))

    # ---- the interpreter
    def call(self, inst: Instance, fn: Function, args: list, named: Optional[dict] = None):
        """Runs one function or event of a script. A generator: it yields when the script has to wait."""
        scope = {}
        named = named or {}
        if len(args) > len(fn.params):
            raise SimError("%s.%s called with %d arguments, takes %d" % (inst.script.name, fn.name, len(args), len(fn.params)))
        for i, p in enumerate(fn.params):
            if i < len(args):
                value = args[i]
            elif p.name.lower() in named:
                value = named[p.name.lower()]
            elif p.has_default:
                value = self._const(p.default, inst)
            else:
                raise SimError("%s.%s called without its parameter %s" % (inst.script.name, fn.name, p.name))
            scope[p.name.lower()] = coerce(value, p.type)
        frame = {"inst": inst, "scopes": [scope], "fn": fn}
        try:
            yield from self.block(fn.body, frame)
        except _Return as r:
            return coerce(r.value, fn.return_type) if fn.return_type else None
        return default_for(fn.return_type)

    def block(self, body, frame):
        frame["scopes"].append({})
        try:
            for st in body:
                yield from self.statement(st, frame)
        finally:
            frame["scopes"].pop()

    def statement(self, st, frame):
        kind = st[0]
        if kind == "expr":
            yield from self.ev(st[1], frame)
        elif kind == "var":
            _, type_name, name, init, _line = st
            value = (yield from self.ev(init, frame)) if init is not None else default_for(type_name)
            frame["scopes"][-1][name.lower()] = coerce(value, type_name)
        elif kind == "assign":
            _, target, op, expr, line = st
            value = yield from self.ev(expr, frame)
            if op != "=":
                current = yield from self.ev(target, frame)
                value = self.binary(op[0], current, value, frame, line)
            yield from self.assign(target, value, frame, line)
        elif kind == "if":
            _, branches, otherwise, _line = st
            for cond, body in branches:
                if truthy((yield from self.ev(cond, frame))):
                    yield from self.block(body, frame)
                    return
            if otherwise is not None:
                yield from self.block(otherwise, frame)
        elif kind == "while":
            _, cond, body, line = st
            turns = 0
            while truthy((yield from self.ev(cond, frame))):
                yield from self.block(body, frame)
                turns += 1
                if turns > 100000:
                    raise SimError("%s line %d: a loop that does not end" % (frame["inst"].script.name, line))
        elif kind == "return":
            value = (yield from self.ev(st[1], frame)) if st[1] is not None else None
            raise _Return(value)
        else:
            raise SimError("statement %r" % kind)

    def lookup(self, name: str, frame):
        low = name.lower()
        for scope in reversed(frame["scopes"]):
            if low in scope:
                return True, scope[low]
        inst = frame["inst"]
        if low in inst.vars:
            return True, inst.vars[low]
        if low in inst.props:
            return True, inst.props[low]
        if low == "self":
            return True, inst
        return False, None

    def assign(self, target, value, frame, line):
        inst = frame["inst"]
        if target[0] == "id":
            low = target[1].lower()
            for scope in reversed(frame["scopes"]):
                if low in scope:
                    scope[low] = self._keep_type(scope[low], value)
                    return
            if low in inst.vars:
                var = inst.script.variables[low]
                if var.const:
                    raise SimError("%s line %d: assignment to the constant %s" % (inst.script.name, line, var.name))
                inst.vars[low] = coerce(value, var.type)
                return
            if low in inst.props:
                prop = inst.script.properties[low]
                if "const" in prop.flags:
                    raise SimError("%s line %d: assignment to the Const property %s" % (inst.script.name, line, prop.name))
                inst.props[low] = coerce(value, prop.type)
                return
            raise SimError("%s line %d: %s is not declared" % (inst.script.name, line, target[1]))
        raise SimError("%s line %d: this kind of assignment is not understood here" % (inst.script.name, line))
        yield  # pragma: no cover  (keeps this a generator)

    @staticmethod
    def _keep_type(old, new):
        if isinstance(old, bool):
            return truthy(new)
        if isinstance(old, int) and isinstance(new, float):
            return int(new)
        if isinstance(old, float) and isinstance(new, int) and not isinstance(new, bool):
            return float(new)
        return new

    def ev(self, node, frame):
        kind = node[0]
        inst = frame["inst"]
        if kind == "lit":
            return node[1]
        if kind == "id":
            found, value = self.lookup(node[1], frame)
            if not found:
                raise SimError("%s line %d: %s is not declared" % (inst.script.name, node[2], node[1]))
            return value
        if kind == "unary":
            value = yield from self.ev(node[2], frame)
            if node[1] == "!":
                return not truthy(value)
            return -value
        if kind == "binary":
            op = node[1]
            left = yield from self.ev(node[2], frame)
            if op == "&&":
                return truthy(left) and truthy((yield from self.ev(node[3], frame)))
            if op == "||":
                return truthy(left) or truthy((yield from self.ev(node[3], frame)))
            right = yield from self.ev(node[3], frame)
            return self.binary(op, left, right, frame, node[4])
        if kind == "cast":
            value = yield from self.ev(node[1], frame)
            return self.cast(value, node[2], frame, node[3])
        if kind == "member":
            obj = yield from self.ev(node[1], frame)
            return self.member(obj, node[2], frame, node[3])
        if kind == "index":
            arr = yield from self.ev(node[1], frame)
            idx = yield from self.ev(node[2], frame)
            if not isinstance(arr, list) or not 0 <= idx < len(arr):
                self.papyrus_error("Array index %r is out of range" % (idx,), inst, node[3])
                return 0
            return arr[idx]
        if kind == "call":
            return (yield from self.call_node(node, frame))
        raise SimError("expression %r" % kind)

    def binary(self, op, left, right, frame, line):
        if op in ("==", "!="):
            a, b = unwrap(left), unwrap(right)
            if isinstance(a, (int, float, str, bool)) or isinstance(b, (int, float, str, bool)):
                same = a == b
            else:
                same = a is b
            return same if op == "==" else not same
        if op == "+" and (isinstance(left, str) or isinstance(right, str)):
            return to_string(left) + to_string(right)
        if isinstance(left, bool) or isinstance(right, bool) or left is None or right is None:
            raise SimError("%s line %d: %r between %r and %r" % (frame["inst"].script.name, line, op, left, right))
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            if isinstance(left, int) and isinstance(right, int):
                return int(left / right) if right else 0
            return left / right if right else 0.0
        if op == "%":
            return int(math.fmod(left, right)) if right else 0
        if op == "<":
            return left < right
        if op == ">":
            return left > right
        if op == "<=":
            return left <= right
        if op == ">=":
            return left >= right
        raise SimError("operator %r" % op)

    def cast(self, value, type_name: str, frame, line):
        low = type_name.lower()
        if low in ("int", "float", "bool", "string"):
            return coerce(value, low)
        if low in self.scripts:
            wanted = self.scripts[low]
            if isinstance(value, Instance) and value.script is wanted:
                return value
            obj = unwrap(value)
            for inst in getattr(obj, "scripts", []):
                if inst.script is wanted:
                    return inst
            return None
        if low in NATIVE_TYPES:
            obj = unwrap(value)
            if obj is None:
                return None
            return obj if isinstance(obj, NATIVE_TYPES[low]) else None
        raise SimError("%s line %d: cast to %s, a type the stand-in does not know" % (frame["inst"].script.name, line, type_name))

    def member(self, obj, name: str, frame, line):
        low = name.lower()
        if isinstance(obj, list) and low == "length":
            return len(obj)
        if isinstance(obj, Instance):
            if low in obj.props:
                return obj.props[low]
            raise SimError("%s line %d: %s has no property %s" % (frame["inst"].script.name, line, obj.script.name, name))
        if obj is None:
            self.papyrus_error("Cannot access a property of a None object", frame["inst"], line)
            return None
        raise SimError("%s line %d: .%s on %r" % (frame["inst"].script.name, line, name, obj))

    def call_node(self, node, frame):
        _, recv_node, name, arg_nodes, line = node
        inst = frame["inst"]
        low = name.lower()
        args, named = [], {}
        # a global script: Game.GetPlayer(), Debug.Trace(...), Utility.Wait(...)
        if recv_node is not None and recv_node[0] == "id" and recv_node[1].lower() in GLOBAL_SCRIPTS:
            found, _ = self.lookup(recv_node[1], frame)
            if not found:
                for arg_name, arg in arg_nodes:
                    if arg_name:
                        raise SimError("%s line %d: named arguments to %s are not understood here" % (inst.script.name, line, name))
                    args.append((yield from self.ev(arg, frame)))
                return (yield from self.native(recv_node[1].lower(), None, None, name, args, frame, line))
        if recv_node is None:
            target = inst
        else:
            target = yield from self.ev(recv_node, frame)
        for arg_name, arg in arg_nodes:
            value = yield from self.ev(arg, frame)
            if arg_name:
                named[arg_name.lower()] = value
            else:
                args.append(value)
        if target is None:
            # [documented] the game logs this and carries on with a zero value.
            self.calls_on_none += 1
            self.papyrus_error("Cannot call %s() on a None object, aborting function call" % name, inst, line)
            return None
        if isinstance(target, Instance) and low in target.script.functions:
            return (yield from self.call(target, target.script.functions[low], args, named))
        if named:
            raise SimError("%s line %d: named arguments to %s are not understood here" % (inst.script.name, line, name))
        context = target if isinstance(target, Instance) else None
        return (yield from self.native(None, unwrap(target), context, name, args, frame, line))

    # ---- the game's own functions
    def native(self, global_script, obj, context: Optional[Instance], name, args, frame, line):
        low = name.lower()
        self._check_arity(name, len(args), frame, line)
        if global_script:
            fn = getattr(self, "g_%s_%s" % (global_script, low), None)
        else:
            fn = None
            for cls in type(obj).__mro__:
                fn = getattr(self, "n_%s_%s" % (cls.__name__.lower(), low), None)
                if fn:
                    break
            if fn is None:
                fn = getattr(self, "n_scriptobject_%s" % low, None)
        if fn is None:
            who = global_script or type(obj).__name__
            raise SimError("%s line %d: %s.%s is not modelled by the stand-in" % (frame["inst"].script.name, line, who, name))
        if self.rng:
            delay = self.rng.randint(0, self.shake_frames) * FRAME
            if delay:
                yield ("sleep", delay)
        elif self.native_delay and (global_script or obj is not frame["inst"].obj):
            # a call out of the script: other threads get a turn
            yield ("sleep", self.native_delay)
        result = fn(*args) if global_script else fn(obj, context, *args)
        if hasattr(result, "send"):          # a function that makes the script wait
            result = yield from result
        return result

    def _check_arity(self, name, argc, frame, line):
        if not self.natives_doc:
            return
        doc = self.natives_doc.get(name)
        if doc is None:
            for key, value in self.natives_doc.items():
                if key.lower() == name.lower():
                    doc = value
                    break
        if doc is None:
            raise SimError("%s line %d: %s() is not in tools/papyrus_natives.json" % (frame["inst"].script.name, line, name))
        if not any(d["min_args"] <= argc <= d["max_args"] for d in doc):
            raise SimError("%s line %d: %s() called with %d argument(s)" % (frame["inst"].script.name, line, name, argc))

    # Game
    def g_game_getplayer(self):
        return self.player

    # Utility
    def g_utility_wait(self, seconds):
        yield ("sleep", seconds)

    def g_utility_waitmenumode(self, seconds):
        yield ("sleep", seconds)

    # Debug.  [seen] these work in the game although the wiki calls them debug-only.
    def g_debug_trace(self, text, severity=0):
        self.trace(to_string(text))

    def g_debug_openuserlog(self, name):
        if name in self.open_logs:
            return False
        self.open_logs.add(name)
        self.user_logs.setdefault(name, [])
        return True

    def g_debug_closeuserlog(self, name):
        self.open_logs.discard(name)

    def g_debug_traceuser(self, name, text, severity=0):
        if name not in self.open_logs:
            return False
        self.user_logs[name].append(to_string(text))
        return True

    def g_debug_notification(self, text):
        self.notifications.append(to_string(text))

    def g_debug_messagebox(self, text):
        self.message_boxes.append(to_string(text))

    def g_debug_quitgame(self):
        raise QuitGame()

    def g_debug_setgodmode(self, on):
        self.god_mode = truthy(on)

    # Quest
    def start_quest(self, quest: Quest):
        if quest.running:
            return
        quest.running = True
        for alias in quest.aliases.values():
            if alias.fill and alias.fill.startswith("forced "):
                alias.ref = self.by_formkey.get(alias.fill.split(" ", 1)[1])
        for inst in quest.scripts:
            self.send_event(inst, "OnQuestInit", [])

    def n_quest_setstage(self, quest: Quest, context, stage):
        if stage not in quest.stages:
            self.papyrus_error("%s has no stage %d" % (quest.editor_id, stage))
            return False
        if not quest.running:
            self.start_quest(quest)                 # [seen] SetStage starts a stopped quest
        if stage in quest.done:
            return False                            # [documented] a stage is set once
        quest.done.append(stage)
        info = quest.stages[stage]
        if info["CompleteQuest"]:
            quest.completed = True                  # [seen] the quest goes on running and handling stages
        if self.rng:
            # the stage reads as set; its handlers have yet to begin
            wait = self.rng.randint(0, self.shake_frames) * FRAME
            if wait:
                yield ("sleep", wait)
        # [seen] the game tells the scripts once per stage item, none for a
        # stage without items; and SetStage returns after the handlers.
        for item in range(info["Items"]):
            for inst in quest.scripts:
                fn = inst.script.functions.get("onstageset")
                if fn:
                    yield from self.call(inst, fn, [stage, item])
        return True

    def n_quest_getstagedone(self, quest, context, stage):
        return stage in quest.done

    def n_quest_isrunning(self, quest, context):
        return quest.running

    def n_quest_iscompleted(self, quest, context):
        return quest.completed

    def _objective(self, quest, index):
        if index not in quest.objectives:
            self.papyrus_error("%s has no objective %d" % (quest.editor_id, index))

    def n_quest_setobjectivedisplayed(self, quest, context, index, displayed=True, force=False):
        self._objective(quest, index)
        quest.displayed[index] = truthy(displayed)

    def n_quest_setobjectivecompleted(self, quest, context, index, completed=True):
        self._objective(quest, index)
        # [seen] an objective completed without ever having been displayed
        # reads as completed (case 213)
        quest.completed_objectives[index] = truthy(completed)

    def n_quest_isobjectivedisplayed(self, quest, context, index):
        return quest.displayed.get(index, False)

    def n_quest_isobjectivecompleted(self, quest, context, index):
        return quest.completed_objectives.get(index, False)

    # timers and distance events belong to the script that asks. [documented]
    def _need_context(self, context, what):
        if context is None:
            raise SimError("%s called on something that is not a script" % what)
        return context

    def n_scriptobject_starttimer(self, obj, context, interval, timer_id=0):
        inst = self._need_context(context, "StartTimer")
        self.timers[(id(inst), timer_id)] = (self.now + float(interval), inst)   # restarts a running one [documented]

    def n_scriptobject_canceltimer(self, obj, context, timer_id=0):
        inst = self._need_context(context, "CancelTimer")
        self.timers.pop((id(inst), timer_id), None)

    def _ref_of(self, thing) -> Optional[ObjectReference]:
        thing = unwrap(thing)
        if isinstance(thing, Alias):
            return thing.ref
        return thing

    def n_scriptobject_registerfordistancegreaterthanevent(self, obj, context, a, b, distance):
        inst = self._need_context(context, "RegisterForDistanceGreaterThanEvent")
        a, b = unwrap(a), unwrap(b)
        if a is None or b is None:
            self.papyrus_error("RegisterForDistanceGreaterThanEvent with a None object", inst)
            return
        # one registration per script and pair; a new one replaces it [documented]
        self.distance_watches = [w for w in self.distance_watches
                                 if not (w["inst"] is inst and {id(w["a"]), id(w["b"])} == {id(a), id(b)})]
        self.distance_watches.append({"inst": inst, "a": a, "b": b, "distance": float(distance)})
        self.check_distances()                      # [seen] sent at once when already apart

    def n_scriptobject_unregisterfordistanceevents(self, obj, context, a, b):
        inst = self._need_context(context, "UnregisterForDistanceEvents")
        a, b = unwrap(a), unwrap(b)
        self.distance_watches = [w for w in self.distance_watches
                                 if not (w["inst"] is inst and {id(w["a"]), id(w["b"])} == {id(a), id(b)})]

    def check_distances(self):
        for w in list(self.distance_watches):
            ra, rb = self._ref_of(w["a"]), self._ref_of(w["b"])
            if ra is None or rb is None:
                continue
            d = math.dist(ra.pos, rb.pos)
            if d > w["distance"]:
                self.distance_watches.remove(w)     # [documented] a single event per registration
                self.send_event(w["inst"], "OnDistanceGreaterThan", [ra, rb, d], DISTANCE_EVENT_DELAY)

    # GlobalVariable
    def n_globalvariable_getvalueint(self, g, context):
        return int(g.value)

    def n_globalvariable_setvalueint(self, g, context, value):
        g.value = float(int(value))

    def n_globalvariable_getvalue(self, g, context):
        return g.value

    def n_globalvariable_setvalue(self, g, context, value):
        g.value = float(value)

    def n_globalvariable_mod(self, g, context, amount):
        g.value += float(amount)
        return g.value

    # Message
    def n_message_show(self, m, context, *floats):
        self.messages_shown.append(m.editor_id)
        if m.box:
            raise SimError("the message box %s opened and nobody is there to answer it" % m.editor_id)
        return -1                                   # [documented] not a box: returns -1 at once

    # Faction
    def n_faction_setplayerenemy(self, f, context, enemy=True):
        f.player_enemy = truthy(enemy)

    # Alias
    def n_alias_getowningquest(self, alias, context):
        return alias.quest

    def n_alias_getreference(self, alias, context):
        return alias.ref

    def n_alias_getactorreference(self, alias, context):
        return alias.ref if isinstance(alias.ref, Actor) else None

    def n_alias_forcerefto(self, alias, context, ref):
        ref = unwrap(ref)
        if not alias.quest.running:
            # [assumed] not tried in the game; the scripts never do it.
            raise SimError("ForceRefTo on %r while its quest is not running" % alias)
        alias.ref = ref                             # [seen] holds an actor made by PlaceAtMe

    def n_alias_trytodisable(self, alias, context):
        if alias.ref is None:
            return False
        self._disable(alias.ref)                    # [seen] the aliased actor is disabled, alive or dead
        return True

    def n_alias_trytostopcombat(self, alias, context):
        if isinstance(alias.ref, Actor):
            self._stop_combat(alias.ref)
            return True
        return False

    def n_alias_trytoevaluatepackage(self, alias, context):
        return isinstance(alias.ref, Actor)

    # ObjectReference
    def n_objectreference_placeatme(self, ref, context, form, count=1, persist=False, disabled=False, delete_when_able=True):
        form = unwrap(form)
        if form is None:
            self.papyrus_error("PlaceAtMe: the form to place is None")
            return None
        if form.kind == "Npc":
            made = Actor(form, ref.pos)             # [seen] a settler made this way stands, fights and dies
            self.actors.append(made)
        else:
            made = ObjectReference(form, ref.pos)   # [seen] a marker and an item
        made.disabled = truthy(disabled)
        return made

    def n_objectreference_moveto(self, ref, context, target, x=0.0, y=0.0, z=0.0, match_rotation=True):
        target = unwrap(target)
        if target is None:
            self.papyrus_error("MoveTo: the target is None")
            return
        if not ref.has_3d():
            # [seen] twice: MoveTo on a placed reference with no model never comes back.
            while True:
                yield ("block",)
        ref.pos = (target.pos[0] + x, target.pos[1] + y, target.pos[2] + z)
        self.check_distances()

    def n_objectreference_getdistance(self, ref, context, other):
        other = unwrap(other)
        if other is None:
            self.papyrus_error("GetDistance: the other object is None")
            return 0.0
        return math.dist(ref.pos, other.pos)

    def _disable(self, ref):
        ref.disabled = True
        if isinstance(ref, Actor):
            self._stop_combat(ref)

    def n_objectreference_disable(self, ref, context, fade=False):
        self._disable(ref)

    def n_objectreference_enable(self, ref, context, fade=False):
        ref.disabled = False

    def n_objectreference_delete(self, ref, context):
        ref.deleted = True

    def n_objectreference_isdisabled(self, ref, context):
        return ref.disabled

    def n_objectreference_is3dloaded(self, ref, context):
        return ref.has_3d()

    def n_objectreference_additem(self, ref, context, form, count=1, silent=False):
        form = unwrap(form)
        if form is None:
            self.papyrus_error("AddItem: the item is None")
            return
        ref.inventory[form] = ref.inventory.get(form, 0) + int(count)

    def n_objectreference_removeitem(self, ref, context, form, count=1, silent=False, other=None):
        form = unwrap(form)
        have = ref.inventory.get(form, 0)
        take = min(have, int(count))
        if take:
            ref.inventory[form] = have - take
            if other is not None:
                unwrap(other).inventory[form] = unwrap(other).inventory.get(form, 0) + take

    def n_objectreference_getitemcount(self, ref, context, form=None):
        form = unwrap(form)
        if form is None:
            return sum(ref.inventory.values())
        return ref.inventory.get(form, 0)

    def n_objectreference_removeallitems(self, ref, context, transfer_to=None, keep_ownership=False):
        ref.inventory = {}                          # [seen] through the wagon alias

    # Actor
    def aliases_holding(self, actor):
        return [a for q in self.quests.values() if q.running for a in q.aliases.values() if a.ref is actor]

    def is_essential(self, actor) -> bool:
        if actor.essential_override is not None:
            return actor.essential_override
        return any("Essential" in a.flags for a in self.aliases_holding(actor))     # [seen] IsEssential true in such an alias

    def is_protected(self, actor) -> bool:
        if actor.protected_override is not None:
            return actor.protected_override                                           # [seen] SetProtected(false) wins over the alias
        return any("Protected" in a.flags for a in self.aliases_holding(actor))

    def player_in_combat(self) -> bool:
        return any(a.combat_target is self.player and not a.dead and not a.disabled for a in self.actors)

    def _stop_combat(self, actor: Actor):
        if actor.combat_target is not None:
            actor.combat_target = None
            self.actor_event(actor, "OnCombatStateChanged", [None, 0], COMBAT_EVENT_DELAY)

    def n_actor_kill(self, actor, context, killer=None):
        killer = unwrap(killer)
        if actor.dead:
            return
        if self.is_essential(actor):
            return                                  # [seen] Kill(player) does not kill an actor in an Essential alias
        if self.is_protected(actor) and not (killer is not None and killer.is_player):
            return                                  # [seen] with no killer; [documented] only the player may kill
        actor.dead = True                           # [seen] IsDead is true at once
        actor.combat_target = None
        for other in self.actors:
            if other.combat_target is actor:
                self._stop_combat(other)
        self.actor_event(actor, "OnDeath", [killer], DEATH_EVENT_DELAY)

    def n_actor_isdead(self, actor, context):
        return actor.dead

    def n_objectreference_isindialoguewithplayer(self, ref, context):
        # [documented] "Is this actor or talking activator currently talking
        # to the player?" [assumed] not once it is dead or disabled. Not seen
        # in the game either way: the project has no dialogue yet.
        return bool(ref.talking_to_player) and not getattr(ref, "dead", False) and not ref.disabled

    def n_actor_isessential(self, actor, context):
        return self.is_essential(actor)

    def n_actor_setprotected(self, actor, context, protected=True):
        actor.protected_override = truthy(protected)

    def n_actor_isincombat(self, actor, context):
        if actor.is_player:
            return self.player_in_combat()          # [seen] true while an actor fights the player, false after it dies
        return actor.combat_target is not None

    def n_actor_startcombat(self, actor, context, target, preferred=False):
        target = unwrap(target)
        if actor.dead or actor.disabled or target is None:
            return
        actor.combat_target = target
        # [seen] the alias script hears it, with the player as target
        self.actor_event(actor, "OnCombatStateChanged", [target, 1], COMBAT_EVENT_DELAY)

    def n_actor_stopcombat(self, actor, context):
        # [documented] "Removes this actor from combat." [seen] together with
        # StopCombatAlarm on the player: the player was out of combat
        # afterwards and stayed out (case 121). Which of the two calls did it
        # was not told apart.
        self._stop_combat(actor)

    def n_actor_stopcombatalarm(self, actor, context):
        # [documented] "Stops all combat and alarms against this actor."
        for other in self.actors:
            if other.combat_target is actor:
                self._stop_combat(other)

    # ---- what a person or the runner does from outside the scripts
    def set_global(self, editor_id: str, value: float):
        self.forms[editor_id].value = float(value)

    def get_global(self, editor_id: str) -> int:
        return int(self.forms[editor_id].value)

    def enter_game(self):
        """Main menu, then the test room: quests flagged to start with the game start."""
        for quest in self.quests.values():
            if "StartGameEnabled" in quest.flags:
                self.start_quest(quest)

    def console_cqf(self, quest_id: str, function: str, args: list):
        """The console's  cqf <quest> <function> [arguments].  [seen] it finds a function on any script of the quest."""
        quest = self.quests[quest_id]
        for inst in quest.scripts:
            fn = inst.script.functions.get(function.lower())
            if fn:
                # [documented] missing parameters are filled with zero or None, not the script's defaults
                full = list(args) + [default_for(p.type) for p in fn.params[len(args):]]
                self.spawn(self.call(inst, fn, full), "cqf %s %s" % (quest_id, function))
                return
        raise SimError("cqf: no script on %s has a function %s" % (quest_id, function))


    def invoke(self, quest_id: str, function: str, args: list, until: float = 900.0):
        """Calls a function of a script on a quest and runs the session until it
        has come back. Returns what it returned. For tests."""
        quest = self.quests[quest_id]
        for inst in quest.scripts:
            fn = inst.script.functions.get(function.lower())
            if fn:
                box = {}

                def body():
                    box["value"] = yield from self.call(inst, fn, list(args))
                th = self.spawn(body(), "invoke %s.%s" % (quest_id, function))
                limit = self.now + until
                try:
                    while True:
                        self.run_ready()
                        # The clock must not run on once the function is back:
                        # whatever is due later belongs to what happens next.
                        if th.done or th.blocked:
                            break
                        if self.advance(limit) in ("idle", "timeout"):
                            break
                except QuitGame:
                    self.ended = "quit"
                if "value" not in box:
                    raise SimError("%s.%s did not come back" % (quest_id, function))
                return box["value"]
        raise SimError("no script on %s has a function %s" % (quest_id, function))


def run_scenario(scenario: int, scripts_folder, plugin_json, vanilla_json=None, natives_json=None,
                 until: float = 900.0, older_scripts: bool = False, native_delay: float = 0.0, shake=None) -> Session:
    """What tools/win/Run-Scenarios.ps1 does with the game: the scenario number
    goes into the plugin's global, the game enters the test room, and the
    self-test runs by itself until it closes the game."""
    s = Session(scripts_folder, plugin_json, vanilla_json, natives_json, older_scripts, native_delay, shake)
    s.set_global("TLM_G_DevScenario", scenario)
    s.enter_game()
    s.run(until)
    return s
