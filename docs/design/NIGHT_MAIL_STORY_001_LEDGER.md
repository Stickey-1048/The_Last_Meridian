# Night Mail source and read-back ledger

This is the completed source candidate built from the interrupted `0d54b91` WIP. The immutable accepted baseline is `016b2b4005203ba180b908fb310a1653a95f934f`. Accepted writing is `d142104fdc6f72ae556f285a0166c1122893b991`; its text is unchanged. The implementation contract and reviews remain the authority. No licensed compile, installed package, terrain build or native Night Mail test has occurred in this worktree.

## Source and text projection

`NIGHT_MAIL_STORY_001_MAPPING.json` maps all 29 speech boxes, 88 build UI boxes, the complete three documents shown page by page, 24 road stages, seven objectives and every alias. Tests compare the written stand-in plugin against accepted JSON, and read the hymnal book directly from the binary. Exact accepted speech is retained, with three declared excerpt records: Lockridge's gate split between sentences (two records), and Dole's dead/absent-Billie share projection. Five button projections are explicit: gate first page Continue, drawer close, dead-Billie Continue, and two Mercy report buttons. Dole's offer without Billie makes no promise about her safety; the build's separate 150-cap offer follows. Post-fair source text is reused for the report; its original fair condition is not imported.

Accepted logs 20,30,41,43,44,50,55,63 require their stated actor/evidence context. Neutral separate stages 21,31,46,47,48,49,51,56,64 cover missing actors and oral admissions. Stage62 uses the approved neutral countersign log instead of claiming an overnight scene. No source text was rewritten. Optional evidence never blocks a core route. The collection plate remains accessible without Dole; a separate coat-looting route is omitted in this greybox.

Only three existing Greenwater UI records and three Mercy briefing UI fields change to the approved two-road availability. Opening footer and guide agree. All speech, old road rules and normal starting stats remain unchanged.

## State contract

| Fact | Representation | Commitment |
|---|---|---|
| Encounter | Outcome 0/41 run/42 defeated/43 sold/44 backed | Exclusive final encounter; later Dole death cannot overwrite it |
| Cargo | Mail 0 aboard/1 delivered/2 yard-retained/3 seized | Visible relevant cargo on, former cargo off, then acknowledgment |
| Engine/train | Engine 0 sound/1 damaged; Train 0 yard/1 Cut/2 platform/3 taken | Train label and current arrival have to agree; no motion physics |
| Dole | 0 alive/1 player-killed/2 otherwise dead | Actual actor event/death observations, separate from encounter |
| Stamp choice | 0 unresolved/61 keep/62 countersign/63 take | Living Lockridge needed to keep or countersign; taking alone allowed |
| Stamp receipt | StampDelivered 0/1 | Actual item leaves player and appears with actual MQ01 sheriff; pending observation may finish later |
| Yard authority | 0 held/1 withdrawn/2 vacant | Visible closed board; stamped/signed boards both off; living/dead Lockridge distinguished |
| Canon reported | LockridgeReported 0/1 | Stamp receipt AND acknowledged yard change, never merely taking/reporting |
| Road report | Reported 0/1 | Explicit Mercy report choice; not a replacement for stamp delivery |
| Knowledge | SilverRail/OstranderKnown | Observed plate/read complete flyleaf, or acknowledged oral admission; oral identity is not book custody |

The nine accepted flags have separate globals. No payer identity is invented. `DoleLives` is not a promise that Dole cannot later die. MQ01 and SQ01 facts are read, never rewritten. SQ01's actual final outcome/yard alert selects the gate greeting: report, sale and public posting remain distinct. All aliases are optional; no all-cast-alive global gate is used.

## Scene acknowledgment and retry ledger

| Operation | Actual source functions | What must be observed / retry rule |
|---|---|---|
| Entry | Travel / Arrived | Player reaches own-cell yard marker; cast succeeds before road start |
| Departure | Depart / CarryOutDepart | Exact Continue; current phase and actor context rechecked; arrival at Cut, lanterns/cargo/driver acknowledged |
| Run gap | Run / CarryOutRun | Staged notice, platform arrival, damaged engine and delivered cargo, Billie driving only when alive/present |
| Reverse | Reverse / CarryOutReverse | Yard arrival with retained cargo; line stays closed unless already cleared |
| Dole defeat | Died / CarryOutDefeat | Actual Dole death, each surviving rifle out of combat at retreat marker; mail remains aboard until separate onward/back scene |
| Post-defeat delivery | Forward / CarryOutForward | Player/driver arrival, sound engine and delivered cargo observed |
| Post-defeat return | CarryBack / CarryOutCarryBack | Yard retained cargo acknowledged; clear Cut remains clear |
| Paid seizure | TakeShare / CarryOutSale / FinishSale | Exactly one actual 150-cap grant; seized cargo on, Cut cargo off, surviving Billie at walking marker; unfinished scene retries without paying twice |
| Sale return context | AfterSale / FinishBillieReport | Separate explicit next-morning staged notice, living Billie back at yard and report acknowledged before Lockridge's full four-AM quotation |
| Countersign | Countersign / CarryOutCountersign | Exact Continue, living current Lockridge, signed board and held stock observed; no night clock simulation |
| Stamp acquisition | Take / CarryOutTake / ConfirmStampTaken | Actual one-time item grant plus drawer piece off; custody is separate from receipt |
| Stamp receipt | ReportTo / HandOver / HandoverSeen | Actual sheriff receives removed item; delayed observation records receipt without duplicating item |
| Authority | BeginAuthority / CarryOutAuthority / FinishAuthority | Closed board on, other boards off; retry only this unfinished part after receipt |
| Mercy report router | Act1Walk / ReportTo | Single menu <=4 options; exact cancel/stale state closes; intentional Later alone allows fallback |

The controller and rule quest both guard requests and acknowledgment. Transient operation claims prevent a second concurrent commitment. `Refresh` reflects recorded/pending facts; failed scenes do not silently complete. Current-player/actor/phase checks run again after modal responses. Labels explicitly call the floor an engine/rail/platform stand-in and say eleven miles, jumps and travel are staged.

## Own-cell and exterior binding

Five labelled zones occupy one new interior cell, `TLM_CELL_NightMail`. Three separate supported floor grids: yard/footplate, Cut/tabernacle, valley platform. No train physics, voice or navmesh is introduced. The fall trigger returns a player who steps off a floor. Native support/collision, trigger behavior and actor visibility remain unknown until the licensed build and playtest.

The exterior cloner appends one controller quest and exactly two persistent initially-disabled objects after the unchanged A1/Greenwater allocations. It leaves all 49 other forced aliases on their original master records, in the own cell, and all road facts in the one master MQ02A quest. It refuses missing/substituted aliases, the wrong owner cell and invalid road/router bindings. The synthetic binary readback below is not an exterior terrain build.

| Exterior alias | Position | Rationale |
|---|---|---|
| MercyTravel | 2950,2640,12 | Yard, ahead of cabin floor and clear of known actor/test points |
| MercyReturn | 3000,2580,32 | Ground in front of cabin, clear of Greenwater travel point; marker elevated to settle |

The stand-in test checks clearance from known placements. Actual ground/collision and where the player settles are native assumptions; this makes no native acceptance claim.

### Alias / actual source placement table

| ID | Alias | Master reference | Cell | Position | Exterior owner |
|---:|---|---|---|---|---|
| 0 | MercyTravel | `000A08:TheLastMeridian.esp` | QASmoke | 1760,-740,76 | TLMWorldSlice.esp |
| 1 | MercyReturn | `000A09:TheLastMeridian.esp` | QASmoke | 1720,-700,64 | TLMWorldSlice.esp |
| 2 | YardArrival | `000A0B:TheLastMeridian.esp` | TLM_CELL_NightMail | 256,160,16 | TheLastMeridian.esp |
| 3 | Rules | `000A0C:TheLastMeridian.esp` | TLM_CELL_NightMail | 400,60,12 | TheLastMeridian.esp |
| 4 | LabelYard | `000A0D:TheLastMeridian.esp` | TLM_CELL_NightMail | 120,60,12 | TheLastMeridian.esp |
| 5 | Exit | `000A0E:TheLastMeridian.esp` | TLM_CELL_NightMail | 20,300,12 | TheLastMeridian.esp |
| 6 | Lockridge | `000A0F:TheLastMeridian.esp` | TLM_CELL_NightMail | 256,420,16 | TheLastMeridian.esp |
| 7 | Drawer | `000A10:TheLastMeridian.esp` | TLM_CELL_NightMail | 120,500,12 | TheLastMeridian.esp |
| 8 | StampInDrawer | `000A11:TheLastMeridian.esp` | TLM_CELL_NightMail | 60,500,12 | TheLastMeridian.esp |
| 9 | BoardStamped | `000A12:TheLastMeridian.esp` | TLM_CELL_NightMail | 400,520,12 | TheLastMeridian.esp |
| 10 | BoardSigned | `000A13:TheLastMeridian.esp` | TLM_CELL_NightMail | 400,520,12 | TheLastMeridian.esp |
| 11 | BoardClosed | `000A14:TheLastMeridian.esp` | TLM_CELL_NightMail | 400,520,12 | TheLastMeridian.esp |
| 12 | HeldStock | `000A15:TheLastMeridian.esp` | TLM_CELL_NightMail | 560,520,12 | TheLastMeridian.esp |
| 13 | CargoRetained | `000A16:TheLastMeridian.esp` | TLM_CELL_NightMail | 600,300,12 | TheLastMeridian.esp |
| 14 | BillieYard | `000A17:TheLastMeridian.esp` | TLM_CELL_NightMail | 400,300,16 | TheLastMeridian.esp |
| 15 | BillieFootplate | `000A69:TheLastMeridian.esp` | TLM_CELL_NightMail | 1040,400,16 | TheLastMeridian.esp |
| 16 | LabelFootplate | `000A18:TheLastMeridian.esp` | TLM_CELL_NightMail | 760,60,12 | TheLastMeridian.esp |
| 17 | YardFootplate | `000A19:TheLastMeridian.esp` | TLM_CELL_NightMail | 880,256,16 | TheLastMeridian.esp |
| 18 | Billie | `000A1A:TheLastMeridian.esp` | TLM_CELL_NightMail | 1040,400,16 | TheLastMeridian.esp |
| 19 | Depart | `000A1B:TheLastMeridian.esp` | TLM_CELL_NightMail | 1040,120,12 | TheLastMeridian.esp |
| 20 | CargoAboard | `000A1C:TheLastMeridian.esp` | TLM_CELL_NightMail | 760,480,12 | TheLastMeridian.esp |
| 21 | CutArrival | `000A1D:TheLastMeridian.esp` | TLM_CELL_NightMail | 3200,256,16 | TheLastMeridian.esp |
| 22 | LabelCut | `000A1E:TheLastMeridian.esp` | TLM_CELL_NightMail | 3060,60,12 | TheLastMeridian.esp |
| 23 | BillieCut | `000A1F:TheLastMeridian.esp` | TLM_CELL_NightMail | 3340,400,16 | TheLastMeridian.esp |
| 24 | Regulator | `000A20:TheLastMeridian.esp` | TLM_CELL_NightMail | 3340,120,12 | TheLastMeridian.esp |
| 25 | Reverser | `000A21:TheLastMeridian.esp` | TLM_CELL_NightMail | 3200,120,12 | TheLastMeridian.esp |
| 26 | CargoAtCut | `000A22:TheLastMeridian.esp` | TLM_CELL_NightMail | 3060,400,12 | TheLastMeridian.esp |
| 27 | BackFromCut | `000A23:TheLastMeridian.esp` | TLM_CELL_NightMail | 2990,256,12 | TheLastMeridian.esp |
| 28 | BillieWalk | `000A24:TheLastMeridian.esp` | TLM_CELL_NightMail | 3000,540,16 | TheLastMeridian.esp |
| 29 | Lanterns | `000A25:TheLastMeridian.esp` | TLM_CELL_NightMail | 3560,256,12 | TheLastMeridian.esp |
| 30 | Dole | `000A26:TheLastMeridian.esp` | TLM_CELL_NightMail | 3800,256,16 | TheLastMeridian.esp |
| 31 | Rifle1 | `000A27:TheLastMeridian.esp` | TLM_CELL_NightMail | 3940,120,16 | TheLastMeridian.esp |
| 32 | Rifle2 | `000A28:TheLastMeridian.esp` | TLM_CELL_NightMail | 3940,400,16 | TheLastMeridian.esp |
| 33 | Rifle3 | `000A29:TheLastMeridian.esp` | TLM_CELL_NightMail | 3980,256,16 | TheLastMeridian.esp |
| 34 | CargoSeized | `000A2A:TheLastMeridian.esp` | TLM_CELL_NightMail | 3700,500,12 | TheLastMeridian.esp |
| 35 | Retreat1 | `000A2B:TheLastMeridian.esp` | TLM_CELL_NightMail | 4640,40,16 | TheLastMeridian.esp |
| 36 | Retreat2 | `000A2C:TheLastMeridian.esp` | TLM_CELL_NightMail | 4640,256,16 | TheLastMeridian.esp |
| 37 | Retreat3 | `000A2D:TheLastMeridian.esp` | TLM_CELL_NightMail | 4640,480,16 | TheLastMeridian.esp |
| 38 | LabelSiding | `000A2E:TheLastMeridian.esp` | TLM_CELL_NightMail | 4160,60,12 | TheLastMeridian.esp |
| 39 | Hymnal | `000A2F:TheLastMeridian.esp` | TLM_CELL_NightMail | 4200,520,12 | TheLastMeridian.esp |
| 40 | Plate | `000A30:TheLastMeridian.esp` | TLM_CELL_NightMail | 4340,520,12 | TheLastMeridian.esp |
| 41 | Chalk | `000A31:TheLastMeridian.esp` | TLM_CELL_NightMail | 4400,120,12 | TheLastMeridian.esp |
| 42 | PlatformArrival | `000A32:TheLastMeridian.esp` | TLM_CELL_NightMail | 6272,256,16 | TheLastMeridian.esp |
| 43 | LabelPlatform | `000A33:TheLastMeridian.esp` | TLM_CELL_NightMail | 6130,60,12 | TheLastMeridian.esp |
| 44 | BilliePlatform | `000A34:TheLastMeridian.esp` | TLM_CELL_NightMail | 6420,400,16 | TheLastMeridian.esp |
| 45 | CargoDelivered | `000A35:TheLastMeridian.esp` | TLM_CELL_NightMail | 6560,500,12 | TheLastMeridian.esp |
| 46 | EngineSound | `000A36:TheLastMeridian.esp` | TLM_CELL_NightMail | 6420,120,12 | TheLastMeridian.esp |
| 47 | EngineDamaged | `000A37:TheLastMeridian.esp` | TLM_CELL_NightMail | 6420,120,12 | TheLastMeridian.esp |
| 48 | PlatformExit | `000A38:TheLastMeridian.esp` | TLM_CELL_NightMail | 6700,300,12 | TheLastMeridian.esp |
| 49 | BackFromPlatform | `000A39:TheLastMeridian.esp` | TLM_CELL_NightMail | 6130,480,12 | TheLastMeridian.esp |
| 50 | Fall | `000A3A:TheLastMeridian.esp` | TLM_CELL_NightMail | 3328,256,-700 | TheLastMeridian.esp |

### Allocation ledger

Earlier 335 IDs remain an exact prefix; 283 new IDs follow contiguously. Hex below is plugin-local, not a loaded-game console ID. The current formkeys file and candidate manifest pin the actual numbers.

| Editor ID | Local ID |
|---|---:|
| `TLM_G_MQ02A_Outcome` | `0x00094F` |
| `TLM_G_MQ02A_Mail` | `0x000950` |
| `TLM_G_MQ02A_Engine` | `0x000951` |
| `TLM_G_MQ02A_Train` | `0x000952` |
| `TLM_G_MQ02A_Dole` | `0x000953` |
| `TLM_G_MQ02A_Stamp` | `0x000954` |
| `TLM_G_MQ02A_StampDelivered` | `0x000955` |
| `TLM_G_MQ02A_YardAuthority` | `0x000956` |
| `TLM_G_MQ02A_Reported` | `0x000957` |
| `TLM_G_MQ02A_MailThrough` | `0x000958` |
| `TLM_G_MQ02A_MailSold` | `0x000959` |
| `TLM_G_MQ02A_LineClosed` | `0x00095A` |
| `TLM_G_MQ02A_DoleLives` | `0x00095B` |
| `TLM_G_MQ02A_SilverRail` | `0x00095C` |
| `TLM_G_MQ02A_OstranderKnown` | `0x00095D` |
| `TLM_G_MQ02A_LockridgeStamping` | `0x00095E` |
| `TLM_G_MQ02A_LockridgeSigned` | `0x00095F` |
| `TLM_G_MQ02A_LockridgeReported` | `0x000960` |
| `TLM_Fac_IronJunction` | `0x000961` |
| `TLM_Fac_BlackRail` | `0x000962` |
| `TLM_MISC_OstranderStamp` | `0x000963` |
| `TLM_ACTI_NM_Travel` | `0x000964` |
| `TLM_ACTI_NM_Rules` | `0x000965` |
| `TLM_ACTI_NM_LabelYard` | `0x000966` |
| `TLM_ACTI_NM_Exit` | `0x000967` |
| `TLM_ACTI_NM_Drawer` | `0x000968` |
| `TLM_ACTI_NM_StampInDrawer` | `0x000969` |
| `TLM_ACTI_NM_BoardStamped` | `0x00096A` |
| `TLM_ACTI_NM_BoardSigned` | `0x00096B` |
| `TLM_ACTI_NM_BoardClosed` | `0x00096C` |
| `TLM_ACTI_NM_HeldStock` | `0x00096D` |
| `TLM_ACTI_NM_CargoRetained` | `0x00096E` |
| `TLM_ACTI_NM_LabelFootplate` | `0x00096F` |
| `TLM_ACTI_NM_Depart` | `0x000970` |
| `TLM_ACTI_NM_CargoAboard` | `0x000971` |
| `TLM_ACTI_NM_LabelCut` | `0x000972` |
| `TLM_ACTI_NM_Regulator` | `0x000973` |
| `TLM_ACTI_NM_Reverser` | `0x000974` |
| `TLM_ACTI_NM_CargoAtCut` | `0x000975` |
| `TLM_ACTI_NM_BackFromCut` | `0x000976` |
| `TLM_ACTI_NM_Lanterns` | `0x000977` |
| `TLM_ACTI_NM_CargoSeized` | `0x000978` |
| `TLM_ACTI_NM_LabelSiding` | `0x000979` |
| `TLM_ACTI_NM_Hymnal` | `0x00097A` |
| `TLM_ACTI_NM_Plate` | `0x00097B` |
| `TLM_ACTI_NM_Chalk` | `0x00097C` |
| `TLM_ACTI_NM_LabelPlatform` | `0x00097D` |
| `TLM_ACTI_NM_CargoDelivered` | `0x00097E` |
| `TLM_ACTI_NM_EngineSound` | `0x00097F` |
| `TLM_ACTI_NM_EngineDamaged` | `0x000980` |
| `TLM_ACTI_NM_PlatformExit` | `0x000981` |
| `TLM_ACTI_NM_BackFromPlatform` | `0x000982` |
| `TLM_TRIG_NM_Fall` | `0x000983` |
| `TLM_NPC_YARDMASTER_IRONJUNCTION` | `0x000984` |
| `TLM_NPC_DRIVER_NIGHTMAIL` | `0x000985` |
| `TLM_NPC_PREACHER_BLACKRAIL` | `0x000986` |
| `TLM_NPC_BLACKRAIL_01` | `0x000987` |
| `TLM_NPC_BLACKRAIL_02` | `0x000988` |
| `TLM_NPC_BLACKRAIL_03` | `0x000989` |
| `TLM_BOOK_HymnalFlyleaf` | `0x00098A` |
| `TLM_MQ02A` | `0x00098B` |
| `TLM_NM` | `0x00098C` |
| `TLM_MSG_NM_LockridgeDefault` | `0x00098D` |
| `TLM_MSG_NM_LockridgeGateA` | `0x00098E` |
| `TLM_MSG_NM_LockridgeGateB` | `0x00098F` |
| `TLM_MSG_NM_LockridgeGateAlerted` | `0x000990` |
| `TLM_MSG_NM_LockridgeGateSold` | `0x000991` |
| `TLM_MSG_NM_LockridgeDole` | `0x000992` |
| `TLM_MSG_NM_LockridgeRails` | `0x000993` |
| `TLM_MSG_NM_LockridgeHired` | `0x000994` |
| `TLM_MSG_NM_LockridgeAfterRan` | `0x000995` |
| `TLM_MSG_NM_LockridgeAfterDole` | `0x000996` |
| `TLM_MSG_NM_LockridgeAfterSold` | `0x000997` |
| `TLM_MSG_NM_LockridgeHymnal` | `0x000998` |
| `TLM_MSG_NM_LockridgeStamp` | `0x000999` |
| `TLM_MSG_NM_BillieDefault` | `0x00099A` |
| `TLM_MSG_NM_BillieFootplate` | `0x00099B` |
| `TLM_MSG_NM_BillieCutBefore` | `0x00099C` |
| `TLM_MSG_NM_BillieInCut` | `0x00099D` |
| `TLM_MSG_NM_BillieRan` | `0x00099E` |
| `TLM_MSG_NM_BillieBacked` | `0x00099F` |
| `TLM_MSG_NM_BillieWalking` | `0x0009A0` |
| `TLM_MSG_NM_DoleDefault` | `0x0009A1` |
| `TLM_MSG_NM_DoleSermon` | `0x0009A2` |
| `TLM_MSG_NM_DoleName` | `0x0009A3` |
| `TLM_MSG_NM_DoleSilver` | `0x0009A4` |
| `TLM_MSG_NM_DoleShare` | `0x0009A5` |
| `TLM_MSG_NM_DoleShareNoBillie` | `0x0009A6` |
| `TLM_MSG_NM_DoleFace` | `0x0009A7` |
| `TLM_MSG_NM_ReportKnown` | `0x0009A8` |
| `TLM_MSG_NM_ReportUnknown` | `0x0009A9` |
| `TLM_MSG_NM_AskTravel` | `0x0009AA` |
| `TLM_MSG_NM_AskTravelAgain` | `0x0009AB` |
| `TLM_MSG_NM_NoteTravelNotYet` | `0x0009AC` |
| `TLM_MSG_NM_NoteTravelFailed` | `0x0009AD` |
| `TLM_MSG_NM_NoteNotAssigned` | `0x0009AE` |
| `TLM_MSG_NM_AskBoard` | `0x0009AF` |
| `TLM_MSG_NM_NoteAssignedNoBillie` | `0x0009B0` |
| `TLM_MSG_NM_AskDepartScene` | `0x0009B1` |
| `TLM_MSG_NM_AskRejoin` | `0x0009B2` |
| `TLM_MSG_NM_NoteTrainNothing` | `0x0009B3` |
| `TLM_MSG_NM_AskRegulator` | `0x0009B4` |
| `TLM_MSG_NM_AskRunScene` | `0x0009B5` |
| `TLM_MSG_NM_AskReverseScene` | `0x0009B6` |
| `TLM_MSG_NM_AskAfterDefeat` | `0x0009B7` |
| `TLM_MSG_NM_AskForwardScene` | `0x0009B8` |
| `TLM_MSG_NM_AskCarryBackScene` | `0x0009B9` |
| `TLM_MSG_NM_NoteSceneFailed` | `0x0009BA` |
| `TLM_MSG_NM_NoteSceneStuck` | `0x0009BB` |
| `TLM_MSG_NM_NoteRunDone` | `0x0009BC` |
| `TLM_MSG_NM_NoteForwardDone` | `0x0009BD` |
| `TLM_MSG_NM_NoteBackedOut` | `0x0009BE` |
| `TLM_MSG_NM_NoteCarriedBack` | `0x0009BF` |
| `TLM_MSG_NM_NoteDefeat` | `0x0009C0` |
| `TLM_MSG_NM_AskShareOffer` | `0x0009C1` |
| `TLM_MSG_NM_NoteShareFailed` | `0x0009C2` |
| `TLM_MSG_NM_NoteSold` | `0x0009C3` |
| `TLM_MSG_NM_NoteSoldNoBillie` | `0x0009C4` |
| `TLM_MSG_NM_NoteSalePending` | `0x0009C5` |
| `TLM_MSG_NM_NotePlate` | `0x0009C6` |
| `TLM_MSG_NM_NoteDrawer` | `0x0009C7` |
| `TLM_MSG_NM_AskStampAlone` | `0x0009C8` |
| `TLM_MSG_NM_NoteStampKept` | `0x0009C9` |
| `TLM_MSG_NM_AskCountersignScene` | `0x0009CA` |
| `TLM_MSG_NM_NoteCountersigned` | `0x0009CB` |
| `TLM_MSG_NM_NoteStampTaken` | `0x0009CC` |
| `TLM_MSG_NM_NoteStampFailed` | `0x0009CD` |
| `TLM_MSG_NM_NoteDecisionFailed` | `0x0009CE` |
| `TLM_MSG_NM_NoteDrawerKept` | `0x0009CF` |
| `TLM_MSG_NM_NoteDrawerSigned` | `0x0009D0` |
| `TLM_MSG_NM_NoteDrawerGone` | `0x0009D1` |
| `TLM_MSG_NM_AskShowHymnal` | `0x0009D2` |
| `TLM_MSG_NM_NoteNoDispatch` | `0x0009D3` |
| `TLM_MSG_NM_NoteSaleStatus` | `0x0009D4` |
| `TLM_MSG_NM_AskBillieReport` | `0x0009D5` |
| `TLM_MSG_NM_AskBackToYard` | `0x0009D6` |
| `TLM_MSG_NM_AskLeaveResolved` | `0x0009D7` |
| `TLM_MSG_NM_AskLeaveUnresolved` | `0x0009D8` |
| `TLM_MSG_NM_AskLeaveAgain` | `0x0009D9` |
| `TLM_MSG_NM_NoteRoadComplete` | `0x0009DA` |
| `TLM_MSG_NM_NoteLeftUnresolved` | `0x0009DB` |
| `TLM_MSG_NM_NoteFall` | `0x0009DC` |
| `TLM_MSG_NM_LabelYard` | `0x0009DD` |
| `TLM_MSG_NM_LabelFootplate` | `0x0009DE` |
| `TLM_MSG_NM_LabelCut` | `0x0009DF` |
| `TLM_MSG_NM_LabelSiding` | `0x0009E0` |
| `TLM_MSG_NM_LabelPlatform` | `0x0009E1` |
| `TLM_MSG_NM_LabelLanterns` | `0x0009E2` |
| `TLM_MSG_NM_LabelCargoAboard` | `0x0009E3` |
| `TLM_MSG_NM_LabelCargoDelivered` | `0x0009E4` |
| `TLM_MSG_NM_LabelCargoRetained` | `0x0009E5` |
| `TLM_MSG_NM_LabelCargoSeized` | `0x0009E6` |
| `TLM_MSG_NM_LabelEngineSound` | `0x0009E7` |
| `TLM_MSG_NM_LabelEngineDamaged` | `0x0009E8` |
| `TLM_MSG_NM_LabelBoardStamped` | `0x0009E9` |
| `TLM_MSG_NM_LabelBoardSigned` | `0x0009EA` |
| `TLM_MSG_NM_LabelBoardClosed` | `0x0009EB` |
| `TLM_MSG_NM_LabelHeldStock` | `0x0009EC` |
| `TLM_MSG_NM_ReportMailDelivered` | `0x0009ED` |
| `TLM_MSG_NM_ReportMailRetained` | `0x0009EE` |
| `TLM_MSG_NM_ReportMailSeized` | `0x0009EF` |
| `TLM_MSG_NM_ReportMailAboard` | `0x0009F0` |
| `TLM_MSG_NM_ReportRan` | `0x0009F1` |
| `TLM_MSG_NM_ReportDoleByYou` | `0x0009F2` |
| `TLM_MSG_NM_ReportDoleDead` | `0x0009F3` |
| `TLM_MSG_NM_ReportSold` | `0x0009F4` |
| `TLM_MSG_NM_ReportBacked` | `0x0009F5` |
| `TLM_MSG_NM_ReportKnowBoth` | `0x0009F6` |
| `TLM_MSG_NM_ReportKnowSilver` | `0x0009F7` |
| `TLM_MSG_NM_ReportKnowName` | `0x0009F8` |
| `TLM_MSG_NM_ReportKnowNeither` | `0x0009F9` |
| `TLM_MSG_NM_ReportEnd` | `0x0009FA` |
| `TLM_MSG_NM_AskHandOver` | `0x0009FB` |
| `TLM_MSG_NM_NoteStampDelivered` | `0x0009FC` |
| `TLM_MSG_NM_NoteHandoverFailed` | `0x0009FD` |
| `TLM_MSG_NM_NoteAuthorityWithdrawn` | `0x0009FE` |
| `TLM_MSG_NM_NoteAuthorityVacant` | `0x0009FF` |
| `TLM_MSG_NM_NoteAuthorityFailed` | `0x000A00` |
| `TLM_MSG_NM_RulesPage1` | `0x000A01` |
| `TLM_MSG_NM_RulesPage2` | `0x000A02` |
| `TLM_MSG_NM_RulesPage3` | `0x000A03` |
| `TLM_MSG_NM_RulesPage4` | `0x000A04` |
| `TLM_MSG_NM_ChalkPage1` | `0x000A05` |
| `TLM_MSG_NM_FlyleafPage1` | `0x000A06` |
| `TLM_MSG_NM_FlyleafPage2` | `0x000A07` |
| `TLM_REF_NM_MercyTravel` | `0x000A08` |
| `TLM_REF_NM_MercyReturn` | `0x000A09` |
| `TLM_CELL_NightMail` | `0x000A0A` |
| `TLM_REF_NM_YardArrival` | `0x000A0B` |
| `TLM_REF_NM_Rules` | `0x000A0C` |
| `TLM_REF_NM_LabelYard` | `0x000A0D` |
| `TLM_REF_NM_Exit` | `0x000A0E` |
| `TLM_REF_NM_Lockridge` | `0x000A0F` |
| `TLM_REF_NM_Drawer` | `0x000A10` |
| `TLM_REF_NM_StampInDrawer` | `0x000A11` |
| `TLM_REF_NM_BoardStamped` | `0x000A12` |
| `TLM_REF_NM_BoardSigned` | `0x000A13` |
| `TLM_REF_NM_BoardClosed` | `0x000A14` |
| `TLM_REF_NM_HeldStock` | `0x000A15` |
| `TLM_REF_NM_CargoRetained` | `0x000A16` |
| `TLM_REF_NM_BillieYard` | `0x000A17` |
| `TLM_REF_NM_LabelFootplate` | `0x000A18` |
| `TLM_REF_NM_YardFootplate` | `0x000A19` |
| `TLM_REF_NM_Billie` | `0x000A1A` |
| `TLM_REF_NM_Depart` | `0x000A1B` |
| `TLM_REF_NM_CargoAboard` | `0x000A1C` |
| `TLM_REF_NM_CutArrival` | `0x000A1D` |
| `TLM_REF_NM_LabelCut` | `0x000A1E` |
| `TLM_REF_NM_BillieCut` | `0x000A1F` |
| `TLM_REF_NM_Regulator` | `0x000A20` |
| `TLM_REF_NM_Reverser` | `0x000A21` |
| `TLM_REF_NM_CargoAtCut` | `0x000A22` |
| `TLM_REF_NM_BackFromCut` | `0x000A23` |
| `TLM_REF_NM_BillieWalk` | `0x000A24` |
| `TLM_REF_NM_Lanterns` | `0x000A25` |
| `TLM_REF_NM_Dole` | `0x000A26` |
| `TLM_REF_NM_Rifle1` | `0x000A27` |
| `TLM_REF_NM_Rifle2` | `0x000A28` |
| `TLM_REF_NM_Rifle3` | `0x000A29` |
| `TLM_REF_NM_CargoSeized` | `0x000A2A` |
| `TLM_REF_NM_Retreat1` | `0x000A2B` |
| `TLM_REF_NM_Retreat2` | `0x000A2C` |
| `TLM_REF_NM_Retreat3` | `0x000A2D` |
| `TLM_REF_NM_LabelSiding` | `0x000A2E` |
| `TLM_REF_NM_Hymnal` | `0x000A2F` |
| `TLM_REF_NM_Plate` | `0x000A30` |
| `TLM_REF_NM_Chalk` | `0x000A31` |
| `TLM_REF_NM_PlatformArrival` | `0x000A32` |
| `TLM_REF_NM_LabelPlatform` | `0x000A33` |
| `TLM_REF_NM_BilliePlatform` | `0x000A34` |
| `TLM_REF_NM_CargoDelivered` | `0x000A35` |
| `TLM_REF_NM_EngineSound` | `0x000A36` |
| `TLM_REF_NM_EngineDamaged` | `0x000A37` |
| `TLM_REF_NM_PlatformExit` | `0x000A38` |
| `TLM_REF_NM_BackFromPlatform` | `0x000A39` |
| `TLM_REF_NM_Fall` | `0x000A3A` |
| `TLM_REF_NM_Floor_A00` | `0x000A3B` |
| `TLM_REF_NM_Floor_A01` | `0x000A3C` |
| `TLM_REF_NM_Floor_A02` | `0x000A3D` |
| `TLM_REF_NM_Floor_A10` | `0x000A3E` |
| `TLM_REF_NM_Floor_A11` | `0x000A3F` |
| `TLM_REF_NM_Floor_A12` | `0x000A40` |
| `TLM_REF_NM_Floor_A20` | `0x000A41` |
| `TLM_REF_NM_Floor_A21` | `0x000A42` |
| `TLM_REF_NM_Floor_A22` | `0x000A43` |
| `TLM_REF_NM_Floor_A30` | `0x000A44` |
| `TLM_REF_NM_Floor_A31` | `0x000A45` |
| `TLM_REF_NM_Floor_A32` | `0x000A46` |
| `TLM_REF_NM_Floor_A40` | `0x000A47` |
| `TLM_REF_NM_Floor_A41` | `0x000A48` |
| `TLM_REF_NM_Floor_A42` | `0x000A49` |
| `TLM_REF_NM_Floor_B00` | `0x000A4A` |
| `TLM_REF_NM_Floor_B01` | `0x000A4B` |
| `TLM_REF_NM_Floor_B02` | `0x000A4C` |
| `TLM_REF_NM_Floor_B10` | `0x000A4D` |
| `TLM_REF_NM_Floor_B11` | `0x000A4E` |
| `TLM_REF_NM_Floor_B12` | `0x000A4F` |
| `TLM_REF_NM_Floor_B20` | `0x000A50` |
| `TLM_REF_NM_Floor_B21` | `0x000A51` |
| `TLM_REF_NM_Floor_B22` | `0x000A52` |
| `TLM_REF_NM_Floor_B30` | `0x000A53` |
| `TLM_REF_NM_Floor_B31` | `0x000A54` |
| `TLM_REF_NM_Floor_B32` | `0x000A55` |
| `TLM_REF_NM_Floor_B40` | `0x000A56` |
| `TLM_REF_NM_Floor_B41` | `0x000A57` |
| `TLM_REF_NM_Floor_B42` | `0x000A58` |
| `TLM_REF_NM_Floor_B50` | `0x000A59` |
| `TLM_REF_NM_Floor_B51` | `0x000A5A` |
| `TLM_REF_NM_Floor_B52` | `0x000A5B` |
| `TLM_REF_NM_Floor_B60` | `0x000A5C` |
| `TLM_REF_NM_Floor_B61` | `0x000A5D` |
| `TLM_REF_NM_Floor_B62` | `0x000A5E` |
| `TLM_REF_NM_Floor_C00` | `0x000A5F` |
| `TLM_REF_NM_Floor_C01` | `0x000A60` |
| `TLM_REF_NM_Floor_C02` | `0x000A61` |
| `TLM_REF_NM_Floor_C10` | `0x000A62` |
| `TLM_REF_NM_Floor_C11` | `0x000A63` |
| `TLM_REF_NM_Floor_C12` | `0x000A64` |
| `TLM_REF_NM_Floor_C20` | `0x000A65` |
| `TLM_REF_NM_Floor_C21` | `0x000A66` |
| `TLM_REF_NM_Floor_C22` | `0x000A67` |
| `TLM_MSG_NM_AskWalkToCut` | `0x000A68` |
| `TLM_REF_NM_BillieFootplate` | `0x000A69` |

## Actual source checks

All five portable phases completed successfully. On this Windows worktree the runner was copied into ignored `build/run-portable-diagnostics.sh` solely to select the real Python interpreter, preserve full unittest diagnostics instead of `tail -4`, and keep generated temporary masters under this worktree without cleanup. No test assertion was removed. Full diagnostic output remains at `build/portable-completion.log` in this isolated worktree.

- Existing model suite: 142 tests, eight pre-existing engine-only placeholders skipped. The six added Night Mail model contract tests passed separately (all eight combinations of living/dead Lockridge/Billie and run/reverse also checked inside them).
- Final full stand-in script suite: **743 tests passed**, no skips. This includes actual controller/model comparisons, coexistence, adversarial calls/modal responses, **56** Night Mail guard-removal mutation trials (counted from the actual trial table), historical 016b candidate verification/mutations, binary cloning/readback and projection tests.
- Strengthened final projection/own-cell checks: **10 passed**, including the extra own-cell/floor assertion added after full-suite discovery; current candidate provenance/mutation/selection checks: **six passed**. No older check was substituted for these focused checks.
- Both scenario replays passed: **65/65 scenarios, 1,628 checks**, normally and with every external call taking a frame at 60 calls/second.
- .NET builders/self-readback, independent plugin byte-layout self-tests, story intake/revision/consistency checks, output/launcher/stager refusal fixtures, and all **eight generated-master lookup/layout variants** passed; allocated IDs remained unchanged across builds.
- PowerShell 7 actually executed **five Night Mail package refusals** and **32 Greenwater package refusals**, with no package build/compiler/game/install execution. The latter first rejects current Night Mail source then exercises every original guard on the exact 016b export. Windows PowerShell 5.1 execution was blocked by the existing script policy; no policy was changed and no 5.1 execution pass is claimed.
- `tools/night_mail_story_candidate.py verify` and `git diff --check` passed. Generated masters and diagnostic binaries are ignored workspace outputs, not accepted or licensed artifacts.

The first remote run on `d5597a9` reached 744 script tests and reported one error. The new book check had assumed the bootstrap binary existed in `build/sim`; the canonical runner copies only JSON there. The follow-up reads the actual skeleton binary at `build/TheLastMeridian.esp`, as the existing book checks do. All ten projection checks passed again with the accidental bootstrap binary removed from that expected path. The portable runner now preserves full unittest diagnostics instead of truncating the traceback. Replacement remote CI is a separate gate; see the PR's exact-head checks rather than inferring a remote pass from the local run.

## Build selection and native gate

Own verifier: `tools/night_mail_story_candidate.py verify`. Own opt-in packager: `tools/win/Build-NightMail.ps1`; it runs that complete verifier before any output and fails closed, requires all 26 freshly compiled scripts and the compile log, selects only 17 source-identical measured Details PEX plus nine fresh ones, and measures results without creating artifact pins. No earlier packager, manifest, stager or launcher is retargeted. Full licensed packaging remains unrun.

Frozen Greenwater candidate tests export exact 016b from Git, build its own stand-in plugin, and run the original source verifier and mutation checks on that export. A separate live assertion requires its verifier to reject this newer source for the changed scripts. The earlier pins and verifier are unchanged. No test skips or waiver was added; the legacy model matrix's eight existing engine-only skipped placeholders remain explicitly native work, never a portable pass claim.

Root must independently review source, compile all 26 against the owner's licensed inputs, preserve the compile log/source manifest, select runtime by the nine-fresh/seventeen-reviewed policy, build/read back the full exterior, run both route orders with MQ01/SQ01, and test all four Night Mail outcomes, optional evidence, three stamp choices, delayed/refused item operations, living/dead cast and authority withdrawal in the game. Persistent saves/new-cell/navmesh/settling/modal timing/controller interactions have no native proof from this source work. No owner install, save/profile changes, artifacts or acceptance pins were produced here.
