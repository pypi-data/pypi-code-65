import sys

def Difference(mse):
    return float(mse)

def ScoreValidation(modelscore):
    if modelscore > 0.9:
        print("\n\n")
        print("[ERROR] No Logic between Predictor(y) and Response(x)")
        sys.exit()
    else:
        pass    
    