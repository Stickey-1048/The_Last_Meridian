#!/usr/bin/env bash
# Runs every check that works without Fallout 4:
#   1. logic model tests (stage table, outcomes, exhaustive state search)
#   2. plugin build + read-back self-check, and a check of the written bytes
#      that does not use the library that wrote them
#   3. cross-check of Papyrus sources, plugin and model
#   4. plugin build with vanilla lookups, against a generated stand-in master
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
python3 tools/check_consistency.py

echo "== 4/5 plugin build against a stand-in master =="
# A tiny generated file standing in for Fallout4.esm, holding only the two
# vanilla records the builder looks up (Caps001, PlayerRef). This exercises the
# lookup code. It says nothing about the real Fallout4.esm.
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
standin() {  # variant
  dotnet run --project tools/StandInMaster -- "$tmp/$1/Fallout4.esm" "$1" | grep -v warning
  dotnet run --project tools/PluginBuilder -- --out "$tmp/$1/out" --fallout4-esm "$tmp/$1/Fallout4.esm" | grep -v warning | grep -E "lookup:|self-check"
}
report() { echo "$tmp/$1/out/TheLastMeridian.report.txt"; }

standin default
python3 tools/check_plugin_layout.py "$tmp/default/out/TheLastMeridian.esp" >/dev/null || { echo "FAILED: the plugin built against a master has the wrong quest layout"; exit 1; }
grep -q "FixtureActorBase = " "$(report default)" || { echo "FAILED: the settler the self-test's stand-ins are made from was not found in the master"; exit 1; }
grep -q "FixtureMarkerBase = " "$(report default)" || { echo "FAILED: the marker the self-test's stand-ins are made from was not found in the master"; exit 1; }
# This build is the one the stand-in engine runs the scripts against (step 5).
mkdir -p build/sim
cp "$tmp/default/out/TheLastMeridian.json" "$tmp/default/out/TheLastMeridian.vanilla.json" build/sim/
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
echo "  vanilla lookups work against five stand-in masters (spelling, fallback, rejection, quest evidence, weak evidence)"

echo "== 5/5 the scripts against a stand-in for the game =="
(cd tools/papyrus_sim && python3 -m unittest 2>&1 | tail -4)
python3 tools/papyrus_sim --plugin build/sim/TheLastMeridian.json 1 2 3 4 5 6 7 8 9 | grep -E "^scenario|stand-in"
