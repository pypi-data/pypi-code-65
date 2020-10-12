import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

import matplotlib.pyplot as plt
import pandas as pd
import pathlib

loc = pathlib.Path(__file__).parent
jsonfile = (loc / "creds.json")

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]




creds = ServiceAccountCredentials.from_json_keyfile_name(jsonfile,scope)

client = gspread.authorize(creds)


class gsheetconnection:
    def __init__(self):
        print("Kindly share your google sheet with the provide address :  nik-522@testsheets-291506.iam.gserviceaccount.com ")
        self.sheetname= input("\n\nEnter your google sheet name: ")
        print("Establishing the connection with the googlespreadsheet")
        try:

            global sheet 
            
            sheet= client.open(self.sheetname).sheet1
           
            print("Connection established successfully")
        except:
            print("Unable to Establishig the connection or unable to find the sheet")
    
    def getAllData(self):
        try:
            data = sheet.get_all_records()
            pprint(data)

        except:
            print("Data Not Found")

    def getRowValues(self,row_number):
        try:
            rows = sheet.row_values(row_number)
            print("The row values are :\n")
            pprint(rows)
        
        except:
            print("Data not Found")

    def getColValues(self,col_number):

        try:
            cols = sheet.col_values(col_number)
            print("The column values are :\n")
            pprint(cols)

        except:
            print("Data not found!")

    def getCellValues(self,start_index,end_inded):

        try:
            cell = sheet.cell(start_index,end_inded).value
            print("The cell values are :\n")
            pprint(cell)

        except:
            print("Data not found!")

    def insertRow(self,insteringValues,index):
        try:

            sheet.insert_row(insteringValues,index)
            print("Inserted Successfully")
        except:
            print("Unable to insert the dat")
    
    def deleteRow(self,start_index,end_index):

        try:
            sheet.delete_rows(start_index,end_index)
            print("Data deleted")
        except:
            print("Data cannot be deleted!")
        
    def updateCell(self,cell_row,cell_col,value):
        try:
            sheet.update_cell(cell_row,cell_col,value)
            print("Updated Successfully")
        except:
            print("Unable to updated the cell")
    
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
            pass
        def ploltHistogram(self):
            pass
        
    
        def plotBarChart(self):
            pass
    
        
        print("Select the Type of the Graph: ")
        graph =[plotLineChart,plotScatterPlot,ploltHistogram,plotBarChart]
        for i,val in enumerate (graph):
            print(str(i)+" : "+str(val))

        choice = int(input())
        graph[choice-1](self)

def run():
    obj = gsheetconnection()        
if __name__ == "__main__":
    run()
    

    

         

