import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import matplotlib.pyplot as plt

def make_chart():
    SCOPES = ["https://spreadsheets.google.com/feeds",
            'https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open("Task2").sheet1
    print(sheet)
    data = sheet.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns = headers)
    print(df)
    x = df.timestamp
    y = df.average_sales
    plt.scatter(x,y)
    #plt.show()
    plt.savefig("chart.jpg")