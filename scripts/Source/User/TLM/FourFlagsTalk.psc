Scriptname TLM:FourFlagsTalk extends ReferenceAlias
{Thin alias forwarding only. Scene, consent, custody and progress belong to
the one master MQ03 ledger and its presentation controller.}

int Property Who Auto Const Mandatory
Quest Property FairQuest Auto Const

Event OnActivate(ObjectReference akActionRef)
	If akActionRef == Game.GetPlayer()
		TLM:FourFlagsWalk fair = GetOwningQuest() as TLM:FourFlagsWalk
		If !fair
			fair = FairQuest as TLM:FourFlagsWalk
		EndIf
		If fair
			fair.Used(Who)
		EndIf
	EndIf
EndEvent

Event OnPlayerLoadGame()
	TLM:FourFlagsWalk fair = GetOwningQuest() as TLM:FourFlagsWalk
	If fair && Who == 0
		fair.Loaded()
	EndIf
EndEvent
