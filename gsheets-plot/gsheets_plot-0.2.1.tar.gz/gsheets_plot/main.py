from gsheets import Sheets
import matplotlib.pyplot as plt

class Gsheets:
    def __init__(self):
        self.gsheets = Sheets.from_files('client_secret.json', 'storage.json')
        self.gsheets  #doctest: +ELLIPSIS

    def get_titles(self,unique:bool=False):
        return self.gsheets.titles(unique=unique)
    
    def get_sheet_title(self,title:str):
        return self.gsheets.find(title=title)

    def get_sheet_url(self,url:str):
        return self.gsheets.get(url)

    def get_dataframe(self,title:str=None,url:str=None,sheet:str='Sheet1'):
        if title:
            book=self.get_sheet_title(title=title)
        if url:
            book=self.get_sheet_url(url=url)
        sheet=book.find(sheet)
        return sheet.to_frame()

class Plot:
    def __init__(self,title:str=None,url:str=None,sheet:str='Sheet1'):
        self.gsheets=Gsheets()
        self.df=self.gsheets.get_dataframe(title=title,url=url,sheet=sheet)
        

    def get_columns(self):
        return self.df.columns

    def plot(self,x:str,y:str):
        plt.plot(self.df[x],self.df[y])
        plt.xlabel(x)
        plt.ylabel(y)
        plt.savefig('plot.png')

