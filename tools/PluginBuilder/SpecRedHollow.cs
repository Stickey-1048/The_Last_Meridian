using System.Text.Json;

namespace Tlm.PluginBuilder;

// RED-HOLLOW-STORY-001. Exact accepted JSON is a BUILD INPUT, never a game dependency.
// A source candidate, not licensed/native acceptance. Four canonical actors and eleven
// unnamed physical roles; the condemned actor is NEVER allocated here: it is MQ01's.
public static class RedHollow
{
    public const string RoadId="TLM_MQ02C", StageId="TLM_RH", CellId="TLM_CELL_RedHollow", Prefix="TLM_MSG_RH_";
    public const string LampId="TLM_MISC_RH_Lamp", KeyId="TLM_MISC_RH_FiringKey", ReceiptId="TLM_MISC_RH_Receipt";
    public const string Available="Three roads are playable. Four Flags entry is available after the first section.";
    public const string Complete="Red Hollow road complete. Three roads and Four Flags entry remain available.";
    public const int Limit=240;
    public static readonly string[] ClockMenus={"LoadingMenu","Console","LevelUpMenu","MessageBoxMenu","ContainerMenu","ExamineMenu","CookingMenu","ExamineConfirmMenu","RobotModMenu","PowerArmorModMenu","WorkshopMenu","PromptMenu","SitWaitMenu","SleepWaitMenu","DialogueMenu","BarterMenu","LockpickingMenu","BookMenu","SPECIALMenu","FavoritesMenu","PauseMenu","VATSMenu","PipboyMenu","PipboyHolotapeMenu","TerminalMenu","LooksMenu"};
    static string StoryRoot(){var d=new DirectoryInfo(AppContext.BaseDirectory);while(d!=null){var p=Path.Combine(d.FullName,"assets/incoming/act1/story");if(Directory.Exists(p))return p;d=d.Parent;}throw new InvalidDataException("Accepted story inputs missing");}
    static JsonElement Load(string path)=>JsonDocument.Parse(File.ReadAllText(Path.Combine(StoryRoot(),path))).RootElement.Clone();
    public static readonly Dictionary<string,JsonElement> Lines=Load("talk/tlm_mq02c.json").GetProperty("lines").EnumerateArray()
        .Concat(Load("talk/tlm_mq02.json").GetProperty("lines").EnumerateArray().Where(l=>l.GetProperty("id").GetString()!.StartsWith("pritchard_hears_pike_after_fair")))
        .ToDictionary(l=>l.GetProperty("id").GetString()!,l=>l);
    static readonly Dictionary<string,string> Names=Load("characters.json").GetProperty("characters").EnumerateArray().ToDictionary(c=>c.GetProperty("id").GetString()!,c=>c.GetProperty("name").GetString()!);
    static string SpeakerName(string id)=>id=="cutter"?"Tellico Cutter":Names[id];
    public static readonly string[] NodeNames=Lines.Keys.ToArray();
    public static string[] Labels(string node)=>Lines[node].TryGetProperty("buttons",out var b)?b.EnumerateArray().Select(x=>x.GetProperty("label").GetString()!).ToArray():new[]{"Continue"};
    public static string[] SpeechPages(string node){var e=Lines[node];var name=SpeakerName(e.GetProperty("speaker").GetString()!);return Wrap(e.GetProperty("text").GetString()!,Limit-name.Length-4).ToArray();}
    static IEnumerable<string> Wrap(string text,int room){while(text.Length>room){int cut=text.LastIndexOf(' ',room);if(cut<1)throw new InvalidDataException("Unsplit story word");yield return text[..cut];text=text[(cut+1)..];}yield return text;}
    public static readonly string[] Canonical={"RopeShot","NeckOwed","QuillShamed","SilverRoad","ShiftSaved","HollowLine","BreakBlown","MouthShut","LampTaken","Docket2298Held","SilverMine"};
    public static readonly string[] Globals=new[]{"Court","Mine","PrisonerRole","Survivors","ObservedDeaths","Entombed","Reported","DeadlineArmed","DeadlineRemaining","MinePending"}.Concat(Canonical).Select(n=>"TLM_G_MQ02C_"+n).ToArray();
    public static readonly string[] Factions={"TLM_Fac_RH_Staging"}; // development AI grouping, no political/player allegiance
    public static readonly MiscSpec[] MiscItems={new(LampId,"Smokeless lamp (greybox proof)",LooksLike:new[]{"Desk Lamp","Lantern","Folder"}),new(KeyId,"Blevins's firing key",LooksLike:new[]{"Key","Screwdriver","Pencil"}),new(ReceiptId,"Sixty-cap court receipt",LooksLike:new[]{"Clipboard","Folder"})};
    public static readonly NpcSpec[] Npcs=new[]{("Quill","quill","female"),("Blevins","greer","male"),("Roark","roark","female"),("Dorn","dorn","female")}
        .Select(p=>new NpcSpec("TLM_NPC_RH_"+p.Item1,Names[p.Item2],"WorkshopNPC",false,p.Item3,Factions[0],true))
        .Concat(Enumerable.Range(1,11).Select(i=>new NpcSpec($"TLM_NPC_RH_Miner{i:00}","Night-shift miner","WorkshopNPC",false,i%2==0?"female":"male",Factions[0],true))).ToArray();
    public sealed record Piece(string Alias,string Name,string Base,float X,float Y,float Z=12,int Who=0,bool Person=false,bool On=true,bool Mercy=false,float[]? Box=null);
    static Piece Marker(string n,float x,float y)=>new(n,n,"XMarker",x,y,16,On:false);
    public static readonly Piece[] Pieces=new Piece[]{
        new("MercyTravel","Travel to Red Hollow: court and mine","TLM_ACTI_RH_MercyTravel",3520,2600,12,1,On:false,Mercy:true),Marker("MercyReturn",3490,2570) with{Mercy=true},
        Marker("GapArrival",256,256),Marker("MouthArrival",3328,256),Marker("CageSurface",3584,256),Marker("CageBelow",6400,256),Marker("GalleryArrival",9472,256),
        Marker("Gallows",768,512),Marker("Released",1024,256),Marker("Custody",512,512),Marker("DornWithdraw",10368,512),
        new("Quill",Names["quill"],"TLM_NPC_RH_Quill",512,512,16,2,true),
        new("Roark",Names["roark"],"TLM_NPC_RH_Roark",3328,512,16,3,true),
        new("Blevins",Names["greer"],"TLM_NPC_RH_Blevins",3840,512,16,4,true),
        new("Dorn",Names["dorn"],"TLM_NPC_RH_Dorn",9984,512,16,5,true),
        new("Rope","Rope attachment: projectile target","TLM_CONT_RH_Rope",768,512,120,6),
        new("RopeBroken","Broken rope attachment","TLM_ACTI_RH_RopeBroken",768,512,120,On:false),
        new("CourtRecord","Court recording board","TLM_ACTI_RH_CourtRecord",576,640,12,7),
        new("ReferralSent","Both dockets referred (court record)","TLM_ACTI_RH_ReferralSent",640,640,12,7,On:false),
        new("TollBoard","Tolls at the Gap","TLM_ACTI_RH_TollBoard",128,512,12,8),
        new("Docket","Docket of the Circuit","TLM_ACTI_RH_Docket",512,640,12,9),
        new("Transcript","Recorded prisoner testimony","TLM_ACTI_RH_Transcript",704,640,12,10),
        new("TollBox","Foot toll: two caps","TLM_CONT_RH_TollBox",256,512,12,11),
        new("Bypass","Walk around the toll-gate","TLM_ACTI_RH_Bypass",1280,256,12,12),
        new("Watch","Watch the local court scene","TLM_ACTI_RH_Watch",768,640,12,13),
        new("ToMouth","Path to the Mouth","TLM_ACTI_RH_ToMouth",1536,256,12,14),
        new("ToGap","Path to the gap","TLM_ACTI_RH_ToGap",3072,256,12,15),
        new("CageControl","Hoist: descend, return or rescue","TLM_ACTI_RH_CageControl",3584,384,12,16),
        new("BelowControl","Hoist: bring miners up or return alone","TLM_ACTI_RH_BelowControl",6400,384,12,17),
        new("FiringControl","Mouth firing key control","TLM_ACTI_RH_FiringControl",3840,384,12,18),
        new("BreakControl","Inner-break charge control","TLM_ACTI_RH_BreakControl",6912,512,12,19),
        new("Roster","Find and muster the night shift","TLM_ACTI_RH_Roster",6656,384,12,20),
        new("Gallery","Path to the sealed gallery","TLM_ACTI_RH_Gallery",7168,256,12,21),
        new("FromGallery","Return to the Nine level","TLM_ACTI_RH_FromGallery",9216,256,12,22),
        new("GalleryLamp","Gallery lamp","TLM_ACTI_RH_GalleryLamp",9984,384,12,23),
        new("CotLamp","Lamp under Blevins's cot","TLM_ACTI_RH_CotLamp",4096,512,12,24),
        new("Silver","Inspect the hoist-house desk","TLM_ACTI_RH_Silver",4096,640,12,25),
        new("Shovel","Chalk on a Shovel Blade","TLM_ACTI_RH_Shovel",3328,640,12,26),
        new("Knocking","Listen at the Mouth (knocking stand-in)","TLM_ACTI_RH_Knocking",3328,384,12,27),
        new("MouthOpen","Mine opening marker: use the hoist control","TLM_ACTI_RH_MouthOpen",3584,640),
        new("MouthClosed","Sealed Mouth rubble (stand-in)","TLM_ACTI_RH_MouthClosed",3584,640,12,On:false),
        new("BreakOpen","Inner break open","TLM_ACTI_RH_BreakOpen",7424,512),
        new("BreakClosed","Collapsed inner break (stand-in)","TLM_ACTI_RH_BreakClosed",7424,512,12,On:false),
        new("StoneDoor","Sealed stone door: no passage beyond","TLM_ACTI_RH_StoneDoor",10240,512,12,28),
        new("Exit","Return to Mercy Crossing","TLM_ACTI_RH_Exit",3200,128,12,29),
        new("Resolve","Rescue outcome and pending break plan","TLM_ACTI_RH_Resolve",3584,128,12,30),
        new("BodyKey","Blevins's body key / hoist fallback","TLM_ACTI_RH_BodyKey",3968,384,12,31),
        new("LabelGap","Outside: Gap court and toll","TLM_ACTI_RH_LabelGap",256,64,12,40),
        new("LabelMouth","Outside: mine work yard","TLM_ACTI_RH_LabelMouth",3328,64,12,41),
        new("LabelCage","Hoist: outside and below","TLM_ACTI_RH_LabelCage",3584,64,12,42),
        new("LabelNine","Belowground: Nine level","TLM_ACTI_RH_LabelNine",6656,64,12,43),
        new("LabelGallery","Belowground: sealed gallery","TLM_ACTI_RH_LabelGallery",9728,64,12,44),
        new("Fall","Supported-floor return","TLM_ACTI_RH_Fall",6912,384,-700,45,Box:new[]{1024f,768f,120f})
    }.Concat(Enumerable.Range(1,11).Select(i=>new Piece($"Miner{i:00}","unnamed night-shift role"+(i==1?" (Pell reference-only relationship)":""),$"TLM_NPC_RH_Miner{i:00}",6656+(i%4)*128,128+(i/4)*128,16,100+i,true)))
      .Concat(Enumerable.Range(1,11).SelectMany(i=>new[]{Marker($"Below{i:00}",6656+(i%4)*128,128+(i/4)*128),Marker($"Cage{i:00}",6400+(i%4)*96,384+(i/4)*96),Marker($"Surface{i:00}",3584+(i%4)*128,768+(i/4)*128)})).ToArray();
    public static readonly ContainerSpec[] Containers={new("TLM_CONT_RH_Rope","Rope attachment: projectile target",new[]{"Toolbox","Wooden Crate","Crate","Suitcase"},"Caps001",0),new("TLM_CONT_RH_TollBox","Court payment box",new[]{"Toolbox","Wooden Crate","Crate","Suitcase"},"Caps001",0)};
    public static readonly ActivatorSpec[] Activators=Pieces.Where(p=>p.Base.StartsWith("TLM_ACTI_")).Select(p=>new ActivatorSpec(p.Base,p.Name,p.Box!=null?null:new[]{"Wooden Crate","Fertilizer Bag","Clipboard","Folder"},"Use")).ToArray();
    public static readonly OwnCellSpec[] Cells={new(CellId,"Red Hollow: Nine level and sealed gallery")};
    static IEnumerable<PlacedSpec> Floors()=>new[]{("A",0,7,4),("B",3072,7,6),("C",6144,7,4),("D",9216,6,4)}.SelectMany(f=>Enumerable.Range(0,f.Item3).SelectMany(x=>Enumerable.Range(0,f.Item4).Select(y=>new PlacedSpec($"TLM_REF_RH_Floor_{f.Item1}{x}{y}",CellId,"workshop_ShackMidFloor01B","Static",y*256,f.Item2+x*256,0))));
    public static readonly PlacedSpec[] Placed=Pieces.Select(p=>new PlacedSpec("TLM_REF_RH_"+p.Alias,p.Mercy?Spec.TrialCell:CellId,p.Base,p.Base=="XMarker"?"Static":null,p.Mercy?620+(p.Alias=="MercyReturn"?40:0):p.Y,p.Mercy?100:p.X,p.Z,true,p.Box)).Concat(Floors()).ToArray();
    static MessageSpec Ui(string id,string text,params string[] buttons)=>new(Prefix+id,null,text,true,(buttons.Length==0?new[]{"Continue"}:buttons).Select(b=>new ButtonSpec(b)).ToArray());
    public static readonly Dictionary<string,(string Text,string[] Buttons)> UiText=new(){
        ["Travel"]=("[Red Hollow story test]\n\n"+Available+" Travel to the gap?",new[]{"Travel","Not now"}),
        ["StageTravel"]=("[Staged travel]\n\nA marked transfer links the labelled areas. It pauses the deadline and keeps unfinished work intact. Continue?",new[]{"Continue","Not now"}),
        ["Descend"]=("[Staged hoist]\n\nGo from the outdoor work yard to the enclosed Nine level. This is a staged transfer; the hoist does not physically move. Continue?",new[]{"Continue","Not now"}),
        ["Rescue"]=("[Bring the shift up]\n\nEvery living unfinished miner must reach the cage and surface. This is a staged batch; incomplete arrivals remain pending. Continue?",new[]{"Continue","Not now"}),
        ["Resolve"]=("[Rescue and break]\n\nChoose only what is represented. A pending blast is not completed by rescue.",new[]{"Leave the break alone","Plan the inner-break blast","Resolve observed casualties","Not now"}),
        ["Blast"]=("[Inner-break blast]\n\nThis closes the gallery break, not the Mouth. Every survivor must already be safe and nobody may remain in the blast area. Continue?",new[]{"Continue","Not now"}),
        ["Seal"]=("[Seal the Mouth]\n\nYou heard the knocking. All eleven are still below. This is your explicit order to entomb the shift. Continue?",new[]{"Give the order","Do not fire"}),
        ["Final"]=("[Deadline final call]\n\nThe warned active-time deadline has expired. The cage brings you out before Blevins fires. Continue acknowledges the warning; it is not your order.",new[]{"Continue","Pause the scene"}),
        ["Clock"]=("[Local deadline]\n\n600 active seconds; 30 after expired-warning renewal. Loaded Mouth/Nine/gallery play only. Standard menu edges, dialogue, transit, absence and load gaps pause. Detected menu uncertainty blocks; renew warning to resume.",new[]{"Accept local deadline","Not now"}),
        ["PendingRescue"]=("[Unfinished rescue]\n\nRetry the remaining survivors, or return below to inspect unfinished fates. Delivered miners stay safe; the unfinished rescue still pauses the deadline.",new[]{"Retry survivors","Inspect below","Not now"}),
        ["HoistBelow"]=("[Staged hoist]\n\nBring the shift up, or return alone. Return alone does not rescue anybody.",new[]{"Bring the shift up","Return alone","Stay"}),
        ["NoWarning"]=("[Rescue fallback]\n\nNo warned rescue deadline has been accepted. You can operate the staged hoist without arming one.",new[]{"Start rescue without deadline","Not now"}),
        ["ReportFacts"]=("[Current Red Hollow facts]\n\nCourt %g; mine %g; safe survivors %g; observed deaths %g (player %g; known nonplayer %g; unknown %g). Entombment is separate.",new[]{"Continue"}),
        ["ReportEvidence"]=("[Evidence and undertaking]\n\nCourt-payment testimony %g; mine silver %g; personal undertaking %g; terms actually delivered %g. No town ratification is claimed.",new[]{"Continue"}),
        ["ReportLamp"]=("[Lamp and custody]\n\nLamp origin %g (1 gallery, 2 cot); presently held %g; 2298 copy presently held %g; entombed %g. Acquisition and current custody are distinct.",new[]{"Continue"}),
        ["NoOperator"]=("[Rescue control]\n\nBlevins cannot operate the firing control. No deadline is armed. The hoist remains available for rescue.",new[]{"Start rescue","Not now"}),
        ["Court"]=("[Court scene]\n\nOptional court controls are independent of the mine. The bypass is a supported walk around the gate.",new[]{"Talk to Quill","Watch local execution scene","Record/pay rope fine","Not now"}),
        ["Watch"]=("[Local gallows scene]\n\nThe drop follows 15 active seconds here, after a final warning. Menus, absence or intervention pause/prevent it. Watch?",new[]{"Watch here","Not now"}),
        ["Drop"]=("[Imminent drop]\n\nThe local sentence is about to be carried out. Continue acknowledges witnessing; cancellation prevents the drop.",new[]{"Continue watching","Stop watching"}),
        ["Referral"]=("[Court referral]\n\nThe current docket and the held 2298 review copy will be entered together for review. This is not a pardon. Confirm the represented referral?",new[]{"Refer both dockets","Not now"}),
        ["Receipt"]=("[Court receipt]\n\nSixty caps received; the receipt is in your inventory. Release still requires the living prisoner to reach the supported safe position.",new[]{"Continue"}),
        ["Report"]=("[Red Hollow report]\n\nReport current court, miner, mine, evidence and lamp facts. No fair or town-wide agreement is implied.",new[]{"Report","Later"}),
        ["Status"]=("[Red Hollow]\n\nUse the labelled controls. At the mine, use the hoist control, muster below, then bring the shift up. Outside, use Rescue outcome and pending break plan, then Return to Mercy Crossing. Missing arrivals remain unfinished.",new[]{"Continue"}),
        ["Failed"]=("[Unfinished scene]\n\nThe required arrival, item or visible effect was not observed. Nothing further is recorded. Use the same control to retry only unfinished work.",new[]{"Continue"}),
        ["Unavailable"]=("[Court unavailable]\n\nNo eligible surviving earlier-road prisoner is available. Nobody is replaced or resurrected. The bypass and mine remain open.",new[]{"Continue"}),
        ["NoTranscript"]=("[Court record]\n\nNo eligible prisoner's statement has been recorded here. The mine does not require this optional evidence.",new[]{"Continue"}),
        ["Rope"]=("[Rope attachment]\n\nUse a real player projectile on the visible attachment target. Activating this control does not count as shooting or release.",new[]{"Continue"}),
        ["Freed"]=("[Rope release]\n\nThe rope is broken. The prisoner is alive and free. The forty-yard quotation is withheld; recording and payment of any rope fine are separate.",new[]{"Continue"}),
        ["Fine"]=("[Rope record]\n\nQuill records the shot and a four-cap rope fine. A recorded fine is not a paid fine.",new[]{"Record damage","Pay recorded four caps","Not now"}),
        ["Knocking"]=("[Knocking stand-in]\n\nThis labelled listening interaction represents the authored hoist-code knocking and its slower reply. It supplies no voice or audio acceptance.",new[]{"Listen","Not now"}),
        ["Prisoner"]=("[Prisoner record]\n\nOnly the actual earlier-road actor is bound here. Freedom, living review custody and death are separate facts.",new[]{"Continue"}),
        ["MineStatus"]=("[Mine status]\n\nRead the counted facts in the notifications. The shift, current survivors, observed deaths and entombment are separate.",new[]{"Continue"}),
        ["Lamp"]=("[Lamp proof]\n\nA world stand-in and one inventory item represent the lamp. No working carried light or later sale is claimed.",new[]{"Take the lamp","Leave it"}),
        ["Silver"]=("[Hoist-house desk]\n\nYou found stamped silver and an instruction to keep the Mouth shut through winter.",new[]{"Continue"}),
        ["Exit"]=("[Return to Mercy]\n\nUnsettled work remains unsettled. Return now?",new[]{"Return","Stay"}),
        ["End"]=("[Red Hollow]\n\n"+Complete,new[]{"Continue"}),
        ["LabelGap"]=("[Outside: Gap court]\n\nCourt, receipt, rope target and evidence are optional. A supported path goes around the labelled gate to the mine route.",new[]{"Continue"}),
        ["LabelMouth"]=("[Outside: mine work yard]\n\nThe hoist leads below to the Nine. Warning, firing control and desk evidence are separate choices. The labelled exit returns to Mercy.",new[]{"Continue"}),
        ["LabelCage"]=("[Hoist: outside and below]\n\nUse Hoist: descend, return or rescue to go below. The mine opening clipboard is only a marker. Below: Find and muster the night shift, then Hoist: bring miners up or return alone. Return alone rescues nobody.",new[]{"Continue"}),
        ["LabelNine"]=("[Belowground: Nine level]\n\nFirst use Find and muster the night shift. Then use Hoist: bring miners up or return alone; choose Bring the shift up to attempt rescue. Outside, use Rescue outcome and pending break plan. The gallery is optional; rescue does not itself blast the break.",new[]{"Continue"}),
        ["LabelGallery"]=("[Belowground: sealed gallery]\n\nThe sealed gallery ends here. The marked path returns to the Nine level; the hoist leads back to the outdoor yard.",new[]{"Continue"}),
    };
    static IEnumerable<MessageSpec> Speech(){foreach(var node in NodeNames){var parts=SpeechPages(node);var who=SpeakerName(Lines[node].GetProperty("speaker").GetString()!);for(int i=0;i<parts.Length;i++)yield return new(Prefix+"S_"+node+"_"+(i+1),who,MercyBriefing.Spoken(who,parts[i]),true,(i==parts.Length-1?Labels(node):new[]{"Continue"}).Select(b=>new ButtonSpec(b)).ToArray());}}
    public static readonly string[] DocumentIds={"toll_board","quill_docket","docket_2298","chalk_message"};
    public static readonly Dictionary<string,JsonElement> Documents=Load("documents.json").GetProperty("documents").EnumerateArray().Where(d=>DocumentIds.Contains(d.GetProperty("id").GetString())).ToDictionary(d=>d.GetProperty("id").GetString()!,d=>d);
    public static string[] DocumentPages(string id)=>Wrap(Documents[id].GetProperty("text").GetString()!,180).ToArray();
    static IEnumerable<MessageSpec> Transcripts(){foreach(var n in new[]{"dunmore_tells","cutter_rope","cutter_rope_missed"}){var text=Lines[n].GetProperty("text").GetString()!;if(n.StartsWith("cutter"))text=text[text.IndexOf("We were paid",StringComparison.Ordinal)..];var pages=Wrap(text,180).ToArray();for(int i=0;i<pages.Length;i++)yield return Ui("T_"+n+"_"+(i+1),"[Recorded prisoner statement, page "+(i+1)+" of "+pages.Length+"]\n\n"+pages[i]);}}
    static IEnumerable<MessageSpec> Papers(){foreach(var id in DocumentIds){var pages=DocumentPages(id);for(int i=0;i<pages.Length;i++)yield return Ui("D_"+id+"_"+(i+1),"["+Documents[id].GetProperty("title").GetString()+$", page {i+1} of {pages.Length}]\n\n"+pages[i]);}}
    public static readonly MessageSpec[] Messages=Speech().Concat(UiText.Select(p=>Ui(p.Key,p.Value.Text,p.Value.Buttons))).Concat(Papers()).Concat(Transcripts()).ToArray();
    static readonly Dictionary<int,string> NeutralLogs=new(){[10]="You reached the Dominion toll-gate.",[11]="The rope is broken. The prisoner is alive and free.",[14]="The court carried out the sentence while you remained at the wagon.",[15]="You heard how the Cutters were paid to watch for Gantt's delayed freight and seize his pouch.",[20]="You reached the chained Mouth at Red Hollow.",[30]="You accepted the warned local rescue deadline. The shift is still below.",[40]="You reached the Nine level by the cage.",[45]="You found eleven miners alive at the break in the rock.",[50]="You reached the cut gallery and its sealed stone door.",[52]="The eleven miners reached the surface. You then blasted the break closed.",[53]="You ordered the Mouth sealed with the shift below. Blevins carried out the order.",[56]="The warned local deadline expired. Blevins sealed the Mouth with the shift below. You gave no order.",[57]="The eleven miners reached the surface. You made no gallery undertaking and did not blast the break.",[58]="The observed casualty count and safe survivors are recorded separately. No all-eleven rescue is claimed.",[60]="You found stamped silver and an instruction to keep the Mouth shut through winter."};
    static readonly JsonElement QuestData=Load("quests/tlm_mq02c.json");
    public static readonly string[] RoadAliases=new[]{"Quill","Blevins","Roark","Dorn","Condemned"}.Concat(Enumerable.Range(1,11).Select(i=>$"Miner{i:00}")).ToArray();
    public static readonly QuestSpec Road=new(RoadId,QuestData.GetProperty("title").GetString()!,"MainQuest",56,false,
        QuestData.GetProperty("stages").EnumerateArray().Select(s=>{int n=s.GetProperty("n").GetInt32();return new StageSpec(n,NeutralLogs.TryGetValue(n,out var text)?text:s.GetProperty("log").ValueKind==JsonValueKind.Null?null:s.GetProperty("log").GetString(),n==100);}).Concat(new[]{new StageSpec(57,NeutralLogs[57]),new StageSpec(58,NeutralLogs[58])}).OrderBy(s=>s.Index).ToArray(),
        QuestData.GetProperty("objectives").EnumerateArray().Select(o=>new ObjectiveSpec(o.GetProperty("n").GetInt32(),o.GetProperty("n").GetInt32()==30?"Decide what happens at the Mouth":o.GetProperty("text").GetString()!)).ToArray(),
        RoadAliases.Select(n=>new AliasSpec(n,Fill.ScriptFilled,AllowDead:true,AllowDisabled:true)).ToArray(),
        new ScriptBind("TLM:MQ02CQuest",new Prop[]{new ReferenceListProp("RHOriginalMiners",Enumerable.Range(1,11).Select(i=>$"TLM_REF_RH_Miner{i:00}").ToArray()),new ReferenceListProp("RHSurfaceReceipts",Enumerable.Range(1,11).Select(i=>$"TLM_REF_RH_Surface{i:00}").ToArray()),new PlacedProp("RHBelowAnchor","TLM_REF_RH_CageBelow"),new PlacedProp("RHBreakControl","TLM_REF_RH_BreakControl"),new FormProp("TLM_MQ01","TLM_MQ01"),new FormProp("TLM_G_MQ01_Done","TLM_G_MQ01_Done"),new FormProp("DocketItem",MercyBriefing.BookId),new FormProp("LampItem",LampId),new FormProp("KeyItem",KeyId),new FormProp("ReceiptItem",ReceiptId),new VanillaProp("Caps","Caps001","MiscItem"),new AliasProp("Alias_Sheriff","SheriffPritchard","TLM_MQ01"),new AliasListProp("Miners",Enumerable.Range(1,11).Select(i=>(RoadId,$"Miner{i:00}")).ToArray())}.Concat(new[]{"Quill","Blevins","Roark","Dorn","Condemned"}.Select(n=>(Prop)new AliasProp("Alias_"+n,n))).Concat(Globals.Select(n=>(Prop)new FormProp(n,n))).ToArray()));
    public static readonly QuestSpec Stage=new(StageId,"Red Hollow: directions","SideQuests",30,false,Array.Empty<StageSpec>(),new ObjectiveSpec[]{
            new(5,"Take the road to Red Hollow from Mercy Crossing","MercyTravel"),
            new(10,"Follow Path to the Mouth to reach the mine","ToMouth"),
            new(20,"Use the hoist control at the mine entrance","CageControl"),
            new(30,"Find and muster the night shift below","Roster"),
            new(40,"Bring the miners up using the hoist","BelowControl"),
            new(50,"Check the miners and decide what to do at the inner break","Resolve"),
            new(55,"Return to the inner-break charge control to finish the work","BreakControl"),
            new(60,"Return to Mercy Crossing and tell Pritchard what happened","Exit"),
            new(70,"Speak to the freed prisoner beside the court","Condemned"),
            new(80,"Return to the Nine level, then take the hoist up","FromGallery"),
            new(85,"Take the hoist back to the mine yard","BelowControl"),
            new(86,"Use the cage control to finish the interrupted operation","BelowControl"),
            new(90,"Tell Sheriff Pritchard what happened at Red Hollow","GuideSheriff")},
        Pieces.Select(p=>new AliasSpec(p.Alias,Fill.Placed,AllowDisabled:true,AllowDead:true,Placed:"TLM_REF_RH_"+p.Alias,Scripts:p.Who==0?Array.Empty<ScriptBind>():new[]{new ScriptBind("TLM:RedHollowTalk",new IntProp("Who",p.Who))})).Concat(new[]{new AliasSpec("Condemned",Fill.ScriptFilled,AllowDead:true,AllowDisabled:true,Scripts:new[]{new ScriptBind("TLM:RedHollowTalk",new IntProp("Who",32))}),new AliasSpec("Player",Fill.Player,Scripts:new[]{new ScriptBind("TLM:RedHollowTalk",new IntProp("Who",-1))})}).Concat(RedHollowEnvironment.FallAliases).Concat(new[]{new AliasSpec("GuideSheriff",Fill.ScriptFilled,AllowDead:true,AllowDisabled:true)}).ToArray(),
        new ScriptBind("TLM:RedHollowWalk",new Prop[]{new FormProp("TLM_MQ02C",RoadId),new FormProp("TLM_MQ01","TLM_MQ01"),new FormProp("TLM_MercyBriefing",MercyBriefing.QuestId),new AliasProp("Alias_Condemned","Condemned"),new AliasProp("Alias_GuideSheriff","GuideSheriff"),new AliasListProp("CastFrom",Pieces.Where(p=>p.Person).Select(p=>(StageId,p.Alias)).ToArray()),new AliasListProp("CastInto",Pieces.Where(p=>p.Person).Select(p=>(RoadId,p.Alias)).ToArray()),new StringListProp("ClockMenus",ClockMenus),new AliasListProp("ZoneOn",Pieces.Where(p=>p.On&&!p.Mercy).Select(p=>(StageId,p.Alias)).Concat(RedHollowEnvironment.FallAliases.Select(a=>(StageId,a.Name))).ToArray())}.Concat(Pieces.Select(p=>(Prop)new AliasProp("Alias_"+p.Alias,p.Alias))).Concat(RedHollowEnvironment.FallAliases.Select(a=>(Prop)new AliasProp("Alias_"+a.Name,a.Name)))
        .Concat(new[]{"Below","Cage","Surface"}.Select(n=>(Prop)new AliasListProp(n+"Slots",Enumerable.Range(1,11).Select(i=>(StageId,n+$"{i:00}")).ToArray())))
        .Concat(Messages.Select(m=>(Prop)new FormProp(m.EditorId[Prefix.Length..],m.EditorId))).ToArray()));
}
