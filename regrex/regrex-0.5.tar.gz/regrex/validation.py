def ScoreValidation(certainval, uncertainval):
    return abs(certainval - uncertainval) 

def CertainValidation(certainval, uncertainval):
    if certainval == uncertainval:
        return True
    else:
        return False    