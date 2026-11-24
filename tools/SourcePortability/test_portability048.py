"""Focused source lint/CLI regressions; actual projection explicitly supplied, never fabricated."""
from pathlib import Path
import ast,json,re,sys,subprocess,tempfile,unittest,argparse
ROOT=Path(__file__).resolve().parents[2]
CHECK=ROOT/'tools/check_consistency.py'
NATIVES=json.loads((ROOT/'tools/papyrus_natives.json').read_text())['natives']

def source_api():
    tree=ast.parse(CHECK.read_text())
    definitions=[node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.ClassDef))]
    ns={'Path':Path,'re':re,'problem':lambda msg:None,'argparse':argparse,'ROOT':ROOT}
    exec(compile(ast.Module(body=definitions,type_ignores=[]),str(CHECK),'exec'),ns)
    return ns
API=source_api()

def real_scripts():
    return {s.name:s for s in (API['Script'](p) for p in sorted((ROOT/'scripts/Source/User/TLM').glob('*.psc')))}

def lint(script,scripts):
    errors=[];API['lint_source'](script,scripts,NATIVES,errors.append);return errors

class Checks(unittest.TestCase):
    def test_actual43_sources_and_exact_metadata_additions(self):
        scripts=real_scripts()
        self.assertEqual(len(scripts),43)
        self.assertEqual({s.name:lint(s,scripts)for s in scripts.values()if lint(s,scripts)}, {})
        old=json.loads(subprocess.check_output(['git','-C',str(ROOT),'show','83af5fc:tools/papyrus_natives.json']))['natives']
        expected={'IsActivationBlocked','SetOverrideVoiceType','GetVoiceType','FadeOutGame','Play','StopInstance','RegisterForRemoteEvent','UnregisterForRemoteEvent','GetAlias','CompleteQuest','Clear','Stop','Actor.OnPlayerLoadGame'}
        self.assertEqual(set(NATIVES)-set(old),expected)
        self.assertTrue(all(NATIVES[k]==v for k,v in old.items()))
        self.assertEqual(NATIVES['OnPlayerLoadGame'][0]['max_args'],0)
        self.assertEqual(NATIVES['Actor.OnPlayerLoadGame'][0]['params'],['Actor akSender'])
    def test_real_receivers_wrong_arity_refused_despite_other_classes(self):
        for caller,good,bad,want in [('TLM:BlackLedgerWalk','Road().Initialize(actual)','Road().Initialize()','takes 1-1'),('TLM:FourFlagsWalk','Road().FinishEncounter(courier,original,player,holder,foundDead,capturedEpoch)','Road().FinishEncounter(courier)','takes 6-6')]:
            scripts=real_scripts();script=scripts[caller];fired=sum(good in line for line in script.lines);self.assertEqual(fired,1)
            script.lines=[line.replace(good,bad)for line in script.lines]
            self.assertTrue(any(want in error for error in lint(script,scripts)))
    def fixture_scripts(self,folder):
        texts={'Owner':'''Scriptname TLM:Owner extends Quest
TLM:Target Property typed Auto
TLM:Target Function Road()
 Return typed
EndFunction
Function Exercise(TLM:Target parameter)
 TLM:Target local = typed
 local.Check(1)
 parameter.Check(1)
 typed.Check(1)
 Road().Check(1)
 Self.Check()
EndFunction
Function Check()
EndFunction
''','Target':'''Scriptname TLM:Target extends Quest
Function Check(int needed)
EndFunction
''','Unrelated':'''Scriptname TLM:Unrelated extends Quest
Function Check(int first,int second)
EndFunction
'''}
        result={}
        for name,text in texts.items():
            path=Path(folder)/(name+'.psc');path.write_text(text);s=API['Script'](path);result[s.name]=s
        return result
    def test_typed_properties_parameters_locals_returns_and_self(self):
        with tempfile.TemporaryDirectory()as tmp:
            scripts=self.fixture_scripts(tmp);s=scripts['TLM:Owner'];self.assertEqual(lint(s,scripts),[])
            s.lines=[line.replace('local.Check(1)','local.Check()')for line in s.lines]
            self.assertTrue(any('takes 1-1'in e for e in lint(s,scripts)))
    def test_unresolved_receiver_does_not_borrow_global_signature(self):
        with tempfile.TemporaryDirectory()as tmp:
            scripts=self.fixture_scripts(tmp);s=scripts['TLM:Owner'];s.lines=[line.replace('typed.Check(1)','unknown.Check(1)')for line in s.lines]
            self.assertTrue(any('unresolved/ambiguous receiver unknown'in e for e in lint(s,scripts)))
            scripts['tlm:TARGET']=scripts['TLM:Target']
            self.assertTrue(any('unresolved/ambiguous receiver Road()'in e for e in lint(s,scripts)))
    def test_actual_remote_handler_wrong_sender_and_count_refused(self):
        for file in ('TLM:Act1Walk','TLM:OpeningPrologue'):
            scripts=real_scripts();s=scripts[file];s.lines=[line.replace('Event Actor.OnPlayerLoadGame(Actor akSender)','Event Actor.OnPlayerLoadGame(ObjectReference akSender)')for line in s.lines]
            self.assertTrue(any('requires Actor sender'in e for e in lint(s,scripts)))
            with tempfile.TemporaryDirectory()as tmp:
                path=Path(tmp)/s.path.name
                path.write_text(scripts[file].path.read_text().replace('Event Actor.OnPlayerLoadGame(Actor akSender)','Event Actor.OnPlayerLoadGame(Actor akSender, Actor extra)'))
                bad=API['Script'](path)
                self.assertTrue(any('declared with 2 parameter'in e for e in lint(bad,scripts)))
    def test_native_wrong_count_still_refused(self):
        scripts=real_scripts();s=scripts['TLM:OpeningPrologue'];matches=[n for n,l in enumerate(s.lines)if 'Sound.StopInstance('in l];self.assertTrue(matches)
        n=matches[0];s.lines[n]=re.sub(r'Sound.StopInstance\([^)]*\)','Sound.StopInstance()',s.lines[n])
        self.assertTrue(any('StopInstance() called with 0'in e for e in lint(s,scripts)))
    def run_cli(self,*args):
        return subprocess.run([sys.executable,'-B',str(CHECK),*map(str,args)],capture_output=True,text=True)
    def test_actual_projection_cli_passes_without_copy_or_emission(self):
        result=self.run_cli('--plugin-json',ACTUAL_PROJECTION);self.assertEqual(result.returncode,0,result.stdout+result.stderr);self.assertIn('18 quests',result.stdout)
    def test_missing_default_and_invalid_inputs_fail(self):
        self.assertFalse((ROOT/'build/TheLastMeridian.json').exists())
        result=self.run_cli();self.assertEqual(result.returncode,1);self.assertIn('not found',result.stdout)
        with tempfile.TemporaryDirectory()as tmp:
            for label,data in [('syntax','{'),('empty',json.dumps({'Quests':[],'Messages':[]})),('nested',json.dumps({'Quests':[{'EditorId':'broken'}],'Messages':[{'EditorId':'broken','Buttons':[]}]}))]:
                p=Path(tmp)/(label+'.json');p.write_text(data);result=self.run_cli('--plugin-json',p);self.assertEqual(result.returncode,1,result.stderr);self.assertIn('Invalid plugin projection',result.stdout);self.assertNotIn('Traceback',result.stderr)
            result=self.run_cli('--plugin-json',Path(tmp)/'absent.json');self.assertEqual(result.returncode,1);self.assertIn('not found',result.stdout)

if __name__=='__main__':
    args=argparse.ArgumentParser();args.add_argument('--actual-plugin-json',type=Path,required=True);known,rest=args.parse_known_args();ACTUAL_PROJECTION=known.actual_plugin_json.resolve();assert ACTUAL_PROJECTION.is_file()
    unittest.main(argv=[sys.argv[0],*rest],verbosity=2)
