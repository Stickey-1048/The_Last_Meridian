"""New travel source on existing PSC interpreter; synthetic worlds/activation, not native proof."""
from pathlib import Path
import json,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'papyrus_sim'))
from sim import Session,ObjectReference,Form,Message,Actor
import verify

OPEN_TEMPS=[]

class Fixture:
 def __init__(self,outgoing=True,source=None):
  self.temp=tempfile.TemporaryDirectory();OPEN_TEMPS.append(self.temp);p=Path(self.temp.name)/'empty.json';p.write_text(json.dumps({'Records':[],'Messages':[],'Quests':[]}))
  self.s=Session(source or ROOT/'scripts/TLMDev',p)
  self.first=self.s._cell('First');self.second=self.s._cell('Second');self.first.world=Form('FromWorld','Worldspace');self.second.world=Form('ToWorld','Worldspace')
  self.s.player.cell=self.first;self.s.player.pos=(0,0,0)
  self.control=ObjectReference(Form('TravelControl','Activator',has_model=True));self.control.editor_id='Control';self.control.cell=self.first
  self.target=ObjectReference(Form('PersistentMarker','Static',has_model=False),(10,20,30));self.target.editor_id='Target';self.target.cell=self.second
  self.s.n_objectreference_getworldspace=lambda ref,ctx:ref.cell.world if ref.cell else None
  self.inst=self.s._attach({'Name':'TLMDev:OptionalTerrainTravel','Props':[]},self.control,None)
  self.inst.props.update(prompt=Message('Prompt',True,[{'Text':'Travel'},{'Text':'Stay here'}]),destination=self.target,sourceworld=self.first.world,destinationworld=self.second.world,outbound=outgoing)
  self.answer=0;self.change=None;self.moves=[]
  def show(message,ctx,*args):
   self.s.messages_shown.append(message.editor_id)
   if self.change:self.change()
   return self.answer
  self.s.n_message_show=show;old=self.s.n_objectreference_moveto
  def move(ref,ctx,*args):
   self.moves.append((ref,args[0]));yield from old(ref,ctx,*args)
  self.s.n_objectreference_moveto=move
 def use(self,who=None):
  self.s.send_event(self.inst,'OnActivate',[who or self.s.player]);self.s.run(self.s.now+1)
  if any(x.startswith('error') for x in self.s.papyrus_log):raise AssertionError(self.s.papyrus_log)

class TravelSource(unittest.TestCase):
 def tearDown(self):
  while OPEN_TEMPS:OPEN_TEMPS.pop().cleanup()
 def test_confirmed_outbound_and_return_move_only_current_player_to_persistent_marker(self):
  for outbound in (True,False):
   a=Fixture(outbound);before=dict(a.s.player.inventory);a.use()
   self.assertEqual(a.moves,[(a.s.player,a.target)]);self.assertIs(a.s.player.cell,a.second)
   self.assertEqual(a.s.player.inventory,before);self.assertEqual(a.s.quests,{})
   self.assertFalse(a.inst.vars['busy']);self.assertTrue(a.s.notifications)
 def test_cancel_invalid_nonplayer_and_initial_dead_combat_absence_do_not_move(self):
  for mode in ('cancel','invalid','npc','dead','combat','scene','missing','disabled','far','world'):
   a=Fixture()
   if mode=='cancel':a.answer=1
   elif mode=='invalid':a.answer=-1
   elif mode=='dead':a.s.player.dead=True
   elif mode=='combat':a.control.combat_target=a.s.player;a.s.actors.append(a.control)
   elif mode=='scene':a.s.player.in_scene=True
   elif mode=='missing':a.inst.props['destination']=None
   elif mode=='disabled':a.control.disabled=True
   elif mode=='far':a.s.player.pos=(9999,0,0)
   elif mode=='world':a.target.cell=a.first
   if mode=='combat':
    # Use a real synthetic Actor to supply the existing player's combat-state native.
    foe=Actor(Form('Foe','Npc',True));foe.combat_target=a.s.player;a.s.actors=[a.s.player,foe]
   who=ObjectReference(Form('Other','Npc',True)) if mode=='npc' else a.s.player
   a.use(who);self.assertEqual(a.moves,[],mode)
 def test_post_confirmation_death_combat_move_target_loss_and_load_close_without_effect(self):
  for mode in ('dead','combat','move','target','load'):
   a=Fixture()
   def change():
    if mode=='dead':a.s.player.dead=True
    elif mode=='combat':
     foe=Actor(Form('Foe','Npc',True));foe.combat_target=a.s.player;a.s.actors=[a.s.player,foe]
    elif mode=='move':a.s.player.pos=(9999,0,0)
    elif mode=='target':a.target.disabled=True
    else:self.assertEqual(list(a.s.call(a.inst,a.inst.script.functions['onload'],[])),[]) # Deliver the actual assignment-only OnLoad before resume.
   a.change=change;a.use();self.assertEqual(a.moves,[],mode)
   a.change=None;a.s.player.dead=False;a.s.actors=[a.s.player];a.s.player.pos=(0,0,0);a.target.disabled=False;a.use();self.assertEqual(len(a.moves),1,mode)
 def test_reentrant_attempt_and_old_generation_release_do_not_unlock_current_attempt(self):
  a=Fixture();a.inst.vars['busy']=True;a.use();self.assertEqual(a.s.messages_shown,[])
  a.inst.vars['generation']=2
  a.s.spawn(a.s.call(a.inst,a.inst.script.functions['endattempt'],[1]),'old release');a.s.run(a.s.now+1)
  self.assertTrue(a.inst.vars['busy']);self.assertEqual(a.moves,[])
 def test_ignoring_confirm_cancel_mutant_reproduces_unwanted_travel(self):
  import shutil
  with tempfile.TemporaryDirectory() as folder:
   source=Path(folder);p=source/'OptionalTerrainTravel.psc';text=(ROOT/'scripts/TLMDev/OptionalTerrainTravel.psc').read_text(encoding='utf-8-sig');old='If answer != 0 || !Context(playerActor,capturedGeneration)';self.assertEqual(text.count(old),1);p.write_text(text.replace(old,'If false || !Context(playerActor,capturedGeneration)'),encoding='utf-8')
   a=Fixture(source=source);a.answer=1;a.use();self.assertEqual(len(a.moves),1)

 def test_sam_late_dialogue_read_changes_block_travel_and_ordinary_retry_recovers(self):
  for mode in ('player-far','wrong-source-world','destination-disabled'):
   with self.subTest(mode=mode):
    a=Fixture();old=a.s.n_objectreference_isindialoguewithplayer;fired=[];before=dict(a.s.player.inventory)
    def late(ref,context):
     if a.s.messages_shown and not fired:
      fired.append(True)
      if mode=='player-far':a.s.player.pos=(9999,0,0)
      elif mode=='wrong-source-world':a.s.player.cell=a.second
      else:a.target.disabled=True
     return old(ref,context)
    a.s.n_objectreference_isindialoguewithplayer=late;a.use()
    self.assertEqual(fired,[True]);self.assertEqual(a.moves,[]);self.assertEqual(a.s.notifications,[])
    self.assertEqual(a.s.player.inventory,before);self.assertEqual(a.s.quests,{})
    self.assertFalse(a.inst.vars['busy'])
    a.s.player.pos=(0,0,0);a.s.player.cell=a.first;a.target.disabled=False
    a.use();self.assertEqual(len(a.moves),1);self.assertIs(a.s.player.cell,a.second)
 def test_restored_actual_old_context_order_mutant_reproduces_late_wrong_move(self):
  import subprocess
  with tempfile.TemporaryDirectory() as folder:
   source=Path(folder)
   old=subprocess.check_output(['git','show','3e89c469e63645c042fb138cc4862d5dcfe85378:tools/TerrainRouteAddon/scripts/TLMDev/OptionalTerrainTravel.psc'],cwd=ROOT.parents[1])
   (source/'OptionalTerrainTravel.psc').write_bytes(old)
   a=Fixture(source=source);native=a.s.n_objectreference_isindialoguewithplayer;fired=[]
   def late(ref,context):
    if a.s.messages_shown and not fired:fired.append(True);a.s.player.pos=(9999,0,0)
    return native(ref,context)
   a.s.n_objectreference_isindialoguewithplayer=late;a.use()
   self.assertEqual(fired,[True]);self.assertEqual(len(a.moves),1)
 def test_unconfirmed_native_move_never_claims_arrival(self):
  a=Fixture(False)
  def refuse(ref,context,*args):return None
  a.s.n_objectreference_moveto=refuse;a.use()
  self.assertIs(a.s.player.cell,a.first)
  self.assertTrue(any('could not be confirmed' in n for n in a.s.notifications))
  self.assertFalse(any('Back at' in n for n in a.s.notifications))

class RawAddon(unittest.TestCase):
 def test_exact_raw_nominal(self):self.assertEqual(verify.verify()['ownPersistentReferences'],3)
 def test_wrong_pose_persistence_header_and_vmad_destination_are_refused(self):
  raw=verify.OUTPUT.read_bytes()
  for needle in (b'TLM_DEV_REF_ReturnMeridian\0',b'TLM_WS_Meridian\0',b'TLMDev:OptionalTerrainTravel'):
   with self.subTest(needle=needle):
    bad=bytearray(raw);where=bad.index(needle);bad[where]=ord('X')
    with self.assertRaises(AssertionError):verify.verify(bytes(bad))
  # Remove persistence on the actual outbound record, not merely a label change.
  import struct
  records=verify.rows(raw);flags,body,_=records[b'REFR',0x03000805]
  header=b'REFR'+struct.pack('<III',len(body),flags,0x03000805)
  at=raw.index(header);bad=bytearray(raw);bad[at+9]^=4
  with self.assertRaises(AssertionError):verify.verify(bytes(bad))
  # Redirect the actual VMAD Destination to the old nonpersistent Meridian marker.
  link=struct.pack('<H',11)+b'Destination'+b'\x01\x01'+struct.pack('<HhI',0,-1,0x01000806)
  at=raw.index(link);bad=bytearray(raw);struct.pack_into('<I',bad,at+len(link)-4,0x02000804)
  with self.assertRaises(AssertionError):verify.verify(bytes(bad))
  # Deliberate whole-file mutations preserve every other byte, reach actual guards.
  for needle,change in ((b'DATA'+__import__('struct').pack('<H6f',24,3184,1104,576,0,0,0),lambda b,p:b.__setitem__(p+6,0)),):
   bad=bytearray(raw);p=bad.index(needle);bad[p+8]^=1
   with self.assertRaises(AssertionError):verify.verify(bytes(bad))
class SourceAndOutputSafety(unittest.TestCase):
 def test_exact_component_source_receipt(self):self.assertEqual(verify.verify_source()['source'],'PASS')
 def test_only_new_addon_source_changes_and_accepted_path_guard_is_exact(self):
  import subprocess,hashlib
  tree=ROOT.parents[1]
  changed=subprocess.check_output(['git','diff','--name-only','f491eeb4e670d306530446b60f82785950dbb747'],cwd=tree,text=True).splitlines()
  self.assertFalse([n for n in changed if not n.startswith('tools/TerrainRouteAddon/')])
  parent=verify.WORKSPACE/'work/spectacle-route-landmarks-001/SafeBuild.cs'
  self.assertEqual((ROOT/'SafeBuild.cs').read_bytes(),parent.read_bytes())
 def test_existing_output_and_bad_owned_input_fail_before_output_or_adoption(self):
  import subprocess,uuid,hashlib
  dll=ROOT/'bin/Debug/net8.0/TerrainRouteAddon.dll';master='C:/Program Files (x86)/GOG Galaxy/Games/Fallout 4 GOTY/Data/Fallout4.esm'
  before=verify.OUTPUT.read_bytes()
  r=subprocess.run(['dotnet',str(dll),master,str(verify.OUTPUT.parent)],capture_output=True,text=True)
  self.assertEqual(r.returncode,1);self.assertIn('existing destination',r.stderr);self.assertEqual(verify.OUTPUT.read_bytes(),before)
  folder=ROOT/'build'/('bad-input-'+uuid.uuid4().hex);folder.mkdir();fake=folder/'Fallout4.esm';fake.write_bytes(b'not the owned master')
  out=ROOT/'build'/('refused-'+uuid.uuid4().hex)
  r=subprocess.run(['dotnet',str(dll),str(fake),str(out)],capture_output=True,text=True)
  self.assertEqual(r.returncode,1);self.assertIn('SHA256 mismatch',r.stderr);self.assertFalse(out.exists())

if __name__=='__main__':unittest.main()
