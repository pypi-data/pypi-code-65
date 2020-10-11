import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

df=pd.read_csv("Spam.csv")

def plot(a,b):
  aa=df.iloc[:,a]
  bb=df.iloc[:,b]
  plt.plot(aa,bb,label="PLOT4")
  plt.title("plot")
  plt.show()

# a=int(input())
# b=int(input())
# plot(a,b)
