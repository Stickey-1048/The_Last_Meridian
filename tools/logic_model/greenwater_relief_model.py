"""Owner-approved finite relief accounting, independent of inventory effects.
This oracle does not claim any native transfer, calendar or population model.
"""
from dataclasses import dataclass


@dataclass
class ReliefLedger:
    starting: int
    donated: int=0
    step: int=0
    bought: int=0
    hunger: bool=False

    @property
    def balance(self):return self.starting+self.donated-150*self.step
    @property
    def reserve(self):return max(0,self.balance)
    @property
    def debt(self):return max(0,-self.balance)
    @property
    def remaining(self):return 150*(6-self.step)
    @property
    def covered(self):return self.balance>=self.remaining
    @property
    def complete(self):return self.step==6 and self.debt==0

    def donate(self,count):
        if self.complete or count not in (1,5,10) or self.donated+10*count>100000:return False
        self.donated+=10*count
        return True
    def purchase(self):
        if self.bought+10>30:return False
        self.bought+=10
        return True
    def advance(self):
        if self.step==6:return False
        self.step+=1
        self.hunger|=self.debt>0
        if self.step<6:self.bought=0
        return True
