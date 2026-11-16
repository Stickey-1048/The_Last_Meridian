Scriptname TLM:Act1Talk extends ReferenceAlias
{Development only. On the aliases of TLM_A1 that hold somebody the player can
speak to in the first section's rough cut, and on the alias of the marshal's
revolver (docs/design/TLM_ACT1_first_section.md). It must be removed before
any release, with its quest.

It knows nothing itself. When the player activates the reference, or picks
it up, it tells TLM:Act1Walk on the owning quest who or what that was; what
is said, and what follows from an answer, is there.

COMPILES (2026-11-14). The half that hears a pick-up RAN IN THE GAME that
day: the marshal's revolver, picked up in scenario 12, was heard here and the
six rounds were given (docs/design/VERIFY_LOG.md, the sixteenth and
seventeenth runs). The half that hears somebody being spoken to has NOT RUN
IN THE GAME: no person of the section has been activated there, because that
opens a box and nobody was at the keyboard. What it rests on has run there:
an alias's script hears its reference being activated by the player
(2026-11-13, the fourteenth run).}

int Property Who Auto Const Mandatory
{Who or what this is, in the numbers of TLM:Act1Walk: 1 Reese Dunmore,
2 Nell Fenwick, 3 Abel Rudd, 4 a Cutter, 5 Owen Pritchard, 6 Ada Pike,
7 Silas Vane, 8 Miriam Keene, 9 Jonah Talbot, 10 Corwin Haskell;
20 the marshal's revolver.}

Event OnActivate(ObjectReference akActionRef)
	If akActionRef != Game.GetPlayer()
		Return
	EndIf
	TLM:Act1Walk walk = GetOwningQuest() as TLM:Act1Walk
	If walk
		walk.Spoken(Who, GetActorReference())
	EndIf
EndEvent

Event OnContainerChanged(ObjectReference akNewContainer, ObjectReference akOldContainer)
	If akNewContainer != Game.GetPlayer()
		Return
	EndIf
	TLM:Act1Walk walk = GetOwningQuest() as TLM:Act1Walk
	If walk
		walk.Taken(Who)
	EndIf
EndEvent
