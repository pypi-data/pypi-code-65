class Sheet_Plot:
    def __init__(self,file,key):
        self.file = file
        self.key = key
    def plot(self):
        import gspread
        gc = gspread.service_account(self.file)
        sheet = gc.open_by_key(self.key)
        worksheet = sheet.sheet1
        res = worksheet.get_all_records()
        y=[]
        x=[]
        t=len(res)
        keys=[]
        keys.append(res[0].keys())
        org_keys=list(keys[0])
        print(org_keys)
        print("Choose columns for x and y from above list: ")
        while(True):
            X=input("Enter for x: ")
            Y=input("Enter for y: ")
            print(X,Y)
            if X in org_keys:
                if Y in org_keys:
                    break
                else:
                    print("Incorrect Column Entered for Y")
            else:
                print("Incorrect Column Entered for X")
        for p in range(t):
            for i,v in res[p].items():
                if(i==X):
                    x.append(v)
                elif(i==Y):
                    y.append(v)
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_axes([0,0,1,1])
        ax.bar(x,y)
        plt.savefig('Pic.png',dpi=100)
        plt.show()

        


