#!/usr/bin/env python3
"""Checks a folder of story material against the intake format
(docs/design/STORY_INTAKE.md).

  python3 tools/check_story_intake.py <folder>             structure only
  python3 tools/check_story_intake.py --strict <folder>    and nothing left blank
  python3 tools/check_story_intake.py --self-test <folder> also damages the
                                       folder's files in some fifty ways, in
                                       memory, and expects each to be noticed
                                       for the reason it is wrong; and adds a
                                       sound last chapter, which has to pass

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
# A quest's id is its record's name: TLM_ and the key in capitals (mq02a is TLM_MQ02A).
QUEST_ID = re.compile(r"^TLM_[A-Z][A-Z0-9_]*$")
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
# The one place in Act I where part of that is said: its last chapter, where the canon has the player recover
# proof of having been a Meridian Rider and Mara Vale say that the player's family came from the Deep
# (docs/three-act-story.md, "05 The Fifth Rider"; docs/child-of-the-deep.md, quest beats: "Mara discloses only
# that the player's family came from the habitat"). So those three words, and no others, may be used by that
# quest and by the talk that belongs to it, and only when the quest file is the real one: this key, this id,
# this chapter, and no second file claiming it. The Charter, the Open Ledger and the vault stay unsaid in all
# of Act I. Everything else (the other chapters, town talk, every paper) is held to the whole list.
REVEALED = {"mq05": {"id": "TLM_MQ05", "chapter": 5, "words": ("deep", "meridian", "rider")}}
PRIORITY_MAX = 1000
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
        self.quest_ids = {v: k for k, v in QUEST_IDS.items()}   # id -> key, of every quest that may be named
        self.may_say = {}                                        # quest id -> the words of REVEALED it may use

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
    def text(self, where, value, most, act_one=True, allow_newlines=False, may_say=()):
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
                if word in may_say:
                    continue        # the last chapter's own quest and talk, and only these words (REVEALED)
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
        seen_keys, seen_ids = {}, {}
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
            # One file for each quest, whether the plugin has the quest or not: a second file about it would
            # be a second account of the same quest, and nothing says which of the two is meant.
            twice = key in seen_keys
            if twice:
                self.bad(path, "the key %s is also in %s: one file for each quest" % (key, seen_keys[key]))
            else:
                seen_keys[key] = path
            # Who the quest is. The key is what conditions and effects use; the id is the record's name.
            # They have to belong together, or a file could be read as being about another quest.
            qid = data.get("id")
            known = False
            if not isinstance(qid, str) or not QUEST_ID.match(qid):
                self.bad(path, "id is the quest's record name: TLM_ and the key in capitals, like TLM_MQ02A")
            elif existing and qid != QUEST_IDS[key]:
                self.bad(path, "%s is %s in the plugin; its id is that and no other, not %s" % (key, QUEST_IDS[key], qid))
            elif not existing and qid in QUEST_IDS.values():
                self.bad(path, "the id %s belongs to %s, which is in the plugin; a new quest has an id of its own" % (
                    qid, [k for k, v in QUEST_IDS.items() if v == qid][0]))
            elif not existing and qid != "TLM_" + key.upper():
                self.bad(path, "the id of %s is TLM_%s (TLM_ and the key in capitals), not %s" % (key, key.upper(), qid))
            elif qid in seen_ids:
                self.bad(path, "the id %s is also in %s" % (qid, seen_ids[qid]))
            else:
                known = not twice
            if isinstance(qid, str):
                seen_ids.setdefault(qid, path)
            stages = [s.get("n") for s in data.get("stages", [])]
            if not stages or not all(isinstance(n, int) and not isinstance(n, bool) and 0 < n < 1000 for n in stages):
                self.bad(path, "every stage has a number from 1 to 999")
                continue
            if len(set(stages)) != len(stages):
                self.bad(path, "a stage number is used twice")
            if existing:
                if sorted(stages) != sorted(QUEST_STAGES[key]):
                    self.bad(path, "%s is in the plugin with stages %s; a file about it lists those and no others" % (key, QUEST_STAGES[key]))
            elif not twice:
                self.quests[key] = stages
            if known:
                self.quest_ids[qid] = key
            for f in data.get("new_flags") or []:
                if not isinstance(f, dict) or not KEY.match(str(f.get("name"))) or not str(f.get("meaning", "")).strip():
                    self.bad(path, "a new flag has a lower-case name and a meaning")
                elif f["name"] in self.flags:
                    self.bad(path, "the flag %s is already there" % f["name"])
                else:
                    self.flags.append(f["name"])
            self._quest_data.append((path, key, data, stages, known))

    def quest_bodies(self):
        for path, key, data, stages, known in self._quest_data:
            # What this quest may say of what Act I does not know: nothing, unless it is the last chapter's own
            # quest, known for certain to be that one (REVEALED).
            may_say = ()
            reveal = REVEALED.get(key)
            if reveal:
                if data.get("chapter") != reveal["chapter"]:
                    self.bad(path, "%s is chapter %d of Act I, not %s" % (key, reveal["chapter"], data.get("chapter")))
                elif known and data.get("id") == reveal["id"]:
                    may_say = reveal["words"]
                    self.may_say[reveal["id"]] = may_say
            for name in ("title", "premise", "cannot_break"):
                if not isinstance(data.get(name), str):
                    self.bad(path, "'%s' is text" % name)
                elif not data[name].strip():
                    self.blank(path, name)
            if data.get("kind") not in ("main", "side"):
                self.bad(path, "kind is main or side")
            if not isinstance(data.get("chapter"), int) or isinstance(data.get("chapter"), bool) or not 1 <= data["chapter"] <= 5:
                self.bad(path, "chapter is a number from 1 to 5: this intake is for Act I")
            if sum(1 for s in data["stages"] if s.get("completes")) != 1:
                self.bad(path, "exactly one stage completes the quest")
            for s in data["stages"]:
                where = "%s, stage %s" % (path, s.get("n"))
                if not str(s.get("set_by", "")).strip():
                    self.blank(where, "set_by (what in the world sets it)")
                if s.get("log") is not None:
                    self.text(where + ", log", s["log"], TEXT_MAX, may_say=may_say)
            for o in data.get("objectives") or []:
                self.text("%s, objective %s" % (path, o.get("n")), o.get("text"), 100, may_say=may_say)
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
                    self.text(where + ", an option", o.get("label"), LABEL_MAX, may_say=may_say)
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
            # Which quest the talk belongs to: one the plugin has, or one a file under quests/ here declares
            # (and declares soundly). Talk that belongs to none is in talk/town.json and says so with null.
            quest = data.get("quest")
            may_say = ()
            if path == "talk/town.json":
                if quest is not None:
                    self.bad(path, "talk/town.json belongs to no quest: its quest is null, not %r" % (quest,))
            elif not isinstance(quest, str) or quest not in self.quest_ids:
                self.bad(path, "quest is %r, which is the id of no quest here: it is one of %s, or the id a file under quests/ gives" % (
                    quest, ", ".join(sorted(QUEST_IDS.values()))))
            else:
                may_say = self.may_say.get(quest, ())
            for line in data.get("lines", []):
                lid = line.get("id")
                where = "%s, %s" % (path, lid)
                if not isinstance(lid, str) or not KEY.match(lid):
                    self.bad(where, "id is a short lower-case word")
                    continue
                if lid in self.line_ids:
                    self.bad(where, "that id is also in %s" % self.line_ids[lid])
                self.line_ids[lid] = path
                lines.append((where, line, may_say))
        for where, line, may_say in lines:
            if line.get("speaker") not in self.characters:
                self.bad(where, "no character '%s'" % (line.get("speaker"),))
            if line.get("kind", "talk") not in ("talk", "aside"):
                self.bad(where, "kind is talk (a box) or aside (a line at the edge of the screen)")
            if line.get("status") not in ("design", "new"):
                self.bad(where, "status is design (it is in the designs already) or new")
            self.text(where, line.get("text"), TEXT_MAX, may_say=may_say)
            # The line with the highest priority among those whose conditions hold is the one said, so a
            # priority has to be a number that can be compared: a whole one. Left out, it is 0.
            priority = line.get("priority", 0)
            if isinstance(priority, bool) or not isinstance(priority, int) or not 0 <= priority <= PRIORITY_MAX:
                self.bad(where, "priority is a whole number from 0 to %d (left out, it is 0); %r is not" % (PRIORITY_MAX, priority))
            for c in line.get("when") or []:
                self.condition(where, c)
            buttons = line.get("buttons") or []
            if line.get("kind") == "aside" and buttons:
                self.bad(where, "an aside has no buttons")
            if len(buttons) > BUTTONS_MAX:
                self.bad(where, "has %d buttons; a box holds %d" % (len(buttons), BUTTONS_MAX))
            for b in buttons:
                self.text(where + ", a button", b.get("label"), LABEL_MAX, may_say=may_say)
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


NOBODY_KNOWS = "which nobody in Act I knows of"
# Words for the self-test only. They are not story text and nothing is built from them.
PROBE = "TEST PROBE, not story text: the Deep, MERIDIAN, a Rider."
PROBE_TOO_FAR = ["TEST PROBE, not story text: the Charter.", "TEST PROBE, not story text: the Open Ledger.",
                 "TEST PROBE, not story text: a vault."]


def changed_in(files, path, change):
    out = dict(files)
    data = json.loads(out[path])
    change(data)
    out[path] = json.dumps(data)
    return out


def with_last_chapter(files):
    """The folder with a sound last chapter added: the quest mq05, its talk, and the one who speaks in it.

    The last chapter is where the canon lets three of Act I's unsaid words be said (REVEALED). The worked
    example has no such chapter, and its writing is not this tool's to do, so the self-test brings its own,
    made of probe text.
    """
    out = dict(files)
    quest = {
        "format": "tlm-quest-1", "key": "mq05", "id": "TLM_MQ05", "title": "The Fifth Rider", "chapter": 5, "kind": "main",
        "premise": "Test probe.", "draws_on": [], "reads": [], "cast": ["probe"], "places": [],
        "stages": [{"n": 10, "set_by": "test probe", "log": PROBE},
                   {"n": 100, "set_by": "test probe", "log": None, "completes": True}],
        "objectives": [{"n": 10, "text": "TEST PROBE: a Meridian Rider, the Deep"}],
        "choices": [{"at": 10, "options": [{"label": "TEST PROBE: the Deep", "sets": 100, "now": "probe", "later": "probe"},
                                           {"label": "TEST PROBE: no", "now": "probe", "later": "probe"}]}],
        "evidence": [], "ways_through": ["test probe one", "test probe two"], "cannot_break": "Test probe.",
        "new_flags": [], "open_questions": [],
    }
    talk = {"format": "tlm-talk-1", "quest": "TLM_MQ05", "lines": [
        {"id": "probe_last_chapter", "speaker": "probe", "status": "new", "priority": 0, "when": [], "text": PROBE,
         "buttons": [{"label": "TEST PROBE: the Rider"}], "sources": []}]}
    probe = {"id": "probe", "record": None, "status": "proposed", "name": "Test Probe", "sex": "female",
             "role": "probe", "looks": "probe", "voice": "probe", "wants": "probe", "fears": "probe", "secret": "probe",
             "wrong_about": "probe", "knows": [], "does_not_know": [], "ties": [], "sources": []}
    people = json.loads(out["characters.json"]) if "characters.json" in out else {"format": "tlm-characters-1", "characters": []}
    people["characters"].append(probe)
    out["characters.json"] = json.dumps(people)
    out["quests/tlm_mq05.json"] = json.dumps(quest)
    out["talk/tlm_mq05.json"] = json.dumps(talk)
    return out


def sound(files):
    """(what it is, the files) for folders the check has to let through."""
    out = [("the folder with a sound last chapter that says what the canon lets it say", with_last_chapter(files))]
    talk = sorted(p for p in files if p.startswith("talk/") and p != "talk/town.json")
    if talk:
        t = talk[0]
        out += [
            ("a line with no priority given", changed_in(files, t, lambda d: d["lines"][0].pop("priority", None))),
            ("a line with the highest priority there is", changed_in(files, t, lambda d: d["lines"][0].update(priority=PRIORITY_MAX))),
            ("talk that belongs to no quest, in talk/town.json", dict(files, **{"talk/town.json": json.dumps(
                {"format": "tlm-talk-1", "quest": None, "lines": []})})),
        ]
    return out


def damages(files):
    """(what was done, the damaged files, what the check has to say) for each kind of damage it has to notice.

    The last is a piece of the message, or several; None where any complaint will do.
    """
    def changed(path, change):
        return changed_in(files, path, change)
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
            ("a line that names what Act I does not know", changed(t, lambda d: first(d).update(text="They say the Deep is open.")), NOBODY_KNOWS),
            ("a line with a percent sign", changed(t, lambda d: first(d).update(text="Half. 50% of it."))),
            ("a box with five buttons", changed(t, lambda d: boxed(d).update(buttons=[{"label": "a"}] * 5))),
            ("a button that sets a stage the quest does not have", changed(t, lambda d: boxed(d)["buttons"].append({"label": "x", "do": ["mq01 set 77"]}) or boxed(d).update(buttons=boxed(d)["buttons"][-1:]))),
            ("a button that sets a stage only the quest's script may set", changed(t, lambda d: boxed(d).update(buttons=[{"label": "x", "do": ["mq01 set 100"]}]))),
            ("a button that leads on to no line", changed(t, lambda d: boxed(d).update(buttons=[{"label": "x", "then": "nowhere"}]))),
            ("a condition in words the format does not have", changed(t, lambda d: first(d).update(when=["if the player is kind"]))),
            ("a condition on an outcome that does not exist", changed(t, lambda d: first(d).update(when=["outcome is won"]))),
            ("two lines with one id", changed(t, lambda d: d["lines"].append(copy.deepcopy(d["lines"][0])))),
            # which quest a talk file belongs to
            ("talk about a quest that does not exist", changed(t, lambda d: d.update(quest="TLM_DOES_NOT_EXIST")), "is the id of no quest here"),
            ("talk that names no quest", changed(t, lambda d: d.pop("quest")), "is the id of no quest here"),
            ("talk that names a quest by its key instead of its id", changed(t, lambda d: d.update(quest="mq01")), "is the id of no quest here"),
            ("town talk that claims a quest", dict(files, **{"talk/town.json": json.dumps(
                {"format": "tlm-talk-1", "quest": "TLM_MQ01", "lines": []})}), "talk/town.json belongs to no quest"),
            # priority is a number that can be compared
            ("a priority in words", changed(t, lambda d: first(d).update(priority="higher")), "priority is a whole number"),
            ("a priority that is a number in quotes", changed(t, lambda d: first(d).update(priority="10")), "priority is a whole number"),
            ("a priority that is not whole", changed(t, lambda d: first(d).update(priority=2.5)), "priority is a whole number"),
            ("a priority below nothing", changed(t, lambda d: first(d).update(priority=-1)), "priority is a whole number"),
            ("a priority that is yes or no", changed(t, lambda d: first(d).update(priority=True)), "priority is a whole number"),
            ("a priority that is nothing", changed(t, lambda d: first(d).update(priority=None)), "priority is a whole number"),
            ("a priority beyond the highest", changed(t, lambda d: first(d).update(priority=PRIORITY_MAX + 1)), "priority is a whole number"),
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
        # who a quest is: the key and the id belong together, and each quest has one file
        key = json.loads(files[q]).get("key")
        if key in QUEST_IDS:
            other = [v for k, v in sorted(QUEST_IDS.items()) if k != key][0]
            out += [
                ("a quest of the plugin's under another quest's id", changed(q, lambda d: d.update(id=other)), "its id is that and no other"),
                ("a quest of the plugin's under an id nothing has", changed(q, lambda d: d.update(id="TLM_DOES_NOT_EXIST")), "its id is that and no other"),
                ("a quest with no id", changed(q, lambda d: d.pop("id")), "id is the quest's record name"),
                ("a quest whose id is not a record name", changed(q, lambda d: d.update(id="tlm sq01")), "id is the quest's record name"),
                ("a second file about a quest of the plugin's", dict(files, **{"quests/duplicate_%s.json" % key: files[q]}), "one file for each quest"),
                ("a quest of the plugin's whose log names what Act I does not know",
                 changed(q, lambda d: d["stages"][0].update(log=PROBE)), NOBODY_KNOWS),
            ]
    # The last chapter: three words may be said there, by the quest that is really that chapter and its talk.
    last = with_last_chapter(files)
    mq05, talk05 = "quests/tlm_mq05.json", "talk/tlm_mq05.json"
    def last_changed(path, change):                                                 # noqa: E306
        return changed_in(last, path, change)
    out += [
        ("the last chapter's quest given as another chapter", last_changed(mq05, lambda d: d.update(chapter=4)),
         ("mq05 is chapter 5", NOBODY_KNOWS)),
        ("the last chapter's quest under the id of a quest of the plugin's", last_changed(mq05, lambda d: d.update(id="TLM_MQ01")),
         ("belongs to mq01", NOBODY_KNOWS)),
        ("the last chapter's quest under an id that is not its own", last_changed(mq05, lambda d: d.update(id="TLM_MQ04")),
         ("the id of mq05 is TLM_MQ05", NOBODY_KNOWS)),
        ("another quest that takes the last chapter's id", last_changed(mq05, lambda d: d.update(key="mq05x")),
         ("the id of mq05x is TLM_MQ05X", NOBODY_KNOWS)),
        ("a quest of another name that says it is chapter 5", last_changed(mq05, lambda d: d.update(key="sq05", id="TLM_SQ05")),
         NOBODY_KNOWS),
        ("two files that both say they are the last chapter's quest", dict(last, **{"quests/tlm_mq05_again.json": last[mq05]}),
         ("one file for each quest", NOBODY_KNOWS)),
        ("talk that says it belongs to the last chapter, whose quest file is not there",
         {k: v for k, v in last.items() if k != mq05}, ("is the id of no quest here", NOBODY_KNOWS)),
        ("talk of the last chapter moved under a quest of the plugin's", last_changed(talk05, lambda d: d.update(quest="TLM_MQ01")),
         NOBODY_KNOWS),
        ("town talk that says what the last chapter may", dict(last, **{"talk/town.json": json.dumps(
            {"format": "tlm-talk-1", "quest": None, "lines": [dict(json.loads(last[talk05])["lines"][0], id="probe_town")]})}),
         NOBODY_KNOWS),
    ]
    for too_far in PROBE_TOO_FAR:
        word = too_far.split(": ")[1].rstrip(".")
        out += [
            ("the last chapter's quest saying more than the canon lets it (%s)" % word,
             last_changed(mq05, lambda d, x=too_far: d["stages"][0].update(log=x)), NOBODY_KNOWS),
            ("the last chapter's talk saying more than the canon lets it (%s)" % word,
             last_changed(talk05, lambda d, x=too_far: d["lines"][0].update(text=x)), NOBODY_KNOWS),
        ]
    if talk:
        out.append(("a line of the first chapter saying what only the last may, with the last chapter present",
                    last_changed(talk[0], lambda d: d["lines"][0].update(text=PROBE)), NOBODY_KNOWS))
    if "documents.json" in files:
        out.append(("a paper saying what only the last chapter's quest and talk may, with the last chapter present",
                    last_changed("documents.json", lambda d: d["documents"][0].update(text=PROBE)), NOBODY_KNOWS))
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
        return self_test(files)
    return 0


def noticed(problems, must_say):
    """Whether the check complained, and of the right thing."""
    if not problems:
        return False
    wanted = [must_say] if isinstance(must_say, str) else list(must_say or [])
    return all(any(w in p for p in problems) for w in wanted)


def self_test(files):
    failed = False
    # What has to pass. Checked strictly where the folder itself passes strictly, so that a blank the worked
    # example leaves on purpose is not held against what the self-test adds.
    strict = not Intake(files, strict=True).run()
    passing = sound(files)
    for what, good in passing:
        problems = Intake(good, strict=strict).run()
        if problems:
            failed = True
            print("STORY INTAKE SELF-TEST FAILED: refused, though it is sound: %s" % what)
            for p in problems[:6]:
                print("    " + p)
    # What has to be refused, and for the reason it is wrong.
    tried = damages(files)
    unnoticed = []
    for case in tried:
        what, damaged = case[0], case[1]
        must_say = case[2] if len(case) > 2 else None
        problems = Intake(damaged, strict=False).run()
        if not noticed(problems, must_say):
            unnoticed.append("%s (it said: %s)" % (what, "; ".join(problems[:3]) or "nothing"))
    whole = all(p in files for p in ("characters.json", "documents.json", "RESEARCH.md")) and \
        any(p.startswith("talk/") for p in files) and any(json.loads(files[p]).get("key") in QUEST_IDS
                                                           for p in files if p.startswith("quests/"))
    if unnoticed or (whole and len(tried) < 55):
        failed = True
        print("STORY INTAKE SELF-TEST FAILED: %d kinds of damage tried; not noticed, or not for the right reason:" % len(tried))
        for u in unnoticed:
            print("    " + u)
    if failed:
        return 1
    print("story intake: %d kinds of deliberate damage were each caught, for the reason each is wrong; %d sound folders passed" % (
        len(tried), len(passing)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
