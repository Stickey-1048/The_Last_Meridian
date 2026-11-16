Scriptname TLM:Act1Guide extends ReferenceAlias
{Development-only, optional directions. Activation reads state; it never sets
a stage, gives an item or resolves an encounter. Not evidence or world lettering.}

Quest Property TLM_MQ01 Auto Const Mandatory
int Property Place Auto Const Mandatory
bool Property Exterior = false Auto Const
{Only the exterior addon sets this; existing QASmoke guide copy stays unchanged.}
; 1 wreck, 2 caravan road, 3 Mercy Crossing.

Event OnActivate(ObjectReference akActionRef)
	If akActionRef != Game.GetPlayer()
		Return
	EndIf
	TLM:Act1Walk walk = GetOwningQuest() as TLM:Act1Walk
	If !walk || !walk.CanReadGuide()
		Return
	EndIf
	string here = "Wreck - the marshal and scattered papers."
	If Place == 2
		here = "Caravan road - the wagon and the Tellico Cutters."
	ElseIf Place == 3
		here = "Mercy Crossing - the timber posts and townsfolk."
		If Exterior
			here = "Mercy Crossing - the fenced cabin yard and townsfolk."
		EndIf
	EndIf
	string next = ""
	; Completed flags, not numeric stage comparisons: an early town visit can
	; set 40/34 without the dispatch's stage20 ever having happened.
	If TLM_MQ01.GetStageDone(60)
		next = "First-section demo complete. Greenwater, Red Hollow and Iron Junction are not implemented here; there are no onward route choices. Optional rail evidence can still be explored, or you can exit the game."
	ElseIf !TLM_MQ01.GetStageDone(20)
		If Place == 1
			next = "Next: search the ground here beside the marshal for the dispatch case. Other papers are optional evidence; this guide is only help."
		Else
			next = "Next: return to the wreck and search the ground beside the marshal for the dispatch case. Other papers are optional evidence; this guide is only help."
		EndIf
	ElseIf TLM_MQ01.GetStageDone(50)
		next = "Next: speak to Owen Pritchard again to finish the dispatch hand-off. Continue dismisses each reply."
	ElseIf TLM_MQ01.GetStageDone(40) || Place == 3
		next = "Next: speak to Sheriff Owen Pritchard in Mercy Crossing and hand over the marshal's dispatch."
	Else
		next = "Next: take the dispatch to Sheriff Owen Pritchard in Mercy Crossing, beyond the timber posts. The caravan by the road is optional: Fight means combat; Leave does not itself start a fight."
		If Exterior
			next = "Next: find Sheriff Pritchard in the fenced cabin yard beyond the timber gateway. The caravan by the wooden road posts is optional. Fight starts combat; Leave does not. To bypass the hold-up, keep east of it."
		EndIf
	EndIf
	Debug.MessageBox("DEMO GUIDE - DIRECTIONS\n" + here + "\n\n" + next)
EndEvent
