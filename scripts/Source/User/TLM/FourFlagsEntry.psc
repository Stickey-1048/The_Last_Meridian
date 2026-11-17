Scriptname TLM:FourFlagsEntry extends Quest
{Two-reference entry adapter only. It owns no story, cast, case or history.}

Quest Property FairQuest Auto Const Mandatory
ReferenceAlias Property Entry Auto Const Mandatory
ReferenceAlias Property MercyReturn Auto Const Mandatory

bool Function OpenFrom(Quest actualFirstSection)
	If !IsRunning()
		If !Start() || !IsRunning()
			Return false
		EndIf
	EndIf
	TLM:FourFlagsWalk fair = FairQuest as TLM:FourFlagsWalk
	If !fair
		Return false
	EndIf
	Return fair.Bind(actualFirstSection,Entry.GetReference(),MercyReturn.GetReference())
EndFunction
