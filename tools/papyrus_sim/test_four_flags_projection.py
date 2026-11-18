"""Four Flags exact authored projection and raw synthetic clone/floor audits.

No licensed master, native asset, actor movement or inventory guarantee.
"""
import json
import copy
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from test_sim import ROOT,PLUGIN
from test_greenwater_world_clone import clone,stand_in_story
from source_snapshot import snapshot,built_greenwater_relief,GREENWATER_RELIEF,built_four_flags,FOUR_FLAGS


class FourFlagsProjection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads(PLUGIN.read_text(encoding='utf-8'))
        cls.msg={m['EditorId']:m for m in cls.d['Messages']}
        cls.m=json.loads((ROOT/'docs/design/FOUR_FLAGS_STORY_001_NODES.json').read_text(encoding='utf-8'))

    def test_all_61_original_nodes_keep_words_buttons_conditions_and_entry(self):
        raw=json.loads((ROOT/self.m['source']).read_text(encoding='utf-8'))['lines']
        mapped={n['source']:n for n in self.m['nodes']}
        self.assertEqual(set(mapped),{n['id'] for n in raw});self.assertEqual(len(mapped),61)
        withheld={'pike_line','pike_flint','flint_line','flint_beaten'}
        for n in raw:
            row=mapped[n['id']]
            for key in ('speaker','text','when','priority','entry','buttons'):
                self.assertEqual(row[key],n.get(key,False if key=='entry' else 0 if key=='priority' else []),n['id']+':'+key)
            if n['id'] in withheld:
                self.assertEqual(row['disposition'],'withheld');self.assertFalse(row['pages']);continue
            self.assertEqual(row['disposition'],'implemented')
            pages=[self.msg['TLM_MSG_FF_'+p] for p in row['pages']]
            # Each page attributes the speaker; concatenation restores every word.
            spoken=' '.join(p['Text'].split(':\n\n',1)[1] for p in pages)
            self.assertEqual(spoken,n['text'],n['id'])
            expected=[b['label'] for b in n.get('buttons',[])] or ['Continue']
            self.assertEqual([b['Text'] for b in pages[-1]['Buttons']],expected,n['id'])
            for p in pages[:-1]:self.assertEqual([b['Text'] for b in p['Buttons']],['Continue'])

    def test_every_fair_message_is_bounded_and_bound_to_its_actual_controller(self):
        q=next(q for q in self.d['Quests'] if q['EditorId']=='TLM_MQ03')
        scripts=q['Scripts'];self.assertEqual([s['Name'] for s in scripts],['TLM:MQ03Quest','TLM:FourFlagsWalk'])
        props={p['Target'] for p in scripts[1]['Props'] if (p.get('Target') or '').startswith('TLM_MSG_FF_')}
        messages={n:m for n,m in self.msg.items() if n.startswith('TLM_MSG_FF_')}
        self.assertEqual(set(messages),props)
        for n,m in messages.items():
            self.assertTrue(m['Box']);self.assertLessEqual(len(m['Text']),240,n)
            self.assertTrue(1<=len(m['Buttons'])<=4,n)
            for b in m['Buttons']:self.assertLessEqual(len(b['Text']),48,n)
        aliases=q['Aliases'];self.assertEqual(len(aliases),32)
        for name in ('Pritchard','Talbot','Pike','Belden'):
            a=next(a for a in aliases if a['Name']==name);self.assertIsNone(a['Fill'],name)

    def test_allocation_is_append_only_to_accepted_relief_not_a_shift(self):
        before=subprocess.run(['git','show',GREENWATER_RELIEF+':tools/PluginBuilder/formkeys.txt'],cwd=ROOT,capture_output=True,check=True).stdout.decode().splitlines()
        now=(snapshot(FOUR_FLAGS)/'tools/PluginBuilder/formkeys.txt').read_text().splitlines()
        self.assertEqual(now[:len(before)],before)
        rest=now[len(before):];self.assertGreater(len(rest),400)
        self.assertEqual([int(rest[i+1]) for i in range(0,len(rest),2)],list(range(int(before[-1])+1,int(before[-1])+1+len(rest)//2)))
        mapping=json.loads((ROOT/'docs/design/FOUR_FLAGS_STORY_001_MAPPING.json').read_text(encoding='utf-8'))
        self.assertEqual([{'record':rest[i],'id':int(rest[i+1])} for i in range(0,len(rest),2)],mapping['allocation']['append'])

    def test_complete_message_alias_and_document_ledgers_match_actual_records(self):
        mapping=json.loads((ROOT/'docs/design/FOUR_FLAGS_STORY_001_MAPPING.json').read_text(encoding='utf-8'))
        rows={row['record']:row for row in mapping['ui']}
        self.assertEqual(set(rows),{n for n in self.msg if n.startswith('TLM_MSG_FF_')})
        for n,row in rows.items():
            self.assertEqual(self.msg[n]['Text'],row['text']);self.assertEqual([b['Text'] for b in self.msg[n]['Buttons']],row['buttons'])
            self.assertTrue(row['guard']);self.assertTrue(row['channel'])
        q=next(q for q in self.d['Quests'] if q['EditorId']=='TLM_MQ03')
        self.assertEqual(mapping['aliases'],[{'id':a['Id'],'name':a['Name'],'fill':a['Fill'],'scripts':a['Scripts']} for a in q['Aliases']])
        documents=json.loads((ROOT/'assets/incoming/act1/story/documents.json').read_text(encoding='utf-8'))
        # Locate from the accepted intake shape without duplicating its words.
        rows=documents.get('notes',documents.get('documents',[]))
        if not rows:self.fail('accepted document intake shape changed')
        for name in ('fair_handbill','silver_case','courier_card'):
            source=next(row for row in rows if row['id']==name)['text'].replace('\n',' ')
            pages=[self.msg[n]['Text'] for n in self.msg if n.startswith('TLM_MSG_FF_D_'+name+'_')]
            self.assertEqual(' '.join(pages),source,name)

    def test_every_old_message_is_exact_except_twelve_declared_technical_availability_updates(self):
        historical_messages={m['EditorId']:m for m in json.loads(built_four_flags().read_text(encoding='utf-8'))['Messages']}
        before=json.loads(built_greenwater_relief().read_text(encoding='utf-8'))
        replacements={
            'Opening complete. All three roads playable; fair unavailable.':'Opening complete. Three roads and Four Flags entry are available.',
            'Mercy briefing. Greenwater, Iron Junction and Red Hollow are playable. The fair is not.':'Mercy briefing. Three roads and the qualified Four Flags entry are available.',
            'Greenwater, Iron Junction and Red Hollow are playable in this candidate; the fair is not.':'Three roads are playable. Four Flags entry is available after the first section.',
            'Greenwater road complete. Iron Junction and Red Hollow are also playable; the fair is not.':'Greenwater road complete. The other roads and Four Flags entry remain available.',
            'Night Mail road complete. Greenwater and Red Hollow remain playable; the fair is not.':'Night Mail road complete. The other roads and Four Flags entry remain available.',
            'Greenwater, Iron Junction and Red Hollow are playable. The fair is not.':'Three roads are playable. Four Flags entry is available after the first section.',
            'Red Hollow road complete. All three roads remain playable; the fair is not.':'Red Hollow road complete. Three roads and Four Flags entry remain available.'}
        expected={'TLM_MSG_A1_'+n for n in ('PritchardHandOff','PritchardAfter','PritchardAfterAndMore')}|{'TLM_MSG_MB_Hub'}|{'TLM_MSG_GW_'+n for n in ('AskTravel','ReportEndKnown','ReportEndUnknown')}|{'TLM_MSG_NM_'+n for n in ('AskTravel','NoteRoadComplete','ReportEnd')}|{'TLM_MSG_RH_Travel','TLM_MSG_RH_End'}
        changed=set()
        for old in before['Messages']:
            name=old['EditorId'];want=dict(old)
            if name in expected:
                text=want['Text'];matches=[(a,b) for a,b in replacements.items() if a in text and (name!='TLM_MSG_MB_Hub' or a.startswith('Mercy briefing.'))]
                self.assertEqual(len(matches),1,name)
                a,b=matches[0];want['Text']=text.replace(a,b);changed.add(name)
            self.assertEqual(historical_messages[name],want,name)
        self.assertEqual(changed,expected)
        self.assertTrue(all(len(historical_messages[n]['Text'])<=240 for n in changed))

    def test_whole_accepted_npcs_refs_and_quest_payloads_are_preserved(self):
        historical=json.loads(built_four_flags().read_text(encoding='utf-8'))
        before=json.loads(built_greenwater_relief().read_text(encoding='utf-8'))
        self.assertEqual(historical['Npcs'][:len(before['Npcs'])],before['Npcs'])
        self.assertEqual({n['EditorId'] for n in historical['Npcs'][len(before['Npcs']):]},{'TLM_NPC_FF_'+n for n in ('Whitcomb','Brigg','Grey','Flint','Juno')})
        oldcells={c['EditorId']:c for c in before['Cells']};newcells={c['EditorId']:c for c in historical['Cells']}
        self.assertEqual(set(newcells),set(oldcells)|{'TLM_CELL_FourFlags'})
        extra=set()
        for n,old in oldcells.items():
            new=newcells[n];oldrefs={p['EditorId']:p for p in old['Placed']};newrefs={p['EditorId']:p for p in new['Placed']}
            self.assertEqual({k:newrefs[k] for k in oldrefs},oldrefs,n)
            self.assertEqual({k:v for k,v in old.items() if k!='Placed'},{k:v for k,v in new.items() if k!='Placed'},n)
            extra.update(set(newrefs)-set(oldrefs))
        self.assertEqual(extra,{'TLM_REF_FF_Entry','TLM_REF_FF_MercyReturn'})
        oldquests={q['EditorId']:q for q in before['Quests']};newquests={q['EditorId']:q for q in historical['Quests']}
        self.assertEqual(set(newquests),set(oldquests)|{'TLM_MQ03','TLM_FF_Entry'})
        for n,old in oldquests.items():
            new=copy.deepcopy(newquests[n])
            allowed={'TLM_A1':{'TLM_FourFlags','TLM_FourFlagsEntry'},'TLM_GW':{'TLM_FourFlags'}}.get(n,set())
            added=[]
            for script in new['Scripts']:
                added.extend(p for p in script['Props'] if p['Name'] in allowed)
                script['Props']=[p for p in script['Props'] if p['Name'] not in allowed]
            self.assertEqual({p['Name'] for p in added},allowed,n)
            for p in added:self.assertEqual(p['Target'],'TLM_FF_Entry' if p['Name']=='TLM_FourFlagsEntry' else 'TLM_MQ03')
            if n=='TLM_MercyBriefing':
                self.assertEqual([s['Log'] for s in new['Stages']],['Mercy briefing. Three roads and the qualified Four Flags entry are available.','Mercy briefing complete. Three roads and qualified Four Flags entry remain available.'])
                for current,prior in zip(new['Stages'],old['Stages']):current['Log']=prior['Log']
            self.assertEqual(new,old,n)

    def test_each_damaged_entry_custody_cast_or_evidence_binding_is_refused(self):
        for damage in ('fair-binding-removed','fair-ledger-missing','fair-cell-missing','fair-entry-substituted','fair-case-alias-substituted','fair-original-cast-forced','fair-dedicated-cast-substituted','fair-case-model-missing'):
            with self.subTest(damage=damage):
                got=clone(damage);self.assertEqual(got.returncode,1,got.stdout+got.stderr);self.assertIn('REFUSED',got.stderr)

    def test_new_entry_and_return_remain_between_both_preserved_east_fences(self):
        got=clone();self.assertEqual(got.returncode,0,got.stdout+got.stderr);d=json.loads(got.stdout)
        self.assertEqual(d['fourFlagsSites'],{'Entry':[3820,3100,12],'MercyReturn':[3820,3070,32]})
        # Independently read actual native bounds: inner east3690, outer west3966.
        for a in d['fourFlags']['aliases']:
            self.assertGreaterEqual(a['x']-(3688+2),96)
            self.assertLessEqual(a['x']+96,3966)
            self.assertTrue(2432<a['y']<3456)

    def test_actual_approach_guard_refuses_both_fences_and_old_outer_crossing(self):
        # Synthetic metadata fixtures reproduce the independently audited native
        # fence AABBs; no licensed assets/master or pre-existing build/sim ESP.
        from test_greenwater_world_clone import DLL
        world=(ROOT/'tools/WorldSliceBuilder/WorldFourFlags.cs').read_text(encoding='utf-8')
        program=(ROOT/'tools/WorldSliceBuilder/Program.cs').read_text(encoding='utf-8')
        self.assertIn('FourFlagsApproach=(3820,3000)',world)
        self.assertIn('AuditFourFlagsApproach(routeObstacles.Select(p=>(p.Id,p.MinX,p.MaxX,p.MinY,p.MaxY)),start.X,start.Y,at.X,at.Y,back.X,back.Y)',program)
        bounds=[{'id':'YardRight4','minX':3686,'maxX':3690,'minY':2944,'maxY':3072},
                {'id':'YardRight5','minX':3686,'maxX':3690,'minY':3072,'maxY':3200},
                {'id':'BoundaryEast22','minX':3966,'maxX':3970,'minY':2944,'maxY':3072},
                {'id':'BoundaryEast23','minX':3966,'maxX':3970,'minY':3072,'maxY':3200}]
        good={'obstacles':bounds,'start':[3820,3000],'entry':[3820,3100],'return':[3820,3070]}
        cases=[({},None),({'start':[4000,3100],'entry':[3920,3100]},'BoundaryEast'),
               ({'start':[3670,3000]},'YardRight'),({'entry':[3750,3100]},'YardRight'),
               ({'return':[3920,3070]},'BoundaryEast'),({'return':[3750,3070]},'YardRight')]
        for edits,blocked in cases:
            with self.subTest(edits=edits),tempfile.TemporaryDirectory() as temp:
                fixture=Path(temp)/'bounds.json';fixture.write_text(json.dumps({**good,**edits}),encoding='utf-8')
                got=subprocess.run(['dotnet',str(DLL),'--four-flags-approach-check',str(fixture)],cwd=ROOT,capture_output=True,text=True)
                self.assertEqual(got.returncode,1 if blocked else 0,got.stdout+got.stderr)
                if blocked:self.assertIn(blocked,got.stderr)
                else:self.assertIn('clearance PASS',got.stdout)

    def test_old_raw_clone_payloads_and_ids_survive_new_entry_adapter(self):
        oldroot=snapshot(GREENWATER_RELIEF);oldplugin=built_greenwater_relief().with_suffix('.esp')
        got=subprocess.run(['dotnet','run','--project',str(oldroot/'tools/WorldSliceBuilder'),'--','--story-clone-check',str(oldplugin),str(Path(tempfile.mkdtemp(prefix='tlm-ff-oldclone-')))],cwd=oldroot,capture_output=True,text=True)
        self.assertEqual(got.returncode,0,got.stdout+got.stderr);before=json.loads(got.stdout[got.stdout.index('{'):])
        # The current cloner must preserve the actual accepted Four Flags source.
        # Current environment deltas are independently compared to this frozen
        # source by test_red_hollow_environment_projection, without repinning it.
        from test_greenwater_world_clone import DLL
        got=subprocess.run(['dotnet',str(DLL),'--story-clone-check',str(built_four_flags().with_suffix('.esp')),str(Path(tempfile.mkdtemp(prefix='tlm-ff-historical-clone-')))],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(got.returncode,0,got.stdout+got.stderr);after=json.loads(got.stdout)
        self.assertEqual(after['quests'],before['quests']+['TLM_WS_FF_Entry'])
        self.assertEqual(after['persistentReferences'],before['persistentReferences']+2)
        self.assertEqual(after['masters'],before['masters'])
        for key in ('nightMail','redHollow'):self.assertEqual(after[key],before[key],key)
        river=after['greenwater'];oldriver=before['greenwater']
        self.assertEqual(river['properties'],oldriver['properties']+1)
        self.assertEqual({k:v for k,v in river['forms'].items() if k!='TLM_FourFlags'},oldriver['forms'])
        self.assertEqual(river['forms']['TLM_FourFlags'],'TLM_MQ03 in TheLastMeridian.esp')
        self.assertEqual({k:v for k,v in river.items() if k not in ('forms','properties')},{k:v for k,v in oldriver.items() if k not in ('forms','properties')})
        first=after['firstSection'];old=before['firstSection']
        self.assertEqual(first['properties'],old['properties']+2)
        self.assertEqual({k:v for k,v in first.items() if k not in ('forms','properties')},{k:v for k,v in old.items() if k not in ('forms','properties')})
        self.assertEqual({k:v for k,v in first['forms'].items() if k not in ('TLM_FourFlags','TLM_FourFlagsEntry')},old['forms'])
        self.assertTrue(after['fourFlags']['present'])
        self.assertEqual(after['fourFlags']['script'],'TLM:FourFlagsEntry')
        self.assertEqual([a['name'] for a in after['fourFlags']['aliases']],['Entry','MercyReturn'])

    def test_floor_model_and_exact_bounds_are_required_before_source_grid_acceptance(self):
        story=stand_in_story()
        self.assertTrue(story.is_file(),'use the binary actually built by the canonical synthetic fixture')
        for variant,accepted in (('four-flags-floor',True),('four-flags-floor-bounds',False),('four-flags-floor-no-model',False)):
            with self.subTest(variant=variant):
                out=Path(tempfile.mkdtemp(prefix='tlm-ff-floor-'));master=out/'Fallout4.esm'
                made=subprocess.run(['dotnet','run','--project','tools/StandInMaster','--',str(master),variant],cwd=ROOT,capture_output=True,text=True)
                self.assertEqual(made.returncode,0,made.stdout+made.stderr)
                got=subprocess.run(['dotnet',str(ROOT/'tools/WorldSliceBuilder/bin/Debug/net8.0/WorldSliceBuilder.dll'),'--four-flags-interior-check',str(master),str(story)],cwd=ROOT,capture_output=True,text=True)
                self.assertEqual(got.returncode,0 if accepted else 1,got.stdout+got.stderr)
                if accepted:
                    d=json.loads(got.stdout);self.assertEqual(d['tiles'],63)
                    self.assertIn('Synthetic',d['model']);self.assertTrue(d['courierBookText'])
                else:self.assertIn('REFUSED',got.stderr)

    def test_fresh_json_only_sim_fixture_needs_no_adjacent_preexisting_binary(self):
        folder=Path(tempfile.mkdtemp(prefix='tlm-ff-json-only-'))
        description=folder/'TheLastMeridian.json'
        description.write_bytes(PLUGIN.read_bytes())
        self.assertFalse(description.with_suffix('.esp').exists())
        # This is the fresh CI shape: a description exists, no sibling ESP,
        # and the canonical binary fixture has not yet built anything.
        with patch('test_four_flags_projection.PLUGIN',description),patch('test_greenwater_world_clone._built',{}):
            self.test_floor_model_and_exact_bounds_are_required_before_source_grid_acceptance()
        self.assertFalse(description.with_suffix('.esp').exists())


if __name__=='__main__':unittest.main()
