"""Current combined source and raw-record boundary checks; no native proof."""
import json,shutil,struct,subprocess,sys,tempfile,unittest
from unittest.mock import patch
from pathlib import Path
from test_sim import ROOT
sys.path.insert(0,str(ROOT/'tools'))
import player_guidance_terrain_candidate as candidate
import run_composed_tests as dispatch
import player_guidance_terrain_layout as terrain_layout
import check_plugin_layout as layout
from test_red_hollow_environment_projection import edit_subrecord
from test_greenwater_world_clone import clone
from rh_terrain_projection import records,subs

def floor_input(raw,variant):
    rows,names=records(raw);data=dict(subs(rows[names['workshop_ShackMidFloor01B']][1]))
    wanted=(-96 if variant=='four-flags-floor-bounds' else -128,-128,-14,128,128,0)
    if struct.unpack('<6h',data[b'OBND'])!=wanted:raise AssertionError('Declared adverse floor bounds were sanitized')
    if variant=='four-flags-floor-no-model':
        if b'MODL' in data:raise AssertionError('Declared missing floor model was sanitized')
    elif data.get(b'MODL')!=b'Synthetic\\FourFlagsFloor.nif\0':raise AssertionError('Declared synthetic floor model was sanitized')

def legacy_master_prefix(old,now):
    before,bnames=records(old);after,anames=records(now)
    if not set(before)<=set(after):raise AssertionError('Legacy synthetic record identity removed or shifted')
    for key,row in before.items():
        current=after[key]
        if key[0]==b'TES4':
            assert [(k,v) for k,v in subs(row[1]) if k!=b'HEDR']==[(k,v) for k,v in subs(current[1]) if k!=b'HEDR'];continue
        assert row[0]==current[0] and row[2]==current[2]
        if key==bnames['workshop_ShackMidFloor01B']:
            a,b=dict(subs(row[1])),dict(subs(current[1]));a.pop(b'OBND');b.pop(b'OBND');b.pop(b'MODL')
            assert a==b;assert dict(subs(current[1]))[b'OBND']==struct.pack('<6h',-128,-128,-14,128,128,0)
            assert dict(subs(current[1]))[b'MODL']==b'Architecture\\Shacks\\ShackMidFloor01B.nif\0'
        elif row!=current:raise AssertionError('Legacy synthetic payload changed')
    new=set(after)-set(before)
    assert len(new)==4 and {n for n,k in anames.items() if k in new}=={'NpcBedWoodLay01Static','NPCCouchModernDomesticSit01Static','FenceWoodStr01','RockPileM01'}
    assert all(k[0]==b'STAT' for k in new)
    assert sorted(k[1] for k in new)==list(range(max(k[1] for k in before)+1,max(k[1] for k in before)+5))
    assert anames['defaultLightWarm01NS']==bnames['defaultLightWarm01NS']==(b'LIGH',0x85F)

def bad_constructor_master(variant):
    # Actual failed7b source is preserved as an ancestor, providing a concrete
    # regression rather than constructing an already-invalid surrogate.
    from composed_test_contexts import archive,execute,text_digest
    root=ROOT/'build/ci-fixture-repair/bad-constructor-7b'
    source=archive('7b43063dc9531f2762e778d80835cd2414cd0572')
    if not root.exists():
        for name,data in source.items():
            target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    else:
        for name,data in source.items():assert candidate.pin(root/name)==text_digest(data),name
    output=root/'build'/variant/'Fallout4.esm'
    execute(['dotnet','run','--project','tools/StandInMaster','--',output,variant],root,ROOT/'build/ci-fixture-repair'/('bad-constructor-'+variant+'.txt'))
    return output.read_bytes()

def copy_source():
    m=json.loads(candidate.MANIFEST.read_text());root=Path(tempfile.mkdtemp(prefix='tlm-composed-source-'))
    for n in set(m['sourceFilesTextSha256'])|{candidate.NAME}:
        p=root/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,p)
    return root
def repin(root):
    p=root/candidate.NAME;m=json.loads(p.read_text());m.update(candidate.describe(root));p.write_text(json.dumps(m))

class CurrentComposition(unittest.TestCase):
    def test_fixture_repair_keeps_all_runtime_and_production_builder_sources_exact(self):
        revision='7b43063dc9531f2762e778d80835cd2414cd0572'
        names=subprocess.check_output(['git','ls-tree','-r','--name-only',revision,'scripts/Source/User/TLM','tools/PluginBuilder','tools/WorldSliceBuilder'],cwd=ROOT,text=True).splitlines()
        self.assertTrue(names)
        from composed_test_contexts import text_digest
        for name in names:
            old=subprocess.check_output(['git','show',revision+':'+name],cwd=ROOT)
            self.assertEqual(candidate.pin(ROOT/name),text_digest(old),name)
        old=json.loads(subprocess.check_output(['git','show',revision+':tools/win/player-guidance-terrain-candidate.json'],cwd=ROOT))
        now=json.loads(candidate.MANIFEST.read_text())
        self.assertEqual(now['sourceTextSha256'],old['sourceTextSha256']);self.assertEqual(now['runtimeSelection'],old['runtimeSelection'])
    def test_default_master_preserves_all_legacy_ids_and_appends_only_four_new_statics(self):
        from composed_test_contexts import context,FD7
        old=context(FD7)/'build/composed-own/Fallout4.esm';now=ROOT/'build/composed/Fallout4.esm'
        legacy_master_prefix(old.read_bytes(),now.read_bytes())
        with self.assertRaises(AssertionError):legacy_master_prefix(old.read_bytes(),bad_constructor_master('default'))
    def test_declared_floor_variants_remain_actual_synthetic_missing_and_bad_width_inputs(self):
        from composed_test_contexts import execute
        for variant in ('four-flags-floor','four-flags-floor-bounds','four-flags-floor-no-model'):
            with self.subTest(variant=variant),tempfile.TemporaryDirectory(prefix='tlm-adverse-floor-') as t:
                master=Path(t)/'Fallout4.esm'
                execute(['dotnet','run','--project','tools/StandInMaster','--',master,variant],ROOT,ROOT/'build/ci-fixture-repair'/('floor-input-'+variant+'.txt'))
                floor_input(master.read_bytes(),variant)
                with self.assertRaisesRegex(AssertionError,'sanitized'):floor_input(bad_constructor_master(variant),variant)
    def test_historical_ordinary_fixtures_are_complete_and_reject_missing_json_or_borrowed_master(self):
        from composed_test_contexts import CONTEXT_DIGESTS,FD7,context,check_ordinary_fixture
        stamp=json.loads((ROOT/'build/composed/fixture-provenance.json').read_text())
        for revision in CONTEXT_DIGESTS:
            root=context(revision);master=root/'build/composed-own/Fallout4.esm';description=root/'build/sim/TheLastMeridian.json'
            self.assertEqual(check_ordinary_fixture(revision,master,description),stamp['historicalOrdinary'][revision])
        root=context(FD7);master=root/'build/composed-own/Fallout4.esm';description=root/'build/sim/TheLastMeridian.json'
        with self.assertRaisesRegex(AssertionError,'borrowed'):check_ordinary_fixture(FD7,ROOT/'build/composed/Fallout4.esm',description)
        original=Path.is_file;fired=[]
        def absent(p):
            if p==description:fired.append(True);return False
            return original(p)
        with patch.object(Path,'is_file',absent),self.assertRaisesRegex(AssertionError,'absent'):check_ordinary_fixture(FD7,master,description)
        self.assertEqual(fired,[True])
    def test_exact_modules_baseline_and_combined_runtime_selection(self):
        self.assertEqual(candidate.problems(),[])
        m=json.loads(candidate.MANIFEST.read_text());self.assertEqual(len(m['baselineFiles']),420)
        self.assertEqual((len(m['sourceTextSha256']),len(m['runtimeSelection']['reusedReviewedPex']),len(m['runtimeSelection']['freshlyCompiled'])),(34,16,18))
        self.assertTrue(all(v is None for v in m['measured'].values()))
    def test_repin_does_not_waive_baseline_module_or_integration_changes(self):
        for n in ('scripts/Source/User/TLM/MQ03Quest.psc','scripts/Source/User/TLM/RedHollowWalk.psc','tools/PluginBuilder/RedHollowTerrain.cs','tools/player_guidance_candidate.py','tools/rh_terrain_candidate.py','tools/WorldSliceBuilder/WorldRedHollow.cs','tools/StandInMaster/RhEnvironmentFixture.cs','tools/check_plugin_layout.py','.github/workflows/portable-checks.yml'):
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
