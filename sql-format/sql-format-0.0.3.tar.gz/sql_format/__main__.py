import tkinter as tk
import requests
import json

# constants
url                 = 'http://www.gudusoft.com/format.php'
ENTRY_WIDTH         = 150
ENTRY_HEIGHT        = 25
ENTRY_PADDING_X     = 25
BG_GREY             = 'lightgrey'
DEFAULT_OPTIONS_URL = 'https://raw.githubusercontent.com/rrickgauer/sql-format/master/options.json'

# formats the text
def formatText():
    formattedText = getFormattedText()
    resultText.delete("1.0", tk.END)
    resultText.insert(tk.INSERT, formattedText)

# sends a post request to the sql formatter api
def getFormattedText():
    configData = getConfigData()
    sql = inputText.get("1.0", tk.END);

    myobj = {
        'rqst_input_sql': sql,
        'rqst_formatOptions': configData,
    }

    x = requests.post(url, data = myobj)
    data = x.json() 
    return data['rspn_formatted_sql']

# returns the config data
def getConfigData():
    configData = requests.get(DEFAULT_OPTIONS_URL).text
    return configData


def main():
    # master window
    master = tk.Tk()
    master.title("SQL Formatter")
    master.configure(bg=BG_GREY)

    # sql format label
    tk.Label(master, text="SQL Formatter", bg=BG_GREY, font=("Helvetica", 16)).grid(row=0, pady=20)

    # input text
    inputText = tk.Text(master, height=10, width=ENTRY_WIDTH, tabs=4)
    inputText.grid(row=1, padx=ENTRY_PADDING_X)
    inputText.insert(tk.INSERT, 'Paste code here...')


    # format sql button
    submitButton = tk.Button(master, text="Format SQL", command=formatText).grid(row=2, column=0, padx=10, pady=10, sticky='e')

    # result text area
    resultText = tk.Text(master, height=ENTRY_HEIGHT, width=ENTRY_WIDTH, tabs=4)
    resultText.grid(row=3, column=0, padx=ENTRY_PADDING_X, pady=10)

    tk.mainloop()


if __name__ == "__main__":
    main()
