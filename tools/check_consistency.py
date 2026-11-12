#!/usr/bin/env python3
"""Cross-checks the three descriptions of the quests against each other.

  1. the Papyrus sources      scripts/Source/User/TLM/*.psc
  2. the plugin as written    build/TheLastMeridian.json (from tools/PluginBuilder)
  3. the logic model          tools/logic_model/tlm_model.py

It also lints the Papyrus against the native signatures documented on the
Creation Kit wiki (tools/papyrus_natives.json).

This is NOT a compiler and NOT a game test. It catches the mistakes that can
be caught without either: a stage the script handles but the plugin lacks, a
property the plugin fills that the script does not declare, a mandatory
property left empty, a native called with the wrong number of arguments, an
event handler with the wrong signature, constants that drifted apart.

Exit status 0 = no problems found.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PSC_DIR = ROOT / "scripts" / "Source" / "User" / "TLM"
PLUGIN_JSON = ROOT / "build" / "TheLastMeridian.json"
NATIVES = json.loads((ROOT / "tools" / "papyrus_natives.json").read_text())["natives"]
MODEL = (ROOT / "tools" / "logic_model" / "tlm_model.py").read_text()

# Base-game scripts the plugin attaches by name. Property names come from the
# wiki pages of the same name; the scripts themselves ship with the game.
DEFAULT_SCRIPTS = {
    "DefaultAliasOnContainerChangedTo": {"StageToSet"},
    "DefaultAliasOnTriggerEnter": {"StageToSet"},
}

problems = []


def problem(msg):
    problems.append(msg)


# ------------------------------------------------------------------ Papyrus

def strip_comments(text):
    out = []
    in_doc = False
    for line in text.splitlines():
        res = ""
        i = 0
        in_str = False
        while i < len(line):
            c = line[i]
            if in_doc:
                if c == "}":
                    in_doc = False
            elif in_str:
                res += c
                if c == '"':
                    in_str = False
            elif c == '"':
                in_str = True
                res += c
            elif c == "{":
                in_doc = True
            elif c == ";":
                break
            else:
                res += c
            i += 1
        out.append(res)
    return out


def split_args(s):
    """Top-level comma split of an argument list."""
    args, depth, cur, in_str = [], 0, "", False
    for c in s:
        if in_str:
            cur += c
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True
            cur += c
        elif c in "([":
            depth += 1
            cur += c
        elif c in ")]":
            depth -= 1
            cur += c
        elif c == "," and depth == 0:
            args.append(cur.strip())
            cur = ""
        else:
            cur += c
    if cur.strip():
        args.append(cur.strip())
    return args


def find_calls(line):
    """Yield (receiver or None, name, argc) for each call on a code line."""
    for m in re.finditer(r"(?:([A-Za-z_][\w:]*(?:\(\))?)\.)?([A-Za-z_]\w*)\(", line):
        start = m.end()
        depth, i = 1, start
        in_str = False
        while i < len(line) and depth:
            c = line[i]
            if in_str:
                in_str = c != '"'
            elif c == '"':
                in_str = True
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            i += 1
        if depth:
            continue
        yield m.group(1), m.group(2), len(split_args(line[start:i - 1]))


class Script:
    def __init__(self, path):
        self.path = path
        self.lines = strip_comments(path.read_text())
        head = next(l for l in self.lines if l.strip())
        m = re.match(r"\s*Scriptname\s+([\w:]+)\s+extends\s+(\w+)", head, re.I)
        self.name, self.extends = m.group(1), m.group(2)
        self.functions = {}      # name -> (min, max)
        self.events = {}         # name -> argc
        self.properties = {}     # name -> (type, mandatory)
        self.constants = {}      # name -> int
        self.stage_handlers = set()
        self.stage_refs = set()  # SetStage / GetStageDone on self
        self.foreign_stage_refs = {}  # property name -> {stages}
        self.parse()

    def parse(self):
        blocks = []
        for n, raw in enumerate(self.lines, 1):
            line = raw.strip()
            if not line:
                continue
            low = line.lower()
            m = re.match(r"(?:[\w:\[\]]+\s+)?function\s+(\w+)\s*\((.*)\)", line, re.I)
            if m and not low.startswith("endfunction"):
                params = split_args(m.group(2))
                self.functions[m.group(1)] = (sum("=" not in p for p in params), len(params))
                blocks.append(("function", n))
                continue
            m = re.match(r"event\s+([\w.]+)\s*\((.*)\)", line, re.I)
            if m:
                self.events[m.group(1)] = len(split_args(m.group(2)))
                blocks.append(("event", n))
                continue
            m = re.match(r"([\w:\[\]]+)\s+property\s+(\w+)(.*)$", line, re.I)
            if m:
                self.properties[m.group(2)] = (m.group(1), "mandatory" in m.group(3).lower())
                continue
            m = re.match(r"int\s+(\w+)\s*=\s*(-?\d+)\s+const\b", line, re.I)
            if m:
                self.constants[m.group(1)] = int(m.group(2))
                continue
            for opener, closer in (("if", "endif"), ("while", "endwhile"), ("group", "endgroup")):
                if re.match(opener + r"\b", low) and not low.startswith("end"):
                    blocks.append((opener, n))
                if low.startswith(closer):
                    if not blocks or blocks[-1][0] != opener:
                        problem(f"{self.path.name}:{n}: {closer} without matching {opener}")
                    else:
                        blocks.pop()
            for closer, opener in (("endfunction", "function"), ("endevent", "event")):
                if low.startswith(closer):
                    if not blocks or blocks[-1][0] != opener:
                        problem(f"{self.path.name}:{n}: {closer} without matching {opener}")
                    else:
                        blocks.pop()
            for m in re.finditer(r"auiStageID\s*==\s*(\d+)", line):
                self.stage_handlers.add(int(m.group(1)))
            m = re.search(r"auiStageID\s*>=\s*(\d+)\s*&&\s*auiStageID\s*<=\s*(\d+)", line)
            if m:
                self.stage_handlers.update(range(int(m.group(1)), int(m.group(2)) + 1))
            for m in re.finditer(r"(?:(\w+)\.)?(?:SetStage|GetStageDone)\((\d+)\)", line):
                if m.group(1) in (None, "q"):
                    self.stage_refs.add(int(m.group(2)))
                else:
                    self.foreign_stage_refs.setdefault(m.group(1), set()).add(int(m.group(2)))
            # TLM:SelfTest sets stages through its helper: Reach(<quest property>, <stage>)
            for m in re.finditer(r"\bReach\((\w+),\s*(\d+)\)", line):
                self.foreign_stage_refs.setdefault(m.group(1), set()).add(int(m.group(2)))
        for kind, n in blocks:
            problem(f"{self.path.name}:{n}: {kind} is never closed")


scripts = {s.name: s for s in (Script(p) for p in sorted(PSC_DIR.glob("*.psc")))}

for s in scripts.values():
    expected_path = PSC_DIR.parent / (s.name.replace(":", "/") + ".psc")
    if expected_path.resolve() != s.path.resolve():
        problem(f"{s.path.name}: Scriptname {s.name} does not match its folder (expected {expected_path.relative_to(ROOT)})")

    for ev, argc in s.events.items():
        sigs = NATIVES.get(ev)
        if not sigs:
            problem(f"{s.path.name}: event {ev} has no documented signature in papyrus_natives.json")
        elif not any(x["kind"] == "event" and x["max_args"] == argc for x in sigs):
            problem(f"{s.path.name}: event {ev} declared with {argc} parameter(s); documented: "
                    + ", ".join(str(x["max_args"]) for x in sigs))

    project_functions = {}
    for other in scripts.values():
        for fn, arity in other.functions.items():
            project_functions.setdefault(fn, []).append(arity)

    for n, raw in enumerate(s.lines, 1):
        line = raw.strip()
        if re.match(r"(?:[\w:\[\]]+\s+)?(function|event)\b", line, re.I) or line.lower().startswith("scriptname"):
            continue
        for receiver, name, argc in find_calls(line):
            if receiver is None and name in s.functions:
                lo, hi = s.functions[name]
            elif name in NATIVES:
                ok = [x for x in NATIVES[name] if x["min_args"] <= argc <= x["max_args"]]
                if not ok:
                    problem(f"{s.path.name}:{n}: {name}() called with {argc} argument(s); documented "
                            + " or ".join(f"{x['min_args']}-{x['max_args']}" for x in NATIVES[name]))
                continue
            elif name in project_functions:
                lo, hi = project_functions[name][0]
            else:
                problem(f"{s.path.name}:{n}: {name}() is neither defined in the project nor in papyrus_natives.json")
                continue
            if not lo <= argc <= hi:
                problem(f"{s.path.name}:{n}: {name}() called with {argc} argument(s), takes {lo}-{hi}")

# ------------------------------------------------------------- plugin JSON

if not PLUGIN_JSON.exists():
    problem(f"{PLUGIN_JSON.relative_to(ROOT)} not found: run  dotnet run --project tools/PluginBuilder")
    plugin = {"Quests": [], "Messages": []}
else:
    plugin = json.loads(PLUGIN_JSON.read_text())

messages = {m["EditorId"]: m for m in plugin["Messages"]}
quests = {q["EditorId"]: q for q in plugin["Quests"]}
quest_of_script = {}


def check_binding(quest, where, bind):
    stages = {s["Index"] for s in quest["Stages"]}
    name = bind["Name"]
    props = {p["Name"]: p for p in bind["Props"]}
    if name in scripts:
        s = scripts[name]
        quest_of_script.setdefault(name, set()).add(quest["EditorId"])
        for pname, p in props.items():
            if pname not in s.properties:
                problem(f"{where}: plugin fills {name}.{pname}, which the script does not declare")
                continue
            ptype = s.properties[pname][0].lower()
            kind = p["Kind"]
            if kind == "int" and ptype != "int":
                problem(f"{where}: {name}.{pname} is {ptype} in the script but int in the plugin")
            if kind == "bool" and ptype != "bool":
                problem(f"{where}: {name}.{pname} is {ptype} in the script but bool in the plugin")
            if kind == "int[]" and ptype != "int[]":
                problem(f"{where}: {name}.{pname} is {ptype} in the script but int[] in the plugin")
            if kind == "object":
                if p["Alias"] is not None and ptype != "referencealias":
                    problem(f"{where}: {name}.{pname} is {ptype} in the script but an alias in the plugin")
                if p["Alias"] is None and ptype in ("int", "bool", "float", "int[]", "referencealias"):
                    problem(f"{where}: {name}.{pname} is {ptype} in the script but a form in the plugin")
        for pname, (ptype, mandatory) in s.properties.items():
            if mandatory and pname not in props:
                problem(f"{where}: mandatory property {name}.{pname} is not filled")
    elif name in DEFAULT_SCRIPTS:
        for pname in props:
            if pname not in DEFAULT_SCRIPTS[name]:
                problem(f"{where}: {name} has no documented property {pname}")
    else:
        problem(f"{where}: script {name} is neither a project script nor a known default script")

    for pname in ("StageToSet", "StageAlways", "RequireStageDone", "BlockIfStageDone"):
        if pname in props and props[pname]["Value"] not in stages and props[pname]["Value"] != 0:
            problem(f"{where}: {name}.{pname} = {props[pname]['Value']} is not a stage of {quest['EditorId']}")
    if "ButtonStages" in props:
        values = props["ButtonStages"]["Value"]
        for v in values:
            if v != 0 and v not in stages:
                problem(f"{where}: ButtonStages entry {v} is not a stage of {quest['EditorId']}")
        msg = messages.get(props.get("MessageToShow", {}).get("Target"))
        if msg is None:
            problem(f"{where}: ButtonStages without a resolvable MessageToShow")
        elif len(msg["Buttons"]) != len(values):
            problem(f"{where}: {len(values)} ButtonStages for {len(msg['Buttons'])} buttons on {msg['EditorId']}")


for q in quests.values():
    for bind in q["Scripts"]:
        check_binding(q, q["EditorId"], bind)
    for a in q["Aliases"]:
        for bind in a["Scripts"]:
            check_binding(q, f"{q['EditorId']} alias {a['Name']}", bind)

# Stage numbers used by each quest script must exist in its quest.
for name, s in scripts.items():
    for qid in quest_of_script.get(name, ()):
        q = quests[qid]
        if s.extends.lower() != "quest":
            continue
        stages = {x["Index"] for x in q["Stages"]}
        for st in sorted(s.stage_handlers - stages):
            problem(f"{name}: OnStageSet handles stage {st}, which {qid} does not have")
        for st in sorted(s.stage_refs - stages):
            problem(f"{name}: refers to stage {st}, which {qid} does not have")
        # Every stage with gameplay meaning should be handled or be a pure marker.
        for prop, refs in s.foreign_stage_refs.items():
            target = next((p["Target"] for b in q["Scripts"] if b["Name"] == name
                           for p in b["Props"] if p["Name"] == prop), None)
            if target in quests:
                missing = refs - {x["Index"] for x in quests[target]["Stages"]}
                for st in sorted(missing):
                    problem(f"{name}: sets stage {st} on {target}, which does not have it")

# ------------------------------------------------------------- logic model

def model_const(name):
    m = re.search(r"^" + name + r"\s*=\s*(-?\d+)\s*$", MODEL, re.M)
    if m:
        return int(m.group(1))
    m = re.search(r"^([A-Z_, ]+)=\s*((?:-?\d+\s*,\s*)+-?\d+)\s*$", MODEL, re.M)
    for m in re.finditer(r"^([A-Z_, ]+?)\s*=\s*((?:-?\d+\s*,\s*)+-?\d+)\s*$", MODEL, re.M):
        names = [x.strip() for x in m.group(1).split(",")]
        vals = [int(x) for x in m.group(2).split(",")]
        if name in names:
            return vals[names.index(name)]
    m = re.search(r"^([A-Z_, ]+?)\s*=\s*range\((\d+)\)\s*$", MODEL, re.M)
    if m:
        names = [x.strip() for x in m.group(1).split(",")]
        if name in names:
            return names.index(name)
    return None


for s in scripts.values():
    for cname, value in s.constants.items():
        want = model_const(cname)
        if want is not None and want != value:
            problem(f"{s.path.name}: {cname} = {value}, but the logic model has {want}")

model_mq_stages, model_sq_stages = set(), set()
for line in MODEL.splitlines():
    nums = {int(x) for x in re.findall(r",\s*(\d+)\)", line)}
    if "sq_set_stage(" in line:
        model_sq_stages |= nums
    elif "set_stage(" in line and not line.lstrip().startswith("def "):
        model_mq_stages |= nums
if "TLM_MQ01" in quests:
    have = {x["Index"] for x in quests["TLM_MQ01"]["Stages"]}
    for st in sorted(model_mq_stages - have):
        problem(f"logic model sets MQ01 stage {st}, which the plugin does not have")
if "TLM_SQ01" in quests:
    have = {x["Index"] for x in quests["TLM_SQ01"]["Stages"]}
    for st in sorted(model_sq_stages - have):
        problem(f"logic model sets SQ01 stage {st}, which the plugin does not have")

# ------------------------------------------------------------------ report

print(f"scripts checked: {len(scripts)}  "
      f"({sum(len(s.functions) for s in scripts.values())} functions, "
      f"{sum(len(s.events) for s in scripts.values())} events, "
      f"{sum(len(s.properties) for s in scripts.values())} properties)")
print(f"plugin: {len(quests)} quests, {sum(len(q['Stages']) for q in quests.values())} stages, "
      f"{sum(len(q['Aliases']) for q in quests.values())} aliases")
print(f"logic model stages: MQ01 {sorted(model_mq_stages)}  SQ01 {sorted(model_sq_stages)}")
if problems:
    print(f"\n{len(problems)} problem(s):")
    for p in problems:
        print("  - " + p)
    sys.exit(1)
print("\nno problems found (documentation-level check; nothing was compiled or run in the game)")
