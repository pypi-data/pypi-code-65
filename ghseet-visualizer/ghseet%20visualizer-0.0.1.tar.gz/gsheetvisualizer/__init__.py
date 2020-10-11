from gsheets import Sheets
import pandas as pd
import matplotlib.pyplot as plt

sheets = Sheets.from_files('~D:/4th Year/client_secrets.json', '~/storage.json') 
s = sheets['18qSZJddBM_zSnFgcYZWHaiOBCT9Zi0PI2VGGamWdIcc']
#print(s.sheets[0]['C1'])
#p = s.sheets[0].to_csv('Spam.csv', encoding='utf-8', dialect='excel')
z= s.find('Greendeck SE Assignment Task 2 - Sheet1').to_frame()
df = pd.DataFrame(z)
#print(df)
x = df.iloc[:,0]
y =df.iloc[:,1]
#print(x)
#print(y)
plt.plot(x,y)
#plt.bar(x,y)
#plt.scatter(x,y)
plt.xlabel('Time Stamp')
plt.ylabel('Avg Sales')
plt.show()