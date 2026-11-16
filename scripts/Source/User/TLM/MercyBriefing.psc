Scriptname TLM:MercyBriefing extends Quest
{Development preview, attached to TLM_MercyBriefing: ACT1-RUNTIME-001, the
Mercy briefing and the optional review copy (docs/design/ACT1_RUNTIME_001.md).

After the dispatch has been delivered and the main quest's debrief is over,
Owen Pritchard can be asked about the three roads. He says what the accepted
writing has him say about each, and about the pike he can be asked what to put
to Quill; he then offers his 2298 review copy, a book the player can read,
once.

This is a utility task of its own. It is NOT TLM_MQ02 and its stages 10 and 20
are NOT that quest's stages. It starts no road, finishes none, sets no stage
of TLM_MQ02c, grants no evidence flag, pays nothing and moves nobody. The
three destinations are not built.

What it keeps to:
  - It changes nothing unless the main quest's delivery is acknowledged, its
    stages 50, 60 and 100 are set, its Done global is 1, the person asked is
    alive and in no fight and the player is alive. All of that is read again
    after every box, before anything is set or given.
  - A visit is the hub, then at most one road, then (the pike only) at most
    the one exchange about the copy. Then it ends. No loop.
  - Stage 10 and the objective come with the first hub; stage 20 and the
    objective's completion once, after a road's brief was actually shown.
    (The quest record itself is started, with no stage and no objective,
    the first time an activation is handed to it.)
  - One copy, on the explicit Take only. The intent is written down before
    the game is asked for the book; the book is acknowledged from the count
    the player then holds. A copy in the inventory, a copy once issued or an
    intent not acknowledged each mean no second request, ever.
  - Whether the copy is carried is read from the inventory when asked
    (HasReviewCopy). It is never remembered and never inferred.
  - Nothing here runs on a timer, on start-up or on loading a game. The
    script's variables are kept by a save as they are.

The lines are in tools/PluginBuilder/SpecMercyBriefing.cs, each taken word for
word from the accepted writing; which field each comes from is in
docs/design/ACT1_RUNTIME_001_MAPPING.json, and tools/papyrus_sim checks it.

NOT COMPILED. NOT RUN IN THE GAME. It runs in the project's stand-in engine
(tools/papyrus_sim/test_mercy_briefing.py), whose rules for a box with
buttons, for AddItem and for a quest that is complete and still running are
marked there as seen, documented or assumed.}

Group MainQuest
	Quest Property TLM_MQ01 Auto Const Mandatory
	{Read only: three stages and the acknowledgment of the delivery.}
	GlobalVariable Property TLM_G_MQ01_Done Auto Const Mandatory
	{Read only.}
EndGroup

Group Briefing
	ReferenceAlias Property Alias_Briefer Auto Const
	{Whoever was asked: the objective points at them. Empty until the first
	hub. Without it the objective has nobody to point at and nothing else
	changes.}
	Form Property ReviewCopy Auto Const Mandatory
	{TLM_BOOK_Docket2298}
	Message Property HubLine Auto Const Mandatory
	{Buttons, in this order: the rail, the river, Red Hollow, not now.}
	Message Property RailLine Auto Const Mandatory
	Message Property RiverLine Auto Const Mandatory
	Message Property PikeLine Auto Const Mandatory
	{Buttons: what to ask Quill, continue.}
	Message Property DocketLine Auto Const Mandatory
	{Buttons: take the review copy, leave it.}
	Message Property DocketIssuedLine Auto Const Mandatory
	{The same speech with no Take: shown when no copy can be given.}
	Message Property CopyIssuedNote Auto Const Mandatory
	Message Property CopyPendingNote Auto Const Mandatory
	Message Property HandOffLine Auto Const
	{Pritchard's hand-off with a footer that says to ask again. None: the
	first section's own hand-off is shown.}
EndGroup

; The hub's buttons, the pike's and the copy's, by place. The same numbers as
; tools/logic_model/mercy_briefing_model.py; the stand-in's tests compare them.
int HUB_RAIL = 0 Const
int HUB_RIVER = 1 Const
int HUB_PIKE = 2 Const
int HUB_NOT_NOW = 3 Const
int PIKE_ASK_QUILL = 0 Const
int PIKE_CONTINUE = 1 Const
int COPY_TAKE = 0 Const
int COPY_LEAVE = 1 Const

int ACK_POLLS = 10 Const

; A briefing is open. Claimed with no call into the game between the test and
; the claim, as TLM:Act1Walk claims a conversation.
bool busy = false
; Private bookkeeping of the hand-over. Not knowledge flags and not stages of
; any later quest: a future migration would have to map them on purpose.
bool CopyIssued = false
bool CopyGrantPending = false

Event OnStageSet(int auiStageID, int auiItemID)
	; One line per stage event in the game's script log, as TLM_MQ01 writes.
	Debug.Trace("TLM_MercyBriefing: stage " + auiStageID + " item " + auiItemID)
EndEvent

; ================================================================ the offer

bool Function Offer(Actor akBriefer)
	{Called by TLM:Act1Walk when Pritchard is activated after the chapter.
	True: the briefing took this activation. False: it is not to be had as
	things stand, nothing was shown or changed, and the first section ends
	as it always did.}
	If busy
		Debug.Trace("TLM_MercyBriefing: a briefing is already open; this activation is ignored")
		Return true
	EndIf
	; Its own quest first, so that nothing below depends on what the script
	; of a quest that was never started can read. Starting it sets no stage,
	; shows no objective and puts nothing in the journal: the task begins
	; with the first hub, in Brief.
	If !IsRunning()
		Start()
	EndIf
	If !Ready() || !IsOpen(akBriefer)
		Return false
	EndIf
	; The two checks call into the game, so another activation may have come
	; in meanwhile. Nothing between this test and the claim does.
	If busy
		Return true
	EndIf
	busy = true
	Brief(akBriefer)
	busy = false
	Return true
EndFunction

bool Function Ready()
	{Everything the briefing cannot do without is filled in. What is not is
	named in the script log.}
	bool ok = true
	If !TLM_MQ01
		Debug.Trace("TLM_MercyBriefing: not bound: TLM_MQ01")
		ok = false
	EndIf
	If !TLM_G_MQ01_Done
		Debug.Trace("TLM_MercyBriefing: not bound: TLM_G_MQ01_Done")
		ok = false
	EndIf
	If !ReviewCopy
		Debug.Trace("TLM_MercyBriefing: not bound: ReviewCopy")
		ok = false
	EndIf
	If !HubLine || !RailLine || !RiverLine || !PikeLine
		Debug.Trace("TLM_MercyBriefing: not bound: one of HubLine, RailLine, RiverLine, PikeLine")
		ok = false
	EndIf
	If !DocketLine || !DocketIssuedLine || !CopyIssuedNote || !CopyPendingNote
		Debug.Trace("TLM_MercyBriefing: not bound: one of DocketLine, DocketIssuedLine, CopyIssuedNote, CopyPendingNote")
		ok = false
	EndIf
	Return ok
EndFunction

bool Function IsOpen(Actor akBriefer)
	{Read afresh every time: before the hub, and after every box before
	anything is set or given. Reads only.}
	If !akBriefer || akBriefer.IsDead() || akBriefer.IsInCombat()
		Return false
	EndIf
	Actor player = Game.GetPlayer()
	If !player || player.IsDead()
		Return false
	EndIf
	If !TLM_MQ01.GetStageDone(50) || !TLM_MQ01.GetStageDone(60) || !TLM_MQ01.GetStageDone(100)
		Return false
	EndIf
	If TLM_G_MQ01_Done.GetValueInt() != 1
		Return false
	EndIf
	TLM:MQ01Quest mainScript = TLM_MQ01 as TLM:MQ01Quest
	If !mainScript
		Return false
	EndIf
	Return mainScript.DeliveryAcknowledged()
EndFunction

Message Function HandOffLineOr(Message akUsual)
	{What Pritchard's hand-off is shown as: with the footer that says to ask
	him again, if the briefing is bound; otherwise the usual line.}
	If HandOffLine && Ready()
		Return HandOffLine
	EndIf
	Return akUsual
EndFunction

; ================================================================ one visit

Function Brief(Actor akBriefer)
	If Alias_Briefer && Alias_Briefer.GetActorReference() != akBriefer
		Alias_Briefer.ForceRefTo(akBriefer)
	EndIf
	If !GetStageDone(10)
		SetStage(10)
		SetObjectiveDisplayed(10)
	EndIf

	int road = HubLine.Show()
	If !IsOpen(akBriefer)
		Debug.Trace("TLM_MercyBriefing: no longer to be had when the hub closed (button " + road + "); nothing shown or changed")
		Return
	EndIf
	bool presented = false
	If road == HUB_RAIL
		presented = RailLine.Show() >= 0
	ElseIf road == HUB_RIVER
		presented = RiverLine.Show() >= 0
	ElseIf road == HUB_PIKE
		int follow = PikeLine.Show()
		presented = follow >= 0
		If follow == PIKE_ASK_QUILL
			If IsOpen(akBriefer)
				AboutTheCopy(akBriefer)
			EndIf
		EndIf
	Else
		; "Not now.", or no answer.
		Return
	EndIf
	If presented
		If IsOpen(akBriefer)
			Finish()
		Else
			Debug.Trace("TLM_MercyBriefing: no longer to be had when the brief closed; the task is not completed by it")
		EndIf
	EndIf
	TraceState()
EndFunction

Function Finish()
	{Once: a road's brief was shown. The utility task is complete; nothing of
	any later quest is.}
	If GetStageDone(20)
		Return
	EndIf
	SetObjectiveCompleted(10)
	SetStage(20)
EndFunction

; ================================================================= the copy

Function AboutTheCopy(Actor akBriefer)
	{Pritchard's account of 2298 and, once, his review copy.}
	Actor player = Game.GetPlayer()
	Acknowledge(player)
	If CopyIssued || CopyGrantPending || player.GetItemCount(ReviewCopy) > 0
		; No button may promise a second copy.
		DocketIssuedLine.Show()
		If CopyGrantPending
			SayPending(player)
		Else
			CopyIssuedNote.Show()
		EndIf
		Return
	EndIf
	If DocketLine.Show() != COPY_TAKE
		Return
	EndIf
	If !IsOpen(akBriefer)
		Debug.Trace("TLM_MercyBriefing: no longer to be had when the copy was taken; none is given")
		Return
	EndIf
	GiveCopy(player)
EndFunction

Function GiveCopy(Actor akPlayer)
	If akPlayer.GetItemCount(ReviewCopy) > 0
		Return
	EndIf
	; No call into the game between this test and the claim.
	If CopyIssued || CopyGrantPending
		Return
	EndIf
	CopyGrantPending = true
	akPlayer.AddItem(ReviewCopy, 1, false)
	; The game is asked once. It is then only looked at, for a second at the
	; most; it is never asked again.
	int polls = 0
	While polls < ACK_POLLS && akPlayer.GetItemCount(ReviewCopy) == 0
		Utility.Wait(0.1)
		polls += 1
	EndWhile
	If akPlayer.GetItemCount(ReviewCopy) > 0
		CopyIssued = true
		CopyGrantPending = false
		Debug.Trace("TLM_MercyBriefing: review copy given; the player holds " + akPlayer.GetItemCount(ReviewCopy))
	Else
		SayPending(akPlayer)
	EndIf
EndFunction

Function Acknowledge(Actor akPlayer)
	{An intent that was never acknowledged (the game was saved or closed in
	the middle) is settled by what the player holds. Nothing is given.}
	If CopyGrantPending
		If akPlayer.GetItemCount(ReviewCopy) > 0
			CopyIssued = true
			CopyGrantPending = false
			Debug.Trace("TLM_MercyBriefing: the review copy asked for earlier is in the inventory; acknowledged, none given again")
		EndIf
	EndIf
EndFunction

Function SayPending(Actor akPlayer)
	{Fails closed. For whoever is testing: what to write down.}
	Debug.Trace("TLM_MercyBriefing: FAIL CLOSED: the review copy was asked for once and is not in the inventory (count " + akPlayer.GetItemCount(ReviewCopy) + "). It is not asked for again and none is claimed as given. CopyIssued=" + CopyIssued + " CopyGrantPending=" + CopyGrantPending + ". The three briefs still work. Report this line.", 2)
	CopyPendingNote.Show()
EndFunction

; ============================================================ what is asked

bool Function HasReviewCopy()
	{The exact copy is in the player's inventory now. Read when asked: neither
	CopyIssued nor the task's progress stands in for it.}
	Actor player = Game.GetPlayer()
	If !player || !ReviewCopy
		Return false
	EndIf
	Return player.GetItemCount(ReviewCopy) > 0
EndFunction

bool Function WasCopyIssued()
	{History of this preview only: a copy was given and seen in the inventory.}
	Return CopyIssued
EndFunction

bool Function IsCopyGrantPending()
	{A copy was asked for and never seen in the inventory.}
	Return CopyGrantPending
EndFunction

Function TraceState()
	{One line in the script log. From the console: cqf TLM_MercyBriefing TraceState}
	Debug.Trace("TLM_MercyBriefing: begun=" + GetStageDone(10) + " complete=" + GetStageDone(20) + " objective shown=" + IsObjectiveDisplayed(10) + " objective complete=" + IsObjectiveCompleted(10) + " CopyIssued=" + CopyIssued + " CopyGrantPending=" + CopyGrantPending + " HasReviewCopy=" + HasReviewCopy())
EndFunction
