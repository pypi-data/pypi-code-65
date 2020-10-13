import os
import matplotlib.pyplot as plt


class Process():
    
    def __init__(self,path):
        
        self.path=path
        
    def ptv(self):
        
        os.system("python tractrac.py -f %s -p 2 -o 2" % self.path)
        