from gsheets import Sheets


def openSheet(sheetId):
    sheets = Sheets.from_files('~/client_secrets.json', '~/storage.json')
    return sheets[sheetId]

def toFrame(sheet,worksheetTitle):
    return sheet.find(worksheetTitle).to_frame()

def plot(dataFrame,yColumn,xColumn):
    fig=dataFrame.plot(x =xColumn, y=yColumn, kind = 'line').get_figure()	
    fig.savefig("output.png")




    


    
