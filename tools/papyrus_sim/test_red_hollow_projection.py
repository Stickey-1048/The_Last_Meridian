"""Exact accepted source projection, mixed alias allocation and no fabricated outcomes."""
import hashlib
import json
import re
import subprocess
import unittest
from test_sim import ROOT,PLUGIN

class RedHollowProjection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.map=json.loads((ROOT/'docs/design/RED_HOLLOW_STORY_001_MAPPING.json').read_text())
        cls.plugin=json.loads(PLUGIN.read_text());cls.msg={m['EditorId']:m for m in cls.plugin['Messages']}
        cls.story=ROOT/cls.map['source']['folder']
        cls.lines={l['id']:l for f in ('tlm_mq02c.json','tlm_mq02.json') for l in json.loads((cls.story/'talk'/f).read_text())['lines']}
    def test_source_is_accepted_text_without_canon_rewrite(self):
        for file,digest in self.map['source']['files'].items():
            text=(self.story/file).read_text()
            old=subprocess.run(['git','show','4624ee9:'+self.map['source']['folder']+'/'+file],cwd=ROOT,capture_output=True,check=True).stdout.decode().replace('\r\n','\n')
            self.assertEqual(text,old,file);self.assertEqual(hashlib.sha256(text.encode()).hexdigest().upper(),digest)
    def test_every_message_is_mapped_once_and_bounded(self):
        rows=sum((self.map[k] for k in ('speech','documents','transcripts','ui')),[])
        ids=[r['record'] for r in rows];self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(set(ids),{n for n in self.msg if n.startswith('TLM_MSG_RH_')})
        self.assertEqual(len(ids),98)
        for name in ids:
            m=self.msg[name];self.assertTrue(m['Box']);self.assertLessEqual(len(m['Text']),240,name);self.assertLessEqual(len(m['Buttons']),4,name)
            for b in m['Buttons']:self.assertFalse(b['Conditions']);self.assertLessEqual(len(b['Text']),48,name)
    def test_all_spoken_words_and_buttons_are_the_actual_accepted_source(self):
        for node in {r['node'] for r in self.map['speech']}:
            pages=sorted((r for r in self.map['speech'] if r['node']==node),key=lambda p:p['page']);text=[]
            for r in pages:
                m=self.msg[r['record']];self.assertEqual(m['Title'],r['speaker'])
                prefix=r['speaker']+': "';self.assertTrue(m['Text'].startswith(prefix));self.assertTrue(m['Text'].endswith('"'))
                text.append(m['Text'][len(prefix):-1])
                labels=[b['Text'] for b in m['Buttons']]
                self.assertEqual(labels,[b['label'] for b in self.lines[node].get('buttons',[])] or ['Continue'] if r is pages[-1] else ['Continue'])
            self.assertEqual(' '.join(text),self.lines[node]['text'],node)
    def test_documents_and_registered_transcripts_preserve_exact_text(self):
        docs={d['id']:d for d in json.loads((self.story/'documents.json').read_text())['documents']}
        for key,group in [('document','documents'),('node','transcripts')]:
            for node in {r[key] for r in self.map[group]}:
                rows=sorted((r for r in self.map[group] if r[key]==node),key=lambda r:r['page'])
                actual=' '.join(self.msg[r['record']]['Text'].split('\n\n',1)[1] for r in rows)
                expected=docs[node]['text'] if key=='document' else self.lines[node]['text']
                if group=='transcripts' and node.startswith('cutter'):expected=expected[expected.index('We were paid'):]
                self.assertEqual(actual,expected,node)
    def test_stages_objectives_aliases_and_append_only_source_prefix(self):
        for q in self.plugin['Quests']:
            if q['EditorId'] in self.map['aliases']:self.assertEqual(q['Aliases'],self.map['aliases'][q['EditorId']])
        q=next(q for q in self.plugin['Quests'] if q['EditorId']=='TLM_MQ02C');self.assertEqual(q['Stages'],self.map['stages']);self.assertEqual(q['Objectives'],self.map['objectives'])
        old=subprocess.run(['git','show','4624ee9:tools/PluginBuilder/formkeys.txt'],cwd=ROOT,capture_output=True,check=True).stdout.decode().splitlines()
        ids=(ROOT/'tools/PluginBuilder/formkeys.txt').read_text().splitlines();self.assertEqual(ids[:len(old)],old)
        self.assertEqual({ids[i]:int(ids[i+1]) for i in range(len(old),len(ids),2)},self.map['allocation']['new'])
        roles=[n for n in self.map['allocation']['new'] if n.startswith('TLM_NPC_RH_')];self.assertEqual(len(roles),15);self.assertFalse(any('Dunmore' in n or 'Cutter' in n for n in roles))
    def test_five_labels_and_every_own_reference_has_supported_floor(self):
        cell=next(c for c in self.plugin['Cells'] if c['EditorId']=='TLM_CELL_RedHollow');self.assertTrue(cell['OfThisPlugin'])
        refs={r['EditorId']:r for r in cell['Placed']};floors=[r['Position'] for n,r in refs.items() if '_Floor_' in n]
        self.assertEqual(len(floors),122)
        for n,r in refs.items():
            if '_Floor_' in n or n=='TLM_REF_RH_Fall':continue
            x,y,z=r['Position'];self.assertTrue(any(abs(x-fx)<=128 and abs(y-fy)<=128 for fx,fy,fz in floors),(n,r['Position']))
        self.assertEqual(len([n for n in refs if n.startswith('TLM_REF_RH_Label')]),5)
    def test_three_road_availability_and_fair_unavailable_across_composition(self):
        self.assertGreater(len(self.map['composedAvailability']),5)
        for name,want in self.map['composedAvailability'].items():
            self.assertEqual(self.msg[name]['Text'],want['text']);self.assertEqual([b['Text'] for b in self.msg[name]['Buttons']],want['buttons'])
            self.assertTrue('Red Hollow' in want['text'] or 'All three roads playable' in want['text']);self.assertTrue('fair is not' in want['text'] or 'fair unavailable' in want['text'])
        guide=(ROOT/'scripts/Source/User/TLM/Act1Guide.psc').read_text();self.assertIn('Greenwater, Iron Junction and Red Hollow are available',guide)
    def test_unsupported_compound_quotes_have_no_route(self):
        source=(ROOT/'scripts/Source/User/TLM/RedHollowWalk.psc').read_text()
        for node in ('quill_after_shot','quill_after_drop','roark_after_line','roark_after_break','roark_after_fire','roark_after_deadline','roark_cage','dunmore_freed','dunmore_freed_fine'):
            self.assertNotIn('Say("'+node+'"',source,node)
        self.assertIn('RegisterForHitEvent(Ref(Alias_Rope), Game.GetPlayer())',source)
        self.assertNotIn('GetCurrentGameTime',source)
        for local in re.findall(r'^\s*(?:int|ObjectReference)\s+(\w+)\s*=',source,re.M):self.assertNotIn(local.lower(),('scene','sound','action'))
