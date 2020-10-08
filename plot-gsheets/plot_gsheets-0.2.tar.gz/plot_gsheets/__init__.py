from __future__ import print_function
import pickle
import os.path
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import matplotlib.pyplot as plt
from pathlib import Path

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

creds = None
root_path=Path(__file__).parent

if os.path.exists(os.path.join( root_path, 'token.pickle')):
    with open(os.path.join( root_path, 'token.pickle'), 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(os.path.join( root_path, 'credentials.json'), SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(os.path.join( root_path, 'token.pickle'), 'wb') as token:
        pickle.dump(creds, token)

service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()


def get_columns(SPREADSHEET_ID,sheet_name):
    return (sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=sheet_name+'!1:1').execute()).get('values')[0]


def plot_sheet_columns(SPREADSHEET_ID,sheet_name,x_column_name,y_column_name):
    column_names = (sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=sheet_name+'!1:1').execute()).get('values')[0]
    x_index=column_names.index(x_column_name)
    y_index=column_names.index(y_column_name)

    sheets_values=sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=sheet_name).execute().get('values',[])[1:]
    x_list=[]
    y_list=[]

    if not sheets_values:
        print('No data found.')
    else:
        for row in sheets_values:
            x_list.append(row[x_index])
            y_list.append(row[y_index])

    plt.plot(x_list, y_list) 
    ax = plt.gca()

    max_yticks = 4
    max_xticks = 4
    yloc = plt.MaxNLocator(max_yticks)
    xloc = plt.MaxNLocator(max_xticks)
    ax.yaxis.set_major_locator(yloc)
    ax.xaxis.set_major_locator(xloc)

    plt.xlabel(x_column_name) 
    plt.ylabel(y_column_name) 


    plt.show()
    plt.savefig('plot.png') 