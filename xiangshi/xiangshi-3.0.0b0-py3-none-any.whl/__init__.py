from .main import calculator
from .weight import calculator as extra

calculator = calculator()

FileDir = calculator.FileDir
GetTF = calculator.GetTF
GetIDF = calculator.GetIDF
GetTFIDF = calculator.GetTFIDF
HashAlg = calculator.HashAlg
HashNums = calculator.HashNums
HashString = calculator.HashString
InputTarget = calculator.InputTarget
SegDepart = calculator.SegDepart
SortDict = calculator.SortDict
UseLog = calculator.UseLog
dict2file = calculator.dict2file
input2list = calculator.input2list
feature = calculator.feature
weight = calculator.weight
prime = calculator.prime
cossim = calculator.cossim
minhash = calculator.minhash
simhash = calculator.simhash


noweight = extra()
noweight.weight = None

tfweight = extra()
noweight.weight = "TF"

__all__ = [
    'noweight',
    'tfweight'
]
