import gspread
import matplotlib.pyplot as plt
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

scope = ['https://www.googleapis.com/auth/drive']
# credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json',scope) <--this is giving error as credentional.json file not found even after it was present in current directory so i have made dictionary explicitly
credentials = service_account.Credentials.from_service_account_info({
  "type": "service_account",
  "project_id": "my-greendeck-ds-project",
  "private_key_id": "9c0e5ae3a5d4f4278cfbf1489cba4da9d60312c9",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCHVsSr/VmOrp1Z\nSnmfJzJ+92pzVnRNBtKq/KGk6887KzrA/S9zTKmwQ/9TMkxgj6FA1QGgXnqvQ9D8\noq85tYOo3tlcCscJeSp2P362z+ogx+Gcl/wV9GSoADDvWG/2QRs1cbw1PUsr0gw9\nip1B2zstLuoI3+7i1IhAwUb+1s6QhylsDGev+bilqX6yGL+bpSi/MJJu+jGRN5D+\n6gTBqfPL5/B0MpG73mzAJf/D9QugHynd3SFEn2ym9CmGtUX1HRqNN1wFIO2ZrvXD\nJsnwtv+uMOrVIonzTD6umDJKVpuWG/+11MNa+OTOhzYiW6XK6s6BsRUP0XzA4X4v\n+4AvLYBFAgMBAAECggEAIcQ/DRdIoy4DUa4gcpo9wcpaq5ywJzCy2pjt/p8cBOv3\n/IMe9eI0eyc3+qqzvirPxYRvo7K24uglagbv95LHXth8/DcvKjiqJLcaVyPASz37\nlw2fhl3DyFvF2c2jn5nmXzr5hYH9sZj2V1tweWgol1EbcKvoZv02YoumejofbxUB\nF1KaQB2KVtt3GbgYNmxeOWee4GBFVIGS8dg01gDxwpUVa7LsNtyAygppYA3j7EZv\nS/hGvY3uJ4VPKnyAghh9IKo65zdfh2p1mjxyEjHgiGmdnDRGetcS2HNMPHH9ZE8K\nwvouJeZD6oAvg7eSBkWZQZcmTcxI/rU8yTeGdLg7+QKBgQC8vh1MKiuw38+7JgBW\nLUHRmCE0QN2hKmM2zKJ5V6otACp1/AkUG9wBibYYLpyG/6Vt/fP1JecttD1TDosz\nfFEzUkVbWv/frlg9ZigMDFDCNlFxdsiotsRGwGkqutzOQ8+ps0PJv7DKIcIO+U5/\nJqVTwVWGgSmXgnMGmp9E+8WKKQKBgQC3kPJ/91T2ACpi+PBUMXLVfZ5IL97gAnVf\nynfRZPgUzY0HqkjD+d+IwmG2qHI64BLY8CoyjbBZEkcij+uOgOAMpXoWB0adKHsN\n4fmZB/mm/bZePjDhhTbyumz4gs1pwifXDYXQZN+b8NqWETGaVBn2XtwKumftVpnn\n1fwOS3KAvQKBgQCmioqHfl52/8XouStq3xxIuRfzZ5kocKKC5CYpM/VxJ8hPu0i3\nea2znbQTum1boZBzcbYmBn/qkDPcaeTiVTvBMUMJzU4iLVCnPNDxcJyCAjPzDoEY\nfczLMVSa46+aQbOnZgrWplJ0yTzWwZ1GDO+s69dvi+ELU4vzs9P9prszoQKBgE6+\n/Whr36SQOZ6vj9luRQbUlpv8/S03oMZxAqlvGQVDkGZjZEe932i5ilVjOW2MRkmN\n7Ww2YBo1vxJSjwhYvMRwEEl24ZH1laRE9l/xjeVXHW6cWzfDf+jslGafJiNiSNj2\nUhstyscIsZyCz7aWsXSBCQAJKyAjcG6F21T+hKY5AoGAUWtJlF/fe3LR0BFVyTgU\ncLvrtXYoder9r+QUjt5tAtFgYKWvTi+eQ0MPvNuxlWmNUfpSRpXr0LcBL0k/h9gC\nGU+ycbL3mGHD5VuruShuxi3EH3BFbVNICS+Dvnvd9qV4hgw5FAa8zamGfIqWjW8S\npea7X00A3SjyNXtgeTjTfi8=\n-----END PRIVATE KEY-----\n",
  "client_email": "greendeckds@my-greendeck-ds-project.iam.gserviceaccount.com",
  "client_id": "106094392297611537557",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/greendeckds%40my-greendeck-ds-project.iam.gserviceaccount.com"
},scopes=scope)
client = gspread.authorize(credentials)

def get_all_columns(url):
  sheet = client.open_by_url(url)
  sheet.share('greendeckds@my-greendeck-ds-project.iam.gserviceaccount.com',perm_type='user',role='writer')
  sheet = client.open(str(sheet.title)).sheet1
  first_row_values = sheet.row_values(1)
  return first_row_values

def plot_graph(url,col1,col2,pa='assets'):
    sheet = client.open_by_url(url)
    sheet.share('greendeckds@my-greendeck-ds-project.iam.gserviceaccount.com',perm_type='user',role='writer')
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


