from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/BlackLedger'))
import test_black_ledger as historical
original=historical.Chapter.answers
def answers(self,**values):
 original(self,**values)
 self.s.answers['TLM_MSG_BS_MQ04Ready']=[0]*10
historical.Chapter.answers=answers
if __name__=='__main__':unittest.main(module=historical,verbosity=2)
