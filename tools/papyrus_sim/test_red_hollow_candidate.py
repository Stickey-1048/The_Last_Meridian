"""New composed source manifest and full-before-output mutation guards.
Dummy PEX in selection tests prove selection logic only; they are not compiled.
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from test_sim import ROOT
sys.path.insert(0,str(ROOT/'tools'))
import red_hollow_story_candidate as candidate


def source_copy():
    r=Path(tempfile.mkdtemp(prefix='tlm-rh-source-'));m=json.loads(candidate.MANIFEST.read_text())
    names=set(m['sourceFilesTextSha256'])|set(m['frozenTextSha256'])|{'.gitattributes','tools/win/red-hollow-story-candidate.json'}
    for name in names:
        (r/name).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,r/name)
    return r

class RedHollowCandidate(unittest.TestCase):
    def test_exact_source_with_frozen_prior_candidates(self):
        self.assertEqual(candidate.problems(),[])
        m=json.loads(candidate.MANIFEST.read_text());self.assertEqual(m['scripts'],29)
        for name in candidate.FROZEN:
            old=subprocess.run(['git','show',candidate.BASELINE+':'+name],cwd=ROOT,capture_output=True,check=True).stdout.decode().replace('\r\n','\n')
            self.assertEqual((ROOT/name).read_text(),old,name)
        self.assertTrue(all(v is None for v in m['measured'].values()))
        self.assertEqual((len(m['runtimeSelection']['reusedReviewedPex']),len(m['runtimeSelection']['freshlyCompiled'])),(17,12))
    def test_every_consequential_source_family_is_guarded(self):
        for name in ('scripts/Source/User/TLM/MQ02CQuest.psc','scripts/Source/User/TLM/RedHollowWalk.psc','tools/PluginBuilder/SpecRedHollow.cs','tools/WorldSliceBuilder/WorldRedHollow.cs','tools/papyrus_natives.json','docs/design/RED_HOLLOW_STORY_001_MAPPING.json','docs/design/ACT1_CREATIVE_DECISIONS_2026-11-16.md','tools/win/Build-RedHollow.ps1','tools/papyrus_sim/test_red_hollow.py'):
            with self.subTest(source=name):
                r=source_copy();p=r/name;p.write_text(p.read_text()+'\nmutation\n')
                self.assertIn('sourceFilesTextSha256 differs',' | '.join(candidate.problems(r)))
    def test_frozen_verifier_and_exact_attributes_allowance(self):
        r=source_copy();p=r/'tools/night_mail_story_candidate.py';p.write_text(p.read_text()+'\n# mutation\n')
        self.assertIn('frozenTextSha256 differs',' | '.join(candidate.problems(r)))
        m=json.loads(candidate.MANIFEST.read_text());before=m['baselineAttributes']
        for text in (before+'* text eol=crlf\n',before+candidate.ATTR_LINE*2,candidate.ATTR_LINE+before,before.replace('world-details-artifact.json text eol=lf','world-details-artifact.json text eol=crlf')):
            r=source_copy();(r/'.gitattributes').write_text(text)
            self.assertIn('frozen attributes altered',' | '.join(candidate.problems(r)))
        for text in (before,before+candidate.ATTR_LINE):
            r=source_copy();(r/'.gitattributes').write_text(text);self.assertEqual(candidate.problems(r),[])
    def test_append_only_allocation_and_membership_are_not_waived(self):
        for extra in ('TLM_BAD\n9999\n','TLM_BAD\n2000\n'):
            r=source_copy();p=r/'tools/PluginBuilder/formkeys.txt';p.write_text(p.read_text()+extra)
            self.assertIn('contiguous append',' | '.join(candidate.problems(r)))
        r=source_copy();(r/'scripts/Source/User/TLM/Extra.psc').write_text('Scriptname TLM:Extra\n')
        self.assertIn('exactly 29',' | '.join(candidate.problems(r)))
    def test_full_fresh_compile_is_required_and_reviewed_bytes_are_never_replaced(self):
        root=Path(tempfile.mkdtemp(prefix='tlm-rh-dummy-'));bundle=root/'bundle';scripts=bundle/'Scripts/TLM';scripts.mkdir(parents=True);compile=root/'compile';compile.mkdir()
        m=json.loads(candidate.MANIFEST.read_text());pins={}
        for name in list(m['runtimeSelection']['reusedReviewedPex'])+m['runtimeSelection']['freshlyCompiled']:
            fresh=('synthetic fresh '+name).encode();reviewed=('synthetic reviewed '+name).encode();(compile/name).write_bytes(fresh)
            if name in m['runtimeSelection']['reusedReviewedPex']:pins[name]=hashlib.sha256(reviewed).hexdigest().upper();(scripts/name).write_bytes(reviewed)
            else:(scripts/name).write_bytes(fresh)
        m['runtimeSelection']['reusedReviewedPex']=pins;manifest=root/'dummy.json';manifest.write_text(json.dumps(m))
        for n in ('TheLastMeridian.esp','TLMWorldSlice.esp'):(bundle/n).write_bytes(b'not a plugin')
        self.assertTrue(candidate.measure(bundle,compile,manifest)['selectionOk']);self.assertFalse(candidate.measure(bundle,None,manifest)['selectionOk'])
        (scripts/'Core.pex').write_bytes((compile/'Core.pex').read_bytes());self.assertIn('reviewed byte pins mismatch',candidate.measure(bundle,compile,manifest)['problems'])
        (scripts/'Core.pex').write_bytes(b'synthetic reviewed Core.pex')
        (scripts/'RedHollowWalk.pex').write_bytes(b'other source');self.assertIn('fresh bundle scripts differ from full compile',candidate.measure(bundle,compile,manifest)['problems'])
        (compile/'MQ02CQuest.pex').unlink();self.assertIn('full fresh compile membership mismatch or absent',candidate.measure(bundle,compile,manifest)['problems'])
