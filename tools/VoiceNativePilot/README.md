# Original-actor native voice pilot 002

Separate opt-in addon, based on exact f491eeb4e670d306530446b60f82785950dbb747. No historical source, manifest, verifier, package, profile or launcher changed. No installation/game launch/merge/workflow/provider change. All output stays ignored under this project's build folder.

## Actual implementation

TLMVoiceNativePilot.esp is GOG0.95, dependent on Fallout4.esm and the exact accepted TheLastMeridian.esp. Use only alongside its reviewed f491 story/world pair in a FUTURE separate private profile. It owns one non-starting dialogue quest, two Custom0 topics/INFO, four messages, two clipboard ACTIs and two persistent controls. It declares exactly two header-only overrides: original RH surface WRLD000CF7 and persistent CELL000CF8; their complete subrecord payloads match the original. No original NPC, placed actor, actor base, voice type, alias, quest logic or existing cell children is copied/edited.

The controls are [Voice test] Blevins at2816,384,0 and [Voice test] Roark at2304,384,0 on the actual outdoor Mouth surface. Their source actors are original Blevins000B22/base000AAB and Roark000B21/base000AAC, all TheLastMeridian.esp. Each control is128units south of its original source placement, with the measured small clipboard base; original actor movement/availability remains authoritative. They refuse a dead/missing/disabled/unloaded/replaced/fighting/distant actor, another player identity, scene/dialogue/talking or lost generation. Controls are optional **recorded auditions**, not replacements for current greer_first/roark_mouth dialogue. Confirmation offers play, text-only or cancel; no gameplay item/stage/outcome/reward is granted. The only started quest is this new no-stage pilot dialogue holder, checked for actual Start success and IsRunning before Say.

## Real audio mapping without actor mutation

Current Traits inheritance bit1 resolves Blevins through owned24A029 EncWorkshopNPCMaleFarmer08b to VTYP00002D MaleRough. Roark resolves through24A016 FemaleFarmer02b to VTYP013ADD FemaleEvenToned. These donors'8126 flags exclude further Traits inheritance. Merely editing stored baseVoice023324 would be wrong. This pilot instead checks actual GetVoiceType against its own existing VTYP binding and uses the normal INFO lookup under that EDID folder. No SetOverrideVoiceType, base actor edit or disposable duplicate actor is needed; there is no persistent voice override to clean after load/interruption. Any unexpected actual runtime voice gets text fallback rather than unbound speech.

Actual emitted mapping:

- Sound/Voice/TLMVoiceNativePilot.esp/MaleRough/00000802_1.fuz: original Blevins line, “For the good of the Hollow, I'd ask you to stand back from the Mouth.”
- Sound/Voice/TLMVoiceNativePilot.esp/FemaleEvenToned/00000808_1.fuz: original Roark line, “I'm listening to something. Say it quiet.”

The reviewed original generated FUZs are copied byte-for-byte (362C8D54... / F152973F...), with complete SDK-generated LIP plus original XWM; no Bethesda actor audio is copied and no regeneration/voice cloning occurs. Voice folder names describe engine lookup, not a claim to clone those stock performers. INFO Sound is unset, INFO Speaker binds the correct original base, and Say uses the exact original reference with speak-as None/false and current player target. No new accent approval is inferred.

Dispatch is not hearing/completion proof. A generation-tagged three-second FO4 StartTimer is only a debounce; IsTalking and scene checks refuse overlap. OnLoad invalidates outstanding activations; stale timer IDs cannot unlock a newer attempt. No call changes actor voice state, inventory, health, dialogue outcomes or story progression. If audible dispatch fails despite valid types, the same control always offers Read text; the notification explicitly says recording requested. Practical finite final checks follow yielding scene/dialogue/voice observations; no impossible atomic-world guarantee is claimed.

## Reproducible local gates

Using cached Mutagen0.53.1 only, dotnet build succeeds with0warnings/errors. SafeBuild restricts owned-master hash and fresh output directly under this project build root, locks input/ancestor handles and never adopts an existing destination. Program writes and reopens the new plugin. Strict verify.py checks the entire Git baseline inventory, exact new-file union/pins, raw record whitelist, old header payload identity, INFO subtitle/speaker/topic and persistent controls. Frozen historical guards remain unchanged.

After portable LF normalization, actual Papyrus2.8.0.4 compile-004:1success0failed, bound by compile-receipt.json. Earlier failed compile-001 is preserved (Skyrim OnUpdate is not FO4); actual source uses FO4 OnTimer. Twelve focused actual-PSC/raw-artifact tests pass, including cancellation, text path, failed Start and true-but-not-running, initial invalid states, post-modal loss/load, old-generation release, fired late dialogue/voice callbacks, recovery, stale fallback suppression, and a guard-removal mutant that dispatches after a demonstrated late death. Raw mutations remove the VMAD binding or alter the approved subtitle and are rejected. Native method stubs are explicit synthetic assumptions, not audio proof.

package.py creates a NEW workspace-only four-payload addon: ESP, one fresh PEX and two original FUZ files. It checks source/artifact and exact compile bindings first and emits a separate package receipt. No licensed base plugin, stock audio, model or master is included. The tiny source manifest contains only hashes/identifiers, never licensed payload.

## Still required

Independent Sam source/compiler/artifact review, then root's explicit isolated use gate. Native quest/Say topic selection, effective voice readback, filename lookup, audibility, volume/subtitle duration, lip movement, heading/range, interruption/load/repeat behavior and owner listening/accent approval are OPEN. This is runnable source and an actual compiled/local package, not a claim of a played/heard demo. No existing candidate or39payload terrain QA bundle is rebound.
