import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .gsheet_image import Create_service


class Image_generator(object):
    def __init__(self,path):
        self.CLIENT_SECRET_FILE = path
        self.API_SERVICE_NAME = 'drive'
        self.API_VERSION = 'v3'
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        self.service=Create_service(self.CLIENT_SECRET_FILE, self.API_SERVICE_NAME, self.API_VERSION, self.SCOPES)
        self.files_service=self.service.files()
        self.query_body="mimeType='application/vnd.google-apps.spreadsheet'"
        self.files_retrieved=self.files_service.list(
            q=self.query_body
        ).execute()
        self.drive_spreadsheet_files_data=pd.DataFrame(self.files_retrieved.get('files'))

        print(self.drive_spreadsheet_files_data.name)
        print("Enter the Respective Sheet Number to select the sheet : ")
        self.sheet_no=int(input())

        self.API_SERVICE_NAME = 'sheets'
        self.API_VERSION = 'v4'

        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
 
        self.spreadsheet_id=self.drive_spreadsheet_files_data.iloc[self.sheet_no]['id']
        self.service = Create_service(self.CLIENT_SECRET_FILE, self.API_SERVICE_NAME, self.API_VERSION, self.SCOPES)
        self.google_sheet = self.service.spreadsheets()
        self.rows = self.google_sheet.values().get(spreadsheetId=self.spreadsheet_id,range='Sheet1').execute()
        self.data = self.rows.get('values')
        self.sheet = pd.DataFrame(self.data)
        self.cols=self.sheet.iloc[0]
        self.sheet=self.sheet.iloc[1:]
        self.sheet.columns=self.cols

    def get_column(self,axis):
        print(self.sheet.columns)
        print("Enter the number to select the column for "+ axis +' axis')
        return str(input())

    def convert_dtype(self,column,type_conversion):
        self.sheet[column]=self.sheet[column]=self.sheet[column].astype(type_conversion)

    def convert_timestamp_to_datetime(self):
        print(self.sheet.columns)
        print("Select & Enter column to convert it in to Date time")
        column=str(input())
        self.sheet[column]=self.sheet[column].astype('int')
        self.sheet[column]=self.sheet[column].apply(lambda x:pd.Timestamp(x,unit='s').date())
        self.sheet[column]=pd.to_datetime(self.sheet[column])
    
    def generate_year(self):
        print("Enter the column name from which you want to extract year")
        print(self.sheet.columns)
        self.column_name=str(input())
        self.sheet['year']=self.sheet[self.column_name].dt.year
    def generate_month(self):
        print("Enter the column name from which you want to extract year")
        print(self.sheet.columns)
        self.column_name=str(input())
        self.sheet['month']=self.sheet[self.column_name].dt.month

    def generate_day(self):
        print("Enter the column name from which you want to extract year")
        print(self.sheet.columns)
        self.column_name=str(input())
        self.sheet['day']=self.sheet[self.column_name].dt.day

    def groupby_column(self,column):
        self.sheet=self.sheet.groupby(by=[column]).sum()
        self.sheet.reset_index(inplace=True)

    def plot_line_graph(self):
        self.sheet_cols=self.sheet.columns
        self.x_axis=self.get_column('X') #Selecting X-axis
        self.y_axis=self.get_column('Y') #Selecting Y-axis


        self.sheet[self.x_axis]=self.sheet[self.x_axis].astype('int')   #Converting the X-axis to Int
        self.sheet[self.y_axis]=self.sheet[self.y_axis].astype('int')   #Converting the Y-axis to Int
        plt.plot(self.sheet[self.x_axis],self.sheet[self.y_axis],'g')   #Plotting the Graph
        plt.yticks(np.linspace(0, max(self.sheet[self.y_axis])+1 , 10).astype('int'))          #Yticks for better vizulization
        plt.xticks(np.arange(min(self.sheet[self.x_axis]),max(self.sheet[self.x_axis]+1),1).astype('int'))  #Xticks for better vizulization
        print("Enter the Director Path where you want to store Yor Image")
        self.path_to_store=str(input())
        plt.savefig(self.path_to_store+'/'+self.x_axis.capitalize()+"_vs_"+self.y_axis.capitalize()+"_Line_Graph")       #Saving the Graph as Image
        plt.show()

    def plot_bar_graph(self):
        self.sheet_cols=self.sheet.columns
        self.x_axis=self.get_column('X') #Selecting X-axis
        self.y_axis=self.get_column('Y') #Selecting Y-axis

        sns.barplot(self.sheet[self.x_axis],self.sheet[self.y_axis])   #Plotting the Graph 
        print("Enter the Director Path where you want to store Yor Image")
        self.path_to_store=str(input())
        plt.savefig(self.path_to_store+'/'+self.x_axis.capitalize()+"_vs_"+self.y_axis.capitalize()+"_Bar_Graph")       #Saving the Graph as Image
        plt.show()

    def box_plot(self):
        self.sheet_cols=self.sheet.columns
        self.x_axis=self.get_column('X') #Selecting X-axis
        self.y_axis=self.get_column('Y') #Selecting Y-axis

        self.sheet[self.x_axis]=self.sheet[self.x_axis].astype('int')   #Converting the X-axis to Int
        self.sheet[self.y_axis]=self.sheet[self.y_axis].astype('int')   #Converting the Y-axis to Int

        sns.boxplot(x=self.sheet[self.x_axis],y=self.sheet[self.y_axis])   #Plotting the Graph 
        print("Enter the Director Path where you want to store Yor Image")
        self.path_to_store=str(input())
        plt.savefig(self.path_to_store+'/'+self.x_axis.capitalize()+"_vs_"+self.y_axis.capitalize()+"_Box_plot")       #Saving the Graph as Image
        plt.show()

    def scatter_plot(self):
        self.sheet_cols=self.sheet.columns
        self.x_axis=self.get_column('X') #Selecting X-axis
        self.y_axis=self.get_column('Y') #Selecting Y-axis


        self.sheet[self.x_axis]=self.sheet[self.x_axis].astype('int')   #Converting the X-axis to Int
        self.sheet[self.y_axis]=self.sheet[self.y_axis].astype('int')   #Converting the Y-axis to Int
        plt.scatter(self.sheet[self.x_axis],self.sheet[self.y_axis],'g')   #Plotting the Graph
        plt.yticks(np.linspace(0, max(self.sheet[self.y_axis])+1 , 10).astype('int'))          #Yticks for better vizulization
        plt.xticks(np.arange(min(self.sheet[self.x_axis]),max(self.sheet[self.x_axis]+1),1).astype('int'))  #Xticks for better vizulization
        print("Enter the Director Path where you want to store Yor Image")
        self.path_to_store=str(input())
        plt.savefig(self.path_to_store+'/'+self.x_axis.capitalize()+"_vs_"+self.y_axis.capitalize()+"_Scatter_plot")       #Saving the Graph as Image
        plt.show()