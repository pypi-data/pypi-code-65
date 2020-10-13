#Importing Libraries-----------------------------------------------
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import matplotlib.pyplot as plt
#------------------------------------------------------------------

# Creating the plot------------------------------------------------
def make_chart(df):
    X = input("Enter the Column Name for x-axis ")
    Y = input("Enter the Column Name for y-axis ")
    df.plot(kind = "scatter", x = X , y = Y)
    plt.autoscale(enable=True, axis='both', tight=None)
    plt.show()
    plt.savefig("chart.jpg")
#------------------------------------------------------------------

# Storing the gsheet's data to dataframe----------------------------
def make_dataframe(sheet):
    data = sheet.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns = headers)
    make_chart(df)
#-------------------------------------------------------------------

# Fetching the sheet from google drive-------------------------------------------------
def fetch_sheet(google_sheet_name):
    SCOPES = ["https://spreadsheets.google.com/feeds",
            'https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPES)
    client = gspread.authorize(creds)
    worksheet_name = input("Enter the name of the worksheet ")
    sheet = client.open(google_sheet_name).worksheet(worksheet_name)
    make_dataframe(sheet)
#-----------------------------------------------------------------------------------------

# Main-------------------------------------------------------------------------------------
if __name__ == '__main__':
    print("Kindly share your google sheet which you want to plot your data for to \"sunidhi@visualization-1602254198024.iam.gserviceaccount.com\" email ID before continuing   ")
    google_sheet_name = input("Enter the name of the google sheet located in your google drive ")
    fetch_sheet(google_sheet_name)
#-------------------------------------------------------------------------------------------