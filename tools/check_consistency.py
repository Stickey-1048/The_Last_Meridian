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
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PSC_DIR = ROOT / "scripts" / "Source" / "User" / "TLM"
def projection_path(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plugin-json', type=Path, default=ROOT / 'build' / 'TheLastMeridian.json',
                        help='Actual plugin readback projection; absent/invalid input remains a failure')
    return parser.parse_args(argv).plugin_json

PLUGIN_JSON = projection_path()
NATIVES = json.loads((ROOT / "tools" / "papyrus_natives.json").read_text())["natives"]
MODEL = (ROOT / "tools" / "logic_model" / "tlm_model.py").read_text()

# Base-game scripts the plugin attaches by name. Property names come from the
# wiki pages of the same name; the scripts themselves ship with the game.
DEFAULT_SCRIPTS = {
    "DefaultAliasOnContainerChangedTo": {"StageToSet", "ShowTraces"},
    "DefaultAliasOnTriggerEnter": {"StageToSet", "ShowTraces"},
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


def expression_start(line, end):
    """Start of a receiver ending at end, including chained calls or casts."""
    end = len(line[:end].rstrip())
    if not end:
        return end
    start = end
    if line[end - 1] == ')':
        depth = 1
        start = end - 1
        while start and depth:
            start -= 1
            depth += (line[start] == ')') - (line[start] == '(')
        if depth:
            return end
        prefix = re.search(r'[A-Za-z_][\w:]*$', line[:start].rstrip())
        if prefix and prefix.group().lower() not in {"if", "elseif", "while", "return"}:
            start = prefix.start()
    else:
        token = re.search(r'[A-Za-z_][\w:]*$', line[:end])
        if not token:
            return end
        start = token.start()
    before = len(line[:start].rstrip())
    if before and line[before - 1] == '.':
        start = expression_start(line, before - 1)
    return start


def find_calls(line):
    """Yield actual calls with complete receiver expressions; ignore quoted text."""
    quoted = False
    positions = set()
    for i, c in enumerate(line):
        if c == '"':
            quoted = not quoted
        if quoted:
            positions.add(i)
    for m in re.finditer(r'([A-Za-z_][\w:]*)\s*\(', line):
        if m.start() in positions or m.group(1).lower() in {"if", "elseif", "while", "return"}:
            continue
        start = m.end()
        depth, i, in_str = 1, start, False
        while i < len(line) and depth:
            c = line[i]
            if c == '"':
                in_str = not in_str
            elif not in_str:
                depth += (c == '(') - (c == ')')
            i += 1
        if depth:
            continue
        before = len(line[:m.start()].rstrip())
        receiver = None
        if before and line[before - 1] == '.':
            end = before - 1
            receiver = line[expression_start(line, end):end].strip()
        yield receiver, m.group(1), len(split_args(line[start:i - 1]))


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
        self.collect_types()

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

    def collect_types(self):
        self.returns, self.line_types = {}, {}
        fields = {name.lower(): value[0] for name, value in self.properties.items()}
        scope = None
        for n, raw in enumerate(self.lines, 1):
            line = raw.strip()
            fn = re.match(r'(?:(\w[\w:\[\]]*)\s+)?function\s+(\w+)\s*\((.*)\)', line, re.I)
            ev = re.match(r'event\s+[\w.]+\s*\((.*)\)', line, re.I)
            if fn or ev:
                if fn:
                    self.returns[fn.group(2).lower()] = fn.group(1) or ''
                params = split_args(fn.group(3) if fn else ev.group(1))
                scope = {}
                for param in params:
                    bits = param.split('=', 1)[0].split()
                    if len(bits) == 2:
                        scope[bits[1].lower()] = bits[0]
            elif re.match(r'end(function|event)\b', line, re.I):
                scope = None
            else:
                declaration = re.match(r'([\w:\[\]]+)\s+(\w+)(?:\s*=|\s*$)', line)
                if declaration and declaration.group(1).lower() not in {'return', 'if', 'elseif', 'while'}:
                    (fields if scope is None else scope)[declaration.group(2).lower()] = declaration.group(1)
            self.line_types[n] = fields | (scope or {})


def project_script(name, scripts):
    matches = [value for key, value in scripts.items() if key.lower() == name.lower()]
    return matches[0] if len(matches) == 1 else None


def member_return(type_name, member, scripts, natives):
    target = project_script(type_name, scripts)
    if target and member.lower() in target.returns:
        return target.returns[member.lower()]
    options = [v for k, values in natives.items() if k.lower() == member.lower() for v in values
               if v['owner'].lower() == type_name.lower() and v['kind'] == 'function']
    types = {v['returns'] for v in options}
    return next(iter(types)) if len(types) == 1 else None


def receiver_type(expression, script, line, scripts, natives):
    expression = expression.strip()
    if expression.startswith('('):
        depth, close = 0, None
        for i, char in enumerate(expression):
            depth += (char == '(') - (char == ')')
            if depth == 0:
                close = i
                break
        if close == len(expression) - 1:
            expression = expression[1:-1].strip()
    cast = re.search(r'\bas\s+([\w:\[\]]+)\s*$', expression, re.I)
    if cast:
        return cast.group(1)
    call = re.match(r'^(.*?)([A-Za-z_][\w]*)\((.*)\)$', expression)
    if call:
        prefix, member, _ = call.groups()
        owner = receiver_type(prefix[:-1], script, line, scripts, natives) if prefix.endswith('.') else script.name
        return member_return(owner, member, scripts, natives) if owner else None
    if expression.lower() == 'self':
        return script.name
    if expression.lower() in script.line_types.get(line, {}):
        return script.line_types[line][expression.lower()]
    if project_script(expression, scripts):
        return expression
    return None


def lint_source(script, scripts, natives, report):
    for event, argc in script.events.items():
        signatures = natives.get(event)
        if not signatures:
            report(f'{script.path.name}: event {event} has no documented signature in papyrus_natives.json')
        elif not any(v['kind'] == 'event' and v['max_args'] == argc for v in signatures):
            report(f'{script.path.name}: event {event} declared with {argc} parameter(s); documented: '
                   + ', '.join(str(v['max_args']) for v in signatures))
        elif event == 'Actor.OnPlayerLoadGame':
            declaration = next(l for l in script.lines if re.match(r'\s*event\s+Actor.OnPlayerLoadGame\s*\(', l, re.I))
            params = split_args(declaration[declaration.index('(') + 1:declaration.rindex(')')])
            if len(params) != 1 or params[0].split()[0].lower() != 'actor':
                report(f'{script.path.name}: event {event} requires Actor sender parameter')
    for n, raw in enumerate(script.lines, 1):
        line = raw.strip()
        if re.match(r'(?:[\w:\[\]]+\s+)?(function|event)\b', line, re.I) or line.lower().startswith('scriptname'):
            continue
        for receiver, name, argc in find_calls(line):
            target = script if receiver is None else project_script(receiver_type(receiver, script, n, scripts, natives) or '', scripts)
            functions = {key.lower(): value for key, value in target.functions.items()} if target else {}
            if name.lower() in functions:
                lo, hi = functions[name.lower()]
                if not lo <= argc <= hi:
                    report(f'{script.path.name}:{n}: {name}() called with {argc} argument(s), takes {lo}-{hi}')
            elif name in natives:
                if not any(v['kind'] == 'function' and v['min_args'] <= argc <= v['max_args'] for v in natives[name]):
                    report(f'{script.path.name}:{n}: {name}() called with {argc} argument(s); documented '
                           + ' or '.join(f"{v['min_args']}-{v['max_args']}" for v in natives[name]))
            elif receiver is not None and target is None:
                report(f'{script.path.name}:{n}: unresolved/ambiguous receiver {receiver} for {name}()')
            else:
                report(f'{script.path.name}:{n}: {name}() is not defined on '
                       + (target.name if target else script.name) + ' or documented in papyrus_natives.json')


scripts = {s.name: s for s in (Script(p) for p in sorted(PSC_DIR.glob("*.psc")))}

for s in scripts.values():
    expected_path = PSC_DIR.parent / (s.name.replace(":", "/") + ".psc")
    if expected_path.resolve() != s.path.resolve():
        problem(f"{s.path.name}: Scriptname {s.name} does not match its folder (expected {expected_path.relative_to(ROOT)})")

    lint_source(s, scripts, NATIVES, problem)

# ------------------------------------------------------------- plugin JSON


def validate_projection(plugin):
    """Validate fields consumed below; malformed/empty/duplicate input cannot pass."""
    def require(condition, message):
        if not condition:
            raise ValueError(message)
    require(isinstance(plugin, dict), 'projection must be an object')
    for kind in ('Quests', 'Messages'):
        rows = plugin.get(kind)
        require(isinstance(rows, list) and bool(rows), f'{kind} must be a nonempty array')
        ids = set()
        for row in rows:
            require(isinstance(row, dict), f'{kind} entry must be an object')
            key = row.get('EditorId')
            require(isinstance(key, str) and bool(key) and key not in ids, f'{kind} EditorId missing or duplicate')
            ids.add(key)
    def bindings(values):
        require(isinstance(values, list), 'Scripts must be an array')
        for bind in values:
            require(isinstance(bind, dict) and isinstance(bind.get('Name'), str), 'invalid script binding')
            require(isinstance(bind.get('Props'), list), 'Props must be an array')
            for prop in bind['Props']:
                require(isinstance(prop, dict) and {'Name', 'Kind', 'Target', 'Alias', 'Value'} <= prop.keys(), 'invalid property binding')
                require(isinstance(prop['Name'], str) and isinstance(prop['Kind'], str), 'invalid property name/kind')
    for quest in plugin['Quests']:
        require(isinstance(quest.get('Stages'), list), 'Stages must be an array')
        for stage in quest['Stages']:
            require(isinstance(stage, dict) and type(stage.get('Index')) is int, 'invalid stage Index')
        bindings(quest.get('Scripts'))
        require(isinstance(quest.get('Aliases'), list), 'Aliases must be an array')
        for alias in quest['Aliases']:
            require(isinstance(alias, dict) and isinstance(alias.get('Name'), str), 'invalid alias name')
            bindings(alias.get('Scripts'))
    for message in plugin['Messages']:
        require(isinstance(message.get('Buttons'), list), 'Buttons must be an array')
    return plugin

if not PLUGIN_JSON.exists():
    problem(f"{PLUGIN_JSON} not found: run  dotnet run --project tools/PluginBuilder")
    plugin = {"Quests": [], "Messages": []}
else:
    try:
        plugin = json.loads(PLUGIN_JSON.read_text(encoding='utf-8-sig'))
        validate_projection(plugin)
    except (OSError, UnicodeError, ValueError) as exc:
        problem(f'Invalid plugin projection: {exc}')
        plugin = {'Quests': [], 'Messages': []}

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
