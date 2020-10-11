import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import matplotlib.pyplot as plt

def make_chart(df):
    X = input("Enter the Column Name for x-axis ")
    Y = input("Enter the Column Name for y-axis ")
    df.plot(kind = "scatter", x = X , y = Y)
    # plt.plot(range(0,10))
    # scale_factor = 5
    # xmin, xmax = plt.xlim()
    # ymin, ymax = plt.ylim()
    # plt.xlim(xmin * scale_factor, xmax* scale_factor)
    # plt.ylim(ymin * scale_factor, ymax * scale_factor)
    # plt.xticks(rotation = 90)
    # plt.axis('scaled')
    plt.autoscale(enable=True, axis='both', tight=None)
    plt.show()
    plt.savefig("chart.jpg")

def make_dataframe(sheet):
    data = sheet.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns = headers)
    make_chart(df)

def fetch_sheet(sheet_name):
    SCOPES = ["https://spreadsheets.google.com/feeds",
            'https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    make_dataframe(sheet)

if __name__ == '__main__':
    print("Kindly share your google sheet which you want to plot your data for to \"sunidhi@visualization-1602254198024.iam.gserviceaccount.com\" email ID before continuing   ")
    sheet_name = input("Enter the name of the sheet in located in your google drive ")
    print(sheet_name)
    fetch_sheet(sheet_name)