import gspread
import matplotlib.pyplot as plt
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

scope = ['https://www.googleapis.com/auth/drive']
# credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json',scope) <--this is giving error as credentional.json file not found even after it was present in current directory so i have made dictionary explicitly
credentials = service_account.Credentials.from_service_account_info({
  "type": "service_account",
  "project_id": "surajfirst1",
  "private_key_id": "04b848082654b564df6c362e04f75f8a73c60504",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC4S6Y17kwVAUGF\n4465H28BBJKlIY0xTtVGhIrGaEqylG+XNKXlO/1zZilW7VtU+A/GKu1Q9slB4R3X\ncDBS+7WMVHtcqEj8Ydzsa6CDdqSTPszZojrF4VKDmSuYw06zVhsmmINoeV0om102\nzzLoyd3NkrGJF+ZMMMKW2Rvz+NzPeBJe2/WT5+AXgEFtsWsbgo1qpk9G0gK29Xxa\nfusg5T47yOYj+9k9Zkz6jKcaI3DGb9XqwX6j1c6o4wWobmt/o7qvEmJuYfVkaw9x\nHC5sS/CSqIC36MykhAnrXHk9e+5xt+IKDxwIxwH9I0FbxvGEoLBBGf9xn3y8PyHt\neV8hagztAgMBAAECggEAHQRmOWgZiRYfSbQ0WOAC44tjhoYDm9+gc3+zdP1fQ4Jd\nFpbmxvLc22JawHHTV0vOegJwxrZwpkOKZg0nQq2Ynm1/1e02Pqyu8veYOJLB42A4\nM00YiWcKjadchqs7tT9pu3g4eobfXOEnelWB28bK+k7uTppZe6YSwVsSTGXi6HRn\nsrGh8A9rIPito+Dy0jCugSC+3uj7XXEJc9uc2qTaywqcgY120nsZDvWl8hRNevyq\n7qiz+m9i5fK0lnKrSIjiyMwleyQz+59fCMVh+JxXzpProze6d9Do5KxF9coDJJwP\nKEQVLno4egd8hpQLO+gj3mGIPPt6tH0hk32tGvu+aQKBgQD1OkRGgsqhK2iWkFc6\nfS6cTNTHhhT0hhOBI1jNanXO5u5dqgu5EuuAXsK9OPtATeaLlaGcftXdAxpZ43Q3\n3Z1d/sk87Xf/uEcLuRehiae5Fa94GWMD+NFITzcJ9Lj+uwMK9adKJyOsJ7XemCXd\nf/dz6JXjih4AhvjXBOAs27JPGQKBgQDAZCoC8SaxgzKdGa+j6NxjPll8GeGysLbw\noXX/F3o/P2I2psgH52XHV2QMoa7D8SYWKCeNXjgo1vvxy7tC3e2+UILx7jTP6TMj\nV0Bj7OxdLOIOFHzMX1N/A4c8SY/vwQv8/6vnYIiJSbpBeY2rbhWwRCmdTXXFRaJV\nSchAN6Rq9QKBgQCzS/fRih13O5LLyxtL820Z8H7+pwU5R7KJD/wErNsX/Pa5WvQZ\nTEEN6br+uOPTP2HaGvw/vOjHIFaq9Efr9Mfziq8+Me4z9VtUse8aN9h+1eEmsYEY\nzVrPQMPgLqL39GokIDpBWF6Xp60s5BeDXOXjRGIbLMgE4KqeI714buVvOQKBgBUy\ntCJQ2deTQh9nNiAURzw0IX34CBM9P1ryH2M0/gY8AKFO7RlZ2LAHJAH0SqJSTsUA\nNaNw7zUowufYb9ClTU2750Gq4mzKIBVTxsd70mtNx7aPcVS/aB7Fj8AHxvE+zwhY\nT2OWElU2J2yRbRencIJUcFVhtIlA6+sDzymsN9SFAoGBAMxNycvF+XLIr/mxrhZ+\nraH+xIp/xurJkybwWfdd11cP8FAK54xViE0ENW0qCAV5Qqpfx92a6e5bZDW4l5+m\nSxIikWkUsKZaEPJG7hOtfyFDAeZwCBJkpCFuyaqJdaZCQLYhO6/6e+joPMqoQX8H\neg7LY2yCdhEf7BGFbH62RBO9\n-----END PRIVATE KEY-----\n",
  "client_email": "greendeckds@surajfirst1.iam.gserviceaccount.com",
  "client_id": "108308946542755285714",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/greendeckds%40surajfirst1.iam.gserviceaccount.com"
},scopes=scope)
client = gspread.authorize(credentials)

def get_all_columns(url):
  sheet = client.open_by_url(url)
  sheet.share('greendeckds@surajfirst1.iam.gserviceaccount.com',perm_type='user',role='writer')
  sheet = client.open(str(sheet.title)).sheet1
  first_row_values = sheet.row_values(1)
  return first_row_values

def plot_graph(url,col1,col2,pa='assets'):
    sheet = client.open_by_url(url)
    sheet.share('greendeckds@surajfirst1.iam.gserviceaccount.com',perm_type='user',role='writer')
    sheet = client.open(str(sheet.title)).sheet1
    data1 = sheet.col_values(col1)
    data2 = sheet.col_values(col2)
    data1 = data1[1:]
    data1 = [int(i) for i in data1] 
    data2 = data2[1:]
    data2 = [int(i) for i in data2] 

    plt.plot(data1, data2)
    plt.savefig(pa+'/my_plot.png')

















































# import gspread
# import matplotlib.pyplot as plt
# from google.oauth2.service_account import Credentials
# from oauth2client.service_account import ServiceAccountCredentials

# scope = ['https://www.googleapis.com/auth/drive']
# # credentials = ServiceAccountCredentials.from_json_keyfile_name('My GreenDeck Project-cd6ad9db2914.json',scope)
# credentials = Credentials.from_service_account_file('Credentials.json',scopes=scope)
# client = gspread.authorize(credentials)



# def sheet_url_and_axis(url,col1,col2):
#     '''This function will take url of the spreadsheet and along with that two column numbers as x-axis and y-axis respectively'''
    
#     sheet = client.open_by_url(url) #
#     sheet.share('dsproject@my-greendeck-project.iam.gserviceaccount.com',perm_type='user',role='writer')  #this will send the sheet to the provided email so that at runtime it will not give fileNotFoundError
#     sheet = client.open(str(sheet.title)).sheet1   #this will fetch the data from the url and store it in the WorkSheet object(sheet)
#     x_axis = sheet.col_values(col1)  #this will fetch the col1 column entry and store its data in x_axis
    
#     y_axis = sheet.col_values(col2)
#     # print(data1)

#     x_axis = x_axis[1:]
#     x_axis = [int(i) for i in x_axis] 
#     y_axis = y_axis[1:]
#     y_axis = [int(i) for i in y_axis] 
#     plt.scatter(x_axis, y_axis)
#     plt.savefig('my_plot.png')


# def get_graph():
#     return 'my_plot.png'


