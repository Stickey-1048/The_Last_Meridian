"""Four Flags exact authored projection and raw synthetic clone/floor audits.

No licensed master, native asset, actor movement or inventory guarantee.
"""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from test_sim import ROOT,PLUGIN
from test_greenwater_world_clone import clone
from source_snapshot import snapshot,built_greenwater_relief,GREENWATER_RELIEF


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
        now=(ROOT/'tools/PluginBuilder/formkeys.txt').read_text().splitlines()
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

    def test_each_damaged_entry_custody_cast_or_evidence_binding_is_refused(self):
        for damage in ('fair-binding-removed','fair-ledger-missing','fair-cell-missing','fair-entry-substituted','fair-case-alias-substituted','fair-original-cast-forced','fair-dedicated-cast-substituted','fair-case-model-missing'):
            with self.subTest(damage=damage):
                got=clone(damage);self.assertEqual(got.returncode,1,got.stdout+got.stderr);self.assertIn('REFUSED',got.stderr)

    def test_old_raw_clone_payloads_and_ids_survive_new_entry_adapter(self):
        oldroot=snapshot(GREENWATER_RELIEF);oldplugin=built_greenwater_relief().with_suffix('.esp')
        got=subprocess.run(['dotnet','run','--project',str(oldroot/'tools/WorldSliceBuilder'),'--','--story-clone-check',str(oldplugin),str(Path(tempfile.mkdtemp(prefix='tlm-ff-oldclone-')))],cwd=oldroot,capture_output=True,text=True)
        self.assertEqual(got.returncode,0,got.stdout+got.stderr);before=json.loads(got.stdout[got.stdout.index('{'):])
        got=clone();self.assertEqual(got.returncode,0,got.stdout+got.stderr);after=json.loads(got.stdout)
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
        for variant,accepted in (('four-flags-floor',True),('four-flags-floor-bounds',False),('four-flags-floor-no-model',False)):
            with self.subTest(variant=variant):
                out=Path(tempfile.mkdtemp(prefix='tlm-ff-floor-'));master=out/'Fallout4.esm'
                made=subprocess.run(['dotnet','run','--project','tools/StandInMaster','--',str(master),variant],cwd=ROOT,capture_output=True,text=True)
                self.assertEqual(made.returncode,0,made.stdout+made.stderr)
                got=subprocess.run(['dotnet',str(ROOT/'tools/WorldSliceBuilder/bin/Debug/net8.0/WorldSliceBuilder.dll'),'--four-flags-interior-check',str(master),str(PLUGIN.with_suffix('.esp'))],cwd=ROOT,capture_output=True,text=True)
                self.assertEqual(got.returncode,0 if accepted else 1,got.stdout+got.stderr)
                if accepted:
                    d=json.loads(got.stdout);self.assertEqual(d['tiles'],63)
                    self.assertIn('Synthetic',d['model']);self.assertTrue(d['courierBookText'])
                else:self.assertIn('REFUSED',got.stderr)


if __name__=='__main__':unittest.main()
