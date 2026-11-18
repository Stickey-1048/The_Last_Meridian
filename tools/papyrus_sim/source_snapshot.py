"""Read-only Git source exports for frozen candidate tests, never live pins."""
import io
import subprocess
import tempfile
import zipfile
from pathlib import Path
from test_sim import ROOT

GREENWATER = "016b2b4005203ba180b908fb310a1653a95f934f"
_snapshots = {}


def snapshot(commit=GREENWATER):
    if commit not in _snapshots:
        got = subprocess.run(["git", "archive", "--format=zip", commit], cwd=ROOT, capture_output=True, check=True)
        target = Path(tempfile.mkdtemp(prefix="tlm-source-"))
        with zipfile.ZipFile(io.BytesIO(got.stdout)) as archive:
            archive.extractall(target)
        _snapshots[commit] = target
    return _snapshots[commit]


def built_greenwater():
    root = snapshot()
    out = root / "build/sim/TheLastMeridian.json"
    if not out.exists():
        for args in (["tools/StandInMaster", "build/standin/Fallout4.esm", "default"],
                     ["tools/PluginBuilder", "--out", "build/sim", "--fallout4-esm", "build/standin/Fallout4.esm"]):
            got = subprocess.run(["dotnet", "run", "--project", args[0], "--"] + args[1:], cwd=root, capture_output=True, text=True)
            if got.returncode:
                raise AssertionError("Frozen 016b stand-in build failed:\n" + got.stdout + got.stderr)
    return out


NIGHT_MAIL = "4624ee90844e34d20db0124b109837798256e8c7"

def built_night_mail():
    root = snapshot(NIGHT_MAIL)
    out = root / "build/sim/TheLastMeridian.json"
    if not out.exists():
        for args in (["tools/StandInMaster", "build/standin/Fallout4.esm", "default"],
                     ["tools/PluginBuilder", "--out", "build/sim", "--fallout4-esm", "build/standin/Fallout4.esm"]):
            got = subprocess.run(["dotnet", "run", "--project", args[0], "--"] + args[1:], cwd=root, capture_output=True, text=True)
            if got.returncode:
                raise AssertionError("Frozen 4624 stand-in build failed:\n" + got.stdout + got.stderr)
    return out


RED_HOLLOW = "1cdd4666b12e3b40f0c3bf5a3e877f561c7b8d83"

def built_red_hollow():
    root = snapshot(RED_HOLLOW)
    out = root / "build/sim/TheLastMeridian.json"
    if not out.exists():
        for args in (["tools/StandInMaster", "build/standin/Fallout4.esm", "default"],
                     ["tools/PluginBuilder", "--out", "build/sim", "--fallout4-esm", "build/standin/Fallout4.esm"]):
            got = subprocess.run(["dotnet", "run", "--project", args[0], "--"] + args[1:], cwd=root, capture_output=True, text=True)
            if got.returncode:
                raise AssertionError("Frozen 1cdd stand-in build failed:\n" + got.stdout + got.stderr)
    return out


GREENWATER_RELIEF = "a31b5eded170dac81cd1d4f5d70a19a758c942e8"

def built_greenwater_relief():
    root = snapshot(GREENWATER_RELIEF)
    out = root / "build/sim/TheLastMeridian.json"
    if not out.exists():
        for args in (["tools/StandInMaster", "build/standin/Fallout4.esm", "default"],
                     ["tools/PluginBuilder", "--out", "build/sim", "--fallout4-esm", "build/standin/Fallout4.esm"]):
            got = subprocess.run(["dotnet", "run", "--project", args[0], "--"] + args[1:], cwd=root, capture_output=True, text=True)
            if got.returncode:
                raise AssertionError("Frozen a31 stand-in build failed:\n" + got.stdout + got.stderr)
    return out

FOUR_FLAGS = 'd43bd336fde2837c9c499b273c4becdee3f4cef9'

def built_four_flags():
    root = snapshot(FOUR_FLAGS)
    out = root / 'build/sim/TheLastMeridian.json'
    if not out.exists():
        for args in (['tools/StandInMaster', 'build/standin/Fallout4.esm', 'default'], ['tools/PluginBuilder', '--out', 'build/sim', '--fallout4-esm', 'build/standin/Fallout4.esm']):
            got = subprocess.run(['dotnet', 'run', '--project', args[0], '--'] + args[1:], cwd=root, capture_output=True, text=True)
            if got.returncode: raise AssertionError('Frozen d43 stand-in build failed:\n'+got.stdout+got.stderr)
    return out

RED_HOLLOW_ENVIRONMENT='5c5c82ea438f1f1730480cd8ccd3b4a2d086add3'

def red_hollow_environment_snapshot():
    return snapshot(RED_HOLLOW_ENVIRONMENT)
