"""Filesystem refusal tests. No licensed master, world build or game required."""
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DLL=ROOT/'tools/WorldSliceBuilder/bin/Debug/net8.0/WorldSliceBuilder.dll'

class OutputSafety(unittest.TestCase):
    def test_expand_flag_preserves_input_and_occupied_output_refusals(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);master=root/'master';master.mkdir()
            input_file=master/'Fallout4.esm';input_file.write_bytes(b'input sentinel')
            occupied=root/'occupied';occupied.mkdir();sentinel=occupied/'keep.txt';sentinel.write_bytes(b'owner content')
            for mode in ('--expand','--natural'):
                for output in (input_file,master,master/'new-output',occupied):
                    result=subprocess.run(['dotnet',str(DLL),str(input_file),str(output),mode],capture_output=True,text=True)
                    self.assertEqual(result.returncode,2,result.stderr)
                    self.assertIn('Output must',result.stderr)
                    self.assertEqual(input_file.read_bytes(),b'input sentinel')
                    self.assertEqual(sentinel.read_bytes(),b'owner content')
                    self.assertFalse((master/'new-output').exists())

    def test_story_source_input_tree_is_never_an_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);master=root/'master';master.mkdir()
            input_file=master/'Fallout4.esm';input_file.write_bytes(b'input sentinel')
            story=root/'story';story.mkdir();template=story/'TheLastMeridian.esp';template.write_bytes(b'story sentinel')
            for output in (template,story,story/'new-output'):
                result=subprocess.run(['dotnet',str(DLL),str(input_file),str(output),'--story-source',str(template)],capture_output=True,text=True)
                self.assertEqual(result.returncode,2,result.stderr)
                self.assertIn('story-source input directory',result.stderr)
                self.assertEqual(template.read_bytes(),b'story sentinel')
                self.assertFalse((story/'new-output').exists())

    def test_refuses_input_file_input_tree_and_nonempty_output_without_touching_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);master=root/'master';master.mkdir()
            input_file=master/'Fallout4.esm';input_file.write_bytes(b'not a licensed master; refusal occurs before parsing')
            occupied=root/'occupied';occupied.mkdir();sentinel=occupied/'owner-file.txt';sentinel.write_bytes(b'preserve me')
            for output in (input_file,master,master/'new-output',occupied):
                with self.subTest(output=str(output)):
                    result=subprocess.run(['dotnet',str(DLL),str(input_file),str(output)],capture_output=True,text=True)
                    self.assertEqual(result.returncode,2,result.stderr)
                    self.assertIn('Output must',result.stderr)
                    self.assertEqual(sentinel.read_bytes(),b'preserve me')
                    self.assertEqual(input_file.read_bytes(),b'not a licensed master; refusal occurs before parsing')
                    self.assertFalse((master/'new-output').exists())
                    self.assertEqual(sorted(p.name for p in occupied.iterdir()),['owner-file.txt'])

if __name__=='__main__':unittest.main()
