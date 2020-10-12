import sys

def Difference(certainval, uncertainval):
    if certainval > uncertainval:
        return certainval - uncertainval
    else:
        return uncertainval - certainval    
def ScoreValidation(modelscore):
    if modelscore > 0.100:
        print("\n\n")
        print("[ERROR] No Logic between Predictor(y) and Response(x)")
        sys.exit()
    else:
        pass    
    