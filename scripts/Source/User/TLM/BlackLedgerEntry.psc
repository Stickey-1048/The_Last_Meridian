Scriptname TLM:BlackLedgerEntry extends Quest
{Only the Mercy-side entry/return binding. No second story ledger.}
Quest Property MainQuest Auto Const Mandatory
ReferenceAlias Property Entry Auto Const Mandatory
ReferenceAlias Property MercyReturn Auto Const Mandatory
ReferenceAlias Property PublicControl Auto Const Mandatory
ReferenceAlias Property FinishControl Auto Const Mandatory
Bool Function OpenFrom(Quest actualFirstSection)
    If !IsRunning()
        If !Start() || !IsRunning()
            Return false
        EndIf
    EndIf
    TLM:BlackLedgerWalk chapter = MainQuest as TLM:BlackLedgerWalk
    If !chapter || !chapter.Bind(actualFirstSection,Entry.GetReference(),MercyReturn.GetReference())
        Return false
    EndIf
    PublicControl.GetReference().Enable()
    FinishControl.GetReference().Enable()
    Return true
EndFunction
