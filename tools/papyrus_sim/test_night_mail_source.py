"""The Night Mail's scripts as text (NIGHT-MAIL-STORY-001): what a compiler would
say of names, and what the road's rules script and its greybox may and may
not do. These are checks of source text. Nothing was compiled.

  - Each script declares every constant, alias and message it uses (the sim
    caught one such miss in the Greenwater repair; the consistency check does
    not see them).
  - The numbers the model, the rules script and the greybox share are the
    same numbers.
  - The rules script shows no box, starts no timer, listens to nothing and
    resets nothing; it is the only script that writes the road's facts and
    stages; the greybox writes none, and nothing here writes the side quest's.
  - The greybox hears exactly four kinds of event, through one alias script.
  - No QA helper, no scenario, no stat is touched, and no box is opened by a
    function that is not a use.

NONE OF THIS IS A COMPILE. Not a game test.
"""
import re
import sys
import unittest

from test_sim import ROOT, SCRIPTS

sys.path.insert(0, str(ROOT / "tools" / "logic_model"))
import night_mail_model as nm                                     # noqa: E402

ROAD = "MQ02AQuest.psc"
WALK = "NightMailWalk.psc"
TALK = "NightMailTalk.psc"


def code(name):
    """The script without its documentation, comments and string contents."""
    text = re.sub(r"\{[^}]*\}", "", (SCRIPTS / name).read_text())
    text = "\n".join(line.split(";")[0] for line in text.splitlines())
    return re.sub(r'"[^"\n]*"', '""', text)


def constants(name):
    return {m.group(1): int(m.group(2)) for m in re.finditer(r"^\s*int\s+(\w+)\s*=\s*(-?\d+)\s+Const", (SCRIPTS / name).read_text(), re.M)}


class Names(unittest.TestCase):
    def test_every_name_a_script_uses_is_one_it_declares(self):
        for name in (ROAD, WALK, TALK, "Act1Walk.psc"):
            text = code(name)
            declared = {m.lower() for m in re.findall(r"^\s*(?:int|float|bool|string)\s+(\w+)\s*=", text, re.M)}
            declared |= {m.lower() for m in re.findall(r"\bProperty\s+(\w+)", text)}
            # Not a name reached through another script's object (akRiver.NM_...): that one is the other's.
            used = set(re.findall(r"(?<![.\w])((?:NM|NW)_[A-Z0-9_]+|Alias_\w+|(?:Say|Note|Ask|Label|Report|RulesPage|ChalkPage|FlyleafPage)[A-Z]\w*)\b", text))
            functions = {m.lower() for m in re.findall(r"\bFunction\s+(\w+)", text)}
            missing = sorted(u for u in used if u.lower() not in declared and u.lower() not in functions)
            self.assertEqual(missing, [], name + " uses names it does not declare")

    def test_a_local_is_never_named_like_a_function_of_its_own_script(self):
        for name in (ROAD, WALK, TALK):
            text = code(name)
            functions = {m.lower() for m in re.findall(r"\bFunction\s+(\w+)", text)}
            local = {m.lower() for m in re.findall(r"^\s*(?:int|float|bool|string|Actor|ObjectReference|Message|Form|ReferenceAlias|Quest)\s+(\w+)\s*=", text, re.M)}
            self.assertEqual(sorted(local & functions), [], name)


class SharedNumbers(unittest.TestCase):
    def test_the_model_the_rules_and_the_greybox_use_the_same_numbers(self):
        road, walk = constants(ROAD), constants(WALK)
        for name, value in road.items():
            if hasattr(nm, name):
                self.assertEqual(getattr(nm, name), value, name)
        for name, value in walk.items():
            if name in road:
                self.assertEqual(road[name], value, "%s differs between the rules script and the greybox" % name)
            elif hasattr(nm, name):
                self.assertEqual(getattr(nm, name), value, name)
        # What the model counts on, by name.
        for name in ("NM_NONE", "NM_RUN", "NM_DEFEAT", "NM_SOLD", "NM_BACKED", "NM_MAIL_ABOARD", "NM_MAIL_DELIVERED", "NM_MAIL_RETAINED", "NM_MAIL_SEIZED",
                     "NM_TRAIN_YARD", "NM_TRAIN_CUT", "NM_TRAIN_PLATFORM", "NM_TRAIN_TAKEN", "NM_STAMP_NONE", "NM_STAMP_KEPT", "NM_STAMP_SIGNED",
                     "NM_STAMP_TAKEN", "NM_SHARE_CAPS", "NM_SQ01_SOLD"):
            self.assertIn(name, road, name)
            self.assertEqual(road[name], getattr(nm, name), name)

    def test_the_report_numbers_are_the_same_four_in_every_script_that_speaks_them(self):
        walk, act1 = (SCRIPTS / WALK).read_text(), (SCRIPTS / "Act1Walk.psc").read_text()
        for name, value in (("NONE", 0), ("GIVEN", 1), ("LATER", 2), ("CLOSED", 3)):
            self.assertIn("int NW_REPORT_%s = %d Const" % (name, value), walk)
            self.assertIn("int RIVER_REPORT_%s = %d Const" % (name, value), act1)
        body = walk.split("int Function OfferReport(Actor akSheriff)")[1].split("EndFunction")[0]
        returns = re.findall(r"^\s*Return (.*)$", body, re.M)
        self.assertEqual(sorted(set(returns)), ["NW_REPORT_CLOSED", "NW_REPORT_GIVEN", "NW_REPORT_LATER", "NW_REPORT_NONE"])
        rail = act1.split("int Function OfferRailReport(Actor akWho)")[1].split("EndFunction")[0]
        for value in set(re.findall(r"^\s*Return (.*)$", rail, re.M)):
            self.assertTrue(value.startswith("RIVER_REPORT_") or "OfferReport" in value, value)


class TheRulesScript(unittest.TestCase):
    def setUp(self):
        self.road = code(ROAD)
        self.walk = code(WALK)
        self.talk = code(TALK)

    def test_the_rules_script_shows_nothing_listens_to_nothing_and_resets_nothing(self):
        for forbidden in (".Show(", "StartTimer", "RegisterFor", "OnInit", "OnPlayerLoadGame", "OnQuestInit", "Stop()", "Reset()",
                          "TLM_MQ01.SetStage", "TLM_SQ01", ".Enable", ".Disable", "Debug.MessageBox", "StartCombat"):
            self.assertNotIn(forbidden, self.road, forbidden)

    def test_the_greybox_writes_no_fact_no_stage_and_nothing_of_the_side_quest(self):
        for forbidden in ("SetStage(", "SetValue", "StartTimer", "OnPlayerLoadGame", "Stop()", "Reset()", "TLM_SQ01", "TLM_G_MQ02A", "TLM_G_SQ01"):
            self.assertNotIn(forbidden, self.walk, forbidden)
        # What it does ask of the game: moves, switches, boxes, a fight the player chose, and a stop to one that is over.
        for natural in ("MoveTo(", "EnableNoWait(", "Disable(", ".Show()", "StartCombat(", "StopCombat("):
            self.assertIn(natural, self.walk, natural)

    def test_the_side_quests_facts_are_read_and_never_written(self):
        self.assertEqual(re.findall(r"TLM_G_SQ01_\w+\.SetValue", self.road), [])
        self.assertIn("TLM_G_SQ01_YardAlerted.GetValueInt()", self.road)
        self.assertIn("TLM_G_SQ01_Outcome.GetValueInt()", self.road)

    def test_only_the_rules_script_gives_the_player_what_it_gives(self):
        for forbidden in ("AddItem", "RemoveItem"):
            self.assertNotIn(forbidden, self.walk, forbidden)
            self.assertNotIn(forbidden, self.talk, forbidden)
        self.assertEqual(sorted(set(re.findall(r"(\w+)\.AddItem\(", self.road))), ["player"])

    def test_each_fact_is_written_in_the_functions_that_own_it(self):
        bodies = {}
        for piece in self.road.split("Function ")[1:]:
            bodies[piece.split("(")[0].strip()] = piece.split("EndFunction")[0]
        owners = {
            "Outcome": ["FinishDefeat", "FinishReverse", "FinishRun", "FinishSale"],
            "MailThrough": ["FinishForward", "FinishRun"], "MailSold": ["FinishSale"], "LineClosed": ["FinishReverse"],
            "SilverRail": ["LearnSilver"], "OstranderKnown": ["LearnName"], "LockridgeStamping": ["KeepStamping"],
            "LockridgeSigned": ["FinishCountersign"], "LockridgeReported": ["FinishAuthority"], "StampDelivered": ["HandOver", "HandoverSeen"],
            "Reported": ["GiveReport"], "YardAuthority": ["FinishAuthority"],
        }
        for fact, functions in owners.items():
            where = sorted(fn for fn, body in bodies.items() if "TLM_G_MQ02A_%s.SetValueInt(" % fact in body)
            self.assertEqual(where, functions, fact)
        # Stage 100 is set in one place, and 10 in one.
        for stage, functions in ((100, ["Complete"]), (10, ["ArriveAtYard"])):
            where = sorted(fn for fn, body in bodies.items() if "SetStage(%d)" % stage in body)
            self.assertEqual(where, functions, str(stage))

    def test_every_record_of_a_scene_is_made_by_a_finish_that_looks(self):
        """Each Finish* of a scene opens by testing what it is handed against what the game now shows."""
        for fn, tests in (("FinishDepart", ("SeenAt(", "IsOn(")), ("FinishRun", ("SeenAt(", "IsOn(", "IsOff(")),
                          ("FinishReverse", ("SeenAt(", "IsOn(", "IsOff(")), ("FinishForward", ("SeenAt(", "IsOn(", "IsOff(")),
                          ("FinishCarryBack", ("SeenAt(", "IsOn(", "IsOff(")), ("FinishSale", ("IsOn(", "IsOff(", "StandsAt(")),
                          ("FinishCountersign", ("IsOn(", "IsOff(")), ("FinishAuthority", ("IsOn(", "IsOff(")),
                          ("ConfirmStampTaken", ("IsOff(",)), ("FinishDefeat", ("SeenDead(", "RifleOut(")),
                          ("FinishBillieReport", ("StandsAt(",))):
            body = self.road.split("Function " + fn + "(")[1].split("EndFunction")[0]
            for test in tests:
                self.assertIn(test, body, "%s does not look with %s" % (fn, test))


class TheTalkScript(unittest.TestCase):
    def test_it_hears_four_events_and_forwards_each(self):
        text = code(TALK)
        events = sorted(re.findall(r"^\s*Event\s+(On\w+)", text, re.M))
        self.assertEqual(events, ["OnActivate", "OnCombatStateChanged", "OnDeath", "OnTriggerEnter"])
        for forbidden in ("OnRead", "OnItemAdded", "OnItemRemoved", "OnContainerChanged", "OnHit", "OnGetUp", "OnPackageStart"):
            self.assertNotIn(forbidden, text)
        # A cancelled menu or an unseen item is not heard of: nothing here guesses at one.
        self.assertNotIn("GetItemCount", text)


class NoHelpersAndNoStatsAreTouched(unittest.TestCase):
    def test_nothing_gates_the_ordinary_character(self):
        text = "".join(code(n) for n in (ROAD, WALK, TALK))
        for word in ("SetValue(Charisma", "ModValue", "SetAV", "ModAV", "ForceAV", "DevScenario", "Scenario", "ConsoleUtil",
                     "CenterOnCell", "Debug.MessageBox", "GetValue(", "GetActorValue", "HasPerk", "GetBaseValue"):
            self.assertNotIn(word, text, word + " is in the road's scripts")


if __name__ == "__main__":
    unittest.main()
