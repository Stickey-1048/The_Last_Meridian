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
# quests, and the references placed in the test room. With --self-test the
# file is also damaged in a dozen ways, and each has to be noticed.
python3 tools/check_plugin_layout.py --self-test "$tmp/default/out/TheLastMeridian.esp" | sed -n '2,3p' || { echo "FAILED: the plugin built against a master has the wrong layout"; exit 1; }
python3 tools/check_plugin_layout.py "$tmp/default/out/TheLastMeridian.esp" >/dev/null || { echo "FAILED: the plugin built against a master has the wrong layout"; exit 1; }
grep -q "TLM_REF_TrialPerson  PlacedNpc of .* at (1500, -950, 64) turned (0, 0, 270)  \[Persistent, InitiallyDisabled\]  in the Persistent list" "$(report default)" || { echo "FAILED: the placed person is not where the arrival marker and its heading put it"; exit 1; }
grep -q "TLM_REF_TrialTrigger  PlacedObject of TLM_ACTI_TrialTrigger  at (1800, -600, 164) .*  Box (150, 150, 150)  collision layer 12" "$(report default)" || { echo "FAILED: the placed trigger is not as specified"; exit 1; }
grep -q "TLM_MISC_TrialObject  \"Trial Object\"  model: " "$(report default)" || { echo "FAILED: the trial object did not borrow a world model from the master"; exit 1; }
grep -q "alias  0 Person  (reference) \[Optional, AllowDisabled\]  fill: forced .*  shown as: TLM_MSG_TrialPersonName" "$(report default)" || { echo "FAILED: the Person alias does not point at the placed person"; exit 1; }
grep -q "FixtureActorBase = " "$(report default)" || { echo "FAILED: the settler the self-test's stand-ins are made from was not found in the master"; exit 1; }
grep -q "FixtureMarkerBase = " "$(report default)" || { echo "FAILED: the marker the self-test's stand-ins are made from was not found in the master"; exit 1; }
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

# A test room with no arrival marker, in a master with no collision layers, no
# empty trigger and no triggers of its own: the builder places what it can,
# from the origin, and says what it left out.
standin bare-room
python3 tools/check_plugin_layout.py "$tmp/bare-room/out/TheLastMeridian.esp" >/dev/null || { echo "FAILED: the plugin built against the bare room has the wrong layout"; exit 1; }
grep -q "placing from the origin (0, 0, 0)" "$(report bare-room)" || { echo "FAILED: a test room without an arrival marker was not reported"; exit 1; }
grep -q "TLM_REF_TrialTrigger: placed without a collision layer" "$(report bare-room)" || { echo "FAILED: a trigger without its collision layer was not reported"; exit 1; }
grep -q "TLM_REF_TrialTriggerGameBase: not placed (no Activator 'DefaultEmptyTrigger' in Fallout4.esm)" "$(report bare-room)" || { echo "FAILED: the missing comparison trigger was not reported"; exit 1; }
grep -q "alias  2 TriggerGameBase  (reference) \[Optional\]$" "$(report bare-room)" || { echo "FAILED: the alias of a reference that was not placed is filled"; exit 1; }

[ "$(git hash-object tools/PluginBuilder/formkeys.txt)" = "$ids_before" ] || { echo "FAILED: a build against a master changed tools/PluginBuilder/formkeys.txt; ids must be given out the same with and without Fallout4.esm"; exit 1; }
echo "  vanilla lookups work against six stand-in masters (spelling, fallback, rejection, quest evidence, weak evidence, a bare test room)"
echo "  the id file came out the same with and without a master"

echo "== 5/5 the scripts against a stand-in for the game =="
(cd tools/papyrus_sim && python3 -m unittest 2>&1 | tail -4)
python3 tools/papyrus_sim --brief all
# The same with every call out of a script taking a frame, so that handlers
# on different threads overlap (amendment A24).
python3 tools/papyrus_sim --brief --calls-per-second 60 all | head -1
