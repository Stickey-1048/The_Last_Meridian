"""Exact new source candidate; historical candidates are tested on actual fd7 exports."""
import hashlib,io,json,shutil,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
from test_sim import ROOT,PLUGIN
from source_snapshot import snapshot
sys.path.insert(0,str(ROOT/'tools'))
import player_guidance_candidate as candidate

def copy_source():
    m=json.loads(candidate.MANIFEST.read_text(encoding='utf-8'));root=Path(tempfile.mkdtemp(prefix='tlm-guidance-'))
    for name in set(m['baselineFiles'])|set(m['sourceFilesTextSha256'])|{'tools/win/player-guidance-candidate.json'}:
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
    return root

def repin(root):
    p=root/'tools/win/player-guidance-candidate.json';m=json.loads(p.read_text(encoding='utf-8'));m.update(candidate.describe(root));p.write_text(json.dumps(m),encoding='utf-8')

class Candidate(unittest.TestCase):
    def test_actual_full_fd7_archive_and_exact_current_source(self):
        self.assertEqual(candidate.problems(),[])
        with zipfile.ZipFile(io.BytesIO(subprocess.check_output(['git','archive','--format=zip',candidate.BASELINE],cwd=ROOT))) as z:
            names=[n for n in z.namelist() if not n.endswith('/')];m=json.loads(candidate.MANIFEST.read_text(encoding='utf-8'))
            self.assertEqual(set(names),set(m['baselineFiles']))
            for n in names:
                data=z.read(n)
                try:data=data.decode('utf-8').replace('\r\n','\n').replace('\r','\n').encode()
                except UnicodeDecodeError:pass
                self.assertEqual(hashlib.sha256(data).hexdigest().upper(),m['baselineFiles'][n],n)
        self.assertEqual(set(candidate.APPROVED),{'scripts/Source/User/TLM/MessageStageAlias.psc','scripts/Source/User/TLM/RedHollowWalk.psc','tools/PluginBuilder/Spec.cs','tools/PluginBuilder/SpecRedHollow.cs'})
    def test_old_case_verifier_passes_only_on_actual_frozen_fd7_not_changed_runtime(self):
        frozen=snapshot(candidate.BASELINE)
        got=subprocess.run([sys.executable,'-B','tools/case_read_access_candidate.py','verify'],cwd=frozen,capture_output=True,text=True)
        self.assertEqual(got.returncode,0,got.stdout+got.stderr)
        got=subprocess.run([sys.executable,'-B','tools/case_read_access_candidate.py','verify'],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(got.returncode,1);self.assertIn('MessageStageAlias.psc',got.stdout)
    def test_repin_cannot_waive_unrelated_or_reviewed_guidance_change(self):
        for name in ('scripts/Source/User/TLM/MQ03Quest.psc','scripts/Source/User/TLM/MQ02CQuest.psc','tools/PluginBuilder/RedHollowEnvironment.cs','tools/PluginBuilder/formkeys.txt','.github/workflows/portable-checks.yml','tools/case_read_access_candidate.py','tools/win/case-read-access-candidate.json','scripts/Source/User/TLM/RedHollowWalk.psc'):
            with self.subTest(name=name):
                root=copy_source();p=root/name;p.write_text(p.read_text(encoding='utf-8')+'\n# unapproved mutation\n',encoding='utf-8');repin(root)
                self.assertIn('unapproved source delta: '+name,candidate.problems(root))
    def test_baseline_membership_cannot_be_replaced_and_native_claim_rejected(self):
        root=copy_source();p=root/'tools/win/player-guidance-candidate.json';m=json.loads(p.read_text(encoding='utf-8'))
        m['baselineFiles']['tools/PluginBuilder/formkeys.txt']='0'*64;m['measured']['nativeAcceptance']=True;p.write_text(json.dumps(m),encoding='utf-8')
        found=candidate.problems(root);self.assertIn('full accepted fd7 baseline membership/pins altered',found);self.assertIn('source-only candidate cannot claim artifact/native measurements',found)
    def test_existing34_runtime_sources_require_new_message_alias_compile(self):
        m=json.loads(candidate.MANIFEST.read_text(encoding='utf-8'));s=m['runtimeSelection']
        self.assertEqual((len(s['reusedReviewedPex']),len(s['freshlyCompiled'])),(16,18))
        self.assertNotIn('MessageStageAlias.pex',s['reusedReviewedPex']);self.assertIn('MessageStageAlias.pex',s['freshlyCompiled']);self.assertIn('RedHollowWalk.pex',s['freshlyCompiled'])
        self.assertTrue(all(v is None for v in m['measured'].values()))
    def test_new_workflow_or_runtime_file_cannot_enter_through_repin(self):
        root=copy_source();(root/'.github/workflows/extra.yml').write_text('name: unrelated\n',encoding='utf-8');repin(root)
        self.assertIn('unapproved GitHub file membership',candidate.problems(root))
        root=copy_source();(root/'scripts/Source/User/TLM/Extra.psc').write_text('Scriptname TLM:Extra\n',encoding='utf-8');repin(root)
        found=candidate.problems(root);self.assertIn('exact existing34scripts required',found);self.assertIn('unapproved source membership',found)
    def test_no_new_ids_or_placed_geometry_and_unrelated_record_projection_preserved(self):
        frozen=snapshot(candidate.BASELINE);out=frozen/'build/sim/TheLastMeridian.json'
        if not out.is_file():
            for args in (['tools/StandInMaster','build/standin/Fallout4.esm','default'],['tools/PluginBuilder','--out','build/sim','--fallout4-esm','build/standin/Fallout4.esm']):
                got=subprocess.run(['dotnet','run','--project',args[0],'--']+args[1:],cwd=frozen,capture_output=True,text=True)
                self.assertEqual(got.returncode,0,got.stdout+got.stderr)
        old=json.loads(out.read_text());now=json.loads(PLUGIN.read_text())
        for key in ('Masters','HeaderVersion','LowestFormId','Cells','Npcs'):self.assertEqual(old[key],now[key],key)
        self.assertEqual(len(old['Messages']),len(now['Messages']))
        for a,b in zip(old['Messages'],now['Messages']):
            if a['EditorId'] in ('TLM_MSG_RH_Status','TLM_MSG_RH_LabelCage','TLM_MSG_RH_LabelNine'):a=dict(a,Text=b['Text'])
            self.assertEqual(a,b,a['EditorId'])
        changed={'TLM_ACTI_RH_MercyTravel','TLM_ACTI_RH_MouthOpen','TLM_ACTI_RH_BelowControl'}
        self.assertEqual(len(old['Records']),len(now['Records']))
        for a,b in zip(old['Records'],now['Records']):
            if a['EditorId'] in changed:a=dict(a,Name=b['Name'])
            self.assertEqual(a,b,a['EditorId'])
        self.assertEqual([q['EditorId'] for q in old['Quests']],[q['EditorId'] for q in now['Quests']])
        for a,b in zip(old['Quests'],now['Quests']):
            if a['EditorId']=='TLM_RH':
                self.assertEqual(len(b['Objectives']),11)
                targets={5:'MercyTravel',10:'ToMouth',20:'CageControl',30:'Roster',40:'BelowControl',50:'Resolve',55:'BreakControl',60:'Exit',70:'Condemned',80:'FromGallery',85:'BelowControl'}
                for obj in b['Objectives']:
                    self.assertEqual(obj['TargetAliases'],[next(x['Id'] for x in b['Aliases'] if x['Name']==targets[obj['Index']])])
                a=dict(a,Name=b['Name'],Type=b['Type'],Objectives=b['Objectives'])
            elif a['EditorId']=='TLM_SQ01':
                b=json.loads(json.dumps(b))
                for bl in b['Aliases']:
                    if bl['Name'] in ('Stove','NoticeBoard'):
                        props=bl['Scripts'][0]['Props'];resolved=[p for p in props if p['Name']=='ResolvedText']
                        self.assertEqual(len(resolved),1);self.assertEqual(resolved[0]['Kind'],'string[]');self.assertEqual(len(resolved[0]['Value']),1)
                        bl['Scripts'][0]['Props']=[p for p in props if p['Name']!='ResolvedText']
            self.assertEqual(a,b,a['EditorId'])

if __name__=='__main__':unittest.main()
