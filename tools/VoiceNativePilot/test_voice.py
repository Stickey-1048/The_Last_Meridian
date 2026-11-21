from pathlib import Path
import json,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'papyrus_sim'))
from sim import Session,ObjectReference,Actor,Form,Message,Quest
TEMPS=[]
class Fixture:
 def __init__(self,source=None):
  temp=tempfile.TemporaryDirectory();TEMPS.append(temp);p=Path(temp.name)/'empty.json';p.write_text(json.dumps({'Records':[],'Messages':[],'Quests':[]}))
  self.s=Session(source or ROOT/'scripts/TLMDev',p);self.cell=self.s._cell('Surface');self.s.player.cell=self.cell;self.s.player.pos=(0,0,0)
  self.control=ObjectReference(Form('Control','Activator',has_model=True));self.control.cell=self.cell
  self.base=Form('OriginalBase','Npc',True);self.voice=Form('VoiceType','VoiceType');self.topic=Form('Topic','Topic')
  self.speaker=Actor(self.base);self.speaker.editor_id='OriginalSpeaker';self.speaker.cell=self.cell;self.speaker.pos=(32,0,0);self.s.actors.append(self.speaker)
  self.q=Quest({'EditorId':'PilotQuest','Flags':[],'Stages':[],'Objectives':[]});self.s.quests['PilotQuest']=self.q
  self.inst=self.s._attach({'Name':'TLMDev:VoicePilot','Props':[]},self.control,None)
  self.inst.props.update(originalspeaker=self.speaker,expectedbase=self.base,expectedvoice=self.voice,linetopic=self.topic,pilotquest=self.q,prompt=Message('Prompt',True,[{}, {}, {}]),textfallback=Message('Fallback',True,[{}]))
  self.answer=0;self.change=None;self.says=[];self.talking=False;self.type=self.voice
  self.updates=[];self.s.n_objectreference_starttimer=lambda ref,ctx,delay,timer:self.updates.append((delay,timer))
  self.s.n_actor_istalking=lambda ref,ctx:self.talking
  self.s.n_actor_getactorbase=lambda ref,ctx:ref.base
  self.s.n_objectreference_getvoicetype=lambda ref,ctx:self.type
  self.s.n_objectreference_say=lambda ref,ctx,*args:self.says.append((ref,args))
  def show(ref,ctx,*args):
   self.s.messages_shown.append(ref.editor_id)
   if ref.editor_id=='Prompt' and self.change:self.change()
   return self.answer if ref.editor_id=='Prompt' else 0
  self.s.n_message_show=show
 def use(self,actor=None):
  self.s.send_event(self.inst,'OnActivate',[actor or self.s.player]);self.s.run(self.s.now+1)
  errors=[x for x in self.s.papyrus_log if x.startswith('error')]
  if errors:raise AssertionError(errors)
class Source(unittest.TestCase):
 def tearDown(self):
  while TEMPS:TEMPS.pop().cleanup()
 def test_audio_uses_exact_original_topic_player_and_no_gameplay_effects(self):
  a=Fixture();before=dict(a.s.player.inventory);a.use();self.assertEqual(a.says,[(a.speaker,(a.topic,None,False,a.s.player))]);self.assertEqual(a.s.player.inventory,before);self.assertEqual(list(a.s.quests),['PilotQuest']);self.assertTrue(a.q.running)
 def test_cancel_invalid_and_text_only(self):
  for answer in (-1,2,7,1):
   a=Fixture();a.answer=answer;a.use();self.assertEqual(a.says,[]);self.assertEqual(a.s.messages_shown,['Prompt','Fallback'] if answer==1 else ['Prompt']);self.assertFalse(a.q.running)
 def test_initial_ineligible_is_silent(self):
  for mode in ('dead','speakerdead','disabled','unloaded','far','speakerfar','wrongcell','scene','talking','base','nonplayer','combat'):
   with self.subTest(mode=mode):
    a=Fixture()
    if mode=='dead':a.s.player.dead=True
    if mode=='speakerdead':a.speaker.dead=True
    if mode=='disabled':a.speaker.disabled=True
    if mode=='unloaded':a.speaker.cell=None
    if mode=='far':a.s.player.pos=(9999,0,0)
    if mode=='speakerfar':a.speaker.pos=(9999,0,0)
    if mode=='wrongcell':a.speaker.cell=a.s._cell('Elsewhere')
    if mode=='scene':a.speaker.in_scene=True
    if mode=='talking':a.talking=True
    if mode=='base':a.speaker.base=Form('Wrong','Npc')
    if mode=='combat':a.speaker.combat_target=a.s.player
    a.use(Actor(Form('Other','Npc')) if mode=='nonplayer' else None);self.assertEqual(a.says,[]);self.assertEqual(a.s.messages_shown,[])
 def test_post_prompt_loss_load_replacement_and_cancel_recover(self):
  for mode in ('death','far','alias','load','player'):
   a=Fixture()
   def change():
    if mode=='death':a.speaker.dead=True
    if mode=='far':a.s.player.pos=(9999,0,0)
    if mode=='alias':a.inst.props['originalspeaker']=Actor(a.base)
    if mode=='load':list(a.s.call(a.inst,a.inst.script.functions['onload'],[]))
    if mode=='player':a.s.player=Actor(Form('NewPlayer','Npc'))
   a.change=change;a.use();self.assertEqual(a.says,[],mode)
 def test_wrong_voice_and_failed_quest_start_show_text_not_speech(self):
  for mode in ('voice','false','true-not-running'):
   a=Fixture()
   if mode=='voice':a.type=Form('Different','VoiceType')
   else:a.s.n_quest_start=lambda ref,ctx: mode=='true-not-running'
   a.use();self.assertEqual(a.says,[]);self.assertEqual(a.s.messages_shown,['Prompt','Fallback'])
 def test_late_voice_context_changes_refuse_and_retry(self):
  for mode in ('death','far','disable','alias'):
   a=Fixture();fired=[]
   def voice(ref,ctx):
    if not fired:
     fired.append(True)
     if mode=='death':a.speaker.dead=True
     if mode=='far':a.s.player.pos=(9999,0,0)
     if mode=='disable':a.speaker.disabled=True
     if mode=='alias':a.inst.props['originalspeaker']=Actor(a.base)
    return a.voice
   a.s.n_objectreference_getvoicetype=voice;a.use();self.assertEqual(fired,[True]);self.assertEqual(a.says,[],mode)
   a.speaker.dead=False;a.speaker.disabled=False;a.s.player.pos=(0,0,0);a.inst.props['originalspeaker']=a.speaker;a.use();self.assertEqual(len(a.says),1,mode)
 def test_busy_reentry_and_generation_release(self):
  a=Fixture();a.inst.vars['busy']=True;a.use();self.assertEqual(a.s.messages_shown,[]);a.inst.vars['generation']=4;list(a.s.call(a.inst,a.inst.script.functions['release'],[3]));self.assertTrue(a.inst.vars['busy'])
 def test_late_dialogue_callback_fires_blocks_and_recovers(self):
  for mode in ('death','far','alias','combat'):
   a=Fixture();native=a.s.n_objectreference_isindialoguewithplayer;fired=[]
   def late(ref,ctx):
    if ref is a.speaker and a.s.messages_shown and not fired:
     fired.append(True)
     if mode=='death':a.speaker.dead=True
     if mode=='far':a.s.player.pos=(9999,0,0)
     if mode=='alias':a.inst.props['originalspeaker']=Actor(a.base)
     if mode=='combat':a.speaker.combat_target=a.s.player
    return native(ref,ctx)
   a.s.n_objectreference_isindialoguewithplayer=late;a.use();self.assertEqual(fired,[True]);self.assertEqual(a.says,[],mode)
   a.speaker.dead=False;a.speaker.combat_target=None;a.s.player.pos=(0,0,0);a.inst.props['originalspeaker']=a.speaker;a.use();self.assertEqual(len(a.says),1)
 def test_debounce_timer_is_generation_bound_not_a_completion_claim(self):
  a=Fixture();a.use();self.assertEqual(len(a.says),1);self.assertTrue(a.inst.vars['busy']);self.assertEqual(a.updates,[(3.0,1)])
  list(a.s.call(a.inst,a.inst.script.functions['ontimer'],[0]));self.assertTrue(a.inst.vars['busy'])
  list(a.s.call(a.inst,a.inst.script.functions['ontimer'],[1]));self.assertFalse(a.inst.vars['busy']);a.talking=True;a.use();self.assertEqual(len(a.says),1)
 def test_removed_context_mutant_exposes_late_death_dispatch(self):
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'VoicePilot.psc';text=(ROOT/'scripts/TLMDev/VoicePilot.psc').read_text(encoding='utf-8-sig')
   first=text.index('    VoiceType observedVoice =');tail=text[first:];old='If !Context(playerActor,speaker,capturedGeneration)';self.assertEqual(tail.count(old),1);tail=tail.replace(old,'If false',1);old='If !EligibleState(playerActor,speaker,capturedGeneration)';self.assertEqual(tail.count(old),1);tail=tail.replace(old,'If false',1);p.write_text(text[:first]+tail,encoding='utf-8')
   a=Fixture(Path(folder));fired=[]
   def late(ref,ctx):
    if not fired:fired.append(True);a.speaker.dead=True
    return a.voice
   a.s.n_objectreference_getvoicetype=late;a.use();self.assertEqual(fired,[True]);self.assertEqual(len(a.says),1)
 def test_second_voice_read_mutation_suppresses_both_speech_and_fallback(self):
  a=Fixture();calls=[]
  def late(ref,ctx):
   calls.append(True)
   if len(calls)==2:a.speaker.dead=True;return Form('Wrong','VoiceType')
   return a.voice
  a.s.n_objectreference_getvoicetype=late;a.use();self.assertEqual(len(calls),2);self.assertEqual(a.says,[]);self.assertEqual(a.s.messages_shown,['Prompt'])
 def test_actual_owned_plugin_headers_speakers_and_audio_mapping_and_mutations(self):
  import verify,struct
  mapping=json.loads((ROOT/'build/pilot-002/voice-mapping.json').read_text());plugin=ROOT/'build/pilot-002/TLMVoiceNativePilot.esp';baseline=ROOT.parents[3]/'work/rh-return-account-build-f491eeb/build/licensed-return-account-skeleton-001/bundle/TheLastMeridian.esp'
  self.assertEqual(verify.artifact_problems(plugin,mapping,baseline),[])
  data=plugin.read_bytes()
  for before,after in [(b'TLMDev:VoicePilot',b'TLMDev:WrongPilot'),(b'For the good of the Hollow',b'For the good of the Valley')]:
   self.assertIn(before,data)
   with tempfile.TemporaryDirectory() as folder:
    p=Path(folder)/'bad.esp';p.write_bytes(data.replace(before,after));self.assertTrue(verify.artifact_problems(p,mapping,baseline))
if __name__=='__main__':unittest.main(verbosity=2)




