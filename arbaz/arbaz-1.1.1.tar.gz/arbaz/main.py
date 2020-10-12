
    ###############                     MAIN CODE              ###################

import  gspread

import matplotlib.pyplot as plt

from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json',scope)

client = gspread.authorize(creds)

sheet= client.open_by_key('1SrZfvr2ee54r7HR1jGtAE9zHIj_Y-UzK9ok8bdwkpqc').sheet1

#print(sheet.get_all_records())




x1= sheet.col_values(1)    #time_stamp
x2 = sheet.col_values(2)   #average_sales
 

plt.bar(x1, x2,color='g')
plt.ylabel('Sales')
plt.xlabel('Time_Stamp')
plt.title('Greendeck')
plt.show()






