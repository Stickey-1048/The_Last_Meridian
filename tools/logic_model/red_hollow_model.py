"""Observation oracle for Red Hollow's independent court and mine resolutions.
No movement, NPC speech, timers or input delivery is simulated here. The PSC
controller's observed facts are checked against these outcome preconditions.
"""
from dataclasses import dataclass

COURTS={0:'unsettled',1:'bypass',11:'rope release',12:'fine release',13:'review custody',14:'observed execution'}
MINES={0:'unsettled',51:'personal line plus eleven safe',52:'eleven safe then break closed',53:'informed order sealed',56:'warned expiry sealed',57:'explicit unpledged rescue resolution',58:'observed casualties resolved'}

@dataclass(frozen=True)
class Observed:
    court:int
    mine:int
    safe:int
    deaths:int
    entombed:int
    eleven_ever_safe:bool
    pact:bool
    break_closed:bool
    mouth_closed:bool
    ordered:bool
    pending:int
    known_fates:bool
    receipt:bool
    fee_paid:bool
    condemned_dead:bool

    def problems(self):
        out=[]
        def need(condition,reason):
            if not condition:out.append(reason)
        need(self.court in COURTS,'unknown court outcome')
        need(self.mine in MINES,'unknown mine outcome')
        need(0<=self.safe<=11 and 0<=self.deaths<=11 and 0<=self.entombed<=11,'invalid cohort count')
        need(self.safe+self.deaths+self.entombed<=11,'fates overlap')
        if self.court==12:need(self.fee_paid and self.receipt,'fine release without payment and receipt')
        if self.court==14:need(self.condemned_dead,'execution without observed actual death')
        if self.mine in (51,52,57):need(self.eleven_ever_safe,'full rescue resolution without eleven safe arrivals')
        if self.mine==51:need(self.pact and not self.break_closed,'line outcome without undertaking or with blasted break')
        if self.mine==52:need(self.break_closed,'blast choice without physical collapse')
        if self.mine==57:need(not self.pact and not self.break_closed,'57 overwrites another resolution')
        if self.mine in (53,56):
            need(self.mouth_closed,'sealing without physical closed entrance')
            need(self.ordered==(self.mine==53),'deadline wrongly attributed as player order')
        if self.mine==58:need(self.deaths>0 and self.known_fates and not self.eleven_ever_safe,'58 without individually observed casualties and every survivor safe')
        if self.mine:need(self.pending==0,'terminal outcome interleaved with unfinished scene')
        return out
