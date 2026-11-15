# WORLD-QUEST-002: opt-in exterior first-section candidate

Development source candidate, not native acceptance. Inputs: world/couch1583f92361ecbdd35f24c9e35ff4b057302623b1 plus reviewed departure runtime7f3d9d1ad789816c9db2963a09aa8fb0b50dd2af, composed as a separate cherry-pick on this isolated branch. QASmoke remains the fallback. No new chapter, quest outcome or canon is introduced.

## Build modes and dependencies

Two-argument WorldSliceBuilder remains the shell mode with Fallout4.esm only. Explicit story mode adds TheLastMeridian.esp as a named master, never as a quiet override:

```powershell
dotnet run --project tools/WorldSliceBuilder -- "F:\SteamLibrary\steamapps\common\Fallout 4\Data\Fallout4.esm" build/world-story-new --story-source "C:\Modlists\TMR\mods\TheLastMeridian-Dev\TheLastMeridian.esp"
```

Use a new/empty staging directory outside both input trees. Input reads do not alter installed files. The story addon still uses the filename TLMWorldSlice.esp; select either shell or story build in the isolated profile, not two renamed copies of the same world. `world-story.json` records the exact source ESP hash, explicit masters, quest IDs and full29-reference mapping. Pin the reviewed runtime too: the departure change is script-only and an ESP hash cannot establish which PEX is installed.

The workspace build compiles18scripts, including the unchanged reviewed departure MQ01Quest, the optional WorldEntry wrapper and the revised Act1Guide. Root must stage this candidate's compiled bundle for native QA, not overwrite it with oldered738runtime or retain a private furniture-probe Core override. No install or launcher change is made by this task.

## Binding and ownership

All249shell references, world/cell/terrain/cabin and furniture remain the same. Story mode appends26interaction references plus3guides, all initially disabled/persistent and owned by the addon. New TLM_WS_A1 copies the existing development quest header/Act1Walk/Talk bindings, rebinds only its own alias objects to the new quest, and preserves CastInto targets in the master MQ01/SQ01. Source records are never overridden or rewritten. Test-room decoration is excluded; original guide IDs33–35are retained with their correct owning quest links. New world-only opening notification replaces only the clone's SayBegin property.

The main/side quest state machines, actor/item bases, messages and quest rules remain in TheLastMeridian.esp. Fresh world actors reuse the existing actor bases. Dispatch/journal/ledger/parts/weapon, caravan and sheriff aliases point only at the new world refs. The addon never moves the original QASmoke people/items.

## Explicit safe development entry

In a fresh isolated COC session with TLM_G_DevScenario0, enter `coc TLM_WS_Clearing`, then `cqf TLM_WS_Entry Begin`. The wrapper requires the correct cell, no running original preview or main/side quest, and no existing main/side stage. It never resets/stops/restarts those quests. An already-started section is not rebound. These guards protect quest state; they do not prove a character was never saved. Fresh disposable-profile use remains a caller prerequisite. No player-stat or one-click launcher implementation is duplicated here.

The wrapper calls the reused Act1Walk.Begin, which starts the shared MQ stage10, casts aliases, enables new refs and opens the two existing trigger types only after actor setup. Do not also start TLM_A1 or use preview scenario900 in this session.

## Layout and directions

Wreck interaction group is around700/1050; road encounter around1900/1950; Mercy sheriff3260/2530and townsfolk beside the cabin yard. Full coordinates are emitted in world-story.json. Ambush sight is a100-half-extent box centered1750/1710/100; town gate is the same size centered3048/2400/100. The eastern bypass branches well before the ambush and passes outside that box. Actor combat pursuit/navigation is not certified.

Repeatable Directions objects at1000/850,2250/1950and3380/2500use the existing read-only guide logic. Only the new aliases set Exterior=true; defaultfalse preserves the tested QASmoke copy. Exterior text names the fenced cabin/marked bypass rather than claiming old timber-post geography. Guides do not set stages, grant items or resolve encounters. They still require native world activation/readability checks before owner story handoff; source wiring alone is not delivery acceptance.

## Required remaining native gates

There is no NAVM/NAVI in this prototype. Root must verify all13actors load/stand safely, alias casts/pickup events reach the reused rules, journal/objectives behave, and the dispatch can be collected and delivered to Pritchard for the truthful first-section endpoint. Independently walk a peaceful Leave route and a bypass route; inspect live trigger behavior and the preserved living-departure cue. Test all3directions objects at relevant stages without accepting source/simulation as visible UI proof. Fight/pursuit, general NPC sandboxing and a finished navigable chapter remain unverified dependencies.

Existing shell native terrain/furniture success does not certify story integration. Preserve exact logs, source/runtime hashes and observed outcomes. Root controls later installation/game/CI; this source task performs none. Rollback is the previous shell artifact/runtime in the disposable profile, without resetting a save or changing QASmoke fallback.
