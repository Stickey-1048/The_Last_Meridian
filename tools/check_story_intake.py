#!/usr/bin/env python3
"""Checks a folder of story material against the intake format
(docs/design/STORY_INTAKE.md).

  python3 tools/check_story_intake.py <folder>             structure only
  python3 tools/check_story_intake.py --strict <folder>    and nothing left blank
  python3 tools/check_story_intake.py --self-test <folder> also damages the
                                       folder's files in a dozen ways, in
                                       memory, and expects each to be noticed

The folder holds any of: characters.json, talk/*.json, quests/*.json,
documents.json, RESEARCH.md. What is written there comes from outside the
repository (the owner's writing partner). This check says whether the
mechanics can take it in as it stands: that every name it uses is one the
plugin and the scripts know, that a box has no more buttons than a box can
have, that a line of Act I does not say what nobody in Act I knows.

It says NOTHING about whether the writing is good, and nothing is canon
because it passes: the owner decides that.
"""
import copy
import json
import re
import sys
from pathlib import Path

# ---- what the plugin and the scripts know today (docs/design/STORY_INTAKE.md has the same tables)
QUEST_STAGES = {
    "mq01": [10, 15, 20, 30, 31, 32, 33, 34, 35, 37, 40, 50, 51, 52, 53, 54, 55, 60, 100],
    "sq01": [5, 10, 11, 12, 13, 14, 20, 25, 41, 42, 43, 44, 45, 46, 50, 100],
}
QUEST_IDS = {"mq01": "TLM_MQ01", "sq01": "TLM_SQ01"}
# Stages a line of talk must not set: the quests' own scripts set them.
NOT_FOR_TALK = {"mq01": {10, 100}, "sq01": {5, 20, 25, 50, 100}}
WORDS = {
    "outcome": ["none", "saved", "evaded", "exploited", "missed"],
    "method": ["none", "deal", "betrayal"],
    "debrief": ["saved", "evaded", "witness", "no_witness", "missed", "lost"],
    "answer": ["none", "admit", "deny", "confess", "blame", "lying", "silent"],
    "ledger": ["none", "reported", "posted", "posted_yard", "posted_haskell", "sold", "destroyed"],
}
COUNTERS = ["truth", "competence", "accountability", "mutual_trust", "regard", "evidence"]
FLAGS = ["yard_alerted", "vane_has_ledger", "haskell_scapegoated"]
CHARACTERS = {
    "pritchard": "TLM_NPC_SHERIFF_MERCY", "pike": "TLM_NPC_GUNSMITH_MERCY", "vane": "TLM_NPC_MERCHANT_MERCY",
    "keene": "TLM_NPC_PHYSICIAN_MERCY", "talbot": "TLM_NPC_DEPUTY_MERCY", "haskell": "TLM_NPC_FREIGHT_MERCY",
    "gantt": "TLM_NPC_MARSHAL_DEAD", "nell": "TLM_NPC_CARAVAN_MASTER", "abel": "TLM_NPC_CARAVAN_DROVER",
    "dunmore": "TLM_NPC_CUTTER_LEAD", "cutter": None,
}
# What nobody in Act I knows of (CANON.md), and what a message cannot hold.
NOT_IN_ACT_ONE = ["deep", "meridian", "rider", "charter", "open ledger", "vault"]
TEXT_MAX, LABEL_MAX, BUTTONS_MAX, DOCUMENT_MAX = 240, 48, 4, 1500
KEY = re.compile(r"^[a-z][a-z0-9_]*$")
SOURCE = re.compile(r"^R\d+$")
KINDS = ["REAL", "FALLOUT", "INVENTED"]


class Intake:
    def __init__(self, files, strict=False):
        """files: relative path -> text."""
        self.files = files
        self.strict = strict
        self.problems, self.blanks = [], []
        self.characters = dict(CHARACTERS)
        self.quests = {k: list(v) for k, v in QUEST_STAGES.items()}
        self.flags = list(FLAGS)
        self.sources = {}
        self.line_ids = {}

    def bad(self, where, what):
        self.problems.append("%s: %s" % (where, what))

    def blank(self, where, what):
        (self.problems if self.strict else self.blanks).append("%s: %s is left blank" % (where, what))

    def load(self, path):
        try:
            return json.loads(self.files[path])
        except ValueError as e:
            self.bad(path, "is not JSON (%s)" % e)
            return None

    # ---- text that goes on the screen
    def text(self, where, value, most, act_one=True, allow_newlines=False):
        if not isinstance(value, str) or not value.strip():
            self.bad(where, "has no text")
            return
        if len(value) > most:
            self.bad(where, "is %d characters; at most %d" % (len(value), most))
        if any(ord(c) > 126 or (ord(c) < 32 and not (allow_newlines and c == "\n")) for c in value):
            self.bad(where, "has a character that is not plain ASCII (curly quotes, long dashes and accents do not survive)")
        if "%" in value:
            self.bad(where, "has a percent sign, which a message takes for a number to fill in")
        if not allow_newlines and '"' in value:
            self.bad(where, 'has a double quote; the speaker\'s words are put in quotes when the line is built')
        if act_one:
            low = value.lower()
            for word in NOT_IN_ACT_ONE:
                if re.search(r"\b%s\b" % re.escape(word), low):
                    self.bad(where, "says '%s', which nobody in Act I knows of" % word)

    # ---- the small language of conditions and effects
    def condition(self, where, text):
        words = text.split() if isinstance(text, str) else []
        if len(words) == 3 and words[0] in self.quests and words[1] in ("done", "notdone") and words[2].isdigit():
            if int(words[2]) not in self.quests[words[0]]:
                self.bad(where, "'%s': %s has no stage %s" % (text, words[0], words[2]))
        elif len(words) == 3 and words[0] in WORDS and words[1] in ("is", "isnot"):
            if words[2] not in WORDS[words[0]]:
                self.bad(where, "'%s': %s is one of %s" % (text, words[0], ", ".join(WORDS[words[0]])))
        elif len(words) == 3 and words[0] in COUNTERS and words[1] in (">=", "<=", "==", "<", ">") and re.match(r"^-?\d+$", words[2]):
            pass
        elif len(words) == 2 and words[0] in ("alive", "dead"):
            if words[1] not in self.characters:
                self.bad(where, "'%s': no character '%s'" % (text, words[1]))
        elif len(words) == 2 and words[0] in ("flag", "notflag"):
            if words[1] not in self.flags:
                self.bad(where, "'%s': no flag '%s'" % (text, words[1]))
        else:
            self.bad(where, "'%s' is not a condition this format has" % (text,))

    def effect(self, where, text):
        words = text.split() if isinstance(text, str) else []
        if len(words) == 3 and words[0] in self.quests and words[1] == "set" and words[2].isdigit():
            stage = int(words[2])
            if stage not in self.quests[words[0]]:
                self.bad(where, "'%s': %s has no stage %s" % (text, words[0], words[2]))
            elif stage in NOT_FOR_TALK.get(words[0], ()):
                self.bad(where, "'%s': that stage is set by the quest's own script, not by a line" % text)
        elif len(words) == 3 and words[:2] == ["give", "caps"] and words[2].isdigit() and 0 < int(words[2]) <= 500:
            pass
        else:
            self.bad(where, "'%s' is not an effect this format has" % (text,))

    # ---- the files
    def research(self):
        path = "RESEARCH.md"
        if path not in self.files:
            return
        for n, line in enumerate(self.files[path].splitlines(), 1):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not line.strip().startswith("|") or not cells or not SOURCE.match(cells[0]):
                continue
            where = "%s line %d (%s)" % (path, n, cells[0])
            if cells[0] in self.sources:
                self.bad(where, "that number is used twice")
            if len(cells) != 5:
                self.bad(where, "a row has five cells: number, what was looked up, source, what it gave the story, kind")
                continue
            kind = cells[4].strip("* ")
            if kind not in KINDS:
                self.bad(where, "kind is one of %s" % ", ".join(KINDS))
            if kind in ("REAL", "FALLOUT") and not re.search(r"https?://\S+", cells[2]):
                self.bad(where, "a %s row needs the address it was read at" % kind)
            for i, name in ((1, "what was looked up"), (2, "the source"), (3, "what it gave the story")):
                if not cells[i]:
                    self.bad(where, "%s is empty" % name)
            self.sources[cells[0]] = kind

    def cites(self, where, value):
        if value is None:
            return
        if not isinstance(value, list):
            self.bad(where, "sources are a list of numbers from RESEARCH.md, like [\"R3\"]")
            return
        for s in value:
            if not isinstance(s, str) or not SOURCE.match(s):
                self.bad(where, "'%s' is not a number from RESEARCH.md" % (s,))
            elif s not in self.sources:
                self.bad(where, "%s is not in RESEARCH.md" % s)

    def characters_file(self):
        path = "characters.json"
        if path not in self.files:
            return
        data = self.load(path)
        if data is None:
            return
        if data.get("format") != "tlm-characters-1":
            self.bad(path, "format is not tlm-characters-1")
        seen = set()
        for c in data.get("characters", []):
            key = c.get("id")
            where = "%s, %s" % (path, key)
            if not isinstance(key, str) or not KEY.match(key):
                self.bad(where, "id is a short lower-case word")
                continue
            if key in seen:
                self.bad(where, "is there twice")
            seen.add(key)
            status = c.get("status")
            if status not in ("canon", "provisional", "proposed"):
                self.bad(where, "status is canon, provisional or proposed")
            if key in CHARACTERS:
                if c.get("record") != CHARACTERS[key]:
                    self.bad(where, "record is %s for this character" % CHARACTERS[key])
                if status == "proposed":
                    self.bad(where, "is already in the plugin: canon or provisional, not proposed")
            else:
                if c.get("record") is not None:
                    self.bad(where, "a new character has no record yet (null)")
                if status != "proposed":
                    self.bad(where, "a character the plugin does not have is 'proposed' until the owner accepts it")
                self.characters[key] = None
            if not isinstance(c.get("name"), str) or not c["name"].strip():
                self.bad(where, "has no name")
            if c.get("sex") not in ("male", "female"):
                self.bad(where, "sex is male or female (the builder picks a face by it)")
            for name in ("role", "looks", "voice", "wants", "fears", "secret", "wrong_about"):
                if not isinstance(c.get(name), str):
                    self.bad(where, "'%s' is text" % name)
                elif not c[name].strip():
                    self.blank(where, name)
            for name in ("knows", "does_not_know"):
                if not isinstance(c.get(name), list) or not all(isinstance(x, str) for x in c[name]):
                    self.bad(where, "'%s' is a list of short statements" % name)
            self.cites(where, c.get("sources"))
            self._ties = getattr(self, "_ties", [])
            for tie in c.get("ties") or []:
                self._ties.append((where, tie.get("to") if isinstance(tie, dict) else None))
        for where, to in getattr(self, "_ties", []):
            if to not in self.characters:
                self.bad(where, "is tied to '%s', who is no character" % (to,))

    def quest_files(self):
        self._quest_data = []
        for path in sorted(p for p in self.files if p.startswith("quests/") and p.endswith(".json")):
            data = self.load(path)
            if data is None:
                continue
            if data.get("format") != "tlm-quest-1":
                self.bad(path, "format is not tlm-quest-1")
            key = data.get("key")
            if not isinstance(key, str) or not KEY.match(key):
                self.bad(path, "key is a short lower-case word, like mq02a")
                continue
            existing = key in QUEST_STAGES
            stages = [s.get("n") for s in data.get("stages", [])]
            if not stages or not all(isinstance(n, int) and 0 < n < 1000 for n in stages):
                self.bad(path, "every stage has a number from 1 to 999")
                continue
            if len(set(stages)) != len(stages):
                self.bad(path, "a stage number is used twice")
            if existing:
                if sorted(stages) != sorted(QUEST_STAGES[key]):
                    self.bad(path, "%s is in the plugin with stages %s; a file about it lists those and no others" % (key, QUEST_STAGES[key]))
            elif key in self.quests:
                self.bad(path, "the key %s is used by two files" % key)
            self.quests[key] = stages
            for f in data.get("new_flags") or []:
                if not isinstance(f, dict) or not KEY.match(str(f.get("name"))) or not str(f.get("meaning", "")).strip():
                    self.bad(path, "a new flag has a lower-case name and a meaning")
                elif f["name"] in self.flags:
                    self.bad(path, "the flag %s is already there" % f["name"])
                else:
                    self.flags.append(f["name"])
            self._quest_data.append((path, key, data, stages))

    def quest_bodies(self):
        for path, key, data, stages in self._quest_data:
            for name in ("title", "premise", "cannot_break"):
                if not isinstance(data.get(name), str):
                    self.bad(path, "'%s' is text" % name)
                elif not data[name].strip():
                    self.blank(path, name)
            if data.get("kind") not in ("main", "side"):
                self.bad(path, "kind is main or side")
            if not isinstance(data.get("chapter"), int) or not 1 <= data["chapter"] <= 5:
                self.bad(path, "chapter is a number from 1 to 5: this intake is for Act I")
            if sum(1 for s in data["stages"] if s.get("completes")) != 1:
                self.bad(path, "exactly one stage completes the quest")
            for s in data["stages"]:
                where = "%s, stage %s" % (path, s.get("n"))
                if not str(s.get("set_by", "")).strip():
                    self.blank(where, "set_by (what in the world sets it)")
                if s.get("log") is not None:
                    self.text(where + ", log", s["log"], TEXT_MAX)
            for o in data.get("objectives") or []:
                self.text("%s, objective %s" % (path, o.get("n")), o.get("text"), 100)
            for c in data.get("cast") or []:
                if c not in self.characters:
                    self.bad(path, "cast: no character '%s' (a new one goes into characters.json as proposed)" % (c,))
            for r in data.get("reads") or []:
                self.condition(path + ", reads", r)
            for ch in data.get("choices") or []:
                options = ch.get("options") or []
                where = "%s, the choice at stage %s" % (path, ch.get("at"))
                if ch.get("at") not in stages:
                    self.bad(where, "is at no stage of this quest")
                if not 2 <= len(options) <= BUTTONS_MAX:
                    self.bad(where, "has %d options; two to %d" % (len(options), BUTTONS_MAX))
                for o in options:
                    self.text(where + ", an option", o.get("label"), LABEL_MAX)
                    if o.get("sets") is not None and o["sets"] not in stages:
                        self.bad(where, "an option sets stage %s, which the quest does not have" % (o.get("sets"),))
                    for name in ("now", "later"):
                        if not str(o.get(name, "")).strip():
                            self.blank(where, "what the option '%s' changes %s" % (o.get("label"), name))
            ids = set()
            for e in data.get("evidence") or []:
                where = "%s, evidence %s" % (path, e.get("id"))
                if not KEY.match(str(e.get("id"))) or e["id"] in ids:
                    self.bad(where, "has no id of its own")
                ids.add(e.get("id"))
                if e.get("sets") is not None and e["sets"] not in stages:
                    self.bad(where, "sets stage %s, which the quest does not have" % (e.get("sets"),))
            ways = data.get("ways_through") or []
            if len(ways) < 2:
                self.bad(path, "ways_through: at least two, and one that needs nothing optional")
            self.cites(path, data.get("draws_on"))

    def talk_files(self):
        lines = []
        for path in sorted(p for p in self.files if p.startswith("talk/") and p.endswith(".json")):
            data = self.load(path)
            if data is None:
                continue
            if data.get("format") != "tlm-talk-1":
                self.bad(path, "format is not tlm-talk-1")
            for line in data.get("lines", []):
                lid = line.get("id")
                where = "%s, %s" % (path, lid)
                if not isinstance(lid, str) or not KEY.match(lid):
                    self.bad(where, "id is a short lower-case word")
                    continue
                if lid in self.line_ids:
                    self.bad(where, "that id is also in %s" % self.line_ids[lid])
                self.line_ids[lid] = path
                lines.append((where, line))
        for where, line in lines:
            if line.get("speaker") not in self.characters:
                self.bad(where, "no character '%s'" % (line.get("speaker"),))
            if line.get("kind", "talk") not in ("talk", "aside"):
                self.bad(where, "kind is talk (a box) or aside (a line at the edge of the screen)")
            if line.get("status") not in ("design", "new"):
                self.bad(where, "status is design (it is in the designs already) or new")
            self.text(where, line.get("text"), TEXT_MAX)
            for c in line.get("when") or []:
                self.condition(where, c)
            buttons = line.get("buttons") or []
            if line.get("kind") == "aside" and buttons:
                self.bad(where, "an aside has no buttons")
            if len(buttons) > BUTTONS_MAX:
                self.bad(where, "has %d buttons; a box holds %d" % (len(buttons), BUTTONS_MAX))
            for b in buttons:
                self.text(where + ", a button", b.get("label"), LABEL_MAX)
                outcomes = [b]
                if "check" in b:
                    if b["check"] != "speech":
                        self.bad(where, "the only check is speech")
                    if not isinstance(b.get("pass"), dict) or not isinstance(b.get("fail"), dict):
                        self.bad(where, "a button with a check says what follows if it passes and if it fails")
                    if b.get("do") or b.get("then"):
                        self.bad(where, "a button with a check has its effects under pass and fail")
                    outcomes = [x for x in (b.get("pass"), b.get("fail")) if isinstance(x, dict)]
                for o in outcomes:
                    for e in o.get("do") or []:
                        self.effect(where, e)
                    if o.get("then") is not None and o["then"] not in self.line_ids:
                        self.bad(where, "leads on to '%s', which is no line" % (o["then"],))
            self.cites(where, line.get("sources"))

    def documents_file(self):
        path = "documents.json"
        if path not in self.files:
            return
        data = self.load(path)
        if data is None:
            return
        if data.get("format") != "tlm-documents-1":
            self.bad(path, "format is not tlm-documents-1")
        seen = set()
        for d in data.get("documents", []):
            where = "%s, %s" % (path, d.get("id"))
            if not KEY.match(str(d.get("id"))) or d["id"] in seen:
                self.bad(where, "has no id of its own")
            seen.add(d.get("id"))
            self.text(where + ", title", d.get("title"), 60)
            self.text(where, d.get("text"), DOCUMENT_MAX, allow_newlines=True)
            if d.get("kind") not in ("note", "letter", "ledger", "notice", "label"):
                self.bad(where, "kind is note, letter, ledger, notice or label")
            if not str(d.get("found", "")).strip():
                self.blank(where, "found (where it lies)")
            self.cites(where, d.get("sources"))

    def run(self):
        self.research()
        self.characters_file()
        self.quest_files()
        self.quest_bodies()
        self.talk_files()
        self.documents_file()
        return self.problems


def read_folder(folder):
    folder = Path(folder)
    files = {}
    for p in sorted(folder.rglob("*")):
        rel = p.relative_to(folder).as_posix()
        if p.is_file() and (rel in ("characters.json", "documents.json", "RESEARCH.md")
                            or (rel.startswith(("talk/", "quests/")) and rel.endswith(".json"))):
            files[rel] = p.read_text(encoding="utf-8")
    return files


def damages(files):
    """(what was done, the damaged files) for each kind of damage the check has to notice."""
    def changed(path, change):
        out = dict(files)
        data = json.loads(out[path])
        change(data)
        out[path] = json.dumps(data)
        return out
    talk = sorted(p for p in files if p.startswith("talk/"))
    quests = sorted(p for p in files if p.startswith("quests/"))
    out = []
    if talk:
        t = talk[0]
        first = lambda d: d["lines"][0]                                             # noqa: E731
        boxed = lambda d: [l for l in d["lines"] if l.get("buttons")][0]            # noqa: E731
        out += [
            ("a line by somebody who is no character", changed(t, lambda d: first(d).update(speaker="nobody"))),
            ("a line longer than a box holds", changed(t, lambda d: first(d).update(text="x" * (TEXT_MAX + 1)))),
            ("a line with a curly quote", changed(t, lambda d: first(d).update(text="It’s late."))),
            ("a line that names what Act I does not know", changed(t, lambda d: first(d).update(text="They say the Deep is open."))),
            ("a line with a percent sign", changed(t, lambda d: first(d).update(text="Half. 50% of it."))),
            ("a box with five buttons", changed(t, lambda d: boxed(d).update(buttons=[{"label": "a"}] * 5))),
            ("a button that sets a stage the quest does not have", changed(t, lambda d: boxed(d)["buttons"].append({"label": "x", "do": ["mq01 set 77"]}) or boxed(d).update(buttons=boxed(d)["buttons"][-1:]))),
            ("a button that sets a stage only the quest's script may set", changed(t, lambda d: boxed(d).update(buttons=[{"label": "x", "do": ["mq01 set 100"]}]))),
            ("a button that leads on to no line", changed(t, lambda d: boxed(d).update(buttons=[{"label": "x", "then": "nowhere"}]))),
            ("a condition in words the format does not have", changed(t, lambda d: first(d).update(when=["if the player is kind"]))),
            ("a condition on an outcome that does not exist", changed(t, lambda d: first(d).update(when=["outcome is won"]))),
            ("two lines with one id", changed(t, lambda d: d["lines"].append(copy.deepcopy(d["lines"][0])))),
        ]
    if "characters.json" in files:
        c = "characters.json"
        out += [
            ("a character of the plugin's under another record", changed(c, lambda d: d["characters"][0].update(record="TLM_NPC_SOMEBODY"))),
            ("a new character passed off as canon", changed(c, lambda d: d["characters"].append(dict(d["characters"][0], id="stranger", record=None, status="canon")))),
            ("a character tied to nobody", changed(c, lambda d: d["characters"][0].update(ties=[{"to": "nobody", "what": "x"}]))),
            ("a source that is not in the research", changed(c, lambda d: d["characters"][0].update(sources=["R999"]))),
        ]
    if quests:
        q = quests[0]
        out += [
            ("a quest with two stages that complete it", changed(q, lambda d: [s.update(completes=True) for s in d["stages"][:2]])),
            ("a choice with one option", changed(q, lambda d: d.update(choices=[{"at": d["stages"][0]["n"], "options": [{"label": "x", "now": "a", "later": "b"}]}]))),
            ("a quest with one way through", changed(q, lambda d: d.update(ways_through=["only this"]))),
            ("a quest of the plugin's with a stage it does not have", changed(q, lambda d: d["stages"].append({"n": 999, "set_by": "x"}))),
        ]
    if "RESEARCH.md" in files:
        text = files["RESEARCH.md"]
        # A row said to be from the real world must say where it was read: take the addresses away, and call a
        # row of the project's own real.
        out.append(("a real-world source with no address",
                    dict(files, **{"RESEARCH.md": re.sub(r"https?://\S+", "a book", text).replace("| INVENTED |", "| REAL |", 1)})))
    if "documents.json" in files:
        out.append(("a document too long to read", changed("documents.json", lambda d: d["documents"][0].update(text="x" * (DOCUMENT_MAX + 1)))))
    return out


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    files = read_folder(args[0])
    if not files:
        print("%s: nothing to check (no characters.json, talk/, quests/, documents.json or RESEARCH.md)" % args[0])
        return 1
    intake = Intake(files, strict="--strict" in argv)
    problems = intake.run()
    if problems:
        print("STORY INTAKE CHECK FAILED (%d):" % len(problems))
        for p in problems:
            print("  " + p)
        return 1
    print("story intake: %d file(s) in %s fit the format: %d character(s), %d quest file(s), %d line(s) of talk, %d source(s)" % (
        len(files), args[0], len(intake.characters) - len(CHARACTERS) + sum(1 for k in CHARACTERS if "characters.json" in files),
        len(intake._quest_data), len(intake.line_ids), len(intake.sources)))
    for b in intake.blanks:
        print("  left blank: " + b)
    if "--self-test" in argv:
        unnoticed = [what for what, damaged in damages(files) if not Intake(damaged, strict=False).run()]
        tried = len(damages(files))
        if unnoticed or tried < 12:
            print("STORY INTAKE SELF-TEST FAILED: %d kinds of damage tried; not noticed: %s" % (tried, unnoticed))
            return 1
        print("story intake: %d kinds of deliberate damage were each caught" % tried)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
