#!/usr/bin/env bash
# Runs every check that works without Fallout 4:
#   1. logic model tests (stage table, outcomes, exhaustive state search)
#   2. plugin build + read-back self-check
#   3. cross-check of Papyrus sources, plugin and model
# A pass here means the design is internally consistent. It does not mean the
# mod works: nothing is compiled by the Papyrus compiler or loaded by the game.
set -euo pipefail
cd "$(dirname "$0")/.."
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1

echo "== 1/3 logic model =="
(cd tools/logic_model && python3 -m unittest 2>&1 | tail -4)

echo "== 2/3 plugin build =="
dotnet run --project tools/PluginBuilder -- --out build | grep -v warning
if ! diff -q build/TheLastMeridian.report.txt tools/PluginBuilder/last-build.report.txt >/dev/null; then
  echo "NOTE: the plugin report changed. Review it, then:"
  echo "  cp build/TheLastMeridian.report.txt tools/PluginBuilder/last-build.report.txt"
  exit 1
fi

echo "== 3/3 consistency =="
python3 tools/check_consistency.py
