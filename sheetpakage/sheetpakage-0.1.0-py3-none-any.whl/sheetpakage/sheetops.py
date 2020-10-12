import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as  pd

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
sheet_range = 'sheet1!$A$1:$ZZ'

#First step
class sheet:
    """
    A class in which have a function and you can give the parameters using those function
    so can create a graph and access values on google spreadsheet via google spreadsheetApi
    """

    #Second step
    def __init__(self, spreadsheet_id: str, sheet_id: int, x_axis: str, y_axis: str):
        """

        :param spreadsheet_id: id of spreadsheet
        :param sheet_id: id of sheet in spreadsheet
        :param x_axis:  name of x axis
        :param y_axis: name of y axis
        :param client_secrete: give your credential file which is in JSON
        """
        self.spreadsheet_id = spreadsheet_id
        self.sheet_id = sheet_id
        self.x_axis = x_axis
        self.y_axis = y_axis

    #Third step
    def call_spreadsheet_n_create_graph(self):
        """
        a fucnction takes argument from init and by using that access the spreadsheet and plot a basic chart on it
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
                    'client_secret.json', SCOPES)
                # giving localhost becaue I mentioned local host in redirect urls
                creds = flow.run_local_server(host='localhost', port=8080)

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        #calling the sheet api
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=self.spreadsheet_id,
                                    range=sheet_range).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
        else:
            print('found')

        #making new headers
        df = pd.DataFrame(values)
        new_header = df.iloc[0]
        df = df[1:]
        df.columns = new_header

        #geting the index value of column
        x = df.columns.get_loc(self.x_axis)
        y = df.columns.get_loc(self.y_axis)


        #making basic graph
        request_body = {
            "requests": [
                {
                    "addChart": {
                        "chart": {
                            "spec": {
                                "title": "Graph",
                                "basicChart": {
                                    "chartType": "COLUMN",
                                    "legendPosition": "BOTTOM_LEGEND",
                                    "axis": [
                                        {
                                            "position": "BOTTOM_AXIS",
                                            "title": self.x_axis
                                        },
                                        {
                                            "position": "LEFT_AXIS",
                                            "title": self.y_axis
                                        }
                                    ],
                                    "domains": [
                                        {
                                            "domain": {
                                                "sourceRange": {
                                                    "sources": [
                                                        {
                                                            "sheetId": self.sheet_id,
                                                            "startRowIndex": 0,
                                                            "endRowIndex": len(values),
                                                            "startColumnIndex": x,
                                                            "endColumnIndex": x+1
                                                        }
                                                    ]
                                                }
                                            }
                                        }
                                    ],
                                    "series": [
                                        {
                                            "series": {
                                                "sourceRange": {
                                                    "sources": [
                                                        {
                                                            "sheetId": self.sheet_id,
                                                            "startRowIndex": 0,
                                                            "endRowIndex": len(values),
                                                            "startColumnIndex": y,
                                                            "endColumnIndex": y+1
                                                        }
                                                    ]
                                                }
                                            },
                                            "targetAxis": "LEFT_AXIS"
                                        }
                                    ],
                                    "headerCount": 1
                                }
                            },
                            "position": {
                                "overlayPosition": {
                                    "anchorCell": {
                                        "sheetId": self.sheet_id,
                                        "rowIndex": 0,
                                        "columnIndex": 3
                                    },
                                    "offsetXPixels": 370,
                                    "offsetYPixels": 200,
                                    "widthPixels": 800,
                                    "heightPixels": 300
                                }
                            }
                        }
                    }
                }
            ]
        }


        response = service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=request_body).execute()




