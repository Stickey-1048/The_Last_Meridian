#!/usr/bin/env python3
"""Focused checks for the Act I writing-intake revision (docs/design/ACT1_CHARLES_REVISION_RECEIPT.md).

  python3 docs/design/ACT1_CHARLES_REVISION_CHECKS.py

Reads the two frozen packets and the story folder and says whether the revision did what the packets
ask: supplied wording applied exactly, removed nodes gone, names propagated, no reference left to what
was removed, ballads routed by the recorded outcome. It also PRINTS things for a person to read:
where the inspector's legal name appears, words that could be a recognition cue, and lines whose
conditions tie.

It is a review aid. A pass says the files agree with the packets. It is not the strict intake check
(tools/check_story_intake.py), not a compile and not a game test, and it says nothing about whether
the writing is good.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STORY = ROOT / "assets/incoming/act1/story"
PACKET = ROOT / "docs/design/ACT1_APPROVED_TEXT_REVISIONS_2026-11-16.json"
ADDENDUM = ROOT / "docs/design/ACT1_BALLAD_ADDENDUM_2026-11-16.json"
HASHES = {PACKET: "364bdaa09fab8658cb99d0ff4eeffcf5db98767d465a0e427b1957ba5f4f2c5a",
          ADDENDUM: "50eeb71025b8cceac6d9d6e5f79656239406fd7a856f2343c94ee83953202cff"}
OLD_SURNAMES = ["Tarrow", "Greer", "Pruitt", "Vickers"]
RETIRED_WORDS = ["Dessie", "Tansley", "H.G.", "talbot_shot", "ninety-eight", "'98"]
CUES = ["familiar", "memory", "recall", "remember", "know you", "knew you", "taught you", "tipped his hat", "walked away from",
        "whoever", "who we think", "always going to", "survivor", "passenger", "how interesting", "isn't that a mercy"]

failed, notes = [], []


def bad(msg):
    failed.append(msg)


def main():
    for path, want in HASHES.items():
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        if got != want:
            bad("%s: SHA-256 is %s, not %s" % (path.name, got, want))
    pk, ad = json.loads(PACKET.read_text()), json.loads(ADDENDUM.read_text())
    chars = {c["id"]: c for c in json.loads((STORY / "characters.json").read_text())["characters"]}
    docs = {d["id"]: d for d in json.loads((STORY / "documents.json").read_text())["documents"]}
    quests = {json.loads(p.read_text())["key"]: json.loads(p.read_text()) for p in sorted((STORY / "quests").glob("*.json"))}
    talk = {p.name: json.loads(p.read_text()) for p in sorted((STORY / "talk").glob("*.json"))}
    lines = {l["id"]: (name, l) for name, t in talk.items() for l in t["lines"]}

    # ---- 1. supplied talk wording, exactly; the addendum overrides flint_who
    want_text = {r["id"]: r["text"] for r in pk["talk_text_replacements"]}
    want_text[ad["flint_who_override"]["id"]] = ad["flint_who_override"]["text"]
    want_text["quill_shamed"] = pk["pritchard_quill_history"]["quill_response"]
    want_text["roark_after_fire"] = pk["conditional_roark_lines"]["ordered_charges"]
    want_text["roark_after_deadline"] = pk["conditional_roark_lines"]["warned_deadline_abandoned"]
    for lid, text in want_text.items():
        if lid not in lines:
            bad("line %s is missing" % lid)
        elif lines[lid][1]["text"] != text:
            bad("line %s does not carry the supplied text" % lid)
    labels = [b["label"] for _, l in lines.values() for b in l.get("buttons", [])]
    for r in pk["talk_text_replacements"]:
        for key in ("incoming_button_change", "button_change"):
            if key in r:
                if r[key]["from"] in labels:
                    bad("old button still there: %s" % r[key]["from"])
                if r[key]["to"] not in labels:
                    bad("new button missing: %s" % r[key]["to"])
    for label in (pk["pritchard_quill_history"]["challenge_button"], pk["quest_text_contracts"]["mq02c_fire_button"],
                  pk["quest_text_contracts"]["mq02b_fire_button"]):
        if label not in labels:
            bad("supplied button missing from talk: %s" % label)
    for old in ("You hanged the wrong man in ninety-eight.", "Fire your charges, Captain.", "Light the boiler and get clear.", "Send your deputy."):
        if old in labels or any(old in json.dumps(q) for q in quests.values()):
            bad("retired button or label still present: %s" % old)

    # ---- 2. what was to be removed is gone, and nothing still points at it
    for lid in pk["remove_fair_dialogue_nodes"] + ["pritchard_talbot_back", "talbot_sent", "keene_talbot_aside"]:
        if lid in lines:
            bad("line %s should have been removed" % lid)
    everything = "\n".join(p.read_text() for p in sorted(STORY.rglob("*.json")))
    for ref in ("mq03 set 30", "mq03 done 30", "mq03 notdone 30", "mq02 set 70", "mq02 done 70", "mq02 notdone 70"):
        if ref in everything:
            bad("reference to a removed stage: %s" % ref)
    if 30 in [s["n"] for s in quests["mq03"]["stages"]]:
        bad("mq03 still has stage 30")
    if 70 in [s["n"] for s in quests["mq02"]["stages"]]:
        bad("mq02 still has stage 70")
    if [s["n"] for s in quests["mq03"]["stages"]] != [10, 20, 21, 22, 40, 41, 42, 43, 44, 50, 60, 70, 100]:
        bad("mq03 stages were renumbered or lost")
    if [s["n"] for s in quests["mq02"]["stages"]] != [10, 20, 30, 40, 50, 60, 100]:
        bad("mq02 stages were renumbered or lost")

    # ---- 3. character metadata
    for r in pk["character_field_replacements"]:
        if chars[r["id"]][r["field"]] != r["value"]:
            bad("characters.json %s.%s is not the supplied value" % (r["id"], r["field"]))
    if chars["pike"]["secret"] != pk["pike_ammunition_tooling"]["replacement_secret"]:
        bad("pike.secret is not the supplied value")
    names = {"tarrow": "Wilhelmina Tupper", "greer": "Hobart Blevins", "pruitt": "Mose Rafferty", "vickers": "Temperance Beckett",
             "dole": "Ezekiel Dole", "lockridge": "Augusta Lockridge", "starnes": "Opal Starnes", "hatcher": "Lyle Hatcher",
             "roark": "Dinah Roark", "threefords": "Juno Three-Fords", "granger": "Tolly Granger"}
    for cid, name in names.items():
        if chars[cid]["name"] != name:
            bad("characters.json %s is named %s, not %s" % (cid, chars[cid]["name"], name))

    # ---- 4. names, initials and retired words, in every story JSON file (ids are lower case and are kept)
    for word in OLD_SURNAMES + RETIRED_WORDS:
        for p in sorted(STORY.rglob("*.json")):
            if word in p.read_text():
                bad("%s still contains %r" % (p.relative_to(STORY), word))

    # ---- 5. supplied quest wording
    q = pk["quest_text_contracts"]
    def log(key, n): return [s for s in quests[key]["stages"] if s["n"] == n][0]["log"]
    def flag(key, name): return [f for f in quests[key]["new_flags"] if f["name"] == name][0]["meaning"]
    def option(key, at, label): return [o for c in quests[key]["choices"] if c["at"] == at for o in c["options"] if o["label"] == label]
    checks = [(log("mq02c", 15), q["mq02c_stage15_log"]), (log("mq02c", 51), q["mq02c_stage51_log"]), (log("mq03", 41), q["mq03_stage41_log"]),
              (flag("mq02c", "hollow_line"), q["mq02c_hollow_line_flag"]), (flag("mq02b", "queen_burned"), q["mq02b_queen_burned_flag"]),
              (flag("mq03", "saw_the_shooter"), q["mq03_saw_the_shooter_flag"]), (quests["mq03"]["premise"], q["mq03_premise"])]
    for got, want in checks:
        if got != want:
            bad("quest text is not the supplied wording: %s" % want[:60])
    o = option("mq03", 40, q["mq03_choice41_label"])
    if not o or o[0]["now"] != q["mq03_choice41_now"] or o[0]["later"] != q["mq03_choice41_later"] or o[0]["sets"] != 41:
        bad("mq03 choice for stage 41 is not the supplied one")
    if not option("mq02c", 50, q["mq02c_fire_button"]) or not option("mq02b", 40, q["mq02b_fire_button"]):
        bad("a supplied choice label is missing from a quest file")
    for key, text in (("mq02", q["mq02"]), ("mq03", q["mq03_shot_and_occupation_rule"])):
        if text not in quests[key]["cannot_break"]:
            bad("%s cannot_break does not carry the supplied contract" % key)
    if "talbot_shot" in json.dumps(quests):
        bad("talbot_shot is still declared or read")

    # ---- 6. ballads: whole replacement, and routing by the recorded outcome
    v = ad["variants"]
    want_docs = {"ballad_six_rounds": v["saved"]["full_text"], "ballad_six_rounds_evaded_or_missed": v["evaded_or_missed"]["full_text"],
                 "ballad_six_rounds_exploited": v["exploited"]["full_text"], "ballad_six_rounds_unconfirmed": ad["common_body"]}
    for did, text in want_docs.items():
        if did not in docs or docs[did]["text"] != text or docs[did]["title"] != ad["target"]["title"]:
            bad("document %s is not the supplied sheet" % did)
    cries = {"saved": "granger_ballad_saved", "evaded": "granger_ballad_walked", "missed": "granger_ballad_missed", "exploited": "granger_ballad_deal"}
    for r in ad["routing"]:
        lid = cries[r["outcome"]]
        if lid not in lines or lines[lid][1]["when"] != ["outcome is " + r["outcome"]]:
            bad("no ballad cry bound to outcome %s" % r["outcome"])
        elif lines[lid][1]["text"] not in v[r["variant"]]["ending"].replace("\n", " "):
            bad("%s does not quote the %s sheet" % (lid, r["variant"]))
    for did, d in docs.items():
        if re.search(r"six rounds|five came back", d["text"], re.I):
            bad("document %s still carries the old fixed-ammunition ballad" % did)

    # ---- 7. wiring the contracts need
    def when(lid): return lines[lid][1]["when"]
    def sets(lid): return [e for b in lines[lid][1].get("buttons", []) for o in ([b] if "check" not in b else [b["pass"], b["fail"]]) for e in o.get("do", [])]
    if "flag docket_2298_held" not in when("quill_court_docket") or "mq02c set 13" not in sets("quill_court_docket") or "mq02c set 13" in sets("quill_court"):
        bad("the 2298 challenge is not gated on holding the docket")
    if any("check" in b for b in lines["quill_court"][1]["buttons"] + lines["quill_court_docket"][1]["buttons"]):
        bad("the 2298 challenge is still a speech check")
    if "mq02c set 53" in sets("greer_first") or "mq02c set 53" not in sets("greer_first_heard") or "mq02c done 30" not in when("greer_first_heard"):
        bad("the seal order is not gated on having heard the knocking")
    if when("roark_after_fire") != ["mq02c done 53"] or when("roark_after_deadline") != ["mq02c done 56"]:
        bad("Roark's two aftermath lines are not bound to their two distinct facts")
    if [e for lid in lines for e in sets(lid) if e == "mq02c set 56"]:
        bad("a button sets the deadline stage; only the local deadline may")
    if sets("pritchard_three_tokens").count("mq02 set 50") != 1 or "mq02 set 100" not in sets("pritchard_three_tokens"):
        bad("calling the fair without a report does not open the fair")
    if "mq02 done 100" not in when("pritchard_three_tokens_later"):
        bad("the roads are not offered again after the fair is called")
    for lid in ("dunmore_freed", "dunmore_freed_fine"):
        if "mq02c done 13" in when(lid) or "mq02c done 15" in when(lid):
            bad("%s can still play for a man who was not freed" % lid)

    # ---- for a person to read
    notes.append("\nWhere the inspector's legal name is written (each must be at or after the reveal):")
    for where, text in player_facing(quests, lines, docs):
        if re.search(r"Ostrander|Reuben", text):
            notes.append("  %s" % where)
    notes.append("\nPossible recognition or foreknowledge cues left in player-facing text or character notes (read each):")
    for where, text in player_facing(quests, lines, docs) + [("characters.json %s.%s" % (c["id"], f), json.dumps(c[f])) for c in chars.values() for f in c if f not in ("id", "record", "name", "status", "sex", "age", "sources")]:
        for cue in CUES:
            if cue in text.lower():
                notes.append("  %-45s %r" % (where, cue))
    notes.append("\nSpeakers with more than one line that has no condition and priority 0 (the format gives no order between them):")
    free = {}
    for lid, (_, l) in lines.items():
        if not l["when"] and l.get("priority", 0) == 0:
            free.setdefault(l["speaker"], []).append(lid)
    targets = {o.get("then") for _, l in lines.values() for b in l.get("buttons", []) for o in ([b] if "check" not in b else [b["pass"], b["fail"]])}
    for speaker, ids in sorted(free.items()):
        if len(ids) > 1:
            notes.append("  %s: %s" % (speaker, ", ".join(ids)))
    notes.append("\nLines nothing leads to and no condition selects, other than a speaker's default:")
    for lid, (_, l) in lines.items():
        if not l["when"] and lid not in targets and not lid.endswith("_default"):
            notes.append("  " + lid)
    notes.append("\nFlags declared and never read by a condition in this folder:")
    used = set(re.findall(r"(?:not)?flag ([a-z0-9_]+)", "\n".join(json.dumps(t) for t in talk.values()) + json.dumps([x["reads"] for x in quests.values()])))
    for key, x in quests.items():
        for f in x["new_flags"]:
            if f["name"] not in used:
                notes.append("  %s: %s" % (key, f["name"]))

    print("\n".join(notes))
    print()
    if failed:
        print("REVISION CHECKS FAILED (%d):" % len(failed))
        for f in failed:
            print("  " + f)
        return 1
    print("revision checks: the story folder agrees with both packets (%d lines, %d documents, %d characters, %d quests)."
          % (len(lines), len(docs), len(chars), len(quests)))
    print("This is agreement with the packets only: not the strict intake check, not a compile, not a game test.")
    return 0


def player_facing(quests, lines, docs):
    out = []
    for key, x in quests.items():
        out += [("quest %s stage %s log" % (key, s["n"]), s["log"]) for s in x["stages"] if s["log"]]
        out += [("quest %s objective %s" % (key, o["n"]), o["text"]) for o in x["objectives"]]
        out += [("quest %s choice label" % key, o["label"]) for c in x["choices"] for o in c["options"]]
    for lid, (name, l) in lines.items():
        out.append(("talk %s" % lid, l["text"]))
        out += [("talk %s button" % lid, b["label"]) for b in l.get("buttons", [])]
    out += [("document %s" % did, d["title"] + "\n" + d["text"]) for did, d in docs.items()]
    return out


if __name__ == "__main__":
    sys.exit(main())
