from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import matplotlib.pyplot as plt 
import pandas as pd
    

def create_plot(id,name):
    
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    # The ID and range of a sample spreadsheet. 
    SAMPLE_SPREADSHEET_ID = id
    SAMPLE_RANGE_NAME = name

    def plot_line(df):
        x = input()
        y = input()
        plt.plot(x, y, data = df)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.savefig('D:\Projects\Greendeck\graph.pdf')
        plt.show()


    def main():
        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])


        l1 = []
        l2 = []
        l3 = []
        if not values:
            print('No data found.')
        else:
            for row in values:
                # Print columns A and B, which correspond to indices 0 and 4.
                # print('%s, %s' % (row[1], row[2]))
                l1.append(row[0])
                l2.append(row[1])
                l3.append(row[2])

            df = pd.DataFrame(list(zip(l1[1:],l2[1:],l3[1:])), columns=[l1[0],l2[0],l3[0]])
            df.timestamp = pd.to_datetime(df.timestamp, unit='s')
            df.average_sales = pd.to_numeric(df.average_sales, downcast = 'integer')
            df.offer_price = pd.to_numeric(df.offer_price, downcast = 'integer')
            plot_line(df)



    if __name__ == '__main__':
        main()

id = input()
name = input()

create_plot(id,name)