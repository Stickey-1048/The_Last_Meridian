"""Current combined source and raw-record boundary checks; no native proof."""
import json,shutil,struct,subprocess,sys,tempfile,unittest
from pathlib import Path
from test_sim import ROOT
sys.path.insert(0,str(ROOT/'tools'))
import player_guidance_terrain_candidate as candidate
import run_composed_tests as dispatch
import player_guidance_terrain_layout as terrain_layout
import check_plugin_layout as layout
from test_red_hollow_environment_projection import edit_subrecord
from test_greenwater_world_clone import clone

def copy_source():
    m=json.loads(candidate.MANIFEST.read_text());root=Path(tempfile.mkdtemp(prefix='tlm-composed-source-'))
    for n in set(m['sourceFilesTextSha256'])|{candidate.NAME}:
        p=root/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,p)
    return root
def repin(root):
    p=root/candidate.NAME;m=json.loads(p.read_text());m.update(candidate.describe(root));p.write_text(json.dumps(m))

class CurrentComposition(unittest.TestCase):
    def test_exact_modules_baseline_and_combined_runtime_selection(self):
        self.assertEqual(candidate.problems(),[])
        m=json.loads(candidate.MANIFEST.read_text());self.assertEqual(len(m['baselineFiles']),420)
        self.assertEqual((len(m['sourceTextSha256']),len(m['runtimeSelection']['reusedReviewedPex']),len(m['runtimeSelection']['freshlyCompiled'])),(34,16,18))
        self.assertTrue(all(v is None for v in m['measured'].values()))
    def test_repin_does_not_waive_baseline_module_or_integration_changes(self):
        for n in ('scripts/Source/User/TLM/MQ03Quest.psc','scripts/Source/User/TLM/RedHollowWalk.psc','tools/PluginBuilder/RedHollowTerrain.cs','tools/player_guidance_candidate.py','tools/rh_terrain_candidate.py','tools/WorldSliceBuilder/WorldRedHollow.cs','tools/check_plugin_layout.py','.github/workflows/portable-checks.yml'):
            with self.subTest(n=n):
                root=copy_source();p=root/n;p.write_text(p.read_text(encoding='utf-8')+'\n# unapproved mutation\n',encoding='utf-8');repin(root)
                self.assertIn('Exact accepted/composed source altered: '+n,candidate.problems(root))
    def test_added_workflow_is_not_an_implicit_composition_input(self):
        root=copy_source();(root/'.github/workflows/extra.yml').write_text('name: unapproved\n');repin(root)
        self.assertIn('Exact composed source membership altered',candidate.problems(root))
    def test_dispatch_accounts_for_every_module_and_rejects_unmapped_source(self):
        ids=[m+'.Example.test_accounted' for m in dispatch.MODULES]+list(dispatch.EXACT)
        groups=dispatch.classify(ids);self.assertEqual(sum(map(len,groups.values())),len(ids))
        with self.assertRaisesRegex(AssertionError,'Unaccounted'):dispatch.classify(ids+['test_new_unreviewed.Example.test_not_hidden'])
        with self.assertRaisesRegex(AssertionError,'removed or renamed'):dispatch.classify([n for n in ids if n not in dispatch.EXACT])
        with self.assertRaisesRegex(AssertionError,'Duplicate'):dispatch.classify(ids+[ids[0]])
    def test_current_terrain_layout_requires_exact_refs_heights_and_normals(self):
        p=ROOT/'build/terrain-002/projection/TheLastMeridian.esp';raw=p.read_bytes();described=layout.placed_from_json(p.with_suffix('.json'))
        self.assertEqual(layout.check_cells(raw,described)[0],[])
        for name,sub,change in [('TLM_REF_RHE_T2_ReleasedWaitingRoof','EDID',lambda b,p,n:b.__setitem__(p,ord('X'))),('TLM_REF_RHE_T2_ReleasedWaitingRoof','EDID',lambda b,p,n:b.__setitem__(p+len('TLM_REF_RHE_T2_'),ord('Z')))]:
            bad=edit_subrecord(raw,'REFR',name,sub,change)
            self.assertTrue(any('exact72reference' in n for n in layout.check_cells(bad,described)[0]))
        # LAND has no EDID: directly mutate its two exact accepted arrays.
        for wanted in ('VHGT','VNML'):
            bad=bytearray(raw);fired=False
            for kind,off,size,fid,flags in layout.records(bad,0,len(bad)):
                if kind!='LAND':continue
                pos=off
                while pos<off+size:
                    sub=bad[pos:pos+4].decode();n=struct.unpack_from('<H',bad,pos+4)[0];pos+=6
                    if sub==wanted:bad[pos+8]^=1;fired=True;break
                    pos+=n
            self.assertTrue(fired);self.assertTrue(any('terrain' in n and 'bytes mismatch' in n for n in layout.check_cells(bytes(bad),described)[0]))
        # Historical flat profile remains an actual complete flat source.
        from composed_test_contexts import context,FD7
        old=context(FD7)/'build/flat-layout/TheLastMeridian.esp'
        if not old.exists():
            from composed_test_contexts import build
            build(context(FD7),ROOT/'build/composed/Fallout4.esm',old.parent,'flat-layout-negative')
        flat=old.read_bytes();self.assertEqual(terrain_layout.context(flat),(False,[]));self.assertEqual(layout.check_cells(flat,layout.placed_from_json(old.with_suffix('.json')))[0],[])
    def test_current_clone_keeps_original101_aliases_and_appends_only_scriptfilled_report_target(self):
        got=clone();self.assertEqual(got.returncode,0,got.stdout+got.stderr);out=json.loads(got.stdout);aliases=out['redHollow']['aliases']
        self.assertEqual(len(aliases),102);self.assertEqual([a['id'] for a in aliases],list(range(102)))
        self.assertEqual((aliases[-1]['name'],aliases[-1]['reference']),('GuideSheriff','script-filled'))
        self.assertEqual({a['name'] for a in aliases if a['owner']=='TLMWorldSlice.esp'},{'MercyTravel','MercyReturn'})
        self.assertEqual(sum(a['owner']=='TheLastMeridian.esp' for a in aliases),97)
        for damage in ('report-guide-forced','report-guide-alias-id','report-guide-binding-removed','report-guide-binding-wrong','report-guide-protected'):
            with self.subTest(damage=damage):
                bad=clone(damage);self.assertEqual(bad.returncode,1,bad.stdout+bad.stderr);self.assertIn('REFUSED',bad.stderr)
    def test_guidance_quest_name_is_natural_and_legacy_name_stays_exact(self):
        from test_greenwater_world_clone import DLL,stand_in_story
        from composed_test_contexts import context,FD7
        from rh_terrain_projection import records,subs
        legacy=context(FD7)/'build/flat-layout/TheLastMeridian.esp'
        for source,expected in ((stand_in_story(),'Red Hollow: directions'),(legacy,'The Last Meridian - exterior-linked Red Hollow (development)')):
            with self.subTest(source=source),tempfile.TemporaryDirectory(prefix='tlm-clone-name-') as t:
                output=Path(t)/'world';result=subprocess.run(['dotnet',str(DLL),'--story-clone-check',str(source),str(output)],cwd=ROOT,capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                rows,names=records((output/'TLMWorldSlice.esp').read_bytes())
                self.assertEqual(dict(subs(rows[names['TLM_WS_RH']][1]))[b'FULL'].rstrip(b'\0').decode(),expected)

if __name__=='__main__':unittest.main()
