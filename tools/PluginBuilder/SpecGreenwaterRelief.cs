namespace Tlm.PluginBuilder;

// Owner-approved DA8164F2 + Sam532668DD, derived technical follow-up UI only.
// No new voiced character, faction, terrain or alteration of river history.
public static class GreenwaterRelief
{
    public const string QuestId="TLM_GW_Relief",Prefix="TLM_MSG_GR_";
    static MessageSpec Ui(string id,string title,string text,params string[] buttons)=>
        new(Prefix+id,null,title+"\n\n"+text,true,(buttons.Length==0?new[]{"Continue"}:buttons).Select(b=>new ButtonSpec(b)).ToArray());
    public static readonly MessageSpec[] Messages={
        Ui("NotReady","[Winter relief unavailable]","Finish the Greenwater road first. Relief also needs verified Corn and caps records and a consistent completed cargo account. No food, money or river result was changed."),
        Ui("Unavailable","[Food request unavailable]","This request could not be safely confirmed. It will not be retried or refunded automatically. Other relief changes are blocked; you can still inspect the ledger. Keep this save for diagnosis."),
        Ui("Blocked","[Relief request held]","An earlier request is unresolved. No further donation, purchase or local step can run. Inspect the current ledger?","Inspect ledger","Close"),
        Ui("Stores","[Winter relief]","Your river decision remains unchanged. Bring real Corn here or buy a finite batch at Mercy's supply shelter. Nothing runs down while you are away.","Inspect reserve","Donate Corn","Advance local 15-day step","Close"),
        Ui("StoresFinal","[Six relief steps accounted for]","No seventh step or new stock period exists. Outstanding need can still be cleared with real Corn. Earlier hunger remains in the record.","Inspect reserve","Donate Corn","Close"),
        Ui("Supply","[Mercy relief supply]","Buy 10 Corn for 20 caps. Stock this period: %g Corn of 30. Buying is NOT a donation; carry it to Greenwater. Scavenged or grown Corn works too.","Buy one batch","Inspect relief ledger","Close"),
        Ui("Status","[Current relief stores]","Step %g of 6. Reserve: %g units. Shortfall: %g. Remaining planned demand: %g. Donated: %g units. Next step costs 150. Ten units represent one provisioning day; this is a simplified ledger."),
        Ui("ForecastCovered","[Relief forecast]","Covered for the remaining planned steps. This is the bounded ledger's forecast, not a promise of universal town prosperity or erased past hunger."),
        Ui("ForecastNeeded","[Food still needed]","More food is needed before winter is covered. Shortfall means unmet need, not a recorded death toll. You can return with Corn. Nothing runs down by waiting or leaving."),
        Ui("PastHunger","[Earlier hunger remains]","A previous local step recorded a shortage. Aid clears current shortfall first, but cannot undo earlier hunger. No famine deaths have been inferred."),
        Ui("DonateMany","[Choose Corn quantity]","Only actual Corn removed from your inventory is credited. Each Corn adds 10 relief units; you keep the rest.","Give 1 Corn","Give 5 Corn","Give 10 Corn","Cancel"),
        Ui("DonateFive","[Choose Corn quantity]","Each Corn adds 10 relief units. You do not currently hold 10 Corn.","Give 1 Corn","Give 5 Corn","Cancel"),
        Ui("DonateOne","[Choose Corn quantity]","You have fewer than 5 Corn. One actual Corn can add 10 relief units.","Give 1 Corn","Cancel"),
        Ui("NoFood","[No Corn to donate]","No Corn is available in your inventory. Gather, grow or bring Corn later; buying food is optional. Nothing was taken."),
        Ui("ConfirmDonate","[Donate food?]","Give %g Corn from your inventory to the town stores. Each item is consumed once. This clears %g shortfall and adds %g reserve units. You keep the rest.","Donate this food","Cancel"),
        Ui("Donated","[Food received]","Your actual Corn contribution was consumed and credited once. Inspect the reserve to see current need. Your earlier river decision and any past hunger remain unchanged."),
        Ui("ConfirmPurchase","[Buy relief food?]","Pay 20 real caps for 10 actual Corn. This uses 10 of the current period's finite 30 stock. The town receives nothing until you donate the food at Greenwater.","Pay 20 caps; receive 10 Corn","Cancel"),
        Ui("Purchased","[Food purchased]","20 caps paid; 10 Corn received. Town reserves did not change. Carry the food to Greenwater's separate winter-relief stores control to contribute it."),
        Ui("NoStock","[Purchase unavailable]","This period has fewer than 10 Corn left, or you have fewer than 20 caps. No payment was taken. Gathered and grown Corn remain valid donations."),
        Ui("ConfirmStep","[Advance local relief step?]","This accounts for 15 days of town provisions only; it does NOT move the game's clock. Demand: 150 units. Projected reserve: %g; shortfall: %g. Nothing advances unless you confirm.","Advance one relief step","Keep gathering"),
        Ui("StepDone","[Local relief step recorded]","One 15-day provision step was accounted for. No global time or other quest changed. Inspect the ledger for current need; real Corn can clear a shortage later."),
        Ui("CompleteNotice","[Bounded winter relief covered]","All six local steps are accounted for and outstanding shortfall is clear. Earlier hunger, the original grain outcome and any lie remain part of the record. No new reward or reputation was invented."),
    };
    public static readonly QuestSpec Quest=new(QuestId,"Greenwater winter relief (local ledger)","None",30,false,
        new[]{new StageSpec(10,"The completed river cargo account was recorded once."),new StageSpec(20,"An actual Corn contribution was credited."),new StageSpec(30,"The first explicit local provision step was recorded."),new StageSpec(90,"Six provision steps and outstanding shortfall are accounted for.",CompleteQuest:true)},
        Array.Empty<ObjectiveSpec>(),
        new[]{new AliasSpec("Stores",Fill.ScriptFilled),new AliasSpec("Supply",Fill.ScriptFilled),
              new AliasSpec("Player",Fill.Player,Scripts:new[]{new ScriptBind("TLM:GreenwaterTalk",new IntProp("Who",0))})},
        new ScriptBind("TLM:GreenwaterRelief",new Prop[]{new FormProp("TLM_MQ02B",Greenwater.QuestId),new AliasProp("Alias_Stores","Stores"),new AliasProp("Alias_Supply","Supply"),
            new StrictVanillaProp("Corn","Corn","Ingestible","Corn"),new StrictVanillaProp("Caps","Caps001","MiscItem","Bottlecap")}
            .Concat(Messages.Select(m=>new FormProp(m.EditorId[Prefix.Length..],m.EditorId))).ToArray()));
}
