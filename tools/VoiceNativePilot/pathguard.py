"""Read-only lexical/whole-ancestor preflight for this NEW workspace package only.
No deletion/adoption/hostile-concurrent-world atomicity promise.
"""
from pathlib import Path
import stat

def check_ancestry(path,inspect=None):
 inspect=inspect or (lambda p:p.lstat())
 for part in [*reversed(Path(path).parents),Path(path)]:
  try:info=inspect(part)
  except FileNotFoundError:continue
  if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:raise ValueError('Reparse package ancestry refused: '+str(part))
  if part!=Path(path) and not stat.S_ISDIR(info.st_mode):raise ValueError('Package ancestor is not a directory')

def check_output(project,output,inspect=None):
 project=Path(project).absolute();output=Path(output).absolute()
 if output.parent!=project/'build' or output.name in ('.','..') or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in output.name):raise ValueError('Package must be one new child of this project build root')
 check_ancestry(project,inspect);check_ancestry(output,inspect)
 inspect=inspect or (lambda p:p.lstat())
 try:inspect(output)
 except FileNotFoundError:return
 raise ValueError('Existing package output is never adopted')
