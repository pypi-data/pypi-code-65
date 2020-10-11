import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def getdata(jsfile, gsfile):
    # use creds to create a client to interact with the Google Drive API
    scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    
    credential = ServiceAccountCredentials.from_json_keyfile_name(jsfile, scope)
    
    client = gspread.authorize(credential)   
  

    googlesheet = client.open(gsfile).sheet1

    # Extract and store all of the values
    gspread_list = googlesheet.get_all_records()
   
    gspread_data = pd.DataFrame.from_dict(gspread_list)

     # return gspread_data
    return gspread_data

#print(getdata("C:\\Users\\Nikhil Shrivastava\\Downloads\\My First Project-af73b868924b.json", "Greendeck Assignment"))   


# Google Sheets Features.
# Open a spreadsheet by title, key or url.
# Read, write, and format cell ranges.
# Sharing and access control.
# Batching updates.
# oauth2client library will help us to get the client credientials a to read the data of specific Spread Sheet.