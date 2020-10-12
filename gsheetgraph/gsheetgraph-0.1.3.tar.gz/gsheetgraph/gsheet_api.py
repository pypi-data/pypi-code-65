# importing all the necessary packages for using google sheet api

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

# importing the packages for ploting the graph
import matplotlib.pyplot as plt
import pandas as pd
import pathlib

# This method will fetch the path for the creds.json which 
# all the access key and token 
loc = pathlib.Path(__file__).parent
jsonfile = (loc / "creds.json")

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]



# Authenticating the access key and tokens
creds = ServiceAccountCredentials.from_json_keyfile_name(jsonfile,scope)

client = gspread.authorize(creds)


# class for fetching the spread sheet data and ploting graphs
class gsheetconnection:
    def __init__(self):
        print("Kindly share your google sheet with the provide address :  nik-522@testsheets-291506.iam.gserviceaccount.com ")
        self.sheetname= input("\n\nEnter your google sheet name: ")
        print("Establishing the connection with the googlespreadsheet")

        # try except block insure that we are succesfully connect with the spreadsheet present in the drive
        try:
         
            # declaring global because we will use this object in all the methods in our program
            global sheet 
            
            sheet= client.open(self.sheetname).sheet1
           
            print("Connection established successfully")
        except:
            print("Unable to Establishig the connection or unable to find the sheet")
    
    # Fetching all the data present in the spreadSheet
    def getAllData(self):
        try:
            data = sheet.get_all_records()
            pprint(data)

        except:
            print("Data Not Found")

    # Fetching the values of row specified by user
    def getRowValues(self,row_number):
        try:
            rows = sheet.row_values(row_number)
            print("The row values are :\n")
            pprint(rows)
        
        except:
            print("Data not Found")

    # Fetching the values of column specified by user
    def getColValues(self,col_number):

        try:
            cols = sheet.col_values(col_number)
            print("The column values are :\n")
            pprint(cols)

        except:
            print("Data not found!")

    # Fetching the cell value
    def getCellValues(self,start_index,end_inded):

        try:
            cell = sheet.cell(start_index,end_inded).value
            print("The cell values are :\n")
            pprint(cell)

        except:
            print("Data not found!")

    # Inserting new row into the spreadsheet
    def insertRow(self,insteringValues,index):
        try:

            sheet.insert_row(insteringValues,index)
            print("Inserted Successfully")
        except:
            print("Unable to insert the dat")
    
    # Deleting the rows of the spreadSheet
    def deleteRow(self,start_index,end_index):

        try:
            sheet.delete_rows(start_index,end_index)
            print("Data deleted")
        except:
            print("Data cannot be deleted!")
        
    # Updating the data present the given cell   
    def updateCell(self,cell_row,cell_col,value):
        try:
            sheet.update_cell(cell_row,cell_col,value)
            print("Updated Successfully")
        except:
            print("Unable to updated the cell")
    
    # The most important task 
    # Ploting the graph by giving user to select the X-axes and y-axes and 
    # based on provided data and selected plot type the graph will be ploted.
    def plotGraph(self):
        data = sheet.get_all_records() 
        df = pd.DataFrame(data)
        header = list(df.columns)
        print("Select the columns for X-axes and Y-axes:\n")
        for val,col in enumerate(header):
            print(str(val)+" -> "+col)
        
        print("Enter the name of  X-axes: ")
        global x_name
        x_name =input()
        print("Enter the name of  Y-axes: ")
        global y_name
        y_name = input()

        global x_axes
        x_axes = df[x_name]
        
        global y_axes
        y_axes = df[y_name]
        def plotLineChart(self):
            plt.xlabel(x_name)
            plt.ylabel(y_name)
            plt.title(x_name +" vs "+ y_name)
            plt.plot(x_axes,y_axes)
            plt.show()
        def plotScatterPlot(self):
            plt.xlabel(x_name)
            plt.ylabel(y_name)
            plt.title(x_name +" vs "+ y_name)
            plt.scatter(x_axes,y_axes)
            plt.show()
        def ploltHistogram(self):
            df.hist()
        
    
        def plotBarChart(self):
            plt.xlabel(x_name)
            plt.ylabel(y_name)
            plt.title(x_name +" vs "+ y_name)
            plt.barh(x_axes,y_axes)
            plt.show()
    
        
        print("Select the Type of the Graph: ")
        graph =[plotLineChart,plotScatterPlot,ploltHistogram,plotBarChart]
        print('''
        1. LineChart
        2. ScatterPlot
        3. Histogram
        4. BarChart
        ''')

        choice = int(input())
        graph[choice-1](self)

def run():
    obj = gsheetconnection()     
if __name__ == "__main__":
    run()
    

    

         

