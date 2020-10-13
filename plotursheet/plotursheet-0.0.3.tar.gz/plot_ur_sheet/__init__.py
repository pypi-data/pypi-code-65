#import stuffs
from gsheets import Sheets
import pandas as pd
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image 

sheets = Sheets.from_files('client_secrets.json', 'storage.json')
sheets  #doctest: +ELLIPSIS


#specify sheet via url
url = 'https://docs.google.com/spreadsheets/d/1SrZfvr2ee54r7HR1jGtAE9zHIj_Y-UzK9ok8bdwkpqc/edit?usp=sharing'
s = sheets.get(url)
#load into csv
s.sheets[0].to_csv('detail.csv', encoding='utf-8', dialect='excel')


df = pd.read_csv('detail.csv')
#print("Enter the column for x-axis")
#x = input()
#print("Enter the column for y-axis")
#y = input()
fig = plt.figure()
x = sys.argv[1]
y = sys.argv[2]
#plot using the columns
plt.scatter(df[str(sys.argv[1])],df[str(sys.argv[2])])
plt.xlabel(x)
plt.ylabel(y)
#save images
fig.savefig('test.png')
# Read image 
img = Image.open('test.png') 
# Output Images 
img.show() 

