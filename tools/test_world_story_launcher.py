"""Run fixture-based launcher checks under the available PowerShell; never launch game."""
import os,shutil,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
shell=shutil.which('pwsh') or shutil.which('powershell')
if not shell:raise SystemExit('PowerShell is required for story launcher fixture checks')
process_flags=['-ExecutionPolicy','Bypass'] if os.name=='nt' else []
subprocess.run([shell,'-NoLogo','-NoProfile',*process_flags,'-File',str(root/'tools/win/tests/Test-WorldStory.ps1'),'-CoreArtifact',str(root/'build/TheLastMeridian.esp')],check=True,cwd=root)
