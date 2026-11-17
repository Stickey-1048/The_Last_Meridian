Scriptname TLM:FourFlagsWalk extends Quest
{Four Flags presentation and fixed original-cast visit adapter. Source only;
no game acceptance, projectile, terrain, audio or native inventory guarantee.}

Form Property MarkerBase Auto Const
Message Property PendingOrder Auto Const Mandatory
Message Property PikeCompare Auto Const Mandatory
Message Property PikeUnavailable Auto Const Mandatory
Message Property A_pike_mould_aside Auto Const Mandatory
ReferenceAlias Property Alias_Entry Auto Const Mandatory
ReferenceAlias Property Alias_MercyReturn Auto Const Mandatory
ReferenceAlias Property Alias_Arrival Auto Const Mandatory
ReferenceAlias Property Alias_Exit Auto Const Mandatory
ReferenceAlias Property Alias_Ready Auto Const Mandatory
ReferenceAlias Property Alias_Response Auto Const Mandatory
ReferenceAlias Property Alias_CaseControl Auto Const Mandatory
ReferenceAlias Property Alias_Firing Auto Const Mandatory
ReferenceAlias Property Alias_Landing Auto Const Mandatory
ReferenceAlias Property Alias_Competition Auto Const Mandatory
ReferenceAlias Property Alias_Status Auto Const Mandatory
ReferenceAlias Property Alias_OccupationBoard Auto Const Mandatory
ReferenceAlias Property Alias_OriginalCase Auto Const Mandatory
ReferenceAlias Property Alias_OriginalSilver Auto Const Mandatory
ReferenceAlias Property Alias_Whitcomb Auto Const Mandatory
ReferenceAlias Property Alias_Brigg Auto Const Mandatory
ReferenceAlias Property Alias_Grey Auto Const Mandatory
ReferenceAlias Property Alias_Flint Auto Const Mandatory
ReferenceAlias Property Alias_Juno Auto Const Mandatory
ReferenceAlias Property Alias_PritchardAnchor Auto Const Mandatory
ReferenceAlias Property Alias_TalbotAnchor Auto Const Mandatory
ReferenceAlias Property Alias_PikeAnchor Auto Const Mandatory
ReferenceAlias Property Alias_BeldenAnchor Auto Const Mandatory
ReferenceAlias Property Alias_PritchardReturn Auto Const Mandatory
ReferenceAlias Property Alias_TalbotReturn Auto Const Mandatory
ReferenceAlias Property Alias_PikeReturn Auto Const Mandatory
ReferenceAlias Property Alias_BeldenReturn Auto Const Mandatory
ReferenceAlias Property Alias_Pritchard Auto Const Mandatory
ReferenceAlias Property Alias_Talbot Auto Const Mandatory
ReferenceAlias Property Alias_Pike Auto Const Mandatory
ReferenceAlias Property Alias_Belden Auto Const Mandatory
ReferenceAlias Property Alias_Player Auto Const Mandatory
Message Property S_pritchard_fair_1 Auto Const Mandatory
Message Property S_pritchard_fair_2 Auto Const Mandatory
Message Property S_whitcomb_default_1 Auto Const Mandatory
Message Property S_whitcomb_offer_1 Auto Const Mandatory
Message Property S_whitcomb_rates_1 Auto Const Mandatory
Message Property S_whitcomb_big_1 Auto Const Mandatory
Message Property S_brigg_default_1 Auto Const Mandatory
Message Property S_brigg_offer_1 Auto Const Mandatory
Message Property S_brigg_offer_2 Auto Const Mandatory
Message Property S_brigg_dissent_1 Auto Const Mandatory
Message Property S_brigg_price_1 Auto Const Mandatory
Message Property S_brigg_price_2 Auto Const Mandatory
Message Property S_brigg_quill_1 Auto Const Mandatory
Message Property S_belden_default_1 Auto Const Mandatory
Message Property S_belden_offer_1 Auto Const Mandatory
Message Property S_belden_dissent_1 Auto Const Mandatory
Message Property S_belden_list_1 Auto Const Mandatory
Message Property S_belden_list_2 Auto Const Mandatory
Message Property S_belden_leave_1 Auto Const Mandatory
Message Property S_grey_default_1 Auto Const Mandatory
Message Property S_grey_offer_1 Auto Const Mandatory
Message Property S_grey_offer_2 Auto Const Mandatory
Message Property S_grey_dissent_1 Auto Const Mandatory
Message Property S_grey_cost_1 Auto Const Mandatory
Message Property S_grey_cost_2 Auto Const Mandatory
Message Property S_grey_train_1 Auto Const Mandatory
Message Property S_flint_default_1 Auto Const Mandatory
Message Property S_threefords_default_1 Auto Const Mandatory
Message Property S_threefords_dying_1 Auto Const Mandatory
Message Property S_threefords_dying_2 Auto Const Mandatory
Message Property S_flint_roof_1 Auto Const Mandatory
Message Property S_flint_who_1 Auto Const Mandatory
Message Property S_flint_hat_1 Auto Const Mandatory
Message Property S_brigg_rifles_1 Auto Const Mandatory
Message Property S_brigg_holds_1 Auto Const Mandatory
Message Property S_pritchard_case_1 Auto Const Mandatory
Message Property S_brigg_demand_1 Auto Const Mandatory
Message Property S_brigg_demand_courier_dead_1 Auto Const Mandatory
Message Property S_brigg_demand_talbot_1 Auto Const Mandatory
Message Property S_brigg_demand_talbot_courier_dead_1 Auto Const Mandatory
Message Property S_brigg_demand_no_whitcomb_1 Auto Const Mandatory
Message Property S_brigg_demand_no_whitcomb_courier_dead_1 Auto Const Mandatory
Message Property S_brigg_demand_no_belden_1 Auto Const Mandatory
Message Property S_brigg_demand_no_belden_courier_dead_1 Auto Const Mandatory
Message Property S_brigg_demand_no_grey_1 Auto Const Mandatory
Message Property S_brigg_demand_no_grey_courier_dead_1 Auto Const Mandatory
Message Property S_brigg_demand_no_officer_1 Auto Const Mandatory
Message Property S_brigg_demand_no_officer_courier_dead_1 Auto Const Mandatory
Message Property S_whitcomb_truce_1 Auto Const Mandatory
Message Property S_belden_truce_1 Auto Const Mandatory
Message Property S_grey_truce_1 Auto Const Mandatory
Message Property S_pritchard_truce_1 Auto Const Mandatory
Message Property S_whitcomb_truce_talbot_1 Auto Const Mandatory
Message Property S_belden_truce_talbot_1 Auto Const Mandatory
Message Property S_grey_truce_talbot_1 Auto Const Mandatory
Message Property S_talbot_truce_1 Auto Const Mandatory
Message Property S_brigg_truce_concession_pritchard_1 Auto Const Mandatory
Message Property S_brigg_truce_concession_talbot_1 Auto Const Mandatory
Message Property S_pritchard_courier_no_brigg_living_1 Auto Const Mandatory
Message Property S_pritchard_courier_no_brigg_dead_1 Auto Const Mandatory
Message Property S_talbot_courier_no_brigg_living_1 Auto Const Mandatory
Message Property S_talbot_courier_no_brigg_dead_1 Auto Const Mandatory
Message Property S_flint_courier_no_brigg_living_1 Auto Const Mandatory
Message Property S_flint_courier_no_brigg_dead_1 Auto Const Mandatory
Message Property D_fair_handbill_1 Auto Const Mandatory
Message Property D_fair_handbill_2 Auto Const Mandatory
Message Property D_fair_handbill_3 Auto Const Mandatory
Message Property D_silver_case_1 Auto Const Mandatory
Message Property D_silver_case_2 Auto Const Mandatory
Message Property D_courier_card_1 Auto Const Mandatory
Message Property D_courier_card_2 Auto Const Mandatory
Message Property D_courier_card_3 Auto Const Mandatory
Message Property Entry Auto Const Mandatory
Message Property NoReport Auto Const Mandatory
Message Property Travel Auto Const Mandatory
Message Property Layout Auto Const Mandatory
Message Property LayoutLimits Auto Const Mandatory
Message Property Ready Auto Const Mandatory
Message Property Shot Auto Const Mandatory
Message Property DeadCourier Auto Const Mandatory
Message Property NoCarrier Auto Const Mandatory
Message Property Occupation Auto Const Mandatory
Message Property OccupationSeen Auto Const Mandatory
Message Property PendingCourse Auto Const Mandatory
Message Property Case Auto Const Mandatory
Message Property Take Auto Const Mandatory
Message Property Public Auto Const Mandatory
Message Property Solo Auto Const Mandatory
Message Property Silver Auto Const Mandatory
Message Property GiveSilver Auto Const Mandatory
Message Property Landing Auto Const Mandatory
Message Property Competition Auto Const Mandatory
Message Property Exit Auto Const Mandatory
Message Property ReturnsPending Auto Const Mandatory
Message Property Blocked Auto Const Mandatory
Message Property Failed Auto Const Mandatory
Message Property Status Auto Const Mandatory
Message Property Custody Auto Const Mandatory
Message Property Unavailable Auto Const Mandatory

Quest sourceOwner = None
bool busy = false
int busyEpoch = -1
bool layoutRead = false
bool visitActive = false
Actor[] visitors
bool[] visitorWasDisabled
bool[] visitorPending
bool[] visitorCaptured
bool[] visitorStaged
ObjectReference entryPoint = None
ObjectReference returnPoint = None

TLM:MQ03Quest Function Road()
	Return Self as TLM:MQ03Quest
EndFunction

ObjectReference Function Ref(ReferenceAlias a)
	If !a
		Return None
	EndIf
	Return a.GetReference()
EndFunction

bool Function NodeCondition(string node)
	If node == "pritchard_fair"
		Return Road().GetStageDone(10) && !Road().GetStageDone(40)
	EndIf
	If node == "whitcomb_default"
		Return true
	EndIf
	If node == "whitcomb_offer"
		Return Road().GetStageDone(10) && !Road().GetStageDone(40)
	EndIf
	If node == "whitcomb_rates"
		Return true
	EndIf
	If node == "whitcomb_big"
		Return true
	EndIf
	If node == "brigg_default"
		Return true
	EndIf
	If node == "brigg_offer"
		Return Road().GetStageDone(10) && !Road().GetStageDone(40)
	EndIf
	If node == "brigg_dissent"
		Return true
	EndIf
	If node == "brigg_price"
		Return true
	EndIf
	If node == "brigg_quill"
		Return true
	EndIf
	If node == "belden_default"
		Return true
	EndIf
	If node == "belden_offer"
		Return Road().GetStageDone(10) && !Road().GetStageDone(40)
	EndIf
	If node == "belden_dissent"
		Return true
	EndIf
	If node == "belden_list"
		Return true
	EndIf
	If node == "belden_leave"
		Return true
	EndIf
	If node == "grey_default"
		Return true
	EndIf
	If node == "grey_offer"
		Return Road().GetStageDone(10) && !Road().GetStageDone(40)
	EndIf
	If node == "grey_dissent"
		Return true
	EndIf
	If node == "grey_cost"
		Return true
	EndIf
	If node == "grey_train"
		Return true
	EndIf
	If node == "flint_default"
		Return true
	EndIf
	If node == "threefords_default"
		Return true
	EndIf
	If node == "threefords_dying"
		Return Road().GetStageDone(42) && !Road().GetStageDone(100) && Usable(8)
	EndIf
	If node == "flint_roof"
		Return Road().GetStageDone(50)
	EndIf
	If node == "flint_who"
		Return true
	EndIf
	If node == "flint_hat"
		Return true
	EndIf
	If node == "brigg_rifles"
		Return Road().GetStageDone(40) && Road().GetStageDone(43) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && Usable(5)
	EndIf
	If node == "brigg_holds"
		Return Road().GetStageDone(70)
	EndIf
	If node == "pritchard_case"
		Return Road().GetStageDone(60) && !Road().GetStageDone(100)
	EndIf
	If node == "brigg_demand"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Usable(3) && Usable(6) && Usable(0) && Usable(8)
	EndIf
	If node == "brigg_demand_courier_dead"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Usable(3) && Usable(6) && Usable(0) && ActuallyDead(8)
	EndIf
	If node == "brigg_demand_talbot"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Usable(3) && Usable(6) && Unavailable(0) && Usable(1) && Usable(8)
	EndIf
	If node == "brigg_demand_talbot_courier_dead"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Usable(3) && Usable(6) && Unavailable(0) && Usable(1) && ActuallyDead(8)
	EndIf
	If node == "brigg_demand_no_whitcomb"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Unavailable(4) && Usable(8)
	EndIf
	If node == "brigg_demand_no_whitcomb_courier_dead"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Unavailable(4) && ActuallyDead(8)
	EndIf
	If node == "brigg_demand_no_belden"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Unavailable(3) && Usable(8)
	EndIf
	If node == "brigg_demand_no_belden_courier_dead"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Unavailable(3) && ActuallyDead(8)
	EndIf
	If node == "brigg_demand_no_grey"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Usable(3) && Unavailable(6) && Usable(8)
	EndIf
	If node == "brigg_demand_no_grey_courier_dead"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Usable(3) && Unavailable(6) && ActuallyDead(8)
	EndIf
	If node == "brigg_demand_no_officer"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Usable(3) && Usable(6) && Unavailable(0) && Unavailable(1) && Usable(8)
	EndIf
	If node == "brigg_demand_no_officer_courier_dead"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Usable(3) && Usable(6) && Unavailable(0) && Unavailable(1) && ActuallyDead(8)
	EndIf
	If node == "whitcomb_truce"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Usable(3) && Usable(6) && Usable(0)
	EndIf
	If node == "belden_truce"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Usable(3) && Usable(6) && Usable(0)
	EndIf
	If node == "grey_truce"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Usable(3) && Usable(6) && Usable(0)
	EndIf
	If node == "pritchard_truce"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Usable(3) && Usable(6) && Usable(0)
	EndIf
	If node == "whitcomb_truce_talbot"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Usable(3) && Usable(6) && Usable(1) && Unavailable(0)
	EndIf
	If node == "belden_truce_talbot"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Usable(3) && Usable(6) && Usable(1) && Unavailable(0)
	EndIf
	If node == "grey_truce_talbot"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Usable(3) && Usable(6) && Usable(1) && Unavailable(0)
	EndIf
	If node == "talbot_truce"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Usable(3) && Usable(6) && Usable(1) && Unavailable(0)
	EndIf
	If node == "brigg_truce_concession_pritchard"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Usable(3) && Usable(6) && Usable(0)
	EndIf
	If node == "brigg_truce_concession_talbot"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Usable(5) && Usable(4) && Usable(3) && Usable(6) && Unavailable(0) && Usable(1)
	EndIf
	If node == "pritchard_courier_no_brigg_living"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Unavailable(5) && Usable(0) && Usable(8)
	EndIf
	If node == "pritchard_courier_no_brigg_dead"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Unavailable(5) && Usable(0) && ActuallyDead(8)
	EndIf
	If node == "talbot_courier_no_brigg_living"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Unavailable(5) && Usable(1) && Unavailable(0) && Usable(8)
	EndIf
	If node == "talbot_courier_no_brigg_dead"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Unavailable(5) && Usable(1) && Unavailable(0) && ActuallyDead(8)
	EndIf
	If node == "flint_courier_no_brigg_living"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Unavailable(5) && Usable(7) && Unavailable(0) && Unavailable(1) && Usable(8)
	EndIf
	If node == "flint_courier_no_brigg_dead"
		Return Road().GetStageDone(40) && !Road().GetStageDone(41) && !Road().GetStageDone(42) && !Road().GetStageDone(43) && !Road().GetStageDone(44) && !Road().GetStageDone(70) && !Road().GetStageDone(100) && Unavailable(5) && Usable(7) && Unavailable(0) && Unavailable(1) && ActuallyDead(8)
	EndIf
	Return false
EndFunction

string Function SelectedEntry(int role)
	If role == 0
		If NodeCondition("pritchard_case")
			Return "pritchard_case"
		EndIf
		If NodeCondition("pritchard_courier_no_brigg_living")
			Return "pritchard_courier_no_brigg_living"
		EndIf
		If NodeCondition("pritchard_courier_no_brigg_dead")
			Return "pritchard_courier_no_brigg_dead"
		EndIf
		If NodeCondition("pritchard_fair")
			Return "pritchard_fair"
		EndIf
	EndIf
	If role == 1
		If NodeCondition("talbot_courier_no_brigg_living")
			Return "talbot_courier_no_brigg_living"
		EndIf
		If NodeCondition("talbot_courier_no_brigg_dead")
			Return "talbot_courier_no_brigg_dead"
		EndIf
	EndIf
	If role == 2
	EndIf
	If role == 3
		If NodeCondition("belden_offer")
			Return "belden_offer"
		EndIf
		If NodeCondition("belden_default")
			Return "belden_default"
		EndIf
	EndIf
	If role == 4
		If NodeCondition("whitcomb_offer")
			Return "whitcomb_offer"
		EndIf
		If NodeCondition("whitcomb_default")
			Return "whitcomb_default"
		EndIf
	EndIf
	If role == 5
		If NodeCondition("brigg_rifles")
			Return "brigg_rifles"
		EndIf
		If NodeCondition("brigg_holds")
			Return "brigg_holds"
		EndIf
		If NodeCondition("brigg_demand")
			Return "brigg_demand"
		EndIf
		If NodeCondition("brigg_demand_talbot")
			Return "brigg_demand_talbot"
		EndIf
		If NodeCondition("brigg_demand_no_whitcomb")
			Return "brigg_demand_no_whitcomb"
		EndIf
		If NodeCondition("brigg_demand_no_belden")
			Return "brigg_demand_no_belden"
		EndIf
		If NodeCondition("brigg_demand_no_grey")
			Return "brigg_demand_no_grey"
		EndIf
		If NodeCondition("brigg_demand_no_officer")
			Return "brigg_demand_no_officer"
		EndIf
		If NodeCondition("brigg_demand_courier_dead")
			Return "brigg_demand_courier_dead"
		EndIf
		If NodeCondition("brigg_demand_talbot_courier_dead")
			Return "brigg_demand_talbot_courier_dead"
		EndIf
		If NodeCondition("brigg_demand_no_whitcomb_courier_dead")
			Return "brigg_demand_no_whitcomb_courier_dead"
		EndIf
		If NodeCondition("brigg_demand_no_belden_courier_dead")
			Return "brigg_demand_no_belden_courier_dead"
		EndIf
		If NodeCondition("brigg_demand_no_grey_courier_dead")
			Return "brigg_demand_no_grey_courier_dead"
		EndIf
		If NodeCondition("brigg_demand_no_officer_courier_dead")
			Return "brigg_demand_no_officer_courier_dead"
		EndIf
		If NodeCondition("brigg_offer")
			Return "brigg_offer"
		EndIf
		If NodeCondition("brigg_default")
			Return "brigg_default"
		EndIf
	EndIf
	If role == 6
		If NodeCondition("grey_offer")
			Return "grey_offer"
		EndIf
		If NodeCondition("grey_default")
			Return "grey_default"
		EndIf
	EndIf
	If role == 7
		If NodeCondition("flint_roof")
			Return "flint_roof"
		EndIf
		If NodeCondition("flint_courier_no_brigg_living")
			Return "flint_courier_no_brigg_living"
		EndIf
		If NodeCondition("flint_courier_no_brigg_dead")
			Return "flint_courier_no_brigg_dead"
		EndIf
		If NodeCondition("flint_default")
			Return "flint_default"
		EndIf
	EndIf
	If role == 8
		If NodeCondition("threefords_dying")
			Return "threefords_dying"
		EndIf
		If NodeCondition("threefords_default")
			Return "threefords_default"
		EndIf
	EndIf
	Return ""
EndFunction

int Function SayNode(string node, Actor speakerActor, int role, int capturedEpoch, Actor[] party)
	If node == "pritchard_fair"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		If S_pritchard_fair_1.Show() != 0 || !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_pritchard_fair_2.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "whitcomb_default"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_whitcomb_default_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "whitcomb_offer"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_whitcomb_offer_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "whitcomb_rates"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_whitcomb_rates_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "whitcomb_big"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_whitcomb_big_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_default"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_default_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_offer"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		If S_brigg_offer_1.Show() != 0 || !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_offer_2.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_dissent"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_dissent_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_price"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		If S_brigg_price_1.Show() != 0 || !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_price_2.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_quill"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_quill_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "belden_default"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_belden_default_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "belden_offer"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_belden_offer_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "belden_dissent"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_belden_dissent_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "belden_list"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		If S_belden_list_1.Show() != 0 || !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_belden_list_2.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "belden_leave"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_belden_leave_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "grey_default"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_grey_default_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "grey_offer"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		If S_grey_offer_1.Show() != 0 || !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_grey_offer_2.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "grey_dissent"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_grey_dissent_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "grey_cost"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		If S_grey_cost_1.Show() != 0 || !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_grey_cost_2.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "grey_train"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_grey_train_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "flint_default"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_flint_default_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "threefords_default"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_threefords_default_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "threefords_dying"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		If S_threefords_dying_1.Show() != 0 || !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_threefords_dying_2.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "flint_roof"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_flint_roof_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "flint_who"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_flint_who_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "flint_hat"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_flint_hat_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_rifles"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_rifles_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_holds"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_holds_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "pritchard_case"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_pritchard_case_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_demand"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_demand_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_demand_courier_dead"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_demand_courier_dead_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_demand_talbot"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_demand_talbot_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_demand_talbot_courier_dead"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_demand_talbot_courier_dead_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_demand_no_whitcomb"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_demand_no_whitcomb_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_demand_no_whitcomb_courier_dead"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_demand_no_whitcomb_courier_dead_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_demand_no_belden"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_demand_no_belden_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_demand_no_belden_courier_dead"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_demand_no_belden_courier_dead_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_demand_no_grey"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_demand_no_grey_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_demand_no_grey_courier_dead"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_demand_no_grey_courier_dead_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_demand_no_officer"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_demand_no_officer_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_demand_no_officer_courier_dead"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_demand_no_officer_courier_dead_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "whitcomb_truce"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_whitcomb_truce_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "belden_truce"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_belden_truce_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "grey_truce"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_grey_truce_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "pritchard_truce"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_pritchard_truce_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "whitcomb_truce_talbot"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_whitcomb_truce_talbot_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "belden_truce_talbot"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_belden_truce_talbot_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "grey_truce_talbot"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_grey_truce_talbot_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "talbot_truce"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_talbot_truce_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_truce_concession_pritchard"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_truce_concession_pritchard_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "brigg_truce_concession_talbot"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_brigg_truce_concession_talbot_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "pritchard_courier_no_brigg_living"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_pritchard_courier_no_brigg_living_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "pritchard_courier_no_brigg_dead"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_pritchard_courier_no_brigg_dead_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "talbot_courier_no_brigg_living"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_talbot_courier_no_brigg_living_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "talbot_courier_no_brigg_dead"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_talbot_courier_no_brigg_dead_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "flint_courier_no_brigg_living"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_flint_courier_no_brigg_living_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	If node == "flint_courier_no_brigg_dead"
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		int selected = S_flint_courier_no_brigg_dead_1.Show()
		If !SpeechContext(node,speakerActor,role,capturedEpoch,party)
			Return -1
		EndIf
		Return selected
	EndIf
	Return -1
EndFunction

bool Function Bind(Quest actualFirstSection, ObjectReference actualEntry, ObjectReference actualReturn)
	TLM:Act1Walk source = actualFirstSection as TLM:Act1Walk
	If !source || !actualFirstSection.IsRunning() || !source.CanVisitFair() || !actualEntry || !actualReturn || actualEntry == actualReturn
		Return false
	EndIf
	If !IsRunning()
		If !Start() || !IsRunning()
			Return false
		EndIf
	EndIf
	If sourceOwner && sourceOwner != actualFirstSection
		Return false
	EndIf
	If entryPoint && (entryPoint != actualEntry || returnPoint != actualReturn)
		Return false
	EndIf
	If !Road().InitializeIdentities()
		Return false
	EndIf
	sourceOwner = actualFirstSection
	entryPoint = actualEntry
	returnPoint = actualReturn
	If !visitors
		visitors = new Actor[4]
		visitorWasDisabled = new bool[4]
		visitorPending = new bool[4]
		visitorCaptured = new bool[4]
		visitorStaged = new bool[4]
	EndIf
	actualEntry.Enable()
	Return !actualEntry.IsDisabled()
EndFunction

Function Loaded()
	Road().Loaded()
	busy = false
	busyEpoch = -1
EndFunction

bool Function Near(ObjectReference target, float reach = 256.0)
	Actor player = Game.GetPlayer()
	Return player && !player.IsDead() && !player.IsInCombat() && target && !target.IsDisabled() && Road().At(player,target,reach)
EndFunction

bool Function Usable(int role)
	Actor who = Road().Person(role)
	bool eligible = Road().Alive(who) && Road().At(Game.GetPlayer(),who,2048.0) && SourceIdentity(role,who)
	If role >= 0 && role < 4
		eligible = eligible && visitorStaged && visitorStaged[role] && Road().At(who,VisitorAnchor(role),256.0)
	EndIf
	Return eligible
EndFunction

bool Function ActuallyDead(int role)
	Actor who = Road().Person(role)
	Return who && who.IsDead()
EndFunction

bool Function Unavailable(int role)
	; Technical presence qualification of the approved carrier families.
	; This records no death and never changes dead-courier speech eligibility.
	Return !Usable(role)
EndFunction

Actor Function SourceActor(int role)
	TLM:Act1Walk original = sourceOwner as TLM:Act1Walk
	If !original
		Return None
	EndIf
	If role >= 0 && role <= 2
		Return original.FairActor(role)
	ElseIf role == 3
		TLM:GreenwaterWalk river = original.Greenwater()
		If river
			Return river.Alias_Belden.GetActorReference()
		EndIf
	EndIf
	Return None
EndFunction

bool Function SourceIdentity(int role, Actor who)
	If role >= 4
		Return who == Road().Person(role)
	EndIf
	Return who && who == SourceActor(role)
EndFunction

bool Function IsVisiting(Actor who)
	If !who || !visitors
		Return false
	EndIf
	int i = 0
	While i < 4
		If visitors[i] == who && visitorPending[i]
			Return true
		EndIf
		i += 1
	EndWhile
	Return false
EndFunction

Actor Function OriginalVisitor(int role)
	If role >= 0 && role < 4 && visitors && visitorPending[role] && visitorCaptured[role]
		Return visitors[role]
	EndIf
	Return None
EndFunction

ReferenceAlias Function VisitorAlias(int role)
	If role == 0
		Return Alias_Pritchard
	ElseIf role == 1
		Return Alias_Talbot
	ElseIf role == 2
		Return Alias_Pike
	ElseIf role == 3
		Return Alias_Belden
	EndIf
	Return None
EndFunction

ObjectReference Function VisitorAnchor(int role, bool returning = false)
	If role == 0
		If returning
			Return Ref(Alias_PritchardReturn)
		EndIf
		Return Ref(Alias_PritchardAnchor)
	ElseIf role == 1
		If returning
			Return Ref(Alias_TalbotReturn)
		EndIf
		Return Ref(Alias_TalbotAnchor)
	ElseIf role == 2
		If returning
			Return Ref(Alias_PikeReturn)
		EndIf
		Return Ref(Alias_PikeAnchor)
	ElseIf role == 3
		If returning
			Return Ref(Alias_BeldenReturn)
		EndIf
		Return Ref(Alias_BeldenAnchor)
	EndIf
	Return None
EndFunction

Function StageVisitors(int capturedEpoch)
	TLM:Act1Walk original = sourceOwner as TLM:Act1Walk
	If !original || !original.CanVisitFair() || !Road().Current(capturedEpoch)
		Return
	EndIf
	int i = 0
	While i < 4
		Actor who = SourceActor(i)
		ObjectReference anchor = VisitorAnchor(i)
		ObjectReference saved = VisitorAnchor(i,true)
		bool eligible = who && !who.IsDead() && !who.IsInCombat() && !who.IsInDialogueWithPlayer() && !who.IsInScene() && anchor && saved
		If i != 3
			eligible = eligible && !who.IsDisabled() && original.FairActorAvailable(who)
		Else
			TLM:GreenwaterWalk river = original.Greenwater()
			eligible = eligible && river && river.CanVisitFairBelden()
		EndIf
		If visitorPending[i]
			; Only this already captured original is eligible for an idempotent
			; unfinished placement. Its return marker is never overwritten.
			eligible = eligible && visitors[i] == who
		ElseIf eligible
			; Disabled/no-3D references have a known nonreturning MoveTo case.
			; These are our four own markers, never an old actor or item.
			saved.Enable()
			bool markerReady = !saved.IsDisabled() && saved.Is3DLoaded()
			If markerReady && capturedEpoch == Road().Epoch()
				saved.MoveTo(who)
			EndIf
			bool captured = markerReady && Road().At(saved,who,16.0)
			bool disabled = who.IsDisabled()
			If captured && SourceActor(i) == who && Road().Current(capturedEpoch)
				visitors[i] = who
				visitorWasDisabled[i] = disabled
				visitorCaptured[i] = true
				visitorPending[i] = true
			Else
				eligible = false
			EndIf
		EndIf
		If eligible && visitorCaptured[i] && Road().Current(capturedEpoch)
			VisitorAlias(i).ForceRefTo(who)
			If i == 3 && visitorWasDisabled[i]
				who.Enable()
			EndIf
			If SourceActor(i) == who && VisitorAlias(i).GetActorReference() == who && !who.IsDead() && Road().Current(capturedEpoch)
				visitorStaged[i] = false
				who.MoveTo(anchor)
				bool arrived = Road().At(who,anchor,128.0) && !who.IsDead() && !who.IsDisabled()
				If arrived && SourceActor(i) == who && VisitorAlias(i).GetActorReference() == who && Road().Current(capturedEpoch)
					visitorStaged[i] = true
				EndIf
			EndIf
		EndIf
		i += 1
	EndWhile
EndFunction

int Function PendingReturns()
	int result = 0
	int i = 0
	If !visitors
		Return 0
	EndIf
	While i < 4
		If visitorPending[i]
			result += 1
		EndIf
		i += 1
	EndWhile
	Return result
EndFunction

Function ReturnVisitors(int capturedEpoch)
	int i = 0
	While i < 4 && capturedEpoch == Road().Epoch()
		Actor who = visitors[i]
		If visitorPending[i] && visitorCaptured[i] && who
			If who.IsDead()
				; Dead actors are never resurrected or teleported as a return.
				visitorPending[i] = false
				visitorStaged[i] = false
			ElseIf !who.IsInCombat() && !who.IsInDialogueWithPlayer() && !who.IsInScene()
				ObjectReference saved = VisitorAnchor(i,true)
				int attempts = 0
				While attempts < 3 && !Road().At(who,saved,32.0) && capturedEpoch == Road().Epoch()
					who.MoveTo(saved)
					attempts += 1
				EndWhile
				bool back = Road().At(who,saved,32.0)
				If back && capturedEpoch == Road().Epoch()
					If visitorWasDisabled[i]
						who.Disable()
					Else
						who.Enable()
					EndIf
					bool sameState = who.IsDisabled() == visitorWasDisabled[i]
					bool stillBack = Road().At(who,saved,32.0)
					If sameState && stillBack && visitors[i] == who && capturedEpoch == Road().Epoch()
						visitorPending[i] = false
						visitorCaptured[i] = false
						visitorStaged[i] = false
					EndIf
				EndIf
			EndIf
		EndIf
		i += 1
	EndWhile
	If PendingReturns() == 0
		visitActive = false
	EndIf
EndFunction

Actor[] Function CaptureParty()
	Actor[] result = new Actor[9]
	int i = 0
	While i < 9
		result[i] = Road().Person(i)
		i += 1
	EndWhile
	Return result
EndFunction

bool Function SameParty(Actor[] party)
	If !party || party.Length != 9
		Return false
	EndIf
	int i = 0
	While i < 9
		If party[i] != Road().Person(i)
			Return false
		EndIf
		i += 1
	EndWhile
	Return true
EndFunction

bool Function SpeechContext(string node, Actor speakerActor, int role, int capturedEpoch, Actor[] party)
	bool eligible = NodeCondition(node) && SourceIdentity(role,speakerActor) && Road().Speaker(speakerActor,role,capturedEpoch) && SameParty(party)
	Return eligible && capturedEpoch == Road().Epoch()
EndFunction

bool Function DocumentContext(string documentId, ObjectReference original, int capturedEpoch)
	bool eligible = false
	If documentId == "fair_handbill"
		eligible = Road().FirstComplete() && Near(entryPoint)
	ElseIf documentId == "courier_card"
		eligible = Road().GetStageDone(40) && Road().CaseAccess(original)
	ElseIf documentId == "silver_case"
		eligible = Road().GetStageDone(40) && original && original == Ref(Alias_OriginalSilver) && Near(original) && !original.GetContainer()
	EndIf
	Return eligible && capturedEpoch == Road().Epoch()
EndFunction

bool Function EntryCurrent(int capturedEpoch)
	bool eligible = sourceOwner && sourceOwner.IsRunning() && Near(entryPoint)
	Return eligible && capturedEpoch == Road().Epoch()
EndFunction

bool Function LocalCurrent(ObjectReference control, int capturedEpoch)
	bool eligible = Near(control) && Road().Local()
	Return eligible && capturedEpoch == Road().Epoch()
EndFunction

Function ClockGap()
	TLM:Act1Walk original = sourceOwner as TLM:Act1Walk
	If original && original.TLM_RedHollow
		(original.TLM_RedHollow as TLM:RedHollowWalk).FairTransitGap()
	EndIf
EndFunction

Function EnableStations()
	Ref(Alias_Exit).Enable()
	Ref(Alias_Ready).Enable()
	Ref(Alias_Response).Enable()
	Ref(Alias_CaseControl).Enable()
	Ref(Alias_Firing).Enable()
	Ref(Alias_Landing).Enable()
	Ref(Alias_Competition).Enable()
	Ref(Alias_Status).Enable()
	Ref(Alias_Whitcomb).Enable()
	Ref(Alias_Brigg).Enable()
	Ref(Alias_Grey).Enable()
	Ref(Alias_Flint).Enable()
EndFunction

Function EntryMenu(int capturedEpoch)
	ReturnVisitors(capturedEpoch)
	If !EntryCurrent(capturedEpoch)
		Return
	EndIf
	If PendingReturns() > 0
		ReturnsPending.Show()
		If !EntryCurrent(capturedEpoch)
			Return
		EndIf
	EndIf
	bool firstFinished = Road().FirstComplete()
	If !EntryCurrent(capturedEpoch)
		Return
	EndIf
	If !firstFinished
		Unavailable.Show()
		Return
	EndIf
	If Road().EntryKind() == 0
		int selected = Entry.Show()
		If !EntryCurrent(capturedEpoch)
			Return
		EndIf
		If selected == 0
			If !Road().AnyRoadComplete()
				If EntryCurrent(capturedEpoch)
					Unavailable.Show()
				EndIf
				Return
			EndIf
			If Road().AnyReportedComplete()
				Road().Qualify(1,capturedEpoch)
			ElseIf EntryCurrent(capturedEpoch) && NoReport.Show() == 0 && EntryCurrent(capturedEpoch)
				Road().Qualify(2,capturedEpoch)
			EndIf
		ElseIf selected == 1
			If NoReport.Show() == 0 && EntryCurrent(capturedEpoch)
				Road().Qualify(3,capturedEpoch)
			EndIf
		ElseIf selected == 2
			If Paper("fair_handbill",entryPoint,capturedEpoch)
				Road().Qualify(4,capturedEpoch)
			EndIf
		Else
			Return
		EndIf
	EndIf
	If Road().EntryKind() == 0 || !EntryCurrent(capturedEpoch)
		Return
	EndIf
	int travelAnswer = Travel.Show()
	TLM:Act1Walk original = sourceOwner as TLM:Act1Walk
	Actor player = Game.GetPlayer()
	If travelAnswer != 0 || !player || !original || !original.CanVisitFair() || !EntryCurrent(capturedEpoch) || !Road().TravelCurrent(capturedEpoch)
		Return
	EndIf
	ClockGap()
	ObjectReference arrival = Ref(Alias_Arrival)
	If !arrival || !Road().TravelCurrent(capturedEpoch)
		Return
	EndIf
	player.MoveTo(arrival)
	ClockGap()
	If !Road().RecordFairArrival(capturedEpoch)
		Return
	EndIf
	EnableStations()
	visitActive = true
	StageVisitors(capturedEpoch)
	If !Road().Current(capturedEpoch)
		Return
	EndIf
	If !layoutRead
		If Layout.Show() != 0 || !Road().Current(capturedEpoch)
			Return
		EndIf
		If LayoutLimits.Show() != 0 || !Road().Current(capturedEpoch)
			Return
		EndIf
		layoutRead = Road().RecordOpportunities(capturedEpoch)
	EndIf
EndFunction

Function ExitFair(int capturedEpoch)
	Actor player = Game.GetPlayer()
	If !LocalCurrent(Ref(Alias_Exit),capturedEpoch) || Exit.Show() != 0 || !LocalCurrent(Ref(Alias_Exit),capturedEpoch)
		Return
	EndIf
	ClockGap()
	ReturnVisitors(capturedEpoch)
	; Returning an absent/busy original may fail, but player exit never depends
	; on those optional returns. No stranded original is reported as restored.
	bool returnReady = returnPoint && player && player == Game.GetPlayer() && Road().Local()
	If !returnReady || capturedEpoch != Road().Epoch()
		Return
	EndIf
	player.MoveTo(returnPoint)
	ClockGap()
	bool arrived = Road().At(Game.GetPlayer(),returnPoint,256.0)
	If arrived && capturedEpoch == Road().Epoch() && PendingReturns() > 0
		ReturnsPending.Show()
	EndIf
EndFunction

Function CourierScene(int capturedEpoch)
	If Road().GetStageDone(40)
		PresentCourses(capturedEpoch)
		Return
	EndIf
	If !Road().Current(capturedEpoch)
		Return
	EndIf
	If !layoutRead
		If Layout.Show() != 0 || !Road().Current(capturedEpoch)
			Return
		EndIf
		If LayoutLimits.Show() != 0 || !Road().Current(capturedEpoch)
			Return
		EndIf
		layoutRead = Road().RecordOpportunities(capturedEpoch)
	EndIf
	Actor courier = Road().Person(8)
	ObjectReference original = Ref(Alias_OriginalCase)
	Actor player = Game.GetPlayer()
	If !courier || !original || !LocalCurrent(Ref(Alias_Ready),capturedEpoch)
		Return
	EndIf
	If Ready.Show() != 0 || !LocalCurrent(Ref(Alias_Ready),capturedEpoch)
		Return
	EndIf
	; Before enabling, disabled original Juno still occupies her own placed
	; station. Neither a replacement nor a dead actor is made to run or die.
	If !Road().BeginEncounter(courier,original,player,capturedEpoch)
		Return
	EndIf
	courier.Enable()
	If !Road().BeginEncounter(courier,original,player,capturedEpoch)
		Return
	EndIf
	; Finish yielding eligibility reads before sampling the effect boundary.
	; An already-enabled paused original needs no Enable, held or otherwise.
	bool needsEnable = original.IsDisabled()
	ObjectReference holder = original.GetContainer()
	If capturedEpoch != Road().Epoch()
		Return
	EndIf
	If needsEnable && !holder
		original.Enable()
	EndIf
	bool foundDead = courier.IsDead()
	If !Road().EncounterContext(courier,original,player,holder,foundDead,capturedEpoch)
		Return
	EndIf
	int witnessed = -1
	If foundDead
		witnessed = DeadCourier.Show()
	Else
		witnessed = Shot.Show()
	EndIf
	If witnessed == 0 && Road().FinishEncounter(courier,original,player,holder,foundDead,capturedEpoch)
		PresentCourses(capturedEpoch)
	EndIf
EndFunction

string Function NextOffer(string node, int selected)
	If node == "whitcomb_offer"
		If selected == 0
			Return "whitcomb_rates"
		ElseIf selected == 1
			Return "whitcomb_big"
		EndIf
	ElseIf node == "brigg_offer"
		If selected == 0
			Return "brigg_price"
		ElseIf selected == 1
			Return "brigg_quill"
		ElseIf selected == 2
			Return "brigg_dissent"
		EndIf
	ElseIf node == "belden_offer"
		If selected == 0
			Return "belden_list"
		ElseIf selected == 1
			Return "belden_leave"
		ElseIf selected == 2
			Return "belden_dissent"
		EndIf
	ElseIf node == "grey_offer"
		If selected == 0
			Return "grey_cost"
		ElseIf selected == 1
			Return "grey_train"
		ElseIf selected == 2
			Return "grey_dissent"
		EndIf
	ElseIf node == "flint_roof"
		If selected == 0
			Return "flint_who"
		ElseIf selected == 1
			Return "flint_hat"
		EndIf
	EndIf
	Return ""
EndFunction

Function TalkRole(int role, int capturedEpoch)
	If !Usable(role)
		Return
	EndIf
	If role == 2
		PikeEvidence(capturedEpoch)
		Return
	EndIf
	If Road().ChoicesOpen() && (role == 5 || role == 0 || role == 1 || role == 7)
		PresentCourses(capturedEpoch)
		Return
	EndIf
	If role == 0 && Road().GetStageDone(60) && !Road().GetStageDone(100)
		ReadCase(true,capturedEpoch)
		Return
	EndIf
	Actor[] party = CaptureParty()
	Actor who = party[role]
	string node = SelectedEntry(role)
	If node == "" || node == "pritchard_case"
		Return
	EndIf
	If node == "flint_roof" && !Road().FlintBefore()
		FiringPosition(capturedEpoch)
		Return
	EndIf
	int selected = SayNode(node,who,role,capturedEpoch,party)
	If selected < 0 || !SpeechContext(node,who,role,capturedEpoch,party)
		Return
	EndIf
	If node == "pritchard_fair" && selected == 0
		SetStage(11)
	ElseIf node == "threefords_dying" && selected == 0
		Road().RecordCourierWords(who,capturedEpoch)
	EndIf
	string nextNode = NextOffer(node,selected)
	If nextNode != ""
		SayNode(nextNode,who,role,capturedEpoch,party)
	EndIf
EndFunction

int Function SourceCourse(string node, int selected)
	If node == "brigg_demand"
		If selected == 0
			Return 41
		EndIf
		If selected == 1
			Return 42
		EndIf
		If selected == 2
			Return 43
		EndIf
		If selected == 3
			Return 44
		EndIf
	EndIf
	If node == "brigg_demand_courier_dead"
		If selected == 0
			Return 41
		EndIf
		If selected == 1
			Return 43
		EndIf
		If selected == 2
			Return 44
		EndIf
	EndIf
	If node == "brigg_demand_talbot"
		If selected == 0
			Return 41
		EndIf
		If selected == 1
			Return 42
		EndIf
		If selected == 2
			Return 43
		EndIf
		If selected == 3
			Return 44
		EndIf
	EndIf
	If node == "brigg_demand_talbot_courier_dead"
		If selected == 0
			Return 41
		EndIf
		If selected == 1
			Return 43
		EndIf
		If selected == 2
			Return 44
		EndIf
	EndIf
	If node == "brigg_demand_no_whitcomb"
		If selected == 0
			Return 41
		EndIf
		If selected == 1
			Return 42
		EndIf
		If selected == 2
			Return 44
		EndIf
	EndIf
	If node == "brigg_demand_no_whitcomb_courier_dead"
		If selected == 0
			Return 41
		EndIf
		If selected == 1
			Return 44
		EndIf
	EndIf
	If node == "brigg_demand_no_belden"
		If selected == 0
			Return 41
		EndIf
		If selected == 1
			Return 42
		EndIf
		If selected == 2
			Return 44
		EndIf
	EndIf
	If node == "brigg_demand_no_belden_courier_dead"
		If selected == 0
			Return 41
		EndIf
		If selected == 1
			Return 44
		EndIf
	EndIf
	If node == "brigg_demand_no_grey"
		If selected == 0
			Return 41
		EndIf
		If selected == 1
			Return 42
		EndIf
		If selected == 2
			Return 44
		EndIf
	EndIf
	If node == "brigg_demand_no_grey_courier_dead"
		If selected == 0
			Return 41
		EndIf
		If selected == 1
			Return 44
		EndIf
	EndIf
	If node == "brigg_demand_no_officer"
		If selected == 0
			Return 41
		EndIf
		If selected == 1
			Return 42
		EndIf
		If selected == 2
			Return 44
		EndIf
	EndIf
	If node == "brigg_demand_no_officer_courier_dead"
		If selected == 0
			Return 41
		EndIf
		If selected == 1
			Return 44
		EndIf
	EndIf
	If node == "pritchard_courier_no_brigg_living"
		If selected == 0
			Return 41
		EndIf
		If selected == 1
			Return 42
		EndIf
		If selected == 2
			Return 44
		EndIf
	EndIf
	If node == "pritchard_courier_no_brigg_dead"
		If selected == 0
			Return 41
		EndIf
		If selected == 1
			Return 44
		EndIf
	EndIf
	If node == "talbot_courier_no_brigg_living"
		If selected == 0
			Return 41
		EndIf
		If selected == 1
			Return 42
		EndIf
		If selected == 2
			Return 44
		EndIf
	EndIf
	If node == "talbot_courier_no_brigg_dead"
		If selected == 0
			Return 41
		EndIf
		If selected == 1
			Return 44
		EndIf
	EndIf
	If node == "flint_courier_no_brigg_living"
		If selected == 0
			Return 41
		EndIf
		If selected == 1
			Return 42
		EndIf
		If selected == 2
			Return 44
		EndIf
	EndIf
	If node == "flint_courier_no_brigg_dead"
		If selected == 0
			Return 41
		EndIf
		If selected == 1
			Return 44
		EndIf
	EndIf
	Return 0
EndFunction

Function PresentCourses(int capturedEpoch)
	If !Road().GetStageDone(40) || Road().GetStageDone(100) || !Road().Current(capturedEpoch)
		Return
	EndIf
	If Road().PendingEffect() != 0
		Blocked.Show()
		Return
	EndIf
	If Road().PendingResponse() != 0
		int retry = -1
		bool occupied = Road().GetStageDone(70)
		If !Road().Current(capturedEpoch)
			Return
		EndIf
		If occupied
			retry = PendingCourse.Show()
		Else
			retry = PendingOrder.Show()
		EndIf
		If !Road().Current(capturedEpoch)
			Return
		EndIf
		If retry == 0
			ContinueSelected(Road().OrderActor(),CaptureParty(),Ref(Alias_OriginalCase),Ref(Alias_OccupationBoard),capturedEpoch)
		ElseIf retry == 1
			If Road().GetStageDone(70)
				ReadCase(false,capturedEpoch)
			Else
				Road().DropUncommittedCourse(capturedEpoch)
			EndIf
		EndIf
		Return
	EndIf
	If !Road().ChoicesOpen()
		Return
	EndIf
	int carrier = -1
	If Usable(5)
		carrier = 5
	ElseIf Usable(0)
		carrier = 0
	ElseIf Usable(1)
		carrier = 1
	ElseIf Usable(7)
		carrier = 7
	EndIf
	If carrier < 0
		If Road().Current(capturedEpoch)
			NoCarrier.Show()
		EndIf
		Return
	EndIf
	Actor[] party = CaptureParty()
	Actor issuer = party[carrier]
	ObjectReference original = Ref(Alias_OriginalCase)
	ObjectReference board = Ref(Alias_OccupationBoard)
	string node = SelectedEntry(carrier)
	If node == ""
		If Road().Current(capturedEpoch)
			Failed.Show()
		EndIf
		Return
	EndIf
	If node == "pritchard_case"
		ReadCase(true,capturedEpoch)
		Return
	EndIf
	int selected = SayNode(node,issuer,carrier,capturedEpoch,party)
	If selected < 0 || !SpeechContext(node,issuer,carrier,capturedEpoch,party) || original != Ref(Alias_OriginalCase) || board != Ref(Alias_OccupationBoard) || !Road().Current(capturedEpoch)
		Return
	EndIf
	int course = SourceCourse(node,selected)
	If course == 0
		Return
	EndIf
	If carrier == 5 && !Road().AcknowledgeOrder(issuer,capturedEpoch)
		Return
	EndIf
	If course == 43
		int officer = 0
		If !Usable(0)
			officer = 1
		EndIf
		Truce(party,officer,capturedEpoch)
	ElseIf Road().PlanCourse(course,issuer,carrier,capturedEpoch)
		If carrier == 5
			ContinueSelected(issuer,party,original,board,capturedEpoch)
		Else
			FinishSelected(original,capturedEpoch)
		EndIf
	EndIf
EndFunction

Function ContinueSelected(Actor issuer, Actor[] party, ObjectReference original, ObjectReference board, int capturedEpoch)
	If !Road().GetStageDone(70)
		If !issuer || !Road().Speaker(issuer,5,capturedEpoch) || !SameParty(party) || original != Ref(Alias_OriginalCase) || board != Ref(Alias_OccupationBoard) || !Road().Current(capturedEpoch)
			Return
		EndIf
		int proceed = Occupation.Show()
		If proceed != 0
			Road().DropUncommittedCourse(capturedEpoch)
			Return
		EndIf
		If !Road().Speaker(issuer,5,capturedEpoch) || !SameParty(party) || original != Ref(Alias_OriginalCase) || board != Ref(Alias_OccupationBoard) || !Road().Current(capturedEpoch)
			Return
		EndIf
		board.Enable()
		bool visible = !board.IsDisabled() && Near(board,2048.0)
		If !visible || !Road().Speaker(issuer,5,capturedEpoch) || !SameParty(party) || board != Ref(Alias_OccupationBoard) || !Road().Current(capturedEpoch)
			Return
		EndIf
		If OccupationSeen.Show() != 0 || !SameParty(party) || !Road().RecordOccupation(issuer,board,capturedEpoch)
			Return
		EndIf
	EndIf
	If original == Ref(Alias_OriginalCase) && Road().Current(capturedEpoch)
		FinishSelected(original,capturedEpoch)
	EndIf
EndFunction

Function FinishSelected(ObjectReference original, int capturedEpoch)
	int course = Road().PendingResponse()
	If course == 41 || course == 42
		If Road().CommitPlanned(capturedEpoch) && course == 42
			TalkRole(8,capturedEpoch)
		EndIf
	ElseIf course == 44
		TakeCase(original,capturedEpoch)
	EndIf
EndFunction

Function Truce(Actor[] party, int officer, int capturedEpoch)
	If !Road().Quorum(party,officer,capturedEpoch)
		Return
	EndIf
	string suffix = ""
	If officer == 1
		suffix = "_talbot"
	EndIf
	If SayNode("whitcomb_truce" + suffix,party[4],4,capturedEpoch,party) != 0 || !Road().Quorum(party,officer,capturedEpoch)
		Return
	EndIf
	If SayNode("belden_truce" + suffix,party[3],3,capturedEpoch,party) != 0 || !Road().Quorum(party,officer,capturedEpoch)
		Return
	EndIf
	If SayNode("grey_truce" + suffix,party[6],6,capturedEpoch,party) != 0 || !Road().Quorum(party,officer,capturedEpoch)
		Return
	EndIf
	string officerNode = "pritchard_truce"
	string concession = "brigg_truce_concession_pritchard"
	If officer == 1
		officerNode = "talbot_truce"
		concession = "brigg_truce_concession_talbot"
	EndIf
	If SayNode(officerNode,party[officer],officer,capturedEpoch,party) != 0 || !Road().Quorum(party,officer,capturedEpoch)
		Return
	EndIf
	If SayNode(concession,party[5],5,capturedEpoch,party) == 0 && Road().Concede(party,officer,capturedEpoch)
		SayNode("brigg_rifles",party[5],5,capturedEpoch,party)
	EndIf
EndFunction

Function TakeCase(ObjectReference original, int capturedEpoch)
	If Road().PendingEffect() != 0
		If Road().Current(capturedEpoch)
			Blocked.Show()
		EndIf
		Return
	EndIf
	If !Road().CaseAccess(original) || !Road().Current(capturedEpoch)
		Return
	EndIf
	If Take.Show() != 0 || !Road().CaseAccess(original) || original != Ref(Alias_OriginalCase) || !Road().Current(capturedEpoch)
		Return
	EndIf
	If Road().Held()
		Road().AcknowledgeHeldTake(original,capturedEpoch)
	Else
		Road().TransferOriginal(1,original,Game.GetPlayer(),capturedEpoch)
	EndIf
EndFunction

Function ReadCase(bool publicReading, int capturedEpoch)
	ObjectReference original = Ref(Alias_OriginalCase)
	Actor[] party = CaptureParty()
	Actor sheriff = party[0]
	If publicReading
		If !Road().Speaker(sheriff,0,capturedEpoch) || !Road().CaseAccess(original) || !Road().Current(capturedEpoch)
			Return
		EndIf
		If original.GetContainer() != sheriff
			If Road().PendingEffect() != 0 || !Road().Current(capturedEpoch)
				Return
			EndIf
			If Public.Show() != 0 || !SameParty(party) || !Road().Speaker(sheriff,0,capturedEpoch) || !Road().Current(capturedEpoch)
				Return
			EndIf
			If !Road().TransferOriginal(2,original,sheriff,capturedEpoch)
				Return
			EndIf
		EndIf
	EndIf
	If !Paper("courier_card",original,capturedEpoch) || !Road().RecordCaseRead(original,capturedEpoch)
		Return
	EndIf
	If Road().GetStageDone(100)
		Return
	EndIf
	If !Road().Current(capturedEpoch)
		Return
	EndIf
	If publicReading
		int reply = SayNode("pritchard_case",sheriff,0,capturedEpoch,party)
		If reply >= 0 && reply <= 1 && original == Ref(Alias_OriginalCase) && SameParty(party) && Road().Current(capturedEpoch)
			Road().FinishRead(original,sheriff,capturedEpoch)
		EndIf
	ElseIf Solo.Show() == 0 && original == Ref(Alias_OriginalCase) && Road().Current(capturedEpoch)
		Road().FinishRead(original,None,capturedEpoch)
	EndIf
EndFunction

Function CaseMenu(int capturedEpoch)
	ObjectReference original = Ref(Alias_OriginalCase)
	If !Road().CaseAccess(original) || !Road().Current(capturedEpoch)
		If Road().Current(capturedEpoch)
			Failed.Show()
		EndIf
		Return
	EndIf
	int selected = Case.Show()
	If original != Ref(Alias_OriginalCase) || !Road().CaseAccess(original) || !Road().Current(capturedEpoch)
		Return
	EndIf
	If selected == 0
		ReadCase(false,capturedEpoch)
	ElseIf selected == 1
		TakeCase(original,capturedEpoch)
	ElseIf selected == 2
		ReadCase(true,capturedEpoch)
	EndIf
EndFunction

Function FiringPosition(int capturedEpoch)
	ObjectReference original = Ref(Alias_OriginalSilver)
	Actor[] party = CaptureParty()
	Actor flint = party[7]
	If !Road().GetStageDone(40) || !LocalCurrent(Ref(Alias_Firing),capturedEpoch)
		Return
	EndIf
	If !Road().SilverBefore()
		If original
			original.Enable()
		EndIf
		If original != Ref(Alias_OriginalSilver) || !LocalCurrent(Ref(Alias_Firing),capturedEpoch)
			Return
		EndIf
		If Silver.Show() != 0 || !LocalCurrent(Ref(Alias_Firing),capturedEpoch) || !Paper("silver_case",original,capturedEpoch) || !Road().InspectSilver(original,capturedEpoch)
			Return
		EndIf
	EndIf
	If !Road().FlintBefore() && Road().PendingEffect() == 0 && Road().Speaker(flint,7,capturedEpoch)
		If GiveSilver.Show() != 0 || !SameParty(party) || original != Ref(Alias_OriginalSilver) || !Road().Speaker(flint,7,capturedEpoch) || !Road().Current(capturedEpoch)
			Return
		EndIf
		If !Road().TransferOriginal(3,original,flint,capturedEpoch)
			Return
		EndIf
	EndIf
	If Road().FlintBefore() && SameParty(party) && Road().Current(capturedEpoch)
		int reply = SayNode("flint_roof",flint,7,capturedEpoch,party)
		string nextNode = NextOffer("flint_roof",reply)
		If nextNode != ""
			SayNode(nextNode,flint,7,capturedEpoch,party)
		EndIf
	EndIf
EndFunction

int Function Number(bool value)
	If value
		Return 1
	EndIf
	Return 0
EndFunction

Function Facts(int capturedEpoch)
	int basis = Road().EntryKind()
	int encounter = Number(Road().GetStageDone(40))
	int course = Road().ResponseKind()
	int occupation = Number(Road().GetStageDone(70))
	int read = Number(Road().ReadBefore())
	If !Road().Current(capturedEpoch)
		Return
	EndIf
	If Status.Show(basis,encounter,course,occupation,read) != 0 || !Road().Current(capturedEpoch)
		Return
	EndIf
	Actor publicHolder = Road().PublicHolder()
	bool publicPresent = Road().Alive(publicHolder) && Road().At(Game.GetPlayer(),publicHolder,2048.0)
	bool held = Road().Held()
	int pending = Road().PendingEffect()
	int returns = PendingReturns()
	If Road().Current(capturedEpoch)
		Custody.Show(Number(held),Number(publicPresent),pending,returns)
	EndIf
EndFunction

Function Used(int who)
	; Atomic page owner before the first native read. A resumed old frame
	; cannot clear the claim made by a later activation after Loaded.
	If busy
		Return
	EndIf
	busy = true
	int capturedEpoch = Road().Epoch()
	busyEpoch = capturedEpoch
	If who == 1 && EntryCurrent(capturedEpoch)
		EntryMenu(capturedEpoch)
	ElseIf Road().Current(capturedEpoch)
		If who == 2
			ExitFair(capturedEpoch)
		ElseIf who == 3 && LocalCurrent(Ref(Alias_Ready),capturedEpoch)
			CourierScene(capturedEpoch)
		ElseIf who == 4 && LocalCurrent(Ref(Alias_Response),capturedEpoch)
			PresentCourses(capturedEpoch)
		ElseIf who == 5 && LocalCurrent(Ref(Alias_CaseControl),capturedEpoch)
			CaseMenu(capturedEpoch)
		ElseIf who == 6
			FiringPosition(capturedEpoch)
		ElseIf who == 7 && LocalCurrent(Ref(Alias_Landing),capturedEpoch)
			ObjectReference landingRef = Ref(Alias_Landing)
			If Landing.Show() == 0 && LocalCurrent(landingRef,capturedEpoch)
				Road().InspectLanding(landingRef,capturedEpoch)
			EndIf
		ElseIf who == 8 && LocalCurrent(Ref(Alias_Competition),capturedEpoch)
			Competition.Show()
		ElseIf who == 9 && LocalCurrent(Ref(Alias_Status),capturedEpoch)
			Facts(capturedEpoch)
		ElseIf who == 10 && LocalCurrent(Ref(Alias_OccupationBoard),capturedEpoch)
			If Road().GetStageDone(70)
				TalkRole(5,capturedEpoch)
			Else
				PresentCourses(capturedEpoch)
			EndIf
		ElseIf who >= 20 && who <= 28
			TalkRole(who - 20,capturedEpoch)
		EndIf
	EndIf
	If capturedEpoch == Road().Epoch() && busyEpoch == capturedEpoch
		busy = false
		busyEpoch = -1
	EndIf
EndFunction

bool Function PikeEvidenceContext(Actor pike, ObjectReference original, int capturedEpoch)
	bool eligible = Road().SilverBefore() && original && original == Road().SilverObject() && original == Ref(Alias_OriginalSilver) && original.GetContainer() == Game.GetPlayer() && SourceIdentity(2,pike) && Road().Speaker(pike,2,capturedEpoch) && Near(pike)
	Return eligible && capturedEpoch == Road().Epoch()
EndFunction

Function PikeEvidence(int capturedEpoch)
	Actor pike = Road().Person(2)
	ObjectReference original = Road().SilverObject()
	If !PikeEvidenceContext(pike,original,capturedEpoch)
		If Road().Speaker(pike,2,capturedEpoch)
			PikeUnavailable.Show()
		EndIf
		Return
	EndIf
	If PikeCompare.Show() != 0 || !PikeEvidenceContext(pike,original,capturedEpoch)
		Return
	EndIf
	; Explicit evidence-aside channel only, never a greeting/priority candidate.
	; The accepted aside remains circumstantial and performs no quest effect.
	A_pike_mould_aside.Show()
EndFunction

bool Function Paper(string documentId, ObjectReference original, int capturedEpoch)
	If documentId == "fair_handbill"
		If !DocumentContext(documentId,original,capturedEpoch) || D_fair_handbill_1.Show() != 0 || !DocumentContext(documentId,original,capturedEpoch)
			Return false
		EndIf
		If !DocumentContext(documentId,original,capturedEpoch) || D_fair_handbill_2.Show() != 0 || !DocumentContext(documentId,original,capturedEpoch)
			Return false
		EndIf
		If !DocumentContext(documentId,original,capturedEpoch) || D_fair_handbill_3.Show() != 0 || !DocumentContext(documentId,original,capturedEpoch)
			Return false
		EndIf
		Return true
	EndIf
	If documentId == "silver_case"
		If !DocumentContext(documentId,original,capturedEpoch) || D_silver_case_1.Show() != 0 || !DocumentContext(documentId,original,capturedEpoch)
			Return false
		EndIf
		If !DocumentContext(documentId,original,capturedEpoch) || D_silver_case_2.Show() != 0 || !DocumentContext(documentId,original,capturedEpoch)
			Return false
		EndIf
		Return true
	EndIf
	If documentId == "courier_card"
		If !DocumentContext(documentId,original,capturedEpoch) || D_courier_card_1.Show() != 0 || !DocumentContext(documentId,original,capturedEpoch)
			Return false
		EndIf
		If !DocumentContext(documentId,original,capturedEpoch) || D_courier_card_2.Show() != 0 || !DocumentContext(documentId,original,capturedEpoch)
			Return false
		EndIf
		If !DocumentContext(documentId,original,capturedEpoch) || D_courier_card_3.Show() != 0 || !DocumentContext(documentId,original,capturedEpoch)
			Return false
		EndIf
		Return true
	EndIf
	Return false
EndFunction
