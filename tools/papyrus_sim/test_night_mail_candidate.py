"""Candidate provenance, fail-closed mutations and honest byte selection.

Synthetic PEX bytes below test selection only, never Papyrus compilation.
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
import night_mail_story_candidate as candidate


def copy_source():
    target=Path(tempfile.mkdtemp(prefix='tlm-night-mail-source-'))
    m=json.loads(candidate.MANIFEST.read_text())
    names=set(m['sourceFilesTextSha256'])|set(m['frozenTextSha256'])|{'.gitattributes','tools/win/night-mail-story-candidate.json'}
    for name in names:
        (target/name).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/name,target/name)
    return target


class Candidate(unittest.TestCase):
    def test_current_source_verifies_and_baseline_is_really_frozen(self):
        self.assertEqual(candidate.problems(),[])
        m=json.loads(candidate.MANIFEST.read_text())
        for name in candidate.FROZEN:
            old=subprocess.run(['git','show',candidate.BASELINE+':'+name],cwd=ROOT,capture_output=True,check=True).stdout.decode('utf-8').replace('\r\n','\n')
            self.assertEqual((ROOT/name).read_text(),old,name)
            self.assertEqual(hashlib.sha256(old.encode()).hexdigest().upper(),m['baselineFrozenTextSha256'][name])
        old_attrs=subprocess.run(['git','show',candidate.BASELINE+':.gitattributes'],cwd=ROOT,capture_output=True,check=True).stdout.decode().replace('\r\n','\n')
        self.assertEqual(m['baselineAttributes'],old_attrs)
        self.assertIn((ROOT/'.gitattributes').read_text(),(old_attrs,old_attrs+candidate.ATTR_LINE))

    def test_every_changed_source_is_fresh_and_reviewed_selection_is_exact(self):
        m=json.loads(candidate.MANIFEST.read_text());old=json.loads((ROOT/'tools/win/greenwater-story-candidate.json').read_text())
        same,changed,new,gone=candidate.against(old['sourceTextSha256'],m['sourceTextSha256'])
        self.assertEqual((changed,new,gone),(['Act1Guide.psc','Act1Walk.psc'],['MQ02AQuest.psc','NightMailTalk.psc','NightMailWalk.psc'],[]))
        selected=m['runtimeSelection'];self.assertEqual((len(selected['reusedReviewedPex']),len(selected['freshlyCompiled'])),(17,9))
        for name in changed+new:self.assertIn(candidate.pex(name),selected['freshlyCompiled'])
        for name in ('GreenwaterTalk.pex','GreenwaterWalk.pex','MQ02BQuest.pex','MercyBriefing.pex'):
            self.assertIn(name,selected['freshlyCompiled'])
        self.assertTrue(all(v is None for v in m['measured'].values()))

    def test_each_source_family_is_guarded_before_output(self):
        for name in ('scripts/Source/User/TLM/NightMailWalk.psc','tools/PluginBuilder/SpecNightMail.cs',
                     'tools/WorldSliceBuilder/WorldNightMail.cs','tools/PluginBuilder/formkeys.txt',
                     'assets/incoming/act1/story/talk/tlm_mq02a.json','docs/design/NIGHT_MAIL_STORY_001_MAPPING.json',
                     'tools/win/Build-NightMail.ps1','tools/papyrus_sim/test_night_mail_scenes.py'):
            with self.subTest(file=name):
                r=copy_source();p=r/name;p.write_text(p.read_text()+'\n# mutation\n')
                self.assertIn('sourceFilesTextSha256 differs',' | '.join(candidate.problems(r)))

    def test_frozen_and_attributes_guards_do_not_accept_broad_exceptions(self):
        r=copy_source();p=r/'tools/win/Build-Greenwater.ps1';p.write_text(p.read_text()+'\n# mutation\n')
        self.assertIn('frozenTextSha256 differs',' | '.join(candidate.problems(r)))
        m=json.loads(candidate.MANIFEST.read_text());before=m['baselineAttributes']
        for attrs in (before+'* text eol=crlf\n',candidate.ATTR_LINE+before,before+candidate.ATTR_LINE*2,
                      before.replace('world-details-artifact.json text eol=lf','world-details-artifact.json text eol=crlf')):
            r=copy_source();(r/'.gitattributes').write_text(attrs)
            self.assertIn('frozen attributes altered',' | '.join(candidate.problems(r)))

    def test_source_membership_and_allocation_mutations(self):
        r=copy_source();(r/'scripts/Source/User/TLM/Extra.psc').write_text('Scriptname TLM:Extra\n')
        self.assertIn('exactly 26',' | '.join(candidate.problems(r)))
        for mutation in ('TLM_FAKE\n9999\n','TLM_FAKE\n2000\n'):
            r=copy_source();p=r/'tools/PluginBuilder/formkeys.txt';p.write_text(p.read_text()+mutation)
            self.assertIn('allocations are not a contiguous append',' | '.join(candidate.problems(r)))

    def bundle_inputs(self):
        r=Path(tempfile.mkdtemp(prefix='tlm-nm-measure-'));bundle=r/'bundle';scripts=bundle/'Scripts/TLM';scripts.mkdir(parents=True)
        compile_folder=r/'full-compile';compile_folder.mkdir();m=json.loads(candidate.MANIFEST.read_text())
        selected=m['runtimeSelection'];pins={}
        for name in list(selected['reusedReviewedPex'])+selected['freshlyCompiled']:
            reviewed=('reviewed '+name).encode();fresh=('fresh '+name).encode()
            (compile_folder/name).write_bytes(fresh)
            if name in selected['reusedReviewedPex']:
                pins[name]=hashlib.sha256(reviewed).hexdigest().upper();(scripts/name).write_bytes(reviewed)
            else:(scripts/name).write_bytes(fresh)
        m['runtimeSelection']['reusedReviewedPex']=pins;manifest=r/'synthetic-selection.json';manifest.write_text(json.dumps(m))
        for name in ('TheLastMeridian.esp','TLMWorldSlice.esp'):(bundle/name).write_bytes(b'not a plugin')
        return bundle,compile_folder,manifest

    def test_measurement_requires_reviewed_bytes_full_compile_and_fresh_identity(self):
        b,c,m=self.bundle_inputs();self.assertTrue(candidate.measure(b,c,m)['selectionOk'])
        self.assertFalse(candidate.measure(b,None,m)['selectionOk'])
        (b/'Scripts/TLM/Core.pex').write_bytes((c/'Core.pex').read_bytes())
        self.assertIn('reviewed byte pins mismatch',candidate.measure(b,c,m)['problems'])
        b,c,m=self.bundle_inputs();(b/'Scripts/TLM/NightMailWalk.pex').write_bytes(b'from other compile')
        self.assertIn('fresh bundle scripts differ from full compile',candidate.measure(b,c,m)['problems'])
        b,c,m=self.bundle_inputs();(c/'NightMailTalk.pex').unlink()
        self.assertIn('full fresh compile membership mismatch or absent',candidate.measure(b,c,m)['problems'])
        b,c,m=self.bundle_inputs();(b/'Scripts/TLM/Extra.pex').write_bytes(b'extra')
        self.assertIn('runtime membership mismatch',candidate.measure(b,c,m)['problems'])


if __name__=='__main__':unittest.main()
