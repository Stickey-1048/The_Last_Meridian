#!/usr/bin/env python3
"""A reference selector for talk in the tlm-talk-2 format.

It answers two questions about a folder of story material, by the rules of
docs/design/ACT1_ENTRY_SELECTION_CONTRACT.md:

  greet(speaker, state)          what does this person say when spoken to?
  press(line, button, state)     what happens when this button is chosen?

It is for the checks and for people reviewing a folder. It is NOT the game and
not an adapter to it: it knows nothing of scenes, timers, inventories, who is
standing where, or what a quest does when one of its stages is set. A stage
that a button sets is noted as set and nothing more; that is a stand-in, and
the tests that use it say so. An answer here is not proof of anything in the
game.

Conditions are the ones tools/check_story_intake.py accepts, checked by that
check's own code before they are evaluated: there is no second grammar.

No dependencies beyond the check itself.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_story_intake as intake                             # noqa: E402

DEFAULT_WORD = {"outcome": "none", "method": "none", "answer": "none", "ledger": "none"}   # debrief has no "none"
COMPARE = {">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b, "==": lambda a, b: a == b, "<": lambda a, b: a < b, ">": lambda a, b: a > b}


class State:
    """What is true at one moment, as far as a condition can ask."""

    def __init__(self, stages=None, words=None, counters=None, flags=(), dead=(), caps=0):
        self.stages = {k: set(v) for k, v in (stages or {}).items()}     # quest key -> the stages that are set
        self.words = dict(words or {})                                   # outcome, method, debrief, answer, ledger
        self.counters = dict(counters or {})                             # truth, evidence, ...
        self.flags = set(flags)
        self.dead = set(dead)
        self.caps = caps

    def done(self, quest, stage):
        return stage in self.stages.get(quest, ())


class Result:
    """line: the id of the line now on the screen, or None if the box closes.
    effects: what a button did, in order. diagnostic: why nothing is said, when that is not the ordinary close."""

    def __init__(self, line=None, effects=(), diagnostic=None):
        self.line, self.effects, self.diagnostic = line, list(effects), diagnostic

    def __repr__(self):
        return "Result(line=%r, effects=%r, diagnostic=%r)" % (self.line, self.effects, self.diagnostic)


class Selector:
    def __init__(self, files, validate=True):
        """files: relative path -> text, as tools/check_story_intake.read_folder gives.

        validate=False takes a folder the check would refuse. It exists for one purpose: to show that the
        selector fails closed on a folder that got past the check wrongly."""
        self.check = intake.Intake(files, strict=False)
        problems = self.check.run()
        if validate and problems:
            raise ValueError("the folder does not pass the intake check: %s" % "; ".join(problems[:3]))
        self.lines = {}
        for path in sorted(p for p in files if p.startswith("talk/") and p.endswith(".json")):
            data = json.loads(files[path])
            if data.get("lines") and data.get("format") != intake.TALK_V2:
                raise ValueError("%s is %s: this selector is for tlm-talk-2 and does not guess at the first format" % (path, data.get("format")))
            for line in data.get("lines", []):
                self.lines.setdefault(line["id"], line)

    # ---- conditions: the check's own grammar, then the answer
    def holds(self, text, state):
        before = len(self.check.problems)
        self.check.condition("selector", text)
        if len(self.check.problems) > before:
            problem = self.check.problems[before]
            del self.check.problems[before:]
            raise ValueError(problem)
        w = text.split()
        if len(w) == 3 and w[1] in ("done", "notdone"):
            return state.done(w[0], int(w[2])) == (w[1] == "done")
        if len(w) == 3 and w[1] in ("is", "isnot"):
            return (state.words.get(w[0], DEFAULT_WORD.get(w[0])) == w[2]) == (w[1] == "is")
        if len(w) == 3:
            return COMPARE[w[1]](state.counters.get(w[0], 0), int(w[2]))
        if w[0] in ("alive", "dead"):
            return (w[1] in state.dead) == (w[0] == "dead")
        return (w[1] in state.flags) == (w[0] == "flag")

    def valid(self, line, state):
        return all(self.holds(c, state) for c in line.get("when") or [])

    # ---- speaking to a person
    def greet(self, speaker, state):
        """Only boxed lines that say entry true are considered. The highest priority among those whose conditions
        all hold is said. None eligible: nothing is said. Two equal at the top: nothing is said."""
        eligible = [l for l in self.lines.values()
                    if l.get("speaker") == speaker and l.get("kind", "talk") != "aside" and l.get("entry") is True and self.valid(l, state)]
        if not eligible:
            return Result(diagnostic="no eligible entry for %s: nothing is said" % speaker)
        top = max(l.get("priority", 0) for l in eligible)
        best = sorted(l["id"] for l in eligible if l.get("priority", 0) == top)
        if len(best) > 1:
            return Result(diagnostic="ambiguous for %s: %s all have priority %d; nothing is said" % (speaker, ", ".join(best), top))
        return Result(line=best[0])

    # ---- choosing a button
    def press(self, line_id, button, state, speech=None):
        """button: its place in the line's list, from 0. speech: True or False where the button has a check.

        The line on the screen is checked again first. The branch's effects are applied once, in the order
        written. A 'then' is looked up by its exact id and its conditions asked AFTER the effects; if they
        hold it is said, whatever its entry or priority. If they do not, the box closes, the effects stay,
        and the diagnostic says so. state is changed in place."""
        line = self.lines[line_id]
        if not self.valid(line, state):
            return Result(diagnostic="%s is no longer valid: no effects were applied and nothing follows" % line_id)
        buttons = line.get("buttons") or []
        # The format supplies a single Continue-close when no choices were
        # authored. It is not an effect-bearing or inferred transition.
        if type(button) is not int or button < 0 or button >= max(1, len(buttons)):
            raise ValueError("%s has no button at index %r" % (line_id, button))
        if not buttons:
            return Result()
        chosen = buttons[button]
        branch = chosen
        if "check" in chosen:
            if speech is not True and speech is not False:
                raise ValueError("%s, button %d has a check: say whether it passed" % (line_id, button))
            branch = chosen["pass"] if speech else chosen["fail"]
        effects = []
        for effect in branch.get("do") or []:
            w = effect.split()
            if w[1] == "set":
                state.stages.setdefault(w[0], set()).add(int(w[2]))     # a stand-in: the stage is noted, the quest's own doing is not played
            else:
                state.caps += int(w[2])
            effects.append(effect)
        target = branch.get("then")
        if target is None:
            return Result(effects=effects)
        if target not in self.lines:
            raise LookupError("%s leads on to '%s', which is no line" % (line_id, target))
        if self.lines[target].get("kind") == "aside":
            raise LookupError("%s leads on to '%s', which is an aside" % (line_id, target))
        if not self.valid(self.lines[target], state):
            return Result(effects=effects, diagnostic="%s is not available after %s: the box closes; the effects were applied and are not undone" % (
                target, ", ".join(effects) or "no effects"))
        return Result(line=target, effects=effects)


def from_folder(folder, validate=True):
    return Selector(intake.read_folder(folder), validate=validate)


if __name__ == "__main__":
    print(__doc__)
