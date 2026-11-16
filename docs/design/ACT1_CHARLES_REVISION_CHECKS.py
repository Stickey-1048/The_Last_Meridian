#!/usr/bin/env python3
"""Focused checks for the Act I writing intake after packet 2 (docs/design/ACT1_CHARLES_PACKET2_RECEIPT.md).

  python3 docs/design/ACT1_CHARLES_REVISION_CHECKS.py

Reads the three frozen packets and the story folder and says whether the folder is what they ask for.

Expected values follow the documented order of precedence: the primary packet, then the ballad
addendum for its two subjects, then packet 2 for exactly what it names. Where a later packet replaces
a value an earlier one supplied, the later value is the one expected, and the pair is printed. Every
comparison of supplied wording is exact, character for character.

One supplied line is WITHHELD and is checked as withheld: packet 2's whitcomb_rates uses a word that
no line of Act I may use. The check holds the line to its earlier text and fails if that stops being
the reason.

It also runs the histories the entry-selection contract names (Dole, Quill) through the reference
selector, and PRINTS things for a person to read.

A pass says the files agree with the packets and the contract's source rules. It is not a compile,
not a game test, and says nothing about whether the writing is good.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import check_story_intake as intake                             # noqa: E402
import story_intake_select as select                            # noqa: E402

STORY = ROOT / "assets/incoming/act1/story"
PACKET = ROOT / "docs/design/ACT1_APPROVED_TEXT_REVISIONS_2026-11-16.json"
ADDENDUM = ROOT / "docs/design/ACT1_BALLAD_ADDENDUM_2026-11-16.json"
PACKET2 = ROOT / "docs/design/ACT1_WRITING_CLOSURE_PACKET_2.json"
CONTRACT = ROOT / "docs/design/ACT1_ENTRY_SELECTION_CONTRACT.md"
HASHES = {PACKET: "364bdaa09fab8658cb99d0ff4eeffcf5db98767d465a0e427b1957ba5f4f2c5a",
          ADDENDUM: "50eeb71025b8cceac6d9d6e5f79656239406fd7a856f2343c94ee83953202cff",
          PACKET2: "f8166ead0b59050aec88a29b88be88244556cc3784c4c32189d503df0adb5a10",
          CONTRACT: "924ed1c382e13425800630c14d2cec8a002f8027996c63968478147bf5957148"}
# The one supplied line that is not applied, the text the line keeps (as at 975a262), and the word that bars it.
WITHHELD = {"whitcomb_rates": ("The carriers do, by vote, one wagon one voice. Nell Fenwick yonder voted against me twice and for me once, "
                               "and I count that a landslide. It's slow. It's loud. Nobody gets shot for losing.", "charter")}
GANTT_SHA256 = "22c5531d1776772e1e91a49604781c0871d0ec057c8f6ee368ba85f9fcc527ee"
OLD_SURNAMES = ["Tarrow", "Greer", "Pruitt", "Vickers"]
RETIRED_WORDS = ["Dessie", "Tansley", "H.G.", "talbot_shot", "ninety-eight", "'98"]
RETIRED_LABELS = ["You hanged the wrong man in ninety-eight.", "Fire your charges, Captain.", "Light the boiler and get clear.", "Send your deputy.",
                  "(Step aside)", "I can't swear for a whole town.", "(Stand between the rifles and the crowd)", "(Go after the shooter)",
                  "He tipped his hat to me.", "Set a line here. Both sides swear to it.", "Then I swear it. A line, here."]
CUES = ["familiar", "memory", "recall", "remember", "know you", "knew you", "taught you", "tipped his hat", "walked away from",
        "whoever", "who we think", "always going to", "survivor", "passenger", "how interesting", "isn't that a mercy"]
CONTINUE = "Continue"

failed, notes, succession = [], [], []


def bad(msg):
    failed.append(msg)


class Expected(dict):
    """What a node should hold, by the last packet to name it. Each replacement of an earlier packet's value is noted."""

    def supply(self, key, value, source):
        if key in self and self[key][0] != value:
            succession.append((key, self[key][1], source))
        self[key] = (value, source)


def lf(path):
    return path.read_bytes().replace(b"\r\n", b"\n")


def main():
    global notes
    for path, want in HASHES.items():
        got = hashlib.sha256(lf(path)).hexdigest()
        if got != want:
            bad("%s: SHA-256 is %s, not %s" % (path.name, got, want))
    pk, ad, p2 = (json.loads(lf(p)) for p in (PACKET, ADDENDUM, PACKET2))
    c2 = p2["quest_and_evidence_contracts"]
    files = intake.read_folder(STORY)
    chars = {c["id"]: c for c in json.loads(files["characters.json"])["characters"]}
    docs = {d["id"]: d for d in json.loads(files["documents.json"])["documents"]}
    quests = {json.loads(t)["key"]: json.loads(t) for p, t in sorted(files.items()) if p.startswith("quests/")}
    talk = {p: json.loads(t) for p, t in sorted(files.items()) if p.startswith("talk/")}
    lines = {l["id"]: l for t in talk.values() for l in t["lines"]}
    where = {l["id"]: p for p, t in talk.items() for l in t["lines"]}

    # ---- 0. the folder itself: the strict check, in the second talk format
    for p in intake.Intake(files, strict=True).run():
        bad("strict intake: " + p)
    for path, t in talk.items():
        if t["format"] != intake.TALK_V2:
            bad("%s is %s, not tlm-talk-2" % (path, t["format"]))

    # ---- 1. spoken text: primary packet, then the addendum's flint_who, then packet 2
    text = Expected()
    for r in pk["talk_text_replacements"]:
        text.supply(r["id"], r["text"], "primary packet")
    text.supply("quill_shamed", pk["pritchard_quill_history"]["quill_response"], "primary packet")
    text.supply("roark_after_fire", pk["conditional_roark_lines"]["ordered_charges"], "primary packet")
    text.supply("roark_after_deadline", pk["conditional_roark_lines"]["warned_deadline_abandoned"], "primary packet")
    text.supply(ad["flint_who_override"]["id"], ad["flint_who_override"]["text"], "addendum")
    for r in p2["talk_replacements"]:
        if "text" not in r:
            continue
        if r["id"] in WITHHELD:
            kept, word = WITHHELD[r["id"]]
            if not intake.names(word, r["text"]):
                bad("%s is withheld for the word %r, which packet 2's text no longer has: apply it and remove the exception" % (r["id"], word))
            text.supply(r["id"], kept, "kept as at 975a262: packet 2's text is WITHHELD")
        else:
            text.supply(r["id"], r["text"], "packet 2")
        if where.get(r["id"]) != r["file"]:
            bad("%s is not in %s" % (r["id"], r["file"]))
    new = {x["id"]: x for x in p2["new_talk_lines"]}
    copies = {"belden_greenwater_relief_fire": "belden_greenwater_relief", "whitcomb_truce_talbot": "whitcomb_truce", "belden_truce_talbot": "belden_truce",
              "grey_truce_talbot": "grey_truce", "brigg_demand_talbot": "brigg_demand", "brigg_demand_no_whitcomb": "brigg_demand",
              "brigg_demand_no_belden": "brigg_demand", "brigg_demand_no_grey": "brigg_demand", "brigg_demand_no_officer": "brigg_demand"}
    for lid, x in new.items():
        text.supply(lid, x["text"], "packet 2")
        if lid in lines and (lines[lid]["speaker"] != x["speaker"] or where[lid] != x["file"]):
            bad("%s has the wrong speaker or file" % lid)
    for lid, of in copies.items():
        text.supply(lid, new[of]["text"], "packet 2 (a context copy of %s)" % of)
        if lid in lines and lines[lid]["speaker"] != new[of]["speaker"]:
            bad("%s has the wrong speaker" % lid)
    for r in c2["after_fair_reports"]:
        text.supply(r["id"], r["known_text"], "packet 2")
        text.supply(r["id"] + "_unknown", r["unknown_text"], "packet 2")
    menus = sorted(l for l in lines if l.startswith("pritchard_report_menu_"))
    for lid in menus:
        text.supply(lid, c2["after_fair_report_menu"]["text"], "packet 2")
    for lid, (want, source) in sorted(text.items()):
        if lid not in lines:
            bad("line %s is missing (%s)" % (lid, source))
        elif lines[lid]["text"] != want:
            bad("line %s does not carry the text expected of it (%s)" % (lid, source))

    # ---- 2. buttons: every replacement made, every retired label gone, every supplied label there
    labels = [b["label"] for l in lines.values() for b in l.get("buttons", [])]
    swaps = [(r["id"], r[k]["from"], r[k]["to"]) for r in pk["talk_text_replacements"] for k in ("incoming_button_change", "button_change") if k in r]
    swaps += [(r["id"], b["from"], b["to"]) for r in p2["talk_replacements"] for b in r.get("button_replacements", [])]
    for lid, old, to in swaps:
        if old in labels:
            bad("old button still there: %s" % old)
        if to not in labels:
            bad("new button missing: %s" % to)
    for old in RETIRED_LABELS:
        if old in labels or any(old in json.dumps(q) for q in quests.values()):
            bad("retired button or label still present: %s" % old)
    for lid, x in new.items():
        for b in x.get("buttons", []):
            mine = [y for y in lines[lid].get("buttons", []) if y["label"] == b["label"]]
            if len(mine) != 1 or mine[0].get("do") != b.get("do") or ("then" in b and mine[0].get("then") != b["then"]):
                bad("%s: the supplied button %r is not there as supplied" % (lid, b["label"]))
    for lid, label, target in (("pritchard_road_pike", "What should I ask Quill?", "pritchard_docket_context"), ("belden_offer", "Who argues against your office?", "belden_dissent"),
                               ("brigg_offer", "Do all your Wardens agree?", "brigg_dissent"), ("grey_offer", "Do your engineers agree?", "grey_dissent")):
        if not [b for b in lines[lid]["buttons"] if b["label"] == label and b.get("then") == target and not b.get("do")]:
            bad("%s lacks the supplied button %r leading to %s" % (lid, label, target))
    for lid in menus:
        if [b["label"] for b in lines[lid]["buttons"]] != c2["after_fair_report_menu"]["buttons"]:
            bad("%s does not have the supplied four buttons" % lid)
    # the only label not supplied by a packet or already in the folder is the builder's own word
    made = sorted({(lid, b["label"]) for lid, l in lines.items() for b in l.get("buttons", []) if b["label"] == CONTINUE})
    notes.append("\nButtons labelled %r, the builder's own word, added because a line with one way on needs a button to carry it (%d):" % (CONTINUE, len(made)))
    notes += ["  " + lid for lid, _ in made]

    # ---- 3. removed nodes and stages stay removed; nothing is renumbered
    for lid in pk["remove_fair_dialogue_nodes"] + ["pritchard_talbot_back", "talbot_sent", "keene_talbot_aside", "quill_unmoved", "pritchard_quill_aside"]:
        if lid in lines:
            bad("line %s should not be there" % lid)
    everything = "\n".join(files[p] for p in sorted(files) if p.endswith(".json"))
    for ref in ("mq03 set 30", "mq03 done 30", "mq03 notdone 30", "mq02 set 70", "mq02 done 70", "mq02 notdone 70"):
        if ref in everything:
            bad("reference to a removed stage: %s" % ref)
    stages = {k: [s["n"] for s in q["stages"]] for k, q in quests.items()}
    want_stages = {"mq02": [10, 20, 30, 40, 50, 60, 100], "mq03": [10, 20, 21, 22, 40, 41, 42, 43, 44, 50, 60, 70, 100],
                   "mq02c": [10, 11, 12, 13, 14, 15, 16, 20, 30, 40, 45, 50, 51, 52, 53, 56, 54, 60, 100]}
    for k, want in want_stages.items():
        if stages[k] != want:
            bad("%s stages are %s, not %s" % (k, stages[k], want))

    # ---- 4. character notes: primary packet, then packet 2 (a tie or a list entry named by its key)
    field = Expected()
    for r in pk["character_field_replacements"]:
        field.supply((r["id"], r["field"]), r["value"], "primary packet")
    field.supply(("pike", "secret"), pk["pike_ammunition_tooling"]["replacement_secret"], "primary packet")
    for r in p2["character_replacements"]:
        field.supply((r["id"], r["field"]), r["value"], "packet 2")
    for (cid, name), (want, source) in sorted(field.items()):
        m = re.match(r"^(\w+)\[(\w+)\]$", name)
        if not m:
            got = chars[cid][name]
        elif m.group(1) == "ties":
            got = [t["what"] for t in chars[cid]["ties"] if t["to"] == m.group(2)]
            got = got[0] if len(got) == 1 else got
        else:
            got = chars[cid][m.group(1)][int(m.group(2))]
        if got != want:
            bad("characters.json %s.%s is not the value expected (%s)" % (cid, name, source))
    names = {"tarrow": "Wilhelmina Tupper", "greer": "Hobart Blevins", "pruitt": "Mose Rafferty", "vickers": "Temperance Beckett",
             "dole": "Ezekiel Dole", "lockridge": "Augusta Lockridge", "starnes": "Opal Starnes", "hatcher": "Lyle Hatcher",
             "roark": "Dinah Roark", "threefords": "Juno Three-Fords", "granger": "Tolly Granger"}
    for cid, name in names.items():
        if chars[cid]["name"] != name:
            bad("characters.json %s is named %s, not %s" % (cid, chars[cid]["name"], name))
    for cid, name, gone in (("flint", "does_not_know", "Whether the stranger is on his side or hers"),
                            ("quill", "does_not_know", "That the stranger at her wagon is the one the Cutters were waiting for")):
        if gone in chars[cid][name]:
            bad("characters.json %s.%s: an entry packet 2 keeps deleted is back" % (cid, name))
    for word in OLD_SURNAMES + RETIRED_WORDS:
        for p in sorted(files):
            if p.endswith(".json") and word in files[p]:
                bad("%s still contains %r" % (p, word))

    # ---- 5. quest wording: primary packet contracts, then packet 2's journals and contracts
    q1 = pk["quest_text_contracts"]
    def stage(key, n): return [s for s in quests[key]["stages"] if s["n"] == n][0]
    def flag(key, name): return [f for f in quests[key]["new_flags"] if f["name"] == name][0]["meaning"]
    def option(key, at, label): return ([o for c in quests[key]["choices"] if c["at"] == at for o in c["options"] if o["label"] == label] or [{}])[0]
    quest = Expected()
    quest.supply("mq02c stage 15 log", q1["mq02c_stage15_log"], "primary packet")
    quest.supply("mq02c stage 51 log", q1["mq02c_stage51_log"], "primary packet")
    quest.supply("mq03 stage 41 log", q1["mq03_stage41_log"], "primary packet")
    for x in p2["journal_replacements"]:
        quest.supply("%s stage %d log" % (x["quest"], x["stage"]), x["log"], "packet 2")
    for key, (want, source) in sorted(quest.items()):
        k, _, n, _ = key.split()
        if stage(k, int(n))["log"] != want:
            bad("%s is not the wording expected (%s)" % (key, source))
    b, v, gf = c2["brigg_choice"], c2["vane_lynching"], {x["target"]: x["text"] for x in c2["grain_fidelity"]}
    exact = [
        ("mq02c stage 16 set_by", stage("mq02c", 16)["set_by"], [x for x in p2["journal_replacements"] if x["stage"] == 16][0]["set_by"]),
        ("mq03 stage 43 set_by", stage("mq03", 43)["set_by"], b["stage43_set_by"]),
        ("mq04 stage 64 set_by", stage("mq04", 64)["set_by"], v["stage64_set_by"]),
        ("mq02c flag hollow_line", flag("mq02c", "hollow_line"), q1["mq02c_hollow_line_flag"]),
        ("mq02b flag queen_burned", flag("mq02b", "queen_burned"), q1["mq02b_queen_burned_flag"]),
        ("mq03 flag saw_the_shooter", flag("mq03", "saw_the_shooter"), q1["mq03_saw_the_shooter_flag"]),
        ("mq03 flag crowd_spared", flag("mq03", "crowd_spared"), b["crowd_spared_meaning"]),
        ("mq02c flag docket_2298_held", flag("mq02c", "docket_2298_held"), c2["docket"]["flag_meaning"]),
        ("mq03 premise", quests["mq03"]["premise"], q1["mq03_premise"]),
        ("mq03 search choice now", option("mq03", 40, q1["mq03_choice41_label"]).get("now"), q1["mq03_choice41_now"]),
        ("mq03 search choice later", option("mq03", 40, q1["mq03_choice41_label"]).get("later"), q1["mq03_choice41_later"]),
        ("mq03 truce choice now", option("mq03", 40, b["label"]).get("now"), b["now"]),
        ("mq03 truce choice later", option("mq03", 40, b["label"]).get("later"), b["later"]),
        ("mq03 truce choice sets nothing by itself: stage 43 is Brigg's concession", option("mq03", 40, b["label"]).get("sets"), None),
        ("mq02b choice 42 now", option("mq02b", 40, "Cut the barge loose.").get("now"), gf["mq02b choices at40 option42 now"]),
        ("mq02b choice 43 now", option("mq02b", 40, q1["mq02b_fire_button"]).get("now"), gf["mq02b choices at40 option43 now"]),
        ("mq02b choice 43 later", option("mq02b", 40, q1["mq02b_fire_button"]).get("later"), gf["mq02b choices at40 option43 later"]),
        ("mq02b choice 44 later", option("mq02b", 40, "Sell me a share, Commodore.").get("later"), gf["mq02b choices at40 option44 later"]),
        ("mq02b choice 60 later", option("mq02b", 41, "He's yours, Opal.").get("later"), gf["mq02b choices at41 option60 later"]),
        ("mq04 hanging choice", option("mq04", 50, v["label"]).get("sets"), 64),
        ("mq02c seal choice", option("mq02c", 50, q1["mq02c_fire_button"]).get("sets"), 53),
    ]
    for what, got, want in exact:
        if got != want:
            bad("%s is not the supplied value" % what)
    ev = [e for e in quests["mq02c"]["evidence"] if e["id"] == "docket_2298"][0]
    if ev["found"] != c2["docket"]["found"] or ev["sets"] != 16:
        bad("mq02c evidence docket_2298 is not the supplied contract")
    contains = [("mq02", "cannot_break", q1["mq02"]), ("mq03", "cannot_break", q1["mq03_shot_and_occupation_rule"]), ("mq03", "cannot_break", c2["brigg_failure_rule"]),
                ("mq04", "cannot_break", v["cannot_break_delta"])]
    for key, name, want in contains:                      # a supplied rule set whole inside a longer field: it must be there entire
        if want not in quests[key][name]:
            bad("%s %s does not carry a supplied rule whole: %s..." % (key, name, want[:50]))
    if c2["mine_warning"] not in stage("mq02c", 30)["set_by"]:
        bad("mq02c stage 30 set_by does not carry the supplied warning rule whole")
    for gone in ("the town hangs Vane", "with or without cutting the barge free first", "saved only if it was cut free first"):
        if gone in json.dumps(quests):
            bad("a claim packet 2 removes is still in a quest file: %s" % gone)

    # ---- 6. papers: the ballads whole, the docket, Gantt's two paragraphs
    var = ad["variants"]
    want_docs = {"ballad_six_rounds": var["saved"]["full_text"], "ballad_six_rounds_evaded_or_missed": var["evaded_or_missed"]["full_text"],
                 "ballad_six_rounds_exploited": var["exploited"]["full_text"], "ballad_six_rounds_unconfirmed": ad["common_body"],
                 "ballad_six_rounds_betrayal": p2["betrayal_ballad"]["text"]}
    for did, want in want_docs.items():
        if did not in docs or docs[did]["text"] != want or docs[did]["title"] != ad["target"]["title"]:
            bad("document %s is not the supplied sheet" % did)
    bb = p2["betrayal_ballad"]
    if any(docs[bb["id"]][k] != bb[k] for k in ("kind", "title", "found", "text")):
        bad("the betrayal sheet is not as supplied")
    if "method is deal" not in docs["ballad_six_rounds_exploited"]["found"]:
        bad("the trading sheet is not restricted to a deal")
    a = p2["document_additions"][0]
    if any(docs.get(a["id"], {}).get(k) != a[k] for k in ("kind", "title", "found", "text", "sources")):
        bad("the 2298 review copy is not as supplied")
    g = docs["gantt_dispatch"]["text"]
    for r in p2["document_paragraph_replacements"]:
        if r["from"] in g or g.count(r["to"]) != 1:
            bad("gantt_dispatch: a supplied paragraph replacement is not made")
    if hashlib.sha256(g.encode()).hexdigest() != GANTT_SHA256:
        bad("gantt_dispatch is not the whole text expected after the two replacements")
    for did, d in docs.items():
        if re.search(r"six rounds|five came back", d["text"], re.I):
            bad("document %s still carries the old fixed-ammunition ballad" % did)

    # ---- 7. routing by what actually happened on the Tellico road
    cries = {"granger_ballad_saved": ["outcome is saved"], "granger_ballad_walked": ["outcome is evaded"], "granger_ballad_missed": ["outcome is missed"],
             "granger_ballad_deal": ["outcome is exploited", "method is deal"], "granger_ballad_betrayal": ["outcome is exploited", "method is betrayal"]}
    for lid, want in cries.items():
        if lid not in lines or lines[lid]["when"] != want or lines[lid].get("kind") != "aside":
            bad("%s is not an aside bound to %s" % (lid, want))

    # ---- 8. evidence: what was learned, against what is in hand
    def sets(lid): return [e for b in lines[lid].get("buttons", []) for o in ([b["pass"], b["fail"]] if "check" in b else [b]) for e in o.get("do", [])]
    def when(lid): return lines[lid]["when"]
    def setters(effect): return sorted(lid for lid in lines if effect in sets(lid))
    for road, fl, claim in (("rail", "silver_rail", "Silver. With a square stamped on it."), ("river", "silver_river", "He was paid to hold it. In silver."),
                            ("pike", "silver_mine", "He was paid to. In silver.")):
        known, unknown = "pritchard_hears_" + road, "pritchard_hears_%s_unknown" % road
        if "flag " + fl not in when(known) or "notflag " + fl not in when(unknown):
            bad("the %s report is not split on %s" % (road, fl))
        if claim not in [x["label"] for x in lines[known]["buttons"]] or claim in [x["label"] for x in lines[unknown]["buttons"]]:
            bad("the %s report offers the payment claim where the evidence was not learned, or withholds it where it was" % road)
        if lines[known]["text"] != lines[unknown]["text"] or [w for w in when(known) if "flag" not in w] != [w for w in when(unknown) if "flag" not in w]:
            bad("the two %s reports differ in more than the evidence" % road)
        for kind in ("", "_unknown"):
            leaf = "pritchard_hears_%s_after_fair%s" % (road, kind)
            if (("notflag " if kind else "flag ") + fl) not in when(leaf):
                bad("%s is not guarded by the evidence it speaks of" % leaf)
    for lid in menus:
        k = dict(zip(("rail", "river", "pike"), lid[-3:]))
        for (road, fl), btn in zip((("rail", "silver_rail"), ("river", "silver_river"), ("pike", "silver_mine")), lines[lid]["buttons"]):
            want_when = ("flag " if k[road] == "k" else "notflag ") + fl
            want_then = "pritchard_hears_%s_after_fair%s" % (road, "" if k[road] == "k" else "_unknown")
            if want_when not in when(lid) or btn.get("then") != want_then or btn.get("do"):
                bad("%s routes the %s report wrongly, or does something besides" % (lid, road))
    if len(menus) != 8:
        bad("there are %d report menus, not eight" % len(menus))
    # the docket: only the flag means it is in hand. Having once taken it (stage 16) is not enough, and nothing here pretends to set the flag.
    if "flag docket_2298_held" not in when("quill_court_docket") or "mq02c set 13" not in sets("quill_court_docket") or "mq02c set 13" in sets("quill_court"):
        bad("the 2298 challenge is not gated on holding the review copy")
    if any("mq02c done 16" in when(lid) for lid in lines):
        bad("a line treats having once taken the review copy (stage 16) as still holding it")
    if setters("mq02c set 13") != ["quill_court_docket"] or setters("mq02c set 16") != ["pritchard_docket_context"]:
        bad("stage 13 or stage 16 of mq02c is set somewhere it should not be")
    if [f for f in ("silver_rail", "silver_river", "silver_mine", "silver_road") if "held" in flag({"silver_rail": "mq02a", "silver_river": "mq02b"}.get(f, "mq02c"), f)]:
        bad("a silver flag is described as something carried; it is something learned")
    if any("check" in x for x in lines["quill_court"]["buttons"] + lines["quill_court_docket"]["buttons"]):
        bad("the 2298 challenge is still a speech check")

    # ---- 9. the mine, the boat, the porch: nothing dark happens by default
    if sets("roark_mouth") or setters("mq02c set 30") != ["roark_deadline_warning"]:
        bad("stage 30 of mq02c is armed by something other than the accepted warning")
    if [x.get("then") for x in lines["roark_mouth"]["buttons"]][0] != "roark_deadline_warning":
        bad("the rescue does not pass through the warning")
    if "mq02c set 53" in sets("greer_first") or setters("mq02c set 53") != ["greer_first_heard"] or "mq02c done 30" not in when("greer_first_heard"):
        bad("the seal order is not gated on the accepted warning")
    if when("roark_after_fire") != ["mq02c done 53"] or when("roark_after_deadline") != ["mq02c done 56"]:
        bad("Roark's two aftermath lines are not bound to their two distinct facts")
    for effect in ("mq02c set 56", "mq03 set 70", "mq04 set 50"):
        if setters(effect):
            bad("a button sets %s; only the event itself may" % effect.split()[-1])
    if "living, functional Blevins" not in stage("mq02c", 56)["set_by"]:
        bad("stage 56 does not require a living Captain")
    if setters("mq02b set 42") != ["pruitt_chain"] or setters("mq02b set 43") != ["pruitt_chain"] or {"mq02b set 42", "mq02b set 43"} <= set(
            e for x in lines["pruitt_chain"]["buttons"] for e in x.get("do", []) if len(x.get("do", [])) > 1):
        bad("the Chute escape and the fire are not two separate choices")
    if when("starnes_after_chute") != ["mq02b done 42"] or when("starnes_after_fire") != ["mq02b done 43"]:
        bad("Starnes's replies to the escape and to the fire are not bound to their own facts")
    if "alive hatcher" not in when("starnes_after_won") or "dead hatcher" not in when("starnes_won_hatcher_dead") or lines["starnes_won_hatcher_dead"].get("buttons"):
        bad("Hatcher can be handed over dead, or not when alive")
    if "alive nell" not in when("nell_soup_aside"):
        bad("Nell's aside can be said by the dead")
    for lid in ("belden_greenwater_relief", "belden_greenwater_relief_fire"):
        if "alive belden" not in when(lid) or sets(lid):
            bad("%s is not a living Belden's offer with no effect" % lid)
    if when("belden_greenwater_relief")[0] != "mq02b done 44" or when("belden_greenwater_relief_fire")[0] != "mq02b done 43":
        bad("Belden's wagon is not bound to the sale and to the fire separately")
    hang = [x for x in lines["vane_porch"]["buttons"] if x["label"] == v["label"]]
    if setters("mq04 set 64") != ["vane_porch"] or len(hang) != 1 or hang[0].get("do") != ["mq04 set 64"]:
        bad("the hanging is set by something other than the one explicit button on the porch")

    # ---- 10. the fair: Brigg's order is read first; the truce is spoken by the living; a request is not a concession
    demands = sorted(l for l in lines if l.startswith("brigg_demand"))
    truce = c2["brigg_choice"]["label"]
    for lid in demands:
        if "alive brigg" not in when(lid) or "mq03 done 40" not in when(lid) or "mq03 notdone 70" not in when(lid):
            bad("%s can be said by a dead Brigg, before the shot or after the occupation" % lid)
        t = [x for x in lines[lid]["buttons"] if x["label"] == truce]
        if t and t[0].get("do"):
            bad("%s: asking for the truce sets a stage. Only Brigg's concession may" % lid)
        if [x["label"] for x in lines[lid]["buttons"] if x["label"] != truce] != ["(Search the roof and landing)", "(Stay with the courier)", "(Take the case and go)"]:
            bad("%s does not keep the other three courses" % lid)
    people = ("whitcomb", "belden", "grey", "pritchard", "talbot")
    def says(lid, who): return "alive " + who in when(lid), "dead " + who in when(lid)
    for i, a_ in enumerate(demands):
        for b_ in demands[i + 1:]:
            if not any((says(a_, p)[0] and says(b_, p)[1]) or (says(a_, p)[1] and says(b_, p)[0]) for p in people):
                bad("%s and %s could both hold" % (a_, b_))
    for lid, order in (("brigg_demand", ["whitcomb_truce", "belden_truce", "grey_truce", "pritchard_truce"]),
                       ("brigg_demand_talbot", ["whitcomb_truce_talbot", "belden_truce_talbot", "grey_truce_talbot", "talbot_truce"])):
        t = [x for x in lines[lid]["buttons"] if x["label"] == truce]
        chain, at = [], (t[0].get("then") if t else None)
        while at and at != "brigg_rifles":
            chain.append(at)
            speaker = lines[at]["speaker"]
            if "alive " + speaker not in when(at) or "alive " + speaker not in when(lid):
                bad("%s can be said by the dead, or is promised by an order that does not ask whether its speaker lives" % at)
            nxt = lines[at]["buttons"]
            if len(nxt) != 1 or nxt[0]["label"] != CONTINUE:
                bad("%s does not lead on by one plain button" % at)
            if nxt[0].get("do") and nxt[0].get("then") != "brigg_rifles":
                bad("%s sets a stage before Brigg has answered" % at)
            at = nxt[0].get("then")
        if chain != order:
            bad("the truce from %s is spoken as %s, not %s" % (lid, chain, order))
        if lines[order[-1]]["buttons"][0].get("do") != ["mq03 set 43"]:
            bad("stage 43 is not set at Brigg's answer")
    for lid in demands:
        if lid not in ("brigg_demand", "brigg_demand_talbot") and truce in [x["label"] for x in lines[lid]["buttons"]]:
            bad("%s offers a truce that someone dead would have to speak" % lid)
    if setters("mq03 set 43") != ["pritchard_truce", "talbot_truce"] or when("brigg_rifles") != ["mq03 done 43"]:
        bad("Brigg's concession is not what sets stage 43, or his reply can be said without it")

    # ---- 11. the entry contract, on this folder: labels, and the histories it names
    for lid in ("tarrow_in_cut", "dole_sermon", "tarrow_ran", "tarrow_backed", "hatcher_table"):
        if lines[lid].get("entry") is not True or not when(lid):
            bad("%s is no longer a guarded greeting" % lid)
    for lid in ("dole_name", "dole_silver", "dole_share", "dole_face", "quill_fine", "quill_shamed"):
        if lines[lid].get("entry") is not False:
            bad("%s is not a continuation" % lid)
    if "mq02a done 55" in when("dole_name") or when("quill_shamed") != ["mq02c done 13"]:
        bad("dole_name is guarded by what it reveals, or quill_shamed is not guarded by the hearing")
    try:
        s = select.Selector(files)
    except ValueError as e:
        s = None
        bad("the reference selector will not take the folder, so no history was run: %s" % e)
    histories = []
    if s is not None:
        S = select.State
        def greet(who, **kw): return s.greet(who, S(**kw)).line
        histories = [
            ("Dole, share taken, name never learned: he does not open with the name", greet("dole", stages={"mq02a": {10, 20, 30, 40, 43}}), "dole_default"),
            ("Dole in the Cut, nothing settled", greet("dole", stages={"mq02a": {10, 20, 30, 40}}), "dole_sermon"),
            ("Quill, fine paid, no docket, no hearing", greet("quill", stages={"mq02c": {10, 12}}), "quill_default"),
            ("Quill, docket in hand", greet("quill", stages={"mq02c": {10}}, flags={"docket_2298_held"}), "quill_court_docket"),
            ("Quill, copy once taken but not in hand", greet("quill", stages={"mq02c": {10, 16}}), "quill_court"),
            ("Quill, after the hearing", greet("quill", stages={"mq02c": {10, 13}}, flags={"docket_2298_held"}), "quill_default"),
            ("Pritchard after a refusal, all roads open", greet("pritchard", stages={"mq01": {100}, "mq02": {50, 100}}), "pritchard_three_tokens_later"),
            ("Pritchard after the fair, rail done", greet("pritchard", stages={"mq01": {100}, "mq02": {10, 20, 60, 100}}), "pritchard_three_tokens_later_river_pike"),
            ("Pritchard after the fair, every road done, nothing learned", greet("pritchard", stages={"mq01": {100}, "mq02": {10, 20, 30, 40, 60, 100}}), "pritchard_report_menu_uuu"),
            ("Pritchard before the fair, rail done, silver learned", greet("pritchard", stages={"mq01": {100}, "mq02": {10, 20}}, flags={"silver_rail"}), "pritchard_hears_rail"),
            ("Pritchard before the fair, rail done, silver not learned", greet("pritchard", stages={"mq01": {100}, "mq02": {10, 20}}), "pritchard_hears_rail_unknown"),
            ("Brigg after the shot, everyone alive", greet("brigg", stages={"mq03": {10, 40}}), "brigg_demand"),
            ("Brigg after the shot, Pritchard dead", greet("brigg", stages={"mq03": {10, 40}}, dead={"pritchard"}), "brigg_demand_talbot"),
            ("Brigg after the shot, Grey dead", greet("brigg", stages={"mq03": {10, 40}}, dead={"grey"}), "brigg_demand_no_grey"),
            ("Brigg after conceding", greet("brigg", stages={"mq03": {10, 40, 43}}), "brigg_rifles"),
            ("Starnes, barge won, Hatcher alive", greet("starnes", stages={"mq02b": {10, 20, 30, 40, 41}}), "starnes_after_won"),
            ("Starnes, barge won, Hatcher dead", greet("starnes", stages={"mq02b": {10, 20, 30, 40, 41}}, dead={"hatcher"}), "starnes_won_hatcher_dead"),
            ("Dunmore on the rope, never met", greet("dunmore", stages={"mq02c": {10}}, words={"outcome": "missed"}), "dunmore_rope_missed"),
            ("Dunmore on the rope, met", greet("dunmore", stages={"mq02c": {10}}, words={"outcome": "saved"}), "dunmore_rope"),
        ]
        for what, got, want in histories:
            if got != want:
                bad("history: %s: said %s, not %s" % (what, got, want))
        st = S(stages={"mq02a": {10, 20, 30, 40}})
        r1 = s.press("dole_sermon", 2, st)
        r2 = s.press("dole_name", 0, st)
        if (r1.line, r1.effects, r2.line, r2.effects) != ("dole_name", [], "dole_silver", ["mq02a set 55"]):
            bad("history: the earned reveal of Dole's name does not run as the contract says")
        st = S(stages={"mq02c": {10}}, flags={"docket_2298_held"})
        r = s.press("quill_court_docket", 1, st)
        if (r.line, r.effects) != ("quill_shamed", ["mq02c set 13"]):
            bad("history: the hearing does not run as the contract says")
        st = S(stages={"mq03": {10, 40}})
        said = ["brigg_demand"]
        r = s.press("brigg_demand", 2, st)
        while r.line:
            said.append(r.line)
            if r.line == "brigg_rifles":
                break
            r = s.press(r.line, 0, st)
        if said != ["brigg_demand", "whitcomb_truce", "belden_truce", "grey_truce", "pritchard_truce", "brigg_rifles"] or not st.done("mq03", 43):
            bad("history: the truce is not spoken through to Brigg's answer: %s" % said)
        st = S(stages={"mq03": {10, 40}})
        s.press("brigg_demand", 2, st)
        if st.done("mq03", 43):
            bad("history: asking for the truce is taken for Brigg's concession")

    # ---- for a person to read
    notes.append("\nValues that a later packet replaced (the later one is expected):")
    notes += ["  %-40s %s -> %s" % (str(k), a_, b_) for k, a_, b_ in succession]
    notes.append("\nWITHHELD: " + ", ".join("%s (packet 2's text says %r)" % (k, w) for k, (_, w) in WITHHELD.items()))
    notes.append("\nWhere the inspector's legal name is written (each must be at or after the reveal):")
    for at, body in player_facing(quests, lines, docs):
        if re.search(r"Ostrander|Reuben", body):
            notes.append("  %s" % at)
    notes.append("\nPossible recognition or foreknowledge cues in player-facing text or character notes (read each):")
    for at, body in player_facing(quests, lines, docs) + [("characters.json %s.%s" % (c["id"], f), json.dumps(c[f])) for c in chars.values() for f in c if f not in ("id", "record", "name", "status", "sex", "age", "sources")]:
        for cue in CUES:
            if cue in body.lower():
                notes.append("  %-45s %r" % (at, cue))
    used = set(re.findall(r"(?:not)?flag ([a-z0-9_]+)", json.dumps([[l["when"] for l in t["lines"]] for t in talk.values()]) + json.dumps([x["reads"] for x in quests.values()])))
    notes.append("\nFlags declared and never read by a condition in this folder:")
    notes += ["  %s: %s" % (k, f["name"]) for k, x in quests.items() for f in x["new_flags"] if f["name"] not in used]
    notes.append("\nFlags a condition reads. NOTHING in this format sets a flag; each needs a mapping in the game:")
    notes += ["  " + f for f in sorted(used)]

    print("\n".join(notes))
    print()
    if failed:
        print("REVISION CHECKS FAILED (%d):" % len(failed))
        for f in failed:
            print("  " + f)
        return 1
    boxed = [l for l in lines.values() if l.get("kind") != "aside"]
    print("revision checks: the story folder agrees with the three packets and the entry contract's source rules")
    print("  %d lines (%d entries, %d continuations, %d asides), %d documents, %d characters, %d quests; %d histories run through the reference selector"
          % (len(lines), sum(1 for l in boxed if l["entry"]), sum(1 for l in boxed if not l["entry"]), len(lines) - len(boxed), len(docs), len(chars), len(quests), len(histories) + 4))
    print("This is agreement of source files with source documents. It is not a compile and not a game test.")
    return 0


def player_facing(quests, lines, docs):
    out = []
    for key, x in quests.items():
        out += [("quest %s stage %s log" % (key, s["n"]), s["log"]) for s in x["stages"] if s["log"]]
        out += [("quest %s objective %s" % (key, o["n"]), o["text"]) for o in x["objectives"]]
        out += [("quest %s choice label" % key, o["label"]) for c in x["choices"] for o in c["options"]]
    for lid, l in lines.items():
        out.append(("talk %s" % lid, l["text"]))
        out += [("talk %s button" % lid, b["label"]) for b in l.get("buttons", [])]
    out += [("document %s" % did, d["title"] + "\n" + d["text"]) for did, d in docs.items()]
    return out


if __name__ == "__main__":
    sys.exit(main())
