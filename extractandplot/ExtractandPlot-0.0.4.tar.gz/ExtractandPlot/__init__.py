from google_drive_downloader import GoogleDriveDownloader as gdd
import pandas as pd
import matplotlib.pyplot as plt


def extract_Dataset(file_id,csv_name):
    #this function accept two strings value
    #1. file_id: The file sharing id of a particular content in ypur google drive
    #2. the Name by which you want to save the file 
    #this function save the file in the current working directory
    '''Summmary:
        this function accepst two strings value 
        1. file_id: The file sharing id of a particular content in ypur google drive
        2. csv_name: with format (filename.csv)
        3. return: Save the file in the current working directory
        '''
    
    gdd.download_file_from_google_drive(file_id='1-UbjfbAOiLriQ2Rstf44IJvsZncWVgeA',
                                    dest_path='./'+csv_name,
                                    unzip=True)
        
        
def plot_data(file_name,col1,col2):
    '''Summary:
        this function accepst three strings value 
        1. file_id: The name of the csv file in filename.csv format
        2. Col1:the Name of the columns to be selected as the x axis
        3. Col2: the Name of the columns to be selected as the y axis
        
        
        return:
               Save the plot with x axis as col1 as x axis and col2 as y axis
               in the current working directory
               '''
    df=pd.read_csv(file_name)
    x=df[col1].values
    y=df[col2].values
    plt.plot( x,y,linestyle='', marker='o', markersize=0.7)
    plt.xlabel(col1)
    plt.ylabel(col2)
    plt.plot()
    plt.savefig('saved_plot.png')