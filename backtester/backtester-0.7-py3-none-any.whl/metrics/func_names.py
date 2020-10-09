function_names = []
with open("metrics.py", "r") as f:
    for line in f.read().split("\n"):
        if "def" in line:
            print(line.split("def")[1].split("(")[0])
                                            
