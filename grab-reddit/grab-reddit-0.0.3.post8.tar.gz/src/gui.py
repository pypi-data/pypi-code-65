"""
@author: RealStickman
"""
import configparser
import os
import subprocess
import tkinter as tk
import sys
from pathlib import Path
from tkinter import messagebox, filedialog, ttk
import praw
import prawcore

#Reads the config and places the values into the global namespace
def readconf():
    print("Reading Config file")
    config.read('grab.ini')
    global lim
    lim = int(config['CONFIG']['limit'])
    global category
    category = config['CONFIG']['category']
    global subl
    subl = config['CONFIG']['subs']
    global sublist
    sublist = subl.replace('.empty.', '')
    global path
    path = config['CONFIG']['path']
    global seltheme
    seltheme = config['CONFIG']['theme']

#Write the configuration file
def writeconf():
    print("placeholder")
    config['CONFIG'] = {'limit': lim,
                        'category': category,
                        'subs': sublist,
                        'path': path,
                        'theme': seltheme}
    with open('grab.ini', 'w') as configfile:
        config.write(configfile)

def addfr():
    #remove add/remove subreddit buttons
    butaddsub.destroy()
    butremsub.destroy()

    #Frame for adding subs
    global addsub
    addsub = ttk.Frame(normal)
    addsub.grid(row=1, column=0, sticky="W")

    #Label
    ttk.Label(addsub, text="Enter subreddit:").grid(row=0, column=0, sticky="W")

    #textbox
    global txtent
    txtent = ttk.Entry(addsub)
    txtent.grid(row=1, column=0, sticky="W")

    #abort
    ttk.Button(addsub, text="Cancel", command=cancel).grid(row=2, column=0, sticky="W")

    #try to add
    ttk.Button(addsub, text="Add", command=save).grid(row=2, column=0, sticky="E")

#kills the add subreddit window
def cancel():
    addsub.destroy()

    # add new subreddits
    global butaddsub
    butaddsub = ttk.Button(normal, text="+", command=addfr)
    butaddsub.grid(row=1, column=0, sticky="W", padx=2)

    # remove subreddits
    global butremsub
    butremsub = ttk.Button(normal, text="-", command=listbox)
    butremsub.grid(row=1, column=0, sticky="E")

#for saving subreddits
def save():
    #reddit stuff
    reddit = praw.Reddit(client_id="48VCokBQkKDsEg",
                         client_secret=None,
                         user_agent="grab, a Reddit download bot by /u/RealStickman_")

    #hope the user wrote something
    try:
        txte = txtent.get()
        #check if what the user wrote makes sense
        try:
            subreddit = reddit.subreddit(txte)
            subreddit.title

            #read the config
            readconf()
            # explicitly assign sublist variable, otherwise it complains about the variable being called before assignment
            global sublist
            #add entered subreddit
            sublist += subreddit.display_name + ";"
            #that's were we're gonna put it
            writeconf()
            print("Added " + subreddit.display_name)

            #reformatting list of subs
            lsublist = sublist.split(";")
            labelsublist = [x for x in lsublist if x]
            # displays list of subreddits
            lbox.delete(0, 'end')
            for i in range(len(labelsublist)):
                lbox.insert('end', labelsublist[i])

            #destroy window
            addsub.destroy()
        #if the subreddit can't be found
        except prawcore.exceptions.Redirect:
            messagebox.showerror("Wrong Subreddit", subreddit.display_name + " does not exist")
        # add new subreddits
        global butaddsub
        butaddsub = ttk.Button(normal, text="+", command=addfr)
        butaddsub.grid(row=1, column=0, sticky="W", padx=2)

        # remove subreddits
        global butremsub
        butremsub = ttk.Button(normal, text="-", command=listbox)
        butremsub.grid(row=1, column=0, sticky="E")
    #if the user didn't type anything
    except TypeError:
        messagebox.showerror("No Subreddit", "Please fill in a subreddit")

#closes the window and stops the program
def stop():
    root.destroy()
    sys.exit()
    exit()

#runs the program
def run():
    messagebox.showinfo("Running", "Program is running")
    #python3 was used to deal with Debian still linking python with python2 instead of python3
    child = subprocess.Popen('python3 grab.py', shell=True, stdout=subprocess.PIPE, text=True)
    data = child.communicate()[0]
    rc = child.returncode
    print(data)
    print("grab.py finished with exit code " + str(rc))
    if rc == 0:
        messagebox.showinfo("Success", "Program ran without errors")
    else:
        messagebox.showerror("Error", "Error code " + str(rc))
        with open("log.txt", "w") as log:
            log.write(data)
            log.write("\nError code " + str(rc))

def listbox():
    result = tk.messagebox.askyesno("Delete", "Remove selected subreddit from list?", icon='warning')
    if result == True:
        #read the config
        readconf()
        selec = lbox.curselection()
        val = lbox.get(selec)
        global sublist
        sublist = sublist.replace(";" + val, '')
        writeconf()
        print("Deleted " + val)
        updatlist()
    else:
        print("Nothing deleted")

def updatlist():
    #read the config
    readconf()
    lcusubl = sublist.split(";")
    labsubl = [x for x in lcusubl if x]
    lbox.delete(0, 'end')
    for i in range(len(labsubl)):
        lbox.insert(0, labsubl[i])

def catsel():
    readconf()
    global category
    #sets category based on the radiobutton selected
    if catvar.get() == 1:
        category = "controversial"
        writeconf()
        print("Setting category to controversial")
    # elif catvar.get() == 2:
    #     category = "gilded"
    #     writeconf()
    #     print("Setting category to gilded")
    elif catvar.get() == 3:
        category = "hot"
        writeconf()
        print("Setting category to hot")
    elif catvar.get() == 4:
        category = "new"
        writeconf()
        print("Setting category to new")
    elif catvar.get() == 5:
        category = "rising"
        writeconf()
        print("Setting category to rising")
    elif catvar.get() == 6:
        category = "top"
        writeconf()
        print("Setting category to top")
    else:
        print("Something went wrong")

#save the limit
def savelim():
    readconf()
    print("New limit: " + limspin.get())
    global lim
    lim = limspin.get()
    writeconf()

#expands the window to show all settings
def winexp():
    global extend
    extend = ttk.Frame(main)
    extend.grid(row=0, column=2, sticky="W")
    readconf()

    #destroy button to expand window
    butexp.destroy()

    #other settings
    setfr = ttk.Frame(extend)
    setfr.grid(row=0, column=1, sticky="W")

    #change theme
    ttk.Label(setfr, text="Change theme").grid(row=0, column=0, sticky="W")
    ttk.Button(setfr, text="light", command=setlight).grid(row=1, column=0, sticky="E")
    ttk.Button(setfr, text="dark", command=setdark).grid(row=1, column=1, sticky="W")

    #frame for various settings
    global varfr
    varfr = ttk.Frame(extend)
    varfr.grid(row=1, column=0, sticky="W")

    # Path
    global pathlab
    pathlab = ttk.Label(varfr, text="Path: " + path)
    pathlab.grid(row=0, column=1, sticky="W")
    global butpath
    butpath = ttk.Button(varfr, text="...", command=dirdialog)
    butpath.grid(row=0, column=2, sticky="W")

    # Limit
    global limspin
    limspin = tk.Spinbox(varfr, from_=0, to=100, width=5, bg=background, fg=foreground)
    limspin.grid(row=1, column=1, sticky="W")
    # show currently set limit
    i = 0
    while i < lim:
        limspin.invoke(element="buttonup")
        i += 1

    # limit save button
    global butsave
    butsave = ttk.Button(varfr, text="Save", command=savelim)
    butsave.grid(row=1, column=1, sticky="W", padx="55")

    #frame for categories
    global categ
    categ = ttk.Frame(extend)
    categ.grid(row=0, column=0, sticky="W")
    # Category label
    global labcateg
    labcateg = ttk.Label(categ, text="Category:")
    labcateg.grid(row=0, column=0, sticky="W")

    # category buttons for selection
    global catvar
    catvar = tk.IntVar()

    global catcont
    catcont = tk.Radiobutton(categ, text="controversial", variable=catvar, value=1, command=catsel, bg=background, fg=foreground, relief="ridge")
    catcont.grid(row=1, column=0, sticky="W")

    # global catgil
    # catgil = tk.Radiobutton(categ, text="gilded", variable=catvar, value=2, command=catsel, bg=background, fg=foreground, relief="ridge")
    # catgil.grid(row=1, column=1, sticky="W")

    global cathot
    cathot = tk.Radiobutton(categ, text="hot", variable=catvar, value=3, command=catsel, bg=background, fg=foreground, relief="ridge")
    cathot.grid(row=1, column=2, sticky="W")

    global catnew
    catnew = tk.Radiobutton(categ, text="new", variable=catvar, value=4, command=catsel, bg=background, fg=foreground, relief="ridge")
    catnew.grid(row=2, column=0, sticky="W")

    global catris
    catris = tk.Radiobutton(categ, text="rising", variable=catvar, value=5, command=catsel, bg=background, fg=foreground, relief="ridge")
    catris.grid(row=2, column=1, sticky="W")

    global cattop
    cattop = tk.Radiobutton(categ, text="top", variable=catvar, value=6, command=catsel, bg=background, fg=foreground, relief="ridge")
    #cattop.grid(row=2, column=2, sticky="W")
    cattop.grid(row=1, column=1, sticky="W")

    # selects appropriate button to show which one is active
    if category == 'controversial':
        print("Current selected category is " + category)
        catcont.select()
    # elif category == 'gilded':
    #     print("Current selected category is " + category)
    #     catgil.select()
    elif category == 'hot':
        print("Current selected category is " + category)
        cathot.select()
    elif category == 'new':
        print("Current selected category is " + category)
        catnew.select()
    elif category == 'rising':
        print("Current selected category is " + category)
        catris.select()
    elif category == 'top':
        print("Current selected category is " + category)
        cattop.select()

    #close expanded view
    global butshr
    butshr = ttk.Button(main, text="<", command=winshr)
    butshr.grid(row=1, column=1, sticky="W")

#setlight and setdark could maybe be integrated into one function.
def setlight():
    readconf()
    global seltheme
    if seltheme != "light":
        seltheme = "light"
        print("Setting " + seltheme + " theme")
        changetheme()
    else:
        print("Program is already using the " + seltheme + " theme")

def setdark():
    readconf()
    global seltheme
    if seltheme != "dark":
        seltheme = "dark"
        print("Setting " + seltheme + " theme")
        changetheme()
    else:
        print("Program is already using the " + seltheme + " theme")

#code pulled out of setlight and setdark in order to avoid huge blocks of duplicate code
def changetheme():
    print("placeholder")
    writeconf()
    root.destroy()
    subprocess.Popen('python3 gui.py', shell=True, text=True)

#shrinks the window back to original size
def winshr():
    #destroy extended view frame & everything in it
    extend.destroy()
    #recreate button to expand window
    global butexp
    butexp = ttk.Button(main, text=">", command=winexp)
    butexp.grid(row=1, column=1, sticky="W")

def dirdialog():
    readconf()
    #explicitly assign path variable, otherwise it complains about the variable being called before assignment
    global path
    path = tk.filedialog.askdirectory(parent=root, initialdir=path, title="Download directory")
    writeconf()
    global pathlab
    pathlab.destroy()
    pathlab = ttk.Label(varfr, text="Path: " + path)
    pathlab.grid(row=0, column=1, sticky="W")

def main():
    ############
    #Initialise#
    ############

    global pathdef
    #choose default path
    pathdef = str(os.path.join(Path.home(), "Downloads", "grab-bot"))

    global config
    #config initialisation
    config = configparser.ConfigParser()

    #make sure the config file is present and correct
    try:
        config.read('grab.ini')
        lim = config['CONFIG']['limit']
        category = config['CONFIG']['category']
        config['CONFIG']['subs']
        path = config['CONFIG']['path']
        seltheme = config['CONFIG']['theme']
        print("Config is present and correct")
    except KeyError:
        config['CONFIG'] = {'limit': '10',
                            'category': 'hot',
                            'subs': '.empty.;',
                            'path': pathdef,
                            'theme': 'light'}
        with open('grab.ini', 'w') as configfile:
            config.write(configfile)
        print("Created config or fixed missing options")

    #read config
    readconf()

    global root
    #main window
    root = tk.Tk()
    root.title("grab - Reddit download bot")

    global theme
    #define theme
    theme = ttk.Style()

    global background
    global foreground
    print("Using " + seltheme + " theme")
    if seltheme == "light":
        root.configure(bg="#ffffff")
        #light theme
        theme.theme_create('light')
        theme.theme_settings('light', {
            "TFrame": {
                "configure": {
                    "background": ["#ffffff"],
                    "foreground": ["#1e1e1e"]
                }
            },
            "TLabel": {
                "configure": {
                    "background": ["#ffffff"],
                    "foreground": ["#1e1e1e"]
                }
            },
            "TButton": {
                "configure": {
                    "relief": ["ridge"],
                    "padding": [8, 1],
                    "background": ["#dedede"],
                    "foreground": ["#1e1e1e"]
                },
                "map": {
                    "relief": [("pressed", "sunken")],
                    "background": [("active", "#f0f0f0")]
                }
            },
            "TEntry": {

            }
        })
        #set background and foreground
        background = "#ffffff"
        foreground = "#1e1e1e"
        #use light theme
        theme.theme_use('light')

    elif seltheme == "dark":
        root.configure(bg="#000000")
        #dark theme
        theme.theme_create('dark')
        theme.theme_settings('dark', {
            "TFrame": {
                "configure": {
                    "background": ["#000000"],
                    "foreground": ["#e1e1e1"]
                }
            },
            "TLabel": {
                "configure": {
                    "background": ["#000000"],
                    "foreground": ["#e1e1e1"]
                }
            },
            "TButton": {
                "configure": {
                    "relief": ["ridge"],
                    "padding": [8, 1],
                    "background": ["#212121"],
                    "foreground": ["#e1e1e1"]
                },
                "map": {
                    "relief": [("pressed", "sunken")],
                    "background": [("active", "#0f0f0f")]
                }
            },
            "TEntry": {

            }
        })
        #set background and foreground
        #problems with visibility of selection from radiobuttons and spinbox up/down arrows
        #change color radiobuttons have when the mouse is hovering over them.
        background = "#000000"
        foreground = "#e1e1e1"
        #use dark theme
        theme.theme_use('dark')
    else:
        print("Sorry, this theme could not be found")

    global main
    #main frame
    main = ttk.Frame(root)
    main.grid(row=0, column=0, sticky="W", padx=5, pady=5)

    global normal
    #frame for listbox and main buttons
    normal = ttk.Frame(main)
    normal.grid(row=0, column=0, sticky="W")

    global var
    #subs label
    ttk.Label(normal, text="Active subreddits:", font="none 16").grid(row=0, column=0)
    var = tk.StringVar()

    global cnnsublist
    global lsublist
    global labelsublist
    #change the list of subs to fit
    cnnsublist = sublist.replace(';', '\n')
    lsublist = sublist.split(";")
    labelsublist = [x for x in lsublist if x]

    global lbox
    #multiple doesn't work with my method
    #lbox = tk.Listbox(window, listvariable=var, selectmode="multiple", width=24)
    #create a listbox with the proper theme
    lbox = tk.Listbox(normal, listvariable=var, selectmode="single", width=26, bg=background, fg=foreground)

    #insert subreddits into listbox
    for y in range(len(labelsublist)):
        lbox.insert('end', labelsublist[y])
    lbox.grid(row=2, column=0, sticky="W")

    #add new subreddits
    global butaddsub
    butaddsub = ttk.Button(normal, text="+", command=addfr)
    butaddsub.grid(row=1, column=0, sticky="W")

    #remove subreddits
    global butremsub
    butremsub = ttk.Button(normal, text="-", command=listbox)
    butremsub.grid(row=1, column=0, sticky="E")

    #y += 1
    #close the program
    ttk.Button(main, text="Exit", command=stop).grid(row=1, column=0, sticky="W")

    #run the program
    ttk.Button(main, text="Run", command=run).grid(row=1, column=0, sticky="E")

    global butexp
    #expand
    butexp = ttk.Button(main, text=">", command=winexp)
    butexp.grid(row=1, column=1, sticky="W")

    root.mainloop()

if __name__ == '__main__':
    main()
