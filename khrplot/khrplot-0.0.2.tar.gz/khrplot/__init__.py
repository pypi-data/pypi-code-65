import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import matplotlib.pyplot as plt

def plotit():
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    cred_path = input("Enter the path of Cred file:")
    creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
    client = gspread.authorize(creds)
    work_sheet=input("Enter your Google sheet url:")
    open_wks = client.open_by_url(work_sheet)
    sheet_name=input("Enter your sheet name:")
    ws = open_wks.worksheet(sheet_name)
    getrec=ws.get_all_records()
    df = pd.DataFrame.from_dict(getrec)
    print("The columns in your sheets are:",list(df))
    x_col=input('Enter the column name for x axis:')
    y_col=input('Enter the column name for y axis:')
    print("The plot for the given columns is")
    plt.plot(df[x_col],df[y_col])
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.show()
plotit()
