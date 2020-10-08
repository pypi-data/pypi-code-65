import json
from os import path
import tkinter as tk


class SqlConfigr:

    ENTRY_WIDTH = 100
    ROW_PADDING = 10
    ROW_PADDING_Y = 5

    def  __init__(self, fileName):
        self.fileName = fileName

        self.master = tk.Tk()
        tk.Label(self.master, text="User").grid(row=0, padx=self.ROW_PADDING, sticky='w')
        tk.Label(self.master, text="Host", anchor='w').grid(row=1, padx=self.ROW_PADDING, sticky='w')
        tk.Label(self.master, text="Database").grid(row=2, padx=self.ROW_PADDING, sticky='w')
        tk.Label(self.master, text="Password").grid(row=3, padx=self.ROW_PADDING, sticky='w')

        self.tk_user     = tk.Entry(self.master)
        self.tk_host     = tk.Entry(self.master)
        self.tk_database = tk.Entry(self.master)
        self.tk_passwd   = tk.Entry(self.master, show="*")
        

        self.tk_user.grid(row=0, column=1, ipadx=self.ENTRY_WIDTH, pady=self.ROW_PADDING_Y)
        self.tk_host.grid(row=1, column=1, ipadx=self.ENTRY_WIDTH, pady=self.ROW_PADDING_Y)
        self.tk_database.grid(row=2, column=1, ipadx=self.ENTRY_WIDTH, pady=self.ROW_PADDING_Y)
        self.tk_passwd.grid(row=3, column=1, ipadx=self.ENTRY_WIDTH, pady=self.ROW_PADDING_Y)
        

        self.b = tk.Button(self.master, text="Submit", command=self.writeToFile).grid(row=4, column=1, sticky='e')




    def getData(self):
        if not path.exists(self.fileName):
            self.createConfigFile()


        data = self.getConfigFileData()

        return data


    def createConfigFile(self):
        self.master.mainloop()

    def writeToFile(self):
        outputData = {
            "host": self.tk_host.get(),
            "user": self.tk_user.get(),
            "passwd": self.tk_passwd.get(),
            "database": self.tk_database.get(),
        }

        jsonString = json.dumps(outputData, sort_keys=True, indent=4)
        with open(self.fileName, "w") as newConfigFile:
            newConfigFile.write(jsonString)

        self.master.destroy()


    def getConfigFileData(self):
        with open(self.fileName, 'r') as configFile:
            configData = json.loads(configFile.read())
            return configData
