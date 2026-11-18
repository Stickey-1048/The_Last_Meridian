"""Fresh synthetic serialization and independent raw group/identity checks.
No licensed master, native lighting/sky/navigation or installed output.
"""
import base64,json,struct,subprocess,sys,tempfile,unittest,zlib
from pathlib import Path
from test_sim import ROOT
from test_greenwater_world_clone import stand_in_story,DLL
from source_snapshot import built_four_flags
sys.path.insert(0,str(ROOT/'tools'))
import check_plugin_layout as layout


def decoded(path):
    raw=Path(path).read_bytes();out={};names={}
    for tag,off,size,fid,flags in layout.records(raw,0,len(raw)):
        payload=raw[off:off+size]
        if flags&layout.COMPRESSED:payload=zlib.decompress(payload[4:])
        out[(tag,fid)]=(flags,payload)
        name=dict(layout.subrecords(payload)).get('EDID',b'').rstrip(b'\0').decode('utf-8')
        if name:names[name]=(tag,fid)
    return raw,out,names


def edit_subrecord(blob,kind,name,subtag,change):
    raw=bytearray(blob)
    for tag,off,size,fid,flags in layout.records(raw,0,len(raw)):
        if tag!=kind:continue
        if flags&layout.COMPRESSED:continue
        ss=dict(layout.subrecords(raw[off:off+size]))
        if ss.get('EDID',b'').rstrip(b'\0').decode()!=name:continue
        pos=off
        while pos<off+size:
            sub=raw[pos:pos+4].decode();length=struct.unpack_from('<H',raw,pos+4)[0];pos+=6
            if sub==subtag:change(raw,pos,length);return bytes(raw)
            pos+=length
    raise AssertionError('Missing uncompressed mutation target '+kind+'/'+name+'/'+subtag)


class EnvironmentProjection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.story=stand_in_story();cls.data=json.loads(cls.story.with_suffix('.json').read_text(encoding='utf-8'))
        cls.receipt=json.loads((cls.story.parent/'red-hollow-environment.json').read_text(encoding='utf-8'))
        cls.mapping=json.loads((ROOT/'docs/design/RED_HOLLOW_ENVIRONMENT_001_MAPPING.json').read_text(encoding='utf-8'))
        cls.raw,cls.records,cls.names=decoded(cls.story);cls.described=layout.placed_from_json(cls.story.with_suffix('.json'))
        cls.earlier=built_four_flags();cls.old=json.loads(cls.earlier.read_text(encoding='utf-8'));cls.oldraw,cls.oldrecords,cls.oldnames=decoded(cls.earlier.with_suffix('.esp'))
    def test_original99_aliases_and_same_original_reference_keys_are_preserved(self):
        old=next(q for q in self.old['Quests'] if q['EditorId']=='TLM_RH');now=next(q for q in self.data['Quests'] if q['EditorId']=='TLM_RH')
        self.assertEqual(len(old['Aliases']),99);self.assertEqual(now['Aliases'][:99],old['Aliases']);self.assertEqual([a['Name'] for a in now['Aliases'][99:]],['SurfaceFall','GalleryFall'])
        self.assertEqual(self.mapping['aliases'],[{'id':a['Id'],'name':a['Name'],'fill':a['Fill']} for a in now['Aliases']])
        self.assertEqual(len([q for q in self.data['Quests'] if q['EditorId']=='TLM_MQ02C']),1)
    def test_complete116_row_transform_and_parent_ledger_match_fresh_records(self):
        old={p['EditorId']:(c,p) for c in self.old['Cells'] for p in c['Placed']};now={p['EditorId']:(c,p) for c in self.data['Cells'] for p in c['Placed']}
        self.assertEqual(len(self.mapping['rehoming']),116)
        self.assertEqual(self.receipt['rehomed'],[{k:v for k,v in r.items() if k not in ('beforeParent','sourceFlagSemantics')} for r in self.mapping['rehoming']])
        for row in self.mapping['rehoming']:
            name=row['reference'];before,p=old[name];after,q=now[name]
            self.assertEqual(before['EditorId'],'TLM_CELL_RedHollow');self.assertEqual(after['EditorId'],'TLM_CELL_RH_SurfacePersistent')
            self.assertEqual(p['FormKey'],q['FormKey']);self.assertEqual(p['Position'],row['before']);self.assertEqual(q['Position'],row['after']);self.assertEqual(p['Base'],q['Base']);self.assertEqual(p['Rotation'],q['Rotation'])
            expected=[row['before'][0]-(1024 if row['before'][0]>=2944 else 0),row['before'][1],row['before'][2]];self.assertEqual(row['after'],expected)
    def test_all_unrelated_old_record_payloads_and_ids_remain_exact(self):
        moved={r['reference'] for r in self.mapping['rehoming']}
        ui={'TLM_MSG_RH_'+n for n in ('StageTravel','Descend','LabelGap','LabelMouth','LabelCage','LabelNine','LabelGallery')}
        labels={'TLM_ACTI_RH_'+n for n in ('LabelGap','LabelMouth','LabelCage','LabelNine','LabelGallery')}
        allowed=moved|ui|labels|{'TLM_MQ02C','TLM_RH','TLM_CELL_RedHollow','TLM_REF_RH_Fall'}|{n for n in self.oldnames if n.startswith('TLM_REF_RH_Floor_')}
        for key,value in self.oldrecords.items():
            self.assertIn(key,self.records)
            if key[0]=='TES4':continue  # record count/next-ID metadata necessarily grows
            name=dict(layout.subrecords(value[1])).get('EDID',b'').rstrip(b'\0').decode('utf-8')
            if name not in allowed:self.assertEqual(self.records[key],value,name or str(key))
        for row in self.mapping['rehoming']:
            key=self.oldnames[row['reference']];before=dict(layout.subrecords(self.oldrecords[key][1]));after=dict(layout.subrecords(self.records[key][1]))
            before.pop('DATA');after.pop('DATA');self.assertEqual(after,before,row['reference'])
        for name in labels:
            key=self.oldnames[name];a=dict(layout.subrecords(self.oldrecords[key][1]));b=dict(layout.subrecords(self.records[key][1]));a.pop('FULL');b.pop('FULL');self.assertEqual(a,b,name)
    def test_world_grid_land_are_real_exterior_structures_and_old_interior_stays(self):
        problems,cells,refs=layout.check_cells(self.raw,self.described);self.assertEqual(problems,[]);self.assertEqual(cells,6);self.assertEqual(refs,sum(len(c['Placed']) for c in self.data['Cells']))
        for name in ('TLM_CELL_RH_SurfacePersistent','TLM_CELL_RH_Surface'):
            ss=dict(layout.subrecords(self.records[self.names[name]][1]));self.assertFalse(struct.unpack('<H',ss['DATA'])[0]&1);self.assertNotIn('XCLL',ss)
        inside=dict(layout.subrecords(self.records[self.names['TLM_CELL_RedHollow']][1]));self.assertTrue(struct.unpack('<H',inside['DATA'])[0]&1);self.assertIn('XCLL',inside);self.assertIn('LTMP',inside)
        self.assertEqual(len([k for k in self.records if k[0]=='LAND']),1)
    def test_emitters_are96_real_LIGH_references_with_exact_typed_receipts(self):
        lights=[(c,p) for c in self.data['Cells'] for p in c['Placed'] if (p['EditorId']or'').startswith('TLM_REF_RHE_Light')]
        self.assertEqual(len(lights),96);self.assertEqual(self.receipt['emitter']['radius'],256);self.assertEqual(self.receipt['emitter']['flags'],8193);self.assertEqual(list(base64.b64decode(self.receipt['emitter']['rgb'])),[228,203,182])
        self.assertEqual(self.receipt['lightingSource']['inherits'],1784)
        self.assertEqual(len({p['FormKey'] for _,p in lights}),96)
        for c,p in lights:self.assertEqual(c['EditorId'],'TLM_CELL_RedHollow');self.assertEqual(p['Base'],self.receipt['emitter']['key']);self.assertFalse(p['InitiallyDisabled'])
        self.assertEqual(self.receipt['emitter'],self.mapping['light']['observedSyntheticMetadata'])
    def test_geometry_readback_contains_real_enclosures_supported_shelters_and_all_cohort_space(self):
        audit=self.receipt['geometryAudit'];self.assertGreaterEqual(audit['minimumHeadroom'],128);self.assertEqual(audit,self.mapping['geometry'])
        names={p['Name'] for p in audit['boxes']};self.assertIn('GallerySeal512',names);self.assertIn('CourtGateRoof',names);self.assertIn('HoistDeskRoof',names)
        for role in ('Nine','Gallery'):
            for part in ('North','South','East','West','Roof','Floor'):self.assertTrue(any(n.startswith(role+part) for n in names),role+part)
    def test_raw_guard_rejects_false_interior_climate_grid_and_parent(self):
        edits=[('CELL','TLM_CELL_RH_Surface','DATA',lambda b,p,n:struct.pack_into('<H',b,p,1),'non-interior'),('CELL','TLM_CELL_RH_Surface','XCLC',lambda b,p,n:struct.pack_into('<i',b,p,1),'grid'),('WRLD','TLM_WRLD_RH_Surface','CNAM',lambda b,p,n:struct.pack_into('<I',b,p,0),'climate')]
        for kind,name,tag,edit,word in edits:
            with self.subTest(word=word):
                changed=edit_subrecord(self.raw,kind,name,tag,edit);problems,_,_=layout.check_cells(changed,self.described);self.assertTrue(any(word in x for x in problems),problems)
    def test_raw_guard_rejects_nonflat_land_without_trusting_writer(self):
        changed=bytearray(self.raw)
        for tag,off,size,fid,flags in layout.records(changed,0,len(changed)):
            if tag!='LAND':continue
            pos=off
            while pos<off+size:
                sub=changed[pos:pos+4].decode();n=struct.unpack_from('<H',changed,pos+4)[0];pos+=6
                if sub=='VHGT':changed[pos+4]=1;break
                pos+=n
        problems,_,_=layout.check_cells(bytes(changed),self.described);self.assertTrue(any('flat LAND' in x for x in problems),problems)
    def test_cloner_rejects_new_surface_coordinate_or_world_substitution(self):
        edits=[('REFR','TLM_REF_RH_MouthArrival','DATA',lambda b,p,n:struct.pack_into('<f',b,p,2305)),('WRLD','TLM_WRLD_RH_Surface','EDID',lambda b,p,n:b.__setitem__(p,ord('X')))]
        for kind,name,tag,edit in edits:
            with self.subTest(name=name),tempfile.TemporaryDirectory() as t:
                source=Path(t)/'input'/'TheLastMeridian.esp';source.parent.mkdir();source.write_bytes(edit_subrecord(self.raw,kind,name,tag,edit))
                got=subprocess.run(['dotnet',str(DLL),'--story-clone-check',str(source),str(Path(t)/'world')],cwd=ROOT,capture_output=True,text=True)
                self.assertEqual(got.returncode,1,got.stdout+got.stderr);self.assertIn('REFUSED',got.stderr)


if __name__=='__main__':unittest.main()
