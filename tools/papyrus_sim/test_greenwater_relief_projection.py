"""Exact technical record/alias/strict-food projection; synthetic fixtures only."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from test_sim import ROOT,PLUGIN
from test_greenwater_world_clone import clone
from source_snapshot import snapshot,built_red_hollow,RED_HOLLOW


class ReliefProjection(unittest.TestCase):
    def test_missing_or_substituted_controls_and_bad_model_bounds_are_refused(self):
        for damage in ('relief-ledger-missing','relief-control-substituted','relief-model-missing','relief-model-oversized','relief-ledger-binding-wrong'):
            with self.subTest(damage=damage):
                got=clone(damage);self.assertEqual(got.returncode,1,got.stdout+got.stderr)
                self.assertIn('REFUSED',got.stderr)

    def test_two_new_control_sites_preserve_every_old_action_and_safe_approach_direction(self):
        got=clone();self.assertEqual(got.returncode,0,got.stdout+got.stderr);world=json.loads(got.stdout)
        controls={a['name']:a for a in world['greenwater']['aliases'][-2:]}
        self.assertEqual({n:[a['x'],a['y'],a['z']] for n,a in controls.items()},{'ReliefStores':[2180,850,12],'ReliefSupply':[3050,3620,12]})
        import math
        for new in controls.values():
            for old in world['greenwater']['aliases'][:31]:
                self.assertGreaterEqual(math.hypot(new['x']-old['x'],new['y']-old['y']),192,old['name'])
        program=(ROOT/'tools/WorldSliceBuilder/Program.cs').read_text()
        self.assertIn('startX=name=="ReliefStores"?2400:3050,startY=name=="ReliefStores"?850:3558',program)
        # Known preserved yard fence atY3456 has actual audited half-depth2;
        # the approach begins on the existing rear street, not inside the yard.
        self.assertGreaterEqual(3558-(3456+2),96)
        self.assertGreater(program.index('WorldStory.CompleteReliefControls'),program.index('ShelterDetails.Add(master,Put)'))

    def setUp(self):
        self.d=json.loads(PLUGIN.read_text())
        self.m=json.loads((ROOT/'docs/design/GREENWATER_CLARITY_WINTER_RELIEF_MAPPING.json').read_text())
        self.msg={m['EditorId']:m for m in self.d['Messages']}
        self.q=next(q for q in self.d['Quests'] if q['EditorId']=='TLM_GW_Relief')
    def test_every_new_ui_record_is_technical_mapped_bound_and_bounded(self):
        mapped={r['record']:r for r in self.m['ui']}
        self.assertEqual(set(mapped),{n for n in self.msg if n.startswith('TLM_MSG_GR_')})
        self.assertEqual(len(mapped),23)
        props={p['Name']:p for p in self.q['Scripts'][0]['Props']}
        for n,row in mapped.items():
            m=self.msg[n];self.assertEqual(m['Text'],row['text']);self.assertIsNone(m['Title'])
            self.assertTrue(m['Text'].startswith('['));self.assertTrue(m['Box']);self.assertLessEqual(len(m['Text']),240,n)
            self.assertEqual([b['Text'] for b in m['Buttons']],row['buttons'])
            self.assertLessEqual(len(m['Buttons']),4)
            self.assertTrue(row['shownWhen'])
            self.assertEqual(props[row['property']]['Target'],n)
            for b in m['Buttons']:self.assertLessEqual(len(b['Text']),48,n);self.assertFalse(b['Conditions'])
    def test_ledger_has_one_owner_with_real_player_load_and_strict_food_binding(self):
        self.assertEqual([s['Name'] for s in self.q['Scripts']],['TLM:GreenwaterRelief'])
        self.assertEqual([(a['Id'],a['Name'],a['Fill']) for a in self.q['Aliases'][:2]],[(0,'Stores',None),(1,'Supply',None)])
        player=self.q['Aliases'][2];self.assertEqual(player['Name'],'Player');self.assertTrue(player['Fill'].startswith('forced '))
        self.assertEqual(player['Scripts'][0]['Name'],'TLM:GreenwaterTalk')
        props={p['Name']:p for p in self.q['Scripts'][0]['Props']}
        self.assertEqual(props['Alias_Stores']['Target'],'TLM_GW_Relief');self.assertEqual(props['Alias_Stores']['Alias'],0)
        vanilla=json.loads((PLUGIN.parent/'TheLastMeridian.vanilla.json').read_text())
        corn=next(x for x in vanilla if x['EditorId']=='Corn' and x['Kind']=='Ingestible')
        self.assertEqual(props['Corn']['Target'],corn['FormKey'])
        river=next(x for x in self.d['Quests'] if x['EditorId']=='TLM_MQ02B')
        meal=next(p for p in river['Scripts'][0]['Props'] if p['Name']=='Meal')
        self.assertNotEqual(props['Corn']['Target'],meal['Target'],'synthetic duplicate display-name food is not the strict Corn EDID')
        got=clone();self.assertEqual(got.returncode,0,got.stdout+got.stderr);world=json.loads(got.stdout)
        self.assertNotIn('TLM_GW_Relief',world['quests'])
        self.assertEqual(world['greenwater']['forms']['TLM_Relief'],'TLM_GW_Relief in TheLastMeridian.esp')
        self.assertEqual([a['name'] for a in world['greenwater']['aliases'][-2:]],['ReliefStores','ReliefSupply'])
    def test_all_new_ids_are_a_precise_contiguous_append(self):
        old=subprocess.run(['git','show',RED_HOLLOW+':tools/PluginBuilder/formkeys.txt'],cwd=ROOT,capture_output=True,check=True).stdout.decode().splitlines()
        now=(ROOT/'tools/PluginBuilder/formkeys.txt').read_text().splitlines();self.assertEqual(now[:len(old)],old)
        rest=now[len(old):];self.assertEqual(len(rest),78)
        actual=[{'record':rest[i],'id':int(rest[i+1])} for i in range(0,len(rest),2)]
        self.assertEqual(actual,self.m['allocation']['append'])
        self.assertEqual([r['id'] for r in actual],list(range(int(old[-1])+1,int(old[-1])+40)))
        base={'TLM_GW_Relief','TLM_ACTI_GW_ReliefStores','TLM_ACTI_Mercy_ReliefSupply','TLM_REF_GW_ReliefStores','TLM_REF_GW_ReliefSupply'}
        clarity={'ArrivalBrief','Goal','Stakes','ConfirmShare','NoteSharePaid','LabelShareHeld','LabelLandingLayout','CardStakes','ConfirmHang','ConfirmCustody','ConfirmRelease'}
        self.assertEqual({r['record'] for r in actual},base|{'TLM_MSG_GW_'+n for n in clarity}|{r['record'] for r in self.m['ui']})
    def test_cloned_old_story_payloads_and_ids_remain_exact(self):
        oldroot=snapshot(RED_HOLLOW);oldplugin=built_red_hollow().with_suffix('.esp');out=Path(tempfile.mkdtemp(prefix='tlm-accepted-clone-'))
        got=subprocess.run(['dotnet','run','--project',str(oldroot/'tools/WorldSliceBuilder'),'--','--story-clone-check',str(oldplugin),str(out)],cwd=oldroot,capture_output=True,text=True)
        self.assertEqual(got.returncode,0,got.stdout+got.stderr)
        # dotnet may print build warnings before the JSON.
        before=json.loads(got.stdout[got.stdout.index('{'):]);current=clone();self.assertEqual(current.returncode,0,current.stdout+current.stderr)
        after=json.loads(current.stdout)
        for key in ('firstSection','nightMail','redHollow','quests','masters'):self.assertEqual(after[key],before[key],key)
        self.assertEqual(after['greenwater']['aliases'][:31],before['greenwater']['aliases'])
        self.assertEqual(after['greenwater']['aliasScripts'][:27],before['greenwater']['aliasScripts'])
        for key in ('forms','ownAliases'):
            self.assertEqual({n:after['greenwater'][key][n] for n in before['greenwater'][key]},before['greenwater'][key])
        self.assertEqual(after['greenwater']['lists'],before['greenwater']['lists'])
        self.assertEqual(after['persistentReferences'],before['persistentReferences']+2)


class StrictLookup(unittest.TestCase):
    def test_other_corn_name_match_or_wrong_name_cannot_be_used_as_strict_corn(self):
        for variant in ('relief-no-corn','relief-wrong-corn-name'):
            with self.subTest(variant=variant):
                folder=Path(tempfile.mkdtemp(prefix='tlm-strict-corn-'));master=folder/'master/Fallout4.esm';out=folder/'out'
                for args in (['dotnet','run','--project','tools/StandInMaster','--',str(master),variant],['dotnet','run','--project','tools/PluginBuilder','--','--out',str(out),'--fallout4-esm',str(master)]):
                    got=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);self.assertEqual(got.returncode,0,got.stdout+got.stderr)
                d=json.loads((out/'TheLastMeridian.json').read_text());q=next(q for q in d['Quests'] if q['EditorId']=='TLM_GW_Relief')
                self.assertNotIn('Corn',{p['Name'] for p in q['Scripts'][0]['Props']})
                self.assertIn('STRICT relief unavailable: Corn',(out/'TheLastMeridian.report.txt').read_text())
