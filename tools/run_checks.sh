#!/usr/bin/env bash
# Runs every check that works without Fallout 4:
#   1. logic model tests (stage table, outcomes, exhaustive state search)
#   2. plugin build + read-back self-check, and a check of the written bytes
#      that does not use the library that wrote them
#   3. cross-check of Papyrus sources, plugin and model
#   4. plugin build with vanilla lookups, against generated stand-in masters:
#      the player reference, and the references the plugin places in the
#      game's test room (written, read back, and checked byte by byte)
#   5. the project's real scripts run against a stand-in for the game
#      (tools/papyrus_sim): every recorded game run is replayed and must come
#      out as it did in the game, and every self-test scenario must pass
# A pass here means the design is internally consistent. It does not mean the
# mod works: nothing is compiled by the Papyrus compiler or loaded by the game.
# Step 5 runs the scripts, but against rules written down from what the game
# was seen to do; it cannot show what the game does with anything new.
set -euo pipefail
cd "$(dirname "$0")/.."
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1

echo "== 1/5 logic model =="
(cd tools/logic_model && python3 -m unittest 2>&1 | tail -4)

echo "== 2/5 plugin build =="
dotnet run --project tools/PluginBuilder -- --out build | grep -v warning
if ! diff -q build/TheLastMeridian.report.txt tools/PluginBuilder/last-build.report.txt >/dev/null; then
  echo "NOTE: the plugin report changed. Review it, then:"
  echo "  cp build/TheLastMeridian.report.txt tools/PluginBuilder/last-build.report.txt"
  exit 1
fi
python3 tools/check_plugin_layout.py --self-test build/TheLastMeridian.esp

echo "== 3/5 consistency =="
# The in-game cases of the test matrix are generated from the logic model;
# the committed files must be what the generator writes now.
python3 tools/gen_matrix_cases.py --check
python3 tools/check_consistency.py

echo "== 4/5 plugin build against a stand-in master =="
# A tiny generated file standing in for Fallout4.esm, holding only what the
# builder looks up there: a few records by name, the player reference, and a
# test room to place things in. This exercises the lookup and placing code.
# It says nothing about the real Fallout4.esm.
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
standin() {  # variant
  dotnet run --project tools/StandInMaster -- "$tmp/$1/Fallout4.esm" "$1" | grep -v warning
  dotnet run --project tools/PluginBuilder -- --out "$tmp/$1/out" --fallout4-esm "$tmp/$1/Fallout4.esm" | grep -v warning | grep -E "lookup:|self-check"
}
report() { echo "$tmp/$1/out/TheLastMeridian.report.txt"; }

# The id file under version control must come out the same whichever way the
# plugin is built: a build that changed it would block a pull on the game PC.
ids_before="$(git hash-object tools/PluginBuilder/formkeys.txt)"

standin default
# The bytes of the written file, without the library that wrote them: the
# quests, the references placed in the test room, and the actors of the
# plugin's own. With --self-test the file is also damaged in two dozen ways,
# and each has to be noticed.
if python3 tools/check_plugin_layout.py --self-test "$tmp/default/out/TheLastMeridian.esp" > "$tmp/layout.txt"; then
  sed -n '2,4p' "$tmp/layout.txt"
else
  cat "$tmp/layout.txt"
  echo "FAILED: the plugin built against a master has the wrong layout"; exit 1
fi
grep -q "TLM_REF_TrialPerson  PlacedNpc of .* at (1500, -950, 64) turned (0, 0, 270)  \[Persistent, InitiallyDisabled\]  in the Persistent list" "$(report default)" || { echo "FAILED: the placed person is not where the arrival marker and its heading put it"; exit 1; }
grep -q "TLM_REF_TrialTrigger  PlacedObject of TLM_ACTI_TrialTrigger  at (1800, -600, 164) .*  Box (150, 150, 150)  bound (150, 150, 150)  collision layer 12" "$(report default)" || { echo "FAILED: the placed trigger is not as specified"; exit 1; }
grep -q "TLM_REF_TrialTriggerNoLayer  PlacedObject of TLM_ACTI_TrialTrigger  at (1560, -280, 164) .*  Box (150, 150, 150)  bound (150, 150, 150)$" "$(report default)" || { echo "FAILED: the trigger of the plugin's own with no collision layer is not as specified"; exit 1; }
grep -q "TLM_REF_TrialTriggerNoLayer: placed in QASmoke at (1560, -280, 164): .*; seen from above, within the span of the room's own objects" "$(report default)" ||
  { echo "FAILED: a reference inside the stand-in room was not reported as inside it"; exit 1; }
grep -q "QASmoke: its name is 'Stand-In Test Room' (the master holds its text itself); this plugin's copy of the cell carries it" "$(report default)" ||
  { echo "FAILED: the cell's name was not carried into the plugin's copy"; exit 1; }
grep -q "^Cell QASmoke .* name: \"Stand-In Test Room\"$" "$(report default)" || { echo "FAILED: the cell's copy in the written plugin does not carry the cell's name"; exit 1; }
grep -q "this build writes it too, as most of them do" "$(report default)" || { echo "FAILED: the builder did not follow a master whose triggers carry their bound"; exit 1; }
grep -q "TLM_MISC_TrialObject  \"Trial Object\"  model: " "$(report default)" || { echo "FAILED: the trial object did not borrow a world model from the master"; exit 1; }
grep -q "alias  0 Person  (reference) \[Optional, AllowDisabled\]  fill: forced .*  shown as: TLM_MSG_TrialPersonName" "$(report default)" || { echo "FAILED: the Person alias does not point at the placed person"; exit 1; }
# The people of scenario 11: actors of the plugin's own, made from the master's settler with nothing to go about.
grep -q "WorkshopNPC: the game's actor has packages: 2: StandInSandbox (.*), StandInPatrol (.*)$" "$(report default)" || { echo "FAILED: the packages of the master's settler were not reported"; exit 1; }
grep -q "WorkshopNPC: default package list: StandInDefaultPackages (.*), which holds 1: StandInSandbox (.*)$" "$(report default)" || { echo "FAILED: what is in the settler's default package list was not reported"; exit 1; }
grep -q "WorkshopNPC: other package lists, which a copy keeps: combat = StandInCombatPackages (.*), which holds 1: StandInPatrol (.*)$" "$(report default)" || { echo "FAILED: the settler's other package lists were not reported"; exit 1; }
grep -q "WorkshopNPC: script(s): StandInWorkshopScript$" "$(report default)" || { echo "FAILED: the settler's scripts were not reported"; exit 1; }
grep -q "WorkshopNPC: takes from a template: Traits, AiPackages, Inventory, Script, DefPackList; template actors named: Traits from StandInLCharSettler (.*), AiPackages from .*, Inventory from .*, Script from .*, DefPackList from .*; default template StandInLCharSettler (.*)$" "$(report default)" || { echo "FAILED: what the settler takes from a template, and from whom, was not reported"; exit 1; }
grep -q "WorkshopNPC: who it is: factions StandInSettlerFaction (.*); keywords StandInActorTypeSettler (.*); voice StandInSettlerVoice (.*); its record is compressed$" "$(report default)" || { echo "FAILED: who the settler is was not reported"; exit 1; }
grep -q "WorkshopNPC: the master's actors and their default package lists: 1 of 15 name one in their own record; different lists: 1; the commonest: StandInDefaultPackages (.*) (1)$" "$(report default)" || { echo "FAILED: the master's default package lists were not counted"; exit 1; }
# The copies: no packages, no script, neither fetched by a template flag nor by a template actor named for it; and plain records, though the master's is compressed.
grep -q "TLM_NPC_TrialPerson: made as a copy of WorkshopNPC with no packages and no script, and its default package list still taken from a template; named 'Second Trial Settler'; still from a template: Traits, Inventory, DefPackList; template actors still named for: Traits, Inventory, DefPackList$" "$(report default)" || { echo "FAILED: the person of the plugin's own was not made from the master's settler as specified"; exit 1; }
grep -q "TLM_NPC_TrialPersonBare: made as a copy of WorkshopNPC with no packages and no script, and no default package list; named 'Third Trial Settler'; still from a template: Traits, Inventory; template actors still named for: Traits, Inventory$" "$(report default)" || { echo "FAILED: the person with no default package list was not made as specified"; exit 1; }
grep -q "TLM_NPC_TrialPerson: 0 package(s), a default package list, script(s) none, from a template: Traits, Inventory, DefPackList, template actors named for: Traits, Inventory, DefPackList; looks from .*; factions: .*; temper: Unaggressive, HelpsNobody, Cowardly$" "$(report default)" || { echo "FAILED: the person of the plugin's own does not read back as made (or reads back compressed)"; exit 1; }
grep -q "TLM_REF_TrialSettlerOnFloor  PlacedNpc of .* at (1800, -600, 64) " "$(report default)" || { echo "FAILED: the second settler is not on the spot of the plugin's own people"; exit 1; }
grep -q "TLM_REF_TrialPersonOwn  PlacedNpc of TLM_NPC_TrialPerson  at (1800, -600, 64) turned (0, 0, 270)  \[Persistent, InitiallyDisabled\]  in the Persistent list" "$(report default)" || { echo "FAILED: the person of the plugin's own is not placed as an actor where specified"; exit 1; }
grep -q "alias  5 PersonOwn  (reference) \[Optional, AllowDisabled\]  fill: forced " "$(report default)" || { echo "FAILED: the PersonOwn alias does not point at the placed person"; exit 1; }
grep -q "packages: the master has 4; 2 have a name that begins 'Default' and holds one of .*: DefaultStandInHoldPosition (.*), DefaultStandInSandboxNearSelf (.*)$" "$(report default)" || { echo "FAILED: the master's stay-put packages were not listed"; exit 1; }
grep -q "FixtureActorBase = " "$(report default)" || { echo "FAILED: the settler the self-test's stand-ins are made from was not found in the master"; exit 1; }
grep -q "FixtureMarkerBase = " "$(report default)" || { echo "FAILED: the marker the self-test's stand-ins are made from was not found in the master"; exit 1; }
# The first section of Act I (docs/design/TLM_ACT1_first_section.md): thirteen people, each with the looks of one of
# the settlers the master's own list offers and of the sex the spec gives; things that look like the master's own
# things, found by the names a player sees; a dead marshal; a revolver; a crate; two papers.
expect() {  # pattern, what failed
  grep -q -- "$1" "$(report default)" || { echo "FAILED: $2"; exit 1; }
}
expect "WorkshopNPC: its looks are drawn from StandInLCharSettler (.*), which offers 7 actor(s): 3 male, 3 female, 1 of no one sex: StandInSettlerFemale01 (female), StandInSettlerMale01 (male), StandInSettlerMale02 (male), StandInSettlerFemale02 (female), StandInSettlerMale03 (male), StandInSettlerAnyFace (of no one sex), StandInSettlerWomanAnyFace (female)$" "the settlers a copy can take its looks from were not found, or their sexes not told (by the flag, by the actor they take their looks from, by a list all of one sex)"
expect "TLM_NPC_SHERIFF_MERCY: made as a copy of WorkshopNPC with no packages and no script, and no default package list; named 'Owen Pritchard'; still from a template: Traits, Inventory; template actors still named for: Traits, Inventory; in TLM_Fac_MercyCrossing and in none of the game's 1 faction(s); starts no fight, joins none, and does not run from one; looks: those of StandInSettlerMale01 (.*), male, number 1 of 3$" "the sheriff was not made as specified"
expect "TLM_NPC_GUNSMITH_MERCY: .*; looks: those of StandInSettlerFemale01 (.*), female, number 1 of 3$" "the first woman did not get the first woman's looks"
expect "TLM_NPC_MERCHANT_MERCY: .*; looks: those of StandInSettlerMale02 (.*), male, number 2 of 3$" "the second man did not get the looks of the settler who takes his own from another man"
expect "TLM_NPC_CARAVAN_MASTER: .*; looks: those of StandInSettlerWomanAnyFace (.*), female, number 3 of 3$" "a settler whose looks come from a list of women only was not taken for a woman"
expect "TLM_NPC_FREIGHT_MERCY: .*; looks: those of StandInSettlerMale01 (.*), male, number 1 of 3 (used before: there are more people than faces)$" "a face used a second time was not said to be"
expect "TLM_NPC_CUTTER_LEAD: .*; in TLM_Fac_Cutters and in none of the game's 1 faction(s); starts no fight, joins one of its own faction's, and does not run from one; looks: " "the Cutter lead was not made as specified"
expect "TLM_NPC_CUTTER_LEAD: 0 package(s), no default package list, script(s) none, from a template: Traits, Inventory, template actors named for: Traits, Inventory; looks from .*; factions: TLM_Fac_Cutters; temper: Unaggressive, HelpsAllies, Foolhardy$" "the Cutter lead does not read back as made"
expect "TLM_MISC_Dispatch: world model borrowed from 'Folder' (StandInFolder): 'StandIn.Folder.nif'$" "the dispatch did not borrow the look of the thing a player sees as Folder"
expect "TLM_ACTI_BrakeShoes: 'Hubcap' -> .* (MiscItem StandInHubcapFirst; found by the name a player sees, the first of 2 so named)$" "of two things with one name the one with the lower id was not taken"
expect "TLM_ACTI_NoticeBoard: world model borrowed from 'Folder' (StandInFolder): " "a thing with the right name and no model was not passed over for the next name"
expect "NOTE TLM_ACTI_DrawBar: none of the things it was to look like was found, so it looks like Caps001$" "a thing none of whose looks is in the master did not fall back on the bottle cap"
expect "notes: 3 of the master's 5 book(s) lie in the world as 'StandIn.Note.nif', more than as any other model; the plugin's papers take after StandInNotePlain (.*)$" "the note for the plugin's papers to take after was not chosen as described (the commonest model, and not the note with a script)"
expect "TLM_BOOK_RailMaintLedger  \"Maintenance Ledger, Line 14\"  model: StandIn.Note.nif$" "the ledger has no world model"
expect "TLM_CONT_WagonCargo  \"Fenwick's Cargo\"  model: StandIn.Crate.nif  holds: 40 of " "the wagon's cargo is not a crate with caps in it"
expect "TLM_REF_A1_Revolver: '.44 Pistol' -> .* (Weapon StandIn44; found by the name a player sees)$" "the marshal's revolver was not found by its name"
expect "TLM_A1 script TLM:Act1Walk.RevolverRounds: what that weapon fires -> .* (Ammunition StandInAmmo44)$" "what the revolver fires was not found"
expect "TLM_REF_A1_Marshal  PlacedNpc of TLM_NPC_MARSHAL_DEAD  at (1430, -380, 64) turned (0, 0, 270)  \[Persistent, InitiallyDisabled, StartsDead\]  in the Persistent list" "the marshal is not placed dead where specified"
expect "TLM_REF_A1_AmbushSight  PlacedObject of TLM_TRIG_AmbushSight  at (1500, -650, 164) .*  Box (100, 100, 100)  bound (100, 100, 100)$" "the box the ambush is seen from is not as specified"
expect "alias 12 Dunmore  (reference) \[Optional, AllowDisabled\]  fill: forced " "the first section's quest does not hold the Cutter lead"
expect "           CastInto = \[alias 1 on TLM_MQ01, alias 2 on TLM_SQ01, alias 2 on TLM_MQ01, " "the list of the real quests' aliases to put things into was not written as a list of aliases"
expect "           PipBoy = " "the thing on the player's arm was not found in the master"
# This build is the one the stand-in engine runs the scripts against (step 5).
mkdir -p build/sim
cp "$tmp/default/out/TheLastMeridian.json" "$tmp/default/out/TheLastMeridian.vanilla.json" "$tmp/default/out/TheLastMeridian.arrivals.json" build/sim/
grep -q "alias  0 Player  (reference) \[\]  fill: forced" "$(report default)" || { echo "FAILED: Player alias was not filled from the master"; exit 1; }
grep -q "Caps = " "$(report default)" || { echo "FAILED: Caps property was not filled from the master"; exit 1; }
grep -q "PlayerRef -> .*which the master spells 'PlayerREF'" "$(report default)" || { echo "FAILED: the player reference was not found regardless of letter case"; exit 1; }
grep -q "places actor 'Player'" "$(report default)" || { echo "FAILED: the player reference was not checked against its base actor"; exit 1; }

standin unnamed-player
grep -q "alias  0 Player  (reference) \[\]  fill: forced 000014:Fallout4.esm" "$(report unnamed-player)" || { echo "FAILED: fallback to the conventional player id did not fill the alias"; exit 1; }
grep -q "Caps = 00000F:Fallout4.esm" "$(report unnamed-player)" || { echo "FAILED: Caps001 was not resolved at a low id"; exit 1; }

standin wrong-player
grep -q "alias  0 Player  (reference) \[Optional\]" "$(report wrong-player)" || { echo "FAILED: a reference that does not place 'Player' was accepted"; exit 1; }
grep -q "does not place the actor 'Player'" "$(report wrong-player)" || { echo "FAILED: the rejected player reference was not reported"; exit 1; }

standin quest-evidence
grep -q "alias  0 Player  (reference) \[\]  fill: forced 000014:Fallout4.esm" "$(report quest-evidence)" || { echo "FAILED: the game's own quests forcing 0x14 into 'Player' aliases were not accepted as evidence"; exit 1; }

standin weak-evidence
grep -q "alias  0 Player  (reference) \[Optional\]" "$(report weak-evidence)" || { echo "FAILED: two quests were accepted as enough evidence for the player reference"; exit 1; }
grep -q "^Cell " "$(report weak-evidence)" && { echo "FAILED: a cell record was written although the master has no test room"; exit 1; }
grep -q "TLM_REF_TrialPerson: not placed (no cell 'QASmoke' in Fallout4.esm)" "$(report weak-evidence)" || { echo "FAILED: a master without the test room was not reported"; exit 1; }
# That master has no settler either: the actors made from it are left out, and so is whoever stands on them.
grep -q "TLM_NPC_TrialPerson: not made (no Npc 'WorkshopNPC' in Fallout4.esm)" "$(report weak-evidence)" || { echo "FAILED: an actor that could not be made was not reported"; exit 1; }
grep -q "^Npc " "$(report weak-evidence)" && { echo "FAILED: an actor record was written although the master has no settler to copy"; exit 1; }
grep -q "TLM_NPC_SHERIFF_MERCY: not made (no Npc 'WorkshopNPC' in Fallout4.esm)" "$(report weak-evidence)" || { echo "FAILED: a person of the first section who could not be made was not reported"; exit 1; }

# A master that keeps its text apart, in strings files, as the game's own
# master does: the room's name has to come out of those. And the same master
# with the strings files taken away: the copy then has no name, the build says
# so, and nothing stops.
standin localized
python3 tools/check_plugin_layout.py "$tmp/localized/out/TheLastMeridian.esp" >/dev/null || { echo "FAILED: the plugin built against the localized master has the wrong layout"; exit 1; }
grep -q "QASmoke: its name is 'Stand-In Test Room' (the master keeps its text in strings files); this plugin's copy of the cell carries it" "$(report localized)" || { echo "FAILED: the cell's name was not read from the master's strings files"; exit 1; }
rm -rf "$tmp/localized/Strings" "$tmp/localized/out"
dotnet run --project tools/PluginBuilder -- --out "$tmp/localized/out" --fallout4-esm "$tmp/localized/Fallout4.esm" | grep -v warning | grep -E "self-check" || { echo "FAILED: the build against a localized master without its strings files did not pass its self-check"; exit 1; }
python3 tools/check_plugin_layout.py "$tmp/localized/out/TheLastMeridian.esp" >/dev/null || { echo "FAILED: the plugin built without the master's strings files has the wrong layout"; exit 1; }
grep -q "NOTE QASmoke: no name was read for it (the master keeps its text in strings files; either the cell has none or the strings were not found)" "$(report localized)" || { echo "FAILED: a cell name that could not be read was not reported"; exit 1; }
grep -q "^Cell QASmoke .* name: none$" "$(report localized)" || { echo "FAILED: the cell's copy has a name although none could be read"; exit 1; }
# Without the strings files no thing has a name a player sees: what was to look like one falls back on the bottle
# cap, and what was to be one (the revolver) is left out and said to be.
grep -q "NOTE TLM_MISC_Dispatch: none of the things it was to look like was found, so it looks like Caps001$" "$(report localized)" || { echo "FAILED: without the master's strings files the dispatch did not fall back on the bottle cap's look"; exit 1; }
grep -q "TLM_REF_A1_Revolver: not placed (no Weapon of that name in Fallout4.esm)" "$(report localized)" || { echo "FAILED: without the master's strings files the revolver was not reported as left out"; exit 1; }

# A master whose own box triggers carry no bound: the builder writes none either.
standin plain-triggers
python3 tools/check_plugin_layout.py "$tmp/plain-triggers/out/TheLastMeridian.esp" >/dev/null || { echo "FAILED: the plugin built against the master with plain triggers has the wrong layout"; exit 1; }
grep -q "TLM_NPC_TrialPerson: made as a copy of WorkshopNPC with no packages and no script, and no default package list (the game's actor names none); named 'Second Trial Settler'; still from a template: nothing; template actors still named for: nothing$" "$(report plain-triggers)" || { echo "FAILED: a settler with no default package list and no template was not copied as it is"; exit 1; }
grep -q "TLM_NPC_SHERIFF_MERCY: .*; NOTE: WorkshopNPC draws its looks from nowhere, so the copy looks as it does, whatever the spec asks for$" "$(report plain-triggers)" || { echo "FAILED: a settler that draws its looks from nowhere was not reported"; exit 1; }
grep -q "this build does not write it, as most of them do not" "$(report plain-triggers)" || { echo "FAILED: the builder did not follow a master whose triggers carry no bound"; exit 1; }
grep -q "TLM_REF_TrialTrigger  PlacedObject of TLM_ACTI_TrialTrigger  at (1800, -600, 164) .*  Box (150, 150, 150)  collision layer 12" "$(report plain-triggers)" || { echo "FAILED: a bound was written although the master's own triggers carry none"; exit 1; }

# A test room with no arrival marker, in a master with no collision layers, no
# empty trigger and no triggers of its own: the builder places what it can,
# from the origin, and says what it left out.
standin bare-room
python3 tools/check_plugin_layout.py "$tmp/bare-room/out/TheLastMeridian.esp" >/dev/null || { echo "FAILED: the plugin built against the bare room has the wrong layout"; exit 1; }
grep -q "TLM_REF_TrialTrigger: placed in QASmoke at (-200, 600, 100): .*NOTE: seen from above, outside the span of the room's own objects" "$(report bare-room)" || { echo "FAILED: a reference outside the bare room was not reported as outside it"; exit 1; }
grep -q "placing from the origin (0, 0, 0)" "$(report bare-room)" || { echo "FAILED: a test room without an arrival marker was not reported"; exit 1; }
grep -q "TLM_REF_TrialTrigger: placed without a collision layer" "$(report bare-room)" || { echo "FAILED: a trigger without its collision layer was not reported"; exit 1; }
grep -q "TLM_REF_TrialTriggerGameBase: not placed (no Activator 'DefaultEmptyTrigger' in Fallout4.esm)" "$(report bare-room)" || { echo "FAILED: the missing comparison trigger was not reported"; exit 1; }
grep -q "alias  2 TriggerGameBase  (reference) \[Optional\]$" "$(report bare-room)" || { echo "FAILED: the alias of a reference that was not placed is filled"; exit 1; }

[ "$(git hash-object tools/PluginBuilder/formkeys.txt)" = "$ids_before" ] || { echo "FAILED: a build against a master changed tools/PluginBuilder/formkeys.txt; ids must be given out the same with and without Fallout4.esm"; exit 1; }
echo "  vanilla lookups work against eight stand-in masters (spelling, fallback, rejection, quest evidence, weak evidence, text in strings files, triggers without a bound, a bare test room)"
echo "  the id file came out the same with and without a master"

echo "== 5/5 the scripts against a stand-in for the game =="
(cd tools/papyrus_sim && python3 -m unittest 2>&1 | tail -4)
python3 tools/papyrus_sim --brief all
# The same with every call out of a script taking a frame, so that handlers
# on different threads overlap (amendment A24).
python3 tools/papyrus_sim --brief --calls-per-second 60 all | head -1
