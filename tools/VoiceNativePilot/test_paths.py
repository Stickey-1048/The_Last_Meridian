from pathlib import Path
from types import SimpleNamespace
import stat,tempfile,unittest
from unittest.mock import patch
from pathguard import check_ancestry,check_output
class PackagePaths(unittest.TestCase):
 def test_actual_new_workspace_only_path_and_existing_refusal(self):
  with tempfile.TemporaryDirectory() as folder:
   project=Path(folder);(project/'build').mkdir();check_output(project,project/'build/new-package');(project/'build/existing').mkdir()
   with self.assertRaises(ValueError):check_output(project,project/'build/existing')
   with self.assertRaises(ValueError):check_output(project,project.parent/'outside')
 def test_mocked_build_or_ancestor_reparse_refused_without_junction_or_output(self):
  project=Path(__file__).absolute().parent;output=project/'build/never-created'
  for target in (project/'build',project,project.parent):
   def inspect(p):
    if p==output:raise FileNotFoundError
    return SimpleNamespace(st_mode=stat.S_IFDIR,st_file_attributes=0x400 if p==target else 0)
   with self.assertRaisesRegex(ValueError,'Reparse'):check_output(project,output,inspect)
  self.assertFalse(output.exists())
 def test_mocked_nondirectory_ancestor_and_existing_link_refused(self):
  project=Path(__file__).absolute().parent;output=project/'build/never-created'
  def inspect(p):
   if p==output:raise FileNotFoundError
   return SimpleNamespace(st_mode=stat.S_IFREG if p==project/'build' else stat.S_IFDIR,st_file_attributes=0)
  with self.assertRaises(ValueError):check_output(project,output,inspect)
if __name__=='__main__':unittest.main(verbosity=2)
