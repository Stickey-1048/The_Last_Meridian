"""Candidate technical text versus accepted source and immutable placements."""
import json
import subprocess
import unittest
from test_sim import ROOT,PLUGIN
from source_snapshot import built_red_hollow


class ClarityProjection(unittest.TestCase):
    def test_all_accepted_speech_and_old_physical_refs_are_unchanged(self):
        old=json.loads(built_red_hollow().read_text());now=json.loads(PLUGIN.read_text())
        oldmsgs={m['EditorId']:m for m in old['Messages']};newmsgs={m['EditorId']:m for m in now['Messages']}
        mapping=json.loads((ROOT/'docs/design/GREENWATER_STORY_001_MAPPING.json').read_text())
        for row in mapping['speech']:
            self.assertEqual(newmsgs[row['record']],oldmsgs[row['record']],row['record'])
        # Reference records retain identity and coordinates; only six existing
        # activator display names explain the roles more clearly.
        self.assertTrue(old['Npcs']);self.assertEqual(now['Npcs'],old['Npcs'])
        oldcells={c['EditorId']:c for c in old['Cells']};newcells={c['EditorId']:c for c in now['Cells']}
        self.assertEqual(set(newcells),set(oldcells))
        additions=[]
        for name,c in oldcells.items():
            before={r['EditorId']:r for r in c['Placed']};after={r['EditorId']:r for r in newcells[name]['Placed']}
            self.assertEqual({n:after[n] for n in before},before,name)
            additions.extend(set(after)-set(before))
            self.assertEqual({k:v for k,v in c.items() if k!='Placed'},{k:v for k,v in newcells[name].items() if k!='Placed'})
        self.assertEqual(sorted(additions),['TLM_REF_GW_ReliefStores','TLM_REF_GW_ReliefSupply'])
        oldq={q['EditorId']:q for q in old['Quests']};newq={q['EditorId']:q for q in now['Quests']}
        for name in ('TLM_MQ01','TLM_SQ01','TLM_MQ02A','TLM_MQ02B','TLM_MQ02C'):
            if name=='TLM_MQ02B':
                # Its technical payment-only44 interim now names the separate
                # barge correctly. Accepted journal/speech on46 stays exact.
                payment=next(s for s in newq[name]['Stages'] if s['Index']==44)
                self.assertEqual(payment['Log'],"You accepted Hatcher's payment. The grain remains on his barge beside the Queen; Greenwater did not receive it.")
                next(s for s in oldq[name]['Stages'] if s['Index']==44)['Log']=payment['Log']
            self.assertEqual(newq[name],oldq[name],name)
        for name in ('scripts/Source/User/TLM/Core.psc',):
            before=subprocess.run(['git','show','1cdd466:'+name],cwd=ROOT,capture_output=True,check=True).stdout.decode().replace('\r\n','\n')
            self.assertEqual((ROOT/name).read_text(),before,name)

    def test_existing_labels_describe_distinct_barge_and_occupied_boat(self):
        d=json.loads(PLUGIN.read_text());records={r['EditorId']:r for r in d['Records']}
        expected={'LabelLanding':'Greenwater landing - find Opal','LabelQueen':'Queen gambling boat - Hatcher and crew',
                  'CargoLashed':"Opal's grain barge - tied to the Queen",'Table':"Hatcher's card table - grain or payment",
                  'Chain':'Grain barge lashing - inspect choices','Pilot':'Grain barge pilot - move freed cargo'}
        for suffix,name in expected.items():self.assertEqual(records['TLM_ACTI_GW_'+suffix]['Name'],name)
