using System.Text.Json;

namespace Tlm.PluginBuilder;

// Frozen 1B5B3117/61829D48 and coordinator order17201E91. Accepted speech is
// a build input; the game does not load JSON or invent continuation greetings.
public static class FourFlags
{
    public const string QuestId="TLM_MQ03", EntryId="TLM_FF_Entry", CellId="TLM_CELL_FourFlags", Prefix="TLM_MSG_FF_";
    public const string CaseId="TLM_BOOK_FF_CourierCase",SilverId="TLM_MISC_FF_Silver";
    static string Root(){var d=new DirectoryInfo(AppContext.BaseDirectory);while(d!=null){var p=Path.Combine(d.FullName,"assets/incoming/act1/story");if(Directory.Exists(p))return p;d=d.Parent;}throw new InvalidDataException("Accepted Four Flags inputs missing");}
    static JsonElement Load(string n)=>JsonDocument.Parse(File.ReadAllText(Path.Combine(Root(),n))).RootElement.Clone();
    public static readonly Dictionary<string,JsonElement> Lines=Load("talk/tlm_mq03.json").GetProperty("lines").EnumerateArray().ToDictionary(l=>l.GetProperty("id").GetString()!,l=>l);
    public static readonly Dictionary<string,JsonElement> Documents=Load("documents.json").GetProperty("documents").EnumerateArray().Where(d=>new[]{"fair_handbill","silver_case","courier_card"}.Contains(d.GetProperty("id").GetString())).ToDictionary(d=>d.GetProperty("id").GetString()!,d=>d);
    static readonly Dictionary<string,string> Names=Load("characters.json").GetProperty("characters").EnumerateArray().ToDictionary(c=>c.GetProperty("id").GetString()!,c=>c.GetProperty("name").GetString()!);
    public static readonly JsonElement PikeAside=Load("talk/town.json").GetProperty("lines").EnumerateArray().Single(l=>l.GetProperty("id").GetString()=="pike_mould_aside");
    public static readonly string[] Roles={"pritchard","talbot","pike","belden","whitcomb","brigg","grey","flint","threefords"};
    public static readonly string[] Withheld={"pike_line","pike_flint","flint_line","flint_beaten"};
    public static readonly string[] NodeNames=Lines.Keys.ToArray();
    public static string[] Labels(string node)=>Lines[node].TryGetProperty("buttons",out var b)?b.EnumerateArray().Select(x=>x.GetProperty("label").GetString()!).ToArray():new[]{"Continue"};
    public static string[] Wrap(string text,int room){var pages=new List<string>();while(text.Length>room){int cut=text.LastIndexOf(' ',room);if(cut<1)throw new InvalidDataException("Unsplit Four Flags word");pages.Add(text[..cut]);text=text[(cut+1)..];}pages.Add(text);return pages.ToArray();}
    public static string[] SpeechPages(string node)=>Wrap(Lines[node].GetProperty("text").GetString()!,240-Names[Lines[node].GetProperty("speaker").GetString()!].Length-4);
    public static string[] DocumentPages(string id)=>Wrap(Documents[id].GetProperty("text").GetString()!.Replace("\n"," "),220);
    static MessageSpec Ui(string id,string text,params string[] buttons)=>new(Prefix+id,null,text,true,(buttons.Length==0?new[]{"Continue"}:buttons).Select(b=>new ButtonSpec(b)).ToArray());
    public static readonly Dictionary<string,(string Text,string[] Buttons)> UiText=new(){
        ["Entry"]=("[The Four Flags]\n\nCall the Decoration Day fair after the first section. Road reports stay separate; no unfinished road resolves automatically.",new[]{"Use a completed road","Call the fair without my report","Read the handbill","Not now"}),
        ["NoReport"]=("[No road report delivered]\n\nCall the fair without my report? This grants no knowledge or old report. All three roads remain open.",new[]{"Call the fair without my report","Not now"}),
        ["Travel"]=("[Fair travel]\n\nTravel to the separate staged camp-ground? Old local clocks pause during transit and absence. This is not a landscape journey.",new[]{"Travel to the camp-ground","Not now"}),
        ["Layout"]=("[Camp-ground prototype]\n\nCompact, Dominion, Commonwealth and Directorate have separate labelled stations. Hearing an offer signs nothing. The central courier scene waits for your explicit readiness.",new[]{"Continue"}),
        ["LayoutLimits"]=("[Four offers, then a response]\n\nWalk to each available delegate. The firing position and landing are ground-level inspection stand-ins. No roof climb, projectile, voice or distant shooter is represented.",new[]{"Continue"}),
        ["Ready"]=("[Continue the fair]\n\nThe four offer stations are available. Start the staged courier encounter now? You may hear more offers first.",new[]{"Continue the fair","Not yet"}),
        ["Shot"]=("[Staged shooting representation]\n\nJuno is at the courier station. Keep the original case where it is, including in your custody. This notice represents the shot and wound; no firearm effect or forced death is claimed.",new[]{"Witness the staged scene","Pause the scene"}),
        ["DeadCourier"]=("[Courier found dead]\n\nYou found the courier dead at the fair. Her case may still hold evidence. No new shot or injury has been staged.",new[]{"Inspect this scene","Not now"}),
        ["NoCarrier"]=("[Response unavailable]\n\nNo officer or witness is available to direct the response. You may still inspect the firing position or read the accessible case.",new[]{"Continue"}),
        ["Occupation"]=("[Dominion order]\n\nBrigg has demanded control of the camp. Continue under that order, or return to the unresolved choices?",new[]{"Continue under the order","Return to choices"}),
        ["OccupationSeen"]=("[Staged Dominion control]\n\nThe Dominion order board is visibly displayed at the central station. This represents occupation, without confiscation, injury, allegiance or a blocked exit.",new[]{"Acknowledge the visible order","Pause here"}),
        ["PendingCourse"]=("[Occupation already recorded]\n\nThe selected response is unfinished. Retry that response or inspect the physical evidence. Earlier occupation remains a fact; the original unresolved demand is not reopened.",new[]{"Retry selected response","Inspect case","Close"}),
        ["PendingOrder"]=("[Response pending]\n\nThe visible order acknowledgment is unfinished. Retry it, or return to unresolved choices. No occupation is recorded until its acknowledgment succeeds.",new[]{"Retry order acknowledgment","Return to choices","Close"}),
        ["Case"]=("[Original courier case]\n\nInspect the actual case, take it for personal custody, or ask an available Pritchard to read it publicly. Copies of its base item never count as the original.",new[]{"Read the accessible original","Take original case","Public reading with Pritchard","Close"}),
        ["Take"]=("[Personal custody]\n\nTake this original case from its actual current position. No wrist cutting, unseen escape, sale, burning or universal witness knowledge is claimed.",new[]{"Take original case","Leave it"}),
        ["Public"]=("[Public case reading]\n\nDeliver this original case to the present Pritchard for a public reading. Its physical custody changes; your earlier observations remain.",new[]{"Deliver original to Pritchard","Keep it here"}),
        ["Solo"]=("[Courier case read]\n\nYou read the line numbered 4117 and the Blackstone sketch. Pritchard's account has not been heard.",new[]{"Acknowledge the read lead","Not now"}),
        ["Silver"]=("[Firing-position stand-in]\n\nInspect the original spent silver cartridge case here. This is ground-level evidence, not a roof climb or observation of a departing shooter.",new[]{"Inspect original silver case","Not now"}),
        ["GiveSilver"]=("[Evidence transfer]\n\nThe eligible Flint can receive this original spent case after your inspection. This is a real item transfer, not evidence inferred from her presence.",new[]{"Give original evidence to Flint","Keep evidence here"}),
        ["Landing"]=("[Landing inspection stand-in]\n\nThis labelled ground-level station represents inspecting the prepared landing. No distant person or moving skiff has been observed; the shooter's identity remains unknown.",new[]{"Inspect the landing","Not now"}),
        ["Competition"]=("[Optional competition]\n\nOptional competition is not available in this prototype. No fee, win, reward or required progression is attached to this station.",new[]{"Continue"}),
        ["PikeCompare"]=("[Pike: evidence comparison]\n\nYou carry the original inspected spent silver case. Ask Pike to compare it? A tooling mark is circumstantial evidence, not the shooter's identity.",new[]{"Compare original evidence","Not now"}),
        ["PikeUnavailable"]=("[Pike at the fair]\n\nThe optional competition is unavailable. Evidence comparison needs the original inspected spent silver case in your inventory. No replacement copy or remote inspection is offered.",new[]{"Continue"}),
        ["Exit"]=("[Return to Mercy]\n\nLeave the camp-ground. Surviving visiting originals will be returned to their captured locations and enabled states. A failed return remains reported; player exit stays usable.",new[]{"Return to Mercy","Stay"}),
        ["ReturnsPending"]=("[Original cast return unfinished]\n\nAt least one original actor has not reached the verified return marker/state. No successful restoration is claimed. Use the fair entry/status control to retry only those returns.",new[]{"Continue"}),
        ["Blocked"]=("[Effect not acknowledged]\n\nAn issued original-reference transfer is unresolved. It will not be reissued or inferred from later inventory changes. Inspect current custody/status; copies, refunds and fabricated success are unavailable.",new[]{"Continue"}),
        ["Failed"]=("[Scene unfinished]\n\nThe required actor, original object, arrival or acknowledgment is not current. Nothing further was recorded. Use the same ordinary control for eligible unfinished scene work.",new[]{"Continue"}),
        ["Status"]=("[Four Flags status]\n\nEntry basis %g; courier encounter %g; response %g; occupation %g. Actual case read %g. Inspect physical custody separately. No older road or relief balance was changed.",new[]{"Continue"}),
        ["Custody"]=("[Original case custody]\n\nHeld by player %g; public custodian present %g; transfer pending %g; original cast returns pending %g. Historical reading and current possession are different facts.",new[]{"Continue"}),
        ["Unavailable"]=("[Fair unavailable]\n\nComplete the first section before calling or entering the fair. No report, injury, allegiance or other-road outcome was created.",new[]{"Continue"})
    };
    public static readonly MessageSpec[] Messages=Lines.Where(p=>!Withheld.Contains(p.Key)).SelectMany(p=>SpeechPages(p.Key).Select((text,i)=>new MessageSpec(Prefix+"S_"+p.Key+"_"+(i+1),null,Names[p.Value.GetProperty("speaker").GetString()!]+":\n\n"+text,true,(i+1==SpeechPages(p.Key).Length?Labels(p.Key):new[]{"Continue"}).Select(b=>new ButtonSpec(b)).ToArray())))
        .Concat(Documents.SelectMany(p=>DocumentPages(p.Key).Select((text,i)=>Ui("D_"+p.Key+"_"+(i+1),text))))
        .Concat(UiText.Select(p=>Ui(p.Key,p.Value.Text,p.Value.Buttons)))
        .Append(Ui("A_pike_mould_aside",Names["pike"]+":\n\n"+PikeAside.GetProperty("text").GetString()!)).ToArray();
    public static readonly string[] Factions={"TLM_Fac_FF_Staging"};
    public static readonly NpcSpec[] Npcs=new[]{("Whitcomb","whitcomb","female"),("Brigg","brigg","male"),("Grey","grey","male"),("Flint","flint","female"),("Juno","threefords","female")}.Select(p=>new NpcSpec("TLM_NPC_FF_"+p.Item1,Names[p.Item2],"WorkshopNPC",false,p.Item3,Factions[0],true)).ToArray();
    public static readonly MiscSpec[] MiscItems={new(SilverId,"Original spent silver cartridge case",LooksLike:new[]{"Pencil","Clipboard","Folder"})};
    public static readonly BookSpec[] Books={new(CaseId,"Original courier case: ledger and Blackstone sketch",Documents["courier_card"].GetProperty("text").GetString()!,true)};
    public sealed record Piece(string Alias,string Name,string Base,float X,float Y,float Z=16,int Who=0,bool Person=false,bool Mercy=false);
    static Piece Marker(string n,float x,float y)=>new(n,n,"XMarker",x,y);
    public static readonly Piece[] Pieces=new Piece[]{
        new("Entry","Four Flags: entry, handbill and returns","TLM_ACTI_FF_Entry",3920,3100,12,1,Mercy:true),Marker("MercyReturn",3890,3070) with{Mercy=true},
        Marker("Arrival",128,128),new("Exit","Return to Mercy","TLM_ACTI_FF_Exit",128,256,12,2),
        new("Ready","Continue the fair: courier scene","TLM_ACTI_FF_Ready",1024,768,12,3),
        new("Response","Current courier response","TLM_ACTI_FF_Response",1024,896,12,4),
        new("CaseControl","Original courier case: access and custody","TLM_ACTI_FF_CaseControl",1152,768,12,5),
        new("Firing","Ground-level firing-position inspection","TLM_ACTI_FF_Firing",1792,1280,12,6),
        new("Landing","Ground-level landing inspection","TLM_ACTI_FF_Landing",1792,256,12,7),
        new("Competition","Optional competition: unavailable","TLM_ACTI_FF_Competition",256,1280,12,8),
        new("Status","Fair facts and original custody","TLM_ACTI_FF_Status",128,384,12,9),
        new("OccupationBoard","Dominion order: occupation representation","TLM_ACTI_FF_OccupationBoard",1024,1024,12,10),
        new("OriginalCase","Original courier case",CaseId,1152,896,32),
        new("OriginalSilver","Original spent silver cartridge case",SilverId,1792,1408,32),
        new("Whitcomb",Names["whitcomb"],"TLM_NPC_FF_Whitcomb",384,512,16,24,true),
        new("Brigg",Names["brigg"],"TLM_NPC_FF_Brigg",1664,512,16,25,true),
        new("Grey",Names["grey"],"TLM_NPC_FF_Grey",1664,1152,16,26,true),
        new("Flint",Names["flint"],"TLM_NPC_FF_Flint",1536,1280,16,27,true),
        new("Juno",Names["threefords"],"TLM_NPC_FF_Juno",1152,896,16,28,true),
        Marker("PritchardAnchor",768,768),Marker("TalbotAnchor",768,512),Marker("PikeAnchor",256,1152),Marker("BeldenAnchor",384,1152),
        Marker("PritchardReturn",128,0),Marker("TalbotReturn",256,0),Marker("PikeReturn",384,0),Marker("BeldenReturn",512,0)
    };
    public static readonly ActivatorSpec[] Activators=Pieces.Where(p=>p.Base.StartsWith("TLM_ACTI_")).Select(p=>new ActivatorSpec(p.Base,p.Name,new[]{"Clipboard","Folder"},"Use")).ToArray();
    public static readonly OwnCellSpec[] Cells={new(CellId,"Decoration Day camp-ground (staged Four Flags)")};
    public static readonly PlacedSpec[] Placed=Pieces.Select(p=>new PlacedSpec("TLM_REF_FF_"+p.Alias,p.Mercy?Spec.TrialCell:CellId,p.Base,p.Base=="XMarker"?"Static":null,p.Mercy?760:p.Y,p.Mercy?(p.Alias=="Entry"?0:40):p.X,p.Z,true))
        .Concat(Enumerable.Range(0,9).SelectMany(x=>Enumerable.Range(0,7).Select(y=>new PlacedSpec($"TLM_REF_FF_Floor{x}{y}",CellId,"workshop_ShackMidFloor01B","Static",y*256,x*256,0)))).ToArray();
    public static readonly StageSpec[] Stages={
        new(10,"You reached the Decoration Day camp-ground. Four factions have been invited."),
        new(11,"Four flags, one table, dinner on the ground. Pritchard says nobody has drawn a gun on Decoration Day in forty years and he would take it kindly if you were not the first."),
        new(40),
        new(41,"You chose to investigate the firing position and landing."),
        new(42,"You chose to stay with the courier. What she can tell you depends on whether she is still alive to speak."),
        new(43,"The delegates and local witnesses backed the Decoration Day truce. Brigg accepted a limited search instead of taking the camp-ground."),
        new(44,"You took the courier's case."),new(45,"You found the courier dead at the fair. Her case may still hold evidence."),
        new(46,"You encountered the courier at the fair during the staged shooting scene."),
        new(50,"You inspected the spent silver case at the firing position."),new(51,"One empty case, silver, standing on end on the bell-rail where it would be found. Edda Flint was already there. She put it on her string."),
        new(60,"The courier's case holds a strip of brass punched with holes, a sketch of a ridge with lamps drawn on it, and one line of writing: a ledger number, in Silas Vane's hand."),
        new(70,"The Dominion holds the camp-ground. Brigg says it is for the public safety and will be for as long as the public is unsafe."),
        new(100,"You read the courier's ledger line, numbered 4117, and the Blackstone sketch.",true),
        new(101,"Pritchard read the number twice and sat down. He has eaten supper with Silas Vane for twenty years.")};
    public static readonly AliasSpec[] Aliases=Pieces.Select(p=>new AliasSpec(p.Alias,Fill.Placed,AllowDisabled:true,AllowDead:p.Person,Placed:"TLM_REF_FF_"+p.Alias,Scripts:p.Who==0?Array.Empty<ScriptBind>():new[]{new ScriptBind("TLM:FourFlagsTalk",new IntProp("Who",p.Who))}))
        .Concat(new[]{"Pritchard","Talbot","Pike","Belden"}.Select((n,i)=>new AliasSpec(n,Fill.ScriptFilled,AllowDead:true,AllowDisabled:true,Scripts:new[]{new ScriptBind("TLM:FourFlagsTalk",new IntProp("Who",20+i))})))
        .Append(new AliasSpec("Player",Fill.Player,Scripts:new[]{new ScriptBind("TLM:FourFlagsTalk",new IntProp("Who",0))})).ToArray();
    public static readonly QuestSpec Quest=new(QuestId,"The Four Flags","MainQuest",55,false,Stages,
        new[]{new ObjectiveSpec(10,"Hear what the four flags are offering"),new ObjectiveSpec(40,"The courier is down. Choose a response"),new ObjectiveSpec(60,"Open the original courier case")},Aliases,
        new ScriptBind("TLM:MQ03Quest",new Prop[]{new FormProp("TLM_MQ01","TLM_MQ01"),new FormProp("TLM_MQ02A",NightMail.QuestId),new FormProp("TLM_MQ02B",Greenwater.QuestId),new FormProp("TLM_MQ02C",RedHollow.RoadId),
            new FormProp("FirstDone","TLM_G_MQ01_Done"),
            new AliasListProp("Cast",new[]{"Pritchard","Talbot","Pike","Belden","Whitcomb","Brigg","Grey","Flint","Juno"}.Select(n=>(QuestId,n)).ToArray()),
            new FormProp("RailReported","TLM_G_MQ02A_Reported"),new FormProp("RiverReported","TLM_G_MQ02B_Reported"),new FormProp("HollowReported","TLM_G_MQ02C_Reported")}
            .Concat(Aliases.Where(a=>new[]{"Player","Arrival","OriginalCase","OriginalSilver","OccupationBoard"}.Contains(a.Name)).Select(a=>new AliasProp("Alias_"+a.Name,a.Name))).ToArray()),
        new[]{new ScriptBind("TLM:FourFlagsWalk",new Prop[]{new VanillaProp("MarkerBase","XMarker","Static")}
            .Concat(Aliases.Select(a=>new AliasProp("Alias_"+a.Name,a.Name)))
            .Concat(Messages.Select(m=>new FormProp(m.EditorId[Prefix.Length..],m.EditorId))).ToArray())});
    // This tiny entry adapter alone is copied into the exterior, after every
    // old allocation. The MQ03 ledger, own cell and actors are never cloned.
    public static readonly QuestSpec Entry=new(EntryId,"Four Flags entry adapter","None",30,false,
        Array.Empty<StageSpec>(),Array.Empty<ObjectiveSpec>(),
        new[]{new AliasSpec("Entry",Fill.Placed,AllowDisabled:true,Placed:"TLM_REF_FF_Entry",Scripts:new[]{new ScriptBind("TLM:FourFlagsTalk",new IntProp("Who",1),new FormProp("FairQuest",QuestId))}),
              new AliasSpec("MercyReturn",Fill.Placed,AllowDisabled:true,Placed:"TLM_REF_FF_MercyReturn")},
        new ScriptBind("TLM:FourFlagsEntry",new FormProp("FairQuest",QuestId),new AliasProp("Entry","Entry"),new AliasProp("MercyReturn","MercyReturn")));
}
