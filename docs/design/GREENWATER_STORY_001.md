# Next playable Act I story: The Queen of Tellico

Iris, 16 November 2026. **Priority change: stop further freight-yard/landscape planning and implement one complete story road next.** This is an engineering contract outline against accepted writing `d142104fdc6f72ae556f285a0166c1122893b991`, not a claim that the road exists in the game. No accepted source, installation, save or cloud session is changed by this brief.

## Pick Greenwater, not all three roads

Build **Chapter 2 / MQ02B, The Queen of Tellico**. Its accepted source already supplies a personal problem, four named roles, investigation, four alternative resolutions, reactions, optional judgment and a payment-evidence lead. Returning food, selling out the town or burning its winter supplies produces an immediately legible consequence. A self-contained dock/boat greybox can deliver those consequences without a moving vehicle simulation.

Iron Junction's strongest authored beat requires a moving engine, a rail gap and a credible train escape. Red Hollow couples a hanging, physically meaningful rope rescue, a warned local deadline, hoist descent, eleven miners and the tightly bounded Dorn encounter. Both are valid later work; they have more interdependent native feasibility gates. Greenwater still needs real engineering, especially cargo delivery and cast-dependent consequences, but neither a timer nor a full driving/boating system is required for a faithful staged prototype.

**Target:** one normal first playthrough aiming for 30-45 minutes, including walking, investigation and a chosen resolution; this is a design goal, not measured duration. The current prose alone cannot establish that duration. Time the actual greybox; report its measured length without padding it with waiting, mandatory repeated conversations or unrelated errands.

## Deliverable and entry boundary

Deliver a separately pinned playable story candidate: player travels from Mercy into a clearly labelled **Greenwater story greybox**, meets Opal, boards the Queen, investigates, chooses a course, sees the resulting cargo/town/NPC state, returns to Mercy and gives a bounded report. All four authored main outcomes must be executable and independently verifiable. One completed path is the owner playthrough; QA exercises the alternatives. A menu that narrates an outcome without changing the world/state is insufficient.

Reuse a simple separate test area, with three connected zones: **landing/cook-shed -> Queen deck/table and cargo -> short Chute/return landing**. Existing basic floors, rails, crates and lights are sufficient. Use readable area labels outside character speech. No finished drowned town, boat model, music band, voice acting, custom art, terrain or full boat physics is a prerequisite. Label any representational section as greybox rather than implying the player is steering a finished vessel.

At Mercy, add one explicit opt-in travel activation after actual MQ01 dispatch delivery/debrief completion. Technical label: `Greenwater story test`. Availability text: `Only the Greenwater road is playable in this candidate.` Preserve SQ01 reporting and existing Pritchard interactions. A river briefing may be offered using accepted text, but the new quest must not depend on taking the optional Red Hollow book or on that book's pending physical clarification. Do not silently turn a8's information-only buttons into promises to travel.

Engineering needs a new composed source candidate selected by Maya. Preserve immutable b280/E127 owner fallback and accepted d142 writing. If a8 MercyBriefing is included, preserve its actual live guards, SQ01 return behavior, manifest/18-old+2-new runtime selection and unresolved native gates; do not assume those facts from source acceptance. Implementation of this story can proceed while that separate native observation waits.

## Exact accepted writing inputs

All paths below are relative to the accepted d142 tree, under `assets/incoming/act1/story/`.

| Source | Exact records/nodes to project |
|---|---|
| `quests/tlm_mq02b.json` | Key `mq02b`, record `TLM_MQ02B`; all stages, objectives, choices, evidence, flags and `cannot_break` |
| `talk/tlm_mq02b.json` | `starnes_first`, `starnes_wants`, `starnes_guns`, `starnes_bowl`; `pruitt_skiff`, `pruitt_confess`; `hatcher_table`, `hatcher_lost`, `hatcher_won`, `hatcher_share`, `hatcher_paid`; `pruitt_chain`, `pruitt_ran`, `pruitt_burned`; all `starnes_after_*`, `starnes_denied`, `starnes_won_hatcher_dead`; `belden_greenwater_relief`, `belden_greenwater_relief_fire`; ordinary defaults as appropriate |
| `documents.json` | Whole `ration_board` and `letter_of_hire` documents; no paraphrased substitute for the evidence |
| `characters.json` | Stable IDs `starnes` = Opal Starnes; `hatcher` = Lyle Hatcher; `pruitt` = Mose Rafferty, Catfish; `belden` = Tomas Belden. Mose is Opal's grandson; no new family branch |
| `talk/tlm_mq02.json` | `pritchard_road_river` for departure information; the exact text of `pritchard_hears_river_after_fair` / `_unknown` for a bounded return-report projection, as explained below |

Do not import the reference selector as if it were a native adapter. Do not blindly execute its button effects when the actual physical outcome has not occurred. Record every native projection and any necessary guard change in a mapping ledger. Character speech and documents above remain exact; technical objective/status text may describe the built prototype honestly. Native message-length/rendering limits must be checked on the full displayed string, with split presentation if necessary.

## Story sequence: action, response, discovery, choice, consequence

| Beat | Actual player action | NPC response / discovery | Meaningful result visible in the build |
|---|---|---|---|
| Arrival | Use the explicit Mercy travel point; physically enter Greenwater landing | Opal's accepted `starnes_first`; ration board visibly/readably identifies nine days of food against ninety | Journal/objective points to the actual cook-shed, not an unbuilt regional destination |
| Ask and investigate | Speak to Opal, optionally take a bowl/read board; choose what she wants done | `starnes_wants` asks for grain and Hatcher's neck; `starnes_guns` explains why the town cannot simply take it | Accepting the problem does not promise a hanging. Leaving now keeps it unresolved |
| Find a way aboard | Walk to Rafferty; choose gangway or off-side and physically cross the corresponding short access path | `pruitt_skiff`; optional `pruitt_confess` reveals his role towing the barge | Two working boarding approaches, not two labels to the same invisible teleport. No need for a rowing minigame |
| Establish the dispute | Reach/activate Hatcher's table | `hatcher_table`: he calls the grain salvage; the visible cargo is still lashed alongside | Player can negotiate, investigate the strongbox, return to the barge chain, or leave without resolving the quest |
| Find the deeper cause | Open/read the actual letter from the strongbox, or hear `hatcher_paid` and its follow-up | He was paid to delay the grain; selling it back was his own additional scheme | Stage50/payment knowledge is earned only by delivered text/read evidence. The unsigned square mark is a lead, not proof of Vane's identity |
| Decide | Play Hatcher's card challenge, cut loose and pilot home, accept the 200-cap share, or explicitly burn the occupied boat | Accepted speeches, warning and responses for that branch | One mutually exclusive outcome commits only after its real action/scene succeeds; effects persist and cannot be farmed |
| Face the result | Walk back to the cook-shed/landing and inspect cargo and surviving people | Correct `starnes_after_*` response; after a card win, optional Hatcher judgment; after fire/share, Belden's real food relief | Full, reduced or absent recovered cargo; Hatcher's tracked fate; 200 caps only for the paid betrayal; a real meal where promised |
| Complete and report | Explicitly depart after one resolved course, then activate the bounded Mercy report | Knowledge-sensitive accepted report text | MQ02B100/completion, persistent outcome/evidence; next lead is the unexplained hire/square-mark payment. Other roads/fair remain unavailable |

## Native stage and state contract

Use one real native quest for this road with the stable `TLM_MQ02B` identity if no record conflict exists. Confirm that before allocation. Its stages reflect the accepted road, not the local a8 briefing helper's similarly numbered stages. Support non-linear optional evidence and persistent outcomes; do not use a single numeric comparison that assumes every lower stage happened.

| Stage | Trigger that actually earns it | Guard / observation |
|---|---|---|
| 10 | Actual Greenwater landing entry on this road | Start once; objective10; travel handoff represents the commissioned river trip, not possession of a token that a8 never granted |
| 20 | Accepted Opal problem conversation delivered and player takes the task | Objective20; no time limit armed; no forced resolution on departure |
| 30 | Player physically boards the Queen by either working approach | Objective40; both entrances converge on the same quest/cargo state |
| 40 | Player reaches/activates Hatcher's table | Table offer is now available; unavailable/dead Hatcher cannot give it |
| 41 | Player passes the card challenge and Hatcher actually yields the barge | Card-win resolution; whole cargo can then be brought to the landing; optional judgment is separate |
| 42 | Player cuts the chain, takes the pilot control and completes the staged Chute return | This is completed escape, not merely a cut-chain click; reduced cargo visibly arrives; live Rafferty alone may speak `pruitt_ran` |
| 43 | Informed fire order plus the actual staged fire/outcome while the grain remains lashed alongside | Occupied Queen and winter cargo lost; no invented exact death count; alternative to completed Chute/card/share, never cut-then-burn |
| 44 | Player accepts Hatcher's share and the one-time payment succeeds | 200 caps once; cargo retained by Queen; the actual return conversation delivers the lie to Opal, if she lives |
| 45 | Failed card challenge | Not a resolved road and not a completion gate; player can still choose another supported course. Accepted prose returns the gun; do not permanently remove it |
| 50 | Letter actually read, or Hatcher's hire admission actually heard | `silver_river` = learned payment evidence. Oral admission is valid; present inventory possession is not required |
| 60 | Explicit hanging choice after card win, living Hatcher in custody, and staged execution committed | `hatcher_hanged`; actual death state. No hanging because the player left, refused, or failed to meet Opal |
| 61 | Explicit alive-to-Pritchard choice and actual custody handoff/transport | Hatcher remains alive and removed from free table interaction; no corpse, duplicate or promise that the fair exists |
| 100 | Actual departure after one of41/42/43/44, following its displayed/physical consequence | Complete once; optional evidence/judgment cannot block completion; unresolved departure never grants100 |

Additional persisted state must distinguish what stages alone cannot: `CargoState` (Queen / yielded / home-whole / home-reduced / destroyed), `CargoDelivered`, actual recovery amount, `CardResult`, `HatcherDisposition` (free / released-friend / custody / hanged / otherwise-dead), `SharePaid`, `LieTold`, `RiverReportGiven`, and earned evidence knowledge. Map the accepted `grain_home`, `grain_sold`, `queen_burned`, `hatcher_hanged`, `hatcher_friend`, `hatcher_hunting`, `silver_river` explicitly. These are runtime bookkeeping, not new fiction. No new timed failure.

Stage41 alone must not pretend the player has already delivered the won grain: require a real cargo-return action before the grain-home display. Stage44 alone must not make an unheard lie true: `grain_sold` follows both paid deal and actual lie delivery. If Opal dies before that lie, preserve the corrupt deal/payment as an observed fact but do not fabricate her response or a false `LieTold` value. The outcome journal/UI can state the remaining truth without ghost dialogue.

The accepted stage44 log currently combines the deal with Opal hearing the lie and thanking the player. **Do not display that combined log merely on payment.** This native projection uses the exact interim journal/status text `You accepted Hatcher's share. The grain remains aboard the Queen.` After the actual living-Opal return exchange, the accepted combined log becomes truthful and may be shown. If she cannot hear it, retain the truthful interim account and finish the paid-deal outcome without fabricating gratitude. Record this context split in the mapping ledger; it changes no accepted source JSON. `grain_sold` remains the stricter deal-plus-lie fact, while the completed paid-deal path is stage44. No need to invent a new speaker to satisfy an inaccurate compound journal.

## Alias and physical action inventory

| Binding | Native requirement |
|---|---|
| Opal / Hatcher / Rafferty / Belden | Four actual canonical actors in their own road area; stable IDs/display names; never clone Mercy's Pritchard or recast a road actor as a new named envoy. Alive/present/noncombat checked after modal returns before state changes |
| Landing, cook-shed, gangway, off-side, table, chain, pilot lever, return dock, exit | Actual references/triggers/activation points with understandable labels, usable approach space and no controller-only inaccessible choice |
| Barge/cargo and Queen | Separately tracked visible references; whole/reduced/destroyed cargo configurations. Do not delete quest evidence merely to show a burned boat |
| Strongbox and hire letter | Actual accessible container/readable evidence; reading observation maps to knowledge. Safe access remains if Hatcher dies; no forced lockpicking/perk gate |
| Ration board | Actual readable approved text; no evidence flag required |
| Belden food | A real, finite, one-time meal/grant or actual usable food source accompanying the accepted relief speech. Eating has no faction agreement effect. Do not pretend one wagon replaces winter stores |
| Mercy return/report | Existing Pritchard activated safely in the owner exterior; optional quest-target alias must not move him or reset MQ01/SQ01 |

## Four resolutions, concretely bounded

**Cards:** one documented native speech/Charisma check, both results exercised at normal character stats. A deterministic prototype threshold of current Charisma5 is an implementation tuning choice, not canon; expose the threshold in test-only status and record it. No boosted QA stats or random result presented as a real skill check. A loss does not end the quest. A win yields the actual barge/cargo-return action. Optional judgment uses the three exact `hatcher_lost`/`starnes_after_won` options: hang him, custody alive, or let him keep his boat. Released-friend state suppresses the unresolved demand on repeats; no invented fourth response is needed.

**Cut and run:** a physical chain activation and separate pilot activation initiate a short clearly represented Chute segment. Use a bounded scene/fade between static boat/dock zones if needed; do not make full vehicle motion a prerequisite. No first-person swimming through lethal water is required. Finish the return before42, then show cargo. Retain the accepted difference: living Rafferty loses a third, player-alone with dead Rafferty loses half. Choose an exact divisible test quantity for bookkeeping; this does not create a canonical sack count. The approved speech deliberately states no fixed fraction. Do not grant full grain after this branch.

**Take the share:** exact `hatcher_share`, explicit `Done.`, one200-cap payment, retained grain, actual lie option on returning. Repeats cannot pay twice. Opal's gratitude is her mistaken belief, not the narrator certifying a rescue. Belden's meal is real; agreeing to eat never consents to a provisioning agreement. No faction commitment is implemented by this road.

**Burn the occupied Queen:** present exact `pruitt_chain` warning that thirty people and the winter cargo are aboard, then explicit confirmation at the actual fire control. Do not offer a safe emptied-boat version or allow it after completed42. A staged fire, disabled/damaged boat configuration, absent recovered cargo and survivor/relief response must make the loss visible. The thirty occupants may be represented in the greybox; do not claim thirty actors were simulated or assign a death count without tracking it. No live actor is scripted to give a reply after death. This is an intentional dark choice, not a trap disguised as the rescue button.

## Cast loss, leaving and repeat safety

- Hatcher killed early: no card/share speech from a corpse. His crew may oppose the player; barge cut/fire actions remain available. Do not start unprovoked town-wide aggression from politely declining Opal.
- Rafferty dead: boarding and player-operated pilot control still work; use the authored half-cargo loss, without his confession/post-escape voice. If fire is offered without him, the same approved occupancy warning must be delivered as clearly labelled action UI before confirmation; no substitute NPC is invented.
- Opal dead: no voiced Opal reactions or automatic hanging. The cook-shed's actual cargo state and objective/status can acknowledge return; a separate anonymous cook is optional representation, not a required named character or new writing dependency. Completion remains possible.
- Belden dead/unavailable: no ghost relief speech or meal grant attributed to him. Lost grain remains lost; this does not block completion.
- Leaving unresolved, pausing, saving/loading, waiting in another area or calling an unbuilt fair never settles the barge or kills the town. Resolve only explicit completed actions. Re-entry resumes the same physical facts.
- Recheck cast, quest-running state, branch unresolved/resolved state and current context before committing any effect. Failed or stale actions do not pay, move custody, deliver cargo or set outcomes. A target failure after an effect is not a rollback mechanism.

## Return report and chapter boundary

The accepted pre-fair `pritchard_hears_river` branch immediately leads to calling the fair, and claims Opal sent a boy. Do not execute that entire source chain or fabricate that message. For this bounded native candidate, project only the exact speech from `pritchard_hears_river_after_fair` when evidence is known, or `_unknown` when it is not, into a new road-completion report action. Document that its original post-fair eligibility is not imported: no fair has occurred. This is the same explicit text-versus-eligibility projection discipline used by the accepted Mercy briefing.

The player can report the actual recovered/lost cargo and learned payment evidence. Store `RiverReportGiven`; keep the outcome and optional hire letter available in the journal. Do not set unrelated canonical MQ02 hub/fair stages merely because a similarly numbered local action occurred. End with separate availability UI: `Greenwater road complete. The other roads and the fair are not playable in this candidate.` This is a completed quest with a clear wider mystery, not an assertion that Chapter2 or ActI is finished.

## Acceptance handoff: one implementation, then independent tests

1. Charles returns a source/runtime mapping ledger first, with real allocation/bindings and declared staging choices, then implements the whole selected road. Missing native plumbing is implementation work, not a new request for already supplied story. No landscape/team work competes with this critical path.
2. Portable state tests exercise all four outcomes, card failure followed by another course, every optional judgment, evidence by letter/admission/none, dead key actors, unresolved departure/re-entry, save/load persistence and repeated/stale/cancelled actions. Independently inspect actual code; green model tests do not prove the plugin uses it.
3. Real-master build, script compile, plugin/VMAD/readback and correctly selected runtime artifacts must pass before isolated staging. Preserve the owner fallback and current save; do not silently overwrite the existing Details package under its old hash.
4. Independent native QA completes at least the straightforward cut-and-return path through Mercy report with normal stats, actual controller/keyboard choices, objective changes, cargo arrival, evidence optionality and reload persistence. QA also observes the card branch and its alternate judgment, the paid betrayal and fire consequences in separate controlled runs/saves. Capture outcomes; do not certify a branch from a console-set stage or the reference selector alone.
5. Record actual first-run duration, dialogue readability, confusion points, branch consequences and any remaining representational limits. If a source check passes but a physical action fails, fix that action before owner delivery. The owner receives one precise start command/launcher, what to try, current availability boundary and honest evidence of what was tested.

**Definition of done for this increment:** a player can leave Mercy, play one coherent Greenwater story with consequential alternatives, observe its result, finish the road and return a truthful report. Another briefing menu, a document grant alone or scenery around an unresolved quest does not meet that definition.
