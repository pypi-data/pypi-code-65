from gsheets import Sheets
import matplotlib.pyplot as plt

class Gsheets:
    def __init__(self):
        self.gsheets = Sheets.from_files('client_secret.json', 'storage.json')
        self.gsheets  #doctest: +ELLIPSIS

    def get_titles(self,unique:bool=False):
        return self.gsheets.titles(unique=unique)
    
    def get_sheet(self,title:str):
        return self.gsheets.find(title=title)

    def get_dataframe(self,title:str,sheet:str='Sheet1'):
        book=self.get_sheet(title=title)
        sheet=book.find(sheet)
        return sheet.to_frame()

class Plot:
    def __init__(self):
        self.gsheets=Gsheets()
    
    def get_dataframe(self,title:str,sheet:str='Sheet1'):
        return self.gsheets.get_dataframe(title=title,sheet=sheet)

    def get_columns(self,title:str,sheet:str='Sheet1'):
        df=self.get_dataframe(title=title,sheet=sheet)
        return df.columns

    def plot(self,x:str,y:str,title:str,sheet:str='Sheet1'):
        df=self.get_dataframe(title=title,sheet=sheet)
        plt.plot(df[x],df[y])
        plt.xlabel(x)
        plt.ylabel(y)
        plt.savefig('plot.png')

